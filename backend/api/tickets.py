"""
API de Tickets
Endpoints para gestión de tickets de soporte
"""
from flask import Blueprint, request
from sqlalchemy import desc, or_
from models import db, Ticket, ComentarioTicket, BaseConocimiento
from config import Config
from utils.api_response import APIResponse, APIError, api_login_required, api_tecnico_required, serialize_model, serialize_list
from utils.validators import TicketValidator, Validator
from datetime import datetime

tickets_api_bp = Blueprint('tickets_api', __name__)


@tickets_api_bp.route('/', methods=['GET'])
@api_login_required
def lista_tickets():
    """
    GET /api/tickets?page=1&estado=nuevo&categoria=problemas_tecnicos
    
    Lista tickets con filtros y paginación
    
    Response:
        {
            "success": true,
            "data": {
                "tickets": [...]
            },
            "meta": {
                "pagination": {...}
            }
        }
    """
    from flask_login import current_user
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    estado_filtro = request.args.get('estado', '')
    categoria_filtro = request.args.get('categoria', '')
    prioridad_filtro = request.args.get('prioridad', '')
    
    # Construir query base
    query = Ticket.query
    
    # Si no es técnico, solo ver sus propios tickets
    if not current_user.es_tecnico:
        query = query.filter_by(usuario_id=current_user.id)
    
    # Aplicar filtros
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    if categoria_filtro:
        query = query.filter_by(categoria=categoria_filtro)
    if prioridad_filtro:
        query = query.filter_by(prioridad=prioridad_filtro)
    
    # Contar total
    total = query.count()
    
    # Ordenar y paginar
    tickets = query.order_by(desc(Ticket.fecha_creacion)).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    # Serializar tickets
    tickets_data = []
    for ticket in tickets:
        ticket_dict = serialize_model(ticket, exclude=['datos_adicionales'])
        ticket_dict['usuario'] = {
            'id': ticket.usuario.id,
            'nombre': ticket.usuario.nombre,
            'email': ticket.usuario.email
        }
        if ticket.tecnico:
            ticket_dict['tecnico'] = {
                'id': ticket.tecnico.id,
                'nombre': ticket.tecnico.nombre
            }
        tickets_data.append(ticket_dict)
    
    return APIResponse.paginated(
        items=tickets_data,
        page=page,
        per_page=per_page,
        total=total,
        data_key='tickets'
    )


@tickets_api_bp.route('/<int:id>', methods=['GET'])
@api_login_required
def detalle_ticket(id):
    """
    GET /api/tickets/{id}
    
    Obtiene detalle de un ticket específico
    """
    from flask_login import current_user
    
    ticket = Ticket.query.get_or_404(id)
    
    # Verificar permisos
    if not current_user.es_tecnico and ticket.usuario_id != current_user.id:
        return APIResponse.error(
            APIError.FORBIDDEN,
            'No tienes permisos para ver este ticket',
            403
        )
    
    # Obtener comentarios
    comentarios = ComentarioTicket.query.filter_by(
        ticket_id=id
    ).order_by(ComentarioTicket.fecha_creacion).all()
    
    # Filtrar comentarios internos si no es técnico
    if not current_user.es_tecnico:
        comentarios = [c for c in comentarios if not c.es_interno]
    
    # Serializar ticket
    ticket_dict = serialize_model(ticket)
    ticket_dict['usuario'] = {
        'id': ticket.usuario.id,
        'nombre': ticket.usuario.nombre,
        'email': ticket.usuario.email,
        'departamento': ticket.usuario.departamento
    }
    
    if ticket.tecnico:
        ticket_dict['tecnico'] = {
            'id': ticket.tecnico.id,
            'nombre': ticket.tecnico.nombre,
            'email': ticket.tecnico.email
        }
    
    # Serializar comentarios
    comentarios_data = []
    for comentario in comentarios:
        com_dict = serialize_model(comentario)
        com_dict['autor'] = {
            'id': comentario.autor.id,
            'nombre': comentario.autor.nombre
        }
        comentarios_data.append(com_dict)
    
    ticket_dict['comentarios'] = comentarios_data
    
    return APIResponse.success(data={'ticket': ticket_dict})


@tickets_api_bp.route('/', methods=['POST'])
@api_login_required
def crear_ticket():
    """
    POST /api/tickets
    
    Body:
        {
            "categoria": "problemas_tecnicos",
            "subcategoria": "computador_celular",
            "titulo": "Mi computador no enciende",
            "descripcion": "Desde esta mañana mi computador no enciende...",
            "prioridad": "alta"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "ticket": {...}
            },
            "meta": {
                "message": "Ticket #123 creado exitosamente"
            }
        }
    """
    from flask_login import current_user
    
    data = request.get_json()
    
    if not data:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Datos inválidos',
            400
        )
    
    # Validar datos
    is_valid, errors = TicketValidator.validar_creacion(data)
    if not is_valid:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Errores de validación',
            400,
            details=errors
        )
    
    # Validar categoría existe
    if data['categoria'] not in Config.MAIN_CATEGORIES:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Categoría no válida',
            400
        )
    
    try:
        # Crear ticket
        nuevo_ticket = Ticket(
            usuario_id=current_user.id,
            categoria=data['categoria'],
            subcategoria=data.get('subcategoria', ''),
            titulo=data['titulo'].strip(),
            descripcion=data['descripcion'].strip(),
            prioridad=data.get('prioridad', 'media'),
            estado='nuevo',
            origen='api',
            datos_adicionales=data.get('datos_adicionales')
        )
        
        db.session.add(nuevo_ticket)
        db.session.commit()
        
        # Crear comentario inicial
        comentario_inicial = ComentarioTicket(
            ticket_id=nuevo_ticket.id,
            autor_id=current_user.id,
            contenido=f"Ticket creado por {current_user.nombre} desde la API.",
            es_interno=False
        )
        db.session.add(comentario_inicial)
        db.session.commit()
        
        # Serializar respuesta
        ticket_dict = serialize_model(nuevo_ticket)
        ticket_dict['usuario'] = {
            'id': current_user.id,
            'nombre': current_user.nombre
        }
        
        return APIResponse.success(
            data={'ticket': ticket_dict},
            message=f'Ticket #{nuevo_ticket.id} creado exitosamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al crear el ticket',
            500,
            details={'error': str(e)}
        )


@tickets_api_bp.route('/<int:id>/comentarios', methods=['POST'])
@api_login_required
def agregar_comentario(id):
    """
    POST /api/tickets/{id}/comentarios
    
    Body:
        {
            "contenido": "Texto del comentario",
            "es_interno": false
        }
    """
    from flask_login import current_user
    
    ticket = Ticket.query.get_or_404(id)
    
    # Verificar permisos
    if not current_user.es_tecnico and ticket.usuario_id != current_user.id:
        return APIResponse.error(
            APIError.FORBIDDEN,
            'No tienes permisos para comentar en este ticket',
            403
        )
    
    data = request.get_json()
    if not data:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Datos inválidos',
            400
        )
    
    contenido = data.get('contenido', '').strip()
    
    # Validar contenido
    is_valid, error = Validator.texto_requerido(contenido, 'Contenido', min_length=1, max_length=2000)
    if not is_valid:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            error,
            400
        )
    
    # Solo técnicos pueden crear comentarios internos
    es_interno = data.get('es_interno', False) and current_user.es_tecnico
    
    try:
        comentario = ComentarioTicket(
            ticket_id=id,
            autor_id=current_user.id,
            contenido=contenido,
            es_interno=es_interno
        )
        
        db.session.add(comentario)
        
        # Actualizar fecha de última modificación
        ticket.fecha_actualizacion = datetime.utcnow()
        db.session.commit()
        
        # Serializar respuesta
        comentario_dict = serialize_model(comentario)
        comentario_dict['autor'] = {
            'id': current_user.id,
            'nombre': current_user.nombre
        }
        
        return APIResponse.success(
            data={'comentario': comentario_dict},
            message='Comentario agregado correctamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al agregar el comentario',
            500,
            details={'error': str(e)}
        )


@tickets_api_bp.route('/<int:id>/estado', methods=['PATCH'])
@api_tecnico_required
def actualizar_estado(id):
    """
    PATCH /api/tickets/{id}/estado
    
    Body:
        {
            "estado": "en_proceso",
            "tecnico_id": 5
        }
    """
    from flask_login import current_user
    
    ticket = Ticket.query.get_or_404(id)
    
    data = request.get_json()
    if not data:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Datos inválidos',
            400
        )
    
    nuevo_estado = data.get('estado')
    
    # Validar estado
    if nuevo_estado not in Config.TICKET_STATES:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Estado no válido',
            400
        )
    
    try:
        estado_anterior = ticket.estado
        ticket.estado = nuevo_estado
        ticket.fecha_actualizacion = datetime.utcnow()
        
        # Asignar técnico si se especifica
        if 'tecnico_id' in data:
            ticket.tecnico_id = data['tecnico_id']
            if nuevo_estado == 'nuevo':
                ticket.estado = 'asignado_a_tecnico'
        
        # Si se marca como cerrado, establecer fecha de cierre
        if nuevo_estado in ['resuelto', 'cerrado']:
            ticket.fecha_cierre = datetime.utcnow()
        
        # Crear comentario automático
        comentario_sistema = ComentarioTicket(
            ticket_id=id,
            autor_id=current_user.id,
            contenido=f"Estado cambiado de '{estado_anterior}' a '{nuevo_estado}' por {current_user.nombre}",
            es_interno=True
        )
        
        db.session.add(comentario_sistema)
        db.session.commit()
        
        ticket_dict = serialize_model(ticket)
        
        return APIResponse.success(
            data={'ticket': ticket_dict},
            message=f'Estado actualizado a: {nuevo_estado}'
        )
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al actualizar el estado',
            500,
            details={'error': str(e)}
        )


@tickets_api_bp.route('/buscar-articulos', methods=['GET'])
@api_login_required
def buscar_articulos():
    """
    GET /api/tickets/buscar-articulos?q=impresora&categoria=problemas_tecnicos
    
    Busca artículos de conocimiento relacionados
    """
    query = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '')
    subcategoria = request.args.get('subcategoria', '')
    
    if len(query) < 3:
        return APIResponse.success(data={'articulos': []})
    
    # Construir query de búsqueda
    busqueda = BaseConocimiento.query.filter_by(activo=True)
    
    if categoria:
        busqueda = busqueda.filter_by(categoria=categoria)
    if subcategoria:
        busqueda = busqueda.filter_by(subcategoria=subcategoria)
    
    busqueda = busqueda.filter(
        or_(
            BaseConocimiento.titulo.contains(query),
            BaseConocimiento.contenido.contains(query),
            BaseConocimiento.palabras_clave.contains(query)
        )
    ).order_by(desc(BaseConocimiento.vistas)).limit(5)
    
    articulos = busqueda.all()
    
    articulos_data = [{
        'id': art.id,
        'titulo': art.titulo,
        'contenido_preview': art.contenido[:150] + '...' if len(art.contenido) > 150 else art.contenido,
        'categoria': art.categoria,
        'subcategoria': art.subcategoria
    } for art in articulos]
    
    return APIResponse.success(data={'articulos': articulos_data})


@tickets_api_bp.route('/estadisticas', methods=['GET'])
@api_tecnico_required
def estadisticas():
    """
    GET /api/tickets/estadisticas?categoria=problemas_tecnicos
    
    Estadísticas de tickets (solo técnicos)
    """
    categoria = request.args.get('categoria')
    
    if categoria:
        # Estadísticas por subcategoría
        stats = db.session.query(
            Ticket.subcategoria,
            db.func.count(Ticket.id).label('total'),
            db.func.sum(db.case([(Ticket.estado.in_(['resuelto', 'cerrado']), 0)], else_=1)).label('abiertos')
        ).filter_by(categoria=categoria).group_by(Ticket.subcategoria).all()
        
        stats_data = [{
            'subcategoria': stat.subcategoria,
            'total': stat.total,
            'abiertos': stat.abiertos or 0
        } for stat in stats]
    else:
        # Estadísticas generales
        stats = db.session.query(
            Ticket.categoria,
            db.func.count(Ticket.id).label('total'),
            db.func.sum(db.case([(Ticket.estado.in_(['resuelto', 'cerrado']), 0)], else_=1)).label('abiertos')
        ).group_by(Ticket.categoria).all()
        
        stats_data = [{
            'categoria': stat.categoria,
            'total': stat.total,
            'abiertos': stat.abiertos or 0
        } for stat in stats]
    
    return APIResponse.success(data={'estadisticas': stats_data})

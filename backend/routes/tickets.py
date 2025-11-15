from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, or_
from models import db, Ticket, Usuario, ComentarioTicket, BaseConocimiento
from config import Config
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    estado_filtro = request.args.get('estado', '')
    categoria_filtro = request.args.get('categoria', '')
    
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
    
    # Ordenar por fecha de creación (más recientes primero)
    tickets = query.order_by(desc(Ticket.fecha_creacion)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('tickets/lista.html', 
                         tickets=tickets,
                         estado_filtro=estado_filtro,
                         categoria_filtro=categoria_filtro)

@tickets_bp.route('/nuevo')
@login_required
def nuevo():
    return render_template('tickets/nuevo.html')

@tickets_bp.route('/flujo_guiado')
@login_required
def flujo_guiado():
    # Paso del flujo guiado
    paso = request.args.get('paso', 'categoria')
    categoria = request.args.get('categoria', '')
    subcategoria = request.args.get('subcategoria', '')
    
    # Datos del contexto según el paso
    contexto = {
        'paso': paso,
        'categoria': categoria,
        'subcategoria': subcategoria,
        'categorias': Config.MAIN_CATEGORIES
    }
    
    # Sugerencias de artículos según la categoría/subcategoría seleccionada
    if categoria and subcategoria:
        articulos_sugeridos = BaseConocimiento.query.filter_by(
            categoria=categoria,
            subcategoria=subcategoria,
            activo=True
        ).order_by(desc(BaseConocimiento.vistas)).limit(3).all()
        contexto['articulos_sugeridos'] = articulos_sugeridos
    
    return render_template('tickets/flujo_guiado.html', **contexto)

@tickets_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    # Datos del formulario
    categoria = request.form.get('categoria')
    subcategoria = request.form.get('subcategoria')
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    prioridad = request.form.get('prioridad', 'media')
    
    # Datos adicionales del flujo guiado (si existen)
    datos_adicionales = {}
    for key, value in request.form.items():
        if key.startswith('flujo_'):
            datos_adicionales[key] = value
    
    # Validaciones
    if not all([categoria, titulo, descripcion]):
        flash('Por favor completa todos los campos obligatorios', 'error')
        return redirect(url_for('tickets.nuevo'))
    
    # Crear el ticket
    nuevo_ticket = Ticket(
        usuario_id=current_user.id,
        categoria=categoria,
        subcategoria=subcategoria,
        titulo=titulo,
        descripcion=descripcion,
        prioridad=prioridad,
        estado='nuevo',
        origen='portal',
        datos_adicionales=datos_adicionales if datos_adicionales else None
    )
    
    db.session.add(nuevo_ticket)
    db.session.commit()
    
    # Crear comentario inicial del sistema
    comentario_inicial = ComentarioTicket(
        ticket_id=nuevo_ticket.id,
        autor_id=current_user.id,
        contenido=f"Ticket creado por {current_user.nombre} desde el portal web.",
        es_interno=False
    )
    db.session.add(comentario_inicial)
    db.session.commit()
    
    flash(f'Ticket #{nuevo_ticket.id} creado exitosamente', 'success')
    return redirect(url_for('tickets.detalle', id=nuevo_ticket.id))

@tickets_bp.route('/<int:id>')
@login_required
def detalle(id):
    ticket = Ticket.query.get_or_404(id)
    
    # Verificar permisos: solo el usuario creador o técnicos pueden ver el ticket
    if not current_user.es_tecnico and ticket.usuario_id != current_user.id:
        flash('No tienes permisos para ver este ticket', 'error')
        return redirect(url_for('tickets.lista'))
    
    # Obtener comentarios del ticket
    comentarios = ComentarioTicket.query.filter_by(
        ticket_id=id
    ).order_by(ComentarioTicket.fecha_creacion).all()
    
    # Si es técnico, puede ver comentarios internos
    if not current_user.es_tecnico:
        comentarios = [c for c in comentarios if not c.es_interno]
    
    # Obtener lista de técnicos para asignación (solo si es técnico)
    tecnicos = []
    if current_user.es_tecnico:
        tecnicos = Usuario.query.filter_by(es_tecnico=True, activo=True).all()
    
    return render_template('tickets/detalle.html', 
                         ticket=ticket, 
                         comentarios=comentarios,
                         tecnicos=tecnicos)

@tickets_bp.route('/<int:id>/comentar', methods=['POST'])
@login_required
def comentar(id):
    ticket = Ticket.query.get_or_404(id)
    
    # Verificar permisos
    if not current_user.es_tecnico and ticket.usuario_id != current_user.id:
        flash('No tienes permisos para comentar en este ticket', 'error')
        return redirect(url_for('tickets.lista'))
    
    contenido = request.form.get('contenido')
    es_interno = request.form.get('es_interno') == 'on' and current_user.es_tecnico
    
    if not contenido:
        flash('El comentario no puede estar vacío', 'error')
        return redirect(url_for('tickets.detalle', id=id))
    
    # Crear comentario
    comentario = ComentarioTicket(
        ticket_id=id,
        autor_id=current_user.id,
        contenido=contenido,
        es_interno=es_interno
    )
    
    db.session.add(comentario)
    
    # Actualizar fecha de última modificación del ticket
    ticket.fecha_actualizacion = datetime.utcnow()
    db.session.commit()
    
    flash('Comentario agregado correctamente', 'success')
    return redirect(url_for('tickets.detalle', id=id))

@tickets_bp.route('/<int:id>/actualizar_estado', methods=['POST'])
@login_required
def actualizar_estado(id):
    if not current_user.es_tecnico:
        flash('Solo los técnicos pueden actualizar el estado de los tickets', 'error')
        return redirect(url_for('tickets.detalle', id=id))
    
    ticket = Ticket.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    tecnico_asignado_id = request.form.get('tecnico_asignado')
    
    if nuevo_estado not in Config.TICKET_STATES:
        flash('Estado no válido', 'error')
        return redirect(url_for('tickets.detalle', id=id))
    
    estado_anterior = ticket.estado
    ticket.estado = nuevo_estado
    ticket.fecha_actualizacion = datetime.utcnow()
    
    # Asignar técnico si se especifica
    if tecnico_asignado_id:
        ticket.tecnico_id = int(tecnico_asignado_id)
        if nuevo_estado == 'nuevo':
            ticket.estado = 'asignado_a_tecnico'
    
    # Si se marca como cerrado, establecer fecha de cierre
    if nuevo_estado in ['resuelto', 'cerrado']:
        ticket.fecha_cierre = datetime.utcnow()
    
    # Crear comentario automático del cambio de estado
    comentario_sistema = ComentarioTicket(
        ticket_id=id,
        autor_id=current_user.id,
        contenido=f"Estado cambiado de '{estado_anterior}' a '{nuevo_estado}' por {current_user.nombre}",
        es_interno=True
    )
    
    db.session.add(comentario_sistema)
    db.session.commit()
    
    flash(f'Estado del ticket actualizado a: {ticket.get_estado_display()}', 'success')
    return redirect(url_for('tickets.detalle', id=id))

@tickets_bp.route('/buscar_articulos')
@login_required
def buscar_articulos():
    """API endpoint para buscar artículos mientras el usuario escribe"""
    query = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '')
    subcategoria = request.args.get('subcategoria', '')
    
    if len(query) < 3:
        return jsonify([])
    
    # Construir query de búsqueda
    busqueda = BaseConocimiento.query.filter_by(activo=True)
    
    # Filtrar por categoría si se especifica
    if categoria:
        busqueda = busqueda.filter_by(categoria=categoria)
    if subcategoria:
        busqueda = busqueda.filter_by(subcategoria=subcategoria)
    
    # Buscar en título, contenido y palabras clave
    busqueda = busqueda.filter(
        or_(
            BaseConocimiento.titulo.contains(query),
            BaseConocimiento.contenido.contains(query),
            BaseConocimiento.palabras_clave.contains(query)
        )
    ).order_by(desc(BaseConocimiento.vistas)).limit(5)
    
    articulos = busqueda.all()
    
    return jsonify([{
        'id': art.id,
        'titulo': art.titulo,
        'contenido_preview': art.contenido[:150] + '...' if len(art.contenido) > 150 else art.contenido,
        'url': url_for('knowledge.articulo', id=art.id)
    } for art in articulos])

@tickets_bp.route('/estadisticas_categoria')
@login_required
def estadisticas_categoria():
    """API endpoint para obtener estadísticas de una categoría específica"""
    if not current_user.es_tecnico:
        return jsonify({'error': 'No autorizado'}), 403
    
    categoria = request.args.get('categoria')
    if not categoria:
        return jsonify({'error': 'Categoría requerida'}), 400
    
    # Contar tickets por subcategoría en esta categoría
    stats = db.session.query(
        Ticket.subcategoria,
        db.func.count(Ticket.id).label('total'),
        db.func.sum(db.case([(Ticket.estado.in_(['resuelto', 'cerrado']), 0)], else_=1)).label('abiertos')
    ).filter_by(categoria=categoria).group_by(Ticket.subcategoria).all()
    
    return jsonify([{
        'subcategoria': stat.subcategoria,
        'total': stat.total,
        'abiertos': stat.abiertos or 0
    } for stat in stats])

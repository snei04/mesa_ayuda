"""
API de Dashboard
Endpoints para estadísticas y datos del dashboard
"""
from flask import Blueprint, request
from sqlalchemy import func, desc
from models import db, Ticket, Usuario, BaseConocimiento
from utils.api_response import APIResponse, APIError, api_login_required, api_tecnico_required, serialize_model
from datetime import datetime, timedelta
from flask_login import current_user

dashboard_api_bp = Blueprint('dashboard_api', __name__)


@dashboard_api_bp.route('/home', methods=['GET'])
@api_login_required
def home():
    """
    GET /api/dashboard/home
    
    Datos del dashboard principal del usuario
    """
    # Tickets abiertos del usuario
    tickets_abiertos = Ticket.query.filter_by(
        usuario_id=current_user.id
    ).filter(
        Ticket.estado.notin_(['resuelto', 'cerrado'])
    ).count()
    
    # Últimos tickets
    tickets_recientes = Ticket.query.filter_by(
        usuario_id=current_user.id
    ).order_by(desc(Ticket.fecha_creacion)).limit(5).all()
    
    # Artículos populares
    articulos_populares = BaseConocimiento.query.filter_by(
        activo=True
    ).order_by(desc(BaseConocimiento.vistas)).limit(3).all()
    
    # Estadísticas para técnicos
    stats_tecnico = {}
    if current_user.es_tecnico:
        stats_tecnico = {
            'tickets_asignados': Ticket.query.filter_by(
                tecnico_id=current_user.id
            ).filter(
                Ticket.estado.notin_(['resuelto', 'cerrado'])
            ).count(),
            'tickets_nuevos': Ticket.query.filter_by(estado='nuevo').count(),
            'tickets_criticos': Ticket.query.filter_by(prioridad='critica').filter(
                Ticket.estado.notin_(['resuelto', 'cerrado'])
            ).count()
        }
    
    return APIResponse.success(data={
        'tickets_abiertos': tickets_abiertos,
        'tickets_recientes': [serialize_model(t, exclude=['descripcion', 'datos_adicionales']) for t in tickets_recientes],
        'articulos_populares': [serialize_model(a, exclude=['contenido']) for a in articulos_populares],
        'stats_tecnico': stats_tecnico
    })


@dashboard_api_bp.route('/buscar-ayuda', methods=['GET'])
@api_login_required
def buscar_ayuda():
    """
    GET /api/dashboard/buscar-ayuda?q=impresora
    """
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 3:
        return APIResponse.success(data={'resultados': []})
    
    resultados = BaseConocimiento.query.filter(
        BaseConocimiento.activo == True
    ).filter(
        db.or_(
            BaseConocimiento.titulo.contains(query),
            BaseConocimiento.contenido.contains(query),
            BaseConocimiento.palabras_clave.contains(query)
        )
    ).order_by(desc(BaseConocimiento.vistas)).limit(10).all()
    
    resultados_data = [{
        'id': art.id,
        'titulo': art.titulo,
        'contenido': art.contenido[:200] + '...' if len(art.contenido) > 200 else art.contenido,
        'categoria': art.categoria,
        'vistas': art.vistas
    } for art in resultados]
    
    return APIResponse.success(data={'resultados': resultados_data})


@dashboard_api_bp.route('/accesos-rapidos', methods=['GET'])
@api_login_required
def accesos_rapidos():
    """
    GET /api/dashboard/accesos-rapidos
    
    Categorías más usadas por el usuario
    """
    from config import Config
    
    categorias_frecuentes = db.session.query(
        Ticket.categoria,
        Ticket.subcategoria,
        func.count(Ticket.id).label('count')
    ).filter_by(
        usuario_id=current_user.id
    ).group_by(
        Ticket.categoria,
        Ticket.subcategoria
    ).order_by(
        desc('count')
    ).limit(3).all()
    
    accesos_rapidos = []
    for cat, subcat, count in categorias_frecuentes:
        categoria_info = Config.MAIN_CATEGORIES.get(cat, {})
        subcategoria_info = categoria_info.get('subcategories', {}).get(subcat, subcat)
        
        accesos_rapidos.append({
            'categoria': cat,
            'subcategoria': subcat,
            'nombre': f"{categoria_info.get('name', cat)} - {subcategoria_info}",
            'count': count
        })
    
    # Si no tiene historial, accesos por defecto
    if not accesos_rapidos:
        accesos_rapidos = [
            {
                'categoria': 'problemas_tecnicos',
                'subcategoria': 'computador_celular',
                'nombre': 'Problemas con Computador/Celular',
                'count': 0
            },
            {
                'categoria': 'permisos_accesos',
                'subcategoria': 'reset_password',
                'nombre': 'Restablecer Contraseña',
                'count': 0
            },
            {
                'categoria': 'problemas_tecnicos',
                'subcategoria': 'impresoras',
                'nombre': 'Problemas con Impresoras',
                'count': 0
            }
        ]
    
    return APIResponse.success(data={'accesos_rapidos': accesos_rapidos})


@dashboard_api_bp.route('/estadisticas', methods=['GET'])
@api_tecnico_required
def estadisticas():
    """
    GET /api/dashboard/estadisticas
    
    Estadísticas generales del sistema (solo técnicos)
    """
    # Estadísticas generales
    total_tickets = Ticket.query.count()
    tickets_abiertos = Ticket.query.filter(
        Ticket.estado.notin_(['resuelto', 'cerrado'])
    ).count()
    
    # Por estado
    tickets_por_estado = db.session.query(
        Ticket.estado,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.estado).all()
    
    # Por categoría (últimos 30 días)
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    tickets_por_categoria = db.session.query(
        Ticket.categoria,
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.fecha_creacion >= fecha_limite
    ).group_by(Ticket.categoria).all()
    
    # Técnicos más activos
    tecnicos_activos = db.session.query(
        Usuario.nombre,
        func.count(Ticket.id).label('tickets_asignados')
    ).join(
        Ticket, Usuario.id == Ticket.tecnico_id
    ).filter(
        Usuario.es_tecnico == True,
        Ticket.fecha_creacion >= fecha_limite
    ).group_by(Usuario.id, Usuario.nombre).order_by(
        desc('tickets_asignados')
    ).limit(5).all()
    
    return APIResponse.success(data={
        'total_tickets': total_tickets,
        'tickets_abiertos': tickets_abiertos,
        'tickets_por_estado': [{'estado': e, 'count': c} for e, c in tickets_por_estado],
        'tickets_por_categoria': [{'categoria': cat, 'count': c} for cat, c in tickets_por_categoria],
        'tecnicos_activos': [{'nombre': n, 'tickets_asignados': t} for n, t in tecnicos_activos]
    })


@dashboard_api_bp.route('/notificaciones', methods=['GET'])
@api_tecnico_required
def notificaciones():
    """
    GET /api/dashboard/notificaciones
    
    Notificaciones en tiempo real para técnicos
    """
    # Tickets nuevos (últimos 5 minutos)
    hace_5_min = datetime.utcnow() - timedelta(minutes=5)
    tickets_nuevos = Ticket.query.filter(
        Ticket.fecha_creacion >= hace_5_min,
        Ticket.estado == 'nuevo'
    ).order_by(desc(Ticket.fecha_creacion)).all()
    
    # Tickets críticos sin asignar
    tickets_criticos = Ticket.query.filter(
        Ticket.prioridad == 'critica',
        Ticket.tecnico_id.is_(None),
        Ticket.estado == 'nuevo'
    ).count()
    
    # Tickets asignados al técnico actual
    mis_tickets_pendientes = Ticket.query.filter(
        Ticket.tecnico_id == current_user.id,
        Ticket.estado.in_(['asignado_a_tecnico', 'en_proceso'])
    ).count()
    
    notificaciones = []
    
    # Notificaciones de tickets nuevos
    for ticket in tickets_nuevos:
        notificaciones.append({
            'tipo': 'nuevo_ticket',
            'titulo': f'Nuevo ticket #{ticket.id}',
            'mensaje': f'{ticket.titulo} - {ticket.usuario.nombre}',
            'url': f'/tickets/{ticket.id}',
            'tiempo': ticket.fecha_creacion.strftime('%H:%M'),
            'prioridad': ticket.prioridad
        })
    
    # Notificación de tickets críticos
    if tickets_criticos > 0:
        notificaciones.append({
            'tipo': 'critico',
            'titulo': f'{tickets_criticos} ticket(s) crítico(s)',
            'mensaje': 'Requieren atención inmediata',
            'url': '/tickets?prioridad=critica&estado=nuevo',
            'tiempo': 'Ahora',
            'prioridad': 'critica'
        })
    
    return APIResponse.success(data={
        'notificaciones': notificaciones,
        'total_nuevos': len(tickets_nuevos),
        'total_criticos': tickets_criticos,
        'mis_pendientes': mis_tickets_pendientes
    })

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from models import db, Ticket, Usuario, BaseConocimiento
from config import Config
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def home():
    # Estadísticas para el dashboard del usuario
    tickets_abiertos = Ticket.query.filter_by(
        usuario_id=current_user.id
    ).filter(
        Ticket.estado.notin_(['resuelto', 'cerrado'])
    ).count()
    
    # Últimos 5 tickets del usuario
    tickets_recientes = Ticket.query.filter_by(
        usuario_id=current_user.id
    ).order_by(desc(Ticket.fecha_creacion)).limit(5).all()
    
    # Artículos más vistos de la base de conocimiento
    articulos_populares = BaseConocimiento.query.filter_by(
        activo=True
    ).order_by(desc(BaseConocimiento.vistas)).limit(3).all()
    
    # Estadísticas adicionales para técnicos
    stats_tecnico = {}
    if current_user.es_tecnico:
        stats_tecnico = {
            'tickets_asignados': Ticket.query.filter_by(
                tecnico_id=current_user.id
            ).filter(
                Ticket.estado.notin_(['resuelto', 'cerrado'])
            ).count(),
            'tickets_nuevos': Ticket.query.filter_by(
                estado='nuevo'
            ).count(),
            'tickets_criticos': Ticket.query.filter_by(
                prioridad='critica'
            ).filter(
                Ticket.estado.notin_(['resuelto', 'cerrado'])
            ).count()
        }
    
    return render_template('dashboard/home.html',
                         tickets_abiertos=tickets_abiertos,
                         tickets_recientes=tickets_recientes,
                         articulos_populares=articulos_populares,
                         stats_tecnico=stats_tecnico)

@dashboard_bp.route('/buscar_ayuda')
@login_required
def buscar_ayuda():
    query = request.args.get('q', '').strip()
    resultados = []
    
    if query and len(query) >= 3:
        # Buscar en la base de conocimiento
        resultados = BaseConocimiento.query.filter(
            BaseConocimiento.activo == True
        ).filter(
            db.or_(
                BaseConocimiento.titulo.contains(query),
                BaseConocimiento.contenido.contains(query),
                BaseConocimiento.palabras_clave.contains(query)
            )
        ).order_by(desc(BaseConocimiento.vistas)).limit(10).all()
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify([{
            'id': art.id,
            'titulo': art.titulo,
            'contenido': art.contenido[:200] + '...' if len(art.contenido) > 200 else art.contenido,
            'categoria': art.categoria,
            'vistas': art.vistas
        } for art in resultados])
    
    return render_template('dashboard/buscar_ayuda.html', 
                         query=query, 
                         resultados=resultados)

@dashboard_bp.route('/accesos_rapidos')
@login_required
def accesos_rapidos():
    # Obtener las 3 categorías más comunes de tickets del usuario
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
    
    # Preparar datos para los botones de acceso rápido
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
    
    # Si no tiene historial, mostrar accesos por defecto
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
    
    return render_template('dashboard/accesos_rapidos.html', 
                         accesos_rapidos=accesos_rapidos)

@dashboard_bp.route('/estadisticas')
@login_required
def estadisticas():
    if not current_user.es_tecnico:
        return redirect(url_for('dashboard.home'))
    
    # Estadísticas generales del sistema
    total_tickets = Ticket.query.count()
    tickets_abiertos = Ticket.query.filter(
        Ticket.estado.notin_(['resuelto', 'cerrado'])
    ).count()
    
    # Tickets por estado
    tickets_por_estado = db.session.query(
        Ticket.estado,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.estado).all()
    
    # Tickets por categoría (últimos 30 días)
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
    
    return render_template('dashboard/estadisticas.html',
                         total_tickets=total_tickets,
                         tickets_abiertos=tickets_abiertos,
                         tickets_por_estado=tickets_por_estado,
                         tickets_por_categoria=tickets_por_categoria,
                         tecnicos_activos=tecnicos_activos)

@dashboard_bp.route('/notificaciones')
@login_required
def notificaciones():
    """API para obtener notificaciones en tiempo real para técnicos"""
    if not current_user.es_tecnico:
        return jsonify({'error': 'No autorizado'}), 403
    
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
    
    # Agregar notificaciones de tickets nuevos
    for ticket in tickets_nuevos:
        notificaciones.append({
            'tipo': 'nuevo_ticket',
            'titulo': f'Nuevo ticket #{ticket.id}',
            'mensaje': f'{ticket.titulo} - {ticket.usuario.nombre}',
            'url': f'/tickets/{ticket.id}',
            'tiempo': ticket.fecha_creacion.strftime('%H:%M'),
            'prioridad': ticket.prioridad
        })
    
    # Agregar notificación de tickets críticos
    if tickets_criticos > 0:
        notificaciones.append({
            'tipo': 'critico',
            'titulo': f'{tickets_criticos} ticket(s) crítico(s)',
            'mensaje': 'Requieren atención inmediata',
            'url': '/tickets?prioridad=critica&estado=nuevo',
            'tiempo': 'Ahora',
            'prioridad': 'critica'
        })
    
    return jsonify({
        'notificaciones': notificaciones,
        'total_nuevos': len(tickets_nuevos),
        'total_criticos': tickets_criticos,
        'mis_pendientes': mis_tickets_pendientes
    })

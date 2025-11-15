"""
API de Base de Conocimiento
Endpoints para gestión de artículos
"""
from flask import Blueprint, request
from sqlalchemy import desc, or_
from models import db, BaseConocimiento
from config import Config
from utils.api_response import APIResponse, APIError, api_login_required, api_tecnico_required, serialize_model
from utils.validators import ConocimientoValidator
from flask_login import current_user

knowledge_api_bp = Blueprint('knowledge_api', __name__)


@knowledge_api_bp.route('/', methods=['GET'])
@api_login_required
def lista_articulos():
    """
    GET /api/knowledge?q=impresora&categoria=problemas_tecnicos&page=1
    """
    query = request.args.get('q', '').strip()
    categoria_filtro = request.args.get('categoria', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Construir query
    articulos_query = BaseConocimiento.query.filter_by(activo=True)
    
    if query:
        articulos_query = articulos_query.filter(
            or_(
                BaseConocimiento.titulo.contains(query),
                BaseConocimiento.contenido.contains(query),
                BaseConocimiento.palabras_clave.contains(query)
            )
        )
    
    if categoria_filtro:
        articulos_query = articulos_query.filter_by(categoria=categoria_filtro)
    
    # Contar total
    total = articulos_query.count()
    
    # Ordenar y paginar
    articulos = articulos_query.order_by(
        desc(BaseConocimiento.vistas),
        desc(BaseConocimiento.fecha_creacion)
    ).offset((page - 1) * per_page).limit(per_page).all()
    
    # Serializar
    articulos_data = []
    for art in articulos:
        art_dict = serialize_model(art, exclude=['contenido'])
        art_dict['autor'] = {'id': art.autor.id, 'nombre': art.autor.nombre}
        art_dict['contenido_preview'] = art.contenido[:200] + '...' if len(art.contenido) > 200 else art.contenido
        articulos_data.append(art_dict)
    
    return APIResponse.paginated(
        items=articulos_data,
        page=page,
        per_page=per_page,
        total=total,
        data_key='articulos'
    )


@knowledge_api_bp.route('/<int:id>', methods=['GET'])
@api_login_required
def detalle_articulo(id):
    """
    GET /api/knowledge/{id}
    """
    articulo = BaseConocimiento.query.get_or_404(id)
    
    if not articulo.activo:
        return APIResponse.error(
            APIError.NOT_FOUND,
            'Este artículo no está disponible',
            404
        )
    
    # Incrementar vistas
    articulo.incrementar_vistas()
    
    # Artículos relacionados
    relacionados = BaseConocimiento.query.filter(
        BaseConocimiento.id != id,
        BaseConocimiento.activo == True
    ).filter(
        or_(
            BaseConocimiento.categoria == articulo.categoria,
            BaseConocimiento.subcategoria == articulo.subcategoria
        )
    ).order_by(desc(BaseConocimiento.vistas)).limit(3).all()
    
    # Serializar
    art_dict = serialize_model(articulo)
    art_dict['autor'] = {'id': articulo.autor.id, 'nombre': articulo.autor.nombre}
    art_dict['relacionados'] = [
        {
            'id': r.id,
            'titulo': r.titulo,
            'categoria': r.categoria
        } for r in relacionados
    ]
    
    return APIResponse.success(data={'articulo': art_dict})


@knowledge_api_bp.route('/', methods=['POST'])
@api_tecnico_required
def crear_articulo():
    """
    POST /api/knowledge
    
    Body:
        {
            "titulo": "Cómo reiniciar una impresora",
            "contenido": "Paso 1: ...",
            "palabras_clave": "impresora, reiniciar, problema",
            "categoria": "problemas_tecnicos",
            "subcategoria": "impresoras"
        }
    """
    data = request.get_json()
    
    if not data:
        return APIResponse.error(APIError.VALIDATION_ERROR, 'Datos inválidos', 400)
    
    # Validar
    is_valid, errors = ConocimientoValidator.validar_articulo(data)
    if not is_valid:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Errores de validación',
            400,
            details=errors
        )
    
    try:
        nuevo_articulo = BaseConocimiento(
            titulo=data['titulo'].strip(),
            contenido=data['contenido'].strip(),
            palabras_clave=data.get('palabras_clave', '').strip(),
            categoria=data['categoria'],
            subcategoria=data.get('subcategoria', ''),
            autor_id=current_user.id,
            activo=True
        )
        
        db.session.add(nuevo_articulo)
        db.session.commit()
        
        art_dict = serialize_model(nuevo_articulo)
        
        return APIResponse.success(
            data={'articulo': art_dict},
            message='Artículo creado exitosamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al crear el artículo',
            500,
            details={'error': str(e)}
        )


@knowledge_api_bp.route('/<int:id>', methods=['PUT'])
@api_tecnico_required
def editar_articulo(id):
    """
    PUT /api/knowledge/{id}
    """
    articulo = BaseConocimiento.query.get_or_404(id)
    
    # Verificar permisos
    if articulo.autor_id != current_user.id:
        return APIResponse.error(
            APIError.FORBIDDEN,
            'No tienes permisos para editar este artículo',
            403
        )
    
    data = request.get_json()
    if not data:
        return APIResponse.error(APIError.VALIDATION_ERROR, 'Datos inválidos', 400)
    
    # Validar
    is_valid, errors = ConocimientoValidator.validar_articulo(data)
    if not is_valid:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Errores de validación',
            400,
            details=errors
        )
    
    try:
        articulo.titulo = data['titulo'].strip()
        articulo.contenido = data['contenido'].strip()
        articulo.palabras_clave = data.get('palabras_clave', '').strip()
        articulo.categoria = data['categoria']
        articulo.subcategoria = data.get('subcategoria', '')
        
        db.session.commit()
        
        art_dict = serialize_model(articulo)
        
        return APIResponse.success(
            data={'articulo': art_dict},
            message='Artículo actualizado exitosamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al actualizar el artículo',
            500,
            details={'error': str(e)}
        )


@knowledge_api_bp.route('/<int:id>', methods=['DELETE'])
@api_tecnico_required
def eliminar_articulo(id):
    """
    DELETE /api/knowledge/{id}
    """
    articulo = BaseConocimiento.query.get_or_404(id)
    
    # Verificar permisos
    if articulo.autor_id != current_user.id:
        return APIResponse.error(
            APIError.FORBIDDEN,
            'No tienes permisos para eliminar este artículo',
            403
        )
    
    try:
        # Marcar como inactivo
        articulo.activo = False
        db.session.commit()
        
        return APIResponse.success(message='Artículo eliminado exitosamente')
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al eliminar el artículo',
            500,
            details={'error': str(e)}
        )


@knowledge_api_bp.route('/buscar-sugerencias', methods=['GET'])
@api_login_required
def buscar_sugerencias():
    """
    GET /api/knowledge/buscar-sugerencias?q=impre
    
    Autocompletado de búsqueda
    """
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return APIResponse.success(data={'sugerencias': []})
    
    sugerencias = BaseConocimiento.query.filter(
        BaseConocimiento.activo == True,
        BaseConocimiento.titulo.contains(query)
    ).order_by(desc(BaseConocimiento.vistas)).limit(5).all()
    
    sugerencias_data = [{
        'titulo': art.titulo,
        'id': art.id,
        'categoria': art.categoria
    } for art in sugerencias]
    
    return APIResponse.success(data={'sugerencias': sugerencias_data})


@knowledge_api_bp.route('/estadisticas', methods=['GET'])
@api_tecnico_required
def estadisticas():
    """
    GET /api/knowledge/estadisticas
    """
    # Artículos más vistos
    mas_vistos = BaseConocimiento.query.filter_by(
        activo=True
    ).order_by(desc(BaseConocimiento.vistas)).limit(10).all()
    
    # Por categoría
    por_categoria = db.session.query(
        BaseConocimiento.categoria,
        db.func.count(BaseConocimiento.id).label('total'),
        db.func.sum(BaseConocimiento.vistas).label('vistas_totales')
    ).filter_by(activo=True).group_by(BaseConocimiento.categoria).all()
    
    return APIResponse.success(data={
        'mas_vistos': [serialize_model(art, exclude=['contenido']) for art in mas_vistos],
        'por_categoria': [{
            'categoria': cat,
            'total': total,
            'vistas_totales': vistas or 0
        } for cat, total, vistas in por_categoria]
    })

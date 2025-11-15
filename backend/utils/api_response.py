"""
Utilidades para respuestas API estandarizadas
Siguiendo las reglas globales de desarrollo
"""
from flask import jsonify
from datetime import datetime
from functools import wraps
from flask_login import current_user


class APIResponse:
    """Clase para manejar respuestas API consistentes"""
    
    @staticmethod
    def success(data=None, message=None, meta=None):
        """
        Respuesta exitosa
        
        Args:
            data: Datos a devolver (dict, list, o None)
            message: Mensaje opcional para el usuario
            meta: Metadatos adicionales (paginación, timestamps, etc.)
        """
        response = {
            'success': True,
            'data': data,
            'error': None,
            'meta': meta or {}
        }
        
        # Agregar timestamp si no existe
        if 'timestamp' not in response['meta']:
            response['meta']['timestamp'] = datetime.utcnow().isoformat()
        
        # Agregar mensaje si existe
        if message:
            response['meta']['message'] = message
            
        return jsonify(response), 200
    
    @staticmethod
    def error(code, message, status=400, details=None):
        """
        Respuesta de error
        
        Args:
            code: Código de error (ej: 'VALIDATION_ERROR', 'NOT_FOUND')
            message: Mensaje amigable para el usuario
            status: Código HTTP (400, 401, 403, 404, 500, etc.)
            details: Detalles adicionales del error
        """
        response = {
            'success': False,
            'data': None,
            'error': {
                'code': code,
                'message': message
            },
            'meta': {
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        if details:
            response['error']['details'] = details
            
        return jsonify(response), status
    
    @staticmethod
    def paginated(items, page, per_page, total, data_key='items'):
        """
        Respuesta con paginación
        
        Args:
            items: Lista de items de la página actual
            page: Número de página actual
            per_page: Items por página
            total: Total de items
            data_key: Nombre de la clave para los items
        """
        total_pages = (total + per_page - 1) // per_page
        
        return APIResponse.success(
            data={data_key: items},
            meta={
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        )


class APIError:
    """Códigos de error estandarizados"""
    
    # Errores de validación (400)
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    MISSING_FIELDS = 'MISSING_FIELDS'
    INVALID_FORMAT = 'INVALID_FORMAT'
    
    # Errores de autenticación (401)
    UNAUTHORIZED = 'UNAUTHORIZED'
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    SESSION_EXPIRED = 'SESSION_EXPIRED'
    
    # Errores de permisos (403)
    FORBIDDEN = 'FORBIDDEN'
    INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS'
    
    # Errores de recursos (404)
    NOT_FOUND = 'NOT_FOUND'
    RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND'
    
    # Errores de conflicto (409)
    ALREADY_EXISTS = 'ALREADY_EXISTS'
    CONFLICT = 'CONFLICT'
    
    # Errores del servidor (500)
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    DATABASE_ERROR = 'DATABASE_ERROR'


def api_login_required(f):
    """
    Decorador para rutas API que requieren autenticación
    Devuelve JSON en lugar de redirigir
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return APIResponse.error(
                APIError.UNAUTHORIZED,
                'Debes iniciar sesión para acceder a este recurso',
                401
            )
        return f(*args, **kwargs)
    return decorated_function


def api_tecnico_required(f):
    """
    Decorador para rutas API que requieren permisos de técnico
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return APIResponse.error(
                APIError.UNAUTHORIZED,
                'Debes iniciar sesión para acceder a este recurso',
                401
            )
        if not current_user.es_tecnico:
            return APIResponse.error(
                APIError.FORBIDDEN,
                'No tienes permisos suficientes para realizar esta acción',
                403
            )
        return f(*args, **kwargs)
    return decorated_function


def validate_required_fields(data, required_fields):
    """
    Valida que todos los campos requeridos estén presentes
    
    Args:
        data: Diccionario con los datos a validar
        required_fields: Lista de campos requeridos
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    missing = [field for field in required_fields if not data.get(field)]
    return len(missing) == 0, missing


def serialize_model(model, fields=None, exclude=None):
    """
    Serializa un modelo SQLAlchemy a diccionario
    
    Args:
        model: Instancia del modelo
        fields: Lista de campos a incluir (None = todos)
        exclude: Lista de campos a excluir
        
    Returns:
        dict: Modelo serializado
    """
    if model is None:
        return None
        
    # Obtener todos los campos del modelo
    data = {}
    
    for column in model.__table__.columns:
        field_name = column.name
        
        # Aplicar filtros
        if fields and field_name not in fields:
            continue
        if exclude and field_name in exclude:
            continue
            
        value = getattr(model, field_name)
        
        # Convertir datetime a ISO format
        if isinstance(value, datetime):
            value = value.isoformat()
            
        data[field_name] = value
    
    return data


def serialize_list(models, fields=None, exclude=None):
    """
    Serializa una lista de modelos
    
    Args:
        models: Lista de instancias de modelos
        fields: Lista de campos a incluir
        exclude: Lista de campos a excluir
        
    Returns:
        list: Lista de modelos serializados
    """
    return [serialize_model(model, fields, exclude) for model in models]

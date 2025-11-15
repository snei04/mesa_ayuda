"""
API de Autenticación
Endpoints para login, logout y registro
"""
from flask import Blueprint, request
from flask_login import login_user, logout_user, current_user
from models import db, Usuario
from utils.api_response import APIResponse, APIError
from utils.validators import UsuarioValidator, Validator

auth_api_bp = Blueprint('auth_api', __name__)


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    
    Body:
        {
            "email": "usuario@example.com"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "es_tecnico": false,
                    "departamento": "Ventas"
                }
            },
            "error": null,
            "meta": {
                "timestamp": "2024-11-13T..."
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Datos inválidos',
            400
        )
    
    email = data.get('email', '').strip()
    
    # Validar email
    is_valid, error_msg = Validator.email(email)
    if not is_valid:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            error_msg,
            400
        )
    
    # Buscar usuario
    usuario = Usuario.query.filter_by(email=email, activo=True).first()
    
    if not usuario:
        return APIResponse.error(
            APIError.INVALID_CREDENTIALS,
            'Usuario no encontrado o inactivo',
            401
        )
    
    # Login exitoso
    login_user(usuario, remember=True)
    
    return APIResponse.success(
        data={
            'user': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'telefono': usuario.telefono,
                'departamento': usuario.departamento,
                'cargo': usuario.cargo,
                'es_tecnico': usuario.es_tecnico
            }
        },
        message=f'¡Bienvenido/a {usuario.nombre}!'
    )


@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    """
    POST /api/auth/logout
    
    Response:
        {
            "success": true,
            "data": null,
            "error": null,
            "meta": {
                "message": "Sesión cerrada correctamente"
            }
        }
    """
    if not current_user.is_authenticated:
        return APIResponse.error(
            APIError.UNAUTHORIZED,
            'No hay sesión activa',
            401
        )
    
    logout_user()
    
    return APIResponse.success(
        message='Sesión cerrada correctamente'
    )


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    
    Body:
        {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "+573001234567",
            "departamento": "Ventas",
            "cargo": "Vendedor"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com"
                }
            },
            "error": null,
            "meta": {
                "message": "Usuario registrado correctamente"
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Datos inválidos',
            400
        )
    
    # Validar datos
    is_valid, errors = UsuarioValidator.validar_registro(data)
    if not is_valid:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'Errores de validación',
            400,
            details=errors
        )
    
    # Verificar si el email ya existe
    usuario_existente = Usuario.query.filter_by(email=data['email']).first()
    if usuario_existente:
        return APIResponse.error(
            APIError.ALREADY_EXISTS,
            'Ya existe un usuario con este correo electrónico',
            409
        )
    
    # Crear usuario
    try:
        nuevo_usuario = Usuario(
            nombre=data['nombre'].strip(),
            email=data['email'].strip().lower(),
            telefono=data.get('telefono', '').strip(),
            departamento=data['departamento'].strip(),
            cargo=data['cargo'].strip(),
            es_tecnico=False,
            activo=True
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return APIResponse.success(
            data={
                'user': {
                    'id': nuevo_usuario.id,
                    'nombre': nuevo_usuario.nombre,
                    'email': nuevo_usuario.email,
                    'departamento': nuevo_usuario.departamento,
                    'cargo': nuevo_usuario.cargo
                }
            },
            message='Usuario registrado correctamente'
        )
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al crear el usuario',
            500,
            details={'error': str(e)}
        )


@auth_api_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    GET /api/auth/me
    
    Obtiene información del usuario actual
    
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "es_tecnico": false
                }
            }
        }
    """
    if not current_user.is_authenticated:
        return APIResponse.error(
            APIError.UNAUTHORIZED,
            'No hay sesión activa',
            401
        )
    
    return APIResponse.success(
        data={
            'user': {
                'id': current_user.id,
                'nombre': current_user.nombre,
                'email': current_user.email,
                'telefono': current_user.telefono,
                'departamento': current_user.departamento,
                'cargo': current_user.cargo,
                'es_tecnico': current_user.es_tecnico
            }
        }
    )


@auth_api_bp.route('/check', methods=['GET'])
def check_auth():
    """
    GET /api/auth/check
    
    Verifica si hay sesión activa
    
    Response:
        {
            "success": true,
            "data": {
                "authenticated": true
            }
        }
    """
    return APIResponse.success(
        data={
            'authenticated': current_user.is_authenticated
        }
    )

import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_magic_token(user_id, expires_in=900):
    """
    Genera un token JWT para login mágico.
    expires_in: tiempo en segundos (default 15 min)
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'sub': user_id,
            'type': 'magic_login'
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)

def verify_magic_token(token):
    """
    Verifica el token y devuelve el user_id si es válido.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=['HS256']
        )
        if payload.get('type') != 'magic_login':
            return None
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        return None # Token expirado
    except jwt.InvalidTokenError:
        return None # Token inválido

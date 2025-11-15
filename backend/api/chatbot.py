"""
API de Chatbot
Endpoints para interacción con el chatbot
"""
from flask import Blueprint, request
from models import db, SesionChatbot
from utils.api_response import APIResponse, APIError, api_login_required
from flask_login import current_user

# Importar el gestor de flujo del chatbot existente
from routes.chatbot import flow_manager, procesar_mensaje_whatsapp

chatbot_api_bp = Blueprint('chatbot_api', __name__)


@chatbot_api_bp.route('/mensaje', methods=['POST'])
@api_login_required
def enviar_mensaje():
    """
    POST /api/chatbot/mensaje
    
    Body:
        {
            "mensaje": "Hola",
            "telefono": "+573001234567"  // Opcional, usa el del usuario actual
        }
    
    Response:
        {
            "success": true,
            "data": {
                "respuesta": {
                    "mensaje": "¡Hola! Soy VisioBot...",
                    "opciones": [...],
                    "tipo": "opciones"
                }
            }
        }
    """
    data = request.get_json()
    
    if not data or 'mensaje' not in data:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'El campo "mensaje" es requerido',
            400
        )
    
    mensaje = data.get('mensaje', '').strip()
    telefono = data.get('telefono', current_user.telefono or f'+57{current_user.id}')
    
    if not mensaje:
        return APIResponse.error(
            APIError.VALIDATION_ERROR,
            'El mensaje no puede estar vacío',
            400
        )
    
    try:
        # Procesar mensaje usando la lógica existente
        respuesta = procesar_mensaje_whatsapp(telefono, mensaje)
        
        return APIResponse.success(data={'respuesta': respuesta})
        
    except Exception as e:
        return APIResponse.error(
            APIError.INTERNAL_ERROR,
            'Error al procesar el mensaje',
            500,
            details={'error': str(e)}
        )


@chatbot_api_bp.route('/sesion', methods=['GET'])
@api_login_required
def obtener_sesion():
    """
    GET /api/chatbot/sesion?telefono=+573001234567
    
    Obtiene la sesión activa del chatbot
    """
    telefono = request.args.get('telefono', current_user.telefono or f'+57{current_user.id}')
    
    sesion = SesionChatbot.query.filter_by(
        usuario_telefono=telefono,
        activa=True
    ).first()
    
    if not sesion:
        return APIResponse.success(data={'sesion': None})
    
    return APIResponse.success(data={
        'sesion': {
            'id': sesion.id,
            'estado_conversacion': sesion.estado_conversacion,
            'datos_temporales': sesion.datos_temporales,
            'fecha_inicio': sesion.fecha_inicio.isoformat() if sesion.fecha_inicio else None
        }
    })


@chatbot_api_bp.route('/sesion', methods=['DELETE'])
@api_login_required
def reiniciar_sesion():
    """
    DELETE /api/chatbot/sesion?telefono=+573001234567
    
    Reinicia la sesión del chatbot
    """
    telefono = request.args.get('telefono', current_user.telefono or f'+57{current_user.id}')
    
    try:
        # Desactivar sesiones anteriores
        sesiones = SesionChatbot.query.filter_by(
            usuario_telefono=telefono,
            activa=True
        ).all()
        
        for sesion in sesiones:
            sesion.activa = False
        
        db.session.commit()
        
        return APIResponse.success(message='Sesión reiniciada correctamente')
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            APIError.DATABASE_ERROR,
            'Error al reiniciar la sesión',
            500,
            details={'error': str(e)}
        )


@chatbot_api_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Webhook para WhatsApp Business API
    Este endpoint NO requiere autenticación (es llamado por WhatsApp)
    """
    if request.method == 'GET':
        # Verificación del webhook
        from config import Config
        verify_token = request.args.get('hub.verify_token')
        if verify_token == Config.WHATSAPP_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Token de verificación inválido', 403
    
    elif request.method == 'POST':
        # Procesar mensaje entrante
        data = request.get_json()
        
        try:
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            
            if 'messages' in value:
                message = value['messages'][0]
                from_number = message['from']
                message_text = message['text']['body']
                
                # Procesar mensaje
                response = procesar_mensaje_whatsapp(from_number, message_text)
                
                # TODO: Enviar respuesta usando WhatsApp Business API
                # enviar_mensaje_whatsapp(from_number, response)
                
        except Exception as e:
            print(f"Error procesando webhook: {e}")
        
        return 'OK', 200

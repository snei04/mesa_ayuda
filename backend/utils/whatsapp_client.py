import requests
import json
from config import Config

class WhatsAppClient:
    """Cliente para interactuar con la API de WhatsApp Cloud"""
    
    BASE_URL = "https://graph.facebook.com/v17.0"
    
    @staticmethod
    def enviar_mensaje(telefono, respuesta_bot):
        """
        Envía un mensaje a WhatsApp basado en la respuesta del bot
        
        Args:
            telefono (str): Número de teléfono del destinatario (con código de país, sin +)
            respuesta_bot (dict): Respuesta generada por el chatbot
        """
        if not Config.WHATSAPP_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
            print("Error: Faltan credenciales de WhatsApp (TOKEN o PHONE_NUMBER_ID)")
            return False

        # Limpiar teléfono (quitar + si existe)
        telefono = telefono.replace('+', '')
        
        mensaje_texto = respuesta_bot.get('mensaje', '')
        opciones = respuesta_bot.get('opciones', [])
        tipo = respuesta_bot.get('tipo', 'texto')
        
        try:
            if tipo == 'opciones' and opciones:
                if len(opciones) <= 3:
                    return WhatsAppClient._enviar_botones(telefono, mensaje_texto, opciones)
                else:
                    return WhatsAppClient._enviar_lista(telefono, mensaje_texto, opciones)
            else:
                # Texto simple (para 'texto_libre', 'final' o 'error')
                return WhatsAppClient._enviar_texto(telefono, mensaje_texto)
                
        except Exception as e:
            print(f"Error enviando mensaje a WhatsApp: {e}")
            return False

    @staticmethod
    def _enviar_texto(telefono, texto):
        url = f"{WhatsAppClient.BASE_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": telefono,
            "type": "text",
            "text": {"body": texto}
        }
        
        response = requests.post(url, headers=headers, json=data)
        return WhatsAppClient._procesar_respuesta(response)

    @staticmethod
    def _enviar_botones(telefono, texto, opciones):
        url = f"{WhatsAppClient.BASE_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        buttons = []
        for op in opciones:
            # ID debe ser único y corto (usamos el valor)
            # Title máx 20 caracteres
            title = op['texto']
            if len(title) > 20:
                title = title[:17] + "..."
                
            buttons.append({
                "type": "reply",
                "reply": {
                    "id": op['valor'],
                    "title": title
                }
            })
            
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": telefono,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": texto},
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return WhatsAppClient._procesar_respuesta(response)

    @staticmethod
    def _enviar_lista(telefono, texto, opciones):
        url = f"{WhatsAppClient.BASE_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        rows = []
        for op in opciones:
            # Title máx 24 caracteres
            title = op['texto']
            description = ""
            
            if len(title) > 24:
                # Intentar mover parte al description
                description = title[24:]
                title = title[:21] + "..."
                if len(description) > 72:
                    description = description[:69] + "..."
            
            rows.append({
                "id": op['valor'],
                "title": title,
                "description": description
            })
            
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": telefono,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Opciones"
                },
                "body": {
                    "text": texto[:1024] # Body máx 1024
                },
                "footer": {
                    "text": "Selecciona una opción"
                },
                "action": {
                    "button": "Ver opciones",
                    "sections": [
                        {
                            "title": "Menú",
                            "rows": rows
                        }
                    ]
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return WhatsAppClient._procesar_respuesta(response)

    @staticmethod
    def _procesar_respuesta(response):
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Error API WhatsApp ({response.status_code}): {response.text}")
            return False

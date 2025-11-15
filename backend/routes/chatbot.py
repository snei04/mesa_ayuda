from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import db, SesionChatbot, Usuario, Ticket, BaseConocimiento
from config import Config
import json
import re

chatbot_bp = Blueprint('chatbot', __name__)

class ChatbotFlowManager:
    """Gestor del flujo de conversación del chatbot"""
    
    def __init__(self):
        self.estados = {
            'inicio': self.estado_inicio,
            'seleccionar_tipo': self.estado_seleccionar_tipo,
            'seleccionar_categoria': self.estado_seleccionar_categoria,
            'seleccionar_subcategoria': self.estado_seleccionar_categoria,
            'buscar_solucion': self.estado_buscar_solucion,
            'crear_ticket': self.estado_crear_ticket,
            'recopilar_descripcion': self.estado_recopilar_descripcion,
            'confirmar_ticket': self.estado_confirmar_ticket,
            'finalizado': self.estado_finalizado
        }
    
    def procesar_mensaje(self, sesion, mensaje):
        """Procesa un mensaje y devuelve la respuesta del bot"""
        estado_actual = sesion.estado_conversacion
        
        if estado_actual in self.estados:
            return self.estados[estado_actual](sesion, mensaje)
        else:
            return self.estado_inicio(sesion, mensaje)
    
    def estado_inicio(self, sesion, mensaje):
        """Estado inicial del chatbot"""
        # No cambiar el estado aún, solo mostrar bienvenida
        sesion.datos_temporales = {}
        
        # Si es el primer mensaje (cualquier mensaje), mostrar bienvenida
        sesion.estado_conversacion = 'seleccionar_tipo'
        
        return {
            'mensaje': '¡Hola! Soy VisioBot, tu asistente de TI de FocusIT 🤖\n\n'
                      'Estoy aquí para ayudarte. ¿Qué necesitas hoy?',
            'opciones': [
                {'texto': '🔧 Solucionar un problema', 'valor': 'problema'},
                {'texto': '📝 Hacer una solicitud', 'valor': 'solicitud'},
                {'texto': '❓ Consulta general', 'valor': 'consulta'},
                {'texto': '🔍 Buscar en la base de conocimiento', 'valor': 'buscar'}
            ],
            'tipo': 'opciones'
        }
    
    def estado_seleccionar_tipo(self, sesion, mensaje):
        """Usuario selecciona el tipo de ayuda que necesita"""
        tipo_seleccionado = mensaje.lower().strip()
        
        # Debug: ver qué mensaje llega
        print(f"Debug - Estado seleccionar_tipo - Mensaje recibido: '{mensaje}'")
        print(f"Debug - Estado seleccionar_tipo - Tipo seleccionado: '{tipo_seleccionado}'")
        
        # Mapear respuestas a tipos
        mapeo_tipos = {
            'problema': 'problemas_tecnicos',
            'solicitud': 'solicitudes_software',
            'consulta': 'consultas_generales',
            'buscar': 'buscar_conocimiento'
        }
        
        print(f"Debug - Estado seleccionar_tipo - Mapeo disponible: {list(mapeo_tipos.keys())}")
        
        if tipo_seleccionado in mapeo_tipos:
            if tipo_seleccionado == 'buscar':
                return self.estado_buscar_solucion(sesion, '')
            
            sesion.datos_temporales['tipo'] = mapeo_tipos[tipo_seleccionado]
            sesion.estado_conversacion = 'seleccionar_categoria'
            
            categoria_info = Config.MAIN_CATEGORIES.get(mapeo_tipos[tipo_seleccionado], {})
            
            # Debug: imprimir información
            print(f"Debug - Tipo seleccionado: {tipo_seleccionado}")
            print(f"Debug - Mapeo: {mapeo_tipos[tipo_seleccionado]}")
            print(f"Debug - Categoria info: {categoria_info}")
            print(f"Debug - Subcategorias: {categoria_info.get('subcategories', {})}")
            
            return {
                'mensaje': f'Perfecto, me dices que necesitas ayuda con: **{categoria_info.get("name", "Ayuda general")}**\n\n'
                          'Para ayudarte mejor, ¿podrías ser más específico?',
                'opciones': [
                    {'texto': subcat_name, 'valor': subcat_key}
                    for subcat_key, subcat_name in categoria_info.get('subcategories', {}).items()
                ],
                'tipo': 'opciones'
            }
        else:
            return {
                'mensaje': 'No entendí tu selección. Por favor elige una de las opciones:',
                'opciones': [
                    {'texto': '🔧 Solucionar un problema', 'valor': 'problema'},
                    {'texto': '📝 Hacer una solicitud', 'valor': 'solicitud'},
                    {'texto': '❓ Consulta general', 'valor': 'consulta'},
                    {'texto': '🔍 Buscar en la base de conocimiento', 'valor': 'buscar'}
                ],
                'tipo': 'opciones'
            }
    
    def estado_seleccionar_categoria(self, sesion, mensaje):
        """Usuario selecciona la categoría específica"""
        subcategoria = mensaje.strip()
        categoria = sesion.datos_temporales.get('tipo')
        
        # Verificar que la subcategoría es válida
        categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
        subcategorias_validas = categoria_info.get('subcategories', {})
        
        if subcategoria in subcategorias_validas:
            sesion.datos_temporales['categoria'] = categoria
            sesion.datos_temporales['subcategoria'] = subcategoria
            sesion.estado_conversacion = 'buscar_solucion'
            
            # Buscar artículos relacionados automáticamente
            return self.buscar_articulos_relacionados(sesion, subcategorias_validas[subcategoria])
        else:
            return {
                'mensaje': 'Por favor selecciona una de las opciones disponibles:',
                'opciones': [
                    {'texto': subcat_name, 'valor': subcat_key}
                    for subcat_key, subcat_name in subcategorias_validas.items()
                ],
                'tipo': 'opciones'
            }
    
    def buscar_articulos_relacionados(self, sesion, nombre_subcategoria):
        """Busca artículos relacionados con la categoría/subcategoría"""
        categoria = sesion.datos_temporales.get('categoria')
        subcategoria = sesion.datos_temporales.get('subcategoria')
        
        # Buscar artículos en la base de conocimiento
        articulos = BaseConocimiento.query.filter_by(
            categoria=categoria,
            subcategoria=subcategoria,
            activo=True
        ).order_by(BaseConocimiento.vistas.desc()).limit(3).all()
        
        if articulos:
            mensaje = f'Entiendo que necesitas ayuda con: **{nombre_subcategoria}**\n\n'
            mensaje += '🔍 Encontré algunos artículos que podrían ayudarte:\n\n'
            
            for i, articulo in enumerate(articulos, 1):
                mensaje += f'{i}. **{articulo.titulo}**\n'
                mensaje += f'   _{articulo.contenido[:100]}..._\n\n'
            
            mensaje += '¿Alguno de estos artículos resuelve tu problema?'
            
            opciones = [
                {'texto': f'📖 Ver artículo {i+1}', 'valor': f'ver_articulo_{articulo.id}'}
                for i, articulo in enumerate(articulos)
            ]
            opciones.append({'texto': '❌ Ninguno me ayuda', 'valor': 'crear_ticket'})
            opciones.append({'texto': '🔄 Buscar otra cosa', 'valor': 'reiniciar'})
            
            return {
                'mensaje': mensaje,
                'opciones': opciones,
                'tipo': 'opciones'
            }
        else:
            # No hay artículos, proceder a crear ticket
            sesion.estado_conversacion = 'crear_ticket'
            return {
                'mensaje': f'Entiendo que necesitas ayuda con: **{nombre_subcategoria}**\n\n'
                          'No encontré artículos específicos para este tema, pero puedo ayudarte creando un ticket para que un técnico te asista.\n\n'
                          '¿Te parece bien que creemos un ticket de soporte?',
                'opciones': [
                    {'texto': '✅ Sí, crear ticket', 'valor': 'si_crear'},
                    {'texto': '🔄 Buscar otra cosa', 'valor': 'reiniciar'}
                ],
                'tipo': 'opciones'
            }
    
    def estado_buscar_solucion(self, sesion, mensaje):
        """Maneja las respuestas cuando se muestran artículos"""
        if mensaje.startswith('ver_articulo_'):
            articulo_id = int(mensaje.split('_')[-1])
            articulo = BaseConocimiento.query.get(articulo_id)
            
            if articulo:
                # Incrementar vistas
                articulo.incrementar_vistas()
                
                return {
                    'mensaje': f'📖 **{articulo.titulo}**\n\n{articulo.contenido}\n\n'
                              '¿Te ayudó esta información?',
                    'opciones': [
                        {'texto': '✅ Sí, problema resuelto', 'valor': 'resuelto'},
                        {'texto': '❌ No, necesito más ayuda', 'valor': 'crear_ticket'},
                        {'texto': '🔄 Buscar otra cosa', 'valor': 'reiniciar'}
                    ],
                    'tipo': 'opciones'
                }
        
        elif mensaje == 'crear_ticket':
            sesion.estado_conversacion = 'crear_ticket'
            return self.estado_crear_ticket(sesion, 'si_crear')
        
        elif mensaje == 'reiniciar':
            return self.estado_inicio(sesion, '')
        
        elif mensaje == 'resuelto':
            sesion.estado_conversacion = 'finalizado'
            return {
                'mensaje': '¡Excelente! Me alegra haber podido ayudarte 😊\n\n'
                          'Si necesitas ayuda en el futuro, no dudes en contactarme.\n\n'
                          '¡Que tengas un buen día!',
                'tipo': 'final'
            }
        
        return {
            'mensaje': 'No entendí tu respuesta. Por favor selecciona una de las opciones disponibles.',
            'tipo': 'error'
        }
    
    def estado_crear_ticket(self, sesion, mensaje):
        """Inicia el proceso de creación de ticket"""
        if mensaje == 'si_crear':
            sesion.estado_conversacion = 'recopilar_descripcion'
            
            categoria = sesion.datos_temporales.get('categoria', '')
            subcategoria = sesion.datos_temporales.get('subcategoria', '')
            
            categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
            subcategoria_nombre = categoria_info.get('subcategories', {}).get(subcategoria, subcategoria)
            
            return {
                'mensaje': f'Perfecto, voy a crear un ticket de soporte para: **{subcategoria_nombre}**\n\n'
                          'Para que el técnico pueda ayudarte mejor, por favor describe tu problema con el mayor detalle posible:\n\n'
                          '• ¿Qué estabas haciendo cuando ocurrió?\n'
                          '• ¿Qué mensaje de error aparece (si hay alguno)?\n'
                          '• ¿Desde cuándo ocurre este problema?\n\n'
                          'Escribe tu descripción completa:',
                'tipo': 'texto_libre'
            }
        else:
            return self.estado_inicio(sesion, '')
    
    def estado_recopilar_descripcion(self, sesion, mensaje):
        """Recopila la descripción detallada del problema"""
        if len(mensaje.strip()) < 10:
            return {
                'mensaje': 'Por favor proporciona una descripción más detallada (mínimo 10 caracteres). '
                          'Esto ayudará al técnico a entender mejor tu problema.',
                'tipo': 'texto_libre'
            }
        
        sesion.datos_temporales['descripcion'] = mensaje.strip()
        sesion.estado_conversacion = 'confirmar_ticket'
        
        # Generar título automático basado en la categoría
        categoria = sesion.datos_temporales.get('categoria', '')
        subcategoria = sesion.datos_temporales.get('subcategoria', '')
        
        categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
        subcategoria_nombre = categoria_info.get('subcategories', {}).get(subcategoria, subcategoria)
        
        titulo_sugerido = f"Problema con {subcategoria_nombre}"
        sesion.datos_temporales['titulo'] = titulo_sugerido
        
        return {
            'mensaje': f'Perfecto, aquí está el resumen de tu ticket:\n\n'
                      f'**Categoría:** {categoria_info.get("name", categoria)}\n'
                      f'**Subcategoría:** {subcategoria_nombre}\n'
                      f'**Título:** {titulo_sugerido}\n'
                      f'**Descripción:** {mensaje[:100]}{"..." if len(mensaje) > 100 else ""}\n\n'
                      '¿Confirmas que quieres crear este ticket?',
            'opciones': [
                {'texto': '✅ Sí, crear ticket', 'valor': 'confirmar'},
                {'texto': '✏️ Modificar descripción', 'valor': 'modificar'},
                {'texto': '❌ Cancelar', 'valor': 'cancelar'}
            ],
            'tipo': 'opciones'
        }
    
    def estado_confirmar_ticket(self, sesion, mensaje):
        """Confirma y crea el ticket"""
        if mensaje == 'confirmar':
            # Buscar usuario por teléfono
            usuario = Usuario.query.filter_by(
                telefono=sesion.usuario_telefono,
                activo=True
            ).first()
            
            if not usuario:
                return {
                    'mensaje': 'Para crear el ticket necesito que te registres en nuestro sistema.\n\n'
                              'Por favor visita: [Portal FocusIT] y regístrate con este número de teléfono.\n\n'
                              'Una vez registrado, podrás crear tickets desde aquí.',
                    'tipo': 'final'
                }
            
            # Crear el ticket
            nuevo_ticket = Ticket(
                usuario_id=usuario.id,
                categoria=sesion.datos_temporales['categoria'],
                subcategoria=sesion.datos_temporales['subcategoria'],
                titulo=sesion.datos_temporales['titulo'],
                descripcion=sesion.datos_temporales['descripcion'],
                prioridad='media',
                estado='nuevo',
                origen='whatsapp',
                datos_adicionales={'chatbot_session': sesion.id}
            )
            
            db.session.add(nuevo_ticket)
            db.session.commit()
            
            sesion.estado_conversacion = 'finalizado'
            
            return {
                'mensaje': f'¡Ticket creado exitosamente! 🎉\n\n'
                          f'**Número de ticket:** #{nuevo_ticket.id}\n'
                          f'**Estado:** Nuevo\n\n'
                          f'Un técnico revisará tu caso y te contactará pronto.\n\n'
                          f'Puedes hacer seguimiento en: [Portal FocusIT]\n\n'
                          '¡Gracias por usar FocusIT!',
                'tipo': 'final'
            }
        
        elif mensaje == 'modificar':
            sesion.estado_conversacion = 'recopilar_descripcion'
            return {
                'mensaje': 'Perfecto, escribe nuevamente la descripción de tu problema:',
                'tipo': 'texto_libre'
            }
        
        else:  # cancelar
            sesion.estado_conversacion = 'finalizado'
            return {
                'mensaje': 'Ticket cancelado. Si necesitas ayuda en el futuro, no dudes en contactarme.\n\n'
                          '¡Que tengas un buen día!',
                'tipo': 'final'
            }
    
    def estado_finalizado(self, sesion, mensaje):
        """Estado final - reiniciar conversación"""
        return self.estado_inicio(sesion, mensaje)

# Instancia global del gestor de flujo
flow_manager = ChatbotFlowManager()

@chatbot_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook para WhatsApp Business API"""
    if request.method == 'GET':
        # Verificación del webhook
        verify_token = request.args.get('hub.verify_token')
        if verify_token == Config.WHATSAPP_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Token de verificación inválido', 403
    
    elif request.method == 'POST':
        # Procesar mensaje entrante
        data = request.get_json()
        
        # Extraer información del mensaje
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
                
                # Enviar respuesta (implementar según API de WhatsApp)
                # enviar_mensaje_whatsapp(from_number, response)
                
        except Exception as e:
            print(f"Error procesando webhook: {e}")
        
        return 'OK', 200

def procesar_mensaje_whatsapp(telefono, mensaje):
    """Procesa un mensaje de WhatsApp y devuelve la respuesta"""
    print(f"Debug - procesar_mensaje_whatsapp - Teléfono: {telefono}, Mensaje: '{mensaje}'")
    
    # Buscar o crear sesión
    sesion = SesionChatbot.query.filter_by(
        usuario_telefono=telefono,
        activa=True
    ).first()
    
    if not sesion:
        print("Debug - Creando nueva sesión")
        sesion = SesionChatbot(
            usuario_telefono=telefono,
            estado_conversacion='inicio',
            datos_temporales={},
            activa=True
        )
        db.session.add(sesion)
        db.session.commit()
    else:
        print(f"Debug - Sesión existente encontrada - Estado: {sesion.estado_conversacion}")
    
    # Procesar mensaje con el gestor de flujo
    respuesta = flow_manager.procesar_mensaje(sesion, mensaje)
    
    # Actualizar sesión
    db.session.commit()
    
    print(f"Debug - Respuesta generada: {respuesta}")
    return respuesta

@chatbot_bp.route('/test')
@login_required
def test():
    """Interfaz de prueba del chatbot"""
    return render_template('chatbot/test.html')

@chatbot_bp.route('/test_message', methods=['POST'])
@login_required
def test_message():
    """API para probar el chatbot desde la interfaz web"""
    data = request.get_json()
    mensaje = data.get('mensaje', '')
    telefono = data.get('telefono', current_user.telefono or '+57300000000')
    
    # Si es el primer mensaje "Hola", limpiar sesiones anteriores
    if mensaje.lower().strip() in ['hola', 'hello', 'hi']:
        # Desactivar sesiones anteriores
        sesiones_anteriores = SesionChatbot.query.filter_by(
            usuario_telefono=telefono,
            activa=True
        ).all()
        for sesion in sesiones_anteriores:
            sesion.activa = False
        db.session.commit()
        print("Debug - Sesiones anteriores desactivadas")
    
    respuesta = procesar_mensaje_whatsapp(telefono, mensaje)
    
    return jsonify(respuesta)

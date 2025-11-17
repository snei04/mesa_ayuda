from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import db, SesionChatbot, Usuario, Ticket, BaseConocimiento
from config import Config
import json
import re
from sqlalchemy import or_
import spacy # <-- PASO 4: IMPORTAR SPACY

# --- INICIO PASO 4: Cargar modelo de NLP ---
# Carga el modelo de español de spaCy una vez al iniciar.
try:
    nlp = spacy.load("es_core_news_sm")
except IOError:
    print("="*50)
    print("ERROR: Modelo 'es_core_news_sm' de spaCy no encontrado.")
    print("Por favor, ejecuta:")
    print("python -m spacy download es_core_news_sm")
    print("="*50)
    nlp = None
# --- FIN PASO 4 ---


chatbot_bp = Blueprint('chatbot', __name__)

# --- INICIO PASO 4: Función de NLP ---
def entender_mensaje_nlp(mensaje):
    """
    Intenta entender la intención y las entidades de un mensaje usando NLP simple.
    """
    if not nlp:
        return None # spaCy no está cargado

    doc = nlp(mensaje.lower())
    
    intencion = None
    entidades = {}

    # 1. Detectar Intención (simple)
    palabras_problema = ['problema', 'error', 'no funciona', 'roto', 'atasco', 'lento', 'caído', 'falla']
    if any(token.lemma_ in palabras_problema for token in doc):
        intencion = 'reportar_problema'

    # 2. Extraer Entidades (basado en tu config.py)
    # En un sistema más avanzado, esto vendría de la Base de Datos
    mapa_entidades = {
        'computador_celular': ['computador', 'pc', 'laptop', 'celular', 'pantalla', 'teclado', 'ratón', 'monitor'],
        'impresoras': ['impresora', 'imprimir', 'factura', 'atasco', 'tinta', 'toner'],
        'software_optica': ['agilmed', 'software', 'aplicativo', 'citas', 'historia'],
        'reset_password': ['contraseña', 'password', 'acceso', 'clave', 'sesión'],
        'carpetas_compartidas': ['carpeta', 'red', 'servidor', 'archivos', 'compartido']
    }

    for token in doc:
        lemma = token.lemma_ # Usamos el lema (ej: "impresoras" -> "impresora")
        for subcategoria, keywords in mapa_entidades.items():
            if lemma in keywords:
                entidades['subcategoria'] = subcategoria
                # Inferir la categoría principal desde la subcategoría
                for cat, data in Config.MAIN_CATEGORIES.items():
                    if subcategoria in data.get('subcategories', {}):
                        entidades['categoria'] = cat
                        break
                break
        if 'categoria' in entidades:
            break # Encontramos lo que necesitábamos

    if intencion and 'categoria' in entidades:
        return {'intencion': intencion, 'entidades': entidades}
    
    return None
# --- FIN PASO 4 ---


class ChatbotFlowManager:
    """Gestor del flujo de conversación del chatbot"""
    
    def __init__(self):
        self.estados = {
            'inicio': self.estado_inicio,
            'seleccionar_tipo': self.estado_seleccionar_tipo,
            'seleccionar_categoria': self.estado_seleccionar_categoria,
            'buscar_solucion': self.estado_buscar_solucion,
            'crear_ticket': self.estado_crear_ticket,
            'recopilar_descripcion': self.estado_recopilar_descripcion,
            'buscar_con_descripcion': self.estado_buscar_con_descripcion,
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
        """Estado inicial del chatbot (con Propuesta 1)"""
        nombre_usuario = sesion.datos_temporales.get('nombre_usuario', "")
        sesion.datos_temporales = {'nombre_usuario': nombre_usuario}
        
        nombre = sesion.datos_temporales.get('nombre_usuario', "")
        saludo = f'¡Hola, {nombre}! Soy VisioBot' if nombre else '¡Hola! Soy VisioBot'
        
        sesion.estado_conversacion = 'seleccionar_tipo'
        
        return {
            'mensaje': f'{saludo}, tu asistente de TI de FocusIT 🤖\n\n'
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
        
        mapeo_tipos = {
            'problema': 'problemas_tecnicos',
            'solicitud': 'solicitudes_software',
            'consulta': 'consultas_generales',
            'buscar': 'buscar_conocimiento'
        }
        
        if tipo_seleccionado in mapeo_tipos:
            sesion.datos_temporales['tipo'] = mapeo_tipos[tipo_seleccionado]

            if tipo_seleccionado == 'buscar':
                sesion.estado_conversacion = 'buscar_solucion'
                return {
                    'mensaje': 'Perfecto, ¿Qué te gustaría buscar en nuestra base de conocimiento?',
                    'tipo': 'texto_libre'
                }
            
            sesion.estado_conversacion = 'seleccionar_categoria'
            categoria_info = Config.MAIN_CATEGORIES.get(mapeo_tipos[tipo_seleccionado], {})
            
            subcategorias = categoria_info.get('subcategories', {})
            if not subcategorias:
                sesion.datos_temporales['categoria'] = mapeo_tipos[tipo_seleccionado]
                sesion.datos_temporales['subcategoria'] = 'general'
                sesion.estado_conversacion = 'crear_ticket'
                return self.estado_crear_ticket(sesion, 'si_crear') 

            return {
                'mensaje': f'Perfecto, me dices que necesitas ayuda con: **{categoria_info.get("name", "Ayuda general")}**\n\n'
                          'Para ayudarte mejor, ¿podrías ser más específico?',
                'opciones': [
                    {'texto': subcat_name, 'valor': subcat_key}
                    for subcat_key, subcat_name in subcategorias.items()
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
        
        if not categoria:
            return self.estado_inicio(sesion, mensaje)
            
        categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
        subcategorias_validas = categoria_info.get('subcategories', {})
        
        if subcategoria in subcategorias_validas:
            sesion.datos_temporales['categoria'] = categoria
            sesion.datos_temporales['subcategoria'] = subcategoria
            sesion.estado_conversacion = 'buscar_solucion'
            
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
        
        articulos = BaseConocimiento.query.filter_by(
            categoria=categoria,
            subcategoria=subcategoria,
            activo=True
        ).order_by(BaseConocimiento.vistas.desc()).limit(3).all()
        
        if articulos:
            mensaje = f'Entiendo que necesitas ayuda con: **{nombre_subcategoria}**\n\n'
            mensaje += '🔍 Encontré algunos artículos que podrían ayudarte:\n\n'
            
            opciones = []
            for i, articulo in enumerate(articulos, 1):
                mensaje += f'{i}. **{articulo.titulo}**\n'
                mensaje += f'   _{articulo.contenido[:100]}..._\n\n'
                opciones.append({'texto': f'📖 Ver artículo {i}', 'valor': f'ver_articulo_{articulo.id}'})
            
            mensaje += '¿Alguno de estos artículos resuelve tu problema?'
            opciones.append({'texto': '❌ Ninguno me ayuda', 'valor': 'crear_ticket'})
            opciones.append({'texto': '🔄 Buscar otra cosa', 'valor': 'reiniciar'})
            
            return {
                'mensaje': mensaje,
                'opciones': opciones,
                'tipo': 'opciones'
            }
        else:
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
        
        if sesion.datos_temporales.get('tipo') == 'buscar_conocimiento':
            sesion.datos_temporales['descripcion'] = mensaje
            sesion.datos_temporales['tipo'] = None 
            return self.estado_buscar_con_descripcion(sesion, mensaje)
        
        if mensaje.startswith('ver_articulo_'):
            articulo_id = int(mensaje.split('_')[-1])
            articulo = BaseConocimiento.query.get(articulo_id)
            
            if articulo:
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

        elif mensaje == 'crear_ticket_directo':
            sesion.estado_conversacion = 'confirmar_ticket'
            return self.estado_confirmar_ticket(sesion, 'mostrar_resumen')
        
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
            'mensaje': 'No entendí tu respuesta. Por favor selecciona una de las opciones.',
            'tipo': 'error'
        }
    
    def estado_crear_ticket(self, sesion, mensaje):
        """Inicia el proceso de creación de ticket"""
        if mensaje == 'si_crear':
            sesion.estado_conversacion = 'recopilar_descripcion'
            
            categoria = sesion.datos_temporales.get('categoria', '')
            subcategoria = sesion.datos_temporales.get('subcategoria', '')
            
            categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
            subcategoria_nombre = categoria_info.get('subcategories', {}).get(subcategoria, "problema")
            
            return {
                'mensaje': f'Perfecto, voy a crear un ticket de soporte para: **{subcategoria_nombre}**\n\n'
                          'Para que el técnico pueda ayudarte mejor, por favor describe tu problema con el mayor detalle posible:\n\n'
                          '• ¿Qué estabas haciendo cuando ocurrió?\n'
                          '• ¿Qué mensaje de error aparece (si hay alguno)?\n'
                          '• ¿Desde cuándo ocurre este problema?\n\n'
                          'Escribe tu descripción completa:',
                'tipo': 'texto_libre'
            }
        
        elif mensaje == 'reiniciar':
             return self.estado_inicio(sesion, '')
        else:
            return {
                'mensaje': 'No entendí tu respuesta. ¿Creamos un ticket de soporte?',
                'opciones': [
                    {'texto': '✅ Sí, crear ticket', 'valor': 'si_crear'},
                    {'texto': '🔄 Buscar otra cosa', 'valor': 'reiniciar'}
                ],
                'tipo': 'opciones'
            }
    
    def estado_recopilar_descripcion(self, sesion, mensaje):
        """Recopila la descripción detallada del problema"""
        if len(mensaje.strip()) < 10:
            return {
                'mensaje': 'Por favor proporciona una descripción más detallada (mínimo 10 caracteres). '
                          'Esto ayudará al técnico a entender mejor tu problema.',
                'tipo': 'texto_libre'
            }
        
        sesion.datos_temporales['descripcion'] = mensaje.strip()
        sesion.estado_conversacion = 'buscar_con_descripcion'
        
        categoria = sesion.datos_temporales.get('categoria', '')
        subcategoria = sesion.datos_temporales.get('subcategoria', '')
        
        categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
        subcategoria_nombre = categoria_info.get('subcategories', {}).get(subcategoria, subcategoria)
        
        titulo_sugerido = f"Problema con {subcategoria_nombre}"
        sesion.datos_temporales['titulo'] = titulo_sugerido
        
        return self.estado_buscar_con_descripcion(sesion, "")

    def estado_buscar_con_descripcion(self, sesion, mensaje):
        """Busca artículos usando la descripción del usuario"""
        descripcion = sesion.datos_temporales.get('descripcion', '')
        palabras_clave = [p for p in re.split(r'\s+|,|\.', descripcion) if len(p) > 3]

        articulos = []
        if palabras_clave:
            query_filters = [
                or_(
                    BaseConocimiento.titulo.contains(palabra),
                    BaseConocimiento.contenido.contains(palabra),
                    BaseConocimiento.palabras_clave.contains(palabra)
                ) for palabra in palabras_clave
            ]
            
            articulos = BaseConocimiento.query.filter(
                BaseConocimiento.activo == True
            ).filter(
                or_(*query_filters)
            ).order_by(BaseConocimiento.vistas.desc()).limit(2).all()
        
        if articulos:
            mensaje_respuesta = "¡Un momento! 🔍\n\nBasado en tu descripción, encontré estos artículos que podrían ayudarte:\n\n"
            
            opciones_respuesta = []
            for i, articulo in enumerate(articulos, 1):
                mensaje_respuesta += f'{i}. **{articulo.titulo}**\n'
                mensaje_respuesta += f'   _{articulo.contenido[:100]}..._\n\n'
                opciones_respuesta.append(
                    {'texto': f'📖 Ver Artículo {i}', 'valor': f'ver_articulo_{articulo.id}'}
                )
            
            mensaje_respuesta += '¿Quieres revisarlos o prefieres crear el ticket directamente?'
            opciones_respuesta.append({'texto': '❌ No, crear el ticket', 'valor': 'crear_ticket_directo'})
            
            sesion.estado_conversacion = 'buscar_solucion'
            
            return {
                'mensaje': mensaje_respuesta,
                'opciones': opciones_respuesta,
                'tipo': 'opciones'
            }
        
        sesion.estado_conversacion = 'confirmar_ticket'
        return self.estado_confirmar_ticket(sesion, 'mostrar_resumen')

    def estado_confirmar_ticket(self, sesion, mensaje):
        """Confirma y crea el ticket"""
        
        if mensaje == 'mostrar_resumen':
            categoria = sesion.datos_temporales.get('categoria', '')
            subcategoria = sesion.datos_temporales.get('subcategoria', '')
            titulo_sugerido = sesion.datos_temporales.get('titulo', 'Sin título')
            descripcion = sesion.datos_temporales.get('descripcion', 'Sin descripción')

            if not categoria:
                categoria_nombre = "Consulta General"
                subcategoria_nombre = "Búsqueda"
                titulo_sugerido = f"Consulta: {descripcion[:30]}..."
                sesion.datos_temporales['titulo'] = titulo_sugerido
            else:
                categoria_info = Config.MAIN_CATEGORIES.get(categoria, {})
                categoria_nombre = categoria_info.get("name", categoria)
                subcategoria_nombre = categoria_info.get('subcategories', {}).get(subcategoria, subcategoria)

            return {
                'mensaje': f'Perfecto, aquí está el resumen de tu ticket:\n\n'
                          f'**Categoría:** {categoria_nombre}\n'
                          f'**Subcategoría:** {subcategoria_nombre}\n'
                          f'**Título:** {titulo_sugerido}\n'
                          f'**Descripción:** {descripcion[:100]}{"..." if len(descripcion) > 100 else ""}\n\n'
                          '¿Confirmas que quieres crear este ticket?',
                'opciones': [
                    {'texto': '✅ Sí, crear ticket', 'valor': 'confirmar'},
                    {'texto': '✏️ Modificar descripción', 'valor': 'modificar'},
                    {'texto': '❌ Cancelar', 'valor': 'cancelar'}
                ],
                'tipo': 'opciones'
            }
        
        elif mensaje == 'confirmar':
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
            
            categoria = sesion.datos_temporales.get('categoria', 'consultas_generales')
            subcategoria = sesion.datos_temporales.get('subcategoria', 'soporte_general')
            
            nuevo_ticket = Ticket(
                usuario_id=usuario.id,
                categoria=categoria,
                subcategoria=subcategoria,
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
                          'Puedes hacer seguimiento en: [Portal FocusIT]\n\n'
                          '¡Gracias por usar FocusIT!',
                'tipo': 'final'
            }
        
        elif mensaje == 'modificar':
            sesion.estado_conversacion = 'recopilar_descripcion'
            return {
                'mensaje': 'Perfecto, escribe nuevamente la descripción de tu problema:',
                'tipo': 'texto_libre'
            }
        
        else:  # cancelar (o cualquier otra cosa no reconocida)
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
        verify_token = request.args.get('hub.verify_token')
        if verify_token == Config.WHATSAPP_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Token de verificación inválido', 403
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            
            if 'messages' in value:
                message = value['messages'][0]
                from_number = message['from']
                message_text = message['text']['body']
                response = procesar_mensaje_whatsapp(from_number, message_text)
                # TODO: Enviar respuesta usando WhatsApp Business API
                # enviar_mensaje_whatsapp(from_number, response)
                
        except Exception as e:
            print(f"Error procesando webhook: {e}")
        return 'OK', 200


# --- INICIO PASO 4: Refactorización de procesar_mensaje_whatsapp ---
def procesar_mensaje_whatsapp(telefono, mensaje):
    """Procesa un mensaje de WhatsApp y devuelve la respuesta"""
    print(f"Debug - procesar_mensaje_whatsapp - Teléfono: {telefono}, Mensaje: '{mensaje}'")
    
    usuario = Usuario.query.filter_by(telefono=telefono, activo=True).first()
    sesion = SesionChatbot.query.filter_by(
        usuario_telefono=telefono,
        activa=True
    ).first()
    
    mensaje_limpio = mensaje.lower().strip()

    # --- Lógica de Sesión y Globales (Propuesta 3) ---

    # 1. Manejar reinicios de sesión
    if mensaje_limpio in ['hola', 'hello', 'hi', 'reiniciar', 'menú', 'menu', 'inicio']:
        if sesion:
            sesion.activa = False
            db.session.commit()
            print("Debug - Sesión existente desactivada por saludo o reinicio.")
        
        sesion = SesionChatbot(
            usuario_telefono=telefono,
            estado_conversacion='inicio',
            datos_temporales={},
            activa=True,
            usuario_id=usuario.id if usuario else None 
        )
        db.session.add(sesion)
        print("Debug - Creando nueva sesión.")
    
    # 2. Si no hay sesión, crearla
    if not sesion:
        sesion = SesionChatbot(
            usuario_telefono=telefono,
            estado_conversacion='inicio',
            datos_temporales={},
            activa=True,
            usuario_id=usuario.id if usuario else None 
        )
        db.session.add(sesion)
        print("Debug - Creando nueva sesión para primer mensaje.")
    
    # 3. Lógica de personalización (Propuesta 1)
    if 'nombre_usuario' not in sesion.datos_temporales or not sesion.datos_temporales.get('nombre_usuario'):
        if usuario and usuario.nombre:
            sesion.datos_temporales['nombre_usuario'] = usuario.nombre.split(' ')[0]
        else:
            sesion.datos_temporales['nombre_usuario'] = ""
    
    if not sesion.usuario_id and usuario:
        sesion.usuario_id = usuario.id

    # 4. Filtro de Intenciones Globales (Propuesta 3)
    if mensaje_limpio in ['cancelar', 'salir', 'adiós', 'chao', 'cancel']:
        sesion.activa = False
        sesion.estado_conversacion = 'finalizado'
        db.session.commit()
        return {
            'mensaje': 'Entendido. He cancelado el proceso. Si necesitas algo más, solo di "hola". ¡Que tengas un buen día!',
            'tipo': 'final'
        }
    
    # 5. Si fue un reinicio o "hola", llamar a 'estado_inicio'
    if mensaje_limpio in ['hola', 'hello', 'hi', 'reiniciar', 'menú', 'menu', 'inicio']:
        respuesta = flow_manager.estado_inicio(sesion, mensaje)
        db.session.commit()
        print(f"Debug - Respuesta generada (Inicio): {respuesta}")
        return respuesta
    
    # --- INICIO LÓGICA NLP (Propuesta 4) ---
    # Si estamos al inicio del flujo, intentar entender el mensaje.
    if (sesion.estado_conversacion == 'inicio' or sesion.estado_conversacion == 'seleccionar_tipo') and nlp:
        resultado_nlp = entender_mensaje_nlp(mensaje)
        
        if resultado_nlp and resultado_nlp['intencion'] == 'reportar_problema':
            print(f"Debug - NLP detectó: {resultado_nlp}")
            
            # ¡Bypass! Saltamos el menú
            sesion.estado_conversacion = 'buscar_con_descripcion' # Saltamos a la búsqueda de artículos
            entidades = resultado_nlp['entidades']
            
            sesion.datos_temporales['categoria'] = entidades['categoria']
            sesion.datos_temporales['subcategoria'] = entidades['subcategoria']
            sesion.datos_temporales['descripcion'] = mensaje # Usamos el mensaje original como descripción
            
            # Generar título
            categoria_info = Config.MAIN_CATEGORIES.get(entidades['categoria'], {})
            subcategoria_nombre = categoria_info.get('subcategories', {}).get(entidades['subcategoria'], entidades['subcategoria'])
            sesion.datos_temporales['titulo'] = f"Problema con {subcategoria_nombre}"

            # Saltamos directo a la búsqueda de artículos
            respuesta = flow_manager.estado_buscar_con_descripcion(sesion, mensaje)
            db.session.commit()
            print(f"Debug - Respuesta generada (NLP Bypass): {respuesta}")
            return respuesta
    # --- FIN LÓGICA NLP ---

    # Si NLP no detectó nada, o no estábamos al inicio,
    # continuar con la máquina de estados normal.
    respuesta = flow_manager.procesar_mensaje(sesion, mensaje)
    
    db.session.commit()
    
    print(f"Debug - Respuesta generada (Flujo): {respuesta}")
    return respuesta
# --- FIN Refactorización ---


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
    
    # Toda la lógica de sesión ahora está en procesar_mensaje_whatsapp
    respuesta = procesar_mensaje_whatsapp(telefono, mensaje)
    
    return jsonify(respuesta)   
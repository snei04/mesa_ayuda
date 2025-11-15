from app import create_app
from models import db, Usuario, BaseConocimiento
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario administrador por defecto
        admin = Usuario.query.filter_by(email='admin@focusit.com').first()
        if not admin:
            admin = Usuario(
                nombre='Administrador FocusIT',
                email='admin@focusit.com',
                departamento='TI',
                cargo='Administrador del Sistema',
                es_tecnico=True,
                activo=True
            )
            db.session.add(admin)
        
        # Crear algunos técnicos de ejemplo
        tecnico1 = Usuario.query.filter_by(email='tecnico1@focusit.com').first()
        if not tecnico1:
            tecnico1 = Usuario(
                nombre='Juan Pérez',
                email='tecnico1@focusit.com',
                telefono='+57300123456',
                departamento='TI',
                cargo='Técnico de Soporte',
                es_tecnico=True,
                activo=True
            )
            db.session.add(tecnico1)
        
        # Crear usuario de ejemplo
        usuario_ejemplo = Usuario.query.filter_by(email='usuario@optica.com').first()
        if not usuario_ejemplo:
            usuario_ejemplo = Usuario(
                nombre='María González',
                email='usuario@optica.com',
                telefono='+57300654321',
                departamento='Ventas',
                cargo='Optómetra',
                es_tecnico=False,
                activo=True
            )
            db.session.add(usuario_ejemplo)
        
        # Crear artículos de base de conocimiento iniciales
        articulos_iniciales = [
            {
                'titulo': 'Cómo configurar el correo electrónico en el celular',
                'contenido': '''
                **Para Android:**
                1. Abrir la aplicación "Email" o "Gmail"
                2. Seleccionar "Agregar cuenta"
                3. Ingresar tu dirección de correo de la óptica
                4. Ingresar tu contraseña
                5. Configurar servidor IMAP: mail.tuoptica.com, Puerto 993, SSL activado
                
                **Para iPhone:**
                1. Ir a Configuración > Mail > Cuentas
                2. Seleccionar "Agregar cuenta" > "Otra"
                3. Ingresar tu información de correo
                4. Configurar servidor entrante: mail.tuoptica.com, Puerto 993, SSL activado
                ''',
                'palabras_clave': 'correo, email, celular, configurar, android, iphone, gmail',
                'categoria': 'problemas_tecnicos',
                'subcategoria': 'computador_celular'
            },
            {
                'titulo': 'Solucionar problemas de impresión de facturas',
                'contenido': '''
                **Pasos para solucionar problemas comunes:**
                
                1. **Verificar conexión:**
                   - Asegúrate de que la impresora esté encendida
                   - Verifica que el cable USB esté bien conectado
                   
                2. **Revisar papel:**
                   - Confirma que hay papel en la bandeja
                   - Verifica que el papel esté bien alineado
                   
                3. **Reiniciar impresora:**
                   - Apaga la impresora por 30 segundos
                   - Enciéndela nuevamente
                   
                4. **Verificar en el sistema:**
                   - Ve a "Dispositivos e impresoras" en Windows
                   - Busca tu impresora y verifica que no tenga errores
                   
                Si el problema persiste, crea un ticket de soporte.
                ''',
                'palabras_clave': 'impresora, facturas, imprimir, papel, conexion, usb',
                'categoria': 'problemas_tecnicos',
                'subcategoria': 'impresoras'
            },
            {
                'titulo': 'Restablecer contraseña del sistema',
                'contenido': '''
                **Para restablecer tu contraseña:**
                
                1. **Opción 1 - Autoservicio:**
                   - Ve al portal de FocusIT
                   - Haz clic en "¿Olvidaste tu contraseña?"
                   - Ingresa tu correo electrónico
                   - Revisa tu correo y sigue las instrucciones
                   
                2. **Opción 2 - Solicitar ayuda:**
                   - Crea un ticket en el portal
                   - Selecciona "Permisos y Accesos" > "Restablecer Contraseña"
                   - Un técnico te ayudará en menos de 2 horas
                   
                **Requisitos para nueva contraseña:**
                - Mínimo 8 caracteres
                - Al menos una mayúscula
                - Al menos un número
                - Al menos un carácter especial
                ''',
                'palabras_clave': 'contraseña, password, restablecer, olvidé, cambiar, acceso',
                'categoria': 'permisos_accesos',
                'subcategoria': 'reset_password'
            },
            {
                'titulo': 'Acceso a carpetas compartidas de exámenes',
                'contenido': '''
                **Para acceder a las carpetas de resultados de exámenes:**
                
                1. **Desde Windows:**
                   - Abre el Explorador de archivos
                   - En la barra de direcciones escribe: \\\\servidor-optica\\examenes
                   - Ingresa tu usuario y contraseña de la red
                   
                2. **Mapear como unidad de red:**
                   - Clic derecho en "Este equipo"
                   - Seleccionar "Conectar a unidad de red"
                   - Elegir una letra de unidad (ej: E:)
                   - Carpeta: \\\\servidor-optica\\examenes
                   - Marcar "Conectar usando credenciales diferentes"
                   
                **Permisos necesarios:**
                - Solo personal autorizado puede acceder
                - Si no tienes acceso, solicítalo mediante un ticket
                ''',
                'palabras_clave': 'carpetas, compartidas, examenes, resultados, servidor, red, acceso',
                'categoria': 'permisos_accesos',
                'subcategoria': 'carpetas_compartidas'
            }
        ]
        
        for articulo_data in articulos_iniciales:
            articulo_existente = BaseConocimiento.query.filter_by(titulo=articulo_data['titulo']).first()
            if not articulo_existente:
                articulo = BaseConocimiento(
                    titulo=articulo_data['titulo'],
                    contenido=articulo_data['contenido'],
                    palabras_clave=articulo_data['palabras_clave'],
                    categoria=articulo_data['categoria'],
                    subcategoria=articulo_data['subcategoria'],
                    autor_id=1,  # Admin
                    activo=True
                )
                db.session.add(articulo)
        
        # Guardar todos los cambios
        db.session.commit()
        print("✅ Base de datos inicializada correctamente")
        print("📧 Usuario admin: admin@focusit.com")
        print("👨‍💻 Técnico: tecnico1@focusit.com (Juan Pérez)")
        print("👩‍💼 Usuario ejemplo: usuario@optica.com (María González)")
        print(f"📚 {len(articulos_iniciales)} artículos de base de conocimiento creados")

if __name__ == '__main__':
    init_database()

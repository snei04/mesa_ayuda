"""
Script para inicializar la base de datos con datos de ejemplo
"""
import sys
import os

# Agregar la carpeta backend al path de Python
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from backend.app import create_app
from models import db, Usuario, BaseConocimiento
from datetime import datetime

def init_database():
    app = create_app()
    
    with app.app_context():
        print("🔧 Creando tablas en la base de datos...")
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas correctamente")
        
        print("\n👤 Creando usuarios de ejemplo...")
        
        # Crear usuario administrador por defecto
        admin = Usuario.query.filter_by(email='admin@focusit.com').first()
        if not admin:
            admin = Usuario(
                nombre='Administrador FocusIT',
                email='admin@focusit.com',
                telefono='+573001234567',
                departamento='TI',
                cargo='Administrador del Sistema',
                es_tecnico=True,
                activo=True
            )
            db.session.add(admin)
            print("  ✓ Admin creado: admin@focusit.com")
        
        # Crear algunos técnicos de ejemplo
        tecnico1 = Usuario.query.filter_by(email='tecnico1@focusit.com').first()
        if not tecnico1:
            tecnico1 = Usuario(
                nombre='Juan Pérez',
                email='tecnico1@focusit.com',
                telefono='+573001111111',
                departamento='TI',
                cargo='Técnico de Soporte',
                es_tecnico=True,
                activo=True
            )
            db.session.add(tecnico1)
            print("  ✓ Técnico 1 creado: tecnico1@focusit.com")
        
        tecnico2 = Usuario.query.filter_by(email='tecnico2@focusit.com').first()
        if not tecnico2:
            tecnico2 = Usuario(
                nombre='María García',
                email='tecnico2@focusit.com',
                telefono='+573002222222',
                departamento='TI',
                cargo='Técnico de Soporte',
                es_tecnico=True,
                activo=True
            )
            db.session.add(tecnico2)
            print("  ✓ Técnico 2 creado: tecnico2@focusit.com")
        
        # Crear usuarios normales de ejemplo
        usuario1 = Usuario.query.filter_by(email='usuario@focusit.com').first()
        if not usuario1:
            usuario1 = Usuario(
                nombre='Carlos López',
                email='usuario@focusit.com',
                telefono='+573003333333',
                departamento='Ventas',
                cargo='Vendedor',
                es_tecnico=False,
                activo=True
            )
            db.session.add(usuario1)
            print("  ✓ Usuario de prueba creado: usuario@focusit.com")
        
        print("\n📚 Creando artículos de base de conocimiento...")
        
        # Crear algunos artículos de base de conocimiento
        articulos = [
            {
                'titulo': 'Cómo reiniciar una impresora',
                'contenido': '''
**Pasos para reiniciar una impresora correctamente:**

1. Apagar la impresora usando el botón de encendido
2. Desconectar el cable de alimentación
3. Esperar 30 segundos
4. Volver a conectar el cable de alimentación
5. Encender la impresora
6. Esperar a que complete su ciclo de inicio

**Nota:** Si el problema persiste, verificar que los cartuchos estén correctamente instalados.
                ''',
                'palabras_clave': 'impresora, reiniciar, problema, no imprime',
                'categoria': 'problemas_tecnicos',
                'subcategoria': 'impresoras'
            },
            {
                'titulo': 'Restablecer contraseña de Windows',
                'contenido': '''
**Para restablecer tu contraseña de Windows:**

1. Presiona Ctrl + Alt + Supr
2. Selecciona "Cambiar contraseña"
3. Ingresa tu contraseña actual
4. Ingresa la nueva contraseña dos veces
5. Presiona Enter

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos un número
- Al menos un carácter especial

**Importante:** Si olvidaste tu contraseña, contacta al departamento de TI.
                ''',
                'palabras_clave': 'contraseña, password, restablecer, cambiar, windows',
                'categoria': 'permisos_accesos',
                'subcategoria': 'reset_password'
            },
            {
                'titulo': 'Solicitar nueva licencia de software',
                'contenido': '''
**Proceso para solicitar una nueva licencia:**

1. Crear un ticket en el sistema
2. Especificar el software requerido
3. Justificar la necesidad del software
4. Esperar aprobación del supervisor
5. El departamento de TI instalará el software una vez aprobado

**Tiempo estimado:** 2-3 días hábiles

**Nota:** Algunas licencias requieren aprobación de gerencia.
                ''',
                'palabras_clave': 'licencia, software, nuevo, solicitar, instalación',
                'categoria': 'solicitudes_software',
                'subcategoria': 'nuevas_licencias'
            },
            {
                'titulo': 'Mi computador no enciende - Soluciones básicas',
                'contenido': '''
**Verificaciones básicas antes de crear un ticket:**

1. **Verificar conexión eléctrica:**
   - ¿El cable está conectado?
   - ¿El tomacorriente funciona?
   - ¿La regleta está encendida?

2. **Verificar luces indicadoras:**
   - ¿Hay alguna luz encendida en el computador?
   - ¿El monitor está encendido?

3. **Intentar reinicio forzado:**
   - Mantener presionado el botón de encendido por 10 segundos
   - Soltar y volver a presionar

4. **Si nada funciona:**
   - Crear un ticket de soporte
   - Indicar qué verificaciones ya realizaste
   - Especificar si escuchas algún sonido al intentar encender

**Prioridad:** Alta - Respuesta en menos de 2 horas
                ''',
                'palabras_clave': 'computador, no enciende, pc, problema, hardware',
                'categoria': 'problemas_tecnicos',
                'subcategoria': 'computador_celular'
            }
        ]
        
        for art_data in articulos:
            articulo_existente = BaseConocimiento.query.filter_by(
                titulo=art_data['titulo']
            ).first()
            
            if not articulo_existente:
                articulo = BaseConocimiento(
                    titulo=art_data['titulo'],
                    contenido=art_data['contenido'],
                    palabras_clave=art_data['palabras_clave'],
                    categoria=art_data['categoria'],
                    subcategoria=art_data['subcategoria'],
                    autor_id=admin.id if admin else 1,
                    activo=True,
                    vistas=0
                )
                db.session.add(articulo)
                print(f"  ✓ Artículo creado: {art_data['titulo']}")
        
        # Guardar todos los cambios
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ Base de datos inicializada correctamente")
        print("="*60)
        print("\n📋 Usuarios creados:")
        print("  • admin@focusit.com (Administrador)")
        print("  • tecnico1@focusit.com (Técnico)")
        print("  • tecnico2@focusit.com (Técnico)")
        print("  • usuario@focusit.com (Usuario normal)")
        print("\n🔐 Nota: Este sistema usa autenticación sin contraseña")
        print("   Solo ingresa el email para iniciar sesión")
        print("\n🚀 Ejecuta 'python run.py' para iniciar el servidor")
        print("="*60)

if __name__ == '__main__':
    init_database()

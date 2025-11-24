import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno explícitamente
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, Usuario
from sqlalchemy import text

app = create_app()

print(f"🔌 Conectando a: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    # Crear tablas si no existen
    db.create_all()
    print("✅ Tablas verificadas/creadas.")
    
    try:
        # Intentar agregar la columna por si la tabla ya existía pero le falta la columna
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN password_hash VARCHAR(256);"))
            conn.commit()
            print("✅ Columna password_hash agregada exitosamente.")
    except Exception as e:
        print(f"ℹ️ Nota (si dice 'duplicate column' es normal): {e}")
        
    # Crear usuario admin si no existe
    if not Usuario.query.filter_by(email='admin@focusit.com').first():
        admin = Usuario(
            nombre='Administrador',
            email='admin@focusit.com',
            cargo='Admin',
            es_tecnico=True,
            activo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("👤 Usuario admin creado: admin@focusit.com / admin123")


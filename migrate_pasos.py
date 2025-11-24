import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno explícitamente
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, PasoGuia

app = create_app()

print(f"🔌 Conectando a: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        # Crear tabla pasos_guia
        db.create_all()
        print("✅ Tabla 'pasos_guia' creada exitosamente.")
    except Exception as e:
        print(f"❌ Error: {e}")

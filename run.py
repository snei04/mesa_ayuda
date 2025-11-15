"""
Punto de entrada principal para ejecutar la aplicación FocusIT
"""
import sys
import os

# Agregar la carpeta backend al path de Python
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models import db
        db.create_all()
    
    print("=" * 60)
    print("🚀 FocusIT - Sistema de Mesa de Ayuda")
    print("=" * 60)
    print("📍 Servidor corriendo en: http://localhost:5000")
    print("📖 API REST disponible en: http://localhost:5000/api")
    print("📚 Documentación: docs/API_DOCUMENTATION.md")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

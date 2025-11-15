"""
Script para verificar que la estructura del proyecto está correcta
"""
import os
import sys

def check_file(path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} NO ENCONTRADO: {path}")
        return False

def check_dir(path, description):
    """Verifica si un directorio existe"""
    if os.path.isdir(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} NO ENCONTRADO: {path}")
        return False

def main():
    print("="*60)
    print("🔍 Verificando estructura del proyecto FocusIT")
    print("="*60)
    
    all_ok = True
    
    # Verificar estructura de carpetas principales
    print("\n📁 Verificando carpetas principales...")
    all_ok &= check_dir("frontend", "Frontend")
    all_ok &= check_dir("backend", "Backend")
    all_ok &= check_dir("docs", "Documentación")
    all_ok &= check_dir("instance", "Instance (BD)")
    
    # Verificar frontend
    print("\n🎨 Verificando frontend...")
    all_ok &= check_dir("frontend/templates", "Templates")
    all_ok &= check_dir("frontend/static", "Static")
    all_ok &= check_dir("frontend/static/css", "CSS")
    all_ok &= check_dir("frontend/static/js", "JavaScript")
    all_ok &= check_file("frontend/templates/base.html", "Base template")
    all_ok &= check_file("frontend/templates/index.html", "Index template")
    all_ok &= check_file("frontend/static/js/api-client.js", "API Client JS")
    
    # Verificar backend
    print("\n⚙️ Verificando backend...")
    all_ok &= check_file("backend/app.py", "App principal")
    all_ok &= check_file("backend/config.py", "Configuración")
    all_ok &= check_dir("backend/models", "Modelos")
    all_ok &= check_dir("backend/routes", "Rutas web")
    all_ok &= check_dir("backend/api", "API REST")
    all_ok &= check_dir("backend/utils", "Utilidades")
    
    # Verificar API
    print("\n🔌 Verificando API REST...")
    all_ok &= check_file("backend/api/__init__.py", "API Init")
    all_ok &= check_file("backend/api/auth.py", "API Auth")
    all_ok &= check_file("backend/api/tickets.py", "API Tickets")
    all_ok &= check_file("backend/api/knowledge.py", "API Knowledge")
    all_ok &= check_file("backend/api/dashboard.py", "API Dashboard")
    all_ok &= check_file("backend/api/chatbot.py", "API Chatbot")
    
    # Verificar utilidades
    print("\n🛠️ Verificando utilidades...")
    all_ok &= check_file("backend/utils/api_response.py", "API Response")
    all_ok &= check_file("backend/utils/validators.py", "Validators")
    
    # Verificar documentación
    print("\n📚 Verificando documentación...")
    all_ok &= check_file("docs/API_DOCUMENTATION.md", "Documentación API")
    all_ok &= check_file("docs/ARQUITECTURA.md", "Arquitectura")
    all_ok &= check_file("docs/FRONTEND_BACKEND_SEPARATION.md", "Separación F/B")
    
    # Verificar archivos raíz
    print("\n📄 Verificando archivos raíz...")
    all_ok &= check_file("run.py", "Run script")
    all_ok &= check_file("init_db.py", "Init DB script")
    all_ok &= check_file("requirements.txt", "Requirements")
    all_ok &= check_file("README.md", "README")
    all_ok &= check_file("QUICK_START.md", "Quick Start")
    all_ok &= check_file(".gitignore", "Gitignore")
    
    # Resultado final
    print("\n" + "="*60)
    if all_ok:
        print("✅ ¡Estructura del proyecto verificada correctamente!")
        print("="*60)
        print("\n🚀 Próximos pasos:")
        print("  1. python init_db.py  # Inicializar base de datos")
        print("  2. python run.py      # Ejecutar aplicación")
        print("\n📖 Documentación:")
        print("  - QUICK_START.md      # Guía rápida")
        print("  - docs/               # Documentación completa")
        return 0
    else:
        print("❌ Hay problemas con la estructura del proyecto")
        print("="*60)
        print("\n⚠️ Revisa los archivos marcados con ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())

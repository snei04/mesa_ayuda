from dotenv import load_dotenv
import os

# Cargar desde la ruta absoluta exacta
env_path = '/home/snei05/aprendo/mesa_ayuda/focusit/.env'
load_dotenv(env_path)

print(f"Ruta: {env_path}")
print(f"Existe: {os.path.exists(env_path)}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

with open(env_path, 'r') as f:
    print("Contenido (primeras lineas):")
    print(f.read(50))

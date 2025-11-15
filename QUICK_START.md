# 🚀 Guía Rápida - FocusIT

## ⚡ Inicio Rápido

### 1. Instalación
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Inicializar Base de Datos
```bash
python init_db.py
```

Esto creará:
- ✅ Tablas de la base de datos
- ✅ Usuario administrador: `admin@focusit.com`
- ✅ Técnicos de ejemplo: `tecnico1@focusit.com`, `tecnico2@focusit.com`
- ✅ Usuario de prueba: `usuario@focusit.com`
- ✅ Artículos de base de conocimiento

### 3. Ejecutar Aplicación
```bash
python run.py
```

Accede a:
- 🌐 **Web:** http://localhost:5000
- 🔌 **API REST:** http://localhost:5000/api
- 📖 **Documentación API:** http://localhost:5000/api (próximamente Swagger)

---

## 📁 Estructura del Proyecto

```
focusit/
├── frontend/          # Todo lo relacionado con la interfaz
│   ├── templates/     # HTML
│   └── static/        # CSS, JS, imágenes
│
├── backend/           # Toda la lógica del servidor
│   ├── app.py         # Aplicación Flask
│   ├── models/        # Modelos de base de datos
│   ├── routes/        # Rutas web (HTML)
│   ├── api/           # API REST (JSON)
│   └── utils/         # Utilidades
│
├── docs/              # Documentación
├── run.py             # Ejecutar aplicación
└── init_db.py         # Inicializar BD
```

---

## 🔑 Usuarios de Prueba

| Email | Rol | Descripción |
|-------|-----|-------------|
| `admin@focusit.com` | Administrador | Acceso completo al sistema |
| `tecnico1@focusit.com` | Técnico | Puede gestionar tickets |
| `tecnico2@focusit.com` | Técnico | Puede gestionar tickets |
| `usuario@focusit.com` | Usuario | Puede crear tickets |

**Nota:** Este sistema usa autenticación sin contraseña. Solo ingresa el email.

---

## 🛠️ Tareas Comunes

### Crear un Nuevo Endpoint API

1. **Agregar función en el archivo API correspondiente:**
```python
# backend/api/tickets.py

@tickets_api_bp.route('/mi-nuevo-endpoint', methods=['GET'])
@api_login_required
def mi_nuevo_endpoint():
    # Tu lógica aquí
    return APIResponse.success(data={'mensaje': 'Hola'})
```

2. **Probar el endpoint:**
```bash
curl http://localhost:5000/api/tickets/mi-nuevo-endpoint
```

### Agregar una Nueva Ruta Web

1. **Agregar función en el archivo de rutas:**
```python
# backend/routes/tickets.py

@tickets_bp.route('/mi-nueva-pagina')
@login_required
def mi_nueva_pagina():
    return render_template('tickets/mi_pagina.html')
```

2. **Crear el template:**
```html
<!-- frontend/templates/tickets/mi_pagina.html -->
{% extends "base.html" %}

{% block content %}
<h1>Mi Nueva Página</h1>
{% endblock %}
```

### Agregar un Nuevo Modelo

1. **Crear el modelo:**
```python
# backend/models/mi_modelo.py

from models import db
from datetime import datetime

class MiModelo(db.Model):
    __tablename__ = 'mi_tabla'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
```

2. **Importar en `models/__init__.py`:**
```python
from models.mi_modelo import MiModelo
```

3. **Crear las tablas:**
```bash
python init_db.py
```

---

## 🧪 Testing

### Probar la API con curl

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@focusit.com"}' \
  -c cookies.txt

# Listar tickets
curl http://localhost:5000/api/tickets \
  -b cookies.txt

# Crear ticket
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "categoria": "problemas_tecnicos",
    "titulo": "Test ticket",
    "descripcion": "Descripción de prueba",
    "prioridad": "media"
  }'
```

### Probar con JavaScript

```javascript
// Usando el cliente API incluido
import { API } from '/static/js/api-client.js';

// Login
const result = await API.auth.login('usuario@focusit.com');
console.log(result);

// Crear ticket
const ticket = await API.tickets.create({
  categoria: 'problemas_tecnicos',
  titulo: 'Mi computador no enciende',
  descripcion: 'Descripción detallada...',
  prioridad: 'alta'
});
console.log(ticket);
```

---

## 📚 Documentación Adicional

- **[API REST Completa](docs/API_DOCUMENTATION.md)** - Todos los endpoints
- **[Arquitectura](docs/ARQUITECTURA.md)** - Diagramas y patrones
- **[Separación Frontend/Backend](docs/FRONTEND_BACKEND_SEPARATION.md)** - Guía de migración

---

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```bash
# Asegúrate de tener el entorno virtual activado
pip install -r requirements.txt
```

### Error: "Template not found"
```bash
# Verifica que la carpeta frontend/ existe y contiene templates/
ls -la frontend/templates/
```

### Error: "Database is locked"
```bash
# Cierra todas las conexiones a la BD y reinicia
rm instance/focusit.db
python init_db.py
```

### La aplicación no encuentra los archivos estáticos
```bash
# Verifica que la carpeta frontend/static/ existe
ls -la frontend/static/
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` en la raíz:

```env
# Flask
SECRET_KEY=tu-clave-secreta-super-segura
FLASK_ENV=development
DEBUG=True

# Base de datos
DATABASE_URL=sqlite:///instance/focusit.db

# WhatsApp (opcional)
WHATSAPP_VERIFY_TOKEN=tu-token-de-verificacion
WHATSAPP_ACCESS_TOKEN=tu-token-de-acceso
```

### Cambiar Puerto

Edita `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambiar 5000 a 8080
```

### Usar PostgreSQL en lugar de SQLite

1. Instalar psycopg2:
```bash
pip install psycopg2-binary
```

2. Actualizar `backend/config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://usuario:password@localhost/focusit'
```

---

## 🚀 Despliegue a Producción

### Usando Gunicorn

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Usando Docker

```dockerfile
# Dockerfile (próximamente)
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

---

## 💡 Tips y Mejores Prácticas

1. **Siempre valida en el backend** - Nunca confíes solo en la validación del frontend
2. **Usa el cliente API** - `static/js/api-client.js` tiene todas las funciones listas
3. **Sigue la estructura** - Mantén frontend y backend separados
4. **Documenta tus endpoints** - Agrega docstrings a todas las funciones API
5. **Usa git** - Haz commits frecuentes con mensajes descriptivos

---

## 📞 Soporte

¿Necesitas ayuda? Revisa:
- 📖 [Documentación completa](docs/)
- 🐛 [Issues en GitHub](https://github.com/tu-repo/focusit/issues)
- 💬 [Discusiones](https://github.com/tu-repo/focusit/discussions)

---

**¡Feliz desarrollo! 🎉**

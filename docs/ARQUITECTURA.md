# 🏗️ Arquitectura del Sistema FocusIT

## 📐 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Opción A: Flask Templates (Actual)                         │
│  ┌──────────────────────────────────────────────┐          │
│  │  templates/                                   │          │
│  │  ├── base.html                                │          │
│  │  ├── auth/login.html                          │          │
│  │  ├── tickets/lista.html                       │          │
│  │  └── ...                                      │          │
│  └──────────────────────────────────────────────┘          │
│                                                               │
│  Opción B: Frontend Moderno (Futuro)                        │
│  ┌──────────────────────────────────────────────┐          │
│  │  React / Vue / Angular                        │          │
│  │  ├── src/components/                          │          │
│  │  ├── src/pages/                               │          │
│  │  └── src/services/api.js                     │          │
│  └──────────────────────────────────────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    HTTP Requests
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      FLASK SERVER                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐          ┌──────────────────┐         │
│  │  Rutas Web      │          │   API REST       │         │
│  │  (HTML)         │          │   (JSON)         │         │
│  ├─────────────────┤          ├──────────────────┤         │
│  │ /auth/login     │          │ /api/auth/login  │         │
│  │ /tickets        │          │ /api/tickets     │         │
│  │ /dashboard      │          │ /api/dashboard   │         │
│  │ /knowledge      │          │ /api/knowledge   │         │
│  │ /chatbot        │          │ /api/chatbot     │         │
│  └─────────────────┘          └──────────────────┘         │
│           ↓                            ↓                     │
│  ┌──────────────────────────────────────────────┐          │
│  │         Capa de Lógica de Negocio            │          │
│  │  ┌────────────────────────────────────────┐  │          │
│  │  │  Validadores (3 capas)                 │  │          │
│  │  │  - Frontend: UX inmediata              │  │          │
│  │  │  - Backend: Seguridad                  │  │          │
│  │  │  - Base de Datos: Integridad           │  │          │
│  │  └────────────────────────────────────────┘  │          │
│  │  ┌────────────────────────────────────────┐  │          │
│  │  │  Autenticación & Autorización          │  │          │
│  │  │  - Flask-Login (sesiones)              │  │          │
│  │  │  - Decoradores (@login_required)       │  │          │
│  │  │  - Permisos (técnico vs usuario)       │  │          │
│  │  └────────────────────────────────────────┘  │          │
│  └──────────────────────────────────────────────┘          │
│           ↓                                                  │
│  ┌──────────────────────────────────────────────┐          │
│  │         Capa de Acceso a Datos               │          │
│  │  ┌────────────────────────────────────────┐  │          │
│  │  │  SQLAlchemy ORM                        │  │          │
│  │  │  - Usuario                             │  │          │
│  │  │  - Ticket                              │  │          │
│  │  │  - ComentarioTicket                    │  │          │
│  │  │  - BaseConocimiento                    │  │          │
│  │  │  - SesionChatbot                       │  │          │
│  │  └────────────────────────────────────────┘  │          │
│  └──────────────────────────────────────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   BASE DE DATOS                              │
├─────────────────────────────────────────────────────────────┤
│  SQLite / PostgreSQL / MySQL                                │
│  ┌──────────────────────────────────────────────┐          │
│  │  Tablas:                                      │          │
│  │  - usuarios                                   │          │
│  │  - tickets                                    │          │
│  │  - comentarios_ticket                         │          │
│  │  - base_conocimiento                          │          │
│  │  - sesiones_chatbot                           │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos

### Flujo 1: Crear Ticket (Frontend Actual)
```
1. Usuario completa formulario en /tickets/nuevo
   ↓
2. Submit → POST /tickets/crear (ruta web)
   ↓
3. Backend valida datos (utils/validators.py)
   ↓
4. Si válido: Crea ticket en BD
   ↓
5. Redirige a /tickets/{id} con mensaje flash
   ↓
6. Renderiza template tickets/detalle.html
```

### Flujo 2: Crear Ticket (API REST)
```
1. Frontend moderno llama: POST /api/tickets
   ↓
2. Backend valida datos (utils/validators.py)
   ↓
3. Si válido: Crea ticket en BD
   ↓
4. Devuelve JSON:
   {
     "success": true,
     "data": { "ticket": {...} },
     "meta": { "message": "Ticket #123 creado" }
   }
   ↓
5. Frontend renderiza UI con los datos
```

---

## 🛡️ Capas de Seguridad

### 1. Validación Frontend (UX)
```javascript
// static/js/validation.js
const validateTicket = (data) => {
  if (!data.titulo || data.titulo.length < 5) {
    return { valid: false, error: 'Título muy corto' };
  }
  return { valid: true };
};
```

### 2. Validación Backend (Seguridad)
```python
# utils/validators.py
from utils.validators import TicketValidator

is_valid, errors = TicketValidator.validar_creacion(data)
if not is_valid:
    return APIResponse.error(
        APIError.VALIDATION_ERROR,
        'Errores de validación',
        400,
        details=errors
    )
```

### 3. Validación Base de Datos (Integridad)
```python
# models/ticket.py
class Ticket(db.Model):
    titulo = db.Column(
        db.String(200), 
        nullable=False,
        # Constraints a nivel de BD
    )
    prioridad = db.Column(
        db.String(20),
        nullable=False,
        default='media'
    )
```

---

## 🔐 Autenticación y Autorización

### Sesiones (Actual)
```python
# Flask-Login maneja sesiones con cookies
from flask_login import login_user, current_user

# Login
usuario = Usuario.query.filter_by(email=email).first()
login_user(usuario, remember=True)

# Proteger rutas
@app.route('/tickets')
@login_required
def tickets():
    # Solo usuarios autenticados
    pass

# Verificar permisos
if current_user.es_tecnico:
    # Acciones de técnico
    pass
```

### Decoradores API
```python
# utils/api_response.py
from utils.api_response import api_login_required, api_tecnico_required

# Requiere autenticación
@api_login_required
def lista_tickets():
    pass

# Requiere ser técnico
@api_tecnico_required
def actualizar_estado():
    pass
```

---

## 📦 Estructura de Carpetas Detallada

```
focusit/
│
├── app.py                      # Aplicación principal Flask
├── config.py                   # Configuración (BD, categorías, etc.)
├── requirements.txt            # Dependencias Python
│
├── models/                     # Modelos de datos (SQLAlchemy)
│   ├── __init__.py
│   ├── usuario.py
│   ├── ticket.py
│   ├── comentario.py
│   ├── conocimiento.py
│   └── chatbot.py
│
├── routes/                     # Rutas WEB (devuelven HTML)
│   ├── __init__.py
│   ├── auth.py                 # /auth/login, /auth/register
│   ├── tickets.py              # /tickets, /tickets/{id}
│   ├── dashboard.py            # /dashboard
│   ├── knowledge.py            # /knowledge
│   └── chatbot.py              # /chatbot/test
│
├── api/                        # 🆕 API REST (devuelven JSON)
│   ├── __init__.py
│   ├── auth.py                 # POST /api/auth/login
│   ├── tickets.py              # GET/POST /api/tickets
│   ├── knowledge.py            # GET/POST /api/knowledge
│   ├── dashboard.py            # GET /api/dashboard/home
│   └── chatbot.py              # POST /api/chatbot/mensaje
│
├── utils/                      # 🆕 Utilidades compartidas
│   ├── __init__.py
│   ├── api_response.py         # Respuestas estandarizadas
│   └── validators.py           # Validadores (3 capas)
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── tickets/
│   │   ├── lista.html
│   │   ├── detalle.html
│   │   ├── nuevo.html
│   │   └── flujo_guiado.html
│   ├── dashboard/
│   │   ├── home.html
│   │   ├── estadisticas.html
│   │   └── accesos_rapidos.html
│   ├── knowledge/
│   │   ├── index.html
│   │   ├── articulo.html
│   │   ├── crear.html
│   │   └── editar.html
│   └── chatbot/
│       └── test.html
│
├── static/                     # Archivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── api-client.js       # 🆕 Cliente API JavaScript
│
├── instance/                   # Configuración específica
│   └── focusit.db             # Base de datos SQLite
│
├── tests/                      # Tests (recomendado)
│   ├── test_api_auth.py
│   ├── test_api_tickets.py
│   └── ...
│
└── docs/                       # Documentación
    ├── API_DOCUMENTATION.md    # 🆕 Documentación API
    ├── ARQUITECTURA.md         # 🆕 Este archivo
    └── FRONTEND_BACKEND_SEPARATION.md  # 🆕 Guía de separación
```

---

## 🔌 Integraciones

### WhatsApp Business API
```python
# api/chatbot.py
@chatbot_api_bp.route('/webhook', methods=['POST'])
def webhook():
    # Recibe mensajes de WhatsApp
    data = request.get_json()
    message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    
    # Procesa con el chatbot
    response = procesar_mensaje_whatsapp(telefono, message_text)
    
    # Envía respuesta a WhatsApp
    # enviar_mensaje_whatsapp(telefono, response)
    
    return 'OK', 200
```

### Notificaciones en Tiempo Real (Futuro)
```python
# Usando Flask-SocketIO
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    if current_user.es_tecnico:
        emit('notification', {
            'message': 'Conectado al sistema de notificaciones'
        })
```

---

## 📊 Patrones de Diseño Utilizados

### 1. Repository Pattern
```python
# Separación entre lógica de negocio y acceso a datos
class TicketRepository:
    @staticmethod
    def find_by_user(user_id):
        return Ticket.query.filter_by(usuario_id=user_id).all()
    
    @staticmethod
    def create(data):
        ticket = Ticket(**data)
        db.session.add(ticket)
        db.session.commit()
        return ticket
```

### 2. Factory Pattern
```python
# app.py
def create_app():
    app = Flask(__name__)
    # Configuración
    # Registro de blueprints
    return app
```

### 3. Decorator Pattern
```python
# Decoradores para autenticación y permisos
@api_login_required
@api_tecnico_required
def endpoint_protegido():
    pass
```

### 4. Strategy Pattern
```python
# Diferentes estrategias de validación
class Validator:
    @staticmethod
    def email(email):
        # Estrategia de validación de email
        pass
    
    @staticmethod
    def telefono(telefono):
        # Estrategia de validación de teléfono
        pass
```

---

## 🚀 Escalabilidad

### Horizontal Scaling
```
┌─────────────┐
│  Load       │
│  Balancer   │
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│App 1│ │App 2│ │App 3│ │App 4│
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───┬───┴───┬───┴───┬───┘
       │       │       │
   ┌───▼───────▼───────▼───┐
   │   Database Cluster    │
   └───────────────────────┘
```

### Caching
```python
# Usando Redis
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.cached(timeout=300)
def get_articulos_populares():
    return BaseConocimiento.query.order_by(
        desc(BaseConocimiento.vistas)
    ).limit(10).all()
```

---

## 🧪 Testing

### Tests de API
```python
# tests/test_api_tickets.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_ticket(client):
    # Login
    client.post('/api/auth/login', json={'email': 'test@example.com'})
    
    # Crear ticket
    response = client.post('/api/tickets', json={
        'categoria': 'problemas_tecnicos',
        'titulo': 'Test ticket',
        'descripcion': 'Descripción de prueba',
        'prioridad': 'media'
    })
    
    data = response.get_json()
    assert data['success'] == True
    assert 'ticket' in data['data']
```

---

## 📈 Monitoreo y Logging

### Logging
```python
# app.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    logger.info(f'Usuario {current_user.id} creando ticket')
    # ...
```

### Métricas (Futuro)
```python
# Usando Prometheus
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métricas automáticas:
# - Requests por segundo
# - Latencia
# - Errores
```

---

## 🔒 Seguridad

### Checklist de Seguridad

- [x] Validación en 3 capas
- [x] Sanitización de inputs
- [x] Parameterized queries (SQLAlchemy)
- [x] Autenticación con Flask-Login
- [x] Autorización por roles (técnico vs usuario)
- [x] HTTPS en producción (recomendado)
- [ ] Rate limiting (recomendado)
- [ ] CSRF protection (implementar)
- [ ] Content Security Policy (implementar)
- [ ] SQL injection protection (SQLAlchemy lo maneja)
- [ ] XSS protection (sanitización básica implementada)

### Configuración de Producción
```python
# config.py
class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## 📚 Recursos Adicionales

- **API Documentation:** `API_DOCUMENTATION.md`
- **Frontend/Backend Separation:** `FRONTEND_BACKEND_SEPARATION.md`
- **JavaScript API Client:** `static/js/api-client.js`
- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/

---

**Última actualización:** 2024-11-13

# 🌳 Estructura Visual del Proyecto FocusIT

## 📊 Vista Completa del Árbol de Directorios

```
focusit/
│
├── 🎨 frontend/                          # INTERFAZ DE USUARIO
│   │
│   ├── templates/                        # Plantillas HTML (Jinja2)
│   │   ├── base.html                     # Template base con navbar
│   │   ├── index.html                    # Página principal
│   │   │
│   │   ├── auth/                         # Autenticación
│   │   │   ├── login.html                # Formulario de login
│   │   │   └── register.html             # Formulario de registro
│   │   │
│   │   ├── tickets/                      # Sistema de tickets
│   │   │   ├── lista.html                # Lista de tickets
│   │   │   ├── detalle.html              # Detalle de un ticket
│   │   │   ├── nuevo.html                # Crear ticket
│   │   │   └── flujo_guiado.html         # Flujo guiado inteligente
│   │   │
│   │   ├── dashboard/                    # Panel de control
│   │   │   ├── home.html                 # Dashboard principal
│   │   │   ├── estadisticas.html         # Estadísticas (técnicos)
│   │   │   └── accesos_rapidos.html      # Accesos rápidos
│   │   │
│   │   ├── knowledge/                    # Base de conocimiento
│   │   │   ├── index.html                # Lista de artículos
│   │   │   ├── articulo.html             # Ver artículo
│   │   │   ├── crear.html                # Crear artículo (técnicos)
│   │   │   └── editar.html               # Editar artículo (autor)
│   │   │
│   │   └── chatbot/                      # Chatbot
│   │       └── test.html                 # Interfaz de prueba
│   │
│   └── static/                           # Archivos estáticos
│       │
│       ├── css/                          # Estilos
│       │   ├── style.css                 # Estilos principales
│       │   └── ...
│       │
│       ├── js/                           # JavaScript
│       │   ├── main.js                   # JavaScript principal
│       │   ├── api-client.js             # 🆕 Cliente API REST
│       │   └── ...
│       │
│       └── images/                       # Imágenes
│           └── ...
│
├── ⚙️ backend/                           # LÓGICA DE NEGOCIO
│   │
│   ├── app.py                            # 🔥 Aplicación Flask principal
│   ├── config.py                         # Configuración del sistema
│   ├── init_db.py                        # Script de inicialización BD
│   │
│   ├── models/                           # Modelos de datos (SQLAlchemy)
│   │   ├── __init__.py                   # Exporta todos los modelos
│   │   ├── usuario.py                    # Modelo Usuario
│   │   ├── ticket.py                     # Modelo Ticket
│   │   ├── comentario.py                 # Modelo ComentarioTicket
│   │   ├── conocimiento.py               # Modelo BaseConocimiento
│   │   └── chatbot.py                    # Modelo SesionChatbot
│   │
│   ├── routes/                           # Rutas WEB (devuelven HTML)
│   │   ├── __init__.py
│   │   ├── auth.py                       # /auth/login, /auth/register
│   │   ├── tickets.py                    # /tickets, /tickets/{id}
│   │   ├── dashboard.py                  # /dashboard
│   │   ├── knowledge.py                  # /knowledge
│   │   └── chatbot.py                    # /chatbot/test
│   │
│   ├── api/                              # 🆕 API REST (devuelven JSON)
│   │   ├── __init__.py                   # Registra todos los blueprints API
│   │   │
│   │   ├── auth.py                       # Autenticación API
│   │   │   ├── POST   /api/auth/login
│   │   │   ├── POST   /api/auth/logout
│   │   │   ├── POST   /api/auth/register
│   │   │   ├── GET    /api/auth/me
│   │   │   └── GET    /api/auth/check
│   │   │
│   │   ├── tickets.py                    # Tickets API
│   │   │   ├── GET    /api/tickets
│   │   │   ├── GET    /api/tickets/{id}
│   │   │   ├── POST   /api/tickets
│   │   │   ├── POST   /api/tickets/{id}/comentarios
│   │   │   ├── PATCH  /api/tickets/{id}/estado
│   │   │   ├── GET    /api/tickets/buscar-articulos
│   │   │   └── GET    /api/tickets/estadisticas
│   │   │
│   │   ├── knowledge.py                  # Base de conocimiento API
│   │   │   ├── GET    /api/knowledge
│   │   │   ├── GET    /api/knowledge/{id}
│   │   │   ├── POST   /api/knowledge
│   │   │   ├── PUT    /api/knowledge/{id}
│   │   │   ├── DELETE /api/knowledge/{id}
│   │   │   ├── GET    /api/knowledge/buscar-sugerencias
│   │   │   └── GET    /api/knowledge/estadisticas
│   │   │
│   │   ├── dashboard.py                  # Dashboard API
│   │   │   ├── GET    /api/dashboard/home
│   │   │   ├── GET    /api/dashboard/buscar-ayuda
│   │   │   ├── GET    /api/dashboard/accesos-rapidos
│   │   │   ├── GET    /api/dashboard/estadisticas
│   │   │   └── GET    /api/dashboard/notificaciones
│   │   │
│   │   └── chatbot.py                    # Chatbot API
│   │       ├── POST   /api/chatbot/mensaje
│   │       ├── GET    /api/chatbot/sesion
│   │       ├── DELETE /api/chatbot/sesion
│   │       └── POST   /api/chatbot/webhook (WhatsApp)
│   │
│   └── utils/                            # 🆕 Utilidades compartidas
│       ├── __init__.py
│       │
│       ├── api_response.py               # Respuestas API estandarizadas
│       │   ├── class APIResponse         # success(), error(), paginated()
│       │   ├── class APIError            # Códigos de error
│       │   ├── @api_login_required       # Decorador autenticación
│       │   ├── @api_tecnico_required     # Decorador permisos
│       │   └── serialize_model()         # Serialización modelos
│       │
│       └── validators.py                 # Validadores (3 capas)
│           ├── class Validator           # Validación general
│           ├── class TicketValidator     # Validación tickets
│           ├── class UsuarioValidator    # Validación usuarios
│           └── class ConocimientoValidator # Validación artículos
│
├── 📚 docs/                              # DOCUMENTACIÓN
│   ├── API_DOCUMENTATION.md              # 🆕 Documentación completa API
│   ├── ARQUITECTURA.md                   # 🆕 Diagramas y patrones
│   └── FRONTEND_BACKEND_SEPARATION.md    # 🆕 Guía de separación
│
├── 📄 Archivos raíz                      # CONFIGURACIÓN Y SCRIPTS
│   ├── run.py                            # 🆕 🔥 Ejecutar aplicación
│   ├── init_db.py                        # 🆕 Inicializar base de datos
│   ├── verify_structure.py               # 🆕 Verificar estructura
│   │
│   ├── requirements.txt                  # Dependencias Python
│   ├── .env.example                      # Ejemplo variables de entorno
│   ├── .gitignore                        # 🆕 Archivos a ignorar en git
│   │
│   ├── README.md                         # ✏️ Documentación principal
│   ├── QUICK_START.md                    # 🆕 Guía rápida
│   ├── REORGANIZATION_SUMMARY.md         # 🆕 Resumen de reorganización
│   └── ESTRUCTURA_VISUAL.md              # 🆕 Este archivo
│
├── 💾 instance/                          # DATOS DE LA APLICACIÓN
│   └── focusit.db                        # Base de datos SQLite
│
└── 🐍 venv/                              # Entorno virtual Python
    └── ...                               # (no incluir en git)
```

---

## 🎯 Flujo de Datos

### 1️⃣ Usuario accede a la web (HTML)
```
Usuario → Navegador → http://localhost:5000/tickets
                           ↓
                    backend/routes/tickets.py
                           ↓
                    backend/models/ticket.py (BD)
                           ↓
                    frontend/templates/tickets/lista.html
                           ↓
                    Navegador renderiza HTML
```

### 2️⃣ Frontend moderno consume API (JSON)
```
Usuario → React App → fetch('/api/tickets')
                           ↓
                    backend/api/tickets.py
                           ↓
                    backend/models/ticket.py (BD)
                           ↓
                    JSON Response
                           ↓
                    React renderiza UI
```

---

## 📦 Módulos Principales

### 🎨 Frontend
| Archivo | Propósito | Tecnología |
|---------|-----------|------------|
| `templates/*.html` | Vistas HTML | Jinja2 |
| `static/css/*.css` | Estilos | CSS |
| `static/js/*.js` | Interactividad | JavaScript |
| `static/js/api-client.js` | Cliente API | JavaScript ES6 |

### ⚙️ Backend
| Archivo | Propósito | Tecnología |
|---------|-----------|------------|
| `app.py` | Aplicación principal | Flask |
| `config.py` | Configuración | Python |
| `models/*.py` | Modelos de datos | SQLAlchemy |
| `routes/*.py` | Rutas web (HTML) | Flask Blueprints |
| `api/*.py` | API REST (JSON) | Flask Blueprints |
| `utils/*.py` | Utilidades | Python |

---

## 🔗 Relaciones entre Módulos

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │ Templates  │  │   Static   │  │   API Client JS    │   │
│  │   (HTML)   │  │  (CSS/JS)  │  │  (Consume API)     │   │
│  └────────────┘  └────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    HTTP Requests
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │   Routes   │  │    API     │  │      Utils         │   │
│  │   (HTML)   │  │   (JSON)   │  │  (Validators, etc) │   │
│  └──────┬─────┘  └──────┬─────┘  └────────────────────┘   │
│         │                │                                   │
│         └────────┬───────┘                                   │
│                  ↓                                           │
│         ┌────────────────┐                                   │
│         │     Models     │                                   │
│         │  (SQLAlchemy)  │                                   │
│         └────────┬───────┘                                   │
└──────────────────┼─────────────────────────────────────────┘
                   ↓
         ┌─────────────────┐
         │   Base de Datos │
         │   (SQLite/PG)   │
         └─────────────────┘
```

---

## 🚀 Puntos de Entrada

### Para Desarrolladores
```bash
# Inicializar proyecto
python init_db.py

# Ejecutar aplicación
python run.py

# Verificar estructura
python verify_structure.py
```

### Para Usuarios
```
# Web
http://localhost:5000

# Login
http://localhost:5000/auth/login

# Dashboard
http://localhost:5000/dashboard

# API
http://localhost:5000/api
```

---

## 📊 Estadísticas del Proyecto

### Archivos Principales
- **Frontend:** ~15 templates HTML + CSS/JS
- **Backend:** ~20 archivos Python
- **API:** 5 módulos (auth, tickets, knowledge, dashboard, chatbot)
- **Documentación:** 6 archivos markdown
- **Total líneas de código:** ~5,000+ líneas

### Endpoints API
- **Autenticación:** 5 endpoints
- **Tickets:** 7 endpoints
- **Base de Conocimiento:** 7 endpoints
- **Dashboard:** 5 endpoints
- **Chatbot:** 4 endpoints
- **Total:** 28 endpoints REST

---

## 🎓 Convenciones de Código

### Nombres de Archivos
- **Templates:** `snake_case.html` (ej: `lista_tickets.html`)
- **Python:** `snake_case.py` (ej: `api_response.py`)
- **Clases:** `PascalCase` (ej: `APIResponse`)
- **Funciones:** `snake_case` (ej: `create_ticket`)

### Estructura de Blueprints
```python
# backend/api/tickets.py
from flask import Blueprint

tickets_api_bp = Blueprint('tickets_api', __name__)

@tickets_api_bp.route('/', methods=['GET'])
def lista_tickets():
    # Lógica aquí
    pass
```

---

## ✨ Características Destacadas

### ✅ Implementadas
- ✅ Separación física frontend/backend
- ✅ API REST completa con JSON
- ✅ Validación en 3 capas
- ✅ Respuestas estandarizadas
- ✅ Autenticación y autorización
- ✅ Documentación completa
- ✅ Cliente JavaScript para API
- ✅ Manejo de errores centralizado

### 🔄 Próximamente
- 🔄 Tests unitarios
- 🔄 Swagger/OpenAPI docs
- 🔄 Rate limiting
- 🔄 Cache con Redis
- 🔄 WebSockets para notificaciones
- 🔄 Docker containerization

---

**Última actualización:** 15 de Noviembre, 2025  
**Versión:** 2.0 (Estructura Reorganizada)

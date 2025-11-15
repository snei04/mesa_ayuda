<<<<<<< HEAD
# FocusIT - Sistema de Mesa de Ayuda Inteligente

## 📋 Descripción
FocusIT es un sistema de mesa de ayuda diseñado específicamente para ópticas, que implementa un flujo guiado inteligente para categorizar y gestionar solicitudes de soporte técnico.

## 🆕 Actualización v2.0: Estructura Reorganizada

**¡Tu proyecto ahora tiene una separación física clara entre frontend y backend!**

✅ **Estructura modular** con carpetas `frontend/` y `backend/`  
✅ **API REST completa** con respuestas JSON estandarizadas  
✅ **Validación en 3 capas** (frontend, backend, base de datos)  
✅ **Documentación completa** de todos los endpoints  
✅ **Cliente JavaScript** listo para usar  
✅ **Compatible con frontend moderno** (React, Vue, Angular)  
✅ **Listo para app móvil** (consume la misma API)  

📚 **Documentación:**
- 🚀 [Quick Start](QUICK_START.md) - **¡Empieza aquí!**
- 📦 [Estructura Visual](ESTRUCTURA_VISUAL.md) - Vista completa del proyecto
- 🔄 [Guía de Migración](MIGRATION_GUIDE.md) - Si vienes de la versión anterior
- 📖 [API REST Documentation](docs/API_DOCUMENTATION.md) - Todos los endpoints
- 🏗️ [Arquitectura del Sistema](docs/ARQUITECTURA.md) - Diagramas y patrones
- 🔀 [Frontend/Backend Separation](docs/FRONTEND_BACKEND_SEPARATION.md) - Guía de separación
- 💻 [JavaScript API Client](frontend/static/js/api-client.js) - Cliente para consumir la API

## Arquitectura del Sistema

### Fase 1: El Cerebro del Sistema (Lógica y Base de Datos)
- Mapeo de categorías y árbol de decisiones
- Estados del ciclo de vida de tickets
- Base de datos estructurada para tickets, usuarios y conocimiento

### Fase 2: Portal de Autoservicio
- Dashboard personalizado para usuarios
- Formularios inteligentes adaptativos
- Base de conocimientos integrada
- Sistema de seguimiento en tiempo real

### Fase 3: Asistente Virtual (Chatbot)
- Chatbot con flujo guiado
- Integración con WhatsApp Business API
- Automatización de respuestas comunes
- Escalamiento inteligente a técnicos

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Inicializar base de datos:
```bash
python init_db.py
```

5. Ejecutar aplicación:
```bash
python run.py
```

La aplicación estará disponible en:
- **Web:** http://localhost:5000
- **API REST:** http://localhost:5000/api

## Estructura del Proyecto

```
focusit/
│
├── 🎨 frontend/                # FRONTEND (Interfaz de Usuario)
│   ├── templates/              # HTML (Jinja2)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── tickets/
│   │   ├── dashboard/
│   │   ├── knowledge/
│   │   └── chatbot/
│   │
│   └── static/                 # CSS, JS, imágenes
│       ├── css/
│       └── js/
│           └── api-client.js   # Cliente JavaScript para API
│
├── ⚙️ backend/                 # BACKEND (Lógica de Negocio)
│   ├── app.py                  # Aplicación principal Flask
│   ├── config.py               # Configuración
│   ├── init_db.py              # Script de inicialización de BD
│   │
│   ├── models/                 # Modelos de datos (SQLAlchemy)
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── routes/                 # Rutas WEB (devuelven HTML)
│   │   ├── auth.py
│   │   ├── tickets.py
│   │   ├── dashboard.py
│   │   ├── knowledge.py
│   │   └── chatbot.py
│   │
│   ├── api/                    # API REST (devuelven JSON)
│   │   ├── __init__.py
│   │   ├── auth.py             # POST /api/auth/login, /register
│   │   ├── tickets.py          # GET/POST /api/tickets
│   │   ├── knowledge.py        # GET/POST /api/knowledge
│   │   ├── dashboard.py        # GET /api/dashboard/home
│   │   └── chatbot.py          # POST /api/chatbot/mensaje
│   │
│   └── utils/                  # Utilidades compartidas
│       ├── __init__.py
│       ├── api_response.py     # Respuestas estandarizadas
│       └── validators.py       # Validadores (3 capas)
│
├── 📚 docs/                    # Documentación
│   ├── API_DOCUMENTATION.md
│   ├── ARQUITECTURA.md
│   └── FRONTEND_BACKEND_SEPARATION.md
│
├── 📄 Archivos raíz
│   ├── run.py                  # 🆕 Punto de entrada principal
│   ├── init_db.py              # 🆕 Inicializar base de datos
│   ├── requirements.txt        # Dependencias Python
│   ├── .env.example            # Ejemplo de variables de entorno
│   └── README.md               # Este archivo
│
└── instance/                   # Datos de la aplicación
    └── focusit.db              # Base de datos SQLite
```

## Categorías Principales de Tickets

1. **Problemas Técnicos**
   - Computador/Celular
   - Impresoras
   - Aplicativo o Software AgilMed

2. **Solicitudes de Software**
   - Nuevas licencias
   - Actualizaciones
   - Instalaciones

3. **Permisos y Accesos**
   - Carpetas compartidas
   - Sistemas internos
   - Restablecimiento de contraseñas

4. **Consultas Generales**
   - Capacitación
   - Procedimientos
   - Soporte general

## 🚀 Ejemplos de Uso de la API

### Ejemplo 1: Login con JavaScript
```javascript
// Usando el cliente API incluido
import { API } from './static/js/api-client.js';

const result = await API.auth.login('usuario@example.com');

if (result.success) {
  console.log('Bienvenido:', result.data.user.nombre);
  // Redirigir al dashboard
  window.location.href = '/dashboard';
} else {
  console.error('Error:', result.error.message);
  // Mostrar error al usuario
  showError(result.error.message);
}
```

### Ejemplo 2: Crear Ticket
```javascript
const ticketData = {
  categoria: 'problemas_tecnicos',
  subcategoria: 'computador_celular',
  titulo: 'Mi computador no enciende',
  descripcion: 'Desde esta mañana mi computador no enciende cuando presiono el botón...',
  prioridad: 'alta'
};

const result = await API.tickets.create(ticketData);

if (result.success) {
  console.log('Ticket creado:', result.data.ticket.id);
  showSuccess(result.meta.message); // "Ticket #123 creado exitosamente"
}
```

### Ejemplo 3: Listar Tickets con Filtros
```javascript
// Obtener tickets nuevos, página 1
const result = await API.tickets.list({
  page: 1,
  per_page: 10,
  estado: 'nuevo',
  categoria: 'problemas_tecnicos'
});

if (result.success) {
  const tickets = result.data.tickets;
  const pagination = result.meta.pagination;
  
  console.log(`Mostrando ${tickets.length} de ${pagination.total} tickets`);
  
  tickets.forEach(ticket => {
    console.log(`#${ticket.id}: ${ticket.titulo}`);
  });
}
```

### Ejemplo 4: Buscar en Base de Conocimiento
```javascript
const result = await API.knowledge.list({
  q: 'impresora',
  categoria: 'problemas_tecnicos',
  page: 1
});

if (result.success) {
  result.data.articulos.forEach(articulo => {
    console.log(`📖 ${articulo.titulo}`);
    console.log(`   ${articulo.contenido_preview}`);
  });
}
```

### Ejemplo 5: Chatbot
```javascript
const result = await API.chatbot.sendMessage('Hola');

if (result.success) {
  const respuesta = result.data.respuesta;
  
  console.log('Bot:', respuesta.mensaje);
  
  if (respuesta.opciones) {
    respuesta.opciones.forEach(opcion => {
      console.log(`  - ${opcion.texto}`);
    });
  }
}
```

## 🔧 Testing de la API

### Con curl
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@example.com"}' \
  -c cookies.txt

# Crear ticket (usando cookies de sesión)
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "categoria": "problemas_tecnicos",
    "titulo": "Test ticket",
    "descripcion": "Descripción de prueba",
    "prioridad": "media"
  }'

# Listar tickets
curl http://localhost:5000/api/tickets?page=1&estado=nuevo \
  -b cookies.txt
```

### Con Postman
1. Importa la colección de Postman (próximamente)
2. Configura el environment con `base_url = http://localhost:5000`
3. Ejecuta los requests en orden (login primero)

## 🎯 Próximos Pasos

### Para Mantener el Frontend Actual
- ✅ Todo sigue funcionando igual
- 🔄 Opcional: Agregar AJAX a formularios para mejor UX
- 🔄 Opcional: Implementar loading states

### Para Migrar a Frontend Moderno
1. Crear app React/Vue en carpeta `frontend/`
2. Consumir API REST desde el nuevo frontend
3. Mantener Flask solo como API
4. Ver guía completa en [FRONTEND_BACKEND_SEPARATION.md](FRONTEND_BACKEND_SEPARATION.md)

### Para Crear App Móvil
1. Usar Flutter, React Native, o Swift
2. Consumir la misma API REST
3. Ver ejemplos en [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 📞 Soporte y Documentación

- 📖 [Documentación API Completa](API_DOCUMENTATION.md)
- 🏗️ [Arquitectura del Sistema](ARQUITECTURA.md)
- 🔀 [Guía de Separación Frontend/Backend](FRONTEND_BACKEND_SEPARATION.md)
- 💻 [Cliente JavaScript](static/js/api-client.js)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

---

**Desarrollado con ❤️ para ópticas modernas**
=======
# mesa_ayuda
>>>>>>> 68f849cf8cc3483b0b0a8bfacf0067f293afca78

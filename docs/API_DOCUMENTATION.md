# 📚 Documentación API REST - FocusIT

## 🎯 Descripción General

API REST para el sistema de mesa de ayuda FocusIT. Todas las respuestas siguen un formato JSON consistente.

**Base URL:** `http://localhost:5000/api`

---

## 📋 Formato de Respuestas

### Respuesta Exitosa
```json
{
  "success": true,
  "data": {
    // Datos de la respuesta
  },
  "error": null,
  "meta": {
    "timestamp": "2024-11-13T22:30:00.000Z",
    "message": "Mensaje opcional"
  }
}
```

### Respuesta con Error
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensaje amigable para el usuario",
    "details": {
      // Detalles adicionales del error
    }
  },
  "meta": {
    "timestamp": "2024-11-13T22:30:00.000Z"
  }
}
```

### Respuesta con Paginación
```json
{
  "success": true,
  "data": {
    "items": [...]
  },
  "error": null,
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 100,
      "total_pages": 10,
      "has_next": true,
      "has_prev": false
    },
    "timestamp": "2024-11-13T22:30:00.000Z"
  }
}
```

---

## 🔐 Autenticación

### POST `/api/auth/login`
Iniciar sesión

**Body:**
```json
{
  "email": "usuario@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "telefono": "+573001234567",
      "departamento": "Ventas",
      "cargo": "Vendedor",
      "es_tecnico": false
    }
  },
  "meta": {
    "message": "¡Bienvenido/a Juan Pérez!"
  }
}
```

**Errores:**
- `401 INVALID_CREDENTIALS`: Usuario no encontrado o inactivo
- `400 VALIDATION_ERROR`: Email inválido

---

### POST `/api/auth/logout`
Cerrar sesión

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "meta": {
    "message": "Sesión cerrada correctamente"
  }
}
```

---

### POST `/api/auth/register`
Registrar nuevo usuario

**Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "+573001234567",
  "departamento": "Ventas",
  "cargo": "Vendedor"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "departamento": "Ventas",
      "cargo": "Vendedor"
    }
  },
  "meta": {
    "message": "Usuario registrado correctamente"
  }
}
```

**Errores:**
- `409 ALREADY_EXISTS`: Email ya registrado
- `400 VALIDATION_ERROR`: Datos inválidos

---

### GET `/api/auth/me`
Obtener usuario actual

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "es_tecnico": false
    }
  }
}
```

---

### GET `/api/auth/check`
Verificar si hay sesión activa

**Response (200):**
```json
{
  "success": true,
  "data": {
    "authenticated": true
  }
}
```

---

## 🎫 Tickets

### GET `/api/tickets`
Listar tickets con filtros

**Query Parameters:**
- `page` (int): Número de página (default: 1)
- `per_page` (int): Items por página (default: 10)
- `estado` (string): Filtrar por estado
- `categoria` (string): Filtrar por categoría
- `prioridad` (string): Filtrar por prioridad

**Response (200):**
```json
{
  "success": true,
  "data": {
    "tickets": [
      {
        "id": 1,
        "titulo": "Mi computador no enciende",
        "descripcion": "...",
        "estado": "nuevo",
        "prioridad": "alta",
        "categoria": "problemas_tecnicos",
        "subcategoria": "computador_celular",
        "fecha_creacion": "2024-11-13T10:00:00",
        "usuario": {
          "id": 1,
          "nombre": "Juan Pérez",
          "email": "juan@example.com"
        },
        "tecnico": null
      }
    ]
  },
  "meta": {
    "pagination": {...}
  }
}
```

**Requiere:** Autenticación

---

### GET `/api/tickets/{id}`
Obtener detalle de un ticket

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ticket": {
      "id": 1,
      "titulo": "...",
      "descripcion": "...",
      "estado": "nuevo",
      "comentarios": [
        {
          "id": 1,
          "contenido": "Ticket creado",
          "fecha_creacion": "2024-11-13T10:00:00",
          "es_interno": false,
          "autor": {
            "id": 1,
            "nombre": "Juan Pérez"
          }
        }
      ]
    }
  }
}
```

**Requiere:** Autenticación
**Errores:**
- `403 FORBIDDEN`: Sin permisos para ver el ticket
- `404 NOT_FOUND`: Ticket no encontrado

---

### POST `/api/tickets`
Crear nuevo ticket

**Body:**
```json
{
  "categoria": "problemas_tecnicos",
  "subcategoria": "computador_celular",
  "titulo": "Mi computador no enciende",
  "descripcion": "Desde esta mañana mi computador no enciende cuando presiono el botón de encendido...",
  "prioridad": "alta"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ticket": {
      "id": 123,
      "titulo": "Mi computador no enciende",
      "estado": "nuevo",
      "prioridad": "alta"
    }
  },
  "meta": {
    "message": "Ticket #123 creado exitosamente"
  }
}
```

**Requiere:** Autenticación
**Errores:**
- `400 VALIDATION_ERROR`: Datos inválidos

---

### POST `/api/tickets/{id}/comentarios`
Agregar comentario a un ticket

**Body:**
```json
{
  "contenido": "Texto del comentario",
  "es_interno": false
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "comentario": {
      "id": 5,
      "contenido": "Texto del comentario",
      "fecha_creacion": "2024-11-13T11:00:00",
      "autor": {
        "id": 1,
        "nombre": "Juan Pérez"
      }
    }
  },
  "meta": {
    "message": "Comentario agregado correctamente"
  }
}
```

**Requiere:** Autenticación
**Errores:**
- `403 FORBIDDEN`: Sin permisos para comentar

---

### PATCH `/api/tickets/{id}/estado`
Actualizar estado de un ticket (solo técnicos)

**Body:**
```json
{
  "estado": "en_proceso",
  "tecnico_id": 5
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ticket": {
      "id": 1,
      "estado": "en_proceso",
      "tecnico_id": 5
    }
  },
  "meta": {
    "message": "Estado actualizado a: en_proceso"
  }
}
```

**Requiere:** Autenticación + Rol Técnico
**Errores:**
- `403 FORBIDDEN`: No es técnico
- `400 VALIDATION_ERROR`: Estado inválido

---

### GET `/api/tickets/buscar-articulos`
Buscar artículos de conocimiento relacionados

**Query Parameters:**
- `q` (string): Término de búsqueda (mínimo 3 caracteres)
- `categoria` (string): Filtrar por categoría
- `subcategoria` (string): Filtrar por subcategoría

**Response (200):**
```json
{
  "success": true,
  "data": {
    "articulos": [
      {
        "id": 1,
        "titulo": "Cómo reiniciar una impresora",
        "contenido_preview": "Paso 1: Apagar la impresora...",
        "categoria": "problemas_tecnicos",
        "subcategoria": "impresoras"
      }
    ]
  }
}
```

---

### GET `/api/tickets/estadisticas`
Estadísticas de tickets (solo técnicos)

**Query Parameters:**
- `categoria` (string): Filtrar por categoría

**Response (200):**
```json
{
  "success": true,
  "data": {
    "estadisticas": [
      {
        "subcategoria": "computador_celular",
        "total": 50,
        "abiertos": 10
      }
    ]
  }
}
```

**Requiere:** Autenticación + Rol Técnico

---

## 📖 Base de Conocimiento

### GET `/api/knowledge`
Listar artículos

**Query Parameters:**
- `q` (string): Búsqueda
- `categoria` (string): Filtrar por categoría
- `page` (int): Página
- `per_page` (int): Items por página

**Response (200):**
```json
{
  "success": true,
  "data": {
    "articulos": [
      {
        "id": 1,
        "titulo": "Cómo reiniciar una impresora",
        "contenido_preview": "...",
        "categoria": "problemas_tecnicos",
        "vistas": 150,
        "autor": {
          "id": 2,
          "nombre": "María García"
        }
      }
    ]
  },
  "meta": {
    "pagination": {...}
  }
}
```

---

### GET `/api/knowledge/{id}`
Obtener artículo específico

**Response (200):**
```json
{
  "success": true,
  "data": {
    "articulo": {
      "id": 1,
      "titulo": "Cómo reiniciar una impresora",
      "contenido": "Contenido completo del artículo...",
      "palabras_clave": "impresora, reiniciar, problema",
      "categoria": "problemas_tecnicos",
      "vistas": 151,
      "autor": {
        "id": 2,
        "nombre": "María García"
      },
      "relacionados": [...]
    }
  }
}
```

---

### POST `/api/knowledge`
Crear artículo (solo técnicos)

**Body:**
```json
{
  "titulo": "Cómo reiniciar una impresora",
  "contenido": "Paso 1: Apagar la impresora...",
  "palabras_clave": "impresora, reiniciar, problema",
  "categoria": "problemas_tecnicos",
  "subcategoria": "impresoras"
}
```

**Requiere:** Autenticación + Rol Técnico

---

### PUT `/api/knowledge/{id}`
Editar artículo (solo autor)

**Body:** Igual que POST

**Requiere:** Autenticación + Ser el autor

---

### DELETE `/api/knowledge/{id}`
Eliminar artículo (solo autor)

**Requiere:** Autenticación + Ser el autor

---

## 📊 Dashboard

### GET `/api/dashboard/home`
Datos del dashboard principal

**Response (200):**
```json
{
  "success": true,
  "data": {
    "tickets_abiertos": 5,
    "tickets_recientes": [...],
    "articulos_populares": [...],
    "stats_tecnico": {
      "tickets_asignados": 10,
      "tickets_nuevos": 3,
      "tickets_criticos": 1
    }
  }
}
```

---

### GET `/api/dashboard/estadisticas`
Estadísticas generales (solo técnicos)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_tickets": 500,
    "tickets_abiertos": 50,
    "tickets_por_estado": [...],
    "tickets_por_categoria": [...],
    "tecnicos_activos": [...]
  }
}
```

**Requiere:** Autenticación + Rol Técnico

---

### GET `/api/dashboard/notificaciones`
Notificaciones en tiempo real (solo técnicos)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "notificaciones": [
      {
        "tipo": "nuevo_ticket",
        "titulo": "Nuevo ticket #123",
        "mensaje": "Problema con impresora - Juan Pérez",
        "url": "/tickets/123",
        "tiempo": "10:30",
        "prioridad": "alta"
      }
    ],
    "total_nuevos": 2,
    "total_criticos": 1,
    "mis_pendientes": 5
  }
}
```

**Requiere:** Autenticación + Rol Técnico

---

## 🤖 Chatbot

### POST `/api/chatbot/mensaje`
Enviar mensaje al chatbot

**Body:**
```json
{
  "mensaje": "Hola",
  "telefono": "+573001234567"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "respuesta": {
      "mensaje": "¡Hola! Soy VisioBot...",
      "opciones": [
        {"texto": "🔧 Solucionar un problema", "valor": "problema"},
        {"texto": "📝 Hacer una solicitud", "valor": "solicitud"}
      ],
      "tipo": "opciones"
    }
  }
}
```

---

### GET `/api/chatbot/sesion`
Obtener sesión activa del chatbot

**Query Parameters:**
- `telefono` (string): Número de teléfono

---

### DELETE `/api/chatbot/sesion`
Reiniciar sesión del chatbot

**Query Parameters:**
- `telefono` (string): Número de teléfono

---

## 🚨 Códigos de Error

| Código | HTTP | Descripción |
|--------|------|-------------|
| `VALIDATION_ERROR` | 400 | Error de validación de datos |
| `MISSING_FIELDS` | 400 | Campos requeridos faltantes |
| `INVALID_FORMAT` | 400 | Formato de datos inválido |
| `UNAUTHORIZED` | 401 | No autenticado |
| `INVALID_CREDENTIALS` | 401 | Credenciales inválidas |
| `SESSION_EXPIRED` | 401 | Sesión expirada |
| `FORBIDDEN` | 403 | Sin permisos suficientes |
| `INSUFFICIENT_PERMISSIONS` | 403 | Permisos insuficientes |
| `NOT_FOUND` | 404 | Recurso no encontrado |
| `RESOURCE_NOT_FOUND` | 404 | Recurso específico no encontrado |
| `ALREADY_EXISTS` | 409 | Recurso ya existe |
| `CONFLICT` | 409 | Conflicto con estado actual |
| `INTERNAL_ERROR` | 500 | Error interno del servidor |
| `DATABASE_ERROR` | 500 | Error de base de datos |

---

## 🔧 Ejemplos de Uso

### JavaScript (Fetch API)

```javascript
// Login
const login = async (email) => {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include', // Importante para cookies de sesión
    body: JSON.stringify({ email })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Usuario:', data.data.user);
  } else {
    console.error('Error:', data.error.message);
  }
};

// Crear ticket
const crearTicket = async (ticketData) => {
  const response = await fetch('http://localhost:5000/api/tickets', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify(ticketData)
  });
  
  const data = await response.json();
  return data;
};

// Listar tickets con paginación
const listarTickets = async (page = 1, estado = '') => {
  const params = new URLSearchParams({ page, estado });
  const response = await fetch(`http://localhost:5000/api/tickets?${params}`, {
    credentials: 'include'
  });
  
  const data = await response.json();
  return data;
};
```

### Python (requests)

```python
import requests

BASE_URL = 'http://localhost:5000/api'
session = requests.Session()

# Login
response = session.post(f'{BASE_URL}/auth/login', json={
    'email': 'usuario@example.com'
})
data = response.json()

if data['success']:
    print('Usuario:', data['data']['user'])

# Crear ticket
ticket_data = {
    'categoria': 'problemas_tecnicos',
    'subcategoria': 'computador_celular',
    'titulo': 'Mi computador no enciende',
    'descripcion': 'Descripción detallada...',
    'prioridad': 'alta'
}

response = session.post(f'{BASE_URL}/tickets', json=ticket_data)
data = response.json()

if data['success']:
    print('Ticket creado:', data['data']['ticket']['id'])
```

---

## 📝 Notas Importantes

1. **Autenticación:** La mayoría de endpoints requieren autenticación mediante cookies de sesión (Flask-Login).

2. **CORS:** Si consumes la API desde un dominio diferente, necesitarás configurar CORS en el backend.

3. **Rate Limiting:** Considera implementar rate limiting en producción.

4. **Validación:** Todos los datos son validados en tres capas:
   - Frontend (UX inmediata)
   - Backend (seguridad)
   - Base de datos (integridad)

5. **Paginación:** Los endpoints que devuelven listas soportan paginación con `page` y `per_page`.

6. **Timestamps:** Todos los timestamps están en formato ISO 8601 UTC.

7. **Sanitización:** Los datos son sanitizados automáticamente para prevenir XSS y SQL injection.

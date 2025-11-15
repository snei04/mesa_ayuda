# 🔄 Guía de Migración - FocusIT v2.0

## 📋 Resumen de Cambios

Tu proyecto ha sido reorganizado de una estructura plana a una estructura modular con separación clara entre frontend y backend.

---

## 🗂️ Cambios en la Estructura

### Antes → Después

| Antes | Después | Motivo |
|-------|---------|--------|
| `app.py` | `backend/app.py` | Organización backend |
| `config.py` | `backend/config.py` | Organización backend |
| `models/` | `backend/models/` | Organización backend |
| `routes/` | `backend/routes/` | Organización backend |
| `api/` | `backend/api/` | Organización backend |
| `utils/` | `backend/utils/` | Organización backend |
| `templates/` | `frontend/templates/` | Separación frontend |
| `static/` | `frontend/static/` | Separación frontend |
| `init_db.py` | `backend/init_db.py` + `init_db.py` (raíz) | Facilitar uso |
| N/A | `run.py` | Punto de entrada único |
| N/A | `docs/` | Documentación centralizada |

---

## 🚀 Cómo Ejecutar el Proyecto Ahora

### ❌ Antes (Ya NO funciona)
```bash
python app.py
```

### ✅ Ahora (Nueva forma)
```bash
python run.py
```

---

## 🔧 Cambios en Imports (Si modificas código)

### En archivos de backend/

#### ❌ Antes
```python
# Esto ya NO funciona si estás en backend/
from app import create_app
from models import db, Usuario
```

#### ✅ Ahora
```python
# Desde backend/app.py o backend/routes/*.py
from config import Config          # Mismo directorio
from models import db, Usuario     # Mismo directorio

# Desde archivos en la raíz (run.py, init_db.py)
from backend.app import create_app
from backend.models import db, Usuario
```

---

## 📝 Cambios en Configuración

### Flask App Configuration

#### ❌ Antes
```python
app = Flask(__name__)
# Flask buscaba templates/ y static/ en la raíz
```

#### ✅ Ahora
```python
# backend/app.py
frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
template_folder = os.path.join(frontend_folder, 'templates')
static_folder = os.path.join(frontend_folder, 'static')

app = Flask(__name__, 
            template_folder=template_folder,
            static_folder=static_folder)
```

---

## 🗄️ Base de Datos

### Ubicación
- **Antes:** `instance/focusit.db` (raíz)
- **Ahora:** `instance/focusit.db` (raíz) - **SIN CAMBIOS**

### Inicialización

#### ❌ Antes
```bash
python init_db.py
```

#### ✅ Ahora
```bash
# Desde la raíz del proyecto
python init_db.py
```

**Nota:** El archivo `init_db.py` ahora está en la raíz para facilitar su uso.

---

## 🌐 URLs y Endpoints

### Sin Cambios
Todas las URLs siguen siendo las mismas:

- ✅ `http://localhost:5000/` - Página principal
- ✅ `http://localhost:5000/auth/login` - Login
- ✅ `http://localhost:5000/tickets` - Tickets
- ✅ `http://localhost:5000/api/tickets` - API Tickets
- ✅ Todas las demás rutas siguen igual

---

## 📁 Rutas de Archivos Estáticos

### Sin Cambios en el Navegador
```html
<!-- Esto sigue funcionando igual -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

Flask maneja automáticamente la nueva ubicación de `frontend/static/`.

---

## 🔄 Migrando Código Personalizado

### Si agregaste código en `app.py`

#### Antes
```python
# app.py (raíz)
from flask import Flask

app = Flask(__name__)

@app.route('/mi-ruta')
def mi_funcion():
    return "Hola"
```

#### Ahora
```python
# backend/app.py
def create_app():
    app = Flask(__name__, ...)
    
    # Agregar tu ruta aquí
    @app.route('/mi-ruta')
    def mi_funcion():
        return "Hola"
    
    return app
```

### Si creaste nuevos modelos

#### Antes
```python
# models/mi_modelo.py
from models import db

class MiModelo(db.Model):
    pass
```

#### Ahora
```python
# backend/models/mi_modelo.py
from models import db

class MiModelo(db.Model):
    pass

# backend/models/__init__.py
from models.mi_modelo import MiModelo  # Agregar esta línea
```

### Si creaste nuevas rutas

#### Antes
```python
# routes/mi_ruta.py
from flask import Blueprint

mi_bp = Blueprint('mi_bp', __name__)
```

#### Ahora
```python
# backend/routes/mi_ruta.py
from flask import Blueprint

mi_bp = Blueprint('mi_bp', __name__)

# backend/app.py - Registrar el blueprint
from routes.mi_ruta import mi_bp
app.register_blueprint(mi_bp, url_prefix='/mi-ruta')
```

---

## 🧪 Testing

### Ejecutar Tests

#### ❌ Antes
```bash
pytest tests/
```

#### ✅ Ahora
```bash
# Asegúrate de estar en la raíz
cd focusit
pytest tests/
```

---

## 🐛 Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'backend'"

**Causa:** Estás ejecutando desde la carpeta incorrecta.

**Solución:**
```bash
# Asegúrate de estar en la raíz del proyecto
cd focusit
python run.py
```

### Error: "Template not found"

**Causa:** Flask no encuentra los templates en la nueva ubicación.

**Solución:** Verifica que `backend/app.py` tiene la configuración correcta:
```python
frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
template_folder = os.path.join(frontend_folder, 'templates')
```

### Error: "No such file or directory: 'static/...'"

**Causa:** Flask no encuentra los archivos estáticos.

**Solución:** Verifica que `frontend/static/` existe y contiene tus archivos CSS/JS.

### Error: "ImportError: cannot import name 'create_app'"

**Causa:** Estás usando el import antiguo.

**Solución:** Actualiza tus imports:
```python
# ❌ Antes
from app import create_app

# ✅ Ahora (desde raíz)
from backend.app import create_app
```

---

## 📦 Dependencias

### Sin Cambios
El archivo `requirements.txt` sigue en la raíz y contiene las mismas dependencias:

```bash
pip install -r requirements.txt
```

---

## 🔐 Variables de Entorno

### Sin Cambios
El archivo `.env` sigue en la raíz:

```bash
# .env
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///instance/focusit.db
```

---

## 📚 Documentación Actualizada

### Nuevos Archivos de Documentación

1. **[QUICK_START.md](QUICK_START.md)** - Guía rápida para empezar
2. **[REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)** - Resumen de cambios
3. **[ESTRUCTURA_VISUAL.md](ESTRUCTURA_VISUAL.md)** - Vista del árbol de directorios
4. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Esta guía
5. **[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Documentación API
6. **[docs/ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Arquitectura del sistema
7. **[docs/FRONTEND_BACKEND_SEPARATION.md](docs/FRONTEND_BACKEND_SEPARATION.md)** - Guía de separación

---

## ✅ Checklist de Migración

### Para Desarrolladores Existentes

- [ ] Leer esta guía completa
- [ ] Actualizar repositorio local: `git pull`
- [ ] Verificar estructura: `python verify_structure.py`
- [ ] Probar ejecución: `python run.py`
- [ ] Verificar que todas las rutas funcionan
- [ ] Actualizar imports en código personalizado (si aplica)
- [ ] Actualizar scripts de deployment (si aplica)
- [ ] Actualizar documentación interna (si aplica)

### Para Nuevos Desarrolladores

- [ ] Clonar repositorio
- [ ] Leer [QUICK_START.md](QUICK_START.md)
- [ ] Crear entorno virtual: `python -m venv venv`
- [ ] Activar entorno: `venv\Scripts\activate`
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Inicializar BD: `python init_db.py`
- [ ] Ejecutar app: `python run.py`
- [ ] Explorar documentación en `docs/`

---

## 🎯 Ventajas de la Nueva Estructura

### 1. **Organización Clara**
```
✅ Frontend separado del backend
✅ Fácil encontrar archivos
✅ Estructura escalable
```

### 2. **Desarrollo en Equipo**
```
✅ Frontend y backend pueden trabajar en paralelo
✅ Menos conflictos en git
✅ Responsabilidades claras
```

### 3. **Mantenibilidad**
```
✅ Código más limpio
✅ Fácil agregar nuevas funcionalidades
✅ Mejor para testing
```

### 4. **Flexibilidad**
```
✅ Puedes reemplazar el frontend sin tocar el backend
✅ Puedes agregar múltiples frontends (web, móvil)
✅ API REST lista para consumir
```

---

## 🚀 Próximos Pasos Recomendados

### Inmediatos
1. ✅ Ejecutar `python verify_structure.py` para verificar todo
2. ✅ Ejecutar `python init_db.py` si es primera vez
3. ✅ Ejecutar `python run.py` para probar
4. ✅ Revisar [QUICK_START.md](QUICK_START.md)

### Corto Plazo
1. Familiarizarte con la nueva estructura
2. Revisar documentación en `docs/`
3. Probar la API REST con Postman o curl
4. Explorar el cliente JavaScript en `frontend/static/js/api-client.js`

### Mediano Plazo
1. Migrar formularios a usar la API REST
2. Agregar tests unitarios
3. Implementar CI/CD
4. Considerar migración a frontend moderno (React/Vue)

---

## 📞 Soporte

Si tienes problemas con la migración:

1. **Revisa esta guía completa**
2. **Ejecuta:** `python verify_structure.py`
3. **Revisa:** [QUICK_START.md](QUICK_START.md)
4. **Consulta:** Documentación en `docs/`

---

## 📝 Notas Importantes

### ⚠️ Importante
- **SIEMPRE ejecuta desde la raíz del proyecto:** `python run.py`
- **NO ejecutes:** `python backend/app.py` (no funcionará correctamente)
- **La base de datos sigue en:** `instance/focusit.db` (sin cambios)

### ✅ Compatibilidad
- Todas las URLs siguen siendo las mismas
- Todas las funcionalidades se mantienen
- La API REST sigue funcionando igual
- Los templates HTML siguen funcionando igual

---

**Fecha de migración:** 15 de Noviembre, 2025  
**Versión anterior:** 1.0 (Estructura plana)  
**Versión actual:** 2.0 (Estructura modular)

**¡La migración está completa y todo funciona correctamente!** ✨

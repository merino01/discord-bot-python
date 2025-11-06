# API Module

REST API para el bot de Discord. Proporciona acceso programático a los datos y funcionalidades del bot.

## Arquitectura

```
api/
├── __init__.py           # Inicialización del módulo
├── app.py                # Aplicación FastAPI principal
├── auth.py               # Autenticación con API key
├── server.py             # Gestión del servidor API
├── routes_health.py      # Endpoints de salud y estado
└── routes_clans.py       # Endpoints de gestión de clanes
```

## Componentes

### `app.py`
Aplicación FastAPI principal que registra todos los routers y configura la documentación automática.

### `auth.py`
Middleware de autenticación que verifica la API key en el header `X-API-Key`.

### `server.py`
Gestiona el ciclo de vida del servidor API usando uvicorn. Se integra con el bot de Discord para iniciar/detener el servidor junto con el bot.

### `routes_health.py`
Endpoints para verificar el estado del API:
- `GET /api/health` - Health check (sin autenticación)
- `GET /api/status` - Estado detallado (requiere autenticación)

### `routes_clans.py`
Endpoints para gestionar clanes:
- `GET /api/clans/` - Listar todos los clanes
- `GET /api/clans/{id}` - Obtener un clan específico
- `GET /api/clans/{id}/members` - Obtener miembros de un clan

## Uso

### Configuración

Añade estos campos a `config.json`:

```json
{
    "api_enabled": true,
    "api_port": 8000,
    "api_key": "tu_clave_secreta"
}
```

### Autenticación

Todas las rutas (excepto `/api/health`) requieren el header:

```
X-API-Key: tu_clave_secreta
```

### Documentación Interactiva

Cuando el API está activa:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Agregar Nuevos Endpoints

Para añadir nuevos endpoints:

1. Crear un nuevo archivo `routes_nombre.py`:

```python
from fastapi import APIRouter, Depends
from api.auth import verify_api_key

router = APIRouter(prefix="/api/nombre", tags=["nombre"])

@router.get("/")
async def list_items(_: str = Depends(verify_api_key)):
    return []
```

2. Registrar el router en `app.py`:

```python
from api.routes_nombre import router as nombre_router
app.include_router(nombre_router)
```

## Seguridad

- Usa HTTPS en producción
- Mantén la API key segura
- Restringe acceso por firewall
- Cambia la API key regularmente
- No compartas la API key en repositorios públicos

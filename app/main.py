import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .config import get_settings
from .database import create_tables
from .exceptions import BaseCustomException

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Obtener configuración
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manejo del ciclo de vida de la aplicación.
    """
    # Startup: Solo crear tablas de base de datos
    logger.info("Iniciando aplicación...")
    try:
        create_tables()
        logger.info("Tablas de base de datos creadas exitosamente")
    except Exception as e:
        logger.error(f"Error al crear tablas: {e}")
        raise

    yield

    # Shutdown: Limpiar recursos si es necesario
    logger.info("Cerrando aplicación...")


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    API REST para prueba técnica de desarrollador backend Python.

    Esta API permite:
    - Gestionar usuarios con CRUD completo
    - Integrar datos con APIs externas
    - Enviar notificaciones por correo
    - Manejar errores de manera robusta

    ## Endpoints principales:

    ### 🎯 Endpoint de integración con API externa
    - `GET /api/v1/usuarios/{id}/con-datos-externos`: Combina datos locales con API externa

    ### 👥 Usuarios
    - CRUD completo para usuarios
    - Integración con JSONPlaceholder API

    ### 🏥 Health Check
    - Verificación de estado de la aplicación y servicios externos
    """,
    lifespan=lifespan,
    debug=settings.debug,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador de excepciones personalizado
@app.exception_handler(BaseCustomException)
async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """
    Maneja las excepciones personalizadas de la aplicación.
    """
    logger.error(f"Excepción personalizada: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Maneja las excepciones HTTP de FastAPI.
    """
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Maneja las excepciones generales no capturadas.
    """
    logger.error(f"Excepción no manejada: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "status_code": 500,
            "path": str(request.url),
        },
    )


# Incluir rutas de la API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Endpoint raíz de la aplicación.
    """
    return {
        "message": "¡Bienvenido a la API de prueba técnica!",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


def start_server() -> None:
    """
    Función para iniciar el servidor desde Poetry scripts.
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    start_server()

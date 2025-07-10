from fastapi import APIRouter

from .endpoints import health, usuarios

# Router principal de la API
api_router = APIRouter()

# Incluir todos los routers con sus prefijos
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    usuarios.router,
    prefix="/usuarios",
    tags=["usuarios"],
    responses={404: {"description": "Not found"}},
)

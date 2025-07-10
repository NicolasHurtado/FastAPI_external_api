import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...config import get_settings
from ...database import get_db
from ...services.external_api_service import external_api_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de health check básico.

    Returns:
        Estado básico de la aplicación
    """
    return {
        "status": "healthy",
        "message": "API funcionando correctamente",
        "version": get_settings().app_version,
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Endpoint de health check detallado que verifica:
    - Estado de la aplicación
    - Conexión a la base de datos
    - Estado de la API externa

    Returns:
        Estado detallado de todos los componentes
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {},
    }

    # Verificar base de datos
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Conexión a base de datos exitosa",
        }
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": "Error al conectar con la base de datos",
        }
        health_status["status"] = "unhealthy"

    # Verificar API externa
    try:
        external_status = await external_api_service.get_status_check()
        health_status["components"]["external_api"] = external_status

        if external_status["status"] != "active":
            health_status["status"] = "degraded"

    except Exception as e:
        logger.error(f"Error al verificar API externa: {e}")
        health_status["components"]["external_api"] = {
            "status": "unhealthy",
            "message": "Error al verificar API externa",
        }
        health_status["status"] = "unhealthy"

    return health_status

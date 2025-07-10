import logging
from typing import Any, Dict

import httpx

from ..config import get_settings
from ..exceptions import ExternalAPIException, ExternalAPITimeoutException

logger = logging.getLogger(__name__)


class ExternalAPIService:
    """
    Servicio para interactuar con APIs externas.
    En este caso, usaremos JSONPlaceholder como ejemplo.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.external_api_base_url
        self.timeout = self.settings.external_api_timeout

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene datos de usuario desde la API externa.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con los datos del usuario

        Raises:
            ExternalAPIException: Si hay error en la API
            ExternalAPITimeoutException: Si hay timeout
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_id}")

                if response.status_code == 404:
                    logger.warning(f"Usuario {user_id} no encontrado en API externa")
                    return {}

                if response.status_code != 200:
                    logger.error(f"Error en API externa: {response.status_code}")
                    raise ExternalAPIException(f"Error en API externa: {response.status_code}")

                data: Dict[str, Any] = response.json()
                logger.info(f"Datos obtenidos de API externa para usuario {user_id}")
                return data

        except httpx.TimeoutException:
            logger.error(f"Timeout al obtener datos de usuario {user_id}")
            raise ExternalAPITimeoutException(f"Timeout al obtener datos de usuario {user_id}")
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al obtener datos de usuario {user_id}: {e}")
            raise ExternalAPIException(f"Error HTTP al obtener datos de usuario {user_id}")
        except Exception as e:
            logger.error(f"Error inesperado al obtener datos de usuario {user_id}: {e}")
            raise ExternalAPIException(f"Error inesperado al obtener datos de usuario {user_id}")

    async def get_post_data(self, post_id: int) -> Dict[str, Any]:
        """
        Obtiene datos de un post desde la API externa.

        Args:
            post_id: ID del post

        Returns:
            Dict con los datos del post

        Raises:
            ExternalAPIException: Si hay error en la API
            ExternalAPITimeoutException: Si hay timeout
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/posts/{post_id}")

                if response.status_code == 404:
                    logger.warning(f"Post {post_id} no encontrado en API externa")
                    return {}

                if response.status_code != 200:
                    logger.error(f"Error en API externa: {response.status_code}")
                    raise ExternalAPIException(f"Error en API externa: {response.status_code}")

                data: Dict[str, Any] = response.json()
                logger.info(f"Datos obtenidos de API externa para post {post_id}")
                return data

        except httpx.TimeoutException:
            logger.error(f"Timeout al obtener datos de post {post_id}")
            raise ExternalAPITimeoutException(f"Timeout al obtener datos de post {post_id}")
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al obtener datos de post {post_id}: {e}")
            raise ExternalAPIException(f"Error HTTP al obtener datos de post {post_id}")
        except Exception as e:
            logger.error(f"Error inesperado al obtener datos de post {post_id}: {e}")
            raise ExternalAPIException(f"Error inesperado al obtener datos de post {post_id}")

    async def get_status_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de la API externa.

        Returns:
            Dict con el estado de la API
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/posts/1")

                if response.status_code == 200:
                    return {
                        "status": "active",
                        "message": "API externa funcionando correctamente",
                    }
                else:
                    return {
                        "status": "inactive",
                        "message": f"API externa respondió con código {response.status_code}",
                    }

        except Exception as e:
            logger.error(f"Error al verificar estado de API externa: {e}")
            return {
                "status": "error",
                "message": "No se pudo conectar con la API externa",
            }


# Instancia singleton del servicio
external_api_service = ExternalAPIService()

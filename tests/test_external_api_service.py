from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.exceptions import ExternalAPIException, ExternalAPITimeoutException
from app.services.external_api_service import ExternalAPIService


class TestExternalAPIService:
    """
    Pruebas para el servicio de API externa.
    """

    def setup_method(self):
        """
        Configuración antes de cada prueba.
        """
        self.service = ExternalAPIService()

    @pytest.mark.asyncio
    async def test_get_user_data_success(self):
        """
        Prueba la obtención exitosa de datos de usuario.
        """
        expected_data = {
            "id": 1,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "Sincere@april.biz",
        }
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: expected_data  # Usar lambda directa en lugar de return_value

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await self.service.get_user_data(1)

            assert result["id"] == expected_data["id"]
            assert result["name"] == expected_data["name"]
            assert result["email"] == expected_data["email"]

    @pytest.mark.asyncio
    async def test_get_user_data_not_found(self):
        """
        Prueba el manejo de usuario no encontrado.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await self.service.get_user_data(999)

            assert result == {}

    @pytest.mark.asyncio
    async def test_get_user_data_server_error(self):
        """
        Prueba el manejo de errores del servidor.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ExternalAPIException):
                await self.service.get_user_data(1)

    @pytest.mark.asyncio
    async def test_get_user_data_timeout(self):
        """
        Prueba el manejo de timeout.
        """
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Timeout")):
            with pytest.raises(ExternalAPITimeoutException):
                await self.service.get_user_data(1)

    @pytest.mark.asyncio
    async def test_get_user_data_http_error(self):
        """
        Prueba el manejo de errores HTTP.
        """
        with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPError("HTTP Error")):
            with pytest.raises(ExternalAPIException):
                await self.service.get_user_data(1)

    @pytest.mark.asyncio
    async def test_get_post_data_success(self):
        """
        Prueba la obtención exitosa de datos de post.
        """
        expected_data = {
            "id": 1,
            "title": "sunt aut facere repellat",
            "body": "quia et suscipit\nsuscipit recusandae",
            "userId": 1,
        }
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: expected_data  # Usar lambda directa en lugar de return_value

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await self.service.get_post_data(1)

            assert result["id"] == expected_data["id"]
            assert result["title"] == expected_data["title"]
            assert result["userId"] == expected_data["userId"]

    @pytest.mark.asyncio
    async def test_get_post_data_not_found(self):
        """
        Prueba el manejo de post no encontrado.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await self.service.get_post_data(999)

            assert result == {}

    @pytest.mark.asyncio
    async def test_get_status_check_healthy(self):
        """
        Prueba el health check cuando la API está funcionando.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await self.service.get_status_check()

            assert result["status"] == "active"
            assert "funcionando correctamente" in result["message"]

    @pytest.mark.asyncio
    async def test_get_status_check_unhealthy(self):
        """
        Prueba el health check cuando la API no está funcionando.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await self.service.get_status_check()

            assert result["status"] == "inactive"
            assert "500" in result["message"]

    @pytest.mark.asyncio
    async def test_get_status_check_error(self):
        """
        Prueba el health check cuando hay error de conexión.
        """
        with patch("httpx.AsyncClient.get", side_effect=Exception("Connection error")):
            result = await self.service.get_status_check()

            assert result["status"] == "error"
            assert "No se pudo conectar" in result["message"]

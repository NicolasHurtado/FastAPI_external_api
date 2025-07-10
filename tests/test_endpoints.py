from unittest.mock import patch

import pytest

from app.exceptions import ExternalAPIException
from app.services.email_service import email_service
from app.services.external_api_service import external_api_service


class TestUsuarioEndpoints:
    """
    Pruebas para los endpoints de usuarios.
    """

    def test_create_usuario(self, client):
        """
        Prueba la creación de un usuario.
        """
        usuario_data = {
            "nombre": "Test User",
            "email": "test@example.com",
            "activo": True,
        }

        response = client.post("/api/v1/usuarios/", json=usuario_data)

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == usuario_data["nombre"]
        assert data["email"] == usuario_data["email"]
        assert data["activo"] == usuario_data["activo"]
        assert "id" in data

    def test_create_usuario_duplicate_email(self, client, sample_usuario):
        """
        Prueba la creación de un usuario con email duplicado.
        """
        usuario_data = {
            "nombre": "Another User",
            "email": sample_usuario.email,
            "activo": True,
        }

        response = client.post("/api/v1/usuarios/", json=usuario_data)

        assert response.status_code == 400
        data = response.json()
        assert "Ya existe un usuario con este email" in data["error"]

    def test_get_usuario(self, client, sample_usuario):
        """
        Prueba la obtención de un usuario por ID.
        """
        response = client.get(f"/api/v1/usuarios/{sample_usuario.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_usuario.id
        assert data["nombre"] == sample_usuario.nombre
        assert data["email"] == sample_usuario.email

    def test_get_usuario_not_found(self, client):
        """
        Prueba la obtención de un usuario que no existe.
        """
        response = client.get("/api/v1/usuarios/999")

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["error"]

    def test_get_usuarios_list(self, client, sample_usuario):
        """
        Prueba la obtención de la lista de usuarios.
        """
        response = client.get("/api/v1/usuarios/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == sample_usuario.id

    def test_update_usuario(self, client, sample_usuario):
        """
        Prueba la actualización de un usuario.
        """
        update_data = {"nombre": "Updated Name"}

        response = client.put(f"/api/v1/usuarios/{sample_usuario.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Updated Name"
        assert data["email"] == sample_usuario.email

    def test_delete_usuario(self, client, sample_usuario):
        """
        Prueba la eliminación de un usuario.
        """
        response = client.delete(f"/api/v1/usuarios/{sample_usuario.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_usuario.id

        # Verificar que el usuario ya no existe
        response = client.get(f"/api/v1/usuarios/{sample_usuario.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_usuario_con_datos_externos(self, client, sample_usuario):
        """
        Prueba el endpoint principal que combina datos locales y externos.
        """
        # Mock de la API externa
        mock_external_data = {
            "id": sample_usuario.id,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "Sincere@april.biz",
            "status": "active",
        }

        with patch.object(external_api_service, "get_user_data", return_value=mock_external_data):
            response = client.get(f"/api/v1/usuarios/{sample_usuario.id}/con-datos-externos")

            assert response.status_code == 200
            data = response.json()
            print(" data: ", data)
            assert data["id"] == sample_usuario.id
            assert data["nombre"] == sample_usuario.nombre
            assert "datos_externos" in data
            assert data["datos_externos"]["name"] == mock_external_data["name"]

    @pytest.mark.asyncio
    async def test_get_usuario_con_datos_externos_with_email_notification(
        self, client, sample_usuario
    ):
        """
        Prueba el endpoint con notificación por email cuando el usuario está inactivo.
        """
        # Mock de la API externa con estado inactivo
        mock_external_data = {"id": 1, "name": "Leanne Graham", "status": "inactive"}

        with patch.object(
            external_api_service, "get_user_data", return_value=mock_external_data
        ), patch.object(
            email_service, "send_user_status_notification", return_value=True
        ) as mock_email:
            response = client.get(f"/api/v1/usuarios/{sample_usuario.id}/con-datos-externos")

            assert response.status_code == 200
            data = response.json()
            assert data["datos_externos"]["status"] == "inactive"

            # Verificar que se llamó al servicio de email
            mock_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_usuario_con_datos_externos_api_error(self, client, sample_usuario):
        """
        Prueba el endpoint cuando la API externa falla.
        """
        with patch.object(
            external_api_service,
            "get_user_data",
            side_effect=ExternalAPIException("API Error"),
        ):
            response = client.get(f"/api/v1/usuarios/{sample_usuario.id}/con-datos-externos")

            print(response.json())

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == sample_usuario.id
            assert "datos_externos" in data
            assert data["datos_externos"]["error"] == "No se pudieron obtener datos externos"


class TestHealthEndpoints:
    """
    Pruebas para los endpoints de health check.
    """

    def test_basic_health_check(self, client):
        """
        Prueba el health check básico.
        """
        response = client.get("/api/v1/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_detailed_health_check(self, client):
        """
        Prueba el health check detallado.
        """
        mock_external_status = {
            "status": "active",
            "message": "API externa funcionando correctamente",
        }

        with patch.object(
            external_api_service, "get_status_check", return_value=mock_external_status
        ):
            response = client.get("/api/v1/health/detailed")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "components" in data
            assert "database" in data["components"]
            assert "external_api" in data["components"]

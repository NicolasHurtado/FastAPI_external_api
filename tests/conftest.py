import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Usuario

# Base de datos de pruebas en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas para las pruebas
Base.metadata.create_all(bind=engine)


def override_get_db():
    """
    Override de la función get_db para usar la base de datos de pruebas.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Aplicar el override
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    """
    Fixture para obtener una sesión de base de datos de pruebas.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """
    Fixture para obtener un cliente de pruebas de FastAPI.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_usuario(db):
    """
    Fixture para crear un usuario de prueba.
    """
    usuario = Usuario(nombre="Test User", email="test@example.com", activo=True)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def mock_external_api():
    """
    Fixture para mockear el servicio de API externa.
    """
    mock = AsyncMock()
    mock.get_user_data.return_value = {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "status": "active",
    }
    mock.get_post_data.return_value = {
        "id": 1,
        "title": "sunt aut facere repellat",
        "body": "quia et suscipit\nsuscipit recusandae",
        "userId": 1,
    }
    mock.get_status_check.return_value = {
        "status": "active",
        "message": "API externa funcionando correctamente",
    }
    return mock


@pytest.fixture
def mock_email_service():
    """
    Fixture para mockear el servicio de email.
    """
    mock = MagicMock()
    mock.send_email.return_value = True
    mock.send_user_status_notification.return_value = True
    return mock


@pytest.fixture(autouse=True)
def cleanup_database():
    """
    Fixture que limpia la base de datos después de cada prueba.
    """
    yield
    # Limpiar tablas después de cada prueba
    db = TestingSessionLocal()
    try:
        db.query(Usuario).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """
    Fixture para manejar el loop de eventos de asyncio.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

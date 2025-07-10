from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee variables de entorno automáticamente.
    """

    # Base de datos
    database_url: str = "postgresql://user:password@localhost:5432/test_db"

    # API Externa (usaremos JSONPlaceholder como ejemplo)
    external_api_base_url: str = "https://jsonplaceholder.typicode.com"
    external_api_timeout: int = 30

    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Configuración de email (opcional)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # Configuración de la aplicación
    app_name: str = "Test Técnico Backend API"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Función para obtener la configuración de manera singleton.
    """
    return Settings()

import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import get_settings

logger = logging.getLogger(__name__)

# Configuración de la base de datos
settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=False,  # Muestra las consultas SQL en desarrollo
    pool_pre_ping=True,  # Verifica conexiones antes de usar
    pool_recycle=3600,  # Recicla conexiones cada hora
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener una sesión de base de datos.
    Se encarga de cerrar la sesión automáticamente.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en la sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """
    Crea todas las tablas definidas en los modelos.
    """
    Base.metadata.create_all(bind=engine)

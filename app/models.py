from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Usuario(Base):
    """
    Modelo de Usuario para la prueba técnica.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, nombre='{self.nombre}', email='{self.email}')>"

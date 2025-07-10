import re
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""

    nombre: str = Field(..., min_length=1, max_length=100)
    email: str
    activo: bool = True

    @validator("email")
    def validate_email(cls, v: str) -> str:
        """Validador simple para email"""
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Email inválido")
        return v


class UsuarioCreate(UsuarioBase):
    """Schema para crear un Usuario"""

    pass


class UsuarioUpdate(BaseModel):
    """Schema para actualizar un Usuario"""

    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    activo: Optional[bool] = None

    @validator("email")
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validador simple para email"""
        if v is not None and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Email inválido")
        return v


class Usuario(UsuarioBase):
    """Schema para respuesta de Usuario"""

    id: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioConDatosExternos(Usuario):
    """Schema para respuesta de Usuario con datos externos"""

    datos_externos: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""

    error: str
    detail: Optional[str] = None
    status_code: int

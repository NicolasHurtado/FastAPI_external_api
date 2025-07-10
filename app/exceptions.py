from typing import Optional

from fastapi import HTTPException


class BaseCustomException(HTTPException):
    """
    Excepción base personalizada para la aplicación.
    """

    def __init__(self, status_code: int, detail: str, headers: Optional[dict] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class DatabaseException(BaseCustomException):
    """
    Excepción para errores de base de datos.
    """

    def __init__(self, detail: str = "Error en la base de datos"):
        super().__init__(status_code=500, detail=detail)


class RecordNotFoundException(BaseCustomException):
    """
    Excepción cuando no se encuentra un registro en la base de datos.
    """

    def __init__(self, detail: str = "Registro no encontrado"):
        super().__init__(status_code=404, detail=detail)


class ExternalAPIException(BaseCustomException):
    """
    Excepción para errores de API externa.
    """

    def __init__(self, detail: str = "Error en la API externa"):
        super().__init__(status_code=502, detail=detail)


class ExternalAPITimeoutException(BaseCustomException):
    """
    Excepción para timeout en API externa.
    """

    def __init__(self, detail: str = "Timeout en la API externa"):
        super().__init__(status_code=504, detail=detail)


class ValidationException(BaseCustomException):
    """
    Excepción para errores de validación.
    """

    def __init__(self, detail: str = "Error de validación"):
        super().__init__(status_code=422, detail=detail)


class EmailServiceException(BaseCustomException):
    """
    Excepción para errores en el servicio de correo.
    """

    def __init__(self, detail: str = "Error en el servicio de correo"):
        super().__init__(status_code=500, detail=detail)

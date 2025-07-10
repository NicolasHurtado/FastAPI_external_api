import logging
from typing import Generic, List, Optional, Type, TypeVar, Protocol

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..exceptions import DatabaseException, RecordNotFoundException
from ..models import Usuario
from ..schemas import UsuarioCreate, UsuarioUpdate

logger = logging.getLogger(__name__)


class HasID(Protocol):
    """Protocolo para objetos que tienen un atributo id."""
    id: int


# TypeVar para tipo genérico con bounds
ModelType = TypeVar("ModelType", bound=HasID)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para operaciones CRUD genéricas.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Obtiene un registro por ID.

        Args:
            db: Sesión de base de datos
            id: ID del registro

        Returns:
            Registro encontrado o None
        """
        try:
            return db.query(self.model).filter(self.model.id == id).first()  # type: ignore
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener {self.model.__name__} con ID {id}: {e}")
            raise DatabaseException(f"Error al obtener {self.model.__name__}")

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtiene múltiples registros.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de registros
        """
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener lista de {self.model.__name__}: {e}")
            raise DatabaseException(f"Error al obtener lista de {self.model.__name__}")

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        Crea un nuevo registro.

        Args:
            db: Sesión de base de datos
            obj_in: Datos para crear el registro

        Returns:
            Registro creado
        """
        try:
            obj_in_data = obj_in.dict()
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Creado {self.model.__name__} con ID {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error al crear {self.model.__name__}: {e}")
            db.rollback()
            raise DatabaseException(f"Error al crear {self.model.__name__}")

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """
        Actualiza un registro existente.

        Args:
            db: Sesión de base de datos
            db_obj: Registro a actualizar
            obj_in: Datos para actualizar

        Returns:
            Registro actualizado
        """
        try:
            obj_data = obj_in.dict(exclude_unset=True)
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Actualizado {self.model.__name__} con ID {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar {self.model.__name__}: {e}")
            db.rollback()
            raise DatabaseException(f"Error al actualizar {self.model.__name__}")

    def delete(self, db: Session, id: int) -> ModelType:
        """
        Elimina un registro por ID.

        Args:
            db: Sesión de base de datos
            id: ID del registro a eliminar

        Returns:
            Registro eliminado
        """
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()  # type: ignore
            if not obj:
                raise RecordNotFoundException(f"{self.model.__name__} con ID {id} no encontrado")
            db.delete(obj)
            db.commit()
            logger.info(f"Eliminado {self.model.__name__} con ID {id}")
            return obj
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar {self.model.__name__} con ID {id}: {e}")
            db.rollback()
            raise DatabaseException(f"Error al eliminar {self.model.__name__}")


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """
    Operaciones CRUD específicas para Usuario.
    """

    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por email.

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Returns:
            Usuario encontrado o None
        """
        try:
            return db.query(Usuario).filter(Usuario.email == email).first()  # type: ignore
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener usuario por email {email}: {e}")
            raise DatabaseException("Error al obtener usuario por email")

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtiene usuarios activos.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de usuarios activos
        """
        try:
            return db.query(Usuario).filter(Usuario.activo).offset(skip).limit(limit).all()  # type: ignore
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener usuarios activos: {e}")
            raise DatabaseException("Error al obtener usuarios activos")


# Instancia del servicio CRUD
crud_usuario = CRUDUsuario(Usuario)

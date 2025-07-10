import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...exceptions import ExternalAPIException, RecordNotFoundException
from ...models import Usuario as UsuarioModel
from ...schemas import Usuario, UsuarioConDatosExternos, UsuarioCreate, UsuarioUpdate
from ...services.database_service import crud_usuario
from ...services.email_service import email_service
from ...services.external_api_service import external_api_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{usuario_id}/con-datos-externos", response_model=UsuarioConDatosExternos)
async def get_usuario_con_datos_externos(usuario_id: int, db: Session = Depends(get_db)) -> UsuarioConDatosExternos:
    """
    Endpoint principal que cumple con el requisito de la prueba técnica.

    Obtiene un usuario de la base de datos y combina la información
    con datos de una API externa (JSONPlaceholder).

    Si el usuario tiene estado 'inactive' en la API externa,
    se envía un correo de notificación.

    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos

    Returns:
        Usuario con datos externos combinados

    Raises:
        HTTPException: Si el usuario no existe o hay error en la API externa
    """
    try:
        # 1. Obtener usuario de la base de datos
        db_usuario = crud_usuario.get(db=db, id=usuario_id)
        if not db_usuario:
            logger.warning(f"Usuario {usuario_id} no encontrado en base de datos")
            raise HTTPException(
                status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado"
            )

        # 2. Obtener datos de la API externa
        try:
            datos_externos = await external_api_service.get_user_data(usuario_id)
        except ExternalAPIException as e:
            logger.error(f"Error al obtener datos externos para usuario {usuario_id}: {e}")
            # Si la API externa falla, devolvemos el usuario con datos externos vacíos
            datos_externos = {
                "error": "No se pudieron obtener datos externos",
                "status": "error",
            }

        # 3. Verificar si necesitamos enviar correo de notificación
        if datos_externos.get("status") == "inactive":
            try:
                email_service.send_user_status_notification(
                    user_email=str(db_usuario.email),
                    user_name=str(db_usuario.nombre),
                    external_status="inactive",
                )
                logger.info(f"Correo de notificación enviado a {db_usuario.email}")
            except Exception as e:
                logger.error(f"Error al enviar correo de notificación: {e}")
                # No interrumpimos el flujo si el correo falla

        # 4. Combinar datos locales y externos
        usuario_con_datos = UsuarioConDatosExternos(
            **db_usuario.__dict__, datos_externos=datos_externos
        )

        logger.info(f"Usuario {usuario_id} obtenido exitosamente con datos externos")
        return usuario_con_datos

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener usuario {usuario_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=List[Usuario])
def get_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    activos_solo: bool = Query(False, description="Obtener solo usuarios activos"),
    db: Session = Depends(get_db),
) -> List[UsuarioModel]:
    """
    Obtiene una lista de usuarios.

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros
        activos_solo: Si True, obtiene solo usuarios activos
        db: Sesión de base de datos

    Returns:
        Lista de usuarios
    """
    try:
        if activos_solo:
            usuarios = crud_usuario.get_active_users(db=db, skip=skip, limit=limit)
        else:
            usuarios = crud_usuario.get_multi(db=db, skip=skip, limit=limit)

        logger.info(f"Obtenidos {len(usuarios)} usuarios")
        return usuarios

    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{usuario_id}", response_model=Usuario)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)) -> UsuarioModel:
    """
    Obtiene un usuario por ID.

    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos

    Returns:
        Usuario encontrado

    Raises:
        HTTPException: Si el usuario no existe
    """
    try:
        db_usuario = crud_usuario.get(db=db, id=usuario_id)
        if not db_usuario:
            raise HTTPException(
                status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado"
            )

        logger.info(f"Usuario {usuario_id} obtenido exitosamente")
        return db_usuario

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario {usuario_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/", response_model=Usuario, status_code=201)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)) -> UsuarioModel:
    """
    Crea un nuevo usuario.

    Args:
        usuario: Datos del usuario a crear
        db: Sesión de base de datos

    Returns:
        Usuario creado

    Raises:
        HTTPException: Si el email ya existe
    """
    try:
        # Verificar si el email ya existe
        db_usuario = crud_usuario.get_by_email(db=db, email=usuario.email)
        if db_usuario:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con este email")

        nuevo_usuario = crud_usuario.create(db=db, obj_in=usuario)
        logger.info(f"Usuario creado exitosamente con ID {nuevo_usuario.id}")
        return nuevo_usuario

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{usuario_id}", response_model=Usuario)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)) -> UsuarioModel:
    """
    Actualiza un usuario existente.

    Args:
        usuario_id: ID del usuario a actualizar
        usuario: Datos actualizados del usuario
        db: Sesión de base de datos

    Returns:
        Usuario actualizado

    Raises:
        HTTPException: Si el usuario no existe
    """
    try:
        db_usuario = crud_usuario.get(db=db, id=usuario_id)
        if not db_usuario:
            raise HTTPException(
                status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado"
            )

        # Verificar si el nuevo email ya existe (si se está actualizando)
        if usuario.email and usuario.email != db_usuario.email:
            existing_usuario = crud_usuario.get_by_email(db=db, email=usuario.email)
            if existing_usuario:
                raise HTTPException(status_code=400, detail="Ya existe un usuario con este email")

        usuario_actualizado = crud_usuario.update(db=db, db_obj=db_usuario, obj_in=usuario)
        logger.info(f"Usuario {usuario_id} actualizado exitosamente")
        return usuario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar usuario {usuario_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{usuario_id}", response_model=Usuario)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)) -> UsuarioModel:
    """
    Elimina un usuario.

    Args:
        usuario_id: ID del usuario a eliminar
        db: Sesión de base de datos

    Returns:
        Usuario eliminado

    Raises:
        HTTPException: Si el usuario no existe
    """
    try:
        usuario_eliminado = crud_usuario.delete(db=db, id=usuario_id)
        logger.info(f"Usuario {usuario_id} eliminado exitosamente")
        return usuario_eliminado

    except RecordNotFoundException:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
    except Exception as e:
        logger.error(f"Error al eliminar usuario {usuario_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

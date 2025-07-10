#!/usr/bin/env python3
"""
Script para inicializar el usuario de prueba.
Se ejecuta después del arranque de la aplicación.
"""

import sys
import logging
import time
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def wait_for_database(max_attempts: int = 30, delay: int = 2) -> bool:
    """
    Espera a que la base de datos esté disponible.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Tiempo de espera entre intentos en segundos
        
    Returns:
        True si la base de datos está disponible, False si no
    """
    from app.database import get_db
    from sqlalchemy import text
    
    for attempt in range(max_attempts):
        try:
            # Intentar obtener una sesión de base de datos
            db = next(get_db())
            db.execute(text("SELECT 1"))  # Test simple con text()
            db.close()
            logger.info("✅ Base de datos disponible")
            return True
        except Exception as e:
            logger.warning(f"⏳ Intento {attempt + 1}/{max_attempts} - Base de datos no disponible: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    
    logger.error("❌ Base de datos no disponible después de todos los intentos")
    return False


def create_initial_user(
    nombre: str = "Usuario de Prueba",
    email: str = "admin@test.com",
    activo: bool = True
) -> Optional[int]:
    """
    Crea el usuario inicial si no existe.
    
    Args:
        nombre: Nombre del usuario
        email: Email del usuario
        activo: Estado activo del usuario
        
    Returns:
        ID del usuario creado o None si ya existe
    """
    from app.database import get_db
    from app.services.database_service import crud_usuario
    from app.schemas import UsuarioCreate
    
    try:
        # Obtener sesión de base de datos
        db = next(get_db())
        
        try:
            # Verificar si ya existe un usuario con este email
            existing_user = crud_usuario.get_by_email(db, email)
            if existing_user:
                logger.info(f"👤 Usuario ya existe: {existing_user.nombre} ({existing_user.email})")
                return None
            
            # Crear usuario de prueba
            usuario_inicial = UsuarioCreate(
                nombre=nombre,
                email=email,
                activo=activo
            )
            
            created_user = crud_usuario.create(db, usuario_inicial)
            logger.info(f"🎉 Usuario creado exitosamente: {created_user.nombre} (ID: {created_user.id})")
            return created_user.id
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Error de base de datos al crear usuario: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado al crear usuario: {e}")
            return None
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error al conectar con la base de datos: {e}")
        return None


def main():
    """
    Función principal del script.
    """
    logger.info("🚀 Iniciando script de inicialización de usuario...")
    
    # Esperar a que la base de datos esté disponible
    if not wait_for_database():
        logger.error("❌ No se pudo conectar a la base de datos")
        sys.exit(1)
    
    # Crear usuario inicial
    user_id = create_initial_user()
    
    if user_id:
        logger.info(f"✅ Inicialización completada - Usuario creado con ID: {user_id}")
    else:
        logger.info("✅ Inicialización completada - Usuario ya existía")
    
    logger.info("🏁 Script de inicialización finalizado")


if __name__ == "__main__":
    main() 
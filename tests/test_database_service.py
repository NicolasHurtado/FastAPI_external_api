import pytest

from app.exceptions import RecordNotFoundException
from app.schemas import UsuarioCreate, UsuarioUpdate
from app.services.database_service import crud_usuario


class TestCRUDUsuario:
    """
    Pruebas para las operaciones CRUD de Usuario.
    """

    def test_create_usuario(self, db):
        """
        Prueba la creación de un usuario.
        """
        usuario_data = UsuarioCreate(nombre="Juan Test", email="juan.test@example.com", activo=True)

        usuario = crud_usuario.create(db=db, obj_in=usuario_data)

        assert usuario.nombre == "Juan Test"
        assert usuario.email == "juan.test@example.com"
        assert usuario.activo is True
        assert usuario.id is not None

    def test_get_usuario(self, db, sample_usuario):
        """
        Prueba la obtención de un usuario por ID.
        """
        usuario = crud_usuario.get(db=db, id=sample_usuario.id)

        assert usuario is not None
        assert usuario.id == sample_usuario.id
        assert usuario.nombre == sample_usuario.nombre
        assert usuario.email == sample_usuario.email

    def test_get_usuario_not_found(self, db):
        """
        Prueba la obtención de un usuario que no existe.
        """
        usuario = crud_usuario.get(db=db, id=999)

        assert usuario is None

    def test_get_usuario_by_email(self, db, sample_usuario):
        """
        Prueba la obtención de un usuario por email.
        """
        usuario = crud_usuario.get_by_email(db=db, email=sample_usuario.email)

        assert usuario is not None
        assert usuario.email == sample_usuario.email

    def test_update_usuario(self, db, sample_usuario):
        """
        Prueba la actualización de un usuario.
        """
        update_data = UsuarioUpdate(nombre="Updated Name")

        usuario_actualizado = crud_usuario.update(db=db, db_obj=sample_usuario, obj_in=update_data)

        assert usuario_actualizado.nombre == "Updated Name"
        assert usuario_actualizado.email == sample_usuario.email
        assert usuario_actualizado.id == sample_usuario.id

    def test_delete_usuario(self, db, sample_usuario):
        """
        Prueba la eliminación de un usuario.
        """
        usuario_eliminado = crud_usuario.delete(db=db, id=sample_usuario.id)

        assert usuario_eliminado.id == sample_usuario.id

        # Verificar que el usuario ya no existe
        usuario_verificacion = crud_usuario.get(db=db, id=sample_usuario.id)
        assert usuario_verificacion is None

    def test_delete_usuario_not_found(self, db):
        """
        Prueba la eliminación de un usuario que no existe.
        """
        with pytest.raises(RecordNotFoundException):
            crud_usuario.delete(db=db, id=999)

    def test_get_active_users(self, db):
        """
        Prueba la obtención de usuarios activos.
        """
        # Crear usuarios activos e inactivos
        usuario_activo = UsuarioCreate(
            nombre="Usuario Activo", email="activo@example.com", activo=True
        )
        usuario_inactivo = UsuarioCreate(
            nombre="Usuario Inactivo", email="inactivo@example.com", activo=False
        )

        crud_usuario.create(db=db, obj_in=usuario_activo)
        crud_usuario.create(db=db, obj_in=usuario_inactivo)

        usuarios_activos = crud_usuario.get_active_users(db=db)

        assert len(usuarios_activos) == 1
        assert usuarios_activos[0].activo is True

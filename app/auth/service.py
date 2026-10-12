
from pwdlib import PasswordHash
from psycopg.errors import UniqueViolation

from app.database.connection import get_db_connection


# Configura el algoritmo de hash seguro para las contraseñas.
password_hash = PasswordHash.recommended()


def registrar_usuario(usuario: str, password: str) -> bool:
    """Registra un usuario y almacena el hash de su contraseña."""

    # Genera un hash; la contraseña original no se guarda en la base de datos.
    hash_generado = password_hash.hash(password)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Inserta el usuario y su hash en la tabla de usuarios.
            cursor.execute(
                """
                INSERT INTO usuarios (usuario, password_hash)
                VALUES (%s, %s)
                """,
                (usuario, hash_generado)
            )

        # Confirma la transacción para guardar el registro.
        connection.commit()
        return True

    except UniqueViolation:
        # Revierte la transacción si el nombre de usuario ya existe.
        connection.rollback()
        return False

    finally:
        # Cierra la conexión incluso si ocurre un error.
        connection.close()


def autenticar_usuario(usuario: str, password: str) -> bool:
    """Comprueba si las credenciales corresponden a un usuario registrado."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Busca el hash asociado al nombre de usuario.
            cursor.execute(
                """
                SELECT password_hash
                FROM usuarios
                WHERE usuario = %s
                """,
                (usuario,)
            )

            resultado = cursor.fetchone()

        # Si el usuario no existe, la autenticación falla.
        if resultado is None:
            return False

        hash_guardado = resultado[0]

        # Compara la contraseña recibida con el hash almacenado.
        return password_hash.verify(password, hash_guardado)

    finally:
        # Libera la conexión con PostgreSQL.
        connection.close()

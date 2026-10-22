
from pwdlib import PasswordHash
from psycopg.errors import UniqueViolation

from app.database.connection import get_db_connection


# Configura el algoritmo recomendado para proteger contraseñas.
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


def autenticar_usuario(usuario: str, password: str) -> int | None:
    """
    Verifica las credenciales y devuelve el ID del usuario
    si la autenticación es correcta.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Ejecuta la consulta para obtener el ID y el hash de la contraseña del usuario.
            cursor.execute(
                """
                SELECT id, password_hash
                FROM usuarios
                WHERE usuario = %s
                """,
                (usuario,)
            )

            resultado = cursor.fetchone()

        # El usuario no existe.
        if resultado is None:
            return None

        usuario_id, hash_guardado = resultado

        # La contraseña no coincide.
        if not password_hash.verify(password, hash_guardado):
            return None

        # Las credenciales son correctas.
        return usuario_id

    finally:
        connection.close()


from datetime import date

from pwdlib import PasswordHash
from psycopg.errors import UniqueViolation

from app.database.connection import get_db_connection


# Configura el algoritmo recomendado para proteger contraseñas.
password_hash = PasswordHash.recommended()


def registrar_usuario(
    nombre: str,
    correo: str,
    fecha_nacimiento: date,
    password: str
) -> bool:
    """Registra un usuario y almacena el hash de su contraseña."""

    # Genera el hash; nunca guarda la contraseña original.
    hash_generado = password_hash.hash(password)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre,
                    correo,
                    fecha_nacimiento,
                    password_hash
                )
                VALUES (%s, LOWER(%s), %s, %s)
                """,
                (nombre, correo, fecha_nacimiento, hash_generado)
            )

        connection.commit()
        return True

    except UniqueViolation:
        connection.rollback()
        return False

    finally:
        connection.close()


def autenticar_usuario(correo: str, password: str) -> int | None:
    """
    Verifica las credenciales y devuelve el ID del usuario
    si la autenticación es correcta.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, password_hash
                FROM usuarios
                WHERE LOWER(correo) = LOWER(%s)
                """,
                (correo,)
            )

            resultado = cursor.fetchone()

        # El correo no existe.
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

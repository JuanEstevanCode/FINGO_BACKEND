
from app.database.connection import get_db_connection


def get_categories(usuario_id: int, tipo: str | None = None):
    """Lista las categorías predeterminadas y las personales activas."""

    connection = get_db_connection()

    try:
        condiciones = [
            "activa = TRUE",
            "(usuario_id IS NULL OR usuario_id = %s)",
        ]
        parametros = [usuario_id]

        if tipo:
            condiciones.append("tipo = %s")
            parametros.append(tipo)

        consulta = f"""
            SELECT
                id,
                nombre,
                tipo,
                es_predeterminada,
                activa
            FROM categorias
            WHERE {" AND ".join(condiciones)}
            ORDER BY tipo, es_predeterminada DESC, nombre;
        """

        with connection.cursor() as cursor:
            cursor.execute(consulta, tuple(parametros))
            return cursor.fetchall()

    finally:
        connection.close()


def get_category_by_id(categoria_id: int, usuario_id: int):
    """Obtiene una categoría accesible para el usuario."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, tipo, usuario_id,
                       es_predeterminada, activa
                FROM categorias
                WHERE id = %s
                  AND activa = TRUE
                  AND (usuario_id IS NULL OR usuario_id = %s);
                """,
                (categoria_id, usuario_id),
            )

            return cursor.fetchone()

    finally:
        connection.close()


def create_category(nombre: str, tipo: str, usuario_id: int):
    """Crea una categoría personal."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO categorias (
                    nombre, tipo, usuario_id, es_predeterminada
                )
                VALUES (%s, %s, %s, FALSE)
                RETURNING id;
                """,
                (nombre, tipo, usuario_id),
            )

            categoria_id = cursor.fetchone()[0]

        connection.commit()
        return categoria_id

    finally:
        connection.close()


def update_category(
    categoria_id: int,
    nombre: str,
    usuario_id: int,
):
    """Renombra una categoría personal del usuario."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE categorias
                SET nombre = %s
                WHERE id = %s
                  AND usuario_id = %s
                  AND es_predeterminada = FALSE
                  AND activa = TRUE
                RETURNING id;
                """,
                (nombre, categoria_id, usuario_id),
            )

            resultado = cursor.fetchone()

        connection.commit()
        return resultado[0] if resultado else None

    finally:
        connection.close()


def deactivate_category(categoria_id: int, usuario_id: int):
    """Desactiva una categoría personal sin borrar su historial."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE categorias
                SET activa = FALSE
                WHERE id = %s
                  AND usuario_id = %s
                  AND es_predeterminada = FALSE
                  AND activa = TRUE
                RETURNING id;
                """,
                (categoria_id, usuario_id),
            )

            resultado = cursor.fetchone()

        connection.commit()
        return resultado[0] if resultado else None

    finally:
        connection.close()

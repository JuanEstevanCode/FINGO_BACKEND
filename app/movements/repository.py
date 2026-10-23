
from app.database.connection import get_db_connection


def validar_categoria(categoria_id: int, tipo: str, usuario_id: int):
    """
    Verifica que la categoría exista, esté activa,
    sea accesible para el usuario y corresponda al tipo.
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, tipo
                FROM categorias
                WHERE id = %s
                  AND activa = TRUE
                  AND (usuario_id IS NULL OR usuario_id = %s);
                """,
                (categoria_id, usuario_id),
            )

            categoria = cursor.fetchone()

        if categoria is None:
            return None

        if categoria[2] != tipo:
            return None

        return categoria

    finally:
        connection.close()


def create_movement(
    tipo, monto, categoria_id, descripcion, fecha, usuario_id
):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO movimientos (
                    tipo,
                    monto,
                    categoria_id,
                    descripcion,
                    fecha,
                    usuario_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    tipo,
                    monto,
                    categoria_id,
                    descripcion,
                    fecha,
                    usuario_id,
                ),
            )

            movement_id = cursor.fetchone()[0]

        connection.commit()
        return movement_id

    finally:
        connection.close()


def get_movements(
    usuario_id,
    tipo=None,
    categoria_id=None,
    fecha_desde=None,
    fecha_hasta=None,
    limite=20,
    desplazamiento=0,
):
    connection = get_db_connection()

    try:
        condiciones = ["m.usuario_id = %s"]
        parametros = [usuario_id]

        if tipo:
            condiciones.append("LOWER(m.tipo) = LOWER(%s)")
            parametros.append(tipo)

        if categoria_id is not None:
            condiciones.append("m.categoria_id = %s")
            parametros.append(categoria_id)

        if fecha_desde:
            condiciones.append("m.fecha >= %s")
            parametros.append(fecha_desde)

        if fecha_hasta:
            condiciones.append("m.fecha <= %s")
            parametros.append(fecha_hasta)

        consulta = f"""
            SELECT
                m.id,
                m.tipo,
                m.monto,
                m.categoria_id,
                c.nombre AS categoria,
                m.descripcion,
                m.fecha
            FROM movimientos AS m
            INNER JOIN categorias AS c
                ON c.id = m.categoria_id
            WHERE {" AND ".join(condiciones)}
            ORDER BY m.fecha DESC, m.id DESC
            LIMIT %s OFFSET %s;
        """

        parametros.extend([limite, desplazamiento])

        with connection.cursor() as cursor:
            cursor.execute(consulta, tuple(parametros))
            return cursor.fetchall()

    finally:
        connection.close()


def get_movement(movement_id, usuario_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    m.id,
                    m.tipo,
                    m.monto,
                    m.categoria_id,
                    c.nombre AS categoria,
                    m.descripcion,
                    m.fecha
                FROM movimientos AS m
                INNER JOIN categorias AS c
                    ON c.id = m.categoria_id
                WHERE m.id = %s
                  AND m.usuario_id = %s;
                """,
                (movement_id, usuario_id),
            )

            return cursor.fetchone()

    finally:
        connection.close()


def update_movement(
    movement_id,
    tipo,
    monto,
    categoria_id,
    descripcion,
    fecha,
    usuario_id,
):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE movimientos
                SET
                    tipo = %s,
                    monto = %s,
                    categoria_id = %s,
                    descripcion = %s,
                    fecha = %s
                WHERE id = %s
                  AND usuario_id = %s
                RETURNING id;
                """,
                (
                    tipo,
                    monto,
                    categoria_id,
                    descripcion,
                    fecha,
                    movement_id,
                    usuario_id,
                ),
            )

            resultado = cursor.fetchone()

        connection.commit()
        return resultado[0] if resultado else None

    finally:
        connection.close()


def delete_movement(movement_id, usuario_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM movimientos
                WHERE id = %s AND usuario_id = %s;
                """,
                (movement_id, usuario_id),
            )

            filas_eliminadas = cursor.rowcount

        connection.commit()
        return filas_eliminadas

    finally:
        connection.close()

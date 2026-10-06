from app.database.connection import get_db_connection

def create_movement(tipo, monto, categoria, descripcion, fecha):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO movimientos
                (tipo, monto, categoria, descripcion, fecha)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (tipo, monto, categoria, descripcion, fecha)
            )
            movement_id = cursor.fetchone()[0]
            connection.commit()

            return movement_id

    finally:
        connection.close()


def get_movements():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tipo, monto, categoria, descripcion, fecha
                FROM movimientos;
                """
            )
            movements = cursor.fetchall()

            return movements

    finally:
        connection.close()


def update_movement(movement_id, tipo, monto, categoria, descripcion, fecha):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE movimientos
                SET tipo = %s,
                    monto = %s,
                    categoria = %s,
                    descripcion = %s,
                    fecha = %s
                WHERE id = %s;
                """,
                (tipo, monto, categoria, descripcion, fecha, movement_id)
            )
            connection.commit()

            return cursor.rowcount

    finally:
        connection.close()


def delete_movement(movement_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM movimientos
                WHERE id = %s;
                """,
                (movement_id,)
            )
            connection.commit()

            return cursor.rowcount

    finally:
        connection.close()
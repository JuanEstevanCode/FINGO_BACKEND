
from app.database.connection import get_db_connection


BUDGET_SELECT = """
    SELECT
        p.id,
        p.usuario_id,
        p.categoria_id,
        c.nombre AS categoria_nombre,
        p.tipo_periodo,
        p.fecha_inicio,
        p.fecha_fin,
        p.monto_limite,
        p.fecha_creacion,
        COALESCE(SUM(m.monto), 0)::NUMERIC(12, 2) AS gasto_acumulado,
        (
            p.monto_limite - COALESCE(SUM(m.monto), 0)
        )::NUMERIC(12, 2) AS saldo_disponible,
        ROUND(
            COALESCE(SUM(m.monto), 0) * 100 / p.monto_limite,
            2
        ) AS porcentaje_utilizado,
        CASE
            WHEN COALESCE(SUM(m.monto), 0) > p.monto_limite
                THEN 'excedido'
            WHEN COALESCE(SUM(m.monto), 0) >= p.monto_limite * 0.80
                THEN 'proximo_limite'
            ELSE 'normal'
        END AS estado
    FROM presupuestos p
    JOIN categorias c
        ON c.id = p.categoria_id
    LEFT JOIN movimientos m
        ON m.usuario_id = p.usuario_id
        AND m.categoria_id = p.categoria_id
        AND m.tipo = 'gasto'
        AND m.fecha >= p.fecha_inicio
        AND m.fecha <= p.fecha_fin
"""

def _row_to_dict(cursor, row):
    if row is None:
        return None

    columnas = [columna.name for columna in cursor.description]
    return dict(zip(columnas, row))


def _budget_query(usuario_id: int, presupuesto_id: int | None = None):
    condiciones = ["p.usuario_id = %s"]
    parametros = [usuario_id]

    if presupuesto_id is not None:
        condiciones.append("p.id = %s")
        parametros.append(presupuesto_id)

    consulta = (
        BUDGET_SELECT
        + " WHERE "
        + " AND ".join(condiciones)
        + """
        GROUP BY
            p.id,
            p.usuario_id,
            p.categoria_id,
            c.nombre,
            p.tipo_periodo,
            p.fecha_inicio,
            p.fecha_fin,
            p.monto_limite,
            p.fecha_creacion
        ORDER BY p.fecha_inicio DESC, p.id DESC
        """
    )

    return consulta, parametros


def get_budgets(usuario_id: int):
    consulta, parametros = _budget_query(usuario_id)
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(consulta, parametros)
            return [
                _row_to_dict(cursor, fila)
                for fila in cursor.fetchall()
            ]
    finally:
        connection.close()


def get_budget_by_id(presupuesto_id: int, usuario_id: int):
    consulta, parametros = _budget_query(usuario_id, presupuesto_id)
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(consulta, parametros)
            return _row_to_dict(cursor, cursor.fetchone())
    finally:
        connection.close()



def create_budget(
    usuario_id: int,
    categoria_id: int,
    tipo_periodo: str,
    fecha_inicio,
    fecha_fin,
    monto_limite,
):
    connection = get_db_connection()
    presupuesto_id = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM categorias
                WHERE id = %s
                  AND tipo = 'gasto'
                  AND activa = TRUE
                  AND (usuario_id IS NULL OR usuario_id = %s)
                """,
                (categoria_id, usuario_id),
            )

            if cursor.fetchone() is None:
                return None

            cursor.execute(
                """
                INSERT INTO presupuestos (
                    usuario_id,
                    categoria_id,
                    tipo_periodo,
                    fecha_inicio,
                    fecha_fin,
                    monto_limite
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    usuario_id,
                    categoria_id,
                    tipo_periodo,
                    fecha_inicio,
                    fecha_fin,
                    monto_limite,
                ),
            )

            presupuesto_id = cursor.fetchone()[0]

        connection.commit()

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return get_budget_by_id(presupuesto_id, usuario_id)


def update_budget(
    presupuesto_id: int,
    usuario_id: int,
    categoria_id: int,
    tipo_periodo: str,
    fecha_inicio,
    fecha_fin,
    monto_limite,
):
    connection = get_db_connection()
    actualizado = False

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM presupuestos
                WHERE id = %s
                  AND usuario_id = %s
                """,
                (presupuesto_id, usuario_id),
            )

            if cursor.fetchone() is None:
                return None

            cursor.execute(
                """
                SELECT id
                FROM categorias
                WHERE id = %s
                  AND tipo = 'gasto'
                  AND activa = TRUE
                  AND (usuario_id IS NULL OR usuario_id = %s)
                """,
                (categoria_id, usuario_id),
            )

            if cursor.fetchone() is None:
                return None

            cursor.execute(
                """
                UPDATE presupuestos
                SET
                    categoria_id = %s,
                    tipo_periodo = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s,
                    monto_limite = %s
                WHERE id = %s
                  AND usuario_id = %s
                RETURNING id
                """,
                (
                    categoria_id,
                    tipo_periodo,
                    fecha_inicio,
                    fecha_fin,
                    monto_limite,
                    presupuesto_id,
                    usuario_id,
                ),
            )

            actualizado = cursor.fetchone() is not None

        connection.commit()

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    if not actualizado:
        return None

    return get_budget_by_id(presupuesto_id, usuario_id)


def delete_budget(presupuesto_id: int, usuario_id: int):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM presupuestos
                WHERE id = %s AND usuario_id = %s
                RETURNING id
                """,
                (presupuesto_id, usuario_id),
            )

            eliminado = cursor.fetchone()
            connection.commit()

            return eliminado is not None
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

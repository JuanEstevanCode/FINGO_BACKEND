
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import obtener_usuario_actual
from app.movements.repository import validar_categoria
from app.movements.repository import (
    create_movement,
    get_movements,
    get_movement,
    update_movement as update_movement_repository,
    delete_movement as delete_movement_repository,
)
from app.movements.schemas import movement_create


router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


def verificar_categoria(categoria_id: int, tipo: str, usuario_id: int):
    categoria = validar_categoria(categoria_id, tipo, usuario_id)

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La categoría no es válida, está inactiva o no corresponde al tipo de movimiento.",
        )

    return categoria


@router.post("/", status_code=status.HTTP_201_CREATED)
def register_movement(
    movement: movement_create,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    verificar_categoria(movement.categoria_id, movement.tipo, usuario_id)

    movement_id = create_movement(
        movement.tipo,
        movement.monto,
        movement.categoria_id,
        movement.descripcion,
        movement.fecha,
        usuario_id,
    )

    return {
        "message": "Movimiento registrado correctamente",
        "id": movement_id,
    }


@router.get("/")
def list_movements(
    tipo: str | None = Query(default=None),
    categoria_id: int | None = Query(default=None, gt=0),
    fecha_desde: date | None = Query(default=None),
    fecha_hasta: date | None = Query(default=None),
    limite: int = Query(default=20, ge=1, le=100),
    desplazamiento: int = Query(default=0, ge=0),
    usuario_id: int = Depends(obtener_usuario_actual),
):
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha inicial no puede ser posterior a la fecha final.",
        )

    if tipo and tipo.lower() not in ("ingreso", "gasto"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El tipo debe ser 'ingreso' o 'gasto'.",
        )

    return get_movements(
        usuario_id=usuario_id,
        tipo=tipo.lower() if tipo else None,
        categoria_id=categoria_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
        desplazamiento=desplazamiento,
    )


@router.get("/{movement_id}")
def read_movement(
    movement_id: int,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    movement = get_movement(movement_id, usuario_id)

    if movement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento no encontrado.",
        )

    return movement


@router.put("/{movement_id}")
def update_movement(
    movement_id: int,
    movement: movement_create,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    verificar_categoria(movement.categoria_id, movement.tipo, usuario_id)

    updated_movement_id = update_movement_repository(
        movement_id,
        movement.tipo,
        movement.monto,
        movement.categoria_id,
        movement.descripcion,
        movement.fecha,
        usuario_id,
    )

    if updated_movement_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento no encontrado.",
        )

    return {
        "message": "Movimiento actualizado correctamente",
        "id": updated_movement_id,
    }


@router.delete("/{movement_id}")
def remove_movement(
    movement_id: int,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    deleted_rows = delete_movement_repository(movement_id, usuario_id)

    if deleted_rows == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento no encontrado.",
        )

    return {
        "message": "Movimiento eliminado correctamente",
        "id": movement_id,
    }

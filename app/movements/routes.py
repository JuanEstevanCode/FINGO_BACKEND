from fastapi import APIRouter, HTTPException

from app.movements.repository import (
    create_movement, 
    get_movements,
    update_movement as update_movement_repository,
    delete_movement as delete_movement_repository
)
from app.movements.schemas import movement_create

router = APIRouter(
    prefix="/movimientos",
    tags=["Movimientos"]
)

@router.post("/")
def register_movement(movement: movement_create):
    movement_id = create_movement(
        movement.tipo,
        movement.monto,
        movement.categoria,
        movement.descripcion,
        movement.fecha

    )
    return {
            "message": "Movimiento registrado correctamente",
            "id": movement_id
    }

@router.get("/")
def list_movements():

    movements = get_movements()

    return movements

@router.put("/{movement_id}")
def update_movement(movement_id: int, movement: movement_create):
    updated_movement_id = update_movement_repository(
    movement_id,
    movement.tipo,
    movement.monto,
    movement.categoria,
    movement.descripcion,
    movement.fecha
    )

    if updated_movement_id is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return {
        "message": "Movimiento actualizado correctamente",
        "id": updated_movement_id
    }

@router.delete("/{movement_id}")
def remove_movement(movement_id:int):

    deleted_rows = delete_movement_repository(movement_id)

    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    return {
        "message": "Movimiento eliminado correctamente",
        "id": movement_id
    }
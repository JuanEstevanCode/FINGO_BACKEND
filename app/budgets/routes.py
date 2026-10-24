
from psycopg.errors import ExclusionViolation
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import obtener_usuario_actual
from app.budgets.repository import (
    create_budget,
    delete_budget,
    get_budget_by_id,
    get_budgets,
    update_budget,
)
from app.budgets.schemas import BudgetCreate, BudgetResponse, BudgetUpdate


router = APIRouter(prefix="/presupuestos", tags=["Presupuestos"])


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def register_budget(
    budget: BudgetCreate,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    try:
        result = create_budget(
            usuario_id=usuario_id,
            categoria_id=budget.categoria_id,
            tipo_periodo=budget.tipo_periodo,
            fecha_inicio=budget.fecha_inicio,
            fecha_fin=budget.fecha_fin,
            monto_limite=budget.monto_limite,
        )
    except ExclusionViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un presupuesto para esa categoría con un periodo que se superpone.",
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La categoría no es válida, está inactiva o no corresponde al tipo de gasto.",
        )

    return result


@router.get("/", response_model=list[BudgetResponse])
def list_budgets(
    usuario_id: int = Depends(obtener_usuario_actual),
):
    return get_budgets(usuario_id)


@router.get("/{presupuesto_id}", response_model=BudgetResponse)
def read_budget(
    presupuesto_id: int,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    result = get_budget_by_id(presupuesto_id, usuario_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado.",
        )

    return result


@router.put("/{presupuesto_id}", response_model=BudgetResponse)
def edit_budget(
    presupuesto_id: int,
    budget: BudgetUpdate,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    try:
        result = update_budget(
            presupuesto_id=presupuesto_id,
            usuario_id=usuario_id,
            categoria_id=budget.categoria_id,
            tipo_periodo=budget.tipo_periodo,
            fecha_inicio=budget.fecha_inicio,
            fecha_fin=budget.fecha_fin,
            monto_limite=budget.monto_limite,
        )
    except ExclusionViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La actualización genera un periodo que se superpone con otro presupuesto de la misma categoría.",
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado o categoría no válida, inactiva o no accesible.",
        )

    return result


@router.delete("/{presupuesto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_budget(
    presupuesto_id: int,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    eliminado = delete_budget(presupuesto_id, usuario_id)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado.",
        )

    return None

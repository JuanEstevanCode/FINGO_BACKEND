
from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg.errors import UniqueViolation

from app.auth.dependencies import obtener_usuario_actual
from app.categories.repository import (
    get_categories,
    create_category,
    update_category,
    deactivate_category,
)
from app.categories.schemas import (
    CategoryCreate,
    CategoryUpdate,
)

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
)


@router.get("/")
def list_categories(
    tipo: str | None = Query(default=None),
    usuario_id: int = Depends(obtener_usuario_actual),
):
    """Lista las categorías predeterminadas y las personales del usuario."""

    if tipo and tipo.lower() not in ("ingreso", "gasto"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El tipo debe ser 'ingreso' o 'gasto'.",
        )

    return get_categories(
        usuario_id=usuario_id,
        tipo=tipo.lower() if tipo else None,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def register_category(
    category: CategoryCreate,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    """Crea una categoría personal."""

    try:
        categoria_id = create_category(
            nombre=category.nombre,
            tipo=category.tipo,
            usuario_id=usuario_id,
        )
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes una categoría con ese nombre y tipo.",
        )

    return {
        "message": "Categoría creada correctamente.",
        "id": categoria_id,
    }


@router.put("/{categoria_id}")
def rename_category(
    categoria_id: int,
    category: CategoryUpdate,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    """Renombra una categoría personal."""

    try:
        updated_id = update_category(
            categoria_id=categoria_id,
            nombre=category.nombre,
            usuario_id=usuario_id,
        )
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes una categoría con ese nombre y tipo.",
        )

    if updated_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría personal no encontrada o inactiva.",
        )

    return {
        "message": "Categoría actualizada correctamente.",
        "id": updated_id,
    }


@router.patch("/{categoria_id}/desactivar")
def disable_category(
    categoria_id: int,
    usuario_id: int = Depends(obtener_usuario_actual),
):
    """Desactiva una categoría personal."""

    deactivated_id = deactivate_category(
        categoria_id=categoria_id,
        usuario_id=usuario_id,
    )

    if deactivated_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría personal no encontrada o inactiva.",
        )

    return {
        "message": "Categoría desactivada correctamente.",
        "id": deactivated_id,
    }

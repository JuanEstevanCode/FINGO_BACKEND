
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal


class CategoryCreate(BaseModel):
    """Datos necesarios para crear una categoría personal."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=100)
    tipo: Literal["ingreso", "gasto"]

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        if not value:
            raise ValueError("El nombre de la categoría no puede estar vacío.")

        return value


class CategoryUpdate(BaseModel):
    """Datos para cambiar el nombre de una categoría personal."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=100)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        if not value:
            raise ValueError("El nombre de la categoría no puede estar vacío.")

        return value


class CategoryResponse(BaseModel):
    """Representación de una categoría en las respuestas de la API."""

    id: int
    nombre: str
    tipo: Literal["ingreso", "gasto"]
    es_predeterminada: bool
    activa: bool

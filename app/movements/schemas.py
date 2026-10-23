
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class movement_create(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tipo: Literal["ingreso", "gasto"]

    monto: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    categoria_id: int = Field(gt=0)

    descripcion: str | None = Field(
        default=None,
        max_length=500,
    )

    fecha: date

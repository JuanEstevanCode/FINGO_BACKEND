
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BudgetBase(BaseModel):
    categoria_id: int = Field(gt=0)
    tipo_periodo: Literal["mensual", "personalizado"]
    fecha_inicio: date
    fecha_fin: date
    monto_limite: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError(
                "La fecha de inicio no puede ser posterior a la fecha de fin."
            )

        if self.tipo_periodo == "mensual":
            ultimo_dia = monthrange(
                self.fecha_inicio.year,
                self.fecha_inicio.month,
            )[1]

            fecha_fin_esperada = self.fecha_inicio.replace(day=ultimo_dia)

            if self.fecha_inicio.day != 1:
                raise ValueError(
                    "Un presupuesto mensual debe iniciar el primer día del mes."
                )

            if self.fecha_fin != fecha_fin_esperada:
                raise ValueError(
                    "Un presupuesto mensual debe finalizar el último día del mismo mes."
                )

        return self


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    categoria_id: int
    categoria_nombre: str
    tipo_periodo: Literal["mensual", "personalizado"]
    fecha_inicio: date
    fecha_fin: date
    monto_limite: Decimal
    gasto_acumulado: Decimal
    saldo_disponible: Decimal
    porcentaje_utilizado: Decimal
    estado: Literal["normal", "proximo_limite", "excedido"]
    fecha_creacion: datetime

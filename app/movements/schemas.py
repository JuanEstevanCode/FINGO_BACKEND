from datetime import date

from pydantic import BaseModel

class movement_create(BaseModel):
    tipo: str
    monto: float
    categoria: str
    descripcion: str | None = None
    fecha: date
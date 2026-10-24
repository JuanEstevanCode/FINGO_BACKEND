
from datetime import date

from pydantic import BaseModel, EmailStr, Field


class RegistroRequest(BaseModel):
    """Datos necesarios para registrar un usuario en FINGO."""

    nombre: str = Field(
        min_length=2,
        max_length=100,
        description="Nombre del usuario"
    )

    correo: EmailStr = Field(
        description="Correo electrónico del usuario"
    )

    fecha_nacimiento: date = Field(
        description="Fecha de nacimiento del usuario"
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Contraseña del usuario"
    )


class LoginRequest(BaseModel):
    """Credenciales necesarias para iniciar sesión."""

    correo: EmailStr = Field(
        description="Correo electrónico registrado"
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Contraseña del usuario"
    )


class AuthResponse(BaseModel):
    """Estructura estándar de las respuestas de autenticación."""

    mensaje: str
    access_token: str | None = None
    token_type: str | None = None


from pydantic import BaseModel, Field


class RegistroRequest(BaseModel):
    """Define y valida los datos necesarios para registrar un usuario."""

    usuario: str = Field(
        min_length=3,
        max_length=50,
        description="Nombre de usuario para acceder a FINGO"
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Contraseña del usuario"
    )


class LoginRequest(BaseModel):
    """Define las credenciales necesarias para iniciar sesión."""

    usuario: str = Field(
        min_length=3,
        max_length=50,
        description="Nombre de usuario registrado"
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Contraseña del usuario"
    )


class AuthResponse(BaseModel):
    """Estructura estándar de las respuestas de autenticación."""

    mensaje: str

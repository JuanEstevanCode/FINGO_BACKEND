
from fastapi import APIRouter, HTTPException, status
from psycopg import Error as PsycopgError

from app.auth.schemas import (
    RegistroRequest,
    LoginRequest,
    AuthResponse
)
from app.auth.service import registrar_usuario, autenticar_usuario


# Agrupa los endpoints relacionados con la autenticación.
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
def registro(datos: RegistroRequest):
    """Registra un nuevo usuario en FINGO."""

    try:
        # Intenta registrar el usuario y su contraseña protegida.
        registrado = registrar_usuario(datos.usuario, datos.password)

        if not registrado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está registrado."
            )

        return AuthResponse(
            mensaje="Usuario registrado satisfactoriamente."
        )

    except HTTPException:
        # Conserva los errores HTTP definidos para el endpoint.
        raise

    except PsycopgError:
        # Evita exponer detalles internos de la base de datos.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible registrar el usuario."
        )


@router.post(
    "/login",
    response_model=AuthResponse
)
def login(datos: LoginRequest):
    """Verifica las credenciales de un usuario."""

    try:
        # Comprueba el nombre de usuario y la contraseña.
        autenticado = autenticar_usuario(
            datos.usuario,
            datos.password
        )

        if not autenticado:
            # Utiliza el mismo mensaje para ambos tipos de credenciales
            # incorrectas y evitar revelar si un usuario existe.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error en la autenticación."
            )

        return AuthResponse(
            mensaje="Autenticación satisfactoria."
        )

    except HTTPException:
        raise

    except PsycopgError:
        # Devuelve un error controlado si falla PostgreSQL.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible procesar la autenticación."
        )

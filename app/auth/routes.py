
from fastapi import APIRouter, HTTPException, status
from psycopg import Error as PsycopgError

from app.auth.schemas import (
    RegistroRequest,
    LoginRequest,
    AuthResponse,
)
from app.auth.service import registrar_usuario, autenticar_usuario
from app.auth.security import crear_access_token


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def registro(datos: RegistroRequest):
    """Registra un nuevo usuario en FINGO."""

    try:
        registrado = registrar_usuario(
            nombre=datos.nombre,
            correo=datos.correo,
            fecha_nacimiento=datos.fecha_nacimiento,
            password=datos.password,
        )

        if not registrado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado.",
            )

        return AuthResponse(
            mensaje="Usuario registrado satisfactoriamente."
        )

    except HTTPException:
        raise

    except PsycopgError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible registrar el usuario.",
        )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(datos: LoginRequest):
    """Verifica las credenciales y genera un token de acceso."""

    try:
        usuario_id = autenticar_usuario(
            datos.correo,
            datos.password,
        )

        if usuario_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo electrónico o contraseña incorrectos.",
            )

        access_token = crear_access_token(usuario_id)

        return AuthResponse(
            mensaje="Autenticación satisfactoria.",
            access_token=access_token,
            token_type="bearer",
        )

    except HTTPException:
        raise

    except PsycopgError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible procesar la autenticación.",
        )


import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "La variable JWT_SECRET_KEY no está configurada en el archivo .env"
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def crear_access_token(usuario_id: int) -> str:
    """Genera un token JWT para el usuario autenticado."""

    ahora = datetime.now(timezone.utc)

    payload = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def verificar_access_token(token: str) -> int | None:
    """Verifica el token y devuelve el ID del usuario si es válido."""

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        usuario_id = payload.get("sub")

        if not isinstance(usuario_id, str) or not usuario_id.isdigit():
            return None

        return int(usuario_id)

    except jwt.InvalidTokenError:
        return None

"""Dependencia FastAPI que exige una sesión válida para usar la API."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from src.auth.errors import AuthError
from src.auth.tokens import InvalidTokenError, decode_access_token
from src.persistence import repository as persistence_repository
from src.persistence.db import session_scope


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str


def require_current_user(request: Request) -> AuthenticatedUser:
    """Extrae y valida el `Authorization: Bearer <token>`; exige sesión activa."""

    header = request.headers.get("authorization", "")
    if not header.startswith("Bearer "):
        raise AuthError("UNAUTHORIZED", "Inicia sesión para usar esta función.", 401)
    token = header.removeprefix("Bearer ").strip()
    if not token:
        raise AuthError("UNAUTHORIZED", "Inicia sesión para usar esta función.", 401)

    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise AuthError("UNAUTHORIZED", "La sesión no es válida o expiró. Vuelve a iniciar sesión.", 401) from None

    try:
        with session_scope() as session:
            user = persistence_repository.get_user_by_id(session, user_id=payload["sub"])
            if user is None:
                raise AuthError("UNAUTHORIZED", "El usuario ya no existe.", 401)
            return AuthenticatedUser(id=user.id, email=user.email)
    except AuthError:
        raise
    except Exception as exc:
        raise AuthError(
            "AUTH_UNAVAILABLE", "No se pudo verificar la sesión (base de datos no disponible).", 503
        ) from exc

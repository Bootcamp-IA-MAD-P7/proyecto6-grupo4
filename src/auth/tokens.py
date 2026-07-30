"""Emisión y verificación de tokens de sesión (JWT).

Sin `AUTH_SECRET_KEY` (por ejemplo en tests o en un entorno local sin
configurar), se usa una clave aleatoria generada al arrancar el proceso:
los tokens emitidos dejan de ser válidos si el proceso se reinicia. En
producción (Render) `AUTH_SECRET_KEY` debe fijarse como variable de
entorno estable para que las sesiones sobrevivan a un redeploy.
"""

from __future__ import annotations

import logging
import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

logger = logging.getLogger("laliga.auth")

ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = timedelta(days=7)


def _get_secret_key() -> str:
    key = os.environ.get("AUTH_SECRET_KEY")
    if key:
        return key
    global _fallback_key
    if _fallback_key is None:
        logger.warning(
            "AUTH_SECRET_KEY no está configurada; usando una clave aleatoria "
            "solo para este proceso. Las sesiones no sobrevivirán a un reinicio."
        )
        _fallback_key = secrets.token_hex(32)
    return _fallback_key


_fallback_key: str | None = None


class InvalidTokenError(Exception):
    pass


def create_access_token(*, user_id: str, email: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, _get_secret_key(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

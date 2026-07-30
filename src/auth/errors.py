"""Error de autenticación con el mismo contrato que InferenceError."""

from __future__ import annotations


class AuthError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code, self.message, self.status_code = code, message, status_code
        super().__init__(message)

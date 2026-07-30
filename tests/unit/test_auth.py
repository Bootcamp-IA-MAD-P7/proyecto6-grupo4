from __future__ import annotations

import pytest

from src.auth.security import hash_password, verify_password
from src.auth.tokens import InvalidTokenError, create_access_token, decode_access_token


def test_hash_password_never_stores_plaintext() -> None:
    password = "mySecret123"
    hashed = hash_password(password)
    assert hashed != password
    assert password not in hashed


def test_verify_password_accepts_correct_and_rejects_wrong() -> None:
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_same_password_produces_different_hashes_due_to_salt() -> None:
    # bcrypt genera un salt aleatorio por llamada: dos hashes del mismo
    # password nunca deben coincidir en texto, aunque ambos verifiquen ok.
    first = hash_password("same-password")
    second = hash_password("same-password")
    assert first != second
    assert verify_password("same-password", first)
    assert verify_password("same-password", second)


def test_verify_password_rejects_malformed_hash_instead_of_raising() -> None:
    assert verify_password("anything", "not-a-real-bcrypt-hash") is False


def test_create_and_decode_access_token_round_trips() -> None:
    token = create_access_token(user_id="user-123", email="a@b.com")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["email"] == "a@b.com"
    assert "exp" in payload


def test_decode_access_token_rejects_garbage() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("this.is.not-a-valid-jwt")


def test_decode_access_token_rejects_expired_token(monkeypatch) -> None:
    import src.auth.tokens as tokens_module

    monkeypatch.setattr(tokens_module, "ACCESS_TOKEN_TTL", __import__("datetime").timedelta(seconds=-1))
    token = create_access_token(user_id="user-123", email="a@b.com")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_a_token_signed_with_a_different_key(monkeypatch) -> None:
    import src.auth.tokens as tokens_module

    monkeypatch.setenv("AUTH_SECRET_KEY", "key-one")
    token = create_access_token(user_id="user-123", email="a@b.com")

    monkeypatch.setenv("AUTH_SECRET_KEY", "key-two")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)

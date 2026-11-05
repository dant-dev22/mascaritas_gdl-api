"""Pruebas del freno de fuerza bruta del login."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.config import LOGIN_MAX_ATTEMPTS
from app.rate_limit import LoginRateLimiter, login_limiter

KEY = "persona@test.local"


def test_no_bloquea_sin_intentos_previos() -> None:
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=60)

    limiter.check(KEY)  # no debe lanzar


def test_bloquea_al_agotar_los_intentos() -> None:
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=60)
    for _ in range(3):
        limiter.register_failure(KEY)

    with pytest.raises(HTTPException) as excinfo:
        limiter.check(KEY)

    assert excinfo.value.status_code == 429
    assert excinfo.value.headers is not None
    assert excinfo.value.headers["Retry-After"]


def test_reset_limpia_los_fallos() -> None:
    limiter = LoginRateLimiter(max_attempts=2, window_seconds=60)
    limiter.register_failure(KEY)
    limiter.register_failure(KEY)

    limiter.reset(KEY)

    limiter.check(KEY)  # no debe lanzar


def test_los_fallos_expiran_con_la_ventana() -> None:
    limiter = LoginRateLimiter(max_attempts=1, window_seconds=0)
    limiter.register_failure(KEY)

    limiter.check(KEY)  # la ventana ya venció, no debe lanzar


def test_login_responde_429_tras_varios_fallos(client: TestClient) -> None:
    email = "brut0@test.local"
    payload = {"email": email, "password": "incorrecta"}
    login_limiter.reset(email)

    for _ in range(LOGIN_MAX_ATTEMPTS):
        assert client.post("/api/auth/login", json=payload).status_code == 401

    bloqueado = client.post("/api/auth/login", json=payload)
    assert bloqueado.status_code == 429

    login_limiter.reset(email)

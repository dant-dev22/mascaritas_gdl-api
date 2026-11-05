"""Pruebas de autenticación del panel admin."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password


def test_login_ok(client: TestClient, admin_user: User, admin_credentials: dict[str, str]) -> None:
    response = client.post("/api/auth/login", json=admin_credentials)

    assert response.status_code == 200
    body = response.json()
    assert body["tokenType"] == "bearer"
    assert body["accessToken"]
    assert body["user"]["email"] == admin_credentials["email"]
    assert body["user"]["role"] == "admin"


def test_login_normaliza_email(client: TestClient, admin_user: User, admin_credentials: dict[str, str]) -> None:
    response = client.post(
        "/api/auth/login",
        json={**admin_credentials, "email": admin_credentials["email"].upper()},
    )
    assert response.status_code == 200


def test_login_contrasena_incorrecta(client: TestClient, admin_user: User, admin_credentials: dict[str, str]) -> None:
    response = client.post("/api/auth/login", json={**admin_credentials, "password": "incorrecta"})
    assert response.status_code == 401


def test_login_email_desconocido(client: TestClient, admin_credentials: dict[str, str]) -> None:
    response = client.post("/api/auth/login", json={**admin_credentials, "email": "nadie@test.local"})
    assert response.status_code == 401


def test_login_usuario_inactivo(
    client: TestClient,
    db_session: Session,
    admin_credentials: dict[str, str],
) -> None:
    db_session.add(
        User(
            email="inactivo@test.local",
            name="Inactivo",
            password_hash=hash_password(admin_credentials["password"]),
            role="admin",
            is_active=False,
        )
    )
    db_session.commit()

    response = client.post("/api/auth/login", json={**admin_credentials, "email": "inactivo@test.local"})
    assert response.status_code == 401


def test_me_sin_token(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_token_invalido(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer token-falso"})
    assert response.status_code == 401


def test_me_con_token_valido(
    client: TestClient,
    auth_headers: dict[str, str],
    admin_credentials: dict[str, str],
) -> None:
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == admin_credentials["email"]

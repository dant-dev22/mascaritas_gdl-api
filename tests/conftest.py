"""Configuración de las pruebas.

Las pruebas corren sobre SQLite en memoria en lugar de MySQL: se sobreescribe la
dependencia `get_db` y no se ejecuta el lifespan de la app, así que no hay seed
ni conexión a la base real.
"""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, User
from app.security import hash_password

ADMIN_EMAIL = "admin@test.local"
ADMIN_PASSWORD = "contrasena-de-prueba"


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Sesión sobre una base SQLite en memoria que se descarta al terminar."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # Sin `with TestClient(...)`: así no se dispara el lifespan (seed / MySQL).
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session: Session) -> User:
    user = User(
        email=ADMIN_EMAIL,
        name="Admin de prueba",
        password_hash=hash_password(ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_credentials() -> dict[str, str]:
    return {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}


@pytest.fixture()
def auth_headers(client: TestClient, admin_user: User, admin_credentials: dict[str, str]) -> dict[str, str]:
    response = client.post("/api/auth/login", json=admin_credentials)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


@pytest.fixture()
def make_product() -> Callable[..., dict]:
    """Fábrica de payloads válidos para crear productos."""

    def _make(**overrides) -> dict:
        payload = {
            "slug": "mascara-prueba",
            "sku": "TEST-001",
            "title": "Máscara de prueba",
            "subtitle": "Subtítulo de prueba",
            "description": "Descripción corta de prueba.",
            "longDescription": "Descripción larga de prueba para el CRUD.",
            "priceMXN": 1200,
            "accentColor": "blue",
            "categoryId": "semi-pro",
            "sizeId": "adulto",
            "maskStyle": "diablo",
            "finish": "Acabado mate",
            "material": "Cuero sintético",
            "lining": "Forro de algodón",
            "tags": ["prueba"],
        }
        payload.update(overrides)
        return payload

    return _make

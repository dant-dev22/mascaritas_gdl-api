"""Configuración leída desde variables de entorno (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_DATABASE_URL = (
    "mysql+pymysql://USUARIO:CONTRASENA@127.0.0.1:3309/mascaritas?charset=utf8mb4"
)

DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

# Entorno: `development` (por defecto) o `production`. Solo en producción se
# activan las guardas de seguridad (clave de firma, docs deshabilitadas...).
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").strip().lower()
IS_PRODUCTION: bool = ENVIRONMENT == "production"

# Orígenes permitidos por CORS, separados por comas.
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

# --- Panel admin ---
# Clave para firmar los tokens de sesión del admin. En producción SIEMPRE
# debe venir del entorno; el valor por defecto solo sirve para desarrollo local.
DEFAULT_JWT_SECRET = "cambia-este-secreto-en-produccion"
JWT_SECRET: str = os.getenv("JWT_SECRET", DEFAULT_JWT_SECRET)
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "480"))

# Freno contra la fuerza bruta sobre el login: intentos fallidos por cuenta
# dentro de la ventana antes de responder 429.
LOGIN_MAX_ATTEMPTS: int = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_WINDOW_SECONDS: int = int(os.getenv("LOGIN_WINDOW_SECONDS", "300"))

# Credenciales del primer admin que crea `python -m app.create_admin`.
ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
ADMIN_NAME: str = os.getenv("ADMIN_NAME", "Administrador")

# Longitud mínima de la clave de firma cuando corre en producción.
MIN_JWT_SECRET_LENGTH = 32


def validate_security_config() -> None:
    """Aborta el arranque si en producción la clave de firma no es segura.

    Un `JWT_SECRET` conocido permite falsificar tokens de admin, así que es
    preferible no arrancar antes que quedar abierto.
    """
    if not IS_PRODUCTION:
        return
    if JWT_SECRET == DEFAULT_JWT_SECRET or len(JWT_SECRET) < MIN_JWT_SECRET_LENGTH:
        raise RuntimeError(
            "Configuración insegura: con ENVIRONMENT=production, JWT_SECRET debe ser "
            f"una clave aleatoria de al menos {MIN_JWT_SECRET_LENGTH} caracteres."
        )

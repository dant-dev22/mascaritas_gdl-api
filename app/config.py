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

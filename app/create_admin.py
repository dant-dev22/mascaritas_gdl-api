"""Crea (o actualiza) el usuario administrador del panel.

Las credenciales se leen del entorno (`ADMIN_EMAIL`, `ADMIN_PASSWORD`,
`ADMIN_NAME`) o de los argumentos. Nunca se guardan en el código.

Uso:
    python -m app.create_admin                          # usa el .env
    python -m app.create_admin correo@x.com secreto     # o por argumentos
"""

import sys

from sqlalchemy import select

from .config import ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD
from .database import SessionLocal, engine
from .models import Base, User
from .security import hash_password

MIN_PASSWORD_LENGTH = 8


def upsert_admin(email: str, password: str, name: str) -> str:
    """Crea el admin o, si ya existe ese email, actualiza contraseña y nombre."""
    email = email.strip().lower()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            db.add(
                User(
                    email=email,
                    name=name,
                    password_hash=hash_password(password),
                    role="admin",
                    is_active=True,
                )
            )
            action = "creado"
        else:
            user.password_hash = hash_password(password)
            user.name = name
            user.role = "admin"
            user.is_active = True
            action = "actualizado"
        db.commit()
    return action


def main() -> None:
    email = sys.argv[1] if len(sys.argv) > 1 else ADMIN_EMAIL
    password = sys.argv[2] if len(sys.argv) > 2 else ADMIN_PASSWORD

    if not email or not password:
        raise SystemExit(
            "Faltan credenciales. Define ADMIN_EMAIL y ADMIN_PASSWORD en el .env "
            "o pásalos como argumentos."
        )
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")

    action = upsert_admin(email, password, ADMIN_NAME)
    print(f"Admin {action}: {email}")


if __name__ == "__main__":
    main()

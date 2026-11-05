"""Dependencias de autenticación del panel admin."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión no válida o expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resuelve el usuario a partir del token Bearer. 401 si no es válido."""
    if credentials is None or not credentials.credentials:
        raise _unauthorized()

    subject = decode_access_token(credentials.credentials)
    if subject is None:
        raise _unauthorized()

    try:
        user_id = int(subject)
    except ValueError:
        raise _unauthorized() from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _unauthorized()

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Exige rol admin. 403 si el usuario no lo tiene."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes",
        )
    return user

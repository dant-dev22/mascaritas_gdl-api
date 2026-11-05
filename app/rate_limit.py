"""Frenos contra la fuerza bruta en memoria.

Deliberadamente simples: con una sola instancia del backend el límite es útil
y no hace falta infraestructura extra. Si algún día corren varias réplicas,
haría falta un almacén compartido (por ejemplo Redis).
"""

import time
from threading import Lock

from fastapi import HTTPException, status

from .config import (
    LOGIN_MAX_ATTEMPTS,
    LOGIN_WINDOW_SECONDS,
    ORDER_LOOKUP_MAX_ATTEMPTS,
    ORDER_LOOKUP_WINDOW_SECONDS,
)


class AttemptRateLimiter:
    """Cuenta intentos fallidos por clave dentro de una ventana móvil.

    En el login se usa una clave por cuenta (el correo normalizado) en lugar de
    la IP: el panel se sirve detrás del proxy de Next.js, así que todas las
    peticiones llegan desde la misma IP y un límite por IP bloquearía a todos.
    En el rastreo público la clave es el código de pedido consultado.
    """

    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._failures: dict[str, list[float]] = {}
        self._lock = Lock()

    def _prune(self, key: str, now: float) -> list[float]:
        """Descarta los intentos fuera de la ventana y devuelve los vigentes."""
        cutoff = now - self._window_seconds
        recent = [stamp for stamp in self._failures.get(key, ()) if stamp > cutoff]
        if recent:
            self._failures[key] = recent
        else:
            self._failures.pop(key, None)
        return recent

    def check(self, key: str) -> None:
        """Responde 429 si la clave ya agotó los intentos de la ventana."""
        now = time.monotonic()
        with self._lock:
            recent = self._prune(key, now)
            if len(recent) >= self._max_attempts:
                retry_after = int(self._window_seconds - (now - recent[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiados intentos fallidos. Intenta de nuevo más tarde.",
                    headers={"Retry-After": str(max(retry_after, 1))},
                )

    def register_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            recent = self._prune(key, now)
            recent.append(now)
            self._failures[key] = recent

    def reset(self, key: str) -> None:
        """Limpia el historial tras un inicio de sesión correcto."""
        with self._lock:
            self._failures.pop(key, None)


login_limiter = AttemptRateLimiter(
    max_attempts=LOGIN_MAX_ATTEMPTS,
    window_seconds=LOGIN_WINDOW_SECONDS,
)

order_lookup_limiter = AttemptRateLimiter(
    max_attempts=ORDER_LOOKUP_MAX_ATTEMPTS,
    window_seconds=ORDER_LOOKUP_WINDOW_SECONDS,
)

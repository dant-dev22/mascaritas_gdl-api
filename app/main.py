"""Aplicación FastAPI: Mascaritas GDL API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS, IS_PRODUCTION, validate_security_config
from .database import engine
from .models import Base
from .routers import admin_productos, auth, productos

# Falla en el arranque si la configuración de seguridad no es apta para producción.
validate_security_config()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        Base.metadata.create_all(engine)
        from .seed import count_products, seed

        if count_products() == 0:
            seed()
    except Exception as exc:  # noqa: BLE001 - aviso no fatal en arranque local
        print(f"Aviso: no se pudo preparar la base al arrancar: {exc}")
    yield


app = FastAPI(
    title="Mascaritas GDL API",
    version="0.1.0",
    description="API del catálogo de máscaras de lucha libre de Mascaritas GDL.",
    lifespan=lifespan,
    # La documentación interactiva queda expuesta solo fuera de producción.
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admin_productos.router, prefix="/api")
app.include_router(productos.router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

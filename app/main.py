"""Aplicación FastAPI: Mascaritas GDL API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base
from .routers import productos


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
    description="API del catálogo de máscaras de lucha libre hechas a mano en Guadalajara.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(productos.router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

"""Crea las tablas y siembra el catálogo (idempotente)."""

import sys
import time

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from .catalog_engine import build_search_blob
from .database import SessionLocal, engine
from .models import Base, Product
from .seed_data import PRODUCTS
from .seed_data_en import PRODUCTS_EN

# Campos de texto que tienen versión inglesa (`*_en`) en el modelo.
# El nombre comercial (`title`) no se traduce.
_TRANSLATABLE_KEYS = (
    "subtitle",
    "description",
    "long_description",
    "badge_label",
    "finish",
    "material",
    "lining",
)


def wait_for_db(attempts: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            return
        except OperationalError:
            print(f"Esperando a MySQL... ({attempt}/{attempts})")
            time.sleep(delay)
    raise SystemExit("No se pudo conectar a MySQL. ¿Está arriba el contenedor?")


def _apply_translation(row: dict, translation: dict[str, str] | None) -> bool:
    """Vuelca la traducción en las claves `*_en` del row. Devuelve si la hubo."""
    if not translation:
        return False
    for key in _TRANSLATABLE_KEYS:
        value = translation.get(key)
        row[f"{key}_en"] = value if value else None
    return True


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for position, data in enumerate(PRODUCTS):
        row = dict(data)
        row["position"] = position
        row["search_blob"] = build_search_blob(
            title=row["title"],
            subtitle=row["subtitle"],
            description=row["description"],
            sku=row["sku"],
            mask_style=row["mask_style"],
            accent_color=row["accent_color"],
            category_id=row["category_id"],
            size_id=row["size_id"],
            tags=row["tags"],
        )

        has_translation = _apply_translation(row, PRODUCTS_EN.get(row["slug"]))
        row["search_blob_en"] = (
            build_search_blob(
                title=row["title"],
                subtitle=row["subtitle_en"] or row["subtitle"],
                description=row["description_en"] or row["description"],
                sku=row["sku"],
                mask_style=row["mask_style"],
                accent_color=row["accent_color"],
                category_id=row["category_id"],
                size_id=row["size_id"],
                tags=row["tags"],
                lang="en",
            )
            if has_translation
            else None
        )
        rows.append(row)
    return rows


def count_products() -> int:
    with SessionLocal() as db:
        return int(db.scalar(select(func.count()).select_from(Product)) or 0)


def seed(reset: bool = False) -> None:
    wait_for_db()
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        if reset:
            db.query(Product).delete()
            db.commit()

        existing = set(db.scalars(select(Product.id)).all())
        for row in build_rows():
            if row["id"] in existing:
                db.merge(Product(**row))
            else:
                db.add(Product(**row))
        db.commit()

    print(f"Seed listo: {count_products()} productos en la base.")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)

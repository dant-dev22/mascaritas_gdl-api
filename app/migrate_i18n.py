"""Migración idempotente de internacionalización (es/en) del catálogo.

Añade a `products` las columnas `*_en` que falten y rellena las traducciones a
partir de `PRODUCTS_EN`. MySQL 8 no soporta `ADD COLUMN IF NOT EXISTS`, por eso
se consulta `information_schema` antes de alterar la tabla.

También elimina la columna obsoleta `title_en`: el nombre comercial no se
traduce.

Ejecutar dos veces no falla ni duplica nada.

Uso:
    python -m app.migrate_i18n
"""

from sqlalchemy import select

from .catalog_engine import build_search_blob
from .database import SessionLocal, engine
from .models import Product
from .seed import _TRANSLATABLE_KEYS
from .seed_data_en import PRODUCTS_EN

# Nombre de columna -> tipo SQL, en el orden de creación.
# El nombre comercial (`title`) no se traduce: no tiene columna inglesa.
EN_COLUMNS: dict[str, str] = {
    "subtitle_en": "VARCHAR(128) NULL",
    "description_en": "TEXT NULL",
    "long_description_en": "TEXT NULL",
    "badge_label_en": "VARCHAR(48) NULL",
    "finish_en": "VARCHAR(96) NULL",
    "material_en": "VARCHAR(96) NULL",
    "lining_en": "VARCHAR(96) NULL",
    "search_blob_en": "TEXT NULL",
}

# Columnas de versiones anteriores que ya no se usan.
LEGACY_COLUMNS: tuple[str, ...] = ("title_en",)


def existing_columns() -> set[str]:
    """Columnas actuales de `products` en la base conectada."""
    with engine.connect() as connection:
        rows = connection.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'products'"
        )
        return {row[0] for row in rows}


def add_missing_columns() -> list[str]:
    """Añade solo las columnas `*_en` que falten. Devuelve las añadidas."""
    present = existing_columns()
    added: list[str] = []
    with engine.begin() as connection:
        for name, sql_type in EN_COLUMNS.items():
            if name in present:
                continue
            connection.exec_driver_sql(f"ALTER TABLE products ADD COLUMN {name} {sql_type}")
            added.append(name)
    return added


def drop_legacy_columns() -> list[str]:
    """Elimina las columnas obsoletas que sigan presentes. Devuelve las quitadas."""
    present = existing_columns()
    dropped: list[str] = []
    with engine.begin() as connection:
        for name in LEGACY_COLUMNS:
            if name not in present:
                continue
            connection.exec_driver_sql(f"ALTER TABLE products DROP COLUMN {name}")
            dropped.append(name)
    return dropped


def apply_translations() -> int:
    """Rellena los campos ingleses y recalcula `search_blob_en`. Idempotente."""
    translated = 0
    with SessionLocal() as db:
        for product in db.scalars(select(Product)).all():
            translation = PRODUCTS_EN.get(product.slug)
            if not translation:
                continue
            for key in _TRANSLATABLE_KEYS:
                value = translation.get(key)
                setattr(product, f"{key}_en", value if value else None)
            product.search_blob_en = build_search_blob(
                title=product.title,
                subtitle=product.subtitle_en or product.subtitle,
                description=product.description_en or product.description,
                sku=product.sku,
                mask_style=product.mask_style,
                accent_color=product.accent_color,
                category_id=product.category_id,
                size_id=product.size_id,
                tags=product.tags,
                lang="en",
            )
            translated += 1
        db.commit()
    return translated


def main() -> None:
    dropped = drop_legacy_columns()
    if dropped:
        print(f"Columnas obsoletas eliminadas ({len(dropped)}): {', '.join(dropped)}")
    else:
        print("Columnas obsoletas eliminadas (0): no había ninguna")

    added = add_missing_columns()
    if added:
        print(f"Columnas añadidas ({len(added)}): {', '.join(added)}")
    else:
        print("Columnas añadidas (0): ya existían todas")

    translated = apply_translations()
    print(f"Productos traducidos: {translated}")
    print("Migración i18n completada (idempotente).")


if __name__ == "__main__":
    main()

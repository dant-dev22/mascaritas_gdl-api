"""Alta y baja de productos de prueba (QA) para validar el catálogo.

Todos los registros llevan el prefijo `test-` en el id y el slug, y el título
empieza con `[TEST]`, para poder borrarlos sin tocar las piezas reales.

Uso (desde la raíz del backend, con el venv activado):
    python -m app.seed_test          # crea/actualiza los 6 productos de prueba
    python -m app.seed_test --clean  # elimina solo los productos de prueba

Los productos se colocan al final del orden "destacado" (position >= 1000), así
que no alteran el orden del catálogo real. Para encontrarlos en /catalogo busca
`test` o navega a la última página.
"""

import sys
from datetime import date

from sqlalchemy import delete, func, select

from .catalog_engine import build_search_blob
from .database import SessionLocal, engine
from .models import Base, Product
from .seed import wait_for_db

TEST_ID_PREFIX = "test-"
# Por encima de las posiciones del catálogo real (0..17) para no reordenarlo.
TEST_POSITION_BASE = 1000

TEST_PRODUCTS: list[dict] = [
    {
        "id": "test-001",
        "slug": "test-tiburon-qa-dorado",
        "sku": "MG-TEST-001",
        "title": "[TEST] Sargento Tiburón QA",
        "subtitle": "Dorado · Clásica",
        "description": "Producto de prueba. Máscara dorada para validar filtros de color y categoría.",
        "long_description": "Registro de QA. No es una pieza real del taller: se usa para verificar el catálogo, la ficha de producto y el carrito en producción.",
        "price_mxn": 899,
        "old_price_mxn": 999,
        "badge_variant": "last-units",
        "badge_label": "Últimas piezas",
        "accent_color": "gold",
        "category_id": "clasicas",
        "size_id": "adulto",
        "mask_style": "tiburon",
        "finish": "Lámina dorada satinada",
        "material": "Cuero sintético de alta densidad",
        "lining": "Doble forro de algodón transpirable",
        "in_stock": True,
        "stock_count": 5,
        "rating": 4.5,
        "reviews_count": 12,
        "tags": ["test", "qa", "tiburon", "dorado", "clasica"],
        "created_at": date(2026, 11, 1),
    },
    {
        "id": "test-002",
        "slug": "test-diablo-qa-verde",
        "sku": "MG-TEST-002",
        "title": "[TEST] Diablo QA",
        "subtitle": "Verde · Semi-Pro",
        "description": "Producto de prueba. Máscara verde para validar la categoría Semi-Pro y el badge.",
        "long_description": "Registro de QA. Sirve para probar el orden por precio, la faceta Semi-Pro y el badge correspondiente en el listado.",
        "price_mxn": 1199,
        "old_price_mxn": None,
        "badge_variant": "semi-pro",
        "badge_label": "Semi-Pro",
        "accent_color": "green",
        "category_id": "semi-pro",
        "size_id": "adulto",
        "mask_style": "diablo",
        "finish": "Mate antirreflejante",
        "material": "Malla deportiva reforzada",
        "lining": "Doble forro acolchado de 4 mm",
        "in_stock": True,
        "stock_count": 20,
        "rating": 4.7,
        "reviews_count": 33,
        "tags": ["test", "qa", "diablo", "verde", "entrenamiento"],
        "created_at": date(2026, 10, 20),
    },
    {
        "id": "test-003",
        "slug": "test-galactico-qa-rojo",
        "sku": "MG-TEST-003",
        "title": "[TEST] El Galáctico QA",
        "subtitle": "Rojo · Colección",
        "description": "Producto de prueba. Máscara roja para validar la categoría Colección y el badge Nueva.",
        "long_description": "Registro de QA. Comprueba la faceta de precio de $1,300 o más, la talla Adulto XL y el badge de novedad.",
        "price_mxn": 1499,
        "old_price_mxn": 1799,
        "badge_variant": "new",
        "badge_label": "Nueva",
        "accent_color": "red",
        "category_id": "coleccion",
        "size_id": "adulto-xl",
        "mask_style": "galactico",
        "finish": "Satinado premium con microtextura",
        "material": "Cuero italiano de grano fino",
        "lining": "Forro de seda sintética",
        "in_stock": True,
        "stock_count": 3,
        "rating": 4.9,
        "reviews_count": 8,
        "tags": ["test", "qa", "galactico", "rojo", "coleccion"],
        "created_at": date(2026, 11, 2),
    },
    {
        "id": "test-004",
        "slug": "test-aguila-qa-plata-infantil",
        "sku": "MG-TEST-004",
        "title": "[TEST] Águila QA",
        "subtitle": "Plata · Infantil",
        "description": "Producto de prueba. Máscara plateada para validar la talla Infantil y el precio más bajo.",
        "long_description": "Registro de QA. Verifica la faceta Infantil, el color Plata y la faceta de precio de menos de $1,000.",
        "price_mxn": 799,
        "old_price_mxn": None,
        "badge_variant": None,
        "badge_label": None,
        "accent_color": "silver",
        "category_id": "clasicas",
        "size_id": "infantil",
        "mask_style": "aguila",
        "finish": "Plata pulida brillante",
        "material": "Cuero sintético de alta densidad",
        "lining": "Doble forro de algodón transpirable",
        "in_stock": True,
        "stock_count": 8,
        "rating": 4.3,
        "reviews_count": 5,
        "tags": ["test", "qa", "aguila", "plata", "infantil"],
        "created_at": date(2026, 9, 15),
    },
    {
        "id": "test-005",
        "slug": "test-serpiente-qa-azul-agotado",
        "sku": "MG-TEST-005",
        "title": "[TEST] Serpiente QA (agotado)",
        "subtitle": "Azul · Personalizada",
        "description": "Producto de prueba sin existencias para validar el filtro «solo disponibles».",
        "long_description": "Registro de QA con stock en cero. Sirve para comprobar que el filtro de disponibilidad lo oculta y que el detalle muestra el estado agotado.",
        "price_mxn": 1299,
        "old_price_mxn": None,
        "badge_variant": None,
        "badge_label": None,
        "accent_color": "blue",
        "category_id": "personalizadas",
        "size_id": "adulto",
        "mask_style": "serpiente",
        "finish": "Brillo espejo",
        "material": "Cuero sintético de alta densidad",
        "lining": "Doble forro de algodón transpirable",
        "in_stock": False,
        "stock_count": 0,
        "rating": 4.1,
        "reviews_count": 3,
        "tags": ["test", "qa", "serpiente", "azul", "agotado"],
        "created_at": date(2026, 8, 30),
    },
    {
        "id": "test-006",
        "slug": "test-pantera-qa-morado",
        "sku": "MG-TEST-006",
        "title": "[TEST] Pantera QA",
        "subtitle": "Morado · Personalizada",
        "description": "Producto de prueba. Máscara morada para validar la categoría Personalizadas.",
        "long_description": "Registro de QA. Completa las 6 paletas de color y las 3 tallas para revisar el comportamiento de las facetas.",
        "price_mxn": 1050,
        "old_price_mxn": 1250,
        "badge_variant": "new",
        "badge_label": "Nueva",
        "accent_color": "purple",
        "category_id": "personalizadas",
        "size_id": "infantil",
        "mask_style": "pantera",
        "finish": "Acabado terciopelo",
        "material": "Cuero sintético de alta densidad",
        "lining": "Doble forro de algodón transpirable",
        "in_stock": True,
        "stock_count": 6,
        "rating": 4.6,
        "reviews_count": 9,
        "tags": ["test", "qa", "pantera", "morado", "personalizada"],
        "created_at": date(2026, 11, 3),
    },
]


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for offset, data in enumerate(TEST_PRODUCTS):
        row = dict(data)
        row["position"] = TEST_POSITION_BASE + offset
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
        rows.append(row)
    return rows


def count_test_products() -> int:
    with SessionLocal() as db:
        total = db.scalar(
            select(func.count()).select_from(Product).where(Product.id.like(f"{TEST_ID_PREFIX}%"))
        )
        return int(total or 0)


def seed_test() -> None:
    wait_for_db()
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        existing = set(
            db.scalars(select(Product.id).where(Product.id.like(f"{TEST_ID_PREFIX}%"))).all()
        )
        for row in build_rows():
            if row["id"] in existing:
                db.merge(Product(**row))
            else:
                db.add(Product(**row))
        db.commit()

    print(f"Productos de prueba activos: {count_test_products()}")


def clean_test() -> None:
    wait_for_db()
    with SessionLocal() as db:
        result = db.execute(delete(Product).where(Product.id.like(f"{TEST_ID_PREFIX}%")))
        db.commit()

    print(f"Productos de prueba eliminados: {result.rowcount}")


def main() -> None:
    if "--clean" in sys.argv:
        clean_test()
    else:
        seed_test()


if __name__ == "__main__":
    main()

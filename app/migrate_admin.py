"""Migración idempotente del panel admin.

1. Crea la tabla `users` si no existe (la usa el login del panel).
2. Añade un índice único a `products.sku`: el SKU ahora se captura a mano, así
   que conviene impedir duplicados a nivel de base.

MySQL 8 no soporta `CREATE INDEX IF NOT EXISTS`, por eso se consulta
`information_schema` antes de alterar. Ejecutar dos veces no falla.

Uso:
    python -m app.migrate_admin
"""

from sqlalchemy import inspect

from .database import engine
from .models import User

SKU_INDEX_NAME = "uq_products_sku"


def create_users_table() -> bool:
    """Crea `users` si falta. Devuelve si la creó."""
    if inspect(engine).has_table(User.__tablename__):
        return False
    User.__table__.create(engine)
    return True


def sku_unique_index_exists() -> bool:
    with engine.connect() as connection:
        rows = connection.exec_driver_sql(
            "SELECT index_name FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND table_name = 'products' "
            "AND column_name = 'sku' AND non_unique = 0"
        )
        return any(row[0] for row in rows)


def add_sku_unique_index() -> bool:
    """Añade el índice único sobre `sku`. Devuelve si lo añadió."""
    if sku_unique_index_exists():
        return False
    with engine.begin() as connection:
        connection.exec_driver_sql(
            f"ALTER TABLE products ADD UNIQUE INDEX {SKU_INDEX_NAME} (sku)"
        )
    return True


def main() -> None:
    created = create_users_table()
    print("Tabla users: " + ("creada" if created else "ya existía"))

    try:
        indexed = add_sku_unique_index()
        print("Índice único en sku: " + ("añadido" if indexed else "ya existía"))
    except Exception as exc:  # noqa: BLE001 - probablemente hay SKU duplicados
        print(
            "No se pudo añadir el índice único en sku "
            f"(revisa duplicados): {exc}"
        )

    print("Migración admin completada (idempotente).")


if __name__ == "__main__":
    main()

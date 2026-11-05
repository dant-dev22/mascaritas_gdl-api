"""Acceso a datos: traduce ProductQuery a SQL sobre MySQL."""

from datetime import date
from uuid import uuid4

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from .catalog_data import (
    CATEGORY_LABELS_EN,
    MASK_PALETTES,
    PALETTE_LABELS_EN,
    PRICE_BUCKET_LABELS_EN,
    PRICE_BUCKETS,
    PRODUCT_CATEGORIES,
    PRODUCT_SIZES,
    SIZE_LABELS_EN,
)
from .catalog_engine import (
    CatalogFacets,
    PaginationMeta,
    ProductQuery,
    build_pagination_meta,
    build_search_blob,
    matches_price_buckets,
    normalize_text,
    resolve_price_bucket,
)
from .models import Product

RELATED_LIMIT = 3


def _search_conditions(query: ProductQuery) -> list:
    conditions: list = []
    term = normalize_text(query.search)
    if term:
        # Se busca en ambos idiomas: basta con que coincida uno de los blobs.
        # Un search_blob_en nulo no rompe el or_ porque el resultado TRUE del
        # blob español se impone; si no coincide ninguno, el filtro descarta.
        conditions.append(
            or_(
                Product.search_blob.contains(term, autoescape=True),
                Product.search_blob_en.contains(term, autoescape=True),
            )
        )
    return conditions


def _filter_conditions(query: ProductQuery) -> list:
    conditions = _search_conditions(query)

    if query.category_ids:
        conditions.append(Product.category_id.in_(query.category_ids))
    if query.size_ids:
        conditions.append(Product.size_id.in_(query.size_ids))
    if query.colors:
        conditions.append(Product.accent_color.in_(query.colors))

    buckets = [
        bucket
        for bucket in (resolve_price_bucket(bucket_id) for bucket_id in query.price_bucket_ids)
        if bucket is not None
    ]
    if buckets:
        price_conditions = []
        for bucket in buckets:
            maximum = bucket["maxMXN"]
            condition = Product.price_mxn >= bucket["minMXN"]
            if maximum is not None:
                condition = and_(condition, Product.price_mxn <= maximum)
            price_conditions.append(condition)
        conditions.append(or_(*price_conditions))

    if query.only_in_stock:
        conditions.append(Product.in_stock.is_(True))

    return conditions


def _order_by(sort: str) -> list:
    if sort == "price-asc":
        return [Product.price_mxn.asc(), Product.position.asc()]
    if sort == "price-desc":
        return [Product.price_mxn.desc(), Product.position.asc()]
    if sort == "newest":
        return [Product.created_at.desc(), Product.position.asc()]
    if sort == "rating":
        return [Product.rating.desc(), Product.reviews_count.desc(), Product.position.asc()]
    return [Product.position.asc()]


def list_products(db: Session, query: ProductQuery) -> tuple[list[Product], PaginationMeta]:
    conditions = _filter_conditions(query)
    total = db.scalar(select(func.count()).select_from(Product).where(*conditions)) or 0
    meta = build_pagination_meta(int(total), query.page, query.per_page)
    offset = (meta.page - 1) * meta.per_page

    stmt = (
        select(Product)
        .where(*conditions)
        .order_by(*_order_by(query.sort))
        .offset(offset)
        .limit(meta.per_page)
    )
    return list(db.scalars(stmt).all()), meta


def get_catalog_facets(db: Session, query: ProductQuery) -> CatalogFacets:
    """Las facetas se calculan sobre el conjunto que respeta solo la búsqueda de texto."""
    conditions = _search_conditions(query)
    rows = list(db.scalars(select(Product).where(*conditions)).all())
    total = len(rows)
    use_en = query.lang == "en"

    categories = [
        {
            "id": category["id"],
            "label": (
                CATEGORY_LABELS_EN.get(category["id"], category["label"])
                if use_en
                else category["label"]
            ),
            "count": sum(1 for row in rows if row.category_id == category["id"]),
        }
        for category in PRODUCT_CATEGORIES
    ]
    sizes = [
        {
            "id": size["id"],
            "label": (
                SIZE_LABELS_EN.get(size["id"], size["label"]) if use_en else size["label"]
            ),
            "count": sum(1 for row in rows if row.size_id == size["id"]),
        }
        for size in PRODUCT_SIZES
    ]
    colors = [
        {
            "id": color_id,
            "label": (
                PALETTE_LABELS_EN.get(color_id, palette["label"]) if use_en else palette["label"]
            ),
            "hex": palette["swatch"],
            "count": sum(1 for row in rows if row.accent_color == color_id),
        }
        for color_id, palette in MASK_PALETTES.items()
    ]
    price_buckets = [
        {
            "id": bucket["id"],
            "label": (
                PRICE_BUCKET_LABELS_EN.get(bucket["id"], bucket["label"])
                if use_en
                else bucket["label"]
            ),
            "count": sum(1 for row in rows if matches_price_buckets(row.price_mxn, [bucket])),
        }
        for bucket in PRICE_BUCKETS
    ]

    return CatalogFacets(
        categories=categories,
        sizes=sizes,
        colors=colors,
        price_buckets=price_buckets,
        total_products=total,
    )


def find_product_by_slug(db: Session, slug: str) -> Product | None:
    return db.scalar(select(Product).where(Product.slug == slug))


def list_related_products(
    db: Session, product: Product, limit: int = RELATED_LIMIT
) -> list[Product]:
    score = (
        case((Product.category_id == product.category_id, 2), else_=0)
        + case((Product.mask_style == product.mask_style, 2), else_=0)
        + case((Product.accent_color == product.accent_color, 1), else_=0)
    )
    stmt = (
        select(Product)
        .where(Product.id != product.id)
        .order_by(score.desc(), Product.rating.desc(), Product.position.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def list_all_slugs(db: Session) -> list[str]:
    return list(db.scalars(select(Product.slug).order_by(Product.position.asc())).all())


# --- Escritura (panel admin) ---

# Campos de texto que tienen versión inglesa (`*_en`). `title` no se traduce.
_EN_TEXT_FIELDS = (
    "subtitle",
    "description",
    "long_description",
    "badge_label",
    "finish",
    "material",
    "lining",
)


def _search_blobs(data: dict) -> tuple[str, str | None]:
    """Recalcula los blobs de búsqueda ES y EN a partir de los datos del producto.

    Reutiliza `build_search_blob`, la misma función que el seed, para no
    duplicar la lógica de normalización.
    """
    search_blob = build_search_blob(
        title=data["title"],
        subtitle=data["subtitle"],
        description=data["description"],
        sku=data["sku"],
        mask_style=data["mask_style"],
        accent_color=data["accent_color"],
        category_id=data["category_id"],
        size_id=data["size_id"],
        tags=data["tags"],
    )

    has_translation = any(data.get(f"{key}_en") for key in _EN_TEXT_FIELDS)
    if not has_translation:
        return search_blob, None

    search_blob_en = build_search_blob(
        title=data["title"],
        subtitle=data.get("subtitle_en") or data["subtitle"],
        description=data.get("description_en") or data["description"],
        sku=data["sku"],
        mask_style=data["mask_style"],
        accent_color=data["accent_color"],
        category_id=data["category_id"],
        size_id=data["size_id"],
        tags=data["tags"],
        lang="en",
    )
    return search_blob, search_blob_en


def next_position(db: Session) -> int:
    """Posición siguiente al final del catálogo (los IDs nuevos van al final)."""
    current = db.scalar(select(func.max(Product.position)))
    return int(current) + 1 if current is not None else 0


def slug_exists(db: Session, slug: str, exclude_id: str | None = None) -> bool:
    stmt = select(Product.id).where(Product.slug == slug)
    if exclude_id is not None:
        stmt = stmt.where(Product.id != exclude_id)
    return db.scalar(stmt) is not None


def sku_exists(db: Session, sku: str, exclude_id: str | None = None) -> bool:
    stmt = select(Product.id).where(Product.sku == sku)
    if exclude_id is not None:
        stmt = stmt.where(Product.id != exclude_id)
    return db.scalar(stmt) is not None


def get_product_by_id(db: Session, product_id: str) -> Product | None:
    return db.get(Product, product_id)


def create_product(db: Session, data: dict) -> Product:
    """Crea un producto calculando id, posición, fecha y blobs de búsqueda."""
    search_blob, search_blob_en = _search_blobs(data)
    product = Product(
        **data,
        id=uuid4().hex,
        position=next_position(db),
        created_at=date.today(),
        search_blob=search_blob,
        search_blob_en=search_blob_en,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: dict) -> Product:
    """Sobrescribe todos los campos editables y recalcula los blobs."""
    search_blob, search_blob_en = _search_blobs(data)
    for key, value in data.items():
        setattr(product, key, value)
    product.search_blob = search_blob
    product.search_blob_en = search_blob_en
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()

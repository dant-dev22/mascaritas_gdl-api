"""Lógica pura del catálogo (espejo de src/__lib__/catalogEngine.ts)."""

import unicodedata
from dataclasses import dataclass, field

from .catalog_data import (
    CATEGORY_LABELS,
    MASK_PALETTES,
    PRICE_BUCKETS,
    SIZE_LABELS,
)


@dataclass(frozen=True)
class ProductQuery:
    search: str = ""
    category_ids: tuple[str, ...] = ()
    size_ids: tuple[str, ...] = ()
    colors: tuple[str, ...] = ()
    price_bucket_ids: tuple[str, ...] = ()
    only_in_stock: bool = False
    sort: str = "featured"
    page: int = 1
    per_page: int = 9


def normalize_text(value: str) -> str:
    """Quita acentos y normaliza para búsquedas tipo "galactico" == "Galáctico"."""
    decomposed = unicodedata.normalize("NFD", value)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_accents.lower().strip()


def build_search_blob(
    *,
    title: str,
    subtitle: str,
    description: str,
    sku: str,
    mask_style: str,
    accent_color: str,
    category_id: str,
    size_id: str,
    tags: list[str],
) -> str:
    parts = [
        title,
        subtitle,
        description,
        sku,
        mask_style,
        MASK_PALETTES[accent_color]["label"],
        CATEGORY_LABELS.get(category_id, ""),
        SIZE_LABELS.get(size_id, ""),
        *tags,
    ]
    return normalize_text(" ".join(parts))


def resolve_price_bucket(bucket_id: str) -> dict[str, object] | None:
    for bucket in PRICE_BUCKETS:
        if bucket["id"] == bucket_id:
            return bucket
    return None


def matches_price_buckets(price_mxn: int, buckets: list[dict[str, object]]) -> bool:
    for bucket in buckets:
        maximum = bucket["maxMXN"]
        if price_mxn >= bucket["minMXN"] and (maximum is None or price_mxn <= maximum):
            return True
    return False


@dataclass(frozen=True)
class PaginationMeta:
    page: int
    per_page: int
    total_items: int
    total_pages: int
    has_prev_page: bool
    has_next_page: bool
    range_start: int
    range_end: int


def build_pagination_meta(total_items: int, page: int, per_page: int) -> PaginationMeta:
    safe_per_page = per_page if per_page > 0 else 1
    total_pages = max(1, -(-total_items // safe_per_page))
    safe_page = min(max(1, page), total_pages)
    offset = (safe_page - 1) * safe_per_page

    return PaginationMeta(
        page=safe_page,
        per_page=safe_per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_prev_page=safe_page > 1,
        has_next_page=safe_page < total_pages,
        range_start=0 if total_items == 0 else offset + 1,
        range_end=min(offset + safe_per_page, total_items),
    )


@dataclass
class CatalogFacets:
    categories: list[dict[str, object]] = field(default_factory=list)
    sizes: list[dict[str, object]] = field(default_factory=list)
    colors: list[dict[str, object]] = field(default_factory=list)
    price_buckets: list[dict[str, object]] = field(default_factory=list)
    total_products: int = 0

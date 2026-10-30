"""Parseo de los search params del catálogo (espejo de src/__lib__/catalogUrl.ts)."""

from collections.abc import Mapping

from .catalog_data import (
    CATALOG_PER_PAGE,
    CATEGORY_IDS,
    COLOR_IDS,
    DEFAULT_CATALOG_SORT,
    MAX_PER_PAGE,
    PRICE_BUCKET_IDS,
    SIZE_IDS,
    SORT_IDS,
)
from .catalog_engine import ProductQuery

PARAM = {
    "search": "q",
    "categories": "cat",
    "sizes": "talla",
    "colors": "color",
    "price": "precio",
    "inStock": "stock",
    "sort": "orden",
    "page": "pagina",
    "perPage": "perPage",
}


def _read_list(params: Mapping[str, str], key: str, allowed: list[str]) -> tuple[str, ...]:
    raw = params.get(key)
    if not raw:
        return ()
    return tuple(
        value for value in (part.strip() for part in raw.split(",")) if value in allowed
    )


def _read_page(params: Mapping[str, str]) -> int:
    raw = params.get(PARAM["page"], "")
    try:
        page = int(raw)
    except (TypeError, ValueError):
        return 1
    return page if page > 0 else 1


def _read_per_page(params: Mapping[str, str]) -> int:
    raw = params.get(PARAM["perPage"], "")
    if not raw:
        return CATALOG_PER_PAGE
    try:
        per_page = int(raw)
    except (TypeError, ValueError):
        return CATALOG_PER_PAGE
    return min(max(1, per_page), MAX_PER_PAGE)


def _read_sort(params: Mapping[str, str]) -> str:
    raw = params.get(PARAM["sort"])
    if raw and raw in SORT_IDS:
        return raw
    return DEFAULT_CATALOG_SORT


def parse_catalog_params(params: Mapping[str, str]) -> ProductQuery:
    return ProductQuery(
        search=(params.get(PARAM["search"]) or "").strip(),
        category_ids=_read_list(params, PARAM["categories"], CATEGORY_IDS),
        size_ids=_read_list(params, PARAM["sizes"], SIZE_IDS),
        colors=_read_list(params, PARAM["colors"], COLOR_IDS),
        price_bucket_ids=_read_list(params, PARAM["price"], PRICE_BUCKET_IDS),
        only_in_stock=params.get(PARAM["inStock"]) == "1",
        sort=_read_sort(params),
        page=_read_page(params),
        per_page=_read_per_page(params),
    )

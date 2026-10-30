"""Schemas de respuesta (Pydantic). Serializan en camelCase como espera el frontend."""

from datetime import date

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ProductBadge(CamelModel):
    variant: str
    label: str


class ProductOut(CamelModel):
    id: str
    slug: str
    sku: str
    title: str
    subtitle: str
    description: str
    long_description: str
    price_mxn: int
    old_price_mxn: int | None = None
    badge: ProductBadge | None = None
    accent_color: str
    category_id: str
    size_id: str
    mask_style: str
    finish: str
    material: str
    lining: str
    in_stock: bool
    stock_count: int
    rating: float
    reviews_count: int
    tags: list[str]
    created_at: date


class PaginationMetaOut(CamelModel):
    page: int
    per_page: int
    total_items: int
    total_pages: int
    has_prev_page: bool
    has_next_page: bool
    range_start: int
    range_end: int


class PaginatedProducts(CamelModel):
    items: list[ProductOut]
    meta: PaginationMetaOut


class FacetBucketOut(CamelModel):
    id: str
    label: str
    count: int


class ColorFacetBucketOut(FacetBucketOut):
    hex: str


class CatalogFacetsOut(CamelModel):
    categories: list[FacetBucketOut]
    sizes: list[FacetBucketOut]
    colors: list[ColorFacetBucketOut]
    price_buckets: list[FacetBucketOut]
    total_products: int


class CatalogListResponse(CamelModel):
    result: PaginatedProducts
    facets: CatalogFacetsOut


class CatalogProductResponse(CamelModel):
    product: ProductOut
    related: list[ProductOut]


class FacetsResponse(CamelModel):
    facets: CatalogFacetsOut


class MessageResponse(CamelModel):
    message: str

"""Schemas de respuesta (Pydantic). Serializan en camelCase como espera el frontend."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
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
    price_mxn: int = Field(serialization_alias="priceMXN")
    old_price_mxn: int | None = Field(default=None, serialization_alias="oldPriceMXN")
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


# --- Panel admin ---


class LoginRequest(CamelModel):
    email: str
    password: str


class UserOut(CamelModel):
    id: int
    email: str
    name: str
    role: str


class AdminProductOut(ProductOut):
    """Producto con las traducciones crudas, para editar en el panel.

    El catálogo público localiza el texto según el idioma y no necesita ver
    los dos valores a la vez; el formulario del panel sí, para no perder las
    traducciones al guardar.
    """

    subtitle_en: str | None = None
    description_en: str | None = None
    long_description_en: str | None = None
    badge_label_en: str | None = None
    finish_en: str | None = None
    material_en: str | None = None
    lining_en: str | None = None


class TokenResponse(CamelModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")
    user: UserOut


# --- Escritura de productos (panel admin) ---

AccentColor = Literal["gold", "green", "red", "blue", "purple", "silver"]
CategoryId = Literal["semi-pro", "profesional"]
SizeId = Literal["infantil", "adulto", "adulto-xl"]
MaskStyle = Literal["tiburon", "diablo", "galactico", "aguila", "serpiente", "pantera"]
BadgeVariant = Literal["semi-pro", "last-units", "new"]

# Slug en kebab-case: minúsculas, números y guiones simples.
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class ProductWrite(CamelModel):
    """Cuerpo de entrada para crear o editar un producto.

    No incluye los campos que calcula el backend (`id`, `position`,
    `createdAt`, `searchBlob`, `searchBlobEn`).
    """

    slug: str = Field(min_length=1, max_length=128, pattern=SLUG_PATTERN)
    sku: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=128)
    subtitle: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1)
    long_description: str = Field(min_length=1)
    price_mxn: int = Field(alias="priceMXN", gt=0)
    old_price_mxn: int | None = Field(default=None, alias="oldPriceMXN", ge=0)
    badge_variant: BadgeVariant | None = None
    badge_label: str | None = Field(default=None, max_length=48)
    accent_color: AccentColor
    category_id: CategoryId
    size_id: SizeId
    mask_style: MaskStyle
    finish: str = Field(min_length=1, max_length=96)
    material: str = Field(min_length=1, max_length=96)
    lining: str = Field(min_length=1, max_length=96)
    in_stock: bool = True
    stock_count: int = Field(default=0, ge=0)
    rating: float = Field(default=0, ge=0, le=5)
    reviews_count: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)

    # Traducciones opcionales. `title` no se traduce.
    subtitle_en: str | None = Field(default=None, max_length=128)
    description_en: str | None = None
    long_description_en: str | None = None
    badge_label_en: str | None = Field(default=None, max_length=48)
    finish_en: str | None = Field(default=None, max_length=96)
    material_en: str | None = Field(default=None, max_length=96)
    lining_en: str | None = Field(default=None, max_length=96)

    @model_validator(mode="after")
    def _validate(self) -> "ProductWrite":
        # El badge se compone de variante + texto: o van los dos o ninguno.
        if bool(self.badge_variant) != bool(self.badge_label):
            raise ValueError("badgeVariant y badgeLabel deben venir juntos")
        # El precio tachado (antes) nunca puede ser menor que el actual.
        if self.old_price_mxn is not None and self.old_price_mxn < self.price_mxn:
            raise ValueError("oldPriceMXN debe ser mayor o igual que priceMXN")
        return self

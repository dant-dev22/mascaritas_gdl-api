"""Modelos ORM."""

from datetime import date

from sqlalchemy import JSON, Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    # Orden de catálogo original: es el criterio de "featured" y de desempate.
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    long_description: Mapped[str] = mapped_column(Text, nullable=False)
    price_mxn: Mapped[int] = mapped_column(Integer, nullable=False)
    old_price_mxn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    badge_variant: Mapped[str | None] = mapped_column(String(24), nullable=True)
    badge_label: Mapped[str | None] = mapped_column(String(48), nullable=True)
    accent_color: Mapped[str] = mapped_column(String(16), nullable=False)
    category_id: Mapped[str] = mapped_column(String(24), nullable=False)
    size_id: Mapped[str] = mapped_column(String(16), nullable=False)
    mask_style: Mapped[str] = mapped_column(String(24), nullable=False)
    finish: Mapped[str] = mapped_column(String(96), nullable=False)
    material: Mapped[str] = mapped_column(String(96), nullable=False)
    lining: Mapped[str] = mapped_column(String(96), nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    stock_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    reviews_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    # Texto normalizado (sin acentos, minúsculas) usado por la búsqueda.
    search_blob: Mapped[str] = mapped_column(Text, nullable=False)

    @property
    def badge(self) -> dict[str, str] | None:
        if self.badge_variant is None or self.badge_label is None:
            return None
        return {"variant": self.badge_variant, "label": self.badge_label}

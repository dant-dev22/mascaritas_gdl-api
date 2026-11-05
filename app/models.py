"""Modelos ORM."""

from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Fecha-hora UTC sin zona, para columnas `DateTime` de MySQL."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
    # Traducciones al inglés. Nullable: sin traducción se cae al español.
    # El nombre comercial (`title`) no se traduce.
    subtitle_en: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    long_description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    badge_label_en: Mapped[str | None] = mapped_column(String(48), nullable=True)
    finish_en: Mapped[str | None] = mapped_column(String(96), nullable=True)
    material_en: Mapped[str | None] = mapped_column(String(96), nullable=True)
    lining_en: Mapped[str | None] = mapped_column(String(96), nullable=True)
    search_blob_en: Mapped[str | None] = mapped_column(Text, nullable=True)

    @property
    def badge(self) -> dict[str, str] | None:
        if self.badge_variant is None or self.badge_label is None:
            return None
        return {"variant": self.badge_variant, "label": self.badge_label}


class User(Base):
    """Cuenta del panel admin. Un solo rol (`admin`) en esta versión."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(24), nullable=False, default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)


class Order(Base):
    """Pedido rastreable. Se alimenta a mano desde el panel admin."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    # Código público que el cliente usa para consultar su pedido (ej. MG-8F3K2A).
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    # Correo o teléfono de contacto. Opcional y nunca se expone en el rastreo público.
    customer_contact: Mapped[str | None] = mapped_column(String(160), nullable=True)
    # Identificador de paquetería (ver `order_data.ORDER_CARRIERS`) o texto libre.
    carrier: Mapped[str | None] = mapped_column(String(48), nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="recibido")
    # Notas internas del equipo: no se muestran al cliente.
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class OrderEvent(Base):
    """Hito de la línea de tiempo de un pedido (visible para el cliente)."""

    __tablename__ = "order_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    # Comentario opcional que sí puede leer el cliente.
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

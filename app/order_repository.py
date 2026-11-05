"""Acceso a datos del dominio de pedidos (rastreo + panel admin)."""

import secrets
from uuid import uuid4

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from .catalog_engine import PaginationMeta, build_pagination_meta
from .models import Order, OrderEvent, utcnow
from .order_data import CODE_ALPHABET, CODE_LENGTH, CODE_PREFIX


def _generate_code() -> str:
    body = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
    return f"{CODE_PREFIX}{body}"


def generate_order_code(db: Session) -> str:
    """Código público aleatorio, reintentando si (por azar) ya existe."""
    for _ in range(10):
        code = _generate_code()
        if db.scalar(select(Order.id).where(Order.code == code)) is None:
            return code
    # En la práctica inalcanzable: 31^6 combinaciones.
    raise RuntimeError("No se pudo generar un código de pedido único")


def list_orders(
    db: Session,
    search: str = "",
    page: int = 1,
    per_page: int = 12,
) -> tuple[list[Order], PaginationMeta]:
    conditions = []
    term = search.strip()
    if term:
        pattern = f"%{term}%"
        conditions.append(or_(Order.code.like(pattern), Order.customer_name.like(pattern)))

    total = db.scalar(select(func.count()).select_from(Order).where(*conditions)) or 0
    meta = build_pagination_meta(int(total), page, per_page)
    offset = (meta.page - 1) * meta.per_page

    stmt = (
        select(Order)
        .where(*conditions)
        .order_by(Order.updated_at.desc(), Order.created_at.desc())
        .offset(offset)
        .limit(meta.per_page)
    )
    return list(db.scalars(stmt).all()), meta


def get_order_by_id(db: Session, order_id: str) -> Order | None:
    return db.get(Order, order_id)


def find_order_by_code(db: Session, code: str) -> Order | None:
    return db.scalar(select(Order).where(Order.code == code))


def list_events(db: Session, order_id: str) -> list[OrderEvent]:
    """Hitos del pedido en orden cronológico ascendente."""
    stmt = (
        select(OrderEvent)
        .where(OrderEvent.order_id == order_id)
        .order_by(OrderEvent.created_at.asc(), OrderEvent.id.asc())
    )
    return list(db.scalars(stmt).all())


def _add_event(db: Session, order_id: str, status: str, note: str | None) -> None:
    db.add(OrderEvent(order_id=order_id, status=status, note=note))


def create_order(db: Session, data: dict) -> Order:
    """Crea el pedido y registra su primer hito en la línea de tiempo."""
    note = data.pop("note", None)
    order = Order(
        **data,
        id=uuid4().hex,
        code=generate_order_code(db),
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db.add(order)
    db.flush()
    _add_event(db, order.id, order.status, note)
    db.commit()
    db.refresh(order)
    return order


def update_order(db: Session, order: Order, data: dict) -> Order:
    """Sobrescribe los campos editables y añade un hito si cambió el estado."""
    note = data.pop("note", None)
    status_changed = data.get("status") is not None and data["status"] != order.status

    for key, value in data.items():
        setattr(order, key, value)

    order.updated_at = utcnow()
    if status_changed:
        _add_event(db, order.id, order.status, note)

    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order: Order) -> None:
    """Elimina el pedido y sus hitos.

    Los hitos se borran primero con un DELETE directo: la clave foránea ya tiene
    `ON DELETE CASCADE`, así que si dejáramos que el ORM los borrara después del
    pedido, la base se los habría llevado antes y SQLAlchemy avisaría con un
    `SAWarning` de filas no encontradas.
    """
    db.execute(delete(OrderEvent).where(OrderEvent.order_id == order.id))
    db.delete(order)
    db.commit()

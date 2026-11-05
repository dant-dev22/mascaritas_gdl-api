"""CRUD de pedidos del panel admin. Todo detrás de `require_admin`."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_admin
from ..models import Order
from ..order_repository import (
    create_order,
    delete_order,
    get_order_by_id,
    list_events,
    list_orders,
    update_order,
)
from ..schemas import (
    AdminOrderOut,
    OrderEventOut,
    OrderWrite,
    PaginatedOrders,
    PaginationMetaOut,
)

router = APIRouter(
    prefix="/admin/pedidos",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")


def _serialize(db: Session, order: Order) -> AdminOrderOut:
    events = list_events(db, order.id)
    data = AdminOrderOut.model_validate(order)
    return data.model_copy(
        update={"timeline": [OrderEventOut.model_validate(event) for event in events]}
    )


@router.get("", response_model=PaginatedOrders)
def list_admin_orders(
    search: str = "",
    page: int = Query(1, ge=1),
    per_page: int = Query(12, alias="perPage", ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedOrders:
    """Lista los pedidos, los más recientes primero."""
    orders, meta = list_orders(db, search=search, page=page, per_page=per_page)
    return PaginatedOrders(
        items=[_serialize(db, order) for order in orders],
        meta=PaginationMetaOut.model_validate(meta),
    )


@router.get("/{order_id}", response_model=AdminOrderOut)
def get_admin_order(order_id: str, db: Session = Depends(get_db)) -> AdminOrderOut:
    order = get_order_by_id(db, order_id)
    if order is None:
        raise _not_found()
    return _serialize(db, order)


@router.post("", response_model=AdminOrderOut, status_code=status.HTTP_201_CREATED)
def create_admin_order(payload: OrderWrite, db: Session = Depends(get_db)) -> AdminOrderOut:
    order = create_order(db, payload.model_dump())
    return _serialize(db, order)


@router.put("/{order_id}", response_model=AdminOrderOut)
def update_admin_order(
    order_id: str,
    payload: OrderWrite,
    db: Session = Depends(get_db),
) -> AdminOrderOut:
    order = get_order_by_id(db, order_id)
    if order is None:
        raise _not_found()
    order = update_order(db, order, payload.model_dump())
    return _serialize(db, order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_order(order_id: str, db: Session = Depends(get_db)) -> Response:
    order = get_order_by_id(db, order_id)
    if order is None:
        raise _not_found()
    delete_order(db, order)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

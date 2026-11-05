"""Rastreo público de pedidos. Se consulta solo con el código."""

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..order_repository import find_order_by_code, list_events
from ..rate_limit import order_lookup_limiter
from ..schemas import OrderEventOut, OrderPublicOut

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

NO_STORE = {"cache-control": "no-store"}


@router.get("/{code}", response_model=OrderPublicOut)
def track_order(code: str, response: Response, db: Session = Depends(get_db)):
    """Devuelve el estado y la línea de tiempo del pedido con ese código."""
    normalized = code.strip().upper()
    order_lookup_limiter.check(normalized)

    order = find_order_by_code(db, normalized)
    if order is None:
        order_lookup_limiter.register_failure(normalized)
        return JSONResponse(
            status_code=404,
            content={"message": "Pedido no encontrado"},
            headers=NO_STORE,
        )

    order_lookup_limiter.reset(normalized)
    events = list_events(db, order.id)
    response.headers.update(NO_STORE)
    return OrderPublicOut(
        code=order.code,
        status=order.status,
        customer_name=order.customer_name,
        carrier=order.carrier,
        tracking_number=order.tracking_number,
        timeline=[OrderEventOut.model_validate(event) for event in events],
    )

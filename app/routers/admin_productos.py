"""CRUD de productos del panel admin. Todo detrás de `require_admin`."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..catalog_engine import ProductQuery
from ..database import get_db
from ..dependencies import require_admin
from ..repository import (
    create_product,
    delete_product,
    get_product_by_id,
    list_products,
    sku_exists,
    slug_exists,
    update_product,
)
from ..schemas import (
    AdminProductOut,
    PaginatedProducts,
    PaginationMetaOut,
    ProductOut,
    ProductWrite,
)

router = APIRouter(
    prefix="/admin/productos",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")


def _conflict(field: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"El {field} ya está en uso",
    )


@router.get("", response_model=PaginatedProducts)
def list_admin_products(
    search: str = "",
    sort: str = "featured",
    page: int = Query(1, ge=1),
    per_page: int = Query(12, alias="perPage", ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedProducts:
    """Lista todo el catálogo (incluye productos sin stock)."""
    query = ProductQuery(search=search, sort=sort, page=page, per_page=per_page)
    items, meta = list_products(db, query)
    return PaginatedProducts(
        items=[ProductOut.model_validate(item) for item in items],
        meta=PaginationMetaOut.model_validate(meta),
    )


@router.get("/{product_id}", response_model=AdminProductOut)
def get_admin_product(product_id: str, db: Session = Depends(get_db)) -> AdminProductOut:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise _not_found()
    return AdminProductOut.model_validate(product)


@router.post("", response_model=AdminProductOut, status_code=status.HTTP_201_CREATED)
def create_admin_product(payload: ProductWrite, db: Session = Depends(get_db)) -> AdminProductOut:
    if slug_exists(db, payload.slug):
        raise _conflict("slug")
    if sku_exists(db, payload.sku):
        raise _conflict("SKU")
    product = create_product(db, payload.model_dump())
    return AdminProductOut.model_validate(product)


@router.put("/{product_id}", response_model=AdminProductOut)
def update_admin_product(
    product_id: str,
    payload: ProductWrite,
    db: Session = Depends(get_db),
) -> AdminProductOut:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise _not_found()
    if slug_exists(db, payload.slug, exclude_id=product.id):
        raise _conflict("slug")
    if sku_exists(db, payload.sku, exclude_id=product.id):
        raise _conflict("SKU")
    product = update_product(db, product, payload.model_dump())
    return AdminProductOut.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_product(product_id: str, db: Session = Depends(get_db)) -> Response:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise _not_found()
    delete_product(db, product)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

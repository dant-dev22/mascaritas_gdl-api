"""Endpoints del catálogo. Espejo del contrato de src/app/api/productos del frontend."""

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..query_params import parse_catalog_params
from ..repository import (
    find_product_by_slug,
    get_catalog_facets,
    list_products,
    list_related_products,
)
from ..schemas import (
    CatalogFacetsOut,
    CatalogListResponse,
    CatalogProductResponse,
    FacetsResponse,
    PaginatedProducts,
    PaginationMetaOut,
    ProductOut,
)

router = APIRouter(prefix="/productos", tags=["productos"])

NO_STORE = {"cache-control": "no-store"}


def _parse(request: Request):
    return parse_catalog_params(dict(request.query_params))


@router.get("", response_model=CatalogListResponse)
def list_catalog(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> CatalogListResponse:
    query = _parse(request)
    items, meta = list_products(db, query)
    facets = get_catalog_facets(db, query)

    response.headers.update(NO_STORE)
    return CatalogListResponse(
        result=PaginatedProducts(
            items=[ProductOut.model_validate(item) for item in items],
            meta=PaginationMetaOut.model_validate(meta),
        ),
        facets=CatalogFacetsOut.model_validate(facets),
    )


@router.get("/facetas", response_model=FacetsResponse)
def list_facets(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> FacetsResponse:
    facets = get_catalog_facets(db, _parse(request))
    response.headers.update(NO_STORE)
    return FacetsResponse(facets=CatalogFacetsOut.model_validate(facets))


@router.get("/{slug}", response_model=CatalogProductResponse)
def get_product(
    slug: str,
    response: Response,
    db: Session = Depends(get_db),
):
    product = find_product_by_slug(db, slug)
    if product is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Producto no encontrado"},
            headers=NO_STORE,
        )

    related = list_related_products(db, product)
    response.headers.update(NO_STORE)
    return CatalogProductResponse(
        product=ProductOut.model_validate(product),
        related=[ProductOut.model_validate(item) for item in related],
    )

"""Localización del catálogo: resuelve el idioma y adapta los productos.

El español es la base. Cuando se pide inglés y existe la traducción (`*_en`
no nula ni vacía) se sustituye el texto; si falta, se cae al español.
"""

from .models import Product

# Campos cuyo texto se traduce al inglés. La clave del diccionario es el
# nombre de la columna en español y el sufijo `_en` da la columna inglesa.
_TRANSLATABLE_FIELDS = (
    "title",
    "subtitle",
    "description",
    "long_description",
    "finish",
    "material",
    "lining",
)


def resolve_lang(raw: str | None) -> str:
    """Devuelve "en" solo si `raw` es exactamente "en"; si no, "es"."""
    return "en" if raw == "en" else "es"


def _has_translation(value: object) -> bool:
    """Hay traducción cuando el valor inglés no es None ni cadena vacía."""
    return value is not None and value != ""


def localize_product(product: Product, lang: str) -> dict[str, object]:
    """Devuelve un dict listo para `ProductOut.model_validate(...)`."""
    data: dict[str, object] = {
        column.key: getattr(product, column.key)
        for column in Product.__table__.columns
    }

    if lang == "en":
        for field in _TRANSLATABLE_FIELDS:
            translated = getattr(product, f"{field}_en")
            if _has_translation(translated):
                data[field] = translated

    badge_variant = data.get("badge_variant")
    label_es = data.get("badge_label")
    label_en = data.get("badge_label_en")
    if lang == "en" and _has_translation(label_en):
        label = label_en
    else:
        label = label_es

    if not _has_translation(badge_variant) or not _has_translation(label):
        data["badge"] = None
    else:
        data["badge"] = {"variant": badge_variant, "label": label}

    return data


def localize_products(products: list[Product], lang: str) -> list[dict[str, object]]:
    """Aplica `localize_product` a una lista de productos."""
    return [localize_product(product, lang) for product in products]

"""Constantes de dominio del catálogo (espejo de src/__data__ del frontend)."""

CATALOG_PER_PAGE = 9
MAX_PER_PAGE = 100
DEFAULT_CATALOG_SORT = "featured"

# El orden de las claves define el orden de las facetas de color.
MASK_PALETTES: dict[str, dict[str, str]] = {
    "gold": {
        "id": "gold",
        "label": "Dorado",
        "base": "#2a2000",
        "baseDark": "#120c00",
        "accent": "#f4c542",
        "accentDark": "#d99b2c",
        "contrast": "#e63946",
        "swatch": "#f4c542",
    },
    "green": {
        "id": "green",
        "label": "Verde",
        "base": "#003322",
        "baseDark": "#001810",
        "accent": "#00a86b",
        "accentDark": "#008f5a",
        "contrast": "#e63946",
        "swatch": "#00a86b",
    },
    "red": {
        "id": "red",
        "label": "Rojo",
        "base": "#33080c",
        "baseDark": "#1a0406",
        "accent": "#e63946",
        "accentDark": "#b82833",
        "contrast": "#f4c542",
        "swatch": "#e63946",
    },
    "blue": {
        "id": "blue",
        "label": "Azul",
        "base": "#041a33",
        "baseDark": "#020d1a",
        "accent": "#2f80ed",
        "accentDark": "#1f5fb3",
        "contrast": "#f4c542",
        "swatch": "#2f80ed",
    },
    "purple": {
        "id": "purple",
        "label": "Morado",
        "base": "#1e0633",
        "baseDark": "#0f031a",
        "accent": "#9b51e0",
        "accentDark": "#7439ad",
        "contrast": "#00a86b",
        "swatch": "#9b51e0",
    },
    "silver": {
        "id": "silver",
        "label": "Plata",
        "base": "#1f2226",
        "baseDark": "#0f1114",
        "accent": "#c9ced6",
        "accentDark": "#9aa1ab",
        "contrast": "#e63946",
        "swatch": "#c9ced6",
    },
}

PRODUCT_CATEGORIES: list[dict[str, str]] = [
    {
        "id": "semi-pro",
        "label": "Semi-Pro",
        "description": "Reforzadas para entrenamiento y funciones locales.",
    },
    {
        "id": "profesional",
        "label": "Profesional",
        "description": "Ediciones de colección y acabados premium.",
    },
]

PRODUCT_SIZES: list[dict[str, str]] = [
    {"id": "infantil", "label": "Infantil", "hint": "6 a 12 años"},
    {"id": "adulto", "label": "Adulto", "hint": "Talla estándar ajustable"},
    {"id": "adulto-xl", "label": "Adulto XL", "hint": "Cabezas grandes / con cabello"},
]

PRICE_BUCKETS: list[dict[str, object]] = [
    {"id": "under-500", "label": "Menos de $500", "minMXN": 0, "maxMXN": 499},
    {"id": "under-1000", "label": "Menos de $1,000", "minMXN": 0, "maxMXN": 999},
    {"id": "over-1000", "label": "Más de $1,000", "minMXN": 1000, "maxMXN": None},
]

PRODUCT_SORT_OPTIONS: list[dict[str, str]] = [
    {"id": "featured", "label": "Destacados"},
    {"id": "price-asc", "label": "Precio: menor a mayor"},
    {"id": "price-desc", "label": "Precio: mayor a menor"},
    {"id": "newest", "label": "Más recientes"},
    {"id": "rating", "label": "Mejor calificadas"},
]

CATEGORY_IDS = [item["id"] for item in PRODUCT_CATEGORIES]
SIZE_IDS = ["infantil", "adulto", "adulto-xl"]
COLOR_IDS = list(MASK_PALETTES.keys())
PRICE_BUCKET_IDS = [item["id"] for item in PRICE_BUCKETS]
SORT_IDS = [item["id"] for item in PRODUCT_SORT_OPTIONS]

CATEGORY_LABELS = {item["id"]: item["label"] for item in PRODUCT_CATEGORIES}
SIZE_LABELS = {item["id"]: item["label"] for item in PRODUCT_SIZES}

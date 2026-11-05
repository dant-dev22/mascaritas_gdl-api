"""Constantes del dominio de pedidos: estados, paqueterías y códigos."""

# Secuencia natural del pedido. `cancelado` es un estado terminal aparte.
ORDER_PROGRESS_STATUSES: tuple[str, ...] = (
    "recibido",
    "en_preparacion",
    "enviado",
    "en_transito",
    "entregado",
)

ORDER_STATUSES: tuple[str, ...] = ORDER_PROGRESS_STATUSES + ("cancelado",)

DEFAULT_ORDER_STATUS = ORDER_PROGRESS_STATUSES[0]

# Identificadores de paquetería. El público los localiza; un valor desconocido
# se muestra tal cual (texto libre del admin).
ORDER_CARRIERS: tuple[str, ...] = (
    "correos_de_mexico",
    "estafeta",
    "dhl",
    "fedex",
    "paqueteria_privada",
    "otro",
)

CODE_PREFIX = "MG-"
CODE_LENGTH = 6
# Alfabeto sin caracteres ambiguos (0/O, 1/I/L) para dictar el código por teléfono.
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"

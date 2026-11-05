"""Pruebas del CRUD de productos del panel admin."""

from collections.abc import Callable

from fastapi.testclient import TestClient

ADMIN_URL = "/api/admin/productos"


def test_listar_requiere_sesion(client: TestClient) -> None:
    assert client.get(ADMIN_URL).status_code == 401


def test_crear_producto(client: TestClient, auth_headers: dict[str, str], make_product: Callable[..., dict]) -> None:
    response = client.post(ADMIN_URL, json=make_product(), headers=auth_headers)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["id"]
    assert body["slug"] == "mascara-prueba"
    assert body["priceMXN"] == 1200
    assert body["inStock"] is True


def test_crear_slug_duplicado(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    client.post(ADMIN_URL, json=make_product(), headers=auth_headers)

    response = client.post(ADMIN_URL, json=make_product(sku="TEST-002"), headers=auth_headers)
    assert response.status_code == 409


def test_crear_sku_duplicado(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    client.post(ADMIN_URL, json=make_product(), headers=auth_headers)

    response = client.post(ADMIN_URL, json=make_product(slug="otra-mascara"), headers=auth_headers)
    assert response.status_code == 409


def test_crear_slug_con_formato_invalido(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    response = client.post(ADMIN_URL, json=make_product(slug="Slug_Invalido"), headers=auth_headers)
    assert response.status_code == 422


def test_crear_badge_incompleto(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    response = client.post(ADMIN_URL, json=make_product(badgeVariant="new"), headers=auth_headers)
    assert response.status_code == 422


def test_crear_precio_tachado_menor(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    response = client.post(ADMIN_URL, json=make_product(priceMXN=1200, oldPriceMXN=900), headers=auth_headers)
    assert response.status_code == 422


def test_crear_precio_cero(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    response = client.post(ADMIN_URL, json=make_product(priceMXN=0), headers=auth_headers)
    assert response.status_code == 422


def test_obtener_por_id(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    created = client.post(ADMIN_URL, json=make_product(), headers=auth_headers).json()

    response = client.get(f"{ADMIN_URL}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_obtener_id_inexistente(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get(f"{ADMIN_URL}/no-existe", headers=auth_headers).status_code == 404


def test_obtener_incluye_traducciones_en(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    """El formulario del panel necesita los dos idiomas crudos para no perderlos al guardar."""
    payload = make_product(
        subtitleEn="English subtitle",
        descriptionEn="English description",
        longDescriptionEn="English long description",
        badgeLabelEn="New",
        finishEn="Matte",
        materialEn="Leather",
        liningEn="Satin",
    )
    created = client.post(ADMIN_URL, json=payload, headers=auth_headers).json()

    response = client.get(f"{ADMIN_URL}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["subtitleEn"] == "English subtitle"
    assert body["descriptionEn"] == "English description"
    assert body["longDescriptionEn"] == "English long description"
    assert body["badgeLabelEn"] == "New"
    assert body["finishEn"] == "Matte"
    assert body["materialEn"] == "Leather"
    assert body["liningEn"] == "Satin"


def test_actualizar_conserva_traducciones_en(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    created = client.post(
        ADMIN_URL,
        json=make_product(subtitleEn="English subtitle", materialEn="Leather"),
        headers=auth_headers,
    ).json()

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=make_product(subtitleEn="English subtitle", materialEn="Leather", priceMXN=1500),
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["subtitleEn"] == "English subtitle"
    assert body["materialEn"] == "Leather"


def test_actualizar_producto(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    created = client.post(ADMIN_URL, json=make_product(), headers=auth_headers).json()

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=make_product(priceMXN=1500, stockCount=4),
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["priceMXN"] == 1500
    assert body["stockCount"] == 4
    assert body["id"] == created["id"]


def test_actualizar_slug_duplicado(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    client.post(ADMIN_URL, json=make_product(), headers=auth_headers)
    segundo = client.post(
        ADMIN_URL,
        json=make_product(slug="segunda-mascara", sku="TEST-002"),
        headers=auth_headers,
    ).json()

    response = client.put(f"{ADMIN_URL}/{segundo['id']}", json=make_product(), headers=auth_headers)
    assert response.status_code == 409


def test_eliminar_producto(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    created = client.post(ADMIN_URL, json=make_product(), headers=auth_headers).json()

    assert client.delete(f"{ADMIN_URL}/{created['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"{ADMIN_URL}/{created['id']}", headers=auth_headers).status_code == 404


def test_listar_incluye_productos_sin_stock(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    client.post(ADMIN_URL, json=make_product(inStock=False, stockCount=0), headers=auth_headers)

    response = client.get(ADMIN_URL, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["meta"]["totalItems"] == 1


def test_busqueda_en_ingles(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    payload = make_product(
        subtitleEn="Test english subtitle",
        descriptionEn="A very particular tokenpalabra inside",
    )
    client.post(ADMIN_URL, json=payload, headers=auth_headers)

    response = client.get("/api/productos", params={"q": "tokenpalabra", "lang": "en"})
    assert response.status_code == 200
    assert response.json()["result"]["meta"]["totalItems"] == 1


def test_busqueda_ignora_acentos(
    client: TestClient,
    auth_headers: dict[str, str],
    make_product: Callable[..., dict],
) -> None:
    client.post(ADMIN_URL, json=make_product(), headers=auth_headers)

    response = client.get("/api/productos", params={"q": "mascara", "lang": "es"})
    assert response.status_code == 200
    assert response.json()["result"]["meta"]["totalItems"] == 1

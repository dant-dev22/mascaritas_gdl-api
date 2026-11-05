"""Pruebas del rastreo público y del CRUD de pedidos."""

from fastapi.testclient import TestClient

ADMIN_URL = "/api/admin/pedidos"
PUBLIC_URL = "/api/pedidos"


def payload(**overrides) -> dict:
    data = {
        "customerName": "Ana Luchadora",
        "customerContact": "ana@test.local",
        "carrier": "estafeta",
        "trackingNumber": "1234567890",
        "status": "recibido",
        "internalNotes": "Pago confirmado por transferencia.",
    }
    data.update(overrides)
    return data


# --- Panel admin ---


def test_listar_requiere_sesion(client: TestClient) -> None:
    assert client.get(ADMIN_URL).status_code == 401


def test_crear_pedido_genera_codigo_y_primer_hito(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(ADMIN_URL, json=payload(note="Pedido recibido"), headers=auth_headers)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["code"].startswith("MG-")
    assert body["status"] == "recibido"
    assert body["customerContact"] == "ana@test.local"
    assert len(body["timeline"]) == 1
    assert body["timeline"][0]["status"] == "recibido"
    assert body["timeline"][0]["note"] == "Pedido recibido"


def test_cambio_de_estado_agrega_hito(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(ADMIN_URL, json=payload(), headers=auth_headers).json()

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=payload(status="enviado", note="Salió del taller"),
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "enviado"
    assert [event["status"] for event in body["timeline"]] == ["recibido", "enviado"]


def test_mismo_estado_no_duplica_hito(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(ADMIN_URL, json=payload(), headers=auth_headers).json()

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=payload(carrier="dhl"),
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert len(response.json()["timeline"]) == 1


def test_estado_invalido(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(ADMIN_URL, json=payload(status="volando"), headers=auth_headers)
    assert response.status_code == 422


def test_obtener_id_inexistente(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get(f"{ADMIN_URL}/no-existe", headers=auth_headers).status_code == 404


def test_eliminar_pedido(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post(ADMIN_URL, json=payload(), headers=auth_headers).json()

    assert client.delete(f"{ADMIN_URL}/{created['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"{ADMIN_URL}/{created['id']}", headers=auth_headers).status_code == 404


def test_listar_busca_por_codigo(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post(ADMIN_URL, json=payload(), headers=auth_headers).json()

    response = client.get(ADMIN_URL, params={"search": created["code"]}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["totalItems"] == 1
    assert body["items"][0]["code"] == created["code"]


# --- Rastreo público ---


def test_rastreo_publico_oculta_datos_internos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(ADMIN_URL, json=payload(), headers=auth_headers).json()

    response = client.get(f"{PUBLIC_URL}/{created['code']}")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "recibido"
    assert body["carrier"] == "estafeta"
    assert len(body["timeline"]) == 1
    assert "customerContact" not in body
    assert "internalNotes" not in body


def test_rastreo_acepta_codigo_en_minusculas(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(ADMIN_URL, json=payload(), headers=auth_headers).json()

    response = client.get(f"{PUBLIC_URL}/{created['code'].lower()}")
    assert response.status_code == 200


def test_rastreo_codigo_inexistente(client: TestClient) -> None:
    assert client.get(f"{PUBLIC_URL}/MG-XXXXXX").status_code == 404

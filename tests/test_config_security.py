"""Pruebas de la guarda de configuración de seguridad."""

import pytest

from app import config

CLAVE_FUERTE = "x" * 40


def test_en_desarrollo_no_valida(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "IS_PRODUCTION", False)
    monkeypatch.setattr(config, "JWT_SECRET", config.DEFAULT_JWT_SECRET)

    config.validate_security_config()  # no debe lanzar


def test_rechaza_la_clave_por_defecto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "IS_PRODUCTION", True)
    monkeypatch.setattr(config, "JWT_SECRET", config.DEFAULT_JWT_SECRET)

    with pytest.raises(RuntimeError):
        config.validate_security_config()


def test_rechaza_una_clave_corta(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "IS_PRODUCTION", True)
    monkeypatch.setattr(config, "JWT_SECRET", "corta")

    with pytest.raises(RuntimeError):
        config.validate_security_config()


def test_acepta_una_clave_fuerte(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "IS_PRODUCTION", True)
    monkeypatch.setattr(config, "JWT_SECRET", CLAVE_FUERTE)

    config.validate_security_config()  # no debe lanzar

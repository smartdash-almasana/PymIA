from __future__ import annotations

from pymia.mcp_server.first_clinical_interview import (
    TOOL_NAME,
    invoke_first_clinical_interview,
)
from pymia.mcp_server.server import build_app


def test_tool_name_is_versioned_contract() -> None:
    assert TOOL_NAME == "pymia.first_clinical_interview.v1"


def test_build_app_registers_without_import_errors() -> None:
    import pytest

    pytest.importorskip("mcp.server.fastmcp")
    app = build_app()
    assert app is not None


def test_ca01_first_contact_returns_taxonomic_framing() -> None:
    response = invoke_first_clinical_interview(
        tenant_id="tenant_ca01",
        channel="test",
        text="vendo mucho pero no se si gano plata",
        previous_progressive_context=None,
    )

    assert response["status"] == "ok"
    assert response["estado_conversacional"] == "encuadre_taxonomico_inicial"
    assert response["message"]
    assert "comercio" in response["message"].lower()
    assert response["anamnesis"]["hipotesis_iniciales"] == []
    assert response["laboratorio"]["evidencia_requerida"] == []
    assert response["progressive_context"]["business_identity"]["taxonomy_phase"] is None


def test_ca05_taxonomic_response_updates_progressive_context() -> None:
    previous = {
        "tenant_id": "tenant_ca05",
        "channel": "test",
        "business_identity": {
            "display_name": None,
            "country_code": None,
            "industry_hint": None,
            "taxonomy_phase": None,
        },
        "symptom_summary": ["incertidumbre de rentabilidad"],
        "documents_requested": [],
    }

    response = invoke_first_clinical_interview(
        tenant_id="tenant_ca05",
        channel="test",
        text="somos una distribuidora de alimentos, 12 empleados, vendemos a comercios",
        previous_progressive_context=previous,
    )

    identity = response["progressive_context"]["business_identity"]
    assert response["status"] == "ok"
    assert identity["industry_hint"] == "logistica/distribucion"
    assert identity["country_code"] == "AR"
    assert identity["taxonomy_phase"] == "FASE_0_IDENTIDAD"


def test_taxonomic_framing_does_not_request_evidence_or_diagnose() -> None:
    response = invoke_first_clinical_interview(
        tenant_id="tenant_no_diag",
        channel="test",
        text="hola, quiero entender mi negocio",
        previous_progressive_context=None,
    )

    forbidden_terms = (
        "margen erosionado",
        "tension de caja",
        "tensión de caja",
        "fuga operativa",
        "hipotesis",
        "hipótesis",
        "laboratorio",
        "incertidumbre de rentabilidad",
    )
    message = response["message"].lower()
    assert response["estado_conversacional"] == "encuadre_taxonomico_inicial"
    assert response["laboratorio"]["evidencia_requerida"] == []
    for term in forbidden_terms:
        assert term not in message


def test_tenant_isolation_violation_returns_error() -> None:
    response = invoke_first_clinical_interview(
        tenant_id="tenant_A",
        channel="test",
        text="vendo mucho",
        previous_progressive_context={
            "tenant_id": "tenant_B",
            "channel": "test",
            "business_identity": {"taxonomy_phase": "FASE_0_IDENTIDAD"},
            "symptom_summary": [],
            "documents_requested": [],
        },
    )

    assert response["status"] == "error"
    assert response["error_code"] == "TENANT_ISOLATION_VIOLATION"


def test_invalid_input_returns_error() -> None:
    response = invoke_first_clinical_interview(
        tenant_id="",
        channel="test",
        text="vendo mucho",
        previous_progressive_context=None,
    )

    assert response["status"] == "error"
    assert response["error_code"] == "INVALID_INPUT"

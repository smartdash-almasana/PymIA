from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_tool_result_v1 import (
    FIRST_AID_TOOL_RESULT_ALLOWED_STATUSES,
    FIRST_AID_TOOL_RESULT_DEFAULT_FORBIDDEN_CLAIMS,
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)


def test_build_first_aid_tool_result_ok_keeps_runtime_blocked() -> None:
    result = build_first_aid_tool_result_v1(
        tool_ref="precio_margen_basico",
        status="OK",
        inputs_used={"precio_venta": 100, "costo_unitario": 60},
        computed_results={"margen_bruto": 40},
        owner_summary="Hay un resultado preliminar, no un diagnostico.",
        limitations=["Resultado preliminar sujeto a evidencia declarada."],
        technical_notes=["No usar como rentabilidad confirmada."],
    )

    assert result["tool_ref"] == "precio_margen_basico"
    assert result["schema_version"] == "1.0"
    assert result["service_name"] == "SERVICE_1"
    assert result["status"] == "OK"
    assert result["computed_results"] == {"margen_bruto": 40}
    assert result["runtime_authorized"] is False


def test_build_missing_inputs_tool_result_sets_missing_inputs_status() -> None:
    result = build_missing_inputs_tool_result_v1(
        tool_ref="caja_diaria_triage",
        missing_inputs=["saldo_inicial", "egresos"],
        owner_summary="Faltan datos para una lectura prudente.",
        inputs_used={"ingresos": 1200},
    )

    assert result["status"] == "MISSING_INPUTS"
    assert result["missing_inputs"] == ["saldo_inicial", "egresos"]
    assert result["computed_results"] == {}
    assert result["runtime_authorized"] is False


def test_rejects_ok_without_computed_results() -> None:
    with pytest.raises(ValueError, match="requires computed_results"):
        build_first_aid_tool_result_v1(
            tool_ref="stock_alertas_basicas",
            status="OK",
            inputs_used={"stock_actual": 5},
            computed_results={},
            owner_summary="No alcanza para afirmar nada fuerte.",
        )


def test_preserves_conservative_forbidden_claims() -> None:
    result = build_first_aid_tool_result_v1(
        tool_ref="precio_margen_basico",
        status="BLOCKED",
        inputs_used={"precio_venta": 100},
        computed_results={},
        owner_summary="No corresponde concluir nada todavía.",
        forbidden_claims=["No confirma punto de equilibrio real."],
    )

    for claim in FIRST_AID_TOOL_RESULT_DEFAULT_FORBIDDEN_CLAIMS:
        assert claim in result["forbidden_claims"]

    assert "No confirma punto de equilibrio real." in result["forbidden_claims"]


def test_forbidden_claims_do_not_introduce_strong_business_claims() -> None:
    result = build_first_aid_tool_result_v1(
        tool_ref="caja_diaria_triage",
        status="INVALID_INPUT",
        inputs_used={"saldo_inicial": "texto"},
        computed_results={},
        owner_summary="Los datos no permiten una lectura prudente.",
    )

    forbidden_claims_blob = " ".join(result["forbidden_claims"]).lower()

    assert "diagnostico" in forbidden_claims_blob
    assert "rentabilidad real" in forbidden_claims_blob
    assert "saldo bancario real" in forbidden_claims_blob
    assert "conciliacion cerrada" in forbidden_claims_blob
    assert "archivo normalizado" in forbidden_claims_blob


def test_contract_module_does_not_depend_on_pipeline_fsm_llm_or_xlsx_delivery() -> None:
    import pymia.smartpyme.first_aid_tool_result_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "service_1_fsm_decision_patch_v1" not in source
    assert "service_1_boundary_chain_v1" not in source
    assert "document_ingestion" not in source
    assert "openpyxl" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_allowed_statuses_are_closed_and_validated() -> None:
    assert FIRST_AID_TOOL_RESULT_ALLOWED_STATUSES == (
        "OK",
        "MISSING_INPUTS",
        "BLOCKED",
        "INVALID_INPUT",
        "NOT_APPLICABLE",
    )

    with pytest.raises(ValueError, match="Unsupported FirstAidToolResultV1 status"):
        build_first_aid_tool_result_v1(  # type: ignore[arg-type]
            tool_ref="precio_margen_basico",
            status="UNEXPECTED_STATUS",
            inputs_used={},
            computed_results={},
            owner_summary="Estado inválido.",
        )


def test_helpers_do_not_mutate_inputs_by_reference() -> None:
    inputs_used = {"precio_venta": 100}
    computed_results = {"margen_bruto": 40}
    missing_inputs = ["costo_unitario"]
    limitations = ["Resultado preliminar."]
    forbidden_claims = ["No confirma escenario fiscal."]
    technical_notes = ["Mantener lectura prudente."]

    result = build_first_aid_tool_result_v1(
        tool_ref="precio_margen_basico",
        status="BLOCKED",
        inputs_used=inputs_used,
        computed_results=computed_results,
        missing_inputs=missing_inputs,
        limitations=limitations,
        forbidden_claims=forbidden_claims,
        owner_summary="Falta evidencia.",
        technical_notes=technical_notes,
    )

    result["inputs_used"]["precio_venta"] = 200
    result["computed_results"]["margen_bruto"] = 10
    result["missing_inputs"].append("precio_lista")
    result["limitations"].append("No confirma rentabilidad.")
    result["forbidden_claims"].append("No confirma EBITDA.")
    result["technical_notes"].append("Extra.")

    assert inputs_used == {"precio_venta": 100}
    assert computed_results == {"margen_bruto": 40}
    assert missing_inputs == ["costo_unitario"]
    assert limitations == ["Resultado preliminar."]
    assert forbidden_claims == ["No confirma escenario fiscal."]
    assert technical_notes == ["Mantener lectura prudente."]

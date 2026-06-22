from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_caja_diaria_triage_v1 import (
    REQUIRED_INPUTS,
    TOOL_REF,
    run_caja_diaria_triage_v1,
)


def test_ok_with_valid_inputs() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=500, egresos=300)

    assert result["tool_ref"] == TOOL_REF
    assert result["status"] == "OK"
    assert result["computed_results"]["flujo_neto"] == 200
    assert result["computed_results"]["saldo_final_estimado"] == 1200
    assert result["runtime_authorized"] is False


def test_missing_saldo_inicial_returns_missing_inputs() -> None:
    result = run_caja_diaria_triage_v1(ingresos=500, egresos=300)

    assert result["status"] == "MISSING_INPUTS"
    assert "saldo_inicial" in result["missing_inputs"]


def test_missing_ingresos_returns_missing_inputs() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=1000, egresos=300)

    assert result["status"] == "MISSING_INPUTS"
    assert "ingresos" in result["missing_inputs"]


def test_missing_egresos_returns_missing_inputs() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=500)

    assert result["status"] == "MISSING_INPUTS"
    assert "egresos" in result["missing_inputs"]


def test_non_numeric_input_returns_invalid_input() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial="texto", ingresos=500, egresos=300)

    assert result["status"] == "INVALID_INPUT"
    assert "must be numeric" in " ".join(result["technical_notes"])


def test_ingresos_negative_returns_invalid_input() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=-1, egresos=300)

    assert result["status"] == "INVALID_INPUT"
    assert "cannot be negative" in " ".join(result["technical_notes"])


def test_egresos_negative_returns_invalid_input() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=500, egresos=-1)

    assert result["status"] == "INVALID_INPUT"
    assert "cannot be negative" in " ".join(result["technical_notes"])


def test_negative_saldo_inicial_allowed() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=-500, ingresos=300, egresos=200)

    assert result["status"] == "OK"
    assert result["computed_results"]["flujo_neto"] == 100
    assert result["computed_results"]["saldo_final_estimado"] == -400


def test_forbidden_claims_remain_conservative() -> None:
    result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=500, egresos=300)
    forbidden_claims_blob = " ".join(result["forbidden_claims"]).lower()

    assert "saldo bancario real" in forbidden_claims_blob
    assert "conciliacion" in forbidden_claims_blob
    assert "archivo normalizado" in forbidden_claims_blob


def test_module_does_not_depend_on_pipeline_fsm_llm_or_xlsx_delivery() -> None:
    import pymia.smartpyme.first_aid_caja_diaria_triage_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "service_1_fsm_decision_patch_v1" not in source
    assert "service_1_boundary_chain_v1" not in source
    assert "document_ingestion" not in source
    assert "openpyxl" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_results_are_independent_across_calls() -> None:
    first_result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=500, egresos=300)
    second_result = run_caja_diaria_triage_v1(saldo_inicial=1000, ingresos=500, egresos=300)

    first_result["limitations"].append("Mutated externally.")
    first_result["computed_results"]["flujo_neto"] = -999

    assert second_result["limitations"] == [
        "No confirma saldo bancario real.",
        "No equivale a conciliacion.",
        "No valida efectivo fisico.",
        "No incluye movimientos no declarados.",
        "No reemplaza revision contable.",
    ]
    assert second_result["computed_results"]["flujo_neto"] == 200


def test_required_inputs_are_closed_for_this_tool() -> None:
    assert REQUIRED_INPUTS == ("saldo_inicial", "ingresos", "egresos")
    assert TOOL_REF == "caja_diaria_triage"

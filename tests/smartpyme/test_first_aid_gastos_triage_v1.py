from __future__ import annotations

import inspect

from pymia.smartpyme.first_aid_gastos_triage_v1 import (
    REQUIRED_INPUTS,
    TOOL_REF,
    run_gastos_triage_v1,
)


def test_ok_with_single_expense() -> None:
    result = run_gastos_triage_v1(concepto="alquiler", importe=1000, categoria="fijo")

    assert result["tool_ref"] == TOOL_REF
    assert result["status"] == "OK"
    assert result["computed_results"]["cantidad_gastos"] == 1
    assert result["computed_results"]["total_gastos"] == 1000
    assert result["computed_results"]["gastos_por_categoria"] == {"fijo": 1000}
    assert result["computed_results"]["gastos_sin_categoria"] == 0
    assert result["runtime_authorized"] is False


def test_ok_with_multiple_expenses_groups_by_category() -> None:
    result = run_gastos_triage_v1(
        concepto=["alquiler", "luz", "insumo"],
        importe=[1000, 200, 300],
        categoria=["fijo", "fijo", "variable"],
    )

    assert result["status"] == "OK"
    assert result["computed_results"]["cantidad_gastos"] == 3
    assert result["computed_results"]["total_gastos"] == 1500
    assert result["computed_results"]["gastos_por_categoria"] == {
        "fijo": 1200,
        "variable": 300,
    }


def test_missing_concepto_returns_missing_inputs() -> None:
    result = run_gastos_triage_v1(importe=1000)

    assert result["status"] == "MISSING_INPUTS"
    assert "concepto" in result["missing_inputs"]


def test_missing_importe_returns_missing_inputs() -> None:
    result = run_gastos_triage_v1(concepto="alquiler")

    assert result["status"] == "MISSING_INPUTS"
    assert "importe" in result["missing_inputs"]


def test_non_numeric_importe_returns_invalid_input() -> None:
    result = run_gastos_triage_v1(concepto="alquiler", importe="1000")

    assert result["status"] == "INVALID_INPUT"
    assert "importe must be numeric" in " ".join(result["technical_notes"])


def test_negative_importe_returns_invalid_input() -> None:
    result = run_gastos_triage_v1(concepto="alquiler", importe=-1)

    assert result["status"] == "INVALID_INPUT"
    assert "importe cannot be negative" in " ".join(result["technical_notes"])


def test_mismatched_sequence_lengths_return_invalid_input() -> None:
    result = run_gastos_triage_v1(concepto=["alquiler", "luz"], importe=[1000])

    assert result["status"] == "INVALID_INPUT"
    assert "same length" in " ".join(result["technical_notes"])


def test_missing_category_is_reported_as_uncategorized() -> None:
    result = run_gastos_triage_v1(concepto=["alquiler", "luz"], importe=[1000, 200])

    assert result["status"] == "OK"
    assert result["computed_results"]["gastos_sin_categoria"] == 2
    assert result["computed_results"]["gastos_por_categoria"] == {"sin_categoria": 1200}


def test_forbidden_claims_remain_conservative() -> None:
    result = run_gastos_triage_v1(concepto="alquiler", importe=1000)
    forbidden_claims_blob = " ".join(result["forbidden_claims"]).lower()
    limitations_blob = " ".join(result["limitations"]).lower()

    assert "diagnostico" in forbidden_claims_blob
    assert "archivo normalizado" in forbidden_claims_blob
    assert "clasifica gastos" in limitations_blob
    assert "audita gastos" in limitations_blob


def test_module_does_not_depend_on_pipeline_fsm_llm_or_xlsx_delivery() -> None:
    import pymia.smartpyme.first_aid_gastos_triage_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "service_1_fsm_decision_patch_v1" not in source
    assert "service_1_boundary_chain_v1" not in source
    assert "document_ingestion" not in source
    assert "openpyxl" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_results_are_independent_across_calls() -> None:
    first_result = run_gastos_triage_v1(concepto="alquiler", importe=1000)
    second_result = run_gastos_triage_v1(concepto="alquiler", importe=1000)

    first_result["limitations"].append("Mutated externally.")
    first_result["computed_results"]["total_gastos"] = -999

    assert second_result["computed_results"]["total_gastos"] == 1000
    assert "Mutated externally." not in second_result["limitations"]


def test_required_inputs_are_closed_for_this_tool() -> None:
    assert REQUIRED_INPUTS == ("concepto", "importe")
    assert TOOL_REF == "gastos_triage"

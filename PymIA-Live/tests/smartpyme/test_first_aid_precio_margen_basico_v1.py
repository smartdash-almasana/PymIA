from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_precio_margen_basico_v1 import (
    REQUIRED_INPUTS,
    TOOL_REF,
    run_precio_margen_basico_v1,
)


def test_ok_with_valid_price_and_cost() -> None:
    result = run_precio_margen_basico_v1(precio_venta=100, costo_unitario=60)

    assert result["tool_ref"] == TOOL_REF
    assert result["status"] == "OK"
    assert result["computed_results"]["margen_bruto_pesos"] == 40
    assert result["computed_results"]["margen_bruto_porcentaje"] == pytest.approx(0.4)
    assert result["computed_results"]["markup_porcentaje"] == pytest.approx(40 / 60)
    assert result["runtime_authorized"] is False


def test_missing_precio_venta_returns_missing_inputs() -> None:
    result = run_precio_margen_basico_v1(costo_unitario=60)

    assert result["status"] == "MISSING_INPUTS"
    assert result["missing_inputs"] == ["precio_venta"]


def test_missing_costo_unitario_returns_missing_inputs() -> None:
    result = run_precio_margen_basico_v1(precio_venta=100)

    assert result["status"] == "MISSING_INPUTS"
    assert result["missing_inputs"] == ["costo_unitario"]


def test_non_numeric_input_returns_invalid_input() -> None:
    result = run_precio_margen_basico_v1(precio_venta="texto", costo_unitario=60)

    assert result["status"] == "INVALID_INPUT"
    assert "must be numeric" in " ".join(result["technical_notes"])


def test_precio_venta_must_be_positive() -> None:
    result = run_precio_margen_basico_v1(precio_venta=0, costo_unitario=60)

    assert result["status"] == "INVALID_INPUT"
    assert "greater than 0" in " ".join(result["technical_notes"])


def test_costo_unitario_cannot_be_negative() -> None:
    result = run_precio_margen_basico_v1(precio_venta=100, costo_unitario=-1)

    assert result["status"] == "INVALID_INPUT"
    assert "cannot be negative" in " ".join(result["technical_notes"])


def test_zero_cost_keeps_ok_and_skips_markup() -> None:
    result = run_precio_margen_basico_v1(precio_venta=100, costo_unitario=0)

    assert result["status"] == "OK"
    assert result["computed_results"]["margen_bruto_pesos"] == 100
    assert result["computed_results"]["margen_bruto_porcentaje"] == pytest.approx(1.0)
    assert result["computed_results"]["markup_porcentaje"] is None
    assert "costo_unitario=0" in " ".join(result["limitations"])


def test_forbidden_claims_remain_conservative() -> None:
    result = run_precio_margen_basico_v1(precio_venta=100, costo_unitario=60)
    forbidden_claims_blob = " ".join(result["forbidden_claims"]).lower()

    assert "diagnostico" in forbidden_claims_blob
    assert "rentabilidad real" in forbidden_claims_blob
    assert "archivo normalizado" in forbidden_claims_blob
    assert "conciliacion" in forbidden_claims_blob


def test_module_does_not_depend_on_pipeline_fsm_llm_or_xlsx_delivery() -> None:
    import pymia.smartpyme.first_aid_precio_margen_basico_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "service_1_fsm_decision_patch_v1" not in source
    assert "service_1_boundary_chain_v1" not in source
    assert "document_ingestion" not in source
    assert "openpyxl" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_results_are_independent_across_calls() -> None:
    first_result = run_precio_margen_basico_v1(precio_venta=100, costo_unitario=60)
    second_result = run_precio_margen_basico_v1(precio_venta=100, costo_unitario=60)

    first_result["limitations"].append("Mutated externally.")
    first_result["computed_results"]["margen_bruto_pesos"] = -999

    assert second_result["limitations"] == [
        "No incluye impuestos.",
        "No incluye comisiones.",
        "No incluye costos fijos.",
        "No incluye costos indirectos.",
        "No reemplaza analisis contable.",
    ]
    assert second_result["computed_results"]["margen_bruto_pesos"] == 40


def test_required_inputs_are_closed_for_this_tool() -> None:
    assert REQUIRED_INPUTS == ("precio_venta", "costo_unitario")
    assert TOOL_REF == "precio_margen_basico"

from __future__ import annotations

import inspect

from pymia.smartpyme.first_aid_proveedores_precio_variacion_triage_v1 import (
    REQUIRED_INPUTS,
    TOOL_REF,
    run_proveedores_precio_variacion_triage_v1,
)


def test_ok_with_single_supplier_price() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor="Proveedor A",
        producto_o_insumo="Harina",
        precio_o_costo=1000,
    )

    assert result["tool_ref"] == TOOL_REF
    assert result["status"] == "OK"
    assert result["computed_results"]["cantidad_registros"] == 1
    assert result["computed_results"]["cantidad_productos_o_insumos"] == 1
    assert result["computed_results"]["productos_con_variacion_visible"] == 0
    assert result["runtime_authorized"] is False


def test_ok_with_multiple_supplier_prices_computes_visible_variation() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor=["Proveedor A", "Proveedor B", "Proveedor A"],
        producto_o_insumo=["Harina", "Harina", "Azucar"],
        precio_o_costo=[1000, 1250, 500],
    )

    harina = result["computed_results"]["variaciones_por_producto"]["Harina"]

    assert result["status"] == "OK"
    assert result["computed_results"]["cantidad_registros"] == 3
    assert result["computed_results"]["cantidad_productos_o_insumos"] == 2
    assert result["computed_results"]["productos_con_variacion_visible"] == 1
    assert harina["min_price"] == 1000
    assert harina["max_price"] == 1250
    assert harina["absolute_variation"] == 250
    assert harina["variation_percentage"] == 0.25
    assert harina["supplier_count"] == 2


def test_missing_proveedor_returns_missing_inputs() -> None:
    result = run_proveedores_precio_variacion_triage_v1(producto_o_insumo="Harina", precio_o_costo=1000)

    assert result["status"] == "MISSING_INPUTS"
    assert "proveedor" in result["missing_inputs"]


def test_missing_producto_returns_missing_inputs() -> None:
    result = run_proveedores_precio_variacion_triage_v1(proveedor="Proveedor A", precio_o_costo=1000)

    assert result["status"] == "MISSING_INPUTS"
    assert "producto_o_insumo" in result["missing_inputs"]


def test_missing_precio_returns_missing_inputs() -> None:
    result = run_proveedores_precio_variacion_triage_v1(proveedor="Proveedor A", producto_o_insumo="Harina")

    assert result["status"] == "MISSING_INPUTS"
    assert "precio_o_costo" in result["missing_inputs"]


def test_non_numeric_precio_returns_invalid_input() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor="Proveedor A",
        producto_o_insumo="Harina",
        precio_o_costo="1000",
    )

    assert result["status"] == "INVALID_INPUT"
    assert "precio_o_costo must be numeric" in " ".join(result["technical_notes"])


def test_negative_precio_returns_invalid_input() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor="Proveedor A",
        producto_o_insumo="Harina",
        precio_o_costo=-1,
    )

    assert result["status"] == "INVALID_INPUT"
    assert "precio_o_costo cannot be negative" in " ".join(result["technical_notes"])


def test_mismatched_sequence_lengths_return_invalid_input() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor=["Proveedor A", "Proveedor B"],
        producto_o_insumo=["Harina"],
        precio_o_costo=[1000, 1200],
    )

    assert result["status"] == "INVALID_INPUT"
    assert "same length" in " ".join(result["technical_notes"])


def test_zero_min_price_does_not_divide_by_zero() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor=["Proveedor A", "Proveedor B"],
        producto_o_insumo=["Harina", "Harina"],
        precio_o_costo=[0, 1200],
    )

    harina = result["computed_results"]["variaciones_por_producto"]["Harina"]

    assert result["status"] == "OK"
    assert harina["absolute_variation"] == 1200
    assert harina["variation_percentage"] is None


def test_forbidden_claims_remain_conservative() -> None:
    result = run_proveedores_precio_variacion_triage_v1(
        proveedor="Proveedor A",
        producto_o_insumo="Harina",
        precio_o_costo=1000,
    )
    forbidden_claims_blob = " ".join(result["forbidden_claims"]).lower()
    limitations_blob = " ".join(result["limitations"]).lower()

    assert "diagnostico" in forbidden_claims_blob
    assert "archivo normalizado" in forbidden_claims_blob
    assert "estrategia de compras" in limitations_blob
    assert "rentabilidad por proveedor" in limitations_blob


def test_module_does_not_depend_on_pipeline_fsm_llm_or_xlsx_delivery() -> None:
    import pymia.smartpyme.first_aid_proveedores_precio_variacion_triage_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "service_1_fsm_decision_patch_v1" not in source
    assert "service_1_boundary_chain_v1" not in source
    assert "document_ingestion" not in source
    assert "openpyxl" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_results_are_independent_across_calls() -> None:
    first_result = run_proveedores_precio_variacion_triage_v1(
        proveedor="Proveedor A",
        producto_o_insumo="Harina",
        precio_o_costo=1000,
    )
    second_result = run_proveedores_precio_variacion_triage_v1(
        proveedor="Proveedor A",
        producto_o_insumo="Harina",
        precio_o_costo=1000,
    )

    first_result["limitations"].append("Mutated externally.")
    first_result["computed_results"]["cantidad_registros"] = -999

    assert second_result["computed_results"]["cantidad_registros"] == 1
    assert "Mutated externally." not in second_result["limitations"]


def test_required_inputs_are_closed_for_this_tool() -> None:
    assert REQUIRED_INPUTS == ("proveedor", "producto_o_insumo", "precio_o_costo")
    assert TOOL_REF == "proveedores_precio_variacion_triage"

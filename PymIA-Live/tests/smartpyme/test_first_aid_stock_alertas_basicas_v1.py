from __future__ import annotations

import inspect

from pymia.smartpyme.first_aid_stock_alertas_basicas_v1 import (
    OPTIONAL_INPUTS,
    REQUIRED_INPUTS,
    TOOL_REF,
    run_stock_alertas_basicas_v1,
)


def test_ok_with_low_stock_and_no_sales_average() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=10,
    )

    assert result["status"] == "OK"
    assert result["computed_results"]["stock_bajo"] is True
    assert result["computed_results"]["diferencia_vs_minimo"] == -5
    assert result["computed_results"]["dias_stock_restante"] is None
    assert result["runtime_authorized"] is False


def test_ok_with_sufficient_stock() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=15,
        stock_minimo=10,
    )

    assert result["status"] == "OK"
    assert result["computed_results"]["stock_bajo"] is False
    assert result["computed_results"]["diferencia_vs_minimo"] == 5


def test_ok_with_daily_sales_average() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=20,
        stock_minimo=10,
        ventas_diarias_promedio=5,
    )

    assert result["status"] == "OK"
    assert result["computed_results"]["dias_stock_restante"] == 4


def test_zero_daily_sales_average_keeps_ok_with_explicit_limitation() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=20,
        stock_minimo=10,
        ventas_diarias_promedio=0,
    )

    assert result["status"] == "OK"
    assert result["computed_results"]["dias_stock_restante"] is None
    assert "ventas_diarias_promedio=0" in " ".join(result["limitations"])


def test_missing_producto_returns_missing_inputs() -> None:
    result = run_stock_alertas_basicas_v1(
        stock_actual=5,
        stock_minimo=10,
    )

    assert result["status"] == "MISSING_INPUTS"
    assert "producto" in result["missing_inputs"]


def test_blank_producto_returns_missing_inputs() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="   ",
        stock_actual=5,
        stock_minimo=10,
    )

    assert result["status"] == "MISSING_INPUTS"
    assert "producto" in result["missing_inputs"]


def test_missing_stock_actual_returns_missing_inputs() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_minimo=10,
    )

    assert result["status"] == "MISSING_INPUTS"
    assert "stock_actual" in result["missing_inputs"]


def test_missing_stock_minimo_returns_missing_inputs() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
    )

    assert result["status"] == "MISSING_INPUTS"
    assert "stock_minimo" in result["missing_inputs"]


def test_non_numeric_stock_actual_returns_invalid_input() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual="texto",
        stock_minimo=10,
    )

    assert result["status"] == "INVALID_INPUT"


def test_non_numeric_stock_minimo_returns_invalid_input() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo="texto",
    )

    assert result["status"] == "INVALID_INPUT"


def test_negative_stock_actual_returns_invalid_input() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=-1,
        stock_minimo=10,
    )

    assert result["status"] == "INVALID_INPUT"


def test_negative_stock_minimo_returns_invalid_input() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=-1,
    )

    assert result["status"] == "INVALID_INPUT"


def test_negative_daily_sales_average_returns_invalid_input() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=10,
        ventas_diarias_promedio=-1,
    )

    assert result["status"] == "INVALID_INPUT"


def test_non_numeric_daily_sales_average_returns_invalid_input() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=10,
        ventas_diarias_promedio="texto",
    )

    assert result["status"] == "INVALID_INPUT"


def test_conservative_claims_remain_visible() -> None:
    result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=10,
    )
    conservative_blob = " ".join(result["forbidden_claims"] + result["limitations"]).lower()

    assert "stock fisico real" in conservative_blob
    assert "quiebre de stock" in conservative_blob
    assert "rotacion real" in conservative_blob
    assert "archivo normalizado" in conservative_blob


def test_module_does_not_depend_on_pipeline_fsm_llm_or_xlsx_delivery() -> None:
    import pymia.smartpyme.first_aid_stock_alertas_basicas_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "service_1_fsm_decision_patch_v1" not in source
    assert "service_1_boundary_chain_v1" not in source
    assert "document_ingestion" not in source
    assert "openpyxl" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_results_are_independent_across_calls() -> None:
    first_result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=10,
    )
    second_result = run_stock_alertas_basicas_v1(
        producto="SKU-1",
        stock_actual=5,
        stock_minimo=10,
    )

    first_result["limitations"].append("Mutated externally.")
    first_result["computed_results"]["diferencia_vs_minimo"] = 999

    assert "Mutated externally." not in second_result["limitations"]
    assert second_result["computed_results"]["diferencia_vs_minimo"] == -5


def test_contract_constants_are_closed_for_this_tool() -> None:
    assert TOOL_REF == "stock_alertas_basicas"
    assert REQUIRED_INPUTS == ("producto", "stock_actual", "stock_minimo")
    assert OPTIONAL_INPUTS == ("ventas_diarias_promedio",)

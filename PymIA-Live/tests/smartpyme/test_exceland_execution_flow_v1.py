from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from pymia.smartpyme.exceland_execution_flow_v1 import (
    run_exceland_execution_flow_v1,
)


def _bridge_input(template_ref: str) -> dict:
    return {
        "requested_template_ref": template_ref,
        "requested_formula_refs": ["margen_bruto", "markup"],
        "input_fields_required": ["precio_venta", "costo_unitario"],
        "input_fields_received": {
            "precio_venta": 120,
            "costo_unitario": 80,
        },
        "warnings": [],
        "limitations": [],
    }


def test_success_precio_margen(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input=_bridge_input("precio_margen_basico_template"),
        output_dir=tmp_path,
    )

    assert result["status"] == "OK"
    assert result["bridge_status"] == "OK"
    assert result["runtime_status"] == "OK"
    assert result["requested_template_ref"] == "precio_margen_basico_template"
    assert result["product_ref"] == "precio_margen"
    assert result["artifact_exists"] is True
    assert result["runtime_authorized"] is False
    assert result["error_message"] is None

    output_path = Path(result["output_path"])
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_success_caja_diaria(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input={
            "requested_template_ref": "caja_diaria_template",
            "requested_formula_refs": ["flujo_caja_neto"],
            "input_fields_required": ["saldo_inicial", "ingresos", "egresos"],
            "input_fields_received": {
                "saldo_inicial": 1000,
                "ingresos": 500,
                "egresos": 300,
            },
            "warnings": [],
        },
        output_dir=tmp_path,
        output_filename="flow_caja.xlsx",
    )

    assert result["status"] == "OK"
    assert result["product_ref"] == "caja_diaria"
    assert Path(result["output_path"]).name == "flow_caja.xlsx"


def test_success_stock_control(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input={
            "requested_template_ref": "stock_alertas_basicas_template",
            "requested_formula_refs": ["alerta_stock_minimo"],
            "input_fields_required": ["producto", "stock_actual", "stock_minimo"],
            "input_fields_received": {
                "producto": "Yerba 1kg",
                "stock_actual": 8,
                "stock_minimo": 15,
            },
            "warnings": [],
        },
        output_dir=tmp_path,
    )

    assert result["status"] == "OK"
    assert result["product_ref"] == "stock_control"
    assert result["artifact_exists"] is True


def test_template_not_mapped_gastos_triage(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input=_bridge_input("gastos_triage_template"),
        output_dir=tmp_path,
    )

    assert result["status"] == "TEMPLATE_NOT_MAPPED"
    assert result["bridge_status"] == "OK"
    assert result["runtime_status"] is None
    assert result["artifact_exists"] is False
    assert "no mapped" in result["error_message"]


def test_template_not_mapped_proveedores(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input=_bridge_input("proveedores_precio_variacion_template"),
        output_dir=tmp_path,
    )

    assert result["status"] == "TEMPLATE_NOT_MAPPED"
    assert result["product_ref"] is None


def test_bridge_not_ok_blocks_runtime(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input={
            "requested_template_ref": None,
            "requested_formula_refs": [],
            "input_fields_required": [],
            "input_fields_received": {},
        },
        output_dir=tmp_path,
    )

    assert result["status"] == "BRIDGE_NOT_OK"
    assert result["runtime_status"] is None
    assert result["artifact_exists"] is False
    assert result["product_ref"] is None


def test_bridge_unknown_template_blocks_runtime(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input=_bridge_input("plantilla_fantasma"),
        output_dir=tmp_path,
    )

    assert result["status"] == "BRIDGE_NOT_OK"
    assert result["bridge_status"] == "UNKNOWN_TEMPLATE"


def test_invalid_bridge_input(tmp_path: Path) -> None:
    result = run_exceland_execution_flow_v1(
        bridge_input="not_a_dict",  # type: ignore[arg-type]
        output_dir=tmp_path,
    )

    assert result["status"] == "INVALID_INPUT"
    assert result["bridge_status"] == "INVALID_INPUT"
    assert result["error_message"] is not None


def test_runtime_authorized_always_false(tmp_path: Path) -> None:
    for template_ref in (
        "precio_margen_basico_template",
        "caja_diaria_template",
        "stock_alertas_basicas_template",
    ):
        result = run_exceland_execution_flow_v1(
            bridge_input=_bridge_input(template_ref),
            output_dir=tmp_path,
        )
        assert result["runtime_authorized"] is False, (
            f"runtime_authorized must be False for template_ref={template_ref}"
        )


def test_module_has_no_forbidden_imports() -> None:
    import pymia.smartpyme.exceland_execution_flow_v1 as module

    source = inspect.getsource(module)

    assert "service_1_pipeline" not in source
    assert "service_1_xlsx_delivery" not in source
    assert "diagnostic_core" not in source
    assert "cli" not in source
    assert "fsm" not in source.lower()
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()
    assert "first_aid" not in source

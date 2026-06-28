from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_caja_diaria_triage_v1 import run_caja_diaria_triage_v1
from pymia.smartpyme.first_aid_precio_margen_basico_v1 import run_precio_margen_basico_v1
from pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 import (
    build_service_1_manual_first_aid_delivery_flow_v1,
)
from pymia.smartpyme.service_1_post_tool_owner_delivery_summary_v1 import (
    SUMMARY_FILENAME,
    render_service_1_post_tool_owner_delivery_summary_v1,
)


def _packet(tmp_path):
    tool_results = [
        run_precio_margen_basico_v1(precio_venta=1000, costo_unitario=600),
        run_precio_margen_basico_v1(precio_venta=1200),
        run_caja_diaria_triage_v1(saldo_inicial=0, ingresos=5000, egresos=4200),
    ]
    flow = build_service_1_manual_first_aid_delivery_flow_v1(
        tool_results=tool_results,
        output_dir=tmp_path,
    )
    return {
        "service_name": "SERVICE_1",
        "asset": {
            "filename": "cafeteria_demo.xlsx",
        },
        "detected_structure": {
            "workbook": {
                "sheets": [
                    {"name": "ventas_detalle"},
                    {"name": "caja_diaria"},
                ]
            },
            "runtime_authorized": False,
        },
        "pipeline_result": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "requested_tool_count": 3,
            "executed_tool_refs": [result["tool_ref"] for result in tool_results],
            "tool_results": tool_results,
            "delivery_flow": flow,
            "runtime_authorized": False,
            "notes": [],
        },
        "runtime_authorized": False,
    }


def test_renders_post_tool_owner_summary_with_real_tool_statuses(tmp_path) -> None:
    summary = render_service_1_post_tool_owner_delivery_summary_v1(_packet(tmp_path))

    assert summary.startswith("# Entrega PymIA — Servicio 1")
    assert "cafeteria_demo.xlsx" in summary
    assert "Herramientas aplicadas: **3**" in summary
    assert "Resultados OK: **2**" in summary
    assert "Datos faltantes: **1**" in summary
    assert "costo_unitario" in summary
    assert "precio_margen_basico" in summary
    assert "caja_diaria_triage" in summary
    assert "first_aid_001_precio_margen_basico.xlsx" in summary
    assert SUMMARY_FILENAME == "post_tool_owner_delivery_summary.md"


def test_summary_does_not_repeat_initial_intake_contradiction(tmp_path) -> None:
    summary = render_service_1_post_tool_owner_delivery_summary_v1(_packet(tmp_path))
    lowered = summary.lower()

    assert "no calcula margenes" not in lowered
    assert "no calcula márgenes" not in lowered
    assert "no calcula caja" not in lowered
    assert "cálculos preliminares" in lowered
    assert "archivos xlsx" in lowered


def test_summary_preserves_conservative_claim_boundaries(tmp_path) -> None:
    summary = render_service_1_post_tool_owner_delivery_summary_v1(_packet(tmp_path))
    lowered = summary.lower()

    assert "no es auditoría" in lowered
    assert "no es certificación" in lowered
    assert "no es conciliación bancaria definitiva" in lowered
    assert "no confirma rentabilidad real" in lowered
    assert "no reemplaza al contador" in lowered
    assert "revisión humana requerida" in lowered

    for forbidden_positive in [
        "rentabilidad real confirmada",
        "conciliación cerrada",
        "saldo real confirmado",
        "cierre contable",
        "cierre fiscal",
        "sí reemplaza al contador",
    ]:
        assert forbidden_positive not in lowered


def test_rejects_missing_pipeline_result() -> None:
    with pytest.raises(ValueError, match="pipeline_result must be a dict"):
        render_service_1_post_tool_owner_delivery_summary_v1({})


def test_rejects_runtime_authorized_pipeline(tmp_path) -> None:
    packet = _packet(tmp_path)
    packet["pipeline_result"]["runtime_authorized"] = True

    with pytest.raises(ValueError, match="requires runtime_authorized=False"):
        render_service_1_post_tool_owner_delivery_summary_v1(packet)


def test_module_is_pure_summary_layer_not_runtime_or_io() -> None:
    import pymia.smartpyme.service_1_post_tool_owner_delivery_summary_v1 as module

    source = inspect.getsource(module)

    assert "openpyxl" not in source
    assert "Path" not in source
    assert ".write_text" not in source
    assert "run_precio_margen" not in source
    assert "run_caja" not in source
    assert "vertical_pipeline" not in source
    assert "service_2" not in source
    assert "openai" not in source.lower()
    assert "chatbot" not in source.lower()

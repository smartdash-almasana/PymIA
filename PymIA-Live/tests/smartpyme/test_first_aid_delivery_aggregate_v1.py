from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_delivery_aggregate_v1 import (
    AGGREGATE_SCHEMA_VERSION,
    SERVICE_NAME,
    build_first_aid_delivery_aggregate_v1,
)
from pymia.smartpyme.first_aid_tool_result_v1 import (
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)


def test_aggregates_single_ok_tool_result() -> None:
    tool_result = build_first_aid_tool_result_v1(
        tool_ref="precio_margen_basico",
        status="OK",
        inputs_used={"precio_venta": 100, "costo_unitario": 60},
        computed_results={"margen_bruto_pesos": 40},
        limitations=["No incluye impuestos."],
        owner_summary="Calculo preliminar.",
        technical_notes=["Tool scope is limited to deterministic math over explicit inputs."],
    )

    aggregate = build_first_aid_delivery_aggregate_v1([tool_result])

    assert aggregate["schema_version"] == AGGREGATE_SCHEMA_VERSION
    assert aggregate["service_name"] == SERVICE_NAME
    assert aggregate["tool_count"] == 1
    assert aggregate["tool_refs"] == ["precio_margen_basico"]
    assert aggregate["statuses"] == ["OK"]


def test_aggregates_multiple_ok_results() -> None:
    first = build_first_aid_tool_result_v1(
        tool_ref="precio_margen_basico",
        status="OK",
        inputs_used={"precio_venta": 100, "costo_unitario": 60},
        computed_results={"margen_bruto_pesos": 40},
        limitations=["No incluye impuestos."],
        owner_summary="Calculo preliminar.",
        technical_notes=["Deterministic math only."],
    )
    second = build_first_aid_tool_result_v1(
        tool_ref="caja_diaria_triage",
        status="OK",
        inputs_used={"saldo_inicial": 100, "ingresos": 50, "egresos": 20},
        computed_results={"flujo_neto": 30},
        limitations=["No confirma saldo bancario real."],
        owner_summary="Caja preliminar.",
        technical_notes=["Deterministic math only."],
    )

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["tool_count"] == 2
    assert len(aggregate["results"]) == 2


def test_preserves_order_of_tool_refs() -> None:
    first = _ok_result("tool_a", {"a": 1})
    second = _ok_result("tool_b", {"b": 2})

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["tool_refs"] == ["tool_a", "tool_b"]


def test_preserves_order_of_statuses() -> None:
    first = build_missing_inputs_tool_result_v1(
        tool_ref="tool_a",
        missing_inputs=["x"],
        owner_summary="Faltan datos.",
    )
    second = _ok_result("tool_b", {"b": 2})

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["statuses"] == ["MISSING_INPUTS", "OK"]


def test_includes_results_per_tool_with_expected_fields() -> None:
    tool_result = build_missing_inputs_tool_result_v1(
        tool_ref="stock_alertas_basicas",
        missing_inputs=["stock_minimo"],
        owner_summary="Falta stock minimo.",
        inputs_used={"producto": "SKU-1", "stock_actual": 5},
    )

    aggregate = build_first_aid_delivery_aggregate_v1([tool_result])

    assert aggregate["results"] == [
        {
            "tool_ref": "stock_alertas_basicas",
            "status": "MISSING_INPUTS",
            "owner_summary": "Falta stock minimo.",
            "inputs_used": {"producto": "SKU-1", "stock_actual": 5},
            "computed_results": {},
            "missing_inputs": ["stock_minimo"],
        }
    ]


def test_aggregates_missing_inputs_by_tool() -> None:
    first = build_missing_inputs_tool_result_v1(
        tool_ref="tool_a",
        missing_inputs=["x"],
        owner_summary="Falta x.",
    )
    second = build_missing_inputs_tool_result_v1(
        tool_ref="tool_b",
        missing_inputs=["y", "z"],
        owner_summary="Faltan y z.",
    )

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["missing_inputs"] == [
        {"tool_ref": "tool_a", "missing_inputs": ["x"]},
        {"tool_ref": "tool_b", "missing_inputs": ["y", "z"]},
    ]


def test_aggregates_limitations_without_exact_duplicates() -> None:
    first = _ok_result("tool_a", {"a": 1}, limitations=["L1", "L2"])
    second = _ok_result("tool_b", {"b": 2}, limitations=["L2", "L3"])

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["limitations"] == ["L1", "L2", "L3"]


def test_aggregates_forbidden_claims_without_exact_duplicates() -> None:
    first = _ok_result("tool_a", {"a": 1}, forbidden_claims=["C1", "C2"])
    second = _ok_result("tool_b", {"b": 2}, forbidden_claims=["C2", "C3"])

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["forbidden_claims"] == ["No es un diagnostico integral de la empresa.", "No confirma rentabilidad real.", "No confirma saldo bancario real.", "No confirma stock fisico real.", "No confirma conciliacion cerrada.", "No confirma archivo normalizado.", "C1", "C2", "C3"]


def test_aggregates_technical_notes_without_exact_duplicates() -> None:
    first = _ok_result("tool_a", {"a": 1}, technical_notes=["N1", "N2"])
    second = _ok_result("tool_b", {"b": 2}, technical_notes=["N2", "N3"])

    aggregate = build_first_aid_delivery_aggregate_v1([first, second])

    assert aggregate["technical_notes"] == ["N1", "N2", "N3"]


def test_rejects_empty_list() -> None:
    with pytest.raises(ValueError, match="requires at least one tool result"):
        build_first_aid_delivery_aggregate_v1([])


def test_rejects_runtime_authorized_result() -> None:
    tool_result = _ok_result("tool_a", {"a": 1})
    tool_result["runtime_authorized"] = True

    with pytest.raises(ValueError, match="does not accept runtime_authorized=True"):
        build_first_aid_delivery_aggregate_v1([tool_result])


def test_aggregate_id_is_deterministic() -> None:
    first = _ok_result("tool_a", {"a": 1}, limitations=["L1"])
    second = _ok_result("tool_b", {"b": 2}, technical_notes=["N1"])

    left = build_first_aid_delivery_aggregate_v1([first, second])
    right = build_first_aid_delivery_aggregate_v1([first, second])

    assert left["aggregate_id"] == right["aggregate_id"]


def test_runtime_authorized_is_false_on_aggregate() -> None:
    aggregate = build_first_aid_delivery_aggregate_v1([_ok_result("tool_a", {"a": 1})])

    assert aggregate["runtime_authorized"] is False


def test_module_does_not_import_concrete_tools() -> None:
    import pymia.smartpyme.first_aid_delivery_aggregate_v1 as module

    source = inspect.getsource(module)

    assert "first_aid_precio_margen_basico_v1" not in source
    assert "first_aid_caja_diaria_triage_v1" not in source
    assert "first_aid_stock_alertas_basicas_v1" not in source
    assert "run_" not in source


def test_module_does_not_depend_on_pipeline_fsm_llm_chatbot_document_ingestion_excelsystems_or_openpyxl() -> None:
    import pymia.smartpyme.first_aid_delivery_aggregate_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "fsm" not in source.lower()
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()
    assert "document_ingestion" not in source
    assert "exceland" not in source.lower()
    assert "openpyxl" not in source.lower()


def test_module_does_not_generate_xlsx() -> None:
    import pymia.smartpyme.first_aid_delivery_aggregate_v1 as module

    source = inspect.getsource(module)

    assert "Workbook" not in source
    assert ".xlsx" not in source.lower()
    assert "build_first_aid_xlsx_delivery_v1" not in source


def _ok_result(
    tool_ref: str,
    computed_results: dict[str, object],
    *,
    limitations: list[str] | None = None,
    forbidden_claims: list[str] | None = None,
    technical_notes: list[str] | None = None,
) -> dict[str, object]:
    return build_first_aid_tool_result_v1(
        tool_ref=tool_ref,
        status="OK",
        inputs_used={"input_ref": tool_ref},
        computed_results=computed_results,
        limitations=limitations,
        forbidden_claims=forbidden_claims,
        owner_summary=f"Resumen {tool_ref}.",
        technical_notes=technical_notes,
    )

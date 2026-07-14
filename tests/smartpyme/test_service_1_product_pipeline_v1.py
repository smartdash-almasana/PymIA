from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_NEEDS_OWNER,
    STATUS_READY,
    run_service_1_product_pipeline_v1,
)


def _clear_ingestion() -> dict:
    return {
        "case_id": "case_product_pipeline",
        "source_kind": "xlsx",
        "filename": "ventas.xlsx",
        "columns": ["fecha", "monto"],
        "input_values": {
            "fecha": "fecha de la operación",
            "monto": "importe total de la operación",
        },
        "runtime_authorized": False,
    }


def _ambiguous_ingestion() -> dict:
    return {
        "case_id": "case_product_pipeline_owner",
        "source_kind": "xlsx",
        "filename": "ambiguous.xlsx",
        "columns": ["valor"],
        "input_values": {"valor": "dato del negocio"},
        "runtime_authorized": False,
    }


def _tool_requests() -> list[dict]:
    return [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {"precio_venta": 120, "costo_unitario": 80},
        }
    ]


def _assert_closed(packet: dict) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False


def test_confirmed_semantics_execute_existing_physical_pipeline(tmp_path: Path) -> None:
    first = run_service_1_product_pipeline_v1(
        ingestion_output=_clear_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
        sheet_name="Ventas",
    )
    owner_answers = {
        question["column_name"]: question["candidate_roles"][0]
        for question in first["owner_questions"]
    }
    out = run_service_1_product_pipeline_v1(
        ingestion_output=_clear_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
        sheet_name="Ventas",
        owner_answers=owner_answers,
    )

    assert out["status"] == STATUS_READY
    assert out["semantic_bindings_confirmed"] is True
    assert out["tools_executed"] is True
    assert out["physical_run"]["executed_tool_refs"] == ["precio_margen_basico"]
    assert out["physical_run"]["delivery_flow"]["deliveries"]
    _assert_closed(out)


def test_owner_questions_block_before_any_tool_or_delivery(tmp_path: Path) -> None:
    out = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
    )

    assert out["status"] == STATUS_NEEDS_OWNER
    assert out["owner_questions"]
    assert out["physical_run"] is None
    assert out["tools_executed"] is False
    assert list(tmp_path.iterdir()) == []
    _assert_closed(out)


def test_owner_reentry_can_unlock_physical_execution(tmp_path: Path) -> None:
    first = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
    )
    question = first["owner_questions"][0]
    answer = question["allowed_answers"][0]

    out = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
        owner_answers={question["column_name"]: answer},
    )

    assert out["status"] == STATUS_READY
    assert out["semantic_bindings_confirmed"] is True
    assert out["tools_executed"] is True
    _assert_closed(out)


def test_invalid_semantic_input_blocks_without_execution(tmp_path: Path) -> None:
    out = run_service_1_product_pipeline_v1(
        ingestion_output=None,
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
    )

    assert out["status"] == STATUS_BLOCKED
    assert out["blocked_reason"] == "INGESTION_OUTPUT_NOT_DICT"
    assert out["physical_run"] is None
    assert list(tmp_path.iterdir()) == []
    _assert_closed(out)


def _cash_collection_ingestion() -> dict:
    return {
        "case_id": "case_product_cash_plan",
        "source_kind": "xlsx",
        "filename": "ventas_cobros.xlsx",
        "columns": ["fecha", "venta_total", "cobrado"],
        "input_values": {
            "fecha": "fecha de la operación",
            "venta_total": "importe total vendido",
            "cobrado": "importe efectivamente cobrado",
        },
        "column_evidence": {
            "fecha": {
                "sample_values": ["2026-06-01", "2026-06-02"],
                "inferred_type": "date",
            },
            "venta_total": {
                "sample_values": [1000, 2000],
                "inferred_type": "number",
            },
            "cobrado": {
                "sample_values": [800, 1500],
                "inferred_type": "number",
            },
        },
        "runtime_authorized": False,
    }


def test_product_root_builds_plan_without_executing_tools(tmp_path: Path) -> None:
    first = run_service_1_product_pipeline_v1(
        ingestion_output=_cash_collection_ingestion(),
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="sold_vs_collected_gap",
        sheet_name="Ventas",
    )
    answers = {
        question["column_name"]: (
            "collected_amount"
            if "collected_amount" in question["allowed_answers"]
            else next(
                item
                for item in question["allowed_answers"]
                if item != "IGNORED_NOT_RELEVANT"
            )
        )
        for question in first["owner_questions"]
    }
    out = run_service_1_product_pipeline_v1(
        ingestion_output=_cash_collection_ingestion(),
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="sold_vs_collected_gap",
        owner_answers=answers,
        sheet_name="Ventas",
    )

    assert out["status"] == STATUS_COMPUTATION_PLAN_READY
    assert out["semantic_bindings_confirmed"] is True
    assert out["computation_plan"]["status"] == "READY_FOR_COMPUTATION"
    assert out["computation_plan"]["formula_id"] == "LIQ_001_vendido_cobrado"
    assert out["physical_run"] is None
    assert out["tools_executed"] is False
    assert list(tmp_path.iterdir()) == []
    _assert_closed(out)

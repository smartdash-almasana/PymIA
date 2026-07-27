from __future__ import annotations

import json

from pathlib import Path

from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_NEEDS_OWNER,
    STATUS_READY,
    run_service_1_product_pipeline_v1,
)



def _first_semantic_option_id(question: dict) -> str:
    return next(
        item["option_id"]
        for item in question["options"]
        if item["option_id"] not in {"OTHER", "IGNORE"}
    )


def _option_id_for_label(question: dict, expected_text: str) -> str:
    expected = expected_text.lower()
    for item in question["options"]:
        if item["option_id"] in {"OTHER", "IGNORE"}:
            continue
        if expected and expected in item["label"].lower():
            return item["option_id"]
    return _first_semantic_option_id(question)


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
        "column_evidence": {
            "valor": {"sample_values": [100, 200], "inferred_type": "number"}
        },
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
        question["column_name"]: _first_semantic_option_id(question)
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
    rendered = json.dumps(out["owner_questions"], ensure_ascii=False)
    for internal_token in (
        "unit_sale_price",
        "unit_cost_candidate",
        "tax_amount",
        "IGNORED_NOT_RELEVANT",
    ):
        assert internal_token not in rendered
    assert all(question["options"] for question in out["owner_questions"])
    assert set(out["semantic_run"]) == {
        "schema_version",
        "service_name",
        "status",
        "blocked_reason",
        "owner_questions",
        "owner_followup",
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    }
    assert "gate_packet" not in out["semantic_run"]
    assert "bridge_packet" not in out["semantic_run"]
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
    answer = _first_semantic_option_id(question)

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
    preferred_labels = {
        "fecha": "fecha",
        "venta_total": "venta total",
        "cobrado": "cobrado",
    }
    answers = {
        question["column_name"]: _option_id_for_label(
            question, preferred_labels.get(question["column_name"], "")
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
    assert out["governed_computation_input"]["schema_version"] == "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1"
    assert out["computability_decision"]["status"] == "COMPUTABLE"
    assert "computation_plan" not in out
    assert out["governed_computation_input"]["formula_id"] == "LIQ_001_vendido_cobrado"
    assert out["physical_run"] is None
    assert out["tools_executed"] is False
    assert list(tmp_path.iterdir()) == []
    _assert_closed(out)

def test_other_free_text_never_executes_tools(tmp_path: Path) -> None:
    first = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
    )
    question = first["owner_questions"][0]

    out = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
        owner_answers={
            question["column_name"]: {
                "option_id": "OTHER",
                "free_text": "Es un indicador interno distinto.",
            }
        },
    )

    assert out["status"] == STATUS_NEEDS_OWNER
    assert out["semantic_bindings_confirmed"] is False
    assert out["tools_executed"] is False
    assert out["physical_run"] is None
    assert out["owner_followup"][0]["normalization_required"] is True
    assert list(tmp_path.iterdir()) == []
    _assert_closed(out)


def test_ignore_all_blocks_without_execution(tmp_path: Path) -> None:
    first = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
    )
    question = first["owner_questions"][0]

    out = run_service_1_product_pipeline_v1(
        ingestion_output=_ambiguous_ingestion(),
        tool_requests=_tool_requests(),
        output_dir=tmp_path,
        owner_answers={question["column_name"]: "IGNORE"},
    )

    assert out["status"] == STATUS_BLOCKED
    assert out["blocked_reason"] == "NO_ACTIVE_SEMANTIC_CANDIDATES"
    assert out["tools_executed"] is False
    assert out["physical_run"] is None
    assert list(tmp_path.iterdir()) == []
    _assert_closed(out)

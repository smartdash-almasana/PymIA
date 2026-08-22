from __future__ import annotations

from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_BLOCKED_PIPELINE,
    STATUS_CONFIRMED_BINDINGS,
    STATUS_OWNER_FOLLOWUP,
    STATUS_OWNER_QUESTIONS,
    run_initial_pass,
    run_owner_reentry,
)



def _first_semantic_option_id(question: dict) -> str:
    return next(
        item["option_id"]
        for item in question["options"]
        if item["option_id"] not in {"OTHER", "IGNORE"}
    )


def _column_refs(*columns: str, sheet: str = "Ventas") -> list[dict]:
    return [
        {
            "field_id": column,
            "question_id": column,
            "sheet_name": sheet,
            "column_name": column,
            "normalized_column_name": column,
        }
        for column in columns
    ]


def _ingestion_output() -> dict:
    return {
        "case_id": "case_pipeline_v1",
        "source_kind": "xlsx",
        "filename": "ventas.xlsx",
        "columns": ["fecha", "monto"],
        "column_refs": _column_refs("fecha", "monto"),
        "input_values": {
            "fecha": "fecha de la operación",
            "monto": "importe total de la operación",
        },
        "runtime_authorized": False,
    }


def _assert_closed(packet: dict) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False


def test_initial_pass_composes_bridge_and_gate() -> None:
    out = run_initial_pass(ingestion_output=_ingestion_output(), sheet_name="Ventas")
    assert out["status"] in {STATUS_OWNER_QUESTIONS, STATUS_CONFIRMED_BINDINGS}
    assert out["bridge_packet"]["status"] == "SEMANTIC_CANDIDATES_READY"
    assert out["gate_packet"] is not None
    _assert_closed(out)


def test_owner_question_round_trip_reaches_confirmed_bindings_when_needed() -> None:
    first = run_initial_pass(ingestion_output=_ingestion_output(), sheet_name="Ventas")
    if first["status"] == STATUS_CONFIRMED_BINDINGS:
        assert first["confirmed_candidate"] is not None
        return

    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in first["owner_questions"]
    }
    out = run_owner_reentry(previous_run=first, owner_answers=answers)
    assert out["status"] == STATUS_CONFIRMED_BINDINGS
    assert out["confirmed_candidate"] is not None
    assert out["reentry_packet"]["reinjected_columns"]
    _assert_closed(out)


def test_invalid_initial_input_blocks() -> None:
    out = run_initial_pass(ingestion_output=None)
    assert out["status"] == STATUS_BLOCKED_PIPELINE
    assert out["blocked_reason"] == "INGESTION_OUTPUT_NOT_DICT"
    _assert_closed(out)


def test_reentry_requires_valid_previous_run() -> None:
    out = run_owner_reentry(previous_run={}, owner_answers={"x": "y"})
    assert out["status"] == STATUS_BLOCKED_PIPELINE
    assert out["blocked_reason"] == "INVALID_PREVIOUS_RUN"
    _assert_closed(out)


def test_reentry_requires_answers() -> None:
    first = run_initial_pass(
        ingestion_output={
            "case_id": "case_owner",
            "source_kind": "xlsx",
            "filename": "ambiguous.xlsx",
            "columns": ["valor"],
            "column_refs": _column_refs("valor"),
            "input_values": {"valor": "dato del negocio"},
        }
    )
    assert first["status"] == STATUS_OWNER_QUESTIONS
    out = run_owner_reentry(previous_run=first, owner_answers={})
    assert out["status"] == STATUS_BLOCKED_PIPELINE
    assert out["blocked_reason"] == "OWNER_ANSWERS_REQUIRED"
    _assert_closed(out)

def test_other_owner_answer_never_creates_semantic_truth() -> None:
    first = run_initial_pass(
        ingestion_output={
            "case_id": "case_other",
            "source_kind": "xlsx",
            "filename": "ambiguous.xlsx",
            "columns": ["valor"],
            "column_refs": _column_refs("valor"),
            "input_values": {"valor": "dato del negocio"},
            "column_evidence": {
                "valor": {"sample_values": [100, 200], "inferred_type": "number"}
            },
        },
        sheet_name="Ventas",
    )
    assert first["status"] == STATUS_OWNER_QUESTIONS
    question = first["owner_questions"][0]

    out = run_owner_reentry(
        previous_run=first,
        owner_answers={
            question["column_name"]: {
                "option_id": "OTHER",
                "free_text": "Es un dato interno no catalogado.",
            }
        },
    )

    assert out["status"] == STATUS_OWNER_FOLLOWUP
    assert out["confirmed_candidate"] is None
    assert out["reentry_packet"] is None
    assert out["owner_followup"][0]["normalization_required"] is True
    _assert_closed(out)

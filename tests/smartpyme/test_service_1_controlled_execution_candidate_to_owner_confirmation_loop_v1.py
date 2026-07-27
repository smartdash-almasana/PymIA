"""
Audit tests for SERVICE_1_CONTROLLED_EXECUTION_CANDIDATE_TO_OWNER_CONFIRMATION_LOOP_V1.

Scope: owner-confirmation loop only (controlled execution gate output ->
confirmation questions / recheck-ready). These tests do NOT execute tools, do
NOT authorize runtime/product/delivery/diagnosis, and do NOT create delivery.
The full-chain tests use real fixtures; the READY path uses a synthetic gate.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1 as build_intake,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1 as build_conn,
)
from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_bridge,
)
from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    STATUS_NEEDS_OWNER_CONFIRMATION as GATE_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY as GATE_READY,
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    BLOCK_ANSWERS_NOT_DICT,
    BLOCK_CONFLICTING_OWNER_ANSWER,
    BLOCK_EMPTY_ANSWERS,
    BLOCK_INVALID_OPTION_ID,
    BLOCK_GATE_BLOCKED,
    BLOCK_GATE_FLAGS_FORBIDDEN,
    BLOCK_GATE_NOT_DICT,
    BLOCK_MISSING_ANSWERS,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    BLOCK_UNKNOWN_ANSWERS,
    STATUS_ALREADY_READY,
    STATUS_OWNER_CONFIRMATION_RECHECK_READY,
    STATUS_OWNER_CONFIRMATION_REQUIRED,
    STATUS_OWNER_FOLLOWUP_REQUIRED,
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1 as build_loop,
)

# --- Fixture resolution ---------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT_ROOT = _REPO_ROOT.parent

_AMBIGUOUS_XLSX_CANDIDATES = [
    _REPO_ROOT / "prueba_excels" / "cafeteria_abc.xlsx",
    _PARENT_ROOT / "prueba_excels" / "cafeteria_abc.xlsx",
]


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip(f"No fixture found among: {[str(c) for c in candidates]}")



def _first_semantic_option_id(question: dict) -> str:
    return next(
        item["option_id"]
        for item in question["options"]
        if item["option_id"] not in {"OTHER", "IGNORE"}
    )


def _assert_all_flags_false(packet: dict) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False


@pytest.fixture()
def case_001_gate_packet() -> dict:
    fixture = _first_existing(_AMBIGUOUS_XLSX_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    bridge = build_bridge(ingestion_output=connector["ingestion_output"])
    gate = build_gate(semantic_bridge_packet=bridge)
    assert gate["status"] == GATE_NEEDS_OWNER_CONFIRMATION
    presentation = build_loop(gate_packet=gate)
    assert presentation["status"] == STATUS_OWNER_CONFIRMATION_REQUIRED
    return {
        **gate,
        "owner_questions": presentation["owner_questions"],
        "owner_answer_bindings": presentation["owner_answer_bindings"],
    }


def _synthetic_ready_gate() -> dict:
    return {
        "status": GATE_READY,
        "case_id": "case_synth",
        "source_kind": "local_path",
        "filename": "synthetic.xlsx",
        "controlled_execution_candidate": {"candidate_columns": ["fecha"]},
        "owner_questions": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


# --- 1. Full chain CASE_001 -> loop without answers -----------------------

def test_case_001_loop_owner_confirmation_required(case_001_gate_packet: dict) -> None:
    out = build_loop(gate_packet=case_001_gate_packet)

    assert out["status"] == STATUS_OWNER_CONFIRMATION_REQUIRED
    assert out["owner_questions"], "expected non-empty owner questions"
    assert out["owner_question_count"] == len(out["owner_questions"])
    _assert_all_flags_false(out)


# --- 2. CASE_001 + complete answers -> recheck ready ----------------------

def test_case_001_complete_answers_recheck_ready(case_001_gate_packet: dict) -> None:
    questions = case_001_gate_packet["owner_questions"]
    pending = [q["column_name"] for q in questions]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in questions
    }

    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)

    assert out["status"] == STATUS_OWNER_CONFIRMATION_RECHECK_READY
    assert set(out["confirmed_answers"].keys()) == set(pending)
    assert len(out["owner_confirmation_events"]) == len(pending)
    assert {event["question_ref"] for event in out["owner_confirmation_events"]} == set(pending)
    assert all(event["confirmed_by_owner"] is True for event in out["owner_confirmation_events"])
    assert all(event["confirmation_scope"] == "SEMANTIC_ROLE" for event in out["owner_confirmation_events"])
    for column, option_id in answers.items():
        assert out["confirmed_answers"][column] == (
            case_001_gate_packet["owner_answer_bindings"][column][option_id]
        )
    _assert_all_flags_false(out)


# --- 3. Synthetic ready gate -> ALREADY_READY -----------------------------

def test_synthetic_ready_gate_already_ready() -> None:
    out = build_loop(gate_packet=_synthetic_ready_gate())
    assert out["status"] == STATUS_ALREADY_READY
    assert out["owner_questions"] == []
    _assert_all_flags_false(out)


# --- 4. Blocks ------------------------------------------------------------

@pytest.mark.parametrize(
    "flag",
    [
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    ],
)
def test_block_request_flags_true(case_001_gate_packet: dict, flag: str) -> None:
    out = build_loop(**{"gate_packet": case_001_gate_packet, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_all_flags_false(out)


def test_block_gate_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_loop(gate_packet=bad)
        assert out["blocked_reason"] == BLOCK_GATE_NOT_DICT
        _assert_all_flags_false(out)


def test_block_gate_flags_true(case_001_gate_packet: dict) -> None:
    tainted = dict(case_001_gate_packet)
    tainted["runtime_authorized"] = True
    out = build_loop(gate_packet=tainted)
    assert out["blocked_reason"] == BLOCK_GATE_FLAGS_FORBIDDEN


def test_block_gate_blocked() -> None:
    out = build_loop(gate_packet={"status": "BLOCKED"})
    assert out["blocked_reason"] == BLOCK_GATE_BLOCKED


def test_block_answers_not_dict(case_001_gate_packet: dict) -> None:
    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=["a", "b"])
    assert out["blocked_reason"] == BLOCK_ANSWERS_NOT_DICT


def test_block_missing_answers(case_001_gate_packet: dict) -> None:
    pending = [q["column_name"] for q in case_001_gate_packet["owner_questions"]]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in case_001_gate_packet["owner_questions"]
    }
    answers.pop(pending[0])
    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)
    assert out["blocked_reason"] == BLOCK_MISSING_ANSWERS


def test_block_unknown_answers(case_001_gate_packet: dict) -> None:
    pending = [q["column_name"] for q in case_001_gate_packet["owner_questions"]]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in case_001_gate_packet["owner_questions"]
    }
    answers["ZZZ_no_pending"] = "A"
    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)
    assert out["blocked_reason"] == BLOCK_UNKNOWN_ANSWERS


def test_block_empty_answers(case_001_gate_packet: dict) -> None:
    pending = [q["column_name"] for q in case_001_gate_packet["owner_questions"]]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in case_001_gate_packet["owner_questions"]
    }
    answers[pending[0]] = "   "  # whitespace-only -> empty
    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)
    assert out["blocked_reason"] == BLOCK_EMPTY_ANSWERS


# --- 5. Stability ---------------------------------------------------------

def test_deterministic_same_input(case_001_gate_packet: dict) -> None:
    a = build_loop(gate_packet=case_001_gate_packet)
    b = build_loop(gate_packet=case_001_gate_packet)
    assert a == b


def test_does_not_mutate_gate_packet(case_001_gate_packet: dict) -> None:
    before_keys = set(case_001_gate_packet.keys())
    before_status = case_001_gate_packet["status"]
    before_questions = len(case_001_gate_packet["owner_questions"])
    build_loop(gate_packet=case_001_gate_packet)
    assert set(case_001_gate_packet.keys()) == before_keys
    assert case_001_gate_packet["status"] == before_status
    assert len(case_001_gate_packet["owner_questions"]) == before_questions

def test_invalid_option_id_blocks(case_001_gate_packet: dict) -> None:
    questions = case_001_gate_packet["owner_questions"]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in questions
    }
    answers[questions[0]["column_name"]] = "NOT_AN_OPTION"

    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)

    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_INVALID_OPTION_ID
    assert out["confirmed_answers"] == {}
    _assert_all_flags_false(out)


def test_other_option_routes_to_fail_closed_followup(case_001_gate_packet: dict) -> None:
    questions = case_001_gate_packet["owner_questions"]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in questions
    }
    column = questions[0]["column_name"]
    answers[column] = {
        "option_id": "OTHER",
        "free_text": "Es un indicador interno distinto.",
    }

    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)

    assert out["status"] == STATUS_OWNER_FOLLOWUP_REQUIRED
    assert out["confirmed_answers"] == {}
    assert out["owner_followup"] == [
        {
            "column_name": column,
            "option_id": "OTHER",
            "owner_free_text": "Es un indicador interno distinto.",
            "normalization_required": True,
        }
    ]
    assert out["owner_questions"][0]["answer_type"] == "semantic_normalization_required"
    _assert_all_flags_false(out)


def test_other_without_text_requests_owner_free_text(case_001_gate_packet: dict) -> None:
    questions = case_001_gate_packet["owner_questions"]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in questions
    }
    column = questions[0]["column_name"]
    answers[column] = "OTHER"

    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)

    assert out["status"] == STATUS_OWNER_FOLLOWUP_REQUIRED
    assert out["confirmed_answers"] == {}
    assert out["owner_followup"][0]["owner_free_text"] is None
    assert out["owner_questions"][0]["answer_type"] == "owner_free_text"
    _assert_all_flags_false(out)


def test_free_text_with_semantic_option_blocks_as_conflicting(
    case_001_gate_packet: dict,
) -> None:
    questions = case_001_gate_packet["owner_questions"]
    answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in questions
    }
    column = questions[0]["column_name"]
    answers[column] = {
        "option_id": _first_semantic_option_id(questions[0]),
        "free_text": "Pero significa otra cosa.",
    }

    out = build_loop(gate_packet=case_001_gate_packet, owner_answers=answers)

    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_CONFLICTING_OWNER_ANSWER
    assert out["confirmed_answers"] == {}
    _assert_all_flags_false(out)

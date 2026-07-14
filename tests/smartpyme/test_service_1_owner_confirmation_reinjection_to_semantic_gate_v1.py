"""
Audit tests for SERVICE_1_OWNER_CONFIRMATION_REINJECTION_TO_SEMANTIC_GATE_V1.

Scope: connector only (semantic bridge + owner confirmation loop ->
re-applied candidates -> re-run controlled execution gate). These tests do NOT
execute tools, do NOT authorize runtime/product/delivery/diagnosis, and do NOT
create delivery. Full-chain tests use real fixtures.
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
    STATUS_READY as BRIDGE_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_bridge,
)
from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    STATUS_OWNER_CONFIRMATION_RECHECK_READY,
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1 as build_loop,
)
from pymia.smartpyme.service_1_owner_confirmation_reinjection_to_semantic_gate_v1 import (
    BLOCK_BRIDGE_NOT_DICT,
    BLOCK_BRIDGE_WRONG_STATUS,
    BLOCK_EMPTY_ANSWERS,
    BLOCK_LOOP_NO_ANSWERS,
    BLOCK_LOOP_NOT_DICT,
    BLOCK_LOOP_WRONG_STATUS,
    BLOCK_MISSING_ANSWERS,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    BLOCK_UNKNOWN_ANSWERS,
    STATUS_READY,
    build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1 as build_reinject,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT_ROOT = _REPO_ROOT.parent

_CASE_001_CANDIDATES = [
    _PARENT_ROOT / "prueba_excels" / "cafeteria_abc.xlsx",
    _REPO_ROOT / "prueba_excels" / "cafeteria_abc.xlsx",
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
def case_001_chain() -> dict:
    """Returns a real ambiguous cafeteria bridge plus canonical reentry answers."""
    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    bridge = build_bridge(ingestion_output=connector["ingestion_output"])
    assert bridge["status"] == BRIDGE_READY
    gate = build_gate(semantic_bridge_packet=bridge)
    assert gate["status"] == "NEEDS_OWNER_CONFIRMATION"
    canonical_answers = {
        question["column_name"]: _first_semantic_option_id(question)
        for question in gate["owner_questions"]
    }
    loop = build_loop(gate_packet=gate, owner_answers=canonical_answers)
    assert loop["status"] == STATUS_OWNER_CONFIRMATION_RECHECK_READY
    return {"bridge": bridge, "loop": loop}


# --- 1. Full chain -> reinjection -> READY --------------------------------

def test_case_001_reinject_then_gate_ready(case_001_chain: dict) -> None:
    bridge_snapshot = {
        "status": case_001_chain["bridge"]["status"],
        "count": case_001_chain["bridge"]["column_candidate_count"],
    }
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=case_001_chain["loop"],
    )

    assert out["status"] == STATUS_READY
    assert out["semantic_candidate_count"] == 11  # cafeteria fixture lock
    assert "operation_date" in out["candidate_roles"]
    assert out["variable_family_count"] == 5
    assert len(out["variable_family_bindings"]) == 5
    assert isinstance(out["ready_variable_family_ids"], list)
    # Input bridge must NOT be mutated.
    assert case_001_chain["bridge"]["status"] == bridge_snapshot["status"]
    assert case_001_chain["bridge"]["column_candidate_count"] == bridge_snapshot["count"]
    _assert_all_flags_false(out)


def test_reinjected_candidates_marked_confirmed(case_001_chain: dict) -> None:
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=case_001_chain["loop"],
    )
    assert out["status"] == STATUS_READY
    # Every column the loop confirmed must appear in reinjected_columns.
    expected = sorted(case_001_chain["loop"]["confirmed_answers"].keys())
    assert sorted(out["reinjected_columns"]) == expected
    # The bridge must still carry the original candidate objects unchanged.
    for c in case_001_chain["bridge"]["column_candidates"]:
        if getattr(c, "owner_confirmation_required", False):
            # Original pending candidate was NOT mutated.
            assert c.metadata.get("owner_confirmed") is None
            assert "owner_confirmation_answer" not in (c.metadata or {})


# --- 2. Blocks ------------------------------------------------------------

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
def test_block_request_flags_true(case_001_chain: dict, flag: str) -> None:
    out = build_reinject(
        **{
            "semantic_bridge_packet": case_001_chain["bridge"],
            "owner_confirmation_loop_packet": case_001_chain["loop"],
            flag: True,
        }
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_all_flags_false(out)


def test_block_bridge_not_dict(case_001_chain: dict) -> None:
    out = build_reinject(
        semantic_bridge_packet=None,
        owner_confirmation_loop_packet=case_001_chain["loop"],
    )
    assert out["blocked_reason"] == BLOCK_BRIDGE_NOT_DICT


def test_block_loop_not_dict(case_001_chain: dict) -> None:
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=None,
    )
    assert out["blocked_reason"] == BLOCK_LOOP_NOT_DICT


def test_block_bridge_wrong_status(case_001_chain: dict) -> None:
    bad_bridge = dict(case_001_chain["bridge"])
    bad_bridge["status"] = "BLOCKED"
    out = build_reinject(
        semantic_bridge_packet=bad_bridge,
        owner_confirmation_loop_packet=case_001_chain["loop"],
    )
    assert out["blocked_reason"] == BLOCK_BRIDGE_WRONG_STATUS


def test_block_loop_wrong_status(case_001_chain: dict) -> None:
    bad_loop = dict(case_001_chain["loop"])
    bad_loop["status"] = "OWNER_CONFIRMATION_REQUIRED"
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=bad_loop,
    )
    assert out["blocked_reason"] == BLOCK_LOOP_WRONG_STATUS


def test_block_loop_no_answers(case_001_chain: dict) -> None:
    no_answers = dict(case_001_chain["loop"])
    no_answers["confirmed_answers"] = {}
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=no_answers,
    )
    assert out["blocked_reason"] == BLOCK_LOOP_NO_ANSWERS


def test_block_unknown_answers(case_001_chain: dict) -> None:
    loop = dict(case_001_chain["loop"])
    loop["confirmed_answers"] = dict(loop["confirmed_answers"])
    loop["confirmed_answers"]["ZZZ_no_column"] = "x"
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=loop,
    )
    assert out["blocked_reason"] == BLOCK_UNKNOWN_ANSWERS


def test_block_empty_answers(case_001_chain: dict) -> None:
    loop = dict(case_001_chain["loop"])
    answers = dict(loop["confirmed_answers"])
    first = next(iter(answers))
    answers[first] = "   "
    loop["confirmed_answers"] = answers
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=loop,
    )
    assert out["blocked_reason"] == BLOCK_EMPTY_ANSWERS


def test_block_missing_answers(case_001_chain: dict) -> None:
    loop = dict(case_001_chain["loop"])
    answers = dict(loop["confirmed_answers"])
    first = next(iter(answers))
    del answers[first]
    loop["confirmed_answers"] = answers
    out = build_reinject(
        semantic_bridge_packet=case_001_chain["bridge"],
        owner_confirmation_loop_packet=loop,
    )
    expected = (
        BLOCK_LOOP_NO_ANSWERS
        if not answers
        else BLOCK_MISSING_ANSWERS
    )
    assert out["blocked_reason"] == expected


# --- helper removed: re-packed bridge is internal to the connector ---

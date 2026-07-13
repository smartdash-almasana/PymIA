"""
Audit tests for SERVICE_1_DRY_RUN_CANDIDATE_TO_OWNER_VALIDATION_DIALOGUE_V1.

Scope: owner-validation dialogue only (READY dry-run candidate -> validation
dialogue). These tests do NOT execute tools, do NOT authorize
runtime/product/delivery/diagnosis, and do NOT create delivery. Full-chain
tests use real fixtures so the dry-run candidate reaches
CONTROLLED_DRY_RUN_CANDIDATE_READY.
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
    STATUS_READY as GATE_READY,
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    STATUS_OWNER_CONFIRMATION_RECHECK_READY,
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1 as build_loop,
)
from pymia.smartpyme.service_1_controlled_execution_ready_to_plan_packet_v1 import (
    STATUS_PLAN_READY as PLAN_READY,
    build_service_1_controlled_execution_plan_packet_v1 as build_plan,
)
from pymia.smartpyme.service_1_plan_packet_to_owner_authorization_dialogue_v1 import (
    AUTH_ACCEPT,
    STATUS_ACCEPTED as DIALOGUE_STATUS_ACCEPTED,
    build_service_1_owner_authorization_dialogue_from_plan_packet_v1 as build_dialogue,
)
from pymia.smartpyme.service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 import (
    STATUS_READY as CANDIDATE_READY,
    build_service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 as build_candidate,
)
from pymia.smartpyme.service_1_dry_run_candidate_to_owner_validation_dialogue_v1 import (
    BLOCK_INPUT_FLAGS_FORBIDDEN,
    BLOCK_INPUT_NOT_DICT,
    BLOCK_MISSING_ANALYSIS,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    BLOCK_WRONG_STATUS,
    STATUS_ACCEPTED,
    STATUS_REJECTED,
    STATUS_REQUIRED,
    STATUS_REQUEST_CHANGES,
    VALIDATION_ACCEPT,
    VALIDATION_REJECT,
    VALIDATION_REQUEST_CHANGES,
    build_service_1_owner_validation_dialogue_from_dry_run_candidate_v1 as build_validation,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT_ROOT = _REPO_ROOT.parent

_CASE_001_CANDIDATES = [
    _PARENT_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
    _REPO_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
]


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip(f"No fixture found among: {[str(c) for c in candidates]}")


def _assert_controlled_flags(packet: dict) -> None:
    assert packet["dry_run_evaluated"] is True
    assert packet["execution_executed"] is False
    assert packet["delivery_created"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False


@pytest.fixture()
def case_001_dry_run_candidate() -> dict:
    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    bridge = build_bridge(ingestion_output=connector["ingestion_output"])
    assert bridge["status"] == BRIDGE_READY
    gate = build_gate(semantic_bridge_packet=bridge)
    assert gate["status"] == GATE_READY
    ready_gate = gate
    plan = build_plan(gate_packet=ready_gate)
    assert plan["status"] == PLAN_READY
    dialogue = build_dialogue(plan_packet=plan, owner_authorization=AUTH_ACCEPT)
    assert dialogue["status"] == DIALOGUE_STATUS_ACCEPTED
    candidate = build_candidate(owner_authorization_dialogue_packet=dialogue)
    assert candidate["status"] == CANDIDATE_READY
    return candidate


# --- 1. Full chain -> validation dialogue ---------------------------------

def test_case_001_candidate_requires_validation(case_001_dry_run_candidate: dict) -> None:
    out = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate)
    assert out["status"] == STATUS_REQUIRED
    assert out["validation_decision"] == STATUS_REQUIRED
    assert out["analysis"] == case_001_dry_run_candidate["analysis"]
    assert "operation_date" in out["roles"]
    _assert_controlled_flags(out)


def test_case_001_candidate_accept(case_001_dry_run_candidate: dict) -> None:
    out = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate, owner_validation=VALIDATION_ACCEPT)
    assert out["status"] == STATUS_ACCEPTED
    assert out["validation_decision"] == STATUS_ACCEPTED
    _assert_controlled_flags(out)


def test_case_001_candidate_reject(case_001_dry_run_candidate: dict) -> None:
    out = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate, owner_validation=VALIDATION_REJECT)
    assert out["status"] == STATUS_REJECTED
    assert out["validation_decision"] == STATUS_REJECTED
    _assert_controlled_flags(out)


def test_case_001_candidate_request_changes(case_001_dry_run_candidate: dict) -> None:
    out = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate, owner_validation=VALIDATION_REQUEST_CHANGES)
    assert out["status"] == STATUS_REQUEST_CHANGES
    assert out["validation_decision"] == STATUS_REQUEST_CHANGES
    _assert_controlled_flags(out)


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
def test_block_request_flags_true(case_001_dry_run_candidate: dict, flag: str) -> None:
    out = build_validation(**{"dry_run_candidate_packet": case_001_dry_run_candidate, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_controlled_flags(out)


def test_block_input_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_validation(dry_run_candidate_packet=bad)
        assert out["blocked_reason"] == BLOCK_INPUT_NOT_DICT
        _assert_controlled_flags(out)


def test_block_wrong_status() -> None:
    out = build_validation(dry_run_candidate_packet={"status": "BLOCKED", "analysis": [{"step": 1}]})
    assert out["blocked_reason"] == BLOCK_WRONG_STATUS


def test_block_input_flags_true(case_001_dry_run_candidate: dict) -> None:
    tainted = dict(case_001_dry_run_candidate)
    tainted["runtime_authorized"] = True
    out = build_validation(dry_run_candidate_packet=tainted)
    assert out["blocked_reason"] == BLOCK_INPUT_FLAGS_FORBIDDEN


def test_block_missing_analysis(case_001_dry_run_candidate: dict) -> None:
    bad = dict(case_001_dry_run_candidate)
    bad.pop("analysis", None)
    out = build_validation(dry_run_candidate_packet=bad)
    assert out["blocked_reason"] == BLOCK_MISSING_ANALYSIS


def test_unknown_validation_answer_blocks(case_001_dry_run_candidate: dict) -> None:
    out = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate, owner_validation="maybe")
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_WRONG_STATUS


# --- 3. Stability ---------------------------------------------------------

def test_deterministic_same_input(case_001_dry_run_candidate: dict) -> None:
    a = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate)
    b = build_validation(dry_run_candidate_packet=case_001_dry_run_candidate)
    assert a == b


def test_does_not_mutate_candidate(case_001_dry_run_candidate: dict) -> None:
    before_status = case_001_dry_run_candidate["status"]
    before_analysis = list(case_001_dry_run_candidate["analysis"])
    build_validation(dry_run_candidate_packet=case_001_dry_run_candidate)
    assert case_001_dry_run_candidate["status"] == before_status
    assert list(case_001_dry_run_candidate["analysis"]) == before_analysis

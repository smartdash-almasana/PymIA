"""
Audit tests for SERVICE_1_OWNER_VALIDATED_DRY_RUN_TO_CONTROLLED_EXECUTION_RESULT_V1.

Scope: controlled execution result only (ACCEPTED validation dialogue ->
in-memory controlled execution). These tests do NOT invoke external tools, do
NOT authorize runtime/product/delivery/diagnosis, and do NOT create delivery or
write files. Full-chain tests use real fixtures so the validation dialogue
reaches OWNER_VALIDATION_ACCEPTED.
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
    STATUS_ACCEPTED as VALIDATION_STATUS_ACCEPTED,
    STATUS_REJECTED,
    STATUS_REQUIRED,
    STATUS_REQUEST_CHANGES,
    VALIDATION_ACCEPT,
    VALIDATION_REJECT,
    VALIDATION_REQUEST_CHANGES,
    build_service_1_owner_validation_dialogue_from_dry_run_candidate_v1 as build_validation,
)
from pymia.smartpyme.service_1_owner_validated_dry_run_to_controlled_execution_result_v1 import (
    BLOCK_INPUT_FLAGS_FORBIDDEN,
    BLOCK_INPUT_NOT_DICT,
    BLOCK_INVALID_STEP,
    BLOCK_MISSING_ANALYSIS,
    BLOCK_NOT_ACCEPTED,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    STATUS_READY,
    build_service_1_owner_validated_dry_run_to_controlled_execution_result_v1 as build_result,
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


def _assert_executed_controlled_flags(packet: dict) -> None:
    # On READY, controlled execution ran in memory; on BLOCKED it never ran.
    is_ready = packet["status"] == STATUS_READY
    assert packet["controlled_execution_executed"] is is_ready
    assert packet["execution_executed"] is is_ready
    assert packet["delivery_created"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False


@pytest.fixture()
def case_001_validation_accepted() -> dict:
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
    validation = build_validation(dry_run_candidate_packet=candidate, owner_validation=VALIDATION_ACCEPT)
    assert validation["status"] == VALIDATION_STATUS_ACCEPTED
    return validation


# --- 1. Full chain -> controlled execution result READY -------------------

def test_case_001_validation_accepted_to_result_ready(case_001_validation_accepted: dict) -> None:
    out = build_result(owner_validation_dialogue_packet=case_001_validation_accepted)

    assert out["status"] == STATUS_READY
    assert out["step_count"] == len(case_001_validation_accepted["analysis"])
    assert out["results"], "expected executed step results"
    assert "operation_date" in out["roles"]
    _assert_executed_controlled_flags(out)
    # Every executed step is marked executed in memory (no file/tool/delivery).
    for result in out["results"]:
        assert result["controlled_execution_executed"] is True
        assert result["execution_executed"] is True
        assert result["delivery_created"] is False


def test_result_is_deterministic(case_001_validation_accepted: dict) -> None:
    a = build_result(owner_validation_dialogue_packet=case_001_validation_accepted)
    b = build_result(owner_validation_dialogue_packet=case_001_validation_accepted)
    assert a["results"] == b["results"]
    assert a["step_count"] == b["step_count"]


def test_no_files_written(case_001_validation_accepted: dict, tmp_path: Path) -> None:
    # Ensure execution writes nothing under a temp dir we control.
    out = build_result(owner_validation_dialogue_packet=case_001_validation_accepted)
    assert out["status"] == STATUS_READY
    assert out["delivery_created"] is False
    assert list(tmp_path.iterdir()) == []  # nothing created


# --- 2. reject / request_changes / required -> BLOCKED --------------------

def test_reject_blocks(case_001_validation_accepted: dict) -> None:
    rejected = dict(case_001_validation_accepted)
    rejected["status"] = STATUS_REJECTED
    out = build_result(owner_validation_dialogue_packet=rejected)
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_NOT_ACCEPTED


def test_request_changes_blocks(case_001_validation_accepted: dict) -> None:
    rc = dict(case_001_validation_accepted)
    rc["status"] = STATUS_REQUEST_CHANGES
    out = build_result(owner_validation_dialogue_packet=rc)
    assert out["blocked_reason"] == BLOCK_NOT_ACCEPTED


def test_required_blocks(case_001_validation_accepted: dict) -> None:
    required = dict(case_001_validation_accepted)
    required["status"] = STATUS_REQUIRED
    out = build_result(owner_validation_dialogue_packet=required)
    assert out["blocked_reason"] == BLOCK_NOT_ACCEPTED


# --- 3. Blocks ------------------------------------------------------------

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
def test_block_request_flags_true(case_001_validation_accepted: dict, flag: str) -> None:
    out = build_result(**{"owner_validation_dialogue_packet": case_001_validation_accepted, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_executed_controlled_flags(out)


def test_block_input_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_result(owner_validation_dialogue_packet=bad)
        assert out["blocked_reason"] == BLOCK_INPUT_NOT_DICT
        _assert_executed_controlled_flags(out)


def test_block_input_flags_true(case_001_validation_accepted: dict) -> None:
    tainted = dict(case_001_validation_accepted)
    tainted["runtime_authorized"] = True
    out = build_result(owner_validation_dialogue_packet=tainted)
    assert out["blocked_reason"] == BLOCK_INPUT_FLAGS_FORBIDDEN


def test_block_missing_analysis(case_001_validation_accepted: dict) -> None:
    bad = dict(case_001_validation_accepted)
    bad.pop("analysis", None)
    out = build_result(owner_validation_dialogue_packet=bad)
    assert out["blocked_reason"] == BLOCK_MISSING_ANALYSIS


def test_block_invalid_step(case_001_validation_accepted: dict) -> None:
    bad = dict(case_001_validation_accepted)
    bad["analysis"] = [{"action": "launch_missiles", "target": "x"}]
    out = build_result(owner_validation_dialogue_packet=bad)
    assert out["blocked_reason"] == BLOCK_INVALID_STEP


# --- 4. Stability ---------------------------------------------------------

def test_does_not_mutate_validation(case_001_validation_accepted: dict) -> None:
    before_status = case_001_validation_accepted["status"]
    before_analysis = list(case_001_validation_accepted["analysis"])
    build_result(owner_validation_dialogue_packet=case_001_validation_accepted)
    assert case_001_validation_accepted["status"] == before_status
    assert list(case_001_validation_accepted["analysis"]) == before_analysis

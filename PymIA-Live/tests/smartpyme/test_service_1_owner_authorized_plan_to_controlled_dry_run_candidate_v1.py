"""
Audit tests for SERVICE_1_OWNER_AUTHORIZED_PLAN_TO_CONTROLLED_DRY_RUN_CANDIDATE_V1.

Scope: controlled dry-run candidate only (ACCEPTED authorization dialogue ->
deterministic analysis candidate). These tests do NOT execute external tools,
do NOT authorize runtime/product/delivery/diagnosis, and do NOT create
delivery. Full-chain tests use real fixtures so the dialogue reaches
OWNER_AUTHORIZATION_ACCEPTED.
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
    AUTH_REJECT,
    STATUS_ACCEPTED,
    STATUS_REJECTED,
    STATUS_REQUIRED,
    build_service_1_owner_authorization_dialogue_from_plan_packet_v1 as build_dialogue,
)
from pymia.smartpyme.service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 import (
    BLOCK_INPUT_FLAGS_FORBIDDEN,
    BLOCK_INPUT_NOT_DICT,
    BLOCK_INVALID_STEP,
    BLOCK_MISSING_PLANNED_STEPS,
    BLOCK_NOT_ACCEPTED,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    STATUS_READY,
    build_service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 as build_dry_run,
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
    # Controlled flags: no real execution, no delivery, no authorization.
    assert packet["execution_executed"] is False
    assert packet["delivery_created"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    # On a BLOCKED packet no analysis ran; on READY dry_run_evaluated is True.
    assert packet["dry_run_evaluated"] is (packet["status"] == STATUS_READY)


def _assert_no_result_or_executed_wording(packet: dict) -> None:
    """No 'result' or 'executed' wording in packet keys except execution_executed."""
    for key in packet:
        key_lower = key.lower()
        assert "result" not in key_lower, f"packet key '{key}' contains 'result'"
        if key == "execution_executed":
            continue
        assert "executed" not in key_lower, f"packet key '{key}' contains 'executed'"
    # Status string must not contain 'result'.
    assert "result" not in packet["status"].lower(), "status contains 'result'"
    # Step analysis entries must also be clean.
    for entry in packet.get("analysis", []):
        for key in entry:
            key_lower = key.lower()
            assert "result" not in key_lower, f"analysis key '{key}' contains 'result'"
            if key == "execution_executed":
                continue
            assert "executed" not in key_lower, f"analysis key '{key}' contains 'executed'"


@pytest.fixture()
def case_001_accepted_dialogue() -> dict:
    from dataclasses import replace

    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    bridge = build_bridge(ingestion_output=connector["ingestion_output"])
    assert bridge["status"] == BRIDGE_READY
    gate = build_gate(semantic_bridge_packet=bridge)
    assert gate["status"] == "NEEDS_OWNER_CONFIRMATION"
    pending = [q["column_name"] for q in gate["owner_questions"]]
    loop = build_loop(gate_packet=gate, owner_answers={c: f"rol {c}" for c in pending})
    assert loop["status"] == STATUS_OWNER_CONFIRMATION_RECHECK_READY

    re_candidates = []
    for c in bridge["column_candidates"]:
        column = str(c.source_column_name).strip()
        if column in loop["confirmed_answers"] and getattr(c, "owner_confirmation_required", False):
            md = dict(c.metadata or {})
            md["owner_confirmed"] = True
            re_candidates.append(replace(c, owner_confirmation_required=False, metadata=md))
        else:
            re_candidates.append(c)
    re_bridge = dict(bridge)
    re_bridge["column_candidates"] = tuple(re_candidates)
    re_bridge.pop("semantic_candidate_count", None)

    ready_gate = build_gate(semantic_bridge_packet=re_bridge)
    assert ready_gate["status"] == GATE_READY
    plan = build_plan(gate_packet=ready_gate)
    assert plan["status"] == PLAN_READY
    dialogue = build_dialogue(plan_packet=plan, owner_authorization=AUTH_ACCEPT)
    assert dialogue["status"] == STATUS_ACCEPTED
    return dialogue


# --- 1. Full chain -> dry-run candidate READY ------------------------------

def test_case_001_accept_to_dry_run_candidate_ready(case_001_accepted_dialogue: dict) -> None:
    out = build_dry_run(owner_authorization_dialogue_packet=case_001_accepted_dialogue)

    assert out["status"] == STATUS_READY
    assert out["step_count"] == len(case_001_accepted_dialogue["planned_steps"])
    assert out["analysis"], "expected analysis entries"
    assert "operation_date" in out["roles"]  # role carried from the chain
    _assert_controlled_flags(out)
    _assert_no_result_or_executed_wording(out)
    # Every analysis entry is marked evaluated only (no real execution/delivery).
    for entry in out["analysis"]:
        assert entry["dry_run_evaluated"] is True
        assert entry["execution_executed"] is False
        assert entry["delivery_created"] is False


def test_dry_run_is_deterministic(case_001_accepted_dialogue: dict) -> None:
    a = build_dry_run(owner_authorization_dialogue_packet=case_001_accepted_dialogue)
    b = build_dry_run(owner_authorization_dialogue_packet=case_001_accepted_dialogue)
    assert a["analysis"] == b["analysis"]
    assert a["step_count"] == b["step_count"]


# --- 2. reject / required -> BLOCKED ----------------------------------------

def test_reject_blocks(case_001_accepted_dialogue: dict) -> None:
    rejected = dict(case_001_accepted_dialogue)
    rejected["status"] = STATUS_REJECTED
    out = build_dry_run(owner_authorization_dialogue_packet=rejected)
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_NOT_ACCEPTED
    _assert_no_result_or_executed_wording(out)


def test_required_blocks(case_001_accepted_dialogue: dict) -> None:
    required = dict(case_001_accepted_dialogue)
    required["status"] = STATUS_REQUIRED
    out = build_dry_run(owner_authorization_dialogue_packet=required)
    assert out["blocked_reason"] == BLOCK_NOT_ACCEPTED
    _assert_no_result_or_executed_wording(out)


# --- 3. Blocks --------------------------------------------------------------

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
def test_block_request_flags_true(case_001_accepted_dialogue: dict, flag: str) -> None:
    out = build_dry_run(**{"owner_authorization_dialogue_packet": case_001_accepted_dialogue, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_controlled_flags(out)


def test_block_input_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_dry_run(owner_authorization_dialogue_packet=bad)
        assert out["blocked_reason"] == BLOCK_INPUT_NOT_DICT
        _assert_controlled_flags(out)


@pytest.mark.parametrize(
    "flag",
    [
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
        "dry_run_evaluated",
        "execution_executed",
    ],
)
def test_block_input_flags_true(case_001_accepted_dialogue: dict, flag: str) -> None:
    tainted = dict(case_001_accepted_dialogue)
    tainted[flag] = True
    out = build_dry_run(owner_authorization_dialogue_packet=tainted)
    assert out["blocked_reason"] == BLOCK_INPUT_FLAGS_FORBIDDEN
    _assert_controlled_flags(out)


def test_block_missing_planned_steps(case_001_accepted_dialogue: dict) -> None:
    bad = dict(case_001_accepted_dialogue)
    bad.pop("planned_steps", None)
    out = build_dry_run(owner_authorization_dialogue_packet=bad)
    assert out["blocked_reason"] == BLOCK_MISSING_PLANNED_STEPS


def test_block_invalid_step(case_001_accepted_dialogue: dict) -> None:
    bad = dict(case_001_accepted_dialogue)
    bad["planned_steps"] = [{"action": "launch_missiles", "target": "x"}]
    out = build_dry_run(owner_authorization_dialogue_packet=bad)
    assert out["blocked_reason"] == BLOCK_INVALID_STEP


# --- 4. Stability -----------------------------------------------------------

def test_does_not_mutate_dialogue(case_001_accepted_dialogue: dict) -> None:
    before_status = case_001_accepted_dialogue["status"]
    before_steps = list(case_001_accepted_dialogue["planned_steps"])
    build_dry_run(owner_authorization_dialogue_packet=case_001_accepted_dialogue)
    assert case_001_accepted_dialogue["status"] == before_status
    assert list(case_001_accepted_dialogue["planned_steps"]) == before_steps

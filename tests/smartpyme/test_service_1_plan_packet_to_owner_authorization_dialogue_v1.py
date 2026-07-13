"""
Audit tests for SERVICE_1_PLAN_PACKET_TO_OWNER_AUTHORIZATION_DIALOGUE_V1.

Scope: owner-authorization dialogue only (READY plan packet -> authorization
dialogue). These tests do NOT execute tools, do NOT authorize
runtime/product/delivery/diagnosis, and do NOT create delivery. Full-chain
tests use real fixtures so the plan packet reaches EXECUTION_PLAN_READY.
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
    BLOCK_MISSING_PLANNED_STEPS,
    BLOCK_PLAN_FLAGS_FORBIDDEN,
    BLOCK_PLAN_NOT_DICT,
    BLOCK_PLAN_WRONG_STATUS,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    STATUS_ACCEPTED,
    STATUS_REJECTED,
    STATUS_REQUIRED,
    build_service_1_owner_authorization_dialogue_from_plan_packet_v1 as build_dialogue,
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


def _assert_all_flags_false(packet: dict) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False
    assert packet["execution_executed"] is False
    assert packet["delivery_created"] is False


@pytest.fixture()
def case_001_plan_packet() -> dict:
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
    return plan


# --- 1. Full chain -> dialogue --------------------------------------------

def test_case_001_plan_requires_authorization(case_001_plan_packet: dict) -> None:
    out = build_dialogue(plan_packet=case_001_plan_packet)
    assert out["status"] == STATUS_REQUIRED
    assert out["authorization_decision"] == STATUS_REQUIRED
    assert out["planned_steps"] == case_001_plan_packet["planned_steps"]
    _assert_all_flags_false(out)


def test_case_001_plan_accept(case_001_plan_packet: dict) -> None:
    out = build_dialogue(plan_packet=case_001_plan_packet, owner_authorization=AUTH_ACCEPT)
    assert out["status"] == STATUS_ACCEPTED
    assert out["authorization_decision"] == STATUS_ACCEPTED
    _assert_all_flags_false(out)


def test_case_001_plan_reject(case_001_plan_packet: dict) -> None:
    out = build_dialogue(plan_packet=case_001_plan_packet, owner_authorization=AUTH_REJECT)
    assert out["status"] == STATUS_REJECTED
    assert out["authorization_decision"] == STATUS_REJECTED
    _assert_all_flags_false(out)


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
def test_block_request_flags_true(case_001_plan_packet: dict, flag: str) -> None:
    out = build_dialogue(**{"plan_packet": case_001_plan_packet, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_all_flags_false(out)


def test_block_plan_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_dialogue(plan_packet=bad)
        assert out["blocked_reason"] == BLOCK_PLAN_NOT_DICT
        _assert_all_flags_false(out)


def test_block_plan_wrong_status() -> None:
    out = build_dialogue(plan_packet={"status": "BLOCKED", "planned_steps": [1, 2]})
    assert out["blocked_reason"] == BLOCK_PLAN_WRONG_STATUS


def test_block_plan_flags_true(case_001_plan_packet: dict) -> None:
    tainted = dict(case_001_plan_packet)
    tainted["runtime_authorized"] = True
    out = build_dialogue(plan_packet=tainted)
    assert out["blocked_reason"] == BLOCK_PLAN_FLAGS_FORBIDDEN


def test_block_missing_planned_steps(case_001_plan_packet: dict) -> None:
    bad = dict(case_001_plan_packet)
    bad.pop("planned_steps", None)
    out = build_dialogue(plan_packet=bad)
    assert out["blocked_reason"] == BLOCK_MISSING_PLANNED_STEPS


# --- 3. Stability ---------------------------------------------------------

def test_deterministic_same_input(case_001_plan_packet: dict) -> None:
    a = build_dialogue(plan_packet=case_001_plan_packet)
    b = build_dialogue(plan_packet=case_001_plan_packet)
    assert a == b


def test_does_not_mutate_plan_packet(case_001_plan_packet: dict) -> None:
    before_status = case_001_plan_packet["status"]
    before_steps = list(case_001_plan_packet["planned_steps"])
    build_dialogue(plan_packet=case_001_plan_packet)
    assert case_001_plan_packet["status"] == before_status
    assert list(case_001_plan_packet["planned_steps"]) == before_steps


def test_unknown_authorization_answer_blocks(case_001_plan_packet: dict) -> None:
    out = build_dialogue(plan_packet=case_001_plan_packet, owner_authorization="maybe")
    # Not accept/reject -> treated as an invalid decision -> BLOCKED.
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_PLAN_WRONG_STATUS

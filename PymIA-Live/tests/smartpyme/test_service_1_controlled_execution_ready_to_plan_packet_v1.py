"""
Audit tests for SERVICE_1_CONTROLLED_EXECUTION_READY_TO_PLAN_PACKET_V1.

Scope: plan packet builder only (READY gate -> auditable plan packet). These
tests do NOT execute tools, do NOT authorize runtime/product/delivery/diagnosis,
and do NOT create delivery. The full-chain test uses real fixtures so the gate
reaches CONTROLLED_EXECUTION_CANDIDATE_READY.
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
    BLOCK_GATE_FLAGS_FORBIDDEN,
    BLOCK_GATE_NOT_DICT,
    BLOCK_GATE_WRONG_STATUS,
    BLOCK_MISSING_CANDIDATE,
    BLOCK_NO_CANDIDATES,
    BLOCK_NO_ROLES,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    STATUS_PLAN_READY,
    build_service_1_controlled_execution_plan_packet_v1 as build_plan,
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


@pytest.fixture()
def case_001_ready_gate() -> dict:
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

    # Re-apply owner confirmations onto the bridge candidates (mirrors the
    # reinjection connector) and re-run the gate to reach READY.
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
    return ready_gate


# --- 1. Full chain -> plan READY ------------------------------------------

def test_case_001_full_chain_plan_ready(case_001_ready_gate: dict) -> None:
    out = build_plan(gate_packet=case_001_ready_gate)

    assert out["status"] == STATUS_PLAN_READY
    assert out["candidate_count"] == 10  # lock CASE_001
    assert "operation_date" in out["roles"]
    assert out["execution_executed"] is False
    assert out["delivery_created"] is False
    assert out["planned_steps"], "expected deterministic planned steps"
    _assert_all_flags_false(out)


def test_plan_is_deterministic(case_001_ready_gate: dict) -> None:
    a = build_plan(gate_packet=case_001_ready_gate)
    b = build_plan(gate_packet=case_001_ready_gate)
    assert a["planned_steps"] == b["planned_steps"]
    assert a["roles"] == b["roles"]
    assert a["candidate_count"] == b["candidate_count"]


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
def test_block_request_flags_true(case_001_ready_gate: dict, flag: str) -> None:
    out = build_plan(**{"gate_packet": case_001_ready_gate, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_all_flags_false(out)


def test_block_gate_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_plan(gate_packet=bad)
        assert out["blocked_reason"] == BLOCK_GATE_NOT_DICT
        _assert_all_flags_false(out)


def test_block_gate_wrong_status() -> None:
    out = build_plan(gate_packet={"status": "NEEDS_OWNER_CONFIRMATION"})
    assert out["blocked_reason"] == BLOCK_GATE_WRONG_STATUS


def test_block_gate_flags_true(case_001_ready_gate: dict) -> None:
    tainted = dict(case_001_ready_gate)
    tainted["runtime_authorized"] = True
    out = build_plan(gate_packet=tainted)
    assert out["blocked_reason"] == BLOCK_GATE_FLAGS_FORBIDDEN


def test_block_missing_candidate(case_001_ready_gate: dict) -> None:
    bad = dict(case_001_ready_gate)
    bad.pop("controlled_execution_candidate", None)
    out = build_plan(gate_packet=bad)
    assert out["blocked_reason"] == BLOCK_MISSING_CANDIDATE


def test_block_no_candidates(case_001_ready_gate: dict) -> None:
    bad = dict(case_001_ready_gate)
    bad["controlled_execution_candidate"] = {
        "candidate_columns": [],
        "candidate_roles": ["operation_date"],
    }
    out = build_plan(gate_packet=bad)
    assert out["blocked_reason"] == BLOCK_NO_CANDIDATES


def test_block_no_roles(case_001_ready_gate: dict) -> None:
    bad = dict(case_001_ready_gate)
    bad["controlled_execution_candidate"] = {
        "candidate_columns": ["fecha"],
        "candidate_roles": [],
    }
    bad.pop("candidate_roles", None)
    out = build_plan(gate_packet=bad)
    assert out["blocked_reason"] == BLOCK_NO_ROLES

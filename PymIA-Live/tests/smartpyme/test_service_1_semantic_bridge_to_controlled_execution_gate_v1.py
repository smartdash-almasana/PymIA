"""
Audit tests for SERVICE_1_SEMANTIC_BRIDGE_TO_CONTROLLED_EXECUTION_GATE_V1.

Scope: fail-closed gate only (semantic bridge output -> controlled execution
gate packet). These tests do NOT execute tools, do NOT authorize
runtime/product/delivery/diagnosis, and do NOT create delivery. The full-chain
test uses real fixtures; the READY path uses synthetic all-safe candidates.
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
    BLOCK_BRIDGE_FLAGS_FORBIDDEN,
    BLOCK_BRIDGE_NOT_DICT,
    BLOCK_BRIDGE_WRONG_STATUS,
    BLOCK_CANDIDATE_FLAGS_FORBIDDEN,
    BLOCK_INVALID_CANDIDATE,
    BLOCK_NO_CANDIDATES,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    EXPECTED_BRIDGE_STATUS,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY,
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)

# --- Fixture resolution ---------------------------------------------------

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


def _safe_candidate(source: str, role: str, *, owner_confirmation_required: bool = False):
    return Service1ColumnSemanticCandidateV1(
        source_column_name=source,
        normalized_column_name=source,
        sheet_name="sheet1",
        observed_data_type="text",
        sample_values=("x",),
        candidate_semantic_roles=(role,),
        candidate_variable_names=(role,),
        confidence=0.9,
        ambiguity_reason=None,
        owner_confirmation_required=owner_confirmation_required,
    )


@pytest.fixture()
def case_001_bridge_packet() -> dict:
    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    bridge = build_bridge(ingestion_output=connector["ingestion_output"])
    assert bridge["status"] == EXPECTED_BRIDGE_STATUS
    return bridge


# --- 1. Full chain: CASE_001 is resolved by the understanding engine -------

def test_full_chain_case_001_reaches_ready_gate(case_001_bridge_packet: dict) -> None:
    out = build_gate(semantic_bridge_packet=case_001_bridge_packet)

    assert case_001_bridge_packet["column_candidate_count"] == 10  # lock
    assert out["semantic_candidate_count"] == 10
    assert out["status"] == STATUS_READY
    assert out["owner_questions"] == []
    assert out["controlled_execution_candidate"] is not None
    _assert_all_flags_false(out)


# --- 2. Synthetic all-safe candidates -> READY ----------------------------

def test_synthetic_all_safe_candidates_ready() -> None:
    bridge = {
        "status": EXPECTED_BRIDGE_STATUS,
        "case_id": "case_synth",
        "source_kind": "local_path",
        "filename": "synthetic.xlsx",
        "column_candidates": (
            _safe_candidate("fecha", "operation_date"),
            _safe_candidate("canal", "sales_channel"),
        ),
    }
    out = build_gate(semantic_bridge_packet=bridge)

    assert out["status"] == STATUS_READY
    assert out["controlled_execution_candidate"] is not None
    cec = out["controlled_execution_candidate"]
    assert cec["runtime_authorized"] is False
    assert cec["tool_execution_authorized"] is False
    assert cec["delivery_authorized"] is False
    assert cec["diagnosis_generated"] is False
    _assert_all_flags_false(out)


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
def test_block_request_flags_true(case_001_bridge_packet: dict, flag: str) -> None:
    out = build_gate(**{"semantic_bridge_packet": case_001_bridge_packet, flag: True})
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_all_flags_false(out)


def test_block_bridge_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_gate(semantic_bridge_packet=bad)
        assert out["blocked_reason"] == BLOCK_BRIDGE_NOT_DICT
        _assert_all_flags_false(out)


def test_block_bridge_wrong_status() -> None:
    out = build_gate(semantic_bridge_packet={"status": "BLOCKED", "column_candidates": ()})
    assert out["blocked_reason"] == BLOCK_BRIDGE_WRONG_STATUS


def test_block_bridge_forbidden_flag_true() -> None:
    bridge = {
        "status": EXPECTED_BRIDGE_STATUS,
        "column_candidates": (_safe_candidate("fecha", "operation_date"),),
        "runtime_authorized": True,
    }
    out = build_gate(semantic_bridge_packet=bridge)
    assert out["blocked_reason"] == BLOCK_BRIDGE_FLAGS_FORBIDDEN


def test_block_no_candidates() -> None:
    out = build_gate(semantic_bridge_packet={"status": EXPECTED_BRIDGE_STATUS, "column_candidates": ()})
    assert out["blocked_reason"] == BLOCK_NO_CANDIDATES


def test_block_invalid_candidate_object() -> None:
    bridge = {
        "status": EXPECTED_BRIDGE_STATUS,
        "column_candidates": ({"not": "a candidate"},),
    }
    out = build_gate(semantic_bridge_packet=bridge)
    assert out["blocked_reason"] == BLOCK_INVALID_CANDIDATE


def test_block_candidate_forbidden_flag_true() -> None:
    # The candidate contract forbids constructing with a True flag, so force it
    # on a frozen instance to simulate a tampered/tainted candidate.
    tainted = _safe_candidate("fecha", "operation_date")
    object.__setattr__(tainted, "runtime_authorized", True)
    bridge = {
        "status": EXPECTED_BRIDGE_STATUS,
        "column_candidates": (tainted,),
    }
    out = build_gate(semantic_bridge_packet=bridge)
    assert out["blocked_reason"] == BLOCK_CANDIDATE_FLAGS_FORBIDDEN


# --- 4. Stability ---------------------------------------------------------

def test_deterministic_same_input(case_001_bridge_packet: dict) -> None:
    a = build_gate(semantic_bridge_packet=case_001_bridge_packet)
    b = build_gate(semantic_bridge_packet=case_001_bridge_packet)
    # Compare ignoring the non-deterministic candidate objects (identity-free).
    assert a["status"] == b["status"]
    assert a["semantic_candidate_count"] == b["semantic_candidate_count"]
    assert a["candidate_roles"] == b["candidate_roles"]
    assert a["owner_questions"] == b["owner_questions"]


def test_does_not_mutate_bridge_packet(case_001_bridge_packet: dict) -> None:
    before_keys = set(case_001_bridge_packet.keys())
    before_status = case_001_bridge_packet["status"]
    before_count = case_001_bridge_packet["column_candidate_count"]
    build_gate(semantic_bridge_packet=case_001_bridge_packet)
    assert set(case_001_bridge_packet.keys()) == before_keys
    assert case_001_bridge_packet["status"] == before_status
    assert case_001_bridge_packet["column_candidate_count"] == before_count


def test_candidate_count_matches_input(case_001_bridge_packet: dict) -> None:
    out = build_gate(semantic_bridge_packet=case_001_bridge_packet)
    assert out["semantic_candidate_count"] == case_001_bridge_packet["column_candidate_count"]


def test_roles_include_operation_date_in_case_001(case_001_bridge_packet: dict) -> None:
    out = build_gate(semantic_bridge_packet=case_001_bridge_packet)
    assert "operation_date" in out["candidate_roles"]

"""
Audit tests for SERVICE_1_CANONICAL_INGESTION_OUTPUT_TO_SEMANTIC_BRIDGE_V1.

Scope: connector only (canonical ingestion_output -> semantic column
candidates). These tests do NOT authorize runtime/product/delivery, do NOT
execute tools, do NOT create delivery, and exercise the real end-to-end chain
using genuine fixtures and existing upstream/downstream modules.
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
    BLOCK_COLUMNS_VALUES_MISMATCH,
    BLOCK_DUPLICATE_COLUMNS,
    BLOCK_INGESTION_FLAGS_FORBIDDEN,
    BLOCK_INGESTION_NOT_DICT,
    BLOCK_NO_COLUMNS,
    BLOCK_NO_INPUT_VALUES,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    STATUS_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_bridge,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
    Service1SemanticEvidenceBindingResultV1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_engine_v1 import (
    build_service_1_semantic_evidence_binding_result_v1 as build_engine_result,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_SALES_MARGIN,
    STATUS_READY as FAMILY_STATUS_READY,
    Service1VariableFamilyBindingV1,
)


def _assert_safety_flags_false(packet: dict) -> None:
    """Every bridge packet (OK or BLOCKED) must keep safety flags false."""
    assert packet["runtime_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False

# --- Fixture resolution ---------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]          # PymIA/
_PARENT_ROOT = _REPO_ROOT.parent                          # PymIA/

_CASE_001_CANDIDATES = [
    _PARENT_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
    _REPO_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
]


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip(f"No fixture found among: {[str(c) for c in candidates]}")


@pytest.fixture()
def case_001_ingestion_output() -> dict:
    """Real ingestion_output built through the full upstream chain."""
    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    assert connector["status"] == "INGESTION_OUTPUT_READY"
    return connector["ingestion_output"]


# --- OK full chain --------------------------------------------------------

def test_ok_full_chain_semantic_candidates_ready(case_001_ingestion_output: dict) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)

    assert out["status"] == STATUS_READY
    assert out["blocked_reason"] is None
    assert out["case_id"] == case_001_ingestion_output["case_id"]
    assert out["source_kind"] == case_001_ingestion_output["source_kind"]
    assert out["filename"] == case_001_ingestion_output["filename"]


def test_produces_10_semantic_candidates(case_001_ingestion_output: dict) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)

    candidates = out["column_candidates"]
    assert out["column_candidate_count"] == 10
    assert len(candidates) == 10
    assert all(isinstance(c, Service1ColumnSemanticCandidateV1) for c in candidates)


def test_case_001_lock_is_10(case_001_ingestion_output: dict) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)
    assert (
        len(out["columns"])
        == out["column_candidate_count"]
        == len(out["column_candidates"])
        == 10
    )


def test_bridge_does_not_run_p7_before_p6(
    case_001_ingestion_output: dict,
) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)

    assert out["variable_family_count"] == 0
    assert out["variable_family_bindings"] == ()
    assert out["ready_variable_family_ids"] == []


def test_at_least_one_role_is_operation_date(case_001_ingestion_output: dict) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)
    all_roles = {
        role
        for candidate in out["column_candidates"]
        for role in candidate.candidate_semantic_roles
    }
    assert "operation_date" in all_roles


def test_semantic_engine_accepts_candidates(case_001_ingestion_output: dict) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)

    result = build_engine_result(
        case_id="case_semantic_bridge_audit",
        column_candidates=out["column_candidates"],
        formula_entries=(),
        pathology_entries=(),
    )
    # The engine must accept the candidates and return the typed result.
    assert isinstance(result, Service1SemanticEvidenceBindingResultV1)
    assert hasattr(result, "case_id")
    # Engine result must stay fail-closed on every authorization flag.
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


# --- safety flags always False --------------------------------------------

def test_safety_flags_false_on_ok(case_001_ingestion_output: dict) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)
    _assert_safety_flags_false(out)


# --- blocks ---------------------------------------------------------------

@pytest.mark.parametrize(
    "flag",
    ["runtime_authorized", "product_ready", "delivery_authorized"],
)
def test_block_request_flags_true(case_001_ingestion_output: dict, flag: str) -> None:
    out = build_bridge(
        **{"ingestion_output": case_001_ingestion_output, flag: True}
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_safety_flags_false(out)


def test_block_ingestion_not_dict() -> None:
    for bad in (None, {}, ["x"]):
        out = build_bridge(ingestion_output=bad)
        assert out["blocked_reason"] == BLOCK_INGESTION_NOT_DICT
        _assert_safety_flags_false(out)


def test_block_ingestion_runtime_authorized_true(case_001_ingestion_output: dict) -> None:
    tainted = dict(case_001_ingestion_output)
    tainted["runtime_authorized"] = True
    out = build_bridge(ingestion_output=tainted)
    assert out["blocked_reason"] == BLOCK_INGESTION_FLAGS_FORBIDDEN
    _assert_safety_flags_false(out)


def test_block_no_columns() -> None:
    out = build_bridge(ingestion_output={"input_values": {"a": 1}})
    assert out["blocked_reason"] == BLOCK_NO_COLUMNS
    _assert_safety_flags_false(out)


def test_block_no_input_values() -> None:
    out = build_bridge(ingestion_output={"columns": ["a", "b"]})
    assert out["blocked_reason"] == BLOCK_NO_INPUT_VALUES
    _assert_safety_flags_false(out)


def test_block_duplicate_columns() -> None:
    out = build_bridge(
        ingestion_output={
            "columns": ["a", "a"],
            "input_values": {"a": 1},
        }
    )
    assert out["blocked_reason"] == BLOCK_DUPLICATE_COLUMNS
    _assert_safety_flags_false(out)


def test_block_columns_values_mismatch() -> None:
    out = build_bridge(
        ingestion_output={
            "columns": ["a", "b"],
            "input_values": {"a": 1},
        }
    )
    assert out["blocked_reason"] == BLOCK_COLUMNS_VALUES_MISMATCH
    _assert_safety_flags_false(out)

def test_bridge_builds_owner_question_views_from_same_understandings(
    case_001_ingestion_output: dict,
) -> None:
    out = build_bridge(ingestion_output=case_001_ingestion_output)

    assert len(out["owner_question_views"]) == len(out["column_understandings"])
    assert [view.column_name for view in out["owner_question_views"]] == [
        understanding.column_name for understanding in out["column_understandings"]
    ]
    assert all(view.runtime_authorized is False for view in out["owner_question_views"])
    assert all(view.delivery_authorized is False for view in out["owner_question_views"])

"""
Audit tests for SERVICE_1_OWNER_CONFIRMATION_TO_CANONICAL_INGESTION_OUTPUT_V1.

Scope: connector only (owner_question_packet + owner_answers -> canonical
ingestion_output). These tests do NOT authorize runtime/product/delivery, do
NOT execute tools, do NOT create delivery, and use real XLSX fixtures via the
boundary module to produce genuine packets.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1 as build_intake,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    BLOCK_ANSWERS_NOT_DICT,
    BLOCK_DUPLICATE_COLUMNS,
    BLOCK_MISSING_ANSWERS,
    BLOCK_PACKET_FLAGS_FORBIDDEN,
    BLOCK_PACKET_NOT_DICT,
    BLOCK_PACKET_WRONG_SCHEMA,
    BLOCK_PACKET_WRONG_STATUS,
    BLOCK_QUESTION_COUNT_INCONSISTENT,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    BLOCK_UNKNOWN_COLUMNS,
    STATUS_READY,
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1 as build_conn,
)
from pymia.smartpyme.service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1 import (
    build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1 as build_adapter,
)

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
def case_001_packet() -> dict:
    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    return packet


@pytest.fixture()
def full_answers(case_001_packet: dict) -> dict:
    return {column: f"significado de {column}" for column in case_001_packet["columns"]}


# --- OK path --------------------------------------------------------------

def test_ok_produces_ingestion_output_ready(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)

    assert out["status"] == STATUS_READY
    assert out["blocked_reason"] is None
    assert out["case_id"] == case_001_packet["case_id"]
    assert out["source_kind"] == case_001_packet["source_kind"]
    assert out["filename"] == case_001_packet["filename"]
    assert out["confirmed_columns"] == case_001_packet["columns"]
    assert out["owner_answers"] == full_answers
    assert out["ingestion_output"] is not None


def test_case_001_lock_is_10(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)
    assert (
        len(out["columns"])
        == len(out["confirmed_columns"])
        == len(out["owner_answers"])
        == len(out["ingestion_output"]["available_data_fields"])
        == 10
    )


# --- ingestion_output compatible with the existing runtime-bridge adapter --

def test_ingestion_output_compatible_with_adapter(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)

    result = build_adapter(
        case_id="c1",
        tenant_id="t1",
        intake_id="i1",
        run_id="r1",
        owner_ref="o1",
        raw_owner_narrative="narrativa de prueba",
        ingestion_output=out["ingestion_output"],
    )

    assert len(result.available_data_fields) == 10
    assert len(result.input_values) == 10
    # The adapter must not be blocked for missing/invalid ingestion output.
    assert result.status not in (
        "ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT",
        "ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT",
    )


# --- safety flags always False --------------------------------------------

def test_safety_flags_false_on_ok(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)
    assert out["runtime_authorized"] is False
    assert out["product_ready"] is False
    assert out["delivery_authorized"] is False
    assert out["ingestion_output"]["runtime_authorized"] is False


# --- blocks ---------------------------------------------------------------

@pytest.mark.parametrize(
    "flag",
    ["runtime_authorized", "product_ready", "delivery_authorized"],
)
def test_block_request_flags_true(case_001_packet: dict, full_answers: dict, flag: str) -> None:
    out = build_conn(
        **{
            "owner_question_packet": case_001_packet,
            "owner_answers": full_answers,
            flag: True,
        }
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    assert out["runtime_authorized"] is False
    assert out["product_ready"] is False
    assert out["delivery_authorized"] is False


def test_block_packet_not_dict() -> None:
    out = build_conn(owner_question_packet=["not", "a", "dict"], owner_answers={})
    assert out["blocked_reason"] == BLOCK_PACKET_NOT_DICT


def test_block_wrong_schema() -> None:
    bad = {"schema_version": "SOMETHING_ELSE", "packet_type": "X", "status": "NEEDS_OWNER_CONFIRMATION"}
    out = build_conn(owner_question_packet=bad, owner_answers={})
    assert out["blocked_reason"] == BLOCK_PACKET_WRONG_SCHEMA


def test_block_wrong_status(case_001_packet: dict, full_answers: dict) -> None:
    packet = dict(case_001_packet)
    packet["status"] = "BLOCKED"
    out = build_conn(owner_question_packet=packet, owner_answers=full_answers)
    assert out["blocked_reason"] == BLOCK_PACKET_WRONG_STATUS


@pytest.mark.parametrize(
    "flag",
    ["runtime_authorized", "product_ready", "delivery_authorized"],
)
def test_block_packet_flags_true(case_001_packet: dict, full_answers: dict, flag: str) -> None:
    packet = dict(case_001_packet)
    packet[flag] = True
    out = build_conn(owner_question_packet=packet, owner_answers=full_answers)
    assert out["blocked_reason"] == BLOCK_PACKET_FLAGS_FORBIDDEN


def test_block_question_count_inconsistent(case_001_packet: dict, full_answers: dict) -> None:
    packet = dict(case_001_packet)
    packet["question_count"] = 999
    out = build_conn(owner_question_packet=packet, owner_answers=full_answers)
    assert out["blocked_reason"] == BLOCK_QUESTION_COUNT_INCONSISTENT


def test_block_owner_answers_not_dict(case_001_packet: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=["a", "b"])
    assert out["blocked_reason"] == BLOCK_ANSWERS_NOT_DICT


def test_block_duplicate_columns(case_001_packet: dict, full_answers: dict) -> None:
    packet = dict(case_001_packet)
    duplicated = list(packet["columns"])
    duplicated[1] = duplicated[0]  # force a duplicate detected column
    packet["columns"] = duplicated
    packet["question_count"] = len(duplicated)
    out = build_conn(owner_question_packet=packet, owner_answers=full_answers)
    assert out["blocked_reason"] == BLOCK_DUPLICATE_COLUMNS


def test_block_unknown_columns(case_001_packet: dict, full_answers: dict) -> None:
    answers = dict(full_answers)
    answers["ZZZ_columna_inexistente"] = "algo"
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=answers)
    assert out["blocked_reason"] == BLOCK_UNKNOWN_COLUMNS


def test_block_missing_answers(case_001_packet: dict, full_answers: dict) -> None:
    answers = dict(full_answers)
    answers.pop(case_001_packet["columns"][0])
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=answers)
    assert out["blocked_reason"] == BLOCK_MISSING_ANSWERS


def test_block_empty_answer_counts_as_missing(case_001_packet: dict, full_answers: dict) -> None:
    answers = dict(full_answers)
    answers[case_001_packet["columns"][0]] = "   "  # whitespace-only -> missing
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=answers)
    assert out["blocked_reason"] == BLOCK_MISSING_ANSWERS

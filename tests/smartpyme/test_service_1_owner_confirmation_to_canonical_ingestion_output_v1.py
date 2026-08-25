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
    CANONICAL_INGESTION_SCHEMA_VERSION,
    REQUEST_KIND_WORKBOOK,
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
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    Service1ProductExecutionDependenciesV1,
    WorkbookSemanticStartRequestV1,
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
    assert out["source_artifact_ref"] == case_001_packet["source_artifact_ref"]
    assert out["workbook_ref"] == case_001_packet["workbook_ref"]
    assert out["confirmed_columns"] == case_001_packet["columns"]
    assert all(
        ref["owner_meaning"] == full_answers[ref["field_id"]]
        for ref in out["ingestion_output"]["column_refs"]
    )
    assert "owner_answers" not in out
    assert out["ingestion_output"] is not None


def test_case_001_lock_is_10(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)
    assert (
        len(out["columns"])
        == len(out["confirmed_columns"])
        == len(out["ingestion_output"]["column_refs"])
        == 10
    )


# --- ingestion_output stays canonical and runtime-independent -----------

def test_ingestion_output_is_canonical_and_runtime_independent(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)

    ingestion_output = out["ingestion_output"]
    assert ingestion_output["schema_version"] == CANONICAL_INGESTION_SCHEMA_VERSION
    assert ingestion_output["request_kind"] == REQUEST_KIND_WORKBOOK
    for removed_alias in (
        "case_id",
        "source_artifact_ref",
        "workbook_ref",
        "source_file_ref",
        "source_kind",
        "filename",
        "ingestion_scope",
        "sheet_name",
        "sheet_names",
        "sheet_ref",
        "sheet_refs",
    ):
        assert removed_alias not in ingestion_output
    assert ingestion_output["workbook_context"]["case_id"] == case_001_packet["case_id"]
    assert ingestion_output["provenance"]["filename"] == case_001_packet["filename"]
    assert ingestion_output["provenance"]["sheet_names"]
    for removed_alias in (
        "available_data_fields",
        "columns",
        "input_values",
        "normalized_values",
        "column_meaning_confirmations",
        "column_evidence",
        "declared_data_sources",
    ):
        assert removed_alias not in ingestion_output
    assert len(ingestion_output["column_refs"]) == 10
    assert all(ref["owner_meaning"] for ref in ingestion_output["column_refs"])
    assert ingestion_output["normalized_tables"]
    assert ingestion_output["runtime_authorized"] is False
    assert ingestion_output["safety_flags"] == {
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def test_workbook_context_is_identity_only_and_matches_intake(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)
    ingestion_output = out["ingestion_output"]
    context = ingestion_output["workbook_context"]

    assert context == {
        "case_id": case_001_packet["case_id"],
        "source_artifact_ref": case_001_packet["source_artifact_ref"],
        "workbook_ref": case_001_packet["workbook_ref"],
        "ingestion_scope": case_001_packet["ingestion_scope"],
        "canonical_reader_schema_version": case_001_packet[
            "canonical_reader_schema_version"
        ],
        "source_system_ref": case_001_packet["source_system_ref"],
        "source_context_ref": case_001_packet["source_context_ref"],
    }
    assert context["workbook_ref"] != case_001_packet["filename"]
    for forbidden in (
        "normalized_tables",
        "column_refs",
        "physical_lineage",
        "input_values",
        "normalized_values",
        "semantic_evidence",
        "p7_p8_evidence_projection",
    ):
        assert forbidden not in context


def test_physical_lineage_projects_reader_coordinates_without_copying_cells(case_001_packet: dict, full_answers: dict) -> None:
    out = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)
    ingestion_output = out["ingestion_output"]
    lineage = ingestion_output["physical_lineage"]
    tables = ingestion_output["normalized_tables"]

    assert len(lineage) == len(tables)
    assert lineage
    for record, table in zip(lineage, tables):
        assert record["sheet_name"] == table["sheet_name"]
        assert record["sheet_ref"].startswith("sheet:sha256:")
        assert record["header_row_number"] == table["header_row_number"]
        assert record["source_row_numbers"] == table["source_row_numbers"]
        assert record["physical_max_column"] == table["physical_max_column"]
        assert record["physical_max_row"] == table["physical_max_row"]
        assert "physical_rows" not in record
        assert "cells" not in record


def test_cli_does_not_mutate_canonical_envelope_after_build(
    case_001_packet: dict,
    full_answers: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pymia.cli.service_1_product as cli

    real = build_conn(owner_question_packet=case_001_packet, owner_answers=full_answers)
    sentinel_output = dict(real["ingestion_output"])
    sentinel_output["normalized_tables"] = [{"sentinel": True}]
    sentinel_connector = dict(real)
    sentinel_connector["ingestion_output"] = sentinel_output
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: sentinel_connector,
    )

    def _capture_product_root(
        request: WorkbookSemanticStartRequestV1,
        *,
        dependencies: Service1ProductExecutionDependenciesV1,
    ) -> dict[str, str]:
        captured["request"] = request
        captured["dependencies"] = dependencies
        return {"status": "BLOCKED"}

    monkeypatch.setattr(
        cli,
        "run_service_1_product_pipeline_v1",
        _capture_product_root,
    )

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=next(
            candidate
            for candidate in _CASE_001_CANDIDATES
            if candidate.exists()
        ),
        owner_column_answers=full_answers,
        semantic_owner_answers=None,
        output_dir=tmp_path,
    )

    assert result["status"] == "BLOCKED"
    request = captured["request"]
    dependencies = captured["dependencies"]
    assert isinstance(request, WorkbookSemanticStartRequestV1)
    assert isinstance(dependencies, Service1ProductExecutionDependenciesV1)
    assert request.ingestion_output is sentinel_output
    assert request.ingestion_output["normalized_tables"] == [{"sentinel": True}]


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

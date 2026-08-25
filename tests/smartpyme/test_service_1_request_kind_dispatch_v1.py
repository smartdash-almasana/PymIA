from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    SPECIALIZED_DOMAIN_COLLECTION_AGING,
    Service1ProductExecutionDependenciesV1,
    SpecializedDomainExecuteRequestV1,
    WorkbookAnalysisExecuteRequestV1,
    WorkbookSemanticStartRequestV1,
)


def _table() -> dict:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": "OK",
        "source_kind": "xlsx",
        "source_path": "fixture.xlsx",
        "sheet_name": "Ventas",
        "headers": ["ID", "Importe"],
        "normalized_headers": ["id", "importe"],
        "rows": [{"id": "1", "importe": "10"}],
        "header_row_number": 1,
        "source_row_numbers": [2],
        "row_count": 1,
        "column_count": 2,
        "warnings": [],
        "blocking_errors": [],
        "physical_rows": [
            {"row_number": 1, "cells": ["ID", "Importe"], "physical_width": 2},
            {"row_number": 2, "cells": ["1", "10"], "physical_width": 2},
        ],
        "physical_max_column": 2,
        "physical_max_row": 2,
        "runtime_authorized": False,
    }


def _workbook_envelope() -> dict:
    return {
        "schema_version": "SERVICE_1_CANONICAL_INGESTION_OUTPUT_V2",
        "workbook_context": {
            "case_id": "case-phase4",
            "source_artifact_ref": "artifact:phase4",
            "workbook_ref": "workbook-phase4",
            "ingestion_scope": "first_non_empty_sheet",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
            "source_system_ref": "xlsx",
            "source_context_ref": "phase4-test",
        },
        "normalized_tables": [_table()],
        "column_refs": [
            {"field_id": "ID", "sheet_name": "Ventas", "column_name": "ID"},
            {"field_id": "Importe", "sheet_name": "Ventas", "column_name": "Importe"},
        ],
        "physical_lineage": [
            {
                "sheet_name": "Ventas",
                "source_kind": "xlsx",
                "source_path": "fixture.xlsx",
                "header_row_number": 1,
                "source_row_numbers": [2],
                "physical_max_column": 2,
                "physical_max_row": 2,
            }
        ],
        "provenance": {
            "source_kind": "xlsx",
            "source_file_ref": "workbook-phase4",
            "filename": "fixture.xlsx",
            "sheet_names": ["Ventas"],
        },
        "safety_flags": {
            "runtime_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
        },
        "case_id": "case-phase4",
        "source_kind": "xlsx",
        "filename": "fixture.xlsx",
        "source_file_ref": "workbook-phase4",
        "columns": ["ID", "Importe"],
        "sheet_names": ["Ventas"],
    }


def _deps(tmp_path: Path) -> Service1ProductExecutionDependenciesV1:
    return Service1ProductExecutionDependenciesV1(output_dir=tmp_path)


def test_root_accepts_only_explicit_command_contracts() -> None:
    signature = inspect.signature(product.run_service_1_product_pipeline_v1)
    assert tuple(signature.parameters) == ("request", "dependencies")


def test_invalid_command_fails_closed_before_d7(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        product,
        "build_service_1_workbook_logical_model_v1",
        lambda **_: pytest.fail("invalid command must not activate D7"),
    )
    result = product.run_service_1_product_pipeline_v1(object(), dependencies=_deps(tmp_path))
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "PRODUCT_EXECUTION_REQUEST_INVALID"


def test_workbook_start_requires_complete_canonical_envelope(tmp_path: Path) -> None:
    incomplete = _workbook_envelope()
    incomplete.pop("workbook_context")
    result = product.run_service_1_product_pipeline_v1(
        WorkbookSemanticStartRequestV1(ingestion_output=incomplete),
        dependencies=_deps(tmp_path),
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "WORKBOOK_CONTEXT_REQUIRED"


def test_workbook_analysis_traverses_d7_before_governed_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        product,
        "build_service_1_workbook_logical_model_v1",
        lambda **_: calls.append("D7")
        or {"status": product.WORKBOOK_LOGICAL_MODEL_READY, "schema_identity": {"schema_fingerprint": "schema:phase4"}},
    )
    monkeypatch.setattr(
        product,
        "run_service_1_governed_analysis_v1",
        lambda **_: calls.append("GOVERNED") or {"status": "READY"},
    )
    result = product.run_service_1_product_pipeline_v1(
        WorkbookAnalysisExecuteRequestV1(
            ingestion_output=_workbook_envelope(),
            confirmed_bindings={"status": product.STATUS_CONFIRMED_BINDINGS},
            analysis_id="sales_total",
        ),
        dependencies=_deps(tmp_path),
    )
    assert result["status"] == "READY"
    assert calls == ["D7", "GOVERNED"]


def test_specialized_command_does_not_activate_d7(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        product,
        "build_service_1_workbook_logical_model_v1",
        lambda **_: pytest.fail("specialized command must not execute D7"),
    )
    monkeypatch.setattr(
        product,
        "build_collection_aging_product_request_v1",
        lambda **_: {
            "status": "AGING_REVIEW_READY",
            "computation_result": {"status": "OK"},
            "bounded_outcome": {"status": "OUTCOME_READY"},
        },
    )
    result = product.run_service_1_product_pipeline_v1(
        SpecializedDomainExecuteRequestV1(
            subtype=SPECIALIZED_DOMAIN_COLLECTION_AGING,
            payload={"owner_requested": True},
        ),
        dependencies=_deps(tmp_path),
    )
    assert result["status"] == "AGING_REVIEW_READY"


def test_resultset_reentry_is_not_an_execution_command(tmp_path: Path) -> None:
    result = product.run_service_1_product_pipeline_v1(
        SpecializedDomainExecuteRequestV1(subtype="RESULTSET_REENTRY", payload={}),
        dependencies=_deps(tmp_path),
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "SPECIALIZED_DOMAIN_SUBTYPE_INVALID"

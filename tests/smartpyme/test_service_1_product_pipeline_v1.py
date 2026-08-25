from __future__ import annotations

from pathlib import Path

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    SPECIALIZED_DOMAIN_COLLECTION_AGING,
    Service1ProductExecutionDependenciesV1,
    SpecializedDomainExecuteRequestV1,
    WorkbookAnalysisExecuteRequestV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookSemanticStartRequestV1,
)


def _table() -> dict:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": "OK",
        "source_kind": "xlsx",
        "source_path": "ventas.xlsx",
        "sheet_name": "Ventas",
        "headers": ["fecha", "monto"],
        "normalized_headers": ["fecha", "monto"],
        "rows": [{"fecha": "2026-06-01", "monto": 100}],
        "header_row_number": 1,
        "source_row_numbers": [2],
        "row_count": 1,
        "column_count": 2,
        "warnings": [],
        "blocking_errors": [],
        "physical_rows": [
            {"row_number": 1, "cells": ["fecha", "monto"], "physical_width": 2},
            {"row_number": 2, "cells": ["2026-06-01", 100], "physical_width": 2},
        ],
        "physical_max_column": 2,
        "physical_max_row": 2,
        "runtime_authorized": False,
    }


def _ingestion() -> dict:
    return {
        "schema_version": "SERVICE_1_CANONICAL_INGESTION_OUTPUT_V2",
        "workbook_context": {
            "case_id": "case-product-root",
            "source_artifact_ref": "artifact:product-root",
            "workbook_ref": "workbook-product-root",
            "ingestion_scope": "first_non_empty_sheet",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
            "source_system_ref": "xlsx",
            "source_context_ref": "product-root-test",
        },
        "normalized_tables": [_table()],
        "column_refs": [
            {"field_id": "fecha", "sheet_name": "Ventas", "column_name": "fecha"},
            {"field_id": "monto", "sheet_name": "Ventas", "column_name": "monto"},
        ],
        "physical_lineage": [
            {
                "sheet_name": "Ventas",
                "source_kind": "xlsx",
                "source_path": "ventas.xlsx",
                "header_row_number": 1,
                "source_row_numbers": [2],
                "physical_max_column": 2,
                "physical_max_row": 2,
            }
        ],
        "provenance": {
            "source_kind": "xlsx",
            "source_file_ref": "workbook-product-root",
            "filename": "ventas.xlsx",
            "sheet_names": ["Ventas"],
        },
        "safety_flags": {
            "runtime_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
        },
        "case_id": "case-product-root",
        "source_kind": "xlsx",
        "filename": "ventas.xlsx",
        "source_file_ref": "workbook-product-root",
        "columns": ["fecha", "monto"],
        "sheet_names": ["Ventas"],
    }


def _deps(tmp_path: Path) -> Service1ProductExecutionDependenciesV1:
    return Service1ProductExecutionDependenciesV1(
        output_dir=tmp_path,
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
    )


def test_workbook_start_is_explicit_and_fail_closed_without_semantic_provider(tmp_path: Path) -> None:
    result = product.run_service_1_product_pipeline_v1(
        WorkbookSemanticStartRequestV1(ingestion_output=_ingestion()),
        dependencies=Service1ProductExecutionDependenciesV1(output_dir=tmp_path),
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"]
    assert result["physical_run"] is None


def test_workbook_start_and_continue_share_one_explicit_root(tmp_path: Path) -> None:
    first = product.run_service_1_product_pipeline_v1(
        WorkbookSemanticStartRequestV1(ingestion_output=_ingestion()),
        dependencies=_deps(tmp_path),
    )
    assert first["status"] in {product.STATUS_NEEDS_OWNER, product.STATUS_READY}
    state = first.get("semantic_assistance_state")
    if first["status"] == product.STATUS_NEEDS_OWNER:
        response_items = tuple(
            {
                "decision_id": question["decision_id"],
                "action": "ACCEPT",
                "option_id": next(
                    option["option_id"]
                    for option in question.get("options", [])
                    if option["option_id"] not in {"OTHER", "IGNORE"}
                )
                if question.get("options")
                else next(
                    option_id
                    for option_id in question.get("allowed_option_ids", ())
                    if option_id not in {"OTHER", "IGNORE"}
                ),
            }
            for question in first["owner_questions"]
            if question.get("options") or question.get("allowed_option_ids")
        )
        if response_items:
            second = product.run_service_1_product_pipeline_v1(
                WorkbookSemanticContinueRequestV1(
                    ingestion_output=_ingestion(),
                    semantic_assistance_state=state,
                    semantic_dialogue_responses=response_items,
                ),
                dependencies=_deps(tmp_path),
            )
            assert second["status"] in {product.STATUS_READY, product.STATUS_NEEDS_OWNER, product.STATUS_BLOCKED}
            assert second["physical_run"] is None


def test_analysis_command_traverses_d7_then_governed_analysis(tmp_path: Path, monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        product,
        "build_service_1_workbook_logical_model_v1",
        lambda **_: calls.append("D7")
        or {"status": product.WORKBOOK_LOGICAL_MODEL_READY, "schema_identity": {"schema_fingerprint": "x"}},
    )
    monkeypatch.setattr(
        product,
        "run_service_1_governed_analysis_v1",
        lambda **_: calls.append("GOVERNED") or {"status": "READY"},
    )
    result = product.run_service_1_product_pipeline_v1(
        WorkbookAnalysisExecuteRequestV1(
            ingestion_output=_ingestion(),
            confirmed_bindings={"status": product.STATUS_CONFIRMED_BINDINGS},
            analysis_id="sales_total",
        ),
        dependencies=Service1ProductExecutionDependenciesV1(output_dir=tmp_path),
    )
    assert result["status"] == "READY"
    assert calls == ["D7", "GOVERNED"]


def test_specialized_subtype_is_explicit_and_never_builds_d7(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        product,
        "build_service_1_workbook_logical_model_v1",
        lambda **_: (_ for _ in ()).throw(AssertionError("D7 bypassed for specialized command")),
    )
    monkeypatch.setattr(
        product,
        "build_collection_aging_product_request_v1",
        lambda **_: {
            "status": "AGING_REVIEW_READY",
            "computation_result": {},
            "bounded_outcome": {},
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

from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_document_curation_report_to_owner_prompt_batch_bridge_v1 import (
    FILE_NAME_MISMATCH,
    MISSING_MATRIX,
    SCHEMA_VERSION,
    build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1,
)
from tools.document_ingestion import DocumentCurationReport


def _entry(role: str = "venta_total") -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name="Total",
        sheet_name="Ventas",
        sample_values=[100, 200, 300],
        inferred_type="number",
        suggested_semantic_role=role,
        calculation_relevance=CalculationRelevance.VENTAS,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
        owner_question="Confirmame si esta columna es ventas.",
    )


def _matrix(file_name: str = "ventas.xlsx") -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(file_name=file_name, entries=[_entry()])


def _report(
    *,
    file_name: str = "ventas.xlsx",
    matrix: ColumnConfirmationMatrix | None = None,
) -> DocumentCurationReport:
    return DocumentCurationReport(
        file_name=file_name,
        status="CURATED",
        tables_count=1,
        rows_count=2,
        mapped_fields={"Total": "venta_total"},
        column_confirmation_matrix=matrix,
    )


def test_report_with_valid_matrix_generates_owner_prompt_batch() -> None:
    result = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=_matrix()),
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.file_name == "ventas.xlsx"
    assert result.report_status == "CURATED"
    assert result.has_column_confirmation_matrix is True
    assert result.blocked_reason is None
    assert result.owner_prompt_batch is not None
    assert result.prompts_count == 1
    assert result.has_prompts is True
    assert result.owner_prompt_batch.file_name == "ventas.xlsx"
    assert result.owner_prompt_batch.prompts[0].column_name == "Total"


def test_report_without_matrix_fails_closed() -> None:
    result = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=None),
    )

    assert result.has_column_confirmation_matrix is False
    assert result.owner_prompt_batch is None
    assert result.prompts_count == 0
    assert result.has_prompts is False
    assert result.blocked_reason == MISSING_MATRIX


def test_report_with_matrix_file_name_mismatch_fails_closed() -> None:
    result = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(file_name="ventas.xlsx", matrix=_matrix(file_name="otro.xlsx")),
    )

    assert result.has_column_confirmation_matrix is True
    assert result.owner_prompt_batch is None
    assert result.blocked_reason == FILE_NAME_MISMATCH
    assert result.prompts_count == 0


def test_metadata_is_propagated_to_wrapper_batch_and_prompts() -> None:
    result = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=_matrix()),
        metadata={"case_id": "case-1", "tenant_id": "tenant-1"},
    )

    assert result.metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}
    assert result.owner_prompt_batch is not None
    assert result.owner_prompt_batch.metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}
    assert result.owner_prompt_batch.prompts[0].metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}


def test_security_flags_are_preserved() -> None:
    result = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=_matrix()),
    )

    assert result.runtime_authorized is False
    assert result.human_review_required is True
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.persistence_authorized is False
    assert result.owner_prompt_batch is not None
    assert result.owner_prompt_batch.runtime_authorized is False
    assert result.owner_prompt_batch.human_review_required is True


def test_to_dict_serializes_batch_or_none() -> None:
    ok = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=_matrix()),
    ).to_dict()
    blocked = build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=None),
    ).to_dict()

    assert ok["owner_prompt_batch"] is not None
    assert ok["owner_prompt_batch"]["file_name"] == "ventas.xlsx"
    assert blocked["owner_prompt_batch"] is None
    assert blocked["blocked_reason"] == MISSING_MATRIX


def test_rejects_invalid_report_type() -> None:
    with pytest.raises(ValueError, match="report"):
        build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
            report="bad",  # type: ignore[arg-type]
        )


def test_rejects_invalid_metadata_type() -> None:
    with pytest.raises(ValueError, match="metadata"):
        build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
            report=_report(matrix=_matrix()),
            metadata="bad",  # type: ignore[arg-type]
        )


def test_bridge_is_pure_no_storage_side_effects(tmp_path) -> None:
    before = set(tmp_path.iterdir())

    build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
        report=_report(matrix=_matrix()),
    )

    after = set(tmp_path.iterdir())
    assert after == before


def test_module_does_not_depend_on_ingestion_runtime_or_io() -> None:
    source = Path(
        "pymia/smartpyme/service_1_document_curation_report_to_owner_prompt_batch_bridge_v1.py"
    ).read_text(encoding="utf-8")

    assert "openpyxl" not in source
    assert "pandas" not in source
    assert "read_excel" not in source
    assert "curate_xlsx_document" not in source
    assert "XlsxCurationPipeline" not in source
    assert "DocumentCurator" not in source

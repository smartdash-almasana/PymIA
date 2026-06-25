from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.column_confirmation_v1 import CalculationRelevance, ColumnConfirmationEntry, ColumnConfirmationMatrix, ConfirmationStatus
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import build_service_1_column_confirmation_owner_prompt_batch_v1
from pymia.smartpyme.service_1_owner_prompt_batch_to_question_bundle_alignment_v1 import (
    ALIGNMENT_STATUS_ALIGNED,
    ALIGNMENT_STATUS_BLOCKED,
    ALIGNMENT_STATUS_EMPTY,
    ALIGNMENT_STATUS_PARTIAL,
    SCHEMA_VERSION,
    align_service_1_owner_prompt_batch_to_question_bundle_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import ANSWER_TYPE_CONFIRM_COLUMN_ROLE, build_service_1_question_bundle_v1


def _entry(column_name: str, role: str, *, status: ConfirmationStatus = ConfirmationStatus.PENDING_OWNER_CONFIRMATION) -> ColumnConfirmationEntry:
    relevance = CalculationRelevance.CANTIDADES if role == "cantidad" else CalculationRelevance.VENTAS
    return ColumnConfirmationEntry(
        original_column_name=column_name,
        sheet_name="Ventas",
        sample_values=[100, 200],
        inferred_type="number",
        suggested_semantic_role=role,
        calculation_relevance=relevance,
        confirmation_status=status,
        owner_question=f"La columna {column_name} confirma {role}?",
    )


def _matrix(entries: list[ColumnConfirmationEntry]) -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(file_name="ventas.xlsx", entries=entries)


def _bundle(matrix: ColumnConfirmationMatrix | None):
    return build_service_1_question_bundle_v1(
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
        run_id="run-1",
        column_confirmation_matrix=matrix.model_dump(mode="json") if matrix is not None else None,
    )


def _batch(matrix: ColumnConfirmationMatrix):
    return build_service_1_column_confirmation_owner_prompt_batch_v1(matrix=matrix)


def test_aligns_prompt_to_question_ref_by_file_sheet_column_target() -> None:
    matrix = _matrix([_entry("Total", "venta_total")])
    bundle = _bundle(matrix)
    batch = _batch(matrix)

    out = align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle=bundle, owner_prompt_batch=batch)

    assert out.schema_version == SCHEMA_VERSION
    assert out.alignment_status == ALIGNMENT_STATUS_ALIGNED
    assert out.aligned_prompts_count == 1
    assert out.unaligned_prompts_count == 0
    assert out.selected_next_question_ref == bundle.selected_next_question_ref
    aligned = out.aligned_prompts[0]
    assert aligned.question_ref == bundle.questions[0].question_ref
    assert aligned.target_ref == "file:ventas.xlsx:sheet:Ventas:column:Total"
    assert aligned.answer_type == ANSWER_TYPE_CONFIRM_COLUMN_ROLE
    assert aligned.prompt_text == batch.prompts[0].owner_prompt.prompt_text
    assert aligned.question_text == bundle.questions[0].text
    assert aligned.question_text != aligned.prompt_text


def test_partial_alignment_reports_missing_question_refs() -> None:
    bundle_matrix = _matrix([_entry("Total", "venta_total")])
    batch_matrix = _matrix([_entry("Total", "venta_total"), _entry("Cantidad", "cantidad")])

    out = align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle=_bundle(bundle_matrix), owner_prompt_batch=_batch(batch_matrix))

    assert out.alignment_status == ALIGNMENT_STATUS_PARTIAL
    assert out.aligned_prompts_count == 1
    assert out.unaligned_prompts_count == 1
    assert out.unaligned_prompt_targets == ("file:ventas.xlsx:sheet:Ventas:column:Cantidad",)


def test_no_matching_questions_is_blocked() -> None:
    matrix = _matrix([_entry("Total", "venta_total")])

    out = align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle=_bundle(None), owner_prompt_batch=_batch(matrix))

    assert out.alignment_status == ALIGNMENT_STATUS_BLOCKED
    assert out.aligned_prompts == ()
    assert out.unaligned_prompt_targets == ("file:ventas.xlsx:sheet:Ventas:column:Total",)


def test_empty_prompt_batch_returns_empty_alignment() -> None:
    matrix = _matrix([_entry("Total", "venta_total", status=ConfirmationStatus.CONFIRMED)])

    out = align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle=_bundle(matrix), owner_prompt_batch=_batch(matrix))

    assert out.alignment_status == ALIGNMENT_STATUS_EMPTY
    assert out.total_prompts == 0
    assert out.aligned_prompts_count == 0
    assert out.unaligned_prompts_count == 0


def test_metadata_flags_and_to_dict_are_stable() -> None:
    matrix = _matrix([_entry("Total", "venta_total")])
    out = align_service_1_owner_prompt_batch_to_question_bundle_v1(
        question_bundle=_bundle(matrix),
        owner_prompt_batch=_batch(matrix),
        metadata={"surface": "owner_display"},
    )

    assert out.metadata == {"surface": "owner_display"}
    assert out.runtime_authorized is False
    assert out.human_review_required is True
    assert out.reexecution_authorized is False
    assert out.recalculation_authorized is False
    assert out.persistence_authorized is False
    assert out.aligned_prompts[0].metadata["surface"] == "owner_display"
    data = out.to_dict()
    assert isinstance(data["aligned_prompts"], list)
    assert data["aligned_prompts"][0]["allowed_owner_responses"] == ["SÍ", "NO", "TU_RESPUESTA"]


def test_rejects_invalid_inputs() -> None:
    matrix = _matrix([_entry("Total", "venta_total")])
    with pytest.raises(ValueError, match="question_bundle"):
        align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle="bad", owner_prompt_batch=_batch(matrix))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="owner_prompt_batch"):
        align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle=_bundle(matrix), owner_prompt_batch="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="metadata"):
        align_service_1_owner_prompt_batch_to_question_bundle_v1(question_bundle=_bundle(matrix), owner_prompt_batch=_batch(matrix), metadata="bad")  # type: ignore[arg-type]


def test_module_does_not_depend_on_io_ingestion_or_runtime() -> None:
    source = Path("pymia/smartpyme/service_1_owner_prompt_batch_to_question_bundle_alignment_v1.py").read_text(encoding="utf-8")
    assert "openpyxl" not in source
    assert "pandas" not in source
    assert "curate_xlsx_document" not in source
    assert "DocumentCurator" not in source
    assert "vertical_pipeline" not in source

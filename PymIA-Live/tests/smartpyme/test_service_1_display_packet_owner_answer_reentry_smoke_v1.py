from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_aligned_owner_prompt_display_packet_v1 import (
    DISPLAY_STATUS_READY,
    build_service_1_aligned_owner_prompt_display_packet_v1,
)
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    build_service_1_column_confirmation_owner_prompt_batch_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    REENTRY_STATUS_ACCEPTED,
    bind_owner_answer_for_service_1_reentry_v1,
)
from pymia.smartpyme.service_1_owner_prompt_batch_to_question_bundle_alignment_v1 import (
    ALIGNMENT_STATUS_ALIGNED,
    align_service_1_owner_prompt_batch_to_question_bundle_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


def _matrix() -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
        file_name="ventas.xlsx",
        entries=(
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                sample_values=[10000, 25000, 30000],
                inferred_type="number",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question="La columna Total corresponde a ventas del periodo?",
            ),
        ),
    )


def test_display_packet_question_ref_binds_owner_answer_for_reentry() -> None:
    matrix = _matrix()
    question_bundle = build_service_1_question_bundle_v1(
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
        run_id="run-1",
        column_confirmation_matrix=matrix.model_dump(mode="json"),
    )
    owner_prompt_batch = build_service_1_column_confirmation_owner_prompt_batch_v1(matrix=matrix)
    alignment = align_service_1_owner_prompt_batch_to_question_bundle_v1(
        question_bundle=question_bundle,
        owner_prompt_batch=owner_prompt_batch,
    )
    display_packet = build_service_1_aligned_owner_prompt_display_packet_v1(alignment=alignment)

    assert alignment.alignment_status == ALIGNMENT_STATUS_ALIGNED
    assert display_packet.display_status == DISPLAY_STATUS_READY
    assert display_packet.total_items == 1

    display_item = display_packet.items[0]
    assert display_item.question_ref == question_bundle.selected_next_question_ref
    assert display_item.question_ref
    assert display_item.prompt_text
    assert display_item.allowed_owner_responses == ("SÍ", "NO", "TU_RESPUESTA")

    reentry_packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=question_bundle,
        question_ref=display_item.question_ref,
        raw_owner_answer="SÍ",
        anamnesis_id="anamnesis-1",
        investigation_id="investigation-1",
        metadata={"source": "display_packet_smoke_v1"},
    )

    assert reentry_packet.status == REENTRY_STATUS_ACCEPTED
    assert reentry_packet.blocked_reason is None
    assert reentry_packet.owner_answer_record is not None
    assert reentry_packet.owner_answer_record.question_ref == display_item.question_ref
    assert reentry_packet.owner_answer_record.raw_owner_answer == "SÍ"
    assert reentry_packet.owner_answer_record.metadata["question_target_ref"] == display_item.target_ref
    assert reentry_packet.owner_answer_record.metadata["question_text"] == question_bundle.questions[0].text
    assert reentry_packet.owner_answer_record.metadata["owner_answer_validation_status"] == "DECLARED_NOT_VALIDATED"
    assert reentry_packet.runtime_authorized is False
    assert reentry_packet.human_review_required is True
    assert reentry_packet.reexecution_authorized is False
    assert reentry_packet.recalculation_authorized is False


def test_reentry_blocks_if_display_question_ref_is_not_in_bundle() -> None:
    matrix = _matrix()
    question_bundle = build_service_1_question_bundle_v1(
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
        run_id="run-1",
        column_confirmation_matrix=matrix.model_dump(mode="json"),
    )

    reentry_packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=question_bundle,
        question_ref="service_1:column_confirmation_matrix:unknown_display_question",
        raw_owner_answer="SÍ",
        anamnesis_id="anamnesis-1",
        investigation_id="investigation-1",
    )

    assert reentry_packet.status != REENTRY_STATUS_ACCEPTED
    assert reentry_packet.owner_answer_record is None
    assert reentry_packet.runtime_authorized is False
    assert reentry_packet.reexecution_authorized is False
    assert reentry_packet.recalculation_authorized is False

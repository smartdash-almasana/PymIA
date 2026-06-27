from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_column_confirmation_reentry_candidate_v1 import (
    BLOCK_ANSWER_TYPE_UNSUPPORTED,
    BLOCK_OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED,
    BLOCK_QUESTION_NOT_ANSWERED,
    BLOCK_QUESTION_SOURCE_UNSUPPORTED,
    BLOCK_RAW_OWNER_ANSWER_MISSING,
    BLOCK_ROLE_MISSING,
    BLOCK_TARGET_REF_INVALID,
    OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED,
    SCHEMA_VERSION,
    STATUS_BLOCKED,
    STATUS_READY_FOR_CLASSIFIER,
    Service1ColumnConfirmationReentryCandidateV1,
    build_service_1_column_confirmation_reentry_candidate_v1,
)
from pymia.smartpyme.service_1_reentry_projection_v1 import Service1ProjectedQuestionV1

TARGET_REF = "file:ventas.xlsx:sheet:Ventas:column:MetodoPago"


def _projected_question(**overrides: object) -> Service1ProjectedQuestionV1:
    data: dict[str, object] = {
        "question_ref": "service_1:column_confirmation_matrix:file_ventas_xlsx_sheet_ventas_column_metodopago",
        "source": "column_confirmation_matrix",
        "text": "Esta columna corresponde al medio de pago?",
        "target_ref": TARGET_REF,
        "answer_type": "confirm_column_role",
        "required": True,
        "original_status": "PENDING",
        "projection_status": "ANSWERED",
        "latest_answer_id": "answer_1",
        "latest_raw_owner_answer": "Sí, esa columna indica el medio de pago.",
        "owner_answer_validation_status": "DECLARED_NOT_VALIDATED",
        "metadata": {"origin": "test"},
    }
    data.update(overrides)
    return Service1ProjectedQuestionV1(**data)


def _assert_safety_flags(result: Service1ColumnConfirmationReentryCandidateV1) -> None:
    assert result.runtime_authorized is False
    assert result.human_review_required is True
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False


def test_builds_ready_candidate_packet_with_proposed_role() -> None:
    projected = _projected_question()

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.status == STATUS_READY_FOR_CLASSIFIER
    assert result.blocked_reason is None
    assert result.question_ref == projected.question_ref
    assert result.question_source == "column_confirmation_matrix"
    assert result.target_ref == TARGET_REF
    assert result.parsed_target_ref is not None
    assert result.parsed_target_ref.file_name == "ventas.xlsx"
    assert result.parsed_target_ref.sheet_name == "Ventas"
    assert result.parsed_target_ref.column_name == "MetodoPago"
    assert result.raw_owner_answer == "Sí, esa columna indica el medio de pago."
    assert result.proposed_role == "payment_method"
    assert (
        result.owner_answer_validation_status
        == OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED
    )
    _assert_safety_flags(result)
    assert not hasattr(result, "owner_column_confirmation_answer")
    assert not hasattr(result, "computation_unlocked")
    assert not hasattr(result, "persistence_authorized")


def test_builds_ready_candidate_packet_with_suggested_role_fallback() -> None:
    projected = _projected_question()

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        suggested_semantic_role="payment_method",
    )

    assert result.status == STATUS_READY_FOR_CLASSIFIER
    assert result.proposed_role == "payment_method"
    _assert_safety_flags(result)


def test_blocks_when_source_is_not_column_confirmation() -> None:
    projected = _projected_question(source="owner_question")

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_QUESTION_SOURCE_UNSUPPORTED
    _assert_safety_flags(result)


def test_blocks_when_answer_type_is_not_confirm_column_role() -> None:
    projected = _projected_question(answer_type="free_text")

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_ANSWER_TYPE_UNSUPPORTED
    _assert_safety_flags(result)


def test_blocks_when_projection_status_is_not_answered() -> None:
    projected = _projected_question(projection_status="PENDING")

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_QUESTION_NOT_ANSWERED
    _assert_safety_flags(result)


def test_blocks_when_raw_owner_answer_is_missing() -> None:
    projected = _projected_question(latest_raw_owner_answer=None)

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_RAW_OWNER_ANSWER_MISSING
    _assert_safety_flags(result)


def test_blocks_when_target_ref_is_invalid() -> None:
    projected = _projected_question(target_ref="owner:manual")

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_TARGET_REF_INVALID
    _assert_safety_flags(result)


def test_blocks_when_role_is_missing() -> None:
    projected = _projected_question()

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_ROLE_MISSING
    _assert_safety_flags(result)


def test_blocks_when_validation_status_is_not_declared_not_validated() -> None:
    projected = _projected_question(owner_answer_validation_status="VALIDATED_EVIDENCE")

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED
    _assert_safety_flags(result)


def test_to_dict_serializes_target_ref_and_metadata() -> None:
    projected = _projected_question()

    result = build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=projected,
        proposed_role="payment_method",
        metadata={"question_ref": projected.question_ref},
    )
    data = result.to_dict()

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["parsed_target_ref"] == {
        "file_name": "ventas.xlsx",
        "sheet_name": "Ventas",
        "column_name": "MetodoPago",
    }
    assert data["metadata"] == {"question_ref": projected.question_ref}
    assert data["owner_answer_validation_status"] == "DECLARED_NOT_VALIDATED"


def test_candidate_builder_is_pure_and_does_not_require_storage(tmp_path: Path) -> None:
    before = set(tmp_path.iterdir())

    build_service_1_column_confirmation_reentry_candidate_v1(
        projected_question=_projected_question(),
        proposed_role="payment_method",
    )

    after = set(tmp_path.iterdir())
    assert after == before


def test_rejects_wrong_projected_question_type() -> None:
    with pytest.raises(ValueError, match="Service1ProjectedQuestionV1"):
        build_service_1_column_confirmation_reentry_candidate_v1(
            projected_question={"bad": True},
            proposed_role="payment_method",
        )


def test_rejects_wrong_metadata_type() -> None:
    with pytest.raises(ValueError, match="metadata must be a dict or None"):
        build_service_1_column_confirmation_reentry_candidate_v1(
            projected_question=_projected_question(),
            proposed_role="payment_method",
            metadata=["bad"],
        )

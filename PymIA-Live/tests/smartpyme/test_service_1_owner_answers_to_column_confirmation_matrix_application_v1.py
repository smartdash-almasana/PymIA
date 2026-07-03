from __future__ import annotations

import json

import pytest

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    OwnerColumnConfirmationAnswer,
    OwnerColumnConfirmationOutcome,
    SemanticRectificationStatus,
)
from pymia.smartpyme.service_1_owner_answers_to_column_confirmation_matrix_application_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_MATRIX_BLOCKED,
    STATUS_MATRIX_PENDING,
    STATUS_MATRIX_UPDATED,
    STATUS_NO_ANSWERS,
    build_service_1_owner_answers_to_column_confirmation_matrix_application_v1,
)


def _entry(column: str, suggested_role: str = "unknown") -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column,
        sheet_name="OPERACION",
        sample_values=[],
        inferred_type="text",
        suggested_semantic_role=suggested_role,
        suggested_data_type="text",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        confidence="unknown",
        owner_question=None,
        owner_confirmed_role=None,
        owner_rectified_function=None,
        semantic_rectification_status=SemanticRectificationStatus.INFERRED_NOT_RECTIFIED,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    )


def _matrix() -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            _entry("producto"),
            _entry("precio"),
            _entry("costo"),
            _entry("nota"),
            _entry("descartar"),
            _entry("rechazada"),
            _entry("dudosa"),
        ],
    )


def _answer(
    *,
    column: str,
    outcome: OwnerColumnConfirmationOutcome,
    proposed_role: str = "unknown",
    confirmed_role: str | None = None,
    text: str = "SÍ",
) -> OwnerColumnConfirmationAnswer:
    return OwnerColumnConfirmationAnswer(
        sheet_name="OPERACION",
        column_name=column,
        owner_answer_text=text,
        proposed_role=proposed_role,
        confirmed_role=confirmed_role,
        outcome=outcome,
        unblocks_variable_names=[],
        reason="test",
    )


def _find(matrix: ColumnConfirmationMatrix, column: str) -> ColumnConfirmationEntry:
    for entry in matrix.entries:
        if entry.original_column_name == column:
            return entry
    raise AssertionError(f"missing column {column}")


def test_applies_computational_answer_to_copied_matrix_without_mutating_input() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[
            _answer(
                column="precio",
                outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL,
                proposed_role="precio_venta",
                confirmed_role="precio_venta",
            )
        ],
    )

    original_entry = _find(matrix, "precio")
    updated_entry = _find(result.updated_matrix, "precio")
    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status == STATUS_MATRIX_PENDING
    assert original_entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert original_entry.owner_rectified_function is None
    assert updated_entry.confirmation_status == ConfirmationStatus.CONFIRMED
    assert updated_entry.owner_confirmed_role == "precio_venta"
    assert updated_entry.owner_rectified_function == "precio_venta"
    assert updated_entry.calculation_relevance == CalculationRelevance.VENTAS
    assert result.summary.confirmed_count == 1
    assert result.summary.owner_rectified_functions_count == 1
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    assert result.evidence_profile_generated is False
    assert result.candidate_tools_generated is False


def test_applies_informational_and_not_relevant_answers() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[
            _answer(
                column="producto",
                outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL,
                proposed_role="producto",
                confirmed_role="producto",
            ),
            _answer(
                column="descartar",
                outcome=OwnerColumnConfirmationOutcome.CONFIRMED_NOT_RELEVANT,
                text="ignorar",
            ),
        ],
    )

    producto = _find(result.updated_matrix, "producto")
    descartar = _find(result.updated_matrix, "descartar")
    assert producto.confirmation_status == ConfirmationStatus.CONFIRMED
    assert producto.owner_rectified_function == "producto"
    assert producto.calculation_relevance == CalculationRelevance.INFORMATIONAL
    assert descartar.confirmation_status == ConfirmationStatus.IGNORED_NOT_RELEVANT
    assert descartar.owner_rectified_function is None
    assert result.summary.confirmed_count == 1
    assert result.summary.ignored_count == 1
    assert result.status == STATUS_MATRIX_PENDING


def test_blocks_rejected_and_conflicting_answers_fail_closed() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[
            _answer(
                column="rechazada",
                outcome=OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING,
                text="NO",
            ),
            _answer(
                column="dudosa",
                outcome=OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER,
                text="SÍ: pero no",
            ),
        ],
    )

    rechazada = _find(result.updated_matrix, "rechazada")
    dudosa = _find(result.updated_matrix, "dudosa")
    assert result.status == STATUS_MATRIX_BLOCKED
    assert rechazada.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
    assert rechazada.semantic_rectification_status == SemanticRectificationStatus.OWNER_REJECTED
    assert rechazada.owner_rectified_function is None
    assert dudosa.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
    assert dudosa.owner_rectified_function is None
    assert result.summary.blocked_count == 2
    assert result.summary.owner_rectified_functions_count == 0


def test_owner_unknown_and_insufficient_remain_pending() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[
            _answer(column="producto", outcome=OwnerColumnConfirmationOutcome.OWNER_UNKNOWN),
            _answer(
                column="nota",
                outcome=OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
                text="no sé",
            ),
        ],
    )

    producto = _find(result.updated_matrix, "producto")
    nota = _find(result.updated_matrix, "nota")
    assert result.status == STATUS_MATRIX_PENDING
    assert producto.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert producto.owner_rectified_function is None
    assert nota.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert nota.owner_rectified_function is None
    assert result.summary.pending_count == 7


def test_tu_respuesta_insufficient_blocks_as_unnormalizable_owner_response() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[
            _answer(
                column="nota",
                outcome=OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
                text="TU_RESPUESTA: es otra cosa",
            )
        ],
    )

    nota = _find(result.updated_matrix, "nota")
    assert result.status == STATUS_MATRIX_BLOCKED
    assert nota.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
    assert nota.semantic_rectification_status == SemanticRectificationStatus.BLOCKED_UNNORMALIZABLE_OWNER_RESPONSE
    assert nota.owner_rectified_function is None


def test_no_answers_returns_no_answers_without_mutating_matrix() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[],
    )

    assert result.status == STATUS_NO_ANSWERS
    assert result.updated_matrix == matrix
    assert result.updated_matrix is not matrix
    assert result.summary.total_answers == 0
    assert result.summary.applied_answers_count == 0
    assert result.summary.pending_count == 7


def test_to_dict_does_not_create_downstream_artifacts_or_authorization() -> None:
    matrix = _matrix()

    result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=matrix,
        owner_answers=[
            _answer(
                column="precio",
                outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL,
                proposed_role="precio_venta",
                confirmed_role="precio_venta",
            )
        ],
    )

    rendered = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "Service1OwnerRectifiedEvidenceProfile" not in rendered
    assert "tool_requests" not in rendered
    assert result.candidate_tools_generated is False
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    assert result.evidence_profile_generated is False
    assert result.candidate_tools_generated is False


def test_rejects_invalid_inputs_fail_closed() -> None:
    matrix = _matrix()

    with pytest.raises(ValueError, match="matrix"):
        build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
            matrix="bad",  # type: ignore[arg-type]
            owner_answers=[],
        )

    with pytest.raises(ValueError, match="owner_answers"):
        build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
            matrix=matrix,
            owner_answers="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="metadata"):
        build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
            matrix=matrix,
            owner_answers=[],
            metadata="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="owner_answers"):
        build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
            matrix=matrix,
            owner_answers=["bad"],  # type: ignore[list-item]
        )

    with pytest.raises(ValueError, match="not found"):
        build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
            matrix=matrix,
            owner_answers=[
                _answer(
                    column="inexistente",
                    outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL,
                    proposed_role="precio_venta",
                    confirmed_role="precio_venta",
                )
            ],
        )

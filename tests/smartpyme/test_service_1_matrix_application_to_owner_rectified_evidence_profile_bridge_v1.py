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
from pymia.smartpyme.service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_EVIDENCE_PROFILE_BLOCKED,
    STATUS_EVIDENCE_PROFILE_NEEDS_MORE_EVIDENCE,
    STATUS_EVIDENCE_PROFILE_READY,
    build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1,
)
from pymia.smartpyme.service_1_owner_answers_to_column_confirmation_matrix_application_v1 import (
    Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1,
    build_service_1_owner_answers_to_column_confirmation_matrix_application_v1,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import MARGIN_SIGNAL


def _entry(column: str) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column,
        sheet_name="OPERACION",
        sample_values=[],
        inferred_type="text",
        suggested_semantic_role="unknown",
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
            _entry("fecha"),
            _entry("cobro"),
            _entry("nota"),
        ],
    )


def _answer(
    *,
    column: str,
    outcome: OwnerColumnConfirmationOutcome,
    role: str | None = None,
    text: str = "SÍ",
) -> OwnerColumnConfirmationAnswer:
    return OwnerColumnConfirmationAnswer(
        sheet_name="OPERACION",
        column_name=column,
        owner_answer_text=text,
        proposed_role=role or "unknown",
        confirmed_role=role,
        outcome=outcome,
        unblocks_variable_names=[],
        reason="test",
    )


def _application_result_for_margin_ready() -> Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1:
    return build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[
            _answer(column="producto", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL, role="producto"),
            _answer(column="precio", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL, role="precio_venta"),
            _answer(column="costo", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL, role="costo_unitario"),
            _answer(column="fecha", outcome=OwnerColumnConfirmationOutcome.OWNER_UNKNOWN),
            _answer(column="cobro", outcome=OwnerColumnConfirmationOutcome.OWNER_UNKNOWN),
            _answer(column="nota", outcome=OwnerColumnConfirmationOutcome.OWNER_UNKNOWN),
        ],
    )


def test_builds_ready_evidence_profile_from_applied_matrix_without_candidate_tools() -> None:
    application_result = _application_result_for_margin_ready()

    bridge = build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application_result,
        case_ref="CASE-001",
        metadata={"operator": "test"},
    )

    assert bridge.schema_version == SCHEMA_VERSION
    assert bridge.service_name == SERVICE_NAME
    assert bridge.status == STATUS_EVIDENCE_PROFILE_READY
    assert bridge.source_file_name == "cafeteria_abc.xlsx"
    assert bridge.evidence_profile.case_ref == "CASE-001"
    assert bridge.evidence_profile.source_file_name == "cafeteria_abc.xlsx"
    assert bridge.evidence_profile.evidence_ready is True
    assert bridge.evidence_profile.blockers == ()
    assert bridge.summary.source_owner_rectified_functions_count == 3
    assert bridge.summary.evidence_source_columns_count == 3
    assert bridge.summary.evidence_ready_signals_count == 1
    margin_signal = next(signal for signal in bridge.evidence_profile.evidence_signals if signal.signal_name == MARGIN_SIGNAL)
    assert margin_signal.evidence_ready is True
    assert margin_signal.source_headers == ("costo", "precio", "producto")
    assert bridge.runtime_authorized is False
    assert bridge.tool_execution_authorized is False
    assert bridge.delivery_authorized is False
    assert bridge.diagnosis_generated is False
    assert bridge.candidate_tools_generated is False
    assert bridge.evidence_profile.runtime_authorized is False
    assert bridge.evidence_profile.tool_execution_authorized is False


def test_blocks_profile_when_applied_matrix_contains_owner_rejection() -> None:
    application_result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[
            _answer(column="producto", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL, role="producto"),
            _answer(column="precio", outcome=OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING, text="NO"),
        ],
    )

    bridge = build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application_result,
    )

    assert bridge.status == STATUS_EVIDENCE_PROFILE_BLOCKED
    assert bridge.evidence_profile.evidence_ready is False
    assert "OWNER_REJECTED:OPERACION.precio" in bridge.evidence_profile.blockers
    assert bridge.summary.blockers_count >= 1
    assert bridge.runtime_authorized is False
    assert bridge.candidate_tools_generated is False


def test_blocks_profile_when_no_owner_rectified_functions_exist() -> None:
    application_result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[],
    )

    bridge = build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application_result,
    )

    assert bridge.status == STATUS_EVIDENCE_PROFILE_BLOCKED
    assert bridge.evidence_profile.source_columns == ()
    assert "NO_OWNER_RECTIFIED_FUNCTIONS" in bridge.evidence_profile.blockers
    assert bridge.summary.evidence_source_columns_count == 0
    assert bridge.summary.evidence_ready is False
    assert bridge.summary.source_pending_count == 6


def test_needs_more_evidence_when_rectified_columns_exist_but_no_signal_is_ready() -> None:
    application_result = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[
            _answer(column="producto", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL, role="producto"),
        ],
    )

    bridge = build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application_result,
    )

    assert bridge.status == STATUS_EVIDENCE_PROFILE_NEEDS_MORE_EVIDENCE
    assert bridge.evidence_profile.evidence_ready is False
    assert bridge.evidence_profile.blockers == ()
    assert bridge.summary.evidence_source_columns_count == 1
    assert bridge.summary.evidence_ready_signals_count == 0
    assert bridge.summary.missing_requirements_count > 0


def test_serialization_does_not_create_candidate_tools_or_runtime_authorization() -> None:
    bridge = build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=_application_result_for_margin_ready(),
    )

    rendered = json.dumps(bridge.to_dict(), ensure_ascii=False)
    assert "candidate_tool_refs" not in rendered
    assert "executable_tool_requests" not in rendered
    assert "autonomous_delivery_authorized" not in rendered
    assert bridge.runtime_authorized is False
    assert bridge.tool_execution_authorized is False
    assert bridge.delivery_authorized is False
    assert bridge.diagnosis_generated is False
    assert bridge.candidate_tools_generated is False


def test_rejects_invalid_inputs_fail_closed() -> None:
    application_result = _application_result_for_margin_ready()

    with pytest.raises(ValueError, match="matrix_application_result"):
        build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
            matrix_application_result="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="metadata"):
        build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
            matrix_application_result=application_result,
            metadata="bad",  # type: ignore[arg-type]
        )

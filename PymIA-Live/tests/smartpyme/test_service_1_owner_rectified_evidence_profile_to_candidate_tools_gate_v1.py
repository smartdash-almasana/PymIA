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
    build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1,
)
from pymia.smartpyme.service_1_owner_answers_to_column_confirmation_matrix_application_v1 import (
    build_service_1_owner_answers_to_column_confirmation_matrix_application_v1,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED,
    STATUS_CANDIDATE_TOOLS_READY,
    STATUS_NEEDS_EVIDENCE,
    build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1,
)


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


def _profile_bridge_margin_ready():
    application = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[
            _answer(column="producto", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL, role="producto"),
            _answer(column="precio", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL, role="precio_venta"),
            _answer(column="costo", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL, role="costo_unitario"),
        ],
    )
    return build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application,
        case_ref="CASE-001",
    )


def _profile_bridge_needs_evidence():
    application = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[
            _answer(column="producto", outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL, role="producto"),
        ],
    )
    return build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application,
        case_ref="CASE-NEEDS",
    )


def _profile_bridge_blocked():
    application = build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
        matrix=_matrix(),
        owner_answers=[
            _answer(column="precio", outcome=OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING, text="NO"),
        ],
    )
    return build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
        matrix_application_result=application,
        case_ref="CASE-BLOCKED",
    )


def test_gate_maps_ready_evidence_profile_to_candidate_tools_without_execution() -> None:
    result = build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
        evidence_profile_bridge_result=_profile_bridge_margin_ready(),
        metadata={"operator": "test"},
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status == STATUS_CANDIDATE_TOOLS_READY
    assert result.source_file_name == "cafeteria_abc.xlsx"
    assert result.candidate_tools_result.status == "CANDIDATE_TOOLS_READY"
    assert result.candidate_tools_result.candidate_tool_refs == ("precio_margen_basico",)
    assert result.summary.candidate_tools_count == 1
    assert result.summary.candidate_tool_refs == ("precio_margen_basico",)
    assert result.summary.phase_closed_without_execution is True
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.executable_tool_requests_authorized is False
    assert result.autonomous_delivery_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    assert result.candidate_tools_result.runtime_authorized is False
    assert result.candidate_tools_result.tool_execution_authorized is False
    assert result.candidate_tools_result.executable_tool_requests_authorized is False
    assert result.candidate_tools_result.autonomous_delivery_authorized is False
    assert all(candidate.tool_execution_authorized is False for candidate in result.candidate_tools_result.candidate_tools)


def test_gate_returns_needs_evidence_when_profile_is_not_ready_but_unblocked() -> None:
    result = build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
        evidence_profile_bridge_result=_profile_bridge_needs_evidence(),
    )

    assert result.status == STATUS_NEEDS_EVIDENCE
    assert result.candidate_tools_result.status == "NEEDS_EVIDENCE"
    assert result.candidate_tools_result.candidate_tools == ()
    assert result.summary.candidate_tools_count == 0
    assert result.summary.missing_requirements_count > 0
    assert result.summary.blockers_count == 0
    assert result.runtime_authorized is False


def test_gate_returns_blocked_when_evidence_profile_has_blockers() -> None:
    result = build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
        evidence_profile_bridge_result=_profile_bridge_blocked(),
    )

    assert result.status == STATUS_BLOCKED
    assert result.candidate_tools_result.status == "BLOCKED"
    assert result.candidate_tools_result.candidate_tools == ()
    assert "OWNER_REJECTED:OPERACION.precio" in result.candidate_tools_result.blockers
    assert result.summary.blockers_count >= 1
    assert result.executable_tool_requests_authorized is False


def test_gate_respects_explicit_tool_allowlist_fail_closed() -> None:
    result = build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
        evidence_profile_bridge_result=_profile_bridge_margin_ready(),
        allowed_tool_refs=("stock_alertas_basicas",),
    )

    assert result.status == STATUS_BLOCKED
    assert result.candidate_tools_result.status == "BLOCKED"
    assert result.candidate_tools_result.candidate_tools == ()
    assert "TOOL_REF_NOT_IN_EXPLICIT_ALLOWLIST:precio_margen_basico" in result.candidate_tools_result.blockers
    assert result.tool_execution_authorized is False


def test_serialization_does_not_create_executable_requests_or_delivery() -> None:
    result = build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
        evidence_profile_bridge_result=_profile_bridge_margin_ready(),
    )

    rendered = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "precio_margen_basico" in rendered
    assert "tool_request_id" not in rendered
    assert result.tool_execution_authorized is False
    assert result.executable_tool_requests_authorized is False
    assert result.autonomous_delivery_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


def test_rejects_invalid_inputs_fail_closed() -> None:
    bridge_result = _profile_bridge_margin_ready()

    with pytest.raises(ValueError, match="evidence_profile_bridge_result"):
        build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
            evidence_profile_bridge_result="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="metadata"):
        build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
            evidence_profile_bridge_result=bridge_result,
            metadata="bad",  # type: ignore[arg-type]
        )

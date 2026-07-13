from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    BINDING_STATUS_BOUND_CANDIDATE,
    BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
    PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS,
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION,
    Service1ColumnSemanticCandidateV1,
    Service1ColumnVariableBindingV1,
    Service1FormulaVariableRequirementV1,
    Service1PathologyFormulaCandidateV1,
    Service1SemanticOwnerQuestionV1,
    build_service_1_semantic_evidence_binding_result_v1,
)


def _column_candidate() -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name="precio_unitario",
        normalized_column_name="precio_unitario",
        sheet_name="Ventas_Junio_2026",
        observed_data_type="number",
        sample_values=(100, 120, 140),
        candidate_semantic_roles=("precio_venta_unitario",),
        candidate_variable_names=("precio_venta",),
        confidence=0.82,
        ambiguity_reason=None,
        owner_confirmation_required=True,
        metadata={"source": "phase_1_contract_test"},
    )


def _formula_requirement() -> Service1FormulaVariableRequirementV1:
    return Service1FormulaVariableRequirementV1(
        formula_id="formula:margen_unitario_candidate",
        variable_name="precio_venta",
        required=True,
        accepted_semantic_roles=("precio_venta_unitario", "precio_unitario"),
        accepted_data_types=("number", "currency"),
        required_grain="row",
        required_unit="money",
        owner_confirmation_required=True,
        metadata={"phase": "semantic_contracts"},
    )


def _owner_question() -> Service1SemanticOwnerQuestionV1:
    return Service1SemanticOwnerQuestionV1(
        question_ref="question:semantic:precio_unitario:001",
        question_text="¿precio_unitario representa el precio final de venta unitario?",
        target_column_name="precio_unitario",
        target_variable_name="precio_venta",
        target_formula_id="formula:margen_unitario_candidate",
        reason="semantic_role_requires_owner_confirmation",
        answer_type="confirm_column_semantic_role",
        required=True,
    )


def test_builds_column_semantic_candidate_for_precio_unitario() -> None:
    candidate = _column_candidate()

    assert candidate.source_column_name == "precio_unitario"
    assert candidate.candidate_variable_names == ("precio_venta",)
    assert candidate.owner_confirmation_required is True
    assert candidate.runtime_authorized is False
    assert candidate.tool_execution_authorized is False
    assert candidate.delivery_authorized is False
    assert candidate.diagnosis_generated is False


def test_builds_formula_variable_requirement_for_sale_price() -> None:
    requirement = _formula_requirement()

    assert requirement.formula_id == "formula:margen_unitario_candidate"
    assert requirement.variable_name == "precio_venta"
    assert requirement.required is True
    assert "precio_venta_unitario" in requirement.accepted_semantic_roles


def test_builds_column_variable_binding_as_candidate() -> None:
    binding = Service1ColumnVariableBindingV1(
        source_column_name="precio_unitario",
        variable_name="precio_venta",
        formula_id="formula:margen_unitario_candidate",
        binding_status=BINDING_STATUS_BOUND_CANDIDATE,
        semantic_role="precio_venta_unitario",
        confidence=0.76,
        owner_confirmed=False,
        blocking_reason=None,
    )

    assert binding.binding_status == BINDING_STATUS_BOUND_CANDIDATE
    assert binding.owner_confirmed is False
    assert binding.blocking_reason is None


def test_builds_column_variable_binding_needing_owner_confirmation() -> None:
    binding = Service1ColumnVariableBindingV1(
        source_column_name="precio_unitario",
        variable_name="precio_venta",
        formula_id="formula:margen_unitario_candidate",
        binding_status=BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
        semantic_role="precio_venta_unitario",
        confidence=0.6,
        owner_confirmed=False,
        blocking_reason="owner_confirmation_required",
    )

    assert binding.binding_status == BINDING_STATUS_NEEDS_OWNER_CONFIRMATION
    assert binding.blocking_reason == "owner_confirmation_required"


def test_builds_pathology_formula_candidate_with_missing_variables() -> None:
    candidate = Service1PathologyFormulaCandidateV1(
        pathology_code="REN_001",
        formula_id="formula:margen_unitario_candidate",
        candidate_status=PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS,
        required_variables=("precio_venta", "costo_unitario", "volumen_vendido"),
        bound_variables=("precio_venta",),
        missing_variables=("costo_unitario", "volumen_vendido"),
        ambiguous_variables=(),
        owner_questions=("question:semantic:precio_unitario:001",),
    )

    assert candidate.candidate_status == PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS
    assert candidate.missing_variables == ("costo_unitario", "volumen_vendido")


def test_builds_semantic_owner_question() -> None:
    question = _owner_question()

    assert question.question_ref == "question:semantic:precio_unitario:001"
    assert question.target_column_name == "precio_unitario"
    assert question.target_variable_name == "precio_venta"
    assert question.required is True


def test_builds_semantic_binding_result_needing_owner_column_confirmation() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:001",
        column_candidates=[_column_candidate()],
        formula_requirements=[_formula_requirement()],
        owner_questions=[_owner_question()],
        ready_formula_ids=[],
        blocked_reasons=[],
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status == STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION
    assert result.owner_questions[0].target_column_name == "precio_unitario"


def test_global_result_never_authorizes_runtime_tools_delivery_or_diagnosis() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:001",
        owner_questions=[_owner_question()],
    )

    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


def test_to_dict_preserves_primary_fields() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:001",
        column_candidates=[_column_candidate()],
        formula_requirements=[_formula_requirement()],
        owner_questions=[_owner_question()],
        metadata={"test": "serialization"},
    )
    data = result.to_dict()

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["service_name"] == SERVICE_NAME
    assert data["case_id"] == "case:s1:semantic:001"
    assert data["column_candidates"][0]["source_column_name"] == "precio_unitario"
    assert data["owner_questions"][0]["question_ref"] == "question:semantic:precio_unitario:001"


def test_invalid_status_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="binding_status must be one of"):
        Service1ColumnVariableBindingV1(
            source_column_name="precio_unitario",
            variable_name="precio_venta",
            formula_id="formula:margen_unitario_candidate",
            binding_status="READY_BUT_FAKE",  # type: ignore[arg-type]
            semantic_role="precio_venta_unitario",
            confidence=0.7,
            owner_confirmed=False,
            blocking_reason=None,
        )

from __future__ import annotations

from typing import Any, Final

from pymia.smartpyme.service_1_semantic_catalog_loader_v1 import (
    Service1NormalizedFormulaCatalogEntryV1,
    Service1NormalizedPathologyCatalogEntryV1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    BINDING_STATUS_AMBIGUOUS,
    BINDING_STATUS_BOUND_CANDIDATE,
    BINDING_STATUS_MISSING_REQUIRED_COLUMN,
    BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
    PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION,
    PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS,
    PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE,
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_NEEDS_FORMULA_INPUTS,
    STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION,
    STATUS_READY_FOR_COMPUTATION_CANDIDATE,
    Service1ColumnSemanticCandidateV1,
    Service1ColumnVariableBindingV1,
    Service1FormulaVariableRequirementV1,
    Service1PathologyFormulaCandidateV1,
    Service1SemanticEvidenceBindingResultV1,
    Service1SemanticOwnerQuestionV1,
    build_service_1_semantic_evidence_binding_result_v1 as _build_contract_result_v1,
)


_QUESTION_TEXT_BY_VARIABLE: Final[dict[str, str]] = {
    "sale_price": (
        "Does this column represent final sale price, gross price, net price, "
        "or an adjusted sale price?"
    ),
    "cost": (
        "Does this column represent real cost, average cost, replacement cost, "
        "or a declared cost?"
    ),
    "sold_amount": (
        "Does this column include discounts, taxes, or adjustments, or does it "
        "come directly from quantity multiplied by price?"
    ),
}


def build_service_1_column_variable_bindings_v1(
    column_candidates: tuple[Service1ColumnSemanticCandidateV1, ...],
    formula_entry: Service1NormalizedFormulaCatalogEntryV1,
) -> tuple[Service1ColumnVariableBindingV1, ...]:
    _validate_column_candidates(column_candidates)
    _validate_formula_entry(formula_entry)

    bindings: list[Service1ColumnVariableBindingV1] = []
    for variable_name in formula_entry.required_variables:
        candidate = _find_candidate_for_variable(column_candidates, variable_name)
        if candidate is None:
            bindings.append(_missing_binding(variable_name=variable_name, formula_id=formula_entry.formula_id))
            continue

        binding_status = (
            BINDING_STATUS_NEEDS_OWNER_CONFIRMATION
            if candidate.owner_confirmation_required
            else BINDING_STATUS_BOUND_CANDIDATE
        )
        bindings.append(
            Service1ColumnVariableBindingV1(
                source_column_name=candidate.source_column_name,
                variable_name=variable_name,
                formula_id=formula_entry.formula_id,
                binding_status=binding_status,
                semantic_role=_first_text(candidate.candidate_semantic_roles),
                confidence=candidate.confidence,
                owner_confirmed=False,
                blocking_reason="owner_confirmation_required"
                if binding_status == BINDING_STATUS_NEEDS_OWNER_CONFIRMATION
                else None,
                runtime_authorized=False,
                tool_execution_authorized=False,
                delivery_authorized=False,
                diagnosis_generated=False,
                metadata={
                    "normalized_column_name": candidate.normalized_column_name,
                    "confidence_label": candidate.metadata.get("confidence_label"),
                },
            )
        )
    return tuple(bindings)


def build_service_1_semantic_owner_questions_v1(
    bindings: tuple[Service1ColumnVariableBindingV1, ...],
) -> tuple[Service1SemanticOwnerQuestionV1, ...]:
    _validate_bindings(bindings)

    questions: list[Service1SemanticOwnerQuestionV1] = []
    for binding in bindings:
        if binding.binding_status not in {
            BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
            BINDING_STATUS_AMBIGUOUS,
        }:
            continue
        questions.append(
            Service1SemanticOwnerQuestionV1(
                question_ref=_question_ref(binding),
                question_text=_question_text(binding.variable_name),
                target_column_name=binding.source_column_name,
                target_variable_name=binding.variable_name,
                target_formula_id=binding.formula_id,
                reason="semantic_binding_requires_owner_confirmation",
                answer_type="confirm_column_semantic_role",
                required=True,
                runtime_authorized=False,
                tool_execution_authorized=False,
                delivery_authorized=False,
                diagnosis_generated=False,
                metadata={"binding_status": binding.binding_status},
            )
        )
    return tuple(questions)


def build_service_1_pathology_formula_candidate_v1(
    pathology_entry: Service1NormalizedPathologyCatalogEntryV1,
    formula_entry: Service1NormalizedFormulaCatalogEntryV1,
    bindings: tuple[Service1ColumnVariableBindingV1, ...],
    owner_questions: tuple[Service1SemanticOwnerQuestionV1, ...],
) -> Service1PathologyFormulaCandidateV1:
    _validate_pathology_entry(pathology_entry)
    _validate_formula_entry(formula_entry)
    _validate_bindings(bindings)
    _validate_owner_questions(owner_questions)

    missing_variables = tuple(
        binding.variable_name
        for binding in bindings
        if binding.binding_status == BINDING_STATUS_MISSING_REQUIRED_COLUMN
    )
    pending_variables = tuple(
        binding.variable_name
        for binding in bindings
        if binding.binding_status
        in {
            BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
            BINDING_STATUS_AMBIGUOUS,
        }
    )
    bound_variables = tuple(
        binding.variable_name
        for binding in bindings
        if binding.binding_status
        in {
            BINDING_STATUS_BOUND_CANDIDATE,
            BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
            BINDING_STATUS_AMBIGUOUS,
        }
    )

    if missing_variables:
        status = PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS
    elif pending_variables:
        status = PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION
    else:
        status = PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE

    return Service1PathologyFormulaCandidateV1(
        pathology_code=pathology_entry.pathology_code,
        formula_id=formula_entry.formula_id,
        candidate_status=status,
        required_variables=formula_entry.required_variables,
        bound_variables=bound_variables,
        missing_variables=missing_variables,
        ambiguous_variables=pending_variables,
        owner_questions=tuple(question.question_ref for question in owner_questions),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={"pathology_name": pathology_entry.name},
    )


def build_service_1_semantic_evidence_binding_result_v1(
    *,
    case_id: str,
    column_candidates: tuple[Service1ColumnSemanticCandidateV1, ...],
    formula_entries: tuple[Service1NormalizedFormulaCatalogEntryV1, ...],
    pathology_entries: tuple[Service1NormalizedPathologyCatalogEntryV1, ...],
    metadata: dict[str, Any] | None = None,
) -> Service1SemanticEvidenceBindingResultV1:
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")
    _validate_column_candidates(column_candidates)
    _validate_formula_entries(formula_entries)
    _validate_pathology_entries(pathology_entries)
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    pathology_by_code = {entry.pathology_code: entry for entry in pathology_entries}
    all_bindings: list[Service1ColumnVariableBindingV1] = []
    all_questions: list[Service1SemanticOwnerQuestionV1] = []
    formula_requirements: list[Service1FormulaVariableRequirementV1] = []
    pathology_formula_candidates: list[Service1PathologyFormulaCandidateV1] = []
    ready_formula_ids: list[str] = []

    for formula_entry in formula_entries:
        pathology_entry = pathology_by_code.get(formula_entry.pathology_code)
        if pathology_entry is None:
            continue

        formula_requirements.extend(_formula_requirements(formula_entry))
        bindings = build_service_1_column_variable_bindings_v1(column_candidates, formula_entry)
        questions = build_service_1_semantic_owner_questions_v1(bindings)
        candidate = build_service_1_pathology_formula_candidate_v1(
            pathology_entry,
            formula_entry,
            bindings,
            questions,
        )

        all_bindings.extend(bindings)
        all_questions.extend(questions)
        pathology_formula_candidates.append(candidate)
        if candidate.candidate_status == PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE:
            ready_formula_ids.append(formula_entry.formula_id)

    status = _global_status(
        owner_questions=tuple(all_questions),
        bindings=tuple(all_bindings),
        ready_formula_ids=tuple(ready_formula_ids),
    )

    return _build_contract_result_v1(
        case_id=case_id.strip(),
        status=status,
        column_candidates=column_candidates,
        formula_requirements=tuple(formula_requirements),
        bindings=tuple(all_bindings),
        pathology_formula_candidates=tuple(pathology_formula_candidates),
        owner_questions=tuple(all_questions),
        ready_formula_ids=tuple(ready_formula_ids),
        blocked_reasons=(),
        metadata=dict(metadata or {}),
    )


def _formula_requirements(
    formula_entry: Service1NormalizedFormulaCatalogEntryV1,
) -> tuple[Service1FormulaVariableRequirementV1, ...]:
    return tuple(
        Service1FormulaVariableRequirementV1(
            formula_id=formula_entry.formula_id,
            variable_name=variable_name,
            required=True,
            accepted_semantic_roles=(),
            accepted_data_types=(),
            required_grain=None,
            required_unit=None,
            owner_confirmation_required=False,
            runtime_authorized=False,
            tool_execution_authorized=False,
            delivery_authorized=False,
            diagnosis_generated=False,
            metadata={"pathology_code": formula_entry.pathology_code},
        )
        for variable_name in formula_entry.required_variables
    )


def _global_status(
    *,
    owner_questions: tuple[Service1SemanticOwnerQuestionV1, ...],
    bindings: tuple[Service1ColumnVariableBindingV1, ...],
    ready_formula_ids: tuple[str, ...],
) -> str:
    if owner_questions:
        return STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION
    if any(binding.binding_status == BINDING_STATUS_MISSING_REQUIRED_COLUMN for binding in bindings):
        return STATUS_NEEDS_FORMULA_INPUTS
    if ready_formula_ids:
        return STATUS_READY_FOR_COMPUTATION_CANDIDATE
    return STATUS_NEEDS_FORMULA_INPUTS


def _find_candidate_for_variable(
    column_candidates: tuple[Service1ColumnSemanticCandidateV1, ...],
    variable_name: str,
) -> Service1ColumnSemanticCandidateV1 | None:
    for candidate in column_candidates:
        if variable_name in candidate.candidate_variable_names:
            return candidate
    return None


def _missing_binding(*, variable_name: str, formula_id: str) -> Service1ColumnVariableBindingV1:
    return Service1ColumnVariableBindingV1(
        source_column_name=f"missing:{variable_name}",
        variable_name=variable_name,
        formula_id=formula_id,
        binding_status=BINDING_STATUS_MISSING_REQUIRED_COLUMN,
        semantic_role=None,
        confidence=0.0,
        owner_confirmed=False,
        blocking_reason="missing_required_column",
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={},
    )


def _question_text(variable_name: str) -> str:
    return _QUESTION_TEXT_BY_VARIABLE.get(
        variable_name,
        "Please confirm the operational meaning of this column before it is used.",
    )


def _question_ref(binding: Service1ColumnVariableBindingV1) -> str:
    return (
        "question:semantic:"
        f"{binding.formula_id}:{binding.variable_name}:{binding.source_column_name}"
    )


def _first_text(values: tuple[str, ...]) -> str | None:
    return values[0] if values else None


def _validate_column_candidates(value: object) -> None:
    if not isinstance(value, tuple):
        raise ValueError("column_candidates must be a tuple")
    if any(not isinstance(item, Service1ColumnSemanticCandidateV1) for item in value):
        raise ValueError("column_candidates must contain Service1ColumnSemanticCandidateV1 items")


def _validate_formula_entry(value: object) -> None:
    if not isinstance(value, Service1NormalizedFormulaCatalogEntryV1):
        raise ValueError("formula_entry must be a Service1NormalizedFormulaCatalogEntryV1")


def _validate_formula_entries(value: object) -> None:
    if not isinstance(value, tuple):
        raise ValueError("formula_entries must be a tuple")
    if any(not isinstance(item, Service1NormalizedFormulaCatalogEntryV1) for item in value):
        raise ValueError("formula_entries must contain Service1NormalizedFormulaCatalogEntryV1 items")


def _validate_pathology_entry(value: object) -> None:
    if not isinstance(value, Service1NormalizedPathologyCatalogEntryV1):
        raise ValueError("pathology_entry must be a Service1NormalizedPathologyCatalogEntryV1")


def _validate_pathology_entries(value: object) -> None:
    if not isinstance(value, tuple):
        raise ValueError("pathology_entries must be a tuple")
    if any(not isinstance(item, Service1NormalizedPathologyCatalogEntryV1) for item in value):
        raise ValueError("pathology_entries must contain Service1NormalizedPathologyCatalogEntryV1 items")


def _validate_bindings(value: object) -> None:
    if not isinstance(value, tuple):
        raise ValueError("bindings must be a tuple")
    if any(not isinstance(item, Service1ColumnVariableBindingV1) for item in value):
        raise ValueError("bindings must contain Service1ColumnVariableBindingV1 items")


def _validate_owner_questions(value: object) -> None:
    if not isinstance(value, tuple):
        raise ValueError("owner_questions must be a tuple")
    if any(not isinstance(item, Service1SemanticOwnerQuestionV1) for item in value):
        raise ValueError("owner_questions must contain Service1SemanticOwnerQuestionV1 items")


__all__ = [
    "build_service_1_column_variable_bindings_v1",
    "build_service_1_semantic_owner_questions_v1",
    "build_service_1_pathology_formula_candidate_v1",
    "build_service_1_semantic_evidence_binding_result_v1",
]

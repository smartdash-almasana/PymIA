from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal


SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

BINDING_STATUS_BOUND_CONFIRMED: Final[str] = "BOUND_CONFIRMED"
BINDING_STATUS_BOUND_CANDIDATE: Final[str] = "BOUND_CANDIDATE"
BINDING_STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"
BINDING_STATUS_MISSING_REQUIRED_COLUMN: Final[str] = "MISSING_REQUIRED_COLUMN"
BINDING_STATUS_AMBIGUOUS: Final[str] = "AMBIGUOUS"
BINDING_STATUS_BLOCKED: Final[str] = "BLOCKED"

ALLOWED_BINDING_STATUSES: Final[tuple[str, ...]] = (
    BINDING_STATUS_BOUND_CONFIRMED,
    BINDING_STATUS_BOUND_CANDIDATE,
    BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
    BINDING_STATUS_MISSING_REQUIRED_COLUMN,
    BINDING_STATUS_AMBIGUOUS,
    BINDING_STATUS_BLOCKED,
)

PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE: Final[str] = "FORMULA_READY_CANDIDATE"
PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS: Final[str] = "NEEDS_VARIABLE_BINDINGS"
PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"
PATHOLOGY_FORMULA_STATUS_BLOCKED_INSUFFICIENT_EVIDENCE: Final[str] = "BLOCKED_INSUFFICIENT_EVIDENCE"
PATHOLOGY_FORMULA_STATUS_BLOCKED_UNSUPPORTED_FORMULA: Final[str] = "BLOCKED_UNSUPPORTED_FORMULA"
PATHOLOGY_FORMULA_STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY: Final[str] = "BLOCKED_UNSUPPORTED_PATHOLOGY"

ALLOWED_PATHOLOGY_FORMULA_STATUSES: Final[tuple[str, ...]] = (
    PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE,
    PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS,
    PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION,
    PATHOLOGY_FORMULA_STATUS_BLOCKED_INSUFFICIENT_EVIDENCE,
    PATHOLOGY_FORMULA_STATUS_BLOCKED_UNSUPPORTED_FORMULA,
    PATHOLOGY_FORMULA_STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
)

STATUS_READY_FOR_COMPUTATION_CANDIDATE: Final[str] = "SEMANTIC_BINDING_READY_FOR_COMPUTATION_CANDIDATE"
STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION: Final[str] = "NEEDS_OWNER_COLUMN_CONFIRMATION"
STATUS_NEEDS_FORMULA_INPUTS: Final[str] = "NEEDS_FORMULA_INPUTS"
STATUS_NEEDS_PATHOLOGY_DISAMBIGUATION: Final[str] = "NEEDS_PATHOLOGY_DISAMBIGUATION"
STATUS_BLOCKED_INSUFFICIENT_EVIDENCE: Final[str] = "BLOCKED_INSUFFICIENT_EVIDENCE"
STATUS_BLOCKED_UNSUPPORTED_FORMULA: Final[str] = "BLOCKED_UNSUPPORTED_FORMULA"
STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY: Final[str] = "BLOCKED_UNSUPPORTED_PATHOLOGY"

ALLOWED_RESULT_STATUSES: Final[tuple[str, ...]] = (
    STATUS_READY_FOR_COMPUTATION_CANDIDATE,
    STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION,
    STATUS_NEEDS_FORMULA_INPUTS,
    STATUS_NEEDS_PATHOLOGY_DISAMBIGUATION,
    STATUS_BLOCKED_INSUFFICIENT_EVIDENCE,
    STATUS_BLOCKED_UNSUPPORTED_FORMULA,
    STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
)

ColumnVariableBindingStatusV1 = Literal[
    "BOUND_CONFIRMED",
    "BOUND_CANDIDATE",
    "NEEDS_OWNER_CONFIRMATION",
    "MISSING_REQUIRED_COLUMN",
    "AMBIGUOUS",
    "BLOCKED",
]

PathologyFormulaCandidateStatusV1 = Literal[
    "FORMULA_READY_CANDIDATE",
    "NEEDS_VARIABLE_BINDINGS",
    "NEEDS_OWNER_CONFIRMATION",
    "BLOCKED_INSUFFICIENT_EVIDENCE",
    "BLOCKED_UNSUPPORTED_FORMULA",
    "BLOCKED_UNSUPPORTED_PATHOLOGY",
]

SemanticEvidenceBindingStatusV1 = Literal[
    "SEMANTIC_BINDING_READY_FOR_COMPUTATION_CANDIDATE",
    "NEEDS_OWNER_COLUMN_CONFIRMATION",
    "NEEDS_FORMULA_INPUTS",
    "NEEDS_PATHOLOGY_DISAMBIGUATION",
    "BLOCKED_INSUFFICIENT_EVIDENCE",
    "BLOCKED_UNSUPPORTED_FORMULA",
    "BLOCKED_UNSUPPORTED_PATHOLOGY",
]


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, (list, set)):
        return tuple(value)
    return (value,)


def _clean_text_tuple(value: Any) -> tuple[str, ...]:
    cleaned: list[str] = []
    for item in _clean_tuple(value):
        text = _clean_optional_text(item)
        if text:
            cleaned.append(text)
    return tuple(cleaned)


def _validate_status(value: str, *, allowed: tuple[str, ...], field_name: str) -> str:
    value = _required_text(value, field_name=field_name)
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of: {', '.join(allowed)}")
    return value


def _validate_confidence(value: float) -> float:
    confidence = float(value)
    if confidence < 0 or confidence > 1:
        raise ValueError("confidence must be between 0 and 1")
    return confidence


def _fail_closed_flag(value: bool, *, field_name: str) -> bool:
    if value is not False:
        raise ValueError(f"{field_name} must remain False in {SCHEMA_VERSION}")
    return False


@dataclass(frozen=True)
class Service1ColumnSemanticCandidateV1:
    source_column_name: str
    normalized_column_name: str
    sheet_name: str | None
    observed_data_type: str | None
    sample_values: tuple[Any, ...]
    candidate_semantic_roles: tuple[str, ...]
    candidate_variable_names: tuple[str, ...]
    confidence: float
    ambiguity_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_column_name", _required_text(self.source_column_name, field_name="source_column_name"))
        object.__setattr__(self, "normalized_column_name", _required_text(self.normalized_column_name, field_name="normalized_column_name"))
        object.__setattr__(self, "sheet_name", _clean_optional_text(self.sheet_name))
        object.__setattr__(self, "observed_data_type", _clean_optional_text(self.observed_data_type))
        object.__setattr__(self, "sample_values", _clean_tuple(self.sample_values))
        object.__setattr__(self, "candidate_semantic_roles", _clean_text_tuple(self.candidate_semantic_roles))
        object.__setattr__(self, "candidate_variable_names", _clean_text_tuple(self.candidate_variable_names))
        object.__setattr__(self, "confidence", _validate_confidence(self.confidence))
        object.__setattr__(self, "ambiguity_reason", _clean_optional_text(self.ambiguity_reason))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1FormulaVariableRequirementV1:
    formula_id: str
    variable_name: str
    required: bool
    accepted_semantic_roles: tuple[str, ...]
    accepted_data_types: tuple[str, ...]
    required_grain: str | None
    required_unit: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "formula_id", _required_text(self.formula_id, field_name="formula_id"))
        object.__setattr__(self, "variable_name", _required_text(self.variable_name, field_name="variable_name"))
        object.__setattr__(self, "accepted_semantic_roles", _clean_text_tuple(self.accepted_semantic_roles))
        object.__setattr__(self, "accepted_data_types", _clean_text_tuple(self.accepted_data_types))
        object.__setattr__(self, "required_grain", _clean_optional_text(self.required_grain))
        object.__setattr__(self, "required_unit", _clean_optional_text(self.required_unit))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnVariableBindingV1:
    source_column_name: str
    variable_name: str
    formula_id: str
    binding_status: ColumnVariableBindingStatusV1
    semantic_role: str | None
    confidence: float
    owner_confirmed: bool
    blocking_reason: str | None
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_column_name", _required_text(self.source_column_name, field_name="source_column_name"))
        object.__setattr__(self, "variable_name", _required_text(self.variable_name, field_name="variable_name"))
        object.__setattr__(self, "formula_id", _required_text(self.formula_id, field_name="formula_id"))
        object.__setattr__(self, "binding_status", _validate_status(self.binding_status, allowed=ALLOWED_BINDING_STATUSES, field_name="binding_status"))
        object.__setattr__(self, "semantic_role", _clean_optional_text(self.semantic_role))
        object.__setattr__(self, "confidence", _validate_confidence(self.confidence))
        object.__setattr__(self, "blocking_reason", _clean_optional_text(self.blocking_reason))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1PathologyFormulaCandidateV1:
    pathology_code: str
    formula_id: str
    candidate_status: PathologyFormulaCandidateStatusV1
    required_variables: tuple[str, ...]
    bound_variables: tuple[str, ...]
    missing_variables: tuple[str, ...]
    ambiguous_variables: tuple[str, ...]
    owner_questions: tuple[str, ...]
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "pathology_code", _required_text(self.pathology_code, field_name="pathology_code"))
        object.__setattr__(self, "formula_id", _required_text(self.formula_id, field_name="formula_id"))
        object.__setattr__(self, "candidate_status", _validate_status(self.candidate_status, allowed=ALLOWED_PATHOLOGY_FORMULA_STATUSES, field_name="candidate_status"))
        object.__setattr__(self, "required_variables", _clean_text_tuple(self.required_variables))
        object.__setattr__(self, "bound_variables", _clean_text_tuple(self.bound_variables))
        object.__setattr__(self, "missing_variables", _clean_text_tuple(self.missing_variables))
        object.__setattr__(self, "ambiguous_variables", _clean_text_tuple(self.ambiguous_variables))
        object.__setattr__(self, "owner_questions", _clean_text_tuple(self.owner_questions))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1SemanticOwnerQuestionV1:
    question_ref: str
    question_text: str
    target_column_name: str | None
    target_variable_name: str | None
    target_formula_id: str | None
    reason: str
    answer_type: str
    required: bool
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "question_ref", _required_text(self.question_ref, field_name="question_ref"))
        object.__setattr__(self, "question_text", _required_text(self.question_text, field_name="question_text"))
        object.__setattr__(self, "target_column_name", _clean_optional_text(self.target_column_name))
        object.__setattr__(self, "target_variable_name", _clean_optional_text(self.target_variable_name))
        object.__setattr__(self, "target_formula_id", _clean_optional_text(self.target_formula_id))
        object.__setattr__(self, "reason", _required_text(self.reason, field_name="reason"))
        object.__setattr__(self, "answer_type", _required_text(self.answer_type, field_name="answer_type"))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1SemanticEvidenceBindingResultV1:
    schema_version: str
    service_name: str
    case_id: str
    status: SemanticEvidenceBindingStatusV1
    column_candidates: tuple[Service1ColumnSemanticCandidateV1, ...]
    formula_requirements: tuple[Service1FormulaVariableRequirementV1, ...]
    bindings: tuple[Service1ColumnVariableBindingV1, ...]
    pathology_formula_candidates: tuple[Service1PathologyFormulaCandidateV1, ...]
    owner_questions: tuple[Service1SemanticOwnerQuestionV1, ...]
    ready_formula_ids: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _required_text(self.schema_version, field_name="schema_version"))
        object.__setattr__(self, "service_name", _required_text(self.service_name, field_name="service_name"))
        object.__setattr__(self, "case_id", _required_text(self.case_id, field_name="case_id"))
        object.__setattr__(self, "status", _validate_status(self.status, allowed=ALLOWED_RESULT_STATUSES, field_name="status"))
        object.__setattr__(self, "column_candidates", tuple(self.column_candidates or ()))
        object.__setattr__(self, "formula_requirements", tuple(self.formula_requirements or ()))
        object.__setattr__(self, "bindings", tuple(self.bindings or ()))
        object.__setattr__(self, "pathology_formula_candidates", tuple(self.pathology_formula_candidates or ()))
        object.__setattr__(self, "owner_questions", tuple(self.owner_questions or ()))
        object.__setattr__(self, "ready_formula_ids", _clean_text_tuple(self.ready_formula_ids))
        object.__setattr__(self, "blocked_reasons", _clean_text_tuple(self.blocked_reasons))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_service_1_semantic_binding_status_v1(
    *,
    owner_questions: list[Service1SemanticOwnerQuestionV1] | tuple[Service1SemanticOwnerQuestionV1, ...] | None = None,
    ready_formula_ids: list[str] | tuple[str, ...] | None = None,
    blocked_reasons: list[str] | tuple[str, ...] | None = None,
) -> SemanticEvidenceBindingStatusV1:
    blocked = _clean_text_tuple(blocked_reasons)
    if blocked:
        return STATUS_BLOCKED_INSUFFICIENT_EVIDENCE
    if tuple(owner_questions or ()):
        return STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION
    if _clean_text_tuple(ready_formula_ids):
        return STATUS_READY_FOR_COMPUTATION_CANDIDATE
    return STATUS_NEEDS_FORMULA_INPUTS


def build_service_1_semantic_evidence_binding_result_v1(
    *,
    case_id: str,
    status: str | None = None,
    column_candidates: list[Service1ColumnSemanticCandidateV1] | tuple[Service1ColumnSemanticCandidateV1, ...] | None = None,
    formula_requirements: list[Service1FormulaVariableRequirementV1] | tuple[Service1FormulaVariableRequirementV1, ...] | None = None,
    bindings: list[Service1ColumnVariableBindingV1] | tuple[Service1ColumnVariableBindingV1, ...] | None = None,
    pathology_formula_candidates: list[Service1PathologyFormulaCandidateV1] | tuple[Service1PathologyFormulaCandidateV1, ...] | None = None,
    owner_questions: list[Service1SemanticOwnerQuestionV1] | tuple[Service1SemanticOwnerQuestionV1, ...] | None = None,
    ready_formula_ids: list[str] | tuple[str, ...] | None = None,
    blocked_reasons: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1SemanticEvidenceBindingResultV1:
    resolved_status = status or resolve_service_1_semantic_binding_status_v1(
        owner_questions=owner_questions,
        ready_formula_ids=ready_formula_ids,
        blocked_reasons=blocked_reasons,
    )
    return Service1SemanticEvidenceBindingResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=case_id,
        status=resolved_status,  # type: ignore[arg-type]
        column_candidates=tuple(column_candidates or ()),
        formula_requirements=tuple(formula_requirements or ()),
        bindings=tuple(bindings or ()),
        pathology_formula_candidates=tuple(pathology_formula_candidates or ()),
        owner_questions=tuple(owner_questions or ()),
        ready_formula_ids=_clean_text_tuple(ready_formula_ids),
        blocked_reasons=_clean_text_tuple(blocked_reasons),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "BINDING_STATUS_BOUND_CONFIRMED",
    "BINDING_STATUS_BOUND_CANDIDATE",
    "BINDING_STATUS_NEEDS_OWNER_CONFIRMATION",
    "BINDING_STATUS_MISSING_REQUIRED_COLUMN",
    "BINDING_STATUS_AMBIGUOUS",
    "BINDING_STATUS_BLOCKED",
    "ALLOWED_BINDING_STATUSES",
    "PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE",
    "PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS",
    "PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION",
    "PATHOLOGY_FORMULA_STATUS_BLOCKED_INSUFFICIENT_EVIDENCE",
    "PATHOLOGY_FORMULA_STATUS_BLOCKED_UNSUPPORTED_FORMULA",
    "PATHOLOGY_FORMULA_STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY",
    "ALLOWED_PATHOLOGY_FORMULA_STATUSES",
    "STATUS_READY_FOR_COMPUTATION_CANDIDATE",
    "STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION",
    "STATUS_NEEDS_FORMULA_INPUTS",
    "STATUS_NEEDS_PATHOLOGY_DISAMBIGUATION",
    "STATUS_BLOCKED_INSUFFICIENT_EVIDENCE",
    "STATUS_BLOCKED_UNSUPPORTED_FORMULA",
    "STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY",
    "ALLOWED_RESULT_STATUSES",
    "Service1ColumnSemanticCandidateV1",
    "Service1FormulaVariableRequirementV1",
    "Service1ColumnVariableBindingV1",
    "Service1PathologyFormulaCandidateV1",
    "Service1SemanticOwnerQuestionV1",
    "Service1SemanticEvidenceBindingResultV1",
    "resolve_service_1_semantic_binding_status_v1",
    "build_service_1_semantic_evidence_binding_result_v1",
]

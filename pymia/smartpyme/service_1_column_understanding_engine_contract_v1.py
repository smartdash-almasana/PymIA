"""Service 1 — Column Understanding Engine contract V1.

Pure contract module. No I/O. No LLM. No delivery. No runtime. No tool
execution. No mutation of inputs. Fail-closed.

Defines the deterministic output shape of the column understanding engine
for a single column. The engine that materializes this contract lives in
``service_1_column_understanding_engine_v1.py`` and must remain the only
producer of ``Service1ColumnUnderstandingV1`` instances.

The contract is intentionally decoupled from the 13 closed Service 1
chain links and from any orchestrator. It is observable, serializable,
and stable enough to be referenced by future integration layers without
leaking permissions or business decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal


SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_ENGINE_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

MAX_SAMPLE_VALUES: Final[int] = 5
MAX_CANDIDATE_MEANINGS: Final[int] = 3
MAX_ALTERNATIVES: Final[int] = 2
MAX_OWNER_ANSWER_OPTIONS: Final[int] = 4

MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS: Final[float] = 0.6
MIN_CONFIDENCE_FOR_OWNER_QUESTION: Final[float] = 0.6
HIGH_CONFIDENCE_THRESHOLD: Final[float] = 0.8

ALLOWED_INFERRED_DATA_TYPES: Final[tuple[str, ...]] = (
    "number",
    "date",
    "text",
    "empty",
    "mixed",
)

UnderstandingConfidenceBandV1 = Literal["high", "medium", "low", "unknown"]
ALLOWED_UNDERSTANDING_CONFIDENCE_BANDS: Final[tuple[str, ...]] = (
    "high",
    "medium",
    "low",
    "unknown",
)

INFERRED_DATA_TYPE_NUMBER: Final[str] = "number"
INFERRED_DATA_TYPE_DATE: Final[str] = "date"
INFERRED_DATA_TYPE_TEXT: Final[str] = "text"
INFERRED_DATA_TYPE_EMPTY: Final[str] = "empty"
INFERRED_DATA_TYPE_MIXED: Final[str] = "mixed"

SEMANTIC_ROLE_UNKNOWN: Final[str] = "unknown"
VARIABLE_NAME_UNKNOWN: Final[str] = "unknown"

OWNER_ANSWER_OTHER: Final[str] = "OTHER"


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_sample_values(value: Any, *, field_name: str) -> tuple[Any, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field_name} must be a list or tuple")
    cleaned: list[Any] = []
    for index, item in enumerate(value):
        if item is None:
            continue
        if isinstance(item, str) and not item.strip():
            continue
        cleaned.append(item)
        if len(cleaned) >= MAX_SAMPLE_VALUES:
            break
    return tuple(cleaned)


def _clean_text_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field_name} must be a list or tuple of strings")
    cleaned: list[str] = []
    for index, item in enumerate(value):
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        cleaned.append(text)
    return tuple(cleaned)


def _validate_confidence(value: float, *, field_name: str) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number between 0 and 1") from exc
    if confidence < 0 or confidence > 1:
        raise ValueError(f"{field_name} must be between 0 and 1")
    return confidence


def _validate_inferred_data_type(value: str, *, field_name: str) -> str:
    cleaned = _required_text(value, field_name=field_name).lower()
    if cleaned not in ALLOWED_INFERRED_DATA_TYPES:
        raise ValueError(
            f"{field_name} must be one of: {', '.join(ALLOWED_INFERRED_DATA_TYPES)}"
        )
    return cleaned


def _fail_closed_flag(value: bool, *, field_name: str) -> bool:
    if value is not False:
        raise ValueError(
            f"{field_name} must remain False in {SCHEMA_VERSION} (fail-closed)"
        )
    return False


@dataclass(frozen=True)
class Service1ColumnUnderstandingHypothesisV1:
    semantic_role: str
    variable_name: str
    score: float
    rationale: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "semantic_role",
            _required_text(self.semantic_role, field_name="semantic_role"),
        )
        object.__setattr__(
            self,
            "variable_name",
            _required_text(self.variable_name, field_name="variable_name"),
        )
        object.__setattr__(
            self,
            "score",
            _validate_confidence(self.score, field_name="score"),
        )
        object.__setattr__(
            self,
            "rationale",
            _clean_optional_text(self.rationale),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnOwnerAnswerOptionV1:
    option_id: str
    label: str
    description: str
    linked_hypothesis: Service1ColumnUnderstandingHypothesisV1 | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "option_id",
            _required_text(self.option_id, field_name="option_id"),
        )
        object.__setattr__(
            self,
            "label",
            _required_text(self.label, field_name="label"),
        )
        object.__setattr__(
            self,
            "description",
            _required_text(self.description, field_name="description"),
        )
        if self.linked_hypothesis is not None and not isinstance(
            self.linked_hypothesis, Service1ColumnUnderstandingHypothesisV1
        ):
            raise ValueError(
                "linked_hypothesis must be a Service1ColumnUnderstandingHypothesisV1 or None"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnUnderstandingV1:
    column_name: str
    sheet_name: str
    sample_values: tuple[Any, ...]
    inferred_data_type: str
    normalized_header: str
    candidate_meanings: tuple[Service1ColumnUnderstandingHypothesisV1, ...]
    primary_hypothesis: Service1ColumnUnderstandingHypothesisV1 | None
    confidence: float
    evidence: tuple[str, ...]
    alternatives: tuple[Service1ColumnUnderstandingHypothesisV1, ...]
    risk_if_wrong: str
    owner_question_needed: bool
    owner_question_text: str | None
    allowed_owner_answers: tuple[Service1ColumnOwnerAnswerOptionV1, ...]
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "column_name",
            _required_text(self.column_name, field_name="column_name"),
        )
        object.__setattr__(
            self,
            "sheet_name",
            _required_text(self.sheet_name, field_name="sheet_name"),
        )
        object.__setattr__(
            self,
            "sample_values",
            _clean_sample_values(self.sample_values, field_name="sample_values"),
        )
        object.__setattr__(
            self,
            "inferred_data_type",
            _validate_inferred_data_type(
                self.inferred_data_type, field_name="inferred_data_type"
            ),
        )
        object.__setattr__(
            self,
            "normalized_header",
            _required_text(self.normalized_header, field_name="normalized_header"),
        )
        object.__setattr__(
            self,
            "candidate_meanings",
            tuple(self.candidate_meanings or ()),
        )
        if self.primary_hypothesis is not None and not isinstance(
            self.primary_hypothesis, Service1ColumnUnderstandingHypothesisV1
        ):
            raise ValueError(
                "primary_hypothesis must be a Service1ColumnUnderstandingHypothesisV1 or None"
            )
        object.__setattr__(
            self,
            "confidence",
            _validate_confidence(self.confidence, field_name="confidence"),
        )
        object.__setattr__(
            self,
            "evidence",
            _clean_text_tuple(self.evidence, field_name="evidence"),
        )
        object.__setattr__(
            self,
            "alternatives",
            tuple(self.alternatives or ()),
        )
        if not isinstance(self.risk_if_wrong, str):
            raise ValueError("risk_if_wrong must be a string")
        object.__setattr__(
            self,
            "owner_question_needed",
            bool(self.owner_question_needed),
        )
        object.__setattr__(
            self,
            "owner_question_text",
            _clean_optional_text(self.owner_question_text),
        )
        object.__setattr__(
            self,
            "allowed_owner_answers",
            tuple(self.allowed_owner_answers or ()),
        )
        object.__setattr__(
            self,
            "runtime_authorized",
            _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"),
        )
        object.__setattr__(
            self,
            "tool_execution_authorized",
            _fail_closed_flag(
                self.tool_execution_authorized,
                field_name="tool_execution_authorized",
            ),
        )
        object.__setattr__(
            self,
            "delivery_authorized",
            _fail_closed_flag(
                self.delivery_authorized, field_name="delivery_authorized"
            ),
        )
        object.__setattr__(
            self,
            "diagnosis_generated",
            _fail_closed_flag(
                self.diagnosis_generated, field_name="diagnosis_generated"
            ),
        )
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

        _validate_invariants(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_invariants(value: Service1ColumnUnderstandingV1) -> None:
    if len(value.candidate_meanings) > MAX_CANDIDATE_MEANINGS:
        raise ValueError(
            f"candidate_meanings accepts at most {MAX_CANDIDATE_MEANINGS} items"
        )
    if len(value.alternatives) > MAX_ALTERNATIVES:
        raise ValueError(
            f"alternatives accepts at most {MAX_ALTERNATIVES} items"
        )
    if len(value.allowed_owner_answers) > MAX_OWNER_ANSWER_OPTIONS:
        raise ValueError(
            f"allowed_owner_answers accepts at most {MAX_OWNER_ANSWER_OPTIONS} items"
        )
    if value.owner_question_needed:
        if not value.owner_question_text:
            raise ValueError(
                "owner_question_text is required when owner_question_needed is True"
            )
        if not value.allowed_owner_answers:
            raise ValueError(
                "allowed_owner_answers must be non-empty when owner_question_needed is True"
            )
    else:
        if value.owner_question_text is not None:
            raise ValueError(
                "owner_question_text must be None when owner_question_needed is False"
            )
        if value.allowed_owner_answers:
            raise ValueError(
                "allowed_owner_answers must be empty when owner_question_needed is False"
            )
    if value.primary_hypothesis is not None and value.primary_hypothesis not in value.candidate_meanings:
        raise ValueError(
            "primary_hypothesis must be one of the candidate_meanings"
        )
    for alternative in value.alternatives:
        if alternative not in value.candidate_meanings:
            raise ValueError(
                "alternatives must be a subset of candidate_meanings"
            )
    if value.primary_hypothesis is not None:
        for alternative in value.alternatives:
            if alternative == value.primary_hypothesis:
                raise ValueError(
                    "primary_hypothesis cannot also appear in alternatives"
                )
    seen_signatures: set[tuple[str, str]] = set()
    for hypothesis in value.candidate_meanings:
        signature = (hypothesis.semantic_role, hypothesis.variable_name)
        if signature in seen_signatures:
            raise ValueError(
                "candidate_meanings must not contain duplicate (semantic_role, variable_name) pairs"
            )
        seen_signatures.add(signature)
    option_ids = [option.option_id for option in value.allowed_owner_answers]
    if len(set(option_ids)) != len(option_ids):
        raise ValueError("allowed_owner_answers must have unique option_id values")


def confidence_band_v1(confidence: float) -> UnderstandingConfidenceBandV1:
    if confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    if confidence >= MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS:
        return "medium"
    if confidence > 0:
        return "low"
    return "unknown"


def build_service_1_column_understanding_v1(
    *,
    column_name: str,
    sheet_name: str,
    sample_values: list[Any] | tuple[Any, ...] | None = None,
    inferred_data_type: str,
    normalized_header: str,
    candidate_meanings: list[Service1ColumnUnderstandingHypothesisV1]
    | tuple[Service1ColumnUnderstandingHypothesisV1, ...]
    | None = None,
    primary_hypothesis: Service1ColumnUnderstandingHypothesisV1 | None = None,
    confidence: float,
    evidence: list[str] | tuple[str, ...] | None = None,
    alternatives: list[Service1ColumnUnderstandingHypothesisV1]
    | tuple[Service1ColumnUnderstandingHypothesisV1, ...]
    | None = None,
    risk_if_wrong: str,
    owner_question_needed: bool,
    owner_question_text: str | None = None,
    allowed_owner_answers: list[Service1ColumnOwnerAnswerOptionV1]
    | tuple[Service1ColumnOwnerAnswerOptionV1, ...]
    | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnUnderstandingV1:
    """Build a column understanding instance with full fail-closed validation.

    The constructor enforces all contract invariants in one place. The
    engine module is expected to populate every field deliberately; any
    silent defaults here would defeat the purpose of the contract.
    """
    return Service1ColumnUnderstandingV1(
        column_name=column_name,
        sheet_name=sheet_name,
        sample_values=tuple(sample_values or ()),
        inferred_data_type=inferred_data_type,
        normalized_header=normalized_header,
        candidate_meanings=tuple(candidate_meanings or ()),
        primary_hypothesis=primary_hypothesis,
        confidence=confidence,
        evidence=tuple(evidence or ()),
        alternatives=tuple(alternatives or ()),
        risk_if_wrong=risk_if_wrong,
        owner_question_needed=owner_question_needed,
        owner_question_text=owner_question_text,
        allowed_owner_answers=tuple(allowed_owner_answers or ()),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "MAX_SAMPLE_VALUES",
    "MAX_CANDIDATE_MEANINGS",
    "MAX_ALTERNATIVES",
    "MAX_OWNER_ANSWER_OPTIONS",
    "MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS",
    "MIN_CONFIDENCE_FOR_OWNER_QUESTION",
    "HIGH_CONFIDENCE_THRESHOLD",
    "ALLOWED_INFERRED_DATA_TYPES",
    "ALLOWED_UNDERSTANDING_CONFIDENCE_BANDS",
    "INFERRED_DATA_TYPE_NUMBER",
    "INFERRED_DATA_TYPE_DATE",
    "INFERRED_DATA_TYPE_TEXT",
    "INFERRED_DATA_TYPE_EMPTY",
    "INFERRED_DATA_TYPE_MIXED",
    "SEMANTIC_ROLE_UNKNOWN",
    "VARIABLE_NAME_UNKNOWN",
    "OWNER_ANSWER_OTHER",
    "Service1ColumnUnderstandingHypothesisV1",
    "Service1ColumnOwnerAnswerOptionV1",
    "Service1ColumnUnderstandingV1",
    "confidence_band_v1",
    "build_service_1_column_understanding_v1",
]

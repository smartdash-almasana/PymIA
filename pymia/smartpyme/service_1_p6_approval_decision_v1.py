"""Canonical P6 semantic approval authority for Servicio 1 Stage 2 Package 3.

P6 decides semantic meaning only. It consumes semantic hypotheses plus optional
owner-confirmation evidence and emits one decision per column. It never selects
capabilities, formulas or pathologies; never decides computability; and never
authorizes execution, product readiness, delivery or diagnosis.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)

SCHEMA_VERSION = "SERVICE_1_P6_APPROVAL_DECISION_V1"

STATUS_APPROVED = "APPROVED"
STATUS_NEEDS_OWNER_CONFIRMATION = "NEEDS_OWNER_CONFIRMATION"
STATUS_AMBIGUOUS = "AMBIGUOUS"
STATUS_BLOCKED = "BLOCKED"
ALLOWED_STATUSES = frozenset(
    {
        STATUS_APPROVED,
        STATUS_NEEDS_OWNER_CONFIRMATION,
        STATUS_AMBIGUOUS,
        STATUS_BLOCKED,
    }
)

_SCOPE_SEMANTIC_ROLE = "SEMANTIC_ROLE"
_SCOPE_COLUMN_EXCLUSION = "COLUMN_EXCLUSION"
_SCOPE_FREE_TEXT_MEANING = "FREE_TEXT_MEANING"


@dataclass(frozen=True)
class Service1P6ApprovalDecisionV1:
    case_id: str
    sheet_ref: str
    column_ref: str
    status: str
    approved_role: str | None
    approved_variable: str | None
    reason: str
    owner_confirmation_question_ref: str | None = None
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("case_id", "sheet_ref", "column_ref", "status", "reason"):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError("invalid P6 status")
        if self.status == STATUS_APPROVED and not str(self.approved_role or "").strip():
            raise ValueError("approved_role is required when P6 status is APPROVED")
        if self.status != STATUS_APPROVED and (
            self.approved_role is not None or self.approved_variable is not None
        ):
            raise ValueError("non-approved P6 decisions cannot carry approved meaning")
        if self.confidence is not None and not 0 <= float(self.confidence) <= 1:
            raise ValueError("confidence must be between 0 and 1")
        forbidden = {
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
            "computation_candidate_ready",
            "formula_id",
            "pathology_code",
            "requested_capability",
        }
        if forbidden.intersection(self.provenance):
            raise ValueError("P6 provenance cannot carry downstream authority")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["provenance"] = dict(self.provenance)
        payload.update(
            {
                "runtime_authorized": False,
                "tool_execution_authorized": False,
                "product_ready": False,
                "delivery_authorized": False,
                "diagnosis_generated": False,
            }
        )
        return payload


def build_service_1_p6_approval_decision_v1(
    *,
    case_id: str,
    candidate: Service1ColumnSemanticCandidateV1,
    owner_confirmation_events: Iterable[Mapping[str, Any]] | None = None,
) -> Service1P6ApprovalDecisionV1:
    """Resolve semantic approval for one column, fail-closed."""
    if not isinstance(candidate, Service1ColumnSemanticCandidateV1):
        raise TypeError("candidate must be Service1ColumnSemanticCandidateV1")

    case = str(case_id or "").strip()
    if not case:
        raise ValueError("case_id is required")
    sheet = str(candidate.sheet_name or "sheet1").strip()
    column = candidate.source_column_name
    ref_id = _candidate_ref_id(candidate)

    relevant_events = [
        event
        for event in (owner_confirmation_events or ())
        if isinstance(event, Mapping)
        and event.get("confirmed_by_owner") is True
        and _event_targets_candidate(event, sheet=sheet, column=column, ref_id=ref_id)
    ]
    if len(relevant_events) > 1:
        return _decision(
            case_id=case,
            candidate=candidate,
            status=STATUS_BLOCKED,
            reason="MULTIPLE_OWNER_CONFIRMATION_EVENTS_FOR_COLUMN",
        )

    if relevant_events:
        event = relevant_events[0]
        scope = str(event.get("confirmation_scope") or "").strip()
        question_ref = str(event.get("question_ref") or "").strip() or None
        if scope == _SCOPE_COLUMN_EXCLUSION:
            return _decision(
                case_id=case,
                candidate=candidate,
                status=STATUS_BLOCKED,
                reason="COLUMN_EXCLUDED_BY_OWNER",
                question_ref=question_ref,
            )
        if scope == _SCOPE_FREE_TEXT_MEANING:
            return _decision(
                case_id=case,
                candidate=candidate,
                status=STATUS_AMBIGUOUS,
                reason="OWNER_FREE_TEXT_REQUIRES_GOVERNED_NORMALIZATION",
                question_ref=question_ref,
            )
        if scope != _SCOPE_SEMANTIC_ROLE:
            return _decision(
                case_id=case,
                candidate=candidate,
                status=STATUS_BLOCKED,
                reason="UNSUPPORTED_OWNER_CONFIRMATION_SCOPE",
                question_ref=question_ref,
            )
        confirmed_role = str(event.get("confirmed_role") or "").strip()
        if not confirmed_role:
            return _decision(
                case_id=case,
                candidate=candidate,
                status=STATUS_BLOCKED,
                reason="OWNER_CONFIRMED_ROLE_MISSING",
                question_ref=question_ref,
            )
        approved_variable = _variable_for_role(candidate, confirmed_role)
        if confirmed_role not in candidate.candidate_semantic_roles:
            return _decision(
                case_id=case,
                candidate=candidate,
                status=STATUS_BLOCKED,
                reason="OWNER_CONFIRMED_ROLE_OUTSIDE_HYPOTHESIS",
                question_ref=question_ref,
            )
        return _decision(
            case_id=case,
            candidate=candidate,
            status=STATUS_APPROVED,
            reason="OWNER_CONFIRMED_SEMANTIC_ROLE",
            approved_role=confirmed_role,
            approved_variable=approved_variable,
            question_ref=question_ref,
        )

    roles = tuple(role for role in candidate.candidate_semantic_roles if role != "unknown")
    if candidate.owner_confirmation_required:
        return _decision(
            case_id=case,
            candidate=candidate,
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            reason="SEMANTIC_HYPOTHESIS_REQUIRES_OWNER_CONFIRMATION",
        )
    if not roles:
        return _decision(
            case_id=case,
            candidate=candidate,
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            reason="NO_APPROVABLE_SEMANTIC_ROLE",
        )
    primary_role = str((candidate.metadata or {}).get("primary_semantic_role") or "").strip()
    if primary_role and primary_role in roles:
        role = primary_role
    elif len(roles) == 1:
        role = roles[0]
    else:
        return _decision(
            case_id=case,
            candidate=candidate,
            status=STATUS_AMBIGUOUS,
            reason="MULTIPLE_SEMANTIC_ROLES_WITHOUT_PRIMARY",
        )
    return _decision(
        case_id=case,
        candidate=candidate,
        status=STATUS_NEEDS_OWNER_CONFIRMATION,
        reason="FIRST_CONTACT_OWNER_CONFIRMATION_REQUIRED",
    )


def build_service_1_p6_approval_decisions_v1(
    *,
    case_id: str,
    candidates: Iterable[Service1ColumnSemanticCandidateV1],
    owner_confirmation_events: Iterable[Mapping[str, Any]] | None = None,
) -> tuple[Service1P6ApprovalDecisionV1, ...]:
    events = tuple(owner_confirmation_events or ())
    return tuple(
        build_service_1_p6_approval_decision_v1(
            case_id=case_id,
            candidate=candidate,
            owner_confirmation_events=events,
        )
        for candidate in candidates
    )


def _decision(
    *,
    case_id: str,
    candidate: Service1ColumnSemanticCandidateV1,
    status: str,
    reason: str,
    approved_role: str | None = None,
    approved_variable: str | None = None,
    question_ref: str | None = None,
) -> Service1P6ApprovalDecisionV1:
    return Service1P6ApprovalDecisionV1(
        case_id=case_id,
        sheet_ref=str(candidate.sheet_name or "sheet1").strip(),
        column_ref=candidate.source_column_name,
        status=status,
        approved_role=approved_role,
        approved_variable=approved_variable,
        reason=reason,
        owner_confirmation_question_ref=question_ref,
        confidence=candidate.confidence,
        provenance={
            "source": "semantic_hypothesis_and_owner_evidence",
            "candidate_ref": _candidate_ref_id(candidate),
        },
    )


def _candidate_ref_id(candidate: Service1ColumnSemanticCandidateV1) -> str:
    metadata = dict(candidate.metadata or {})
    return str(
        metadata.get("column_ref_id")
        or metadata.get("question_id")
        or candidate.source_column_name
    ).strip()


def _event_targets_candidate(
    event: Mapping[str, Any], *, sheet: str, column: str, ref_id: str
) -> bool:
    question_ref = str(event.get("question_ref") or "").strip()
    event_sheet = str(event.get("sheet_ref") or "").strip()
    event_column = str(event.get("column_ref") or "").strip()
    return bool(
        (question_ref and question_ref == ref_id)
        or (event_sheet == sheet and event_column == column)
    )


def _variable_for_role(
    candidate: Service1ColumnSemanticCandidateV1, role: str
) -> str | None:
    roles = tuple(candidate.candidate_semantic_roles)
    variables = tuple(candidate.candidate_variable_names)
    if len(roles) == len(variables):
        try:
            return variables[roles.index(role)] or None
        except ValueError:
            return None
    if len(variables) == 1:
        return variables[0]
    return None


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_APPROVED",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_AMBIGUOUS",
    "STATUS_BLOCKED",
    "ALLOWED_STATUSES",
    "Service1P6ApprovalDecisionV1",
    "build_service_1_p6_approval_decision_v1",
    "build_service_1_p6_approval_decisions_v1",
]

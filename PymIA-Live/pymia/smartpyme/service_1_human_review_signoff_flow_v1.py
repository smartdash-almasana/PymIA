from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "SERVICE_1_HUMAN_REVIEW_SIGNOFF_FLOW_V1"
SERVICE_NAME = "SERVICE_1"

DECISION_APPROVED_FOR_DELIVERY = "APPROVED_FOR_DELIVERY"
DECISION_NEEDS_CORRECTION = "NEEDS_CORRECTION"
DECISION_BLOCKED = "BLOCKED"
ALLOWED_DECISIONS = (
    DECISION_APPROVED_FOR_DELIVERY,
    DECISION_NEEDS_CORRECTION,
    DECISION_BLOCKED,
)

STATUS_SIGNED_OFF_FOR_DELIVERY = "SIGNED_OFF_FOR_DELIVERY"
STATUS_NEEDS_CORRECTION = "NEEDS_CORRECTION"
STATUS_BLOCKED = "BLOCKED"
STATUS_REJECTED = "REJECTED"

REJECT_GATE_MISSING = "HUMAN_REVIEW_GATE_MISSING"
REJECT_GATE_NOT_PENDING = "HUMAN_REVIEW_GATE_NOT_PENDING"
REJECT_DECISION_NOT_ALLOWED = "DECISION_NOT_ALLOWED"
REJECT_REVIEWER_MISSING = "REVIEWER_MISSING"
REJECT_FORBIDDEN_CLAIM = "FORBIDDEN_CLAIM"


@dataclass(frozen=True)
class Service1HumanReviewSignoffV1:
    schema_version: str
    service_name: str
    signoff_type: str
    status: str
    decision: str
    reviewer_id: str
    reviewer_role: str
    case_id: str | None
    delivery_status_before: str | None
    delivery_status_after: str
    blocked_reason: str | None
    reviewer_notes: str | None
    correction_required: bool
    delivery_allowed_after_signoff: bool
    runtime_authorized: bool
    human_review_required: bool
    autonomous_use_authorized: bool
    created_at: str
    blocked_claims: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["blocked_claims"] = list(self.blocked_claims)
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _blocked_claims_from_gate(gate: dict[str, Any]) -> tuple[str, ...]:
    raw = gate.get("blocked_claims", [])
    if not isinstance(raw, list):
        return ()
    return tuple(_text(item) for item in raw if _text(item))


def _contains_forbidden_claim(text: str, blocked_claims: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(claim.lower() in normalized for claim in blocked_claims if claim)


def _status_for_decision(decision: str) -> tuple[str, str, bool, bool]:
    if decision == DECISION_APPROVED_FOR_DELIVERY:
        return STATUS_SIGNED_OFF_FOR_DELIVERY, "APPROVED_FOR_HUMAN_SUPERVISED_DELIVERY", False, True
    if decision == DECISION_NEEDS_CORRECTION:
        return STATUS_NEEDS_CORRECTION, "NEEDS_OPERATOR_CORRECTION", True, False
    return STATUS_BLOCKED, "BLOCKED_BY_HUMAN_REVIEW", False, False


def _rejected_packet(*, decision: str, reviewer_id: str, reviewer_role: str, case_id: str | None, delivery_status_before: str | None, blocked_reason: str, blocked_claims: tuple[str, ...], reviewer_notes: str | None, metadata: dict[str, Any] | None) -> Service1HumanReviewSignoffV1:
    return Service1HumanReviewSignoffV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        signoff_type="SERVICE_1_HUMAN_REVIEW_SIGNOFF",
        status=STATUS_REJECTED,
        decision=decision,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        case_id=case_id,
        delivery_status_before=delivery_status_before,
        delivery_status_after="BLOCKED_BY_SIGNOFF_VALIDATION",
        blocked_reason=blocked_reason,
        reviewer_notes=reviewer_notes,
        correction_required=True,
        delivery_allowed_after_signoff=False,
        runtime_authorized=False,
        human_review_required=True,
        autonomous_use_authorized=False,
        created_at=_now_iso(),
        blocked_claims=blocked_claims,
        metadata=dict(metadata or {}),
    )


def apply_service_1_human_review_signoff_v1(*, human_review_gate: dict[str, Any], decision: str, reviewer_id: str, reviewer_role: str | None = None, reviewer_notes: str | None = None, case_id: str | None = None, delivery_status_before: str | None = None, metadata: dict[str, Any] | None = None) -> Service1HumanReviewSignoffV1:
    if not isinstance(human_review_gate, dict):
        return _rejected_packet(decision=_text(decision), reviewer_id=_text(reviewer_id), reviewer_role=_text(reviewer_role) or "unknown", case_id=case_id, delivery_status_before=delivery_status_before, blocked_reason=REJECT_GATE_MISSING, blocked_claims=(), reviewer_notes=reviewer_notes, metadata=metadata)

    decision = _text(decision)
    reviewer_id = _text(reviewer_id)
    reviewer_role = _text(reviewer_role) or _text(human_review_gate.get("reviewer_role")) or "operator_or_accountant"
    reviewer_notes = _text(reviewer_notes) or None
    blocked_claims = _blocked_claims_from_gate(human_review_gate)
    allowed = human_review_gate.get("allowed_decisions", ALLOWED_DECISIONS)
    if not isinstance(allowed, list):
        allowed = list(ALLOWED_DECISIONS)

    gate_status = human_review_gate.get("status")
    if gate_status != "PENDING_HUMAN_REVIEW":
        return _rejected_packet(decision=decision, reviewer_id=reviewer_id, reviewer_role=reviewer_role, case_id=case_id, delivery_status_before=delivery_status_before, blocked_reason=REJECT_GATE_NOT_PENDING, blocked_claims=blocked_claims, reviewer_notes=reviewer_notes, metadata=metadata)
    if decision not in allowed or decision not in ALLOWED_DECISIONS:
        return _rejected_packet(decision=decision, reviewer_id=reviewer_id, reviewer_role=reviewer_role, case_id=case_id, delivery_status_before=delivery_status_before, blocked_reason=REJECT_DECISION_NOT_ALLOWED, blocked_claims=blocked_claims, reviewer_notes=reviewer_notes, metadata=metadata)
    if not reviewer_id:
        return _rejected_packet(decision=decision, reviewer_id=reviewer_id, reviewer_role=reviewer_role, case_id=case_id, delivery_status_before=delivery_status_before, blocked_reason=REJECT_REVIEWER_MISSING, blocked_claims=blocked_claims, reviewer_notes=reviewer_notes, metadata=metadata)
    if reviewer_notes and _contains_forbidden_claim(reviewer_notes, blocked_claims):
        return _rejected_packet(decision=decision, reviewer_id=reviewer_id, reviewer_role=reviewer_role, case_id=case_id, delivery_status_before=delivery_status_before, blocked_reason=REJECT_FORBIDDEN_CLAIM, blocked_claims=blocked_claims, reviewer_notes=reviewer_notes, metadata=metadata)

    status, delivery_status_after, correction_required, delivery_allowed = _status_for_decision(decision)
    return Service1HumanReviewSignoffV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        signoff_type="SERVICE_1_HUMAN_REVIEW_SIGNOFF",
        status=status,
        decision=decision,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        case_id=case_id,
        delivery_status_before=delivery_status_before,
        delivery_status_after=delivery_status_after,
        blocked_reason=None,
        reviewer_notes=reviewer_notes,
        correction_required=correction_required,
        delivery_allowed_after_signoff=delivery_allowed,
        runtime_authorized=False,
        human_review_required=True,
        autonomous_use_authorized=False,
        created_at=_now_iso(),
        blocked_claims=blocked_claims,
        metadata={"hardening_scope": "S1_FULL_ASSISTED_V1_HARDENING", "does_not_reopen_full_assisted_v1_closure": True, **dict(metadata or {})},
    )


__all__ = [
    "SCHEMA_VERSION",
    "DECISION_APPROVED_FOR_DELIVERY",
    "DECISION_NEEDS_CORRECTION",
    "DECISION_BLOCKED",
    "STATUS_SIGNED_OFF_FOR_DELIVERY",
    "STATUS_NEEDS_CORRECTION",
    "STATUS_BLOCKED",
    "STATUS_REJECTED",
    "Service1HumanReviewSignoffV1",
    "apply_service_1_human_review_signoff_v1",
]

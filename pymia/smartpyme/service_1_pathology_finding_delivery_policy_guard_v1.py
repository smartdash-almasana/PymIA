from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_operational_finding_owner_view_v1 import (
    STATUS_OWNER_VIEW_BUILT,
    Service1OperationalFindingOwnerViewV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_FINDING_DELIVERY_POLICY_GUARD_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_POLICY_PASS: Final[str] = "POLICY_PASS"
STATUS_POLICY_BLOCKED: Final[str] = "POLICY_BLOCKED"
STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"
STATUS_BLOCKED_OWNER_VIEW_NOT_BUILT: Final[str] = "BLOCKED_OWNER_VIEW_NOT_BUILT"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_POLICY_PASS,
    STATUS_POLICY_BLOCKED,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_BLOCKED_OWNER_VIEW_NOT_BUILT,
)

GUARD_RESULT_PASS: Final[str] = "PASS"
GUARD_RESULT_BLOCKED: Final[str] = "BLOCKED"
GUARD_RESULT_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"

_PROHIBITED_CLAIMS: Final[tuple[str, ...]] = (
    "diagnóstico definitivo",
    "diagnostico definitivo",
    "certeza absoluta",
    "contabilidad definitiva",
    "saldo real definitivo",
    "inventario real definitivo",
    "rentabilidad global definitiva",
    "auditoría contable",
    "auditoria contable",
    "garantía",
    "garantia",
    "automático sin revisión",
    "automatico sin revision",
    "autónomo",
    "autonomo",
)

PolicyGuardStatusV1 = Literal[
    "POLICY_PASS",
    "POLICY_BLOCKED",
    "NEEDS_OWNER_CONFIRMATION",
    "BLOCKED_OWNER_VIEW_NOT_BUILT",
]


@dataclass(frozen=True)
class Service1PathologyFindingDeliveryPolicyGuardV1:
    schema_version: str
    service_name: str
    status: PolicyGuardStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    pathology_code: str | None
    allowed_computation_ref: str | None
    guard_result: str
    policy_violations: tuple[str, ...]
    required_owner_confirmations: tuple[str, ...]
    delivery_allowed_candidate: bool
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_owner_view(
    operational_finding_owner_view_result: Service1OperationalFindingOwnerViewV1,
) -> Service1OperationalFindingOwnerViewV1:
    if not isinstance(operational_finding_owner_view_result, Service1OperationalFindingOwnerViewV1):
        raise ValueError("operational_finding_owner_view_result must be a Service1OperationalFindingOwnerViewV1")
    return operational_finding_owner_view_result


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _policy_violations(owner_view: Service1OperationalFindingOwnerViewV1) -> tuple[str, ...]:
    summary = _normalize_text(owner_view.finding_summary or "")
    violations: list[str] = []
    for claim in _PROHIBITED_CLAIMS:
        if _normalize_text(claim) in summary:
            violations.append(claim)
    if not owner_view.limits:
        violations.append("missing_explicit_limits")
    return tuple(violations)


def _build_result(
    *,
    owner_view: Service1OperationalFindingOwnerViewV1,
    status: PolicyGuardStatusV1,
    guard_result: str,
    policy_violations: tuple[str, ...],
    required_owner_confirmations: tuple[str, ...],
    delivery_allowed_candidate: bool,
    blocked_reason: str | None,
    owner_confirmation_required: bool,
    metadata: dict[str, Any] | None,
) -> Service1PathologyFindingDeliveryPolicyGuardV1:
    return Service1PathologyFindingDeliveryPolicyGuardV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=owner_view.case_id,
        tenant_id=owner_view.tenant_id,
        intake_id=owner_view.intake_id,
        run_id=owner_view.run_id,
        pathology_code=owner_view.pathology_code,
        allowed_computation_ref=owner_view.allowed_computation_ref,
        guard_result=guard_result,
        policy_violations=policy_violations,
        required_owner_confirmations=required_owner_confirmations,
        delivery_allowed_candidate=delivery_allowed_candidate,
        blocked_reason=blocked_reason,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_pathology_finding_delivery_policy_guard_v1(
    *,
    operational_finding_owner_view_result: Service1OperationalFindingOwnerViewV1,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyFindingDeliveryPolicyGuardV1:
    owner_view = _required_owner_view(operational_finding_owner_view_result)

    if owner_view.status != STATUS_OWNER_VIEW_BUILT:
        return _build_result(
            owner_view=owner_view,
            status=STATUS_BLOCKED_OWNER_VIEW_NOT_BUILT,
            guard_result=GUARD_RESULT_BLOCKED,
            policy_violations=(),
            required_owner_confirmations=(),
            delivery_allowed_candidate=False,
            blocked_reason="owner_view_not_built",
            owner_confirmation_required=True,
            metadata=metadata,
        )

    if owner_view.owner_confirmation_required:
        return _build_result(
            owner_view=owner_view,
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            guard_result=GUARD_RESULT_NEEDS_OWNER_CONFIRMATION,
            policy_violations=(),
            required_owner_confirmations=("owner_confirmation_required",),
            delivery_allowed_candidate=False,
            blocked_reason="owner_confirmation_required",
            owner_confirmation_required=True,
            metadata=metadata,
        )

    policy_violations = _policy_violations(owner_view)
    if policy_violations:
        blocked_reason = (
            "missing_explicit_limits"
            if "missing_explicit_limits" in policy_violations
            else "prohibited_claims_detected"
        )
        return _build_result(
            owner_view=owner_view,
            status=STATUS_POLICY_BLOCKED,
            guard_result=GUARD_RESULT_BLOCKED,
            policy_violations=policy_violations,
            required_owner_confirmations=(),
            delivery_allowed_candidate=False,
            blocked_reason=blocked_reason,
            owner_confirmation_required=False,
            metadata=metadata,
        )

    return _build_result(
        owner_view=owner_view,
        status=STATUS_POLICY_PASS,
        guard_result=GUARD_RESULT_PASS,
        policy_violations=(),
        required_owner_confirmations=(),
        delivery_allowed_candidate=True,
        blocked_reason=None,
        owner_confirmation_required=False,
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_POLICY_PASS",
    "STATUS_POLICY_BLOCKED",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_BLOCKED_OWNER_VIEW_NOT_BUILT",
    "ALLOWED_STATUSES",
    "Service1PathologyFindingDeliveryPolicyGuardV1",
    "build_service_1_pathology_finding_delivery_policy_guard_v1",
]

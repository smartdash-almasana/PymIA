from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_pathology_finding_delivery_policy_guard_v1 import (
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_POLICY_PASS,
    Service1PathologyFindingDeliveryPolicyGuardV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_FINDING_DELIVERY_PACKAGE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT: Final[str] = "DELIVERY_PACKAGE_CANDIDATE_BUILT"
STATUS_BLOCKED_POLICY_NOT_PASS: Final[str] = "BLOCKED_POLICY_NOT_PASS"
STATUS_BLOCKED_OWNER_CONFIRMATION_REQUIRED: Final[str] = "BLOCKED_OWNER_CONFIRMATION_REQUIRED"
STATUS_BLOCKED_EMPTY_PACKAGE: Final[str] = "BLOCKED_EMPTY_PACKAGE"

DeliveryPackageStatusV1 = Literal[
    "DELIVERY_PACKAGE_CANDIDATE_BUILT",
    "BLOCKED_POLICY_NOT_PASS",
    "BLOCKED_OWNER_CONFIRMATION_REQUIRED",
    "BLOCKED_EMPTY_PACKAGE",
]


@dataclass(frozen=True)
class Service1PathologyFindingDeliveryPackageV1:
    schema_version: str
    service_name: str
    status: DeliveryPackageStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    pathology_code: str | None
    allowed_computation_ref: str | None
    package_id: str
    owner_title: str | None
    owner_summary: str | None
    evidence_used: tuple[str, ...]
    computed_values: dict[str, Any]
    limits: tuple[str, ...]
    next_recommended_action: str | None
    policy_guard_status: str
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


def _required_guard(value: Service1PathologyFindingDeliveryPolicyGuardV1) -> Service1PathologyFindingDeliveryPolicyGuardV1:
    if not isinstance(value, Service1PathologyFindingDeliveryPolicyGuardV1):
        raise ValueError("delivery_policy_guard_result must be a Service1PathologyFindingDeliveryPolicyGuardV1")
    return value


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values = value if isinstance(value, (list, tuple, set)) else (value,)
    return tuple(text for item in values if (text := _text(item)))


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _package_id(guard: Service1PathologyFindingDeliveryPolicyGuardV1) -> str:
    pathology = guard.pathology_code or "UNKNOWN_PATHOLOGY"
    return f"s1:xlsx-first:package:{guard.case_id}:{guard.run_id}:{pathology}"


def _material(metadata: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(metadata or {})
    nested = data.get("package_material")
    if isinstance(nested, dict):
        return {**data, **nested}
    return data


def _default_title(guard: Service1PathologyFindingDeliveryPolicyGuardV1) -> str:
    return f"Hallazgo operativo preliminar - {guard.pathology_code or 'UNKNOWN_PATHOLOGY'}"


def _default_summary(guard: Service1PathologyFindingDeliveryPolicyGuardV1) -> str:
    computation = guard.allowed_computation_ref or "cómputo permitido"
    return f"El hallazgo pasó el policy guard y queda estructurado como paquete candidato usando {computation}."


def _default_limits() -> tuple[str, ...]:
    return (
        "Paquete candidato; no representa publicación autónoma.",
        "El alcance queda limitado a la evidencia y al cómputo permitido del caso.",
        "No reemplaza revisión ni decisión del dueño PyME.",
    )


def _default_next_action(guard: Service1PathologyFindingDeliveryPolicyGuardV1) -> str:
    return f"Revisar el paquete candidato antes de cualquier salida final para {guard.pathology_code or 'el caso'}."


def _build(
    *,
    guard: Service1PathologyFindingDeliveryPolicyGuardV1,
    status: DeliveryPackageStatusV1,
    owner_title: str | None,
    owner_summary: str | None,
    evidence_used: tuple[str, ...],
    computed_values: dict[str, Any],
    limits: tuple[str, ...],
    next_recommended_action: str | None,
    delivery_allowed_candidate: bool,
    blocked_reason: str | None,
    owner_confirmation_required: bool,
    metadata: dict[str, Any] | None,
) -> Service1PathologyFindingDeliveryPackageV1:
    return Service1PathologyFindingDeliveryPackageV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=guard.case_id,
        tenant_id=guard.tenant_id,
        intake_id=guard.intake_id,
        run_id=guard.run_id,
        pathology_code=guard.pathology_code,
        allowed_computation_ref=guard.allowed_computation_ref,
        package_id=_package_id(guard),
        owner_title=owner_title,
        owner_summary=owner_summary,
        evidence_used=evidence_used,
        computed_values=computed_values,
        limits=limits,
        next_recommended_action=next_recommended_action,
        policy_guard_status=guard.status,
        delivery_allowed_candidate=delivery_allowed_candidate,
        blocked_reason=blocked_reason,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_pathology_finding_delivery_package_v1(
    *,
    delivery_policy_guard_result: Service1PathologyFindingDeliveryPolicyGuardV1,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyFindingDeliveryPackageV1:
    guard = _required_guard(delivery_policy_guard_result)

    if guard.status != STATUS_POLICY_PASS:
        reason = "policy_not_pass"
        if guard.status == STATUS_NEEDS_OWNER_CONFIRMATION or guard.owner_confirmation_required:
            reason = "owner_confirmation_required"
        return _build(
            guard=guard,
            status=STATUS_BLOCKED_POLICY_NOT_PASS,
            owner_title=None,
            owner_summary=None,
            evidence_used=(),
            computed_values={},
            limits=(),
            next_recommended_action=None,
            delivery_allowed_candidate=False,
            blocked_reason=reason,
            owner_confirmation_required=guard.owner_confirmation_required,
            metadata=metadata,
        )

    if guard.owner_confirmation_required:
        return _build(
            guard=guard,
            status=STATUS_BLOCKED_OWNER_CONFIRMATION_REQUIRED,
            owner_title=None,
            owner_summary=None,
            evidence_used=(),
            computed_values={},
            limits=(),
            next_recommended_action=None,
            delivery_allowed_candidate=False,
            blocked_reason="owner_confirmation_required",
            owner_confirmation_required=True,
            metadata=metadata,
        )

    data = _material(metadata)
    owner_title = _text(data.get("owner_title")) or _default_title(guard)
    owner_summary = _text(data.get("owner_summary")) or _text(data.get("finding_summary")) or _default_summary(guard)
    evidence_used = _tuple(data.get("evidence_used"))
    computed_values = _dict(data.get("computed_values"))
    limits = _tuple(data.get("limits")) or _default_limits()
    next_recommended_action = _text(data.get("next_recommended_action")) or _default_next_action(guard)

    if not owner_title or not owner_summary or not limits:
        return _build(
            guard=guard,
            status=STATUS_BLOCKED_EMPTY_PACKAGE,
            owner_title=owner_title,
            owner_summary=owner_summary,
            evidence_used=evidence_used,
            computed_values=computed_values,
            limits=limits,
            next_recommended_action=next_recommended_action,
            delivery_allowed_candidate=False,
            blocked_reason="empty_package",
            owner_confirmation_required=False,
            metadata=metadata,
        )

    return _build(
        guard=guard,
        status=STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT,
        owner_title=owner_title,
        owner_summary=owner_summary,
        evidence_used=evidence_used,
        computed_values=computed_values,
        limits=limits,
        next_recommended_action=next_recommended_action,
        delivery_allowed_candidate=guard.delivery_allowed_candidate,
        blocked_reason=None,
        owner_confirmation_required=False,
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT",
    "STATUS_BLOCKED_POLICY_NOT_PASS",
    "STATUS_BLOCKED_OWNER_CONFIRMATION_REQUIRED",
    "STATUS_BLOCKED_EMPTY_PACKAGE",
    "Service1PathologyFindingDeliveryPackageV1",
    "build_service_1_pathology_finding_delivery_package_v1",
]

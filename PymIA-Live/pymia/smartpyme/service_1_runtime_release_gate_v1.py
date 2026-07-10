"""
SERVICE_1_RUNTIME_AUTHORIZATION_GATE_V1

Pure gate that separates candidate-ready from runtime-authorized for Servicio 1.
It can authorize controlled runtime as data only. It never executes runtime,
imports CLI, parses XLSX, authorizes delivery, publishes, notifies, or marks a
product ready.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Final

from pymia.smartpyme.service_1_semantic_plan_to_xlsx_bridge_composition_v1 import (
    STATUS_COMPOSITION_CANDIDATE_READY,
    Service1SemanticPlanToXlsxBridgeCompositionV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_RUNTIME_AUTHORIZATION_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_RUNTIME_AUTHORIZED: Final[str] = "SERVICE_1_RUNTIME_AUTHORIZED"
STATUS_BLOCKED_BY_COMPOSITION: Final[str] = "SERVICE_1_RUNTIME_AUTH_BLOCKED_BY_COMPOSITION"
STATUS_BLOCKED_BY_OWNER_CONFIRMATION: Final[str] = "SERVICE_1_RUNTIME_AUTH_BLOCKED_BY_OWNER_CONFIRMATION"
STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION: Final[str] = "SERVICE_1_RUNTIME_AUTH_BLOCKED_BY_OPERATOR_AUTHORIZATION"
STATUS_BLOCKED_BY_SCOPE: Final[str] = "SERVICE_1_RUNTIME_AUTH_BLOCKED_BY_SCOPE"
STATUS_BLOCKED_BY_GUARD: Final[str] = "SERVICE_1_RUNTIME_AUTH_BLOCKED_BY_GUARD"
STATUS_BLOCKED_BY_POLICY: Final[str] = "SERVICE_1_RUNTIME_AUTH_BLOCKED_BY_POLICY"

AUTHORIZATION_DECISION: Final[str] = "AUTHORIZE_SERVICE_1_RUNTIME"
AUTHORIZATION_SCOPE: Final[str] = "SERVICE_1_XLSX_RUNTIME_ONLY"

_PROHIBITED_OPERATOR_FLAGS: Final[tuple[str, ...]] = (
    "delivery_authorized",
    "autonomous_delivery_authorized",
    "product_ready",
    "publish_authorized",
    "notification_authorized",
    "service_2_opened",
    "phase_j_opened",
    "llm_authorized",
    "api_exposed",
)


@dataclass(frozen=True)
class Service1RuntimeAuthorizationGateResultV1:
    schema_version: str = SCHEMA_VERSION
    service_name: str = SERVICE_NAME
    gate_status: str = STATUS_BLOCKED_BY_COMPOSITION
    case_id: str = ""
    tenant_id: str = ""
    intake_id: str = ""
    run_id: str = ""
    owner_ref: str = ""
    operator_ref: str | None = None
    controlled_runtime_session_ref: str | None = None
    composition_status: str = ""
    allowed_computation_ref: str | None = None
    package_candidate_ref: str | None = None
    runtime_authorization_candidate_prepared: bool = False
    runtime_authorized: bool = False
    runtime_execution_authorized: bool = False
    pipeline_execution_authorized: bool = False
    reexecution_authorized: bool = False
    recalculation_authorized: bool = False
    delivery_authorized: bool = False
    autonomous_delivery_authorized: bool = False
    product_ready: bool = False
    execution_done: bool = False
    next_required_action: str | None = None
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def build_service_1_runtime_authorization_gate_v1(
    *,
    composition: Service1SemanticPlanToXlsxBridgeCompositionV1,
    operator_authorization_packet: dict[str, Any] | None,
    metadata: dict[str, Any] | None = None,
) -> Service1RuntimeAuthorizationGateResultV1:
    base = _base_result(composition=composition, metadata=metadata)

    upstream_guard_reasons = _composition_guard_reasons(composition)
    if upstream_guard_reasons:
        return _blocked(base, STATUS_BLOCKED_BY_GUARD, "composition_guard", upstream_guard_reasons)

    if _has_policy_violation(composition.metadata) or _has_policy_violation(metadata):
        return _blocked(base, STATUS_BLOCKED_BY_POLICY, "policy", ("policy_violation",))

    if composition.composition_status != STATUS_COMPOSITION_CANDIDATE_READY:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_COMPOSITION,
            "composition",
            ("composition_candidate_not_ready",),
        )

    if not composition.composition_candidate_prepared:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_COMPOSITION,
            "composition",
            ("composition_candidate_not_prepared",),
        )

    if composition.owner_confirmation_required or not composition.owner_confirmed:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
            "owner_confirmation",
            ("owner_confirmation_required",),
            next_required_action="REQUEST_OWNER_CONFIRMATION",
        )

    if not isinstance(operator_authorization_packet, dict) or not operator_authorization_packet:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
            "operator_authorization",
            ("operator_authorization_packet_required",),
            next_required_action="REQUEST_OPERATOR_AUTHORIZATION",
        )

    if _has_policy_violation(operator_authorization_packet):
        return _blocked(base, STATUS_BLOCKED_BY_POLICY, "policy", ("policy_violation",))

    operator_guard_reasons = _operator_guard_reasons(operator_authorization_packet)
    if operator_guard_reasons:
        return _blocked(base, STATUS_BLOCKED_BY_GUARD, "operator_authorization_guard", operator_guard_reasons)

    operator_ref = _text(operator_authorization_packet.get("operator_ref"))
    if operator_ref is None:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
            "operator_authorization",
            ("operator_ref_required",),
        )

    if _text(operator_authorization_packet.get("authorization_decision")) != AUTHORIZATION_DECISION:
        return _blocked(
            replace(base, operator_ref=operator_ref),
            STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
            "operator_authorization",
            ("runtime_authorization_decision_required",),
        )

    if _text(operator_authorization_packet.get("authorization_scope")) != AUTHORIZATION_SCOPE:
        return _blocked(
            replace(base, operator_ref=operator_ref),
            STATUS_BLOCKED_BY_SCOPE,
            "authorization_scope",
            ("authorization_scope_must_be_service_1_xlsx_runtime_only",),
        )

    ref_mismatch = _reference_mismatch(composition, operator_authorization_packet)
    if ref_mismatch:
        return _blocked(
            replace(base, operator_ref=operator_ref),
            STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
            "operator_authorization_refs",
            (ref_mismatch,),
        )

    if operator_authorization_packet.get("human_review_completed") is not True:
        return _blocked(
            replace(base, operator_ref=operator_ref),
            STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
            "operator_authorization",
            ("human_review_completed_required",),
        )

    if operator_authorization_packet.get("owner_confirmation_seen") is not True:
        return _blocked(
            replace(base, operator_ref=operator_ref),
            STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
            "operator_authorization",
            ("owner_confirmation_seen_required",),
        )

    controlled_session_ref = _text(operator_authorization_packet.get("controlled_runtime_session_ref"))
    if controlled_session_ref is None:
        return _blocked(
            replace(base, operator_ref=operator_ref),
            STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
            "operator_authorization",
            ("controlled_runtime_session_ref_required",),
        )

    return Service1RuntimeAuthorizationGateResultV1(
        **{
            **base.__dict__,
            "gate_status": STATUS_RUNTIME_AUTHORIZED,
            "operator_ref": operator_ref,
            "controlled_runtime_session_ref": controlled_session_ref,
            "runtime_authorization_candidate_prepared": True,
            "runtime_authorized": True,
            "runtime_execution_authorized": True,
            "pipeline_execution_authorized": True,
            "reexecution_authorized": False,
            "recalculation_authorized": False,
            "delivery_authorized": False,
            "autonomous_delivery_authorized": False,
            "product_ready": False,
            "execution_done": False,
            "next_required_action": "RUN_CONTROLLED_SERVICE_1_RUNTIME",
            "blocking_layer": None,
            "blocking_reasons": (),
            "metadata": {"rule": "runtime_authorized", **dict(metadata or {})},
        }
    )


def _base_result(
    *,
    composition: Service1SemanticPlanToXlsxBridgeCompositionV1,
    metadata: dict[str, Any] | None,
) -> Service1RuntimeAuthorizationGateResultV1:
    return Service1RuntimeAuthorizationGateResultV1(
        case_id=composition.case_id,
        tenant_id=composition.tenant_id,
        intake_id=composition.intake_id,
        run_id=composition.run_id,
        owner_ref=composition.owner_ref,
        composition_status=composition.composition_status,
        allowed_computation_ref=composition.allowed_computation_ref,
        package_candidate_ref=composition.package_candidate_ref,
        runtime_authorization_candidate_prepared=False,
        runtime_authorized=False,
        runtime_execution_authorized=False,
        pipeline_execution_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        autonomous_delivery_authorized=False,
        product_ready=False,
        execution_done=False,
        metadata=dict(metadata or {}),
    )


def _blocked(
    base: Service1RuntimeAuthorizationGateResultV1,
    status: str,
    layer: str,
    reasons: tuple[str, ...],
    *,
    next_required_action: str | None = None,
) -> Service1RuntimeAuthorizationGateResultV1:
    return Service1RuntimeAuthorizationGateResultV1(
        **{
            **base.__dict__,
            "gate_status": status,
            "runtime_authorization_candidate_prepared": False,
            "runtime_authorized": False,
            "runtime_execution_authorized": False,
            "pipeline_execution_authorized": False,
            "reexecution_authorized": False,
            "recalculation_authorized": False,
            "delivery_authorized": False,
            "autonomous_delivery_authorized": False,
            "product_ready": False,
            "execution_done": False,
            "next_required_action": next_required_action or "KEEP_RUNTIME_BLOCKED",
            "blocking_layer": layer,
            "blocking_reasons": reasons,
            "metadata": {"rule": reasons[0] if reasons else "blocked", **base.metadata},
        }
    )


def _composition_guard_reasons(
    composition: Service1SemanticPlanToXlsxBridgeCompositionV1,
) -> tuple[str, ...]:
    checks = (
        (composition.runtime_authorized, "composition_runtime_authorized_must_enter_gate_false"),
        (composition.reexecution_authorized, "composition_reexecution_authorized_must_be_false"),
        (composition.recalculation_authorized, "composition_recalculation_authorized_must_be_false"),
        (composition.delivery_authorized, "composition_delivery_authorized_must_be_false"),
        (composition.product_ready, "composition_product_ready_must_be_false"),
    )
    return tuple(reason for flag, reason in checks if flag)


def _operator_guard_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"operator_{flag}_must_be_false"
        for flag in _PROHIBITED_OPERATOR_FLAGS
        if packet.get(flag) is True
    )


def _reference_mismatch(
    composition: Service1SemanticPlanToXlsxBridgeCompositionV1,
    packet: dict[str, Any],
) -> str | None:
    refs = (
        ("authorized_case_id", composition.case_id, "case_id_mismatch"),
        ("authorized_run_id", composition.run_id, "run_id_mismatch"),
        ("authorized_owner_ref", composition.owner_ref, "owner_ref_mismatch"),
        (
            "allowed_computation_ref",
            composition.allowed_computation_ref,
            "allowed_computation_ref_mismatch",
        ),
    )
    for key, expected, reason in refs:
        actual = _text(packet.get(key))
        if expected and actual is not None and actual != expected:
            return reason
    return None


def _has_policy_violation(metadata: Any) -> bool:
    return isinstance(metadata, dict) and metadata.get("policy_violation") is True


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_RUNTIME_AUTHORIZED",
    "STATUS_BLOCKED_BY_COMPOSITION",
    "STATUS_BLOCKED_BY_OWNER_CONFIRMATION",
    "STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION",
    "STATUS_BLOCKED_BY_SCOPE",
    "STATUS_BLOCKED_BY_GUARD",
    "STATUS_BLOCKED_BY_POLICY",
    "AUTHORIZATION_DECISION",
    "AUTHORIZATION_SCOPE",
    "Service1RuntimeAuthorizationGateResultV1",
    "build_service_1_runtime_authorization_gate_v1",
]

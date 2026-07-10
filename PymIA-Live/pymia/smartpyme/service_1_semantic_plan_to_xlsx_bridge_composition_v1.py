"""
SERVICE_1_SEMANTIC_PLAN_TO_XLSX_BRIDGE_COMPOSITION_V1

Pure composition candidate joining an already prepared semantic runtime plan,
an existing XLSX runtime bridge result, and the owner confirmation boundary.
It never parses XLSX, imports CLI, executes runtime, authorizes delivery, or
marks a product ready.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_owner_confirmation_boundary_v1 import (
    OWNER_CONFIRMED,
    Service1OwnerConfirmationResultV1,
)
from pymia.smartpyme.service_1_semantic_runtime_plan_candidate_v1 import (
    PLAN_READY_CANDIDATE,
    Service1SemanticRuntimePlanCandidateV1,
)
from pymia.smartpyme.service_1_xlsx_runtime_bridge_v1 import (
    STATUS_BRIDGE_NEXT_OWNER_QUESTION,
    STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
    Service1XlsxRuntimeBridgeV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_PLAN_TO_XLSX_BRIDGE_COMPOSITION_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_COMPOSITION_CANDIDATE_READY: Final[str] = "COMPOSITION_CANDIDATE_READY"
STATUS_BLOCKED_BY_SEMANTIC_PLAN: Final[str] = "COMPOSITION_BLOCKED_BY_SEMANTIC_PLAN"
STATUS_BLOCKED_BY_XLSX_BRIDGE: Final[str] = "COMPOSITION_BLOCKED_BY_XLSX_BRIDGE"
STATUS_BLOCKED_BY_OWNER_CONFIRMATION: Final[str] = "COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION"
STATUS_BLOCKED_BY_GUARD: Final[str] = "COMPOSITION_BLOCKED_BY_GUARD"


@dataclass(frozen=True)
class Service1SemanticPlanToXlsxBridgeCompositionV1:
    schema_version: str = SCHEMA_VERSION
    service_name: str = SERVICE_NAME
    composition_status: str = STATUS_BLOCKED_BY_SEMANTIC_PLAN
    pathology_code: str = ""
    case_id: str = ""
    tenant_id: str = ""
    intake_id: str = ""
    run_id: str = ""
    owner_ref: str = ""
    semantic_plan_status: str = ""
    xlsx_bridge_status: str = ""
    owner_confirmation_status: str = ""
    allowed_computation_ref: str | None = None
    bridge_allowed_computation_ref: str | None = None
    package_candidate_ref: str | None = None
    next_owner_question: str | None = None
    composition_candidate_prepared: bool = False
    semantic_plan_ready: bool = False
    xlsx_bridge_ready: bool = False
    owner_confirmed: bool = False
    owner_confirmation_required: bool = True
    runtime_authorized: bool = False
    reexecution_authorized: bool = False
    recalculation_authorized: bool = False
    delivery_authorized: bool = False
    product_ready: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def build_service_1_semantic_plan_to_xlsx_bridge_composition_v1(
    *,
    semantic_plan: Service1SemanticRuntimePlanCandidateV1,
    xlsx_bridge: Service1XlsxRuntimeBridgeV1,
    owner_confirmation: Service1OwnerConfirmationResultV1,
    metadata: dict[str, Any] | None = None,
) -> Service1SemanticPlanToXlsxBridgeCompositionV1:
    base = _base_result(
        semantic_plan=semantic_plan,
        xlsx_bridge=xlsx_bridge,
        owner_confirmation=owner_confirmation,
        metadata=metadata,
    )

    guard_reasons = _guard_reasons(semantic_plan, xlsx_bridge, owner_confirmation)
    if guard_reasons:
        return _blocked(base, STATUS_BLOCKED_BY_GUARD, "guard", guard_reasons)

    if semantic_plan.plan_status != PLAN_READY_CANDIDATE:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_SEMANTIC_PLAN,
            "semantic_plan",
            ("semantic_plan_not_ready",),
        )

    if not semantic_plan.semantic_runtime_plan_prepared:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_SEMANTIC_PLAN,
            "semantic_plan",
            ("semantic_runtime_plan_not_prepared",),
        )

    if xlsx_bridge.status == STATUS_BRIDGE_NEXT_OWNER_QUESTION:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
            "xlsx_bridge_owner_question",
            ("xlsx_bridge_requires_owner_confirmation",),
            owner_confirmation_required=True,
        )

    if xlsx_bridge.status != STATUS_BRIDGE_PACKAGE_CANDIDATE_READY:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_XLSX_BRIDGE,
            "xlsx_bridge",
            ("xlsx_bridge_not_ready",),
        )

    if xlsx_bridge.owner_confirmation_required:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
            "xlsx_bridge_owner_confirmation",
            ("xlsx_bridge_owner_confirmation_required",),
            owner_confirmation_required=True,
        )

    if owner_confirmation.confirmation_status != OWNER_CONFIRMED:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
            "owner_confirmation",
            ("owner_not_confirmed",),
            owner_confirmation_required=True,
        )

    mismatch = _allowed_computation_mismatch(semantic_plan, xlsx_bridge)
    if mismatch:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_XLSX_BRIDGE,
            "allowed_computation_ref",
            (mismatch,),
        )

    return Service1SemanticPlanToXlsxBridgeCompositionV1(
        **{
            **base.__dict__,
            "composition_status": STATUS_COMPOSITION_CANDIDATE_READY,
            "composition_candidate_prepared": True,
            "semantic_plan_ready": True,
            "xlsx_bridge_ready": True,
            "owner_confirmed": True,
            "owner_confirmation_required": False,
            "blocking_layer": None,
            "blocking_reasons": (),
            "metadata": {"rule": "ready", **dict(metadata or {})},
        }
    )


def _base_result(
    *,
    semantic_plan: Service1SemanticRuntimePlanCandidateV1,
    xlsx_bridge: Service1XlsxRuntimeBridgeV1,
    owner_confirmation: Service1OwnerConfirmationResultV1,
    metadata: dict[str, Any] | None,
) -> Service1SemanticPlanToXlsxBridgeCompositionV1:
    return Service1SemanticPlanToXlsxBridgeCompositionV1(
        pathology_code=semantic_plan.pathology_code,
        case_id=xlsx_bridge.case_id,
        tenant_id=xlsx_bridge.tenant_id,
        intake_id=xlsx_bridge.intake_id,
        run_id=xlsx_bridge.run_id,
        owner_ref=xlsx_bridge.owner_ref,
        semantic_plan_status=semantic_plan.plan_status,
        xlsx_bridge_status=xlsx_bridge.status,
        owner_confirmation_status=owner_confirmation.confirmation_status,
        allowed_computation_ref=semantic_plan.allowed_computation_ref,
        bridge_allowed_computation_ref=xlsx_bridge.allowed_computation_ref,
        package_candidate_ref=xlsx_bridge.package_candidate_ref,
        next_owner_question=xlsx_bridge.next_owner_question,
        semantic_plan_ready=semantic_plan.plan_status == PLAN_READY_CANDIDATE
        and semantic_plan.semantic_runtime_plan_prepared,
        xlsx_bridge_ready=xlsx_bridge.status == STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
        owner_confirmed=owner_confirmation.confirmation_status == OWNER_CONFIRMED,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        product_ready=False,
        metadata=dict(metadata or {}),
    )


def _blocked(
    base: Service1SemanticPlanToXlsxBridgeCompositionV1,
    status: str,
    layer: str,
    reasons: tuple[str, ...],
    *,
    owner_confirmation_required: bool = True,
) -> Service1SemanticPlanToXlsxBridgeCompositionV1:
    return Service1SemanticPlanToXlsxBridgeCompositionV1(
        **{
            **base.__dict__,
            "composition_status": status,
            "composition_candidate_prepared": False,
            "owner_confirmation_required": owner_confirmation_required,
            "runtime_authorized": False,
            "reexecution_authorized": False,
            "recalculation_authorized": False,
            "delivery_authorized": False,
            "product_ready": False,
            "blocking_layer": layer,
            "blocking_reasons": reasons,
            "metadata": {"rule": reasons[0] if reasons else "blocked", **base.metadata},
        }
    )


def _guard_reasons(
    semantic_plan: Service1SemanticRuntimePlanCandidateV1,
    xlsx_bridge: Service1XlsxRuntimeBridgeV1,
    owner_confirmation: Service1OwnerConfirmationResultV1,
) -> tuple[str, ...]:
    checks = (
        (semantic_plan.computation_execution_allowed, "semantic_plan_execution_allowed"),
        (semantic_plan.runtime_authorized, "semantic_plan_runtime_authorized"),
        (semantic_plan.reexecution_authorized, "semantic_plan_reexecution_authorized"),
        (semantic_plan.recalculation_authorized, "semantic_plan_recalculation_authorized"),
        (semantic_plan.delivery_authorized, "semantic_plan_delivery_authorized"),
        (semantic_plan.phase_5_allowed, "semantic_plan_phase_5_allowed"),
        (semantic_plan.product_ready, "semantic_plan_product_ready"),
        (xlsx_bridge.runtime_authorized, "xlsx_bridge_runtime_authorized"),
        (xlsx_bridge.reexecution_authorized, "xlsx_bridge_reexecution_authorized"),
        (xlsx_bridge.recalculation_authorized, "xlsx_bridge_recalculation_authorized"),
        (xlsx_bridge.delivery_authorized, "xlsx_bridge_delivery_authorized"),
        (owner_confirmation.runtime_allowed, "owner_confirmation_runtime_allowed"),
        (owner_confirmation.phase_5_allowed, "owner_confirmation_phase_5_allowed"),
    )
    return tuple(reason for flag, reason in checks if flag)


def _allowed_computation_mismatch(
    semantic_plan: Service1SemanticRuntimePlanCandidateV1,
    xlsx_bridge: Service1XlsxRuntimeBridgeV1,
) -> str | None:
    semantic_ref = semantic_plan.allowed_computation_ref
    bridge_ref = xlsx_bridge.allowed_computation_ref
    if semantic_ref and bridge_ref and semantic_ref != bridge_ref:
        return "allowed_computation_ref_mismatch"
    return None


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_COMPOSITION_CANDIDATE_READY",
    "STATUS_BLOCKED_BY_SEMANTIC_PLAN",
    "STATUS_BLOCKED_BY_XLSX_BRIDGE",
    "STATUS_BLOCKED_BY_OWNER_CONFIRMATION",
    "STATUS_BLOCKED_BY_GUARD",
    "Service1SemanticPlanToXlsxBridgeCompositionV1",
    "build_service_1_semantic_plan_to_xlsx_bridge_composition_v1",
]

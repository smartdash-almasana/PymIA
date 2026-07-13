"""
SERVICE_1_SEMANTIC_RUNTIME_PLAN_CANDIDATE_V1

Pure fail-closed plan candidate built from the bounded-engine adapter output.
It prepares a semantic runtime plan candidate only. It never executes computation,
runtime, CLI, delivery, recalculation, reexecution, or Phase 5.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_bounded_engine_to_allowed_computation_adapter_v1 import (
    ADAPTER_READY,
    Service1BoundedEngineToAllowedComputationAdapterResultV1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    STATUS_READY_FOR_COMPUTATION_PLAN,
)

PLAN_READY_CANDIDATE = "SERVICE_1_SEMANTIC_RUNTIME_PLAN_READY_CANDIDATE"
PLAN_BLOCKED_BY_ADAPTER = "SERVICE_1_SEMANTIC_RUNTIME_PLAN_BLOCKED_BY_ADAPTER"
PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE = (
    "SERVICE_1_SEMANTIC_RUNTIME_PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE"
)
PLAN_BLOCKED_BY_POLICY = "SERVICE_1_SEMANTIC_RUNTIME_PLAN_BLOCKED_BY_POLICY"
PLAN_BLOCKED_BY_GUARD = "SERVICE_1_SEMANTIC_RUNTIME_PLAN_BLOCKED_BY_GUARD"


@dataclass(frozen=True)
class Service1SemanticRuntimePlanCandidateV1:
    schema_version: str = "SERVICE_1_SEMANTIC_RUNTIME_PLAN_CANDIDATE_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    plan_status: str = PLAN_BLOCKED_BY_ADAPTER
    adapter_status: str = ""
    allowed_computation_ref: str | None = None
    required_fields: tuple[str, ...] = ()
    available_fields: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    semantic_runtime_plan_prepared: bool = False
    computation_execution_allowed: bool = False
    runtime_authorized: bool = False
    reexecution_authorized: bool = False
    recalculation_authorized: bool = False
    delivery_authorized: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def build_service_1_semantic_runtime_plan_candidate_v1(
    adapter_result: Service1BoundedEngineToAllowedComputationAdapterResultV1,
) -> Service1SemanticRuntimePlanCandidateV1:
    pathology_code = getattr(adapter_result, "pathology_code", "")
    adapter_status = getattr(adapter_result, "adapter_status", "")
    adapter_metadata = getattr(adapter_result, "metadata", None)
    adapter_metadata = adapter_metadata if isinstance(adapter_metadata, dict) else {}
    computation_candidate = getattr(adapter_result, "allowed_computation_candidate", None)

    def _blocked(
        status: str,
        layer: str,
        reason: str,
    ) -> Service1SemanticRuntimePlanCandidateV1:
        return Service1SemanticRuntimePlanCandidateV1(
            pathology_code=pathology_code,
            plan_status=status,
            adapter_status=adapter_status,
            semantic_runtime_plan_prepared=False,
            computation_execution_allowed=False,
            runtime_authorized=False,
            reexecution_authorized=False,
            recalculation_authorized=False,
            delivery_authorized=False,
            phase_5_allowed=False,
            product_ready=False,
            blocking_layer=layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    if bool(adapter_metadata.get("policy_violation")):
        return _blocked(PLAN_BLOCKED_BY_POLICY, "policy", "policy_violation")

    if any(
        bool(getattr(adapter_result, attr, False))
        for attr in (
            "runtime_authorized",
            "reexecution_authorized",
            "recalculation_authorized",
            "delivery_authorized",
        )
    ):
        return _blocked(PLAN_BLOCKED_BY_GUARD, "adapter_guard", "upstream_guard_open")

    if adapter_status != ADAPTER_READY:
        return _blocked(PLAN_BLOCKED_BY_ADAPTER, "adapter", "adapter_not_ready")

    if not bool(getattr(adapter_result, "adapter_prepared", False)):
        return _blocked(PLAN_BLOCKED_BY_ADAPTER, "adapter", "adapter_not_prepared")

    if computation_candidate is None:
        return _blocked(
            PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE,
            "allowed_computation_candidate",
            "allowed_computation_candidate_missing",
        )

    if getattr(computation_candidate, "status", "") != STATUS_READY_FOR_COMPUTATION_PLAN:
        return _blocked(
            PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE,
            "allowed_computation_candidate",
            "allowed_computation_candidate_not_ready",
        )

    if not getattr(computation_candidate, "allowed_computation_ref", None):
        return _blocked(
            PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE,
            "allowed_computation_candidate",
            "allowed_computation_ref_missing",
        )

    if any(
        bool(getattr(computation_candidate, attr, False))
        for attr in (
            "runtime_authorized",
            "reexecution_authorized",
            "recalculation_authorized",
            "delivery_authorized",
        )
    ):
        return _blocked(
            PLAN_BLOCKED_BY_GUARD,
            "allowed_computation_guard",
            "allowed_computation_guard_open",
        )

    return Service1SemanticRuntimePlanCandidateV1(
        pathology_code=pathology_code,
        plan_status=PLAN_READY_CANDIDATE,
        adapter_status=adapter_status,
        allowed_computation_ref=computation_candidate.allowed_computation_ref,
        required_fields=tuple(computation_candidate.required_fields),
        available_fields=tuple(computation_candidate.available_fields),
        missing_fields=tuple(computation_candidate.missing_fields),
        semantic_runtime_plan_prepared=True,
        computation_execution_allowed=False,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        phase_5_allowed=False,
        product_ready=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )


__all__ = [
    "PLAN_READY_CANDIDATE",
    "PLAN_BLOCKED_BY_ADAPTER",
    "PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE",
    "PLAN_BLOCKED_BY_POLICY",
    "PLAN_BLOCKED_BY_GUARD",
    "Service1SemanticRuntimePlanCandidateV1",
    "build_service_1_semantic_runtime_plan_candidate_v1",
]

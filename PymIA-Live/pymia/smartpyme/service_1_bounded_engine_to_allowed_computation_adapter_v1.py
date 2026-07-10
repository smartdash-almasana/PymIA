"""
SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_V1

Bridges the fail-closed bounded semantic engine candidate to the existing
pathology-to-allowed-computation candidate. It never authorizes or performs runtime,
reexecution, recalculation, delivery, CLI, mapper, or engine execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_bounded_semantic_engine_implementation_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE,
    Service1BoundedSemanticEngineResultV1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    Service1AllowedComputationCandidateV1,
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)

ADAPTER_READY = "SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_READY"
ADAPTER_BLOCKED_BY_ENGINE = "SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_BLOCKED_BY_ENGINE"
ADAPTER_BLOCKED_BY_POLICY = "SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_BLOCKED_BY_POLICY"
ADAPTER_BLOCKED_BY_GUARD = "SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_BLOCKED_BY_GUARD"


@dataclass(frozen=True)
class Service1BoundedEngineToAllowedComputationAdapterResultV1:
    schema_version: str = "SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    adapter_status: str = ADAPTER_BLOCKED_BY_ENGINE
    engine_status: str = ""
    allowed_computation_candidate: Service1AllowedComputationCandidateV1 | None = None
    adapter_prepared: bool = False
    runtime_authorized: bool = False
    reexecution_authorized: bool = False
    recalculation_authorized: bool = False
    delivery_authorized: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def build_service_1_bounded_engine_to_allowed_computation_adapter_v1(
    *,
    engine_result: Service1BoundedSemanticEngineResultV1,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    missing_evidence_items: list[str] | tuple[str, ...] | None = None,
    business_period_reference: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1BoundedEngineToAllowedComputationAdapterResultV1:
    pathology_code = getattr(engine_result, "pathology_code", "")
    engine_status = getattr(engine_result, "engine_status", "")
    engine_metadata = getattr(engine_result, "metadata", None)
    engine_metadata = engine_metadata if isinstance(engine_metadata, dict) else {}

    def _blocked(status: str, layer: str, reason: str) -> Service1BoundedEngineToAllowedComputationAdapterResultV1:
        return Service1BoundedEngineToAllowedComputationAdapterResultV1(
            pathology_code=pathology_code,
            adapter_status=status,
            engine_status=engine_status,
            allowed_computation_candidate=None,
            adapter_prepared=False,
            runtime_authorized=False,
            reexecution_authorized=False,
            recalculation_authorized=False,
            delivery_authorized=False,
            blocking_layer=layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    if bool(engine_metadata.get("policy_violation")):
        return _blocked(ADAPTER_BLOCKED_BY_POLICY, "policy", "policy_violation")

    if any(
        bool(getattr(engine_result, attr, False))
        for attr in (
            "bounded_semantic_engine_execution_allowed",
            "execution_performed",
            "runtime_allowed",
            "phase_5_allowed",
            "product_ready",
            "delivery_allowed",
        )
    ):
        return _blocked(ADAPTER_BLOCKED_BY_GUARD, "engine_guard", "upstream_guard_open")

    if engine_status != SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE:
        return _blocked(ADAPTER_BLOCKED_BY_ENGINE, "bounded_engine", "bounded_engine_not_ready")

    if not bool(getattr(engine_result, "bounded_semantic_engine_candidate_prepared", False)):
        return _blocked(ADAPTER_BLOCKED_BY_ENGINE, "bounded_engine", "bounded_engine_candidate_not_prepared")

    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=pathology_code,
        available_data_fields=available_data_fields,
        missing_evidence_items=missing_evidence_items,
        business_period_reference=business_period_reference,
        metadata={"source": "bounded_semantic_engine", **dict(metadata or {})},
    )

    return Service1BoundedEngineToAllowedComputationAdapterResultV1(
        pathology_code=pathology_code,
        adapter_status=ADAPTER_READY,
        engine_status=engine_status,
        allowed_computation_candidate=candidate,
        adapter_prepared=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )


__all__ = [
    "ADAPTER_READY",
    "ADAPTER_BLOCKED_BY_ENGINE",
    "ADAPTER_BLOCKED_BY_POLICY",
    "ADAPTER_BLOCKED_BY_GUARD",
    "Service1BoundedEngineToAllowedComputationAdapterResultV1",
    "build_service_1_bounded_engine_to_allowed_computation_adapter_v1",
]

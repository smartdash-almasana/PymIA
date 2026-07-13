"""
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_IMPLEMENTATION_V1

Pure fail-closed engine boundary for Servicio 1. It consumes the bounded semantic
engine contract and prepares a deterministic engine candidate only. It never performs
runtime, CLI, mapper, delivery, JSON mutation, or real engine execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_bounded_semantic_engine_contract_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE,
    Service1BoundedSemanticEngineContractResultV1,
)

SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_POLICY = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_POLICY"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_EXECUTION_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_EXECUTION_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_RUNTIME_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_RUNTIME_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PHASE_5_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PHASE_5_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PRODUCT_READY_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PRODUCT_READY_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_DELIVERY_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_DELIVERY_GUARD"
)


@dataclass(frozen=True)
class Service1BoundedSemanticEngineResultV1:
    schema_version: str = "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_IMPLEMENTATION_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    engine_status: str = SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT
    contract_status: str = ""
    bounded_semantic_engine_candidate_prepared: bool = False
    bounded_semantic_engine_execution_allowed: bool = False
    execution_performed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    delivery_allowed: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def _metadata(contract_result: Any) -> dict[str, Any]:
    metadata = getattr(contract_result, "metadata", None)
    return metadata if isinstance(metadata, dict) else {}


def build_bounded_semantic_engine_result_v1(
    contract_result: Service1BoundedSemanticEngineContractResultV1,
) -> Service1BoundedSemanticEngineResultV1:
    pathology_code = getattr(contract_result, "pathology_code", "")
    contract_status = getattr(contract_result, "contract_status", "")
    metadata = _metadata(contract_result)

    def _blocked(
        status: str,
        layer: str,
        reason: str,
    ) -> Service1BoundedSemanticEngineResultV1:
        return Service1BoundedSemanticEngineResultV1(
            pathology_code=pathology_code,
            engine_status=status,
            contract_status=contract_status,
            bounded_semantic_engine_candidate_prepared=False,
            bounded_semantic_engine_execution_allowed=False,
            execution_performed=False,
            runtime_allowed=False,
            phase_5_allowed=False,
            product_ready=False,
            delivery_allowed=False,
            blocking_layer=layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    if bool(metadata.get("policy_violation")):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_POLICY,
            "policy",
            "policy_violation",
        )

    if bool(
        getattr(contract_result, "bounded_semantic_engine_execution_allowed", False)
    ) or bool(metadata.get("bounded_semantic_engine_execution_allowed")):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_EXECUTION_GUARD,
            "execution_guard",
            "bounded_semantic_engine_execution_guard_open",
        )

    if bool(getattr(contract_result, "runtime_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_RUNTIME_GUARD,
            "runtime_guard",
            "runtime_guard_open",
        )

    if bool(getattr(contract_result, "phase_5_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PHASE_5_GUARD,
            "phase_5_guard",
            "phase_5_guard_open",
        )

    if bool(getattr(contract_result, "product_ready", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PRODUCT_READY_GUARD,
            "product_ready_guard",
            "product_ready_guard_open",
        )

    if bool(getattr(contract_result, "delivery_allowed", False)) or bool(
        metadata.get("delivery_allowed")
    ):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_DELIVERY_GUARD,
            "delivery_guard",
            "delivery_guard_open",
        )

    if contract_status != SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE:
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT,
            "engine_contract",
            "engine_contract_not_ready",
        )

    if not bool(
        getattr(contract_result, "bounded_semantic_engine_contract_prepared", False)
    ):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT,
            "engine_contract",
            "engine_contract_not_prepared",
        )

    return Service1BoundedSemanticEngineResultV1(
        pathology_code=pathology_code,
        engine_status=SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE,
        contract_status=contract_status,
        bounded_semantic_engine_candidate_prepared=True,
        bounded_semantic_engine_execution_allowed=False,
        execution_performed=False,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        delivery_allowed=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

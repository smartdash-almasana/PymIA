"""
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_V1

Pure fail-closed contract between the bounded invocation port and a future bounded
semantic engine implementation. It validates contract readiness only and never
executes or authorizes engine, runtime, CLI, mapper, delivery, or Phase 5.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_bounded_semantic_engine_invocation_port_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE,
    Service1BoundedSemanticEngineInvocationPortResultV1,
)

SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_POLICY = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_POLICY"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_EXECUTION_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_EXECUTION_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_RUNTIME_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_RUNTIME_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PHASE_5_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PHASE_5_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PRODUCT_READY_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PRODUCT_READY_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_DELIVERY_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_DELIVERY_GUARD"
)


@dataclass(frozen=True)
class Service1BoundedSemanticEngineContractResultV1:
    schema_version: str = "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    contract_status: str = SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT
    port_status: str = ""
    bounded_semantic_engine_contract_prepared: bool = False
    bounded_semantic_engine_execution_allowed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    delivery_allowed: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def _metadata(port_result: Any) -> dict[str, Any]:
    metadata = getattr(port_result, "metadata", None)
    return metadata if isinstance(metadata, dict) else {}


def build_bounded_semantic_engine_contract_result_v1(
    port_result: Service1BoundedSemanticEngineInvocationPortResultV1,
) -> Service1BoundedSemanticEngineContractResultV1:
    pathology_code = getattr(port_result, "pathology_code", "")
    port_status = getattr(port_result, "port_status", "")
    metadata = _metadata(port_result)

    def _blocked(
        status: str,
        layer: str,
        reason: str,
    ) -> Service1BoundedSemanticEngineContractResultV1:
        return Service1BoundedSemanticEngineContractResultV1(
            pathology_code=pathology_code,
            contract_status=status,
            port_status=port_status,
            bounded_semantic_engine_contract_prepared=False,
            bounded_semantic_engine_execution_allowed=False,
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
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_POLICY,
            "policy",
            "policy_violation",
        )

    if bool(getattr(port_result, "bounded_engine_execution_allowed", False)) or bool(
        metadata.get("bounded_engine_execution_allowed")
    ):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_EXECUTION_GUARD,
            "execution_guard",
            "bounded_engine_execution_guard_open",
        )

    if bool(getattr(port_result, "runtime_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_RUNTIME_GUARD,
            "runtime_guard",
            "runtime_guard_open",
        )

    if bool(getattr(port_result, "phase_5_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PHASE_5_GUARD,
            "phase_5_guard",
            "phase_5_guard_open",
        )

    if bool(getattr(port_result, "product_ready", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PRODUCT_READY_GUARD,
            "product_ready_guard",
            "product_ready_guard_open",
        )

    if bool(getattr(port_result, "delivery_allowed", False)) or bool(
        metadata.get("delivery_allowed")
    ):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_DELIVERY_GUARD,
            "delivery_guard",
            "delivery_guard_open",
        )

    if port_status != SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE:
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT,
            "invocation_port",
            "invocation_port_not_ready",
        )

    if not bool(getattr(port_result, "bounded_engine_invocation_port_prepared", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT,
            "invocation_port",
            "invocation_port_not_prepared",
        )

    return Service1BoundedSemanticEngineContractResultV1(
        pathology_code=pathology_code,
        contract_status=SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE,
        port_status=port_status,
        bounded_semantic_engine_contract_prepared=True,
        bounded_semantic_engine_execution_allowed=False,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        delivery_allowed=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

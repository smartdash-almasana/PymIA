"""
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_V1

Fail-closed contract port between Servicio 1 bounded semantic invocation and a future
bounded semantic engine. This module prepares a port request candidate only; it does
not execute an engine, runtime, CLI, mapper, delivery, or JSON mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_semantic_binding_bounded_invocation_v1 import (
    SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE,
    Service1SemanticBindingBoundedInvocationResultV1,
)

SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_POLICY = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_POLICY"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_EXECUTION_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_EXECUTION_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_RUNTIME_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_RUNTIME_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PHASE_5_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PHASE_5_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PRODUCT_READY_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PRODUCT_READY_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_DELIVERY_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_DELIVERY_GUARD"
)
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_ENGINE_GUARD = (
    "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_ENGINE_GUARD"
)


@dataclass(frozen=True)
class Service1BoundedSemanticEngineInvocationPortResultV1:
    schema_version: str = "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    port_status: str = SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION
    invocation_status: str = ""
    bounded_engine_invocation_port_prepared: bool = False
    semantic_binding_execution_allowed: bool = False
    bounded_engine_execution_allowed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    delivery_allowed: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def _metadata(invocation_result: Any) -> dict[str, Any]:
    metadata = getattr(invocation_result, "metadata", None)
    return metadata if isinstance(metadata, dict) else {}


def _has_policy_violation(metadata: dict[str, Any]) -> bool:
    return bool(metadata.get("policy_violation"))


def _delivery_allowed(invocation_result: Any, metadata: dict[str, Any]) -> bool:
    return bool(getattr(invocation_result, "delivery_allowed", False)) or bool(
        metadata.get("delivery_allowed")
    )


def _engine_execution_allowed(invocation_result: Any, metadata: dict[str, Any]) -> bool:
    return bool(getattr(invocation_result, "bounded_engine_execution_allowed", False)) or bool(
        metadata.get("bounded_engine_execution_allowed")
    )


def build_bounded_semantic_engine_invocation_port_result_v1(
    invocation_result: Service1SemanticBindingBoundedInvocationResultV1,
) -> Service1BoundedSemanticEngineInvocationPortResultV1:
    pathology_code = getattr(invocation_result, "pathology_code", "")
    invocation_status = getattr(invocation_result, "invocation_status", "")
    metadata = _metadata(invocation_result)

    def _blocked(
        status: str,
        layer: str,
        reason: str,
    ) -> Service1BoundedSemanticEngineInvocationPortResultV1:
        return Service1BoundedSemanticEngineInvocationPortResultV1(
            pathology_code=pathology_code,
            port_status=status,
            invocation_status=invocation_status,
            bounded_engine_invocation_port_prepared=False,
            semantic_binding_execution_allowed=False,
            bounded_engine_execution_allowed=False,
            runtime_allowed=False,
            phase_5_allowed=False,
            product_ready=False,
            delivery_allowed=False,
            blocking_layer=layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    if _has_policy_violation(metadata):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_POLICY,
            "policy",
            "policy_violation",
        )

    if bool(getattr(invocation_result, "semantic_binding_execution_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_EXECUTION_GUARD,
            "execution_guard",
            "execution_guard_open",
        )

    if _engine_execution_allowed(invocation_result, metadata):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_ENGINE_GUARD,
            "engine_guard",
            "bounded_engine_execution_guard_open",
        )

    if bool(getattr(invocation_result, "runtime_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_RUNTIME_GUARD,
            "runtime_guard",
            "runtime_guard_open",
        )

    if bool(getattr(invocation_result, "phase_5_allowed", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PHASE_5_GUARD,
            "phase_5_guard",
            "phase_5_guard_open",
        )

    if bool(getattr(invocation_result, "product_ready", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PRODUCT_READY_GUARD,
            "product_ready_guard",
            "product_ready_guard_open",
        )

    if _delivery_allowed(invocation_result, metadata):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_DELIVERY_GUARD,
            "delivery_guard",
            "delivery_guard_open",
        )

    if invocation_status != SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE:
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION,
            "bounded_invocation",
            "bounded_invocation_not_ready",
        )

    if not bool(getattr(invocation_result, "semantic_binding_invocation_prepared", False)):
        return _blocked(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION,
            "bounded_invocation",
            "semantic_binding_invocation_not_prepared",
        )

    return Service1BoundedSemanticEngineInvocationPortResultV1(
        pathology_code=pathology_code,
        port_status=SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE,
        invocation_status=invocation_status,
        bounded_engine_invocation_port_prepared=True,
        semantic_binding_execution_allowed=False,
        bounded_engine_execution_allowed=False,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        delivery_allowed=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

"""
SERVICE_1_SEMANTIC_BINDING_BOUNDED_INVOCATION_V1

Pure invocation-preparation boundary for Servicio 1 semantic binding.
No runtime, mapper, engine, CLI, case fixtures, delivery generation, or JSON mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_semantic_binding_execution_harness_v1 import (
    SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE,
    Service1SemanticBindingExecutionHarnessResultV1,
)

SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_POLICY = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_POLICY"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_EXECUTION_GUARD = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_EXECUTION_GUARD"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_RUNTIME_GUARD = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_RUNTIME_GUARD"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PHASE_5_GUARD = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PHASE_5_GUARD"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PRODUCT_READY_GUARD = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PRODUCT_READY_GUARD"
)
SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_DELIVERY_GUARD = (
    "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_DELIVERY_GUARD"
)


@dataclass(frozen=True)
class Service1SemanticBindingBoundedInvocationResultV1:
    schema_version: str = "SERVICE_1_SEMANTIC_BINDING_BOUNDED_INVOCATION_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    invocation_status: str = SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS
    harness_status: str = ""
    semantic_binding_invocation_prepared: bool = False
    semantic_binding_execution_allowed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    delivery_allowed: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def _metadata(harness_result: Any) -> dict[str, Any]:
    metadata = getattr(harness_result, "metadata", None)
    return metadata if isinstance(metadata, dict) else {}


def _has_policy_violation(metadata: dict[str, Any]) -> bool:
    return bool(metadata.get("policy_violation"))


def _delivery_allowed(harness_result: Any, metadata: dict[str, Any]) -> bool:
    return bool(getattr(harness_result, "delivery_allowed", False)) or bool(
        metadata.get("delivery_allowed")
    )


def build_semantic_binding_bounded_invocation_result_v1(
    harness_result: Service1SemanticBindingExecutionHarnessResultV1,
) -> Service1SemanticBindingBoundedInvocationResultV1:
    pathology_code = getattr(harness_result, "pathology_code", "")
    harness_status = getattr(harness_result, "harness_status", "")
    metadata = _metadata(harness_result)

    def _blocked(
        status: str,
        layer: str,
        reason: str,
    ) -> Service1SemanticBindingBoundedInvocationResultV1:
        return Service1SemanticBindingBoundedInvocationResultV1(
            pathology_code=pathology_code,
            invocation_status=status,
            harness_status=harness_status,
            semantic_binding_invocation_prepared=False,
            semantic_binding_execution_allowed=False,
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
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_POLICY,
            "policy",
            "policy_violation",
        )

    if bool(getattr(harness_result, "semantic_binding_execution_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_EXECUTION_GUARD,
            "execution_guard",
            "execution_guard_open",
        )

    if bool(getattr(harness_result, "runtime_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_RUNTIME_GUARD,
            "runtime_guard",
            "runtime_guard_open",
        )

    if bool(getattr(harness_result, "phase_5_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PHASE_5_GUARD,
            "phase_5_guard",
            "phase_5_guard_open",
        )

    if bool(getattr(harness_result, "product_ready", False)):
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PRODUCT_READY_GUARD,
            "product_ready_guard",
            "product_ready_guard_open",
        )

    if _delivery_allowed(harness_result, metadata):
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_DELIVERY_GUARD,
            "delivery_guard",
            "delivery_guard_open",
        )

    if harness_status != SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE:
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS,
            "harness",
            "harness_not_ready",
        )

    if not bool(
        getattr(harness_result, "semantic_binding_request_prepared", False)
    ):
        return _blocked(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS,
            "harness",
            "semantic_binding_request_not_prepared",
        )

    return Service1SemanticBindingBoundedInvocationResultV1(
        pathology_code=pathology_code,
        invocation_status=SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE,
        harness_status=harness_status,
        semantic_binding_invocation_prepared=True,
        semantic_binding_execution_allowed=False,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        delivery_allowed=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

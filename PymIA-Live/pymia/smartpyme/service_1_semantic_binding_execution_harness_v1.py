"""
SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_V1

Pure request-preparation harness for Servicio 1 semantic binding.
No runtime, mapper, engine, CLI, case fixtures, delivery, or JSON mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_semantic_binding_activation_v1 import (
    SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE,
)

SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE"
)
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION"
)
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_POLICY = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_POLICY"
)
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_EXECUTION_GUARD = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_EXECUTION_GUARD"
)
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_RUNTIME_GUARD = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_RUNTIME_GUARD"
)
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PHASE_5_GUARD = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PHASE_5_GUARD"
)
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PRODUCT_READY_GUARD = (
    "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PRODUCT_READY_GUARD"
)


@dataclass(frozen=True)
class Service1SemanticBindingExecutionHarnessResultV1:
    schema_version: str = "SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    harness_status: str = SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION
    activation_status: str = ""
    semantic_binding_request_prepared: bool = False
    semantic_binding_execution_allowed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def _has_policy_violation(metadata: Any) -> bool:
    return isinstance(metadata, dict) and bool(metadata.get("policy_violation"))


def build_semantic_binding_execution_harness_result_v1(
    activation_result,
) -> Service1SemanticBindingExecutionHarnessResultV1:
    pathology_code = getattr(activation_result, "pathology_code", "")
    activation_status = activation_result.activation_status

    def _blocked(
        status: str,
        layer: str,
        reason: str,
    ) -> Service1SemanticBindingExecutionHarnessResultV1:
        return Service1SemanticBindingExecutionHarnessResultV1(
            pathology_code=pathology_code,
            harness_status=status,
            activation_status=activation_status,
            semantic_binding_request_prepared=False,
            semantic_binding_execution_allowed=False,
            runtime_allowed=False,
            phase_5_allowed=False,
            product_ready=False,
            blocking_layer=layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    if _has_policy_violation(getattr(activation_result, "metadata", None)):
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_POLICY,
            "policy",
            "policy_violation",
        )

    if bool(getattr(activation_result, "semantic_binding_execution_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_EXECUTION_GUARD,
            "execution_guard",
            "execution_guard_open",
        )

    if bool(getattr(activation_result, "runtime_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_RUNTIME_GUARD,
            "runtime_guard",
            "runtime_guard_open",
        )

    if bool(getattr(activation_result, "phase_5_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PHASE_5_GUARD,
            "phase_5_guard",
            "phase_5_guard_open",
        )

    if bool(getattr(activation_result, "product_ready", False)):
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PRODUCT_READY_GUARD,
            "product_ready_guard",
            "product_ready_guard_open",
        )

    if activation_status != SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE:
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION,
            "activation",
            "activation_not_ready",
        )

    if not bool(getattr(activation_result, "semantic_binding_activation_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION,
            "activation",
            "semantic_binding_activation_not_allowed",
        )

    return Service1SemanticBindingExecutionHarnessResultV1(
        pathology_code=pathology_code,
        harness_status=SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE,
        activation_status=activation_status,
        semantic_binding_request_prepared=True,
        semantic_binding_execution_allowed=False,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

"""
SERVICE_1_SEMANTIC_BINDING_ACTIVATION_V1

Pure activation boundary for Servicio 1 semantic binding.
No runtime, mapper, engine, CLI, case fixtures, delivery, or JSON mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_runtime_catalog_pipeline_composition_v1 import (
    COMPOSITION_READY_FOR_SEMANTIC_BINDING,
)

SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE = "SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE"
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION = "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION"
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY = "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY"
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD = "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD"
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD = "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD"
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD = "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD"


@dataclass(frozen=True)
class Service1SemanticBindingActivationResultV1:
    schema_version: str = "SERVICE_1_SEMANTIC_BINDING_ACTIVATION_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    activation_status: str = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
    composition_status: str = ""
    semantic_binding_activation_allowed: bool = False
    semantic_binding_execution_allowed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def _has_policy_violation(metadata: Any) -> bool:
    return isinstance(metadata, dict) and bool(metadata.get("policy_violation"))


def build_semantic_binding_activation_result_v1(
    composition_result,
) -> Service1SemanticBindingActivationResultV1:
    pathology_code = getattr(composition_result, "pathology_code", "")
    composition_status = composition_result.composition_status

    def _blocked(status: str, layer: str, reason: str) -> Service1SemanticBindingActivationResultV1:
        return Service1SemanticBindingActivationResultV1(
            pathology_code=pathology_code,
            activation_status=status,
            composition_status=composition_status,
            semantic_binding_activation_allowed=False,
            semantic_binding_execution_allowed=False,
            runtime_allowed=False,
            phase_5_allowed=False,
            product_ready=False,
            blocking_layer=layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    if _has_policy_violation(getattr(composition_result, "metadata", None)):
        return _blocked(SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY, "policy", "policy_violation")

    if bool(getattr(composition_result, "runtime_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD,
            "runtime_guard",
            "runtime_guard_open",
        )

    if bool(getattr(composition_result, "phase_5_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD,
            "phase_5_guard",
            "phase_5_guard_open",
        )

    if bool(getattr(composition_result, "product_ready", False)):
        return _blocked(
            SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD,
            "product_ready_guard",
            "product_ready_guard_open",
        )

    if composition_status != COMPOSITION_READY_FOR_SEMANTIC_BINDING:
        return _blocked(
            SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION,
            "composition",
            "composition_not_ready",
        )

    if not bool(getattr(composition_result, "semantic_binding_consideration_allowed", False)):
        return _blocked(
            SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION,
            "composition",
            "semantic_binding_consideration_not_allowed",
        )

    return Service1SemanticBindingActivationResultV1(
        pathology_code=pathology_code,
        activation_status=SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE,
        composition_status=composition_status,
        semantic_binding_activation_allowed=True,
        semantic_binding_execution_allowed=False,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

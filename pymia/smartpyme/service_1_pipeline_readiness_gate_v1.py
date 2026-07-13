"""
SERVICE_1_PIPELINE_READINESS_GATE_V1

Pure, read-only gate that aggregates the four governed Servicio 1 layers
into a single pipeline readiness decision for semantic evidence binding.

This module is a governance aggregator, not an execution bridge. It
performs no runtime, no mapper, no engine, no CLI, no case traces, and
never mutates JSON.

Mode: PURE GATE ONLY
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_owner_confirmation_boundary_v1 import OWNER_CONFIRMED
from pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1 import (
    ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
)
from pymia.smartpyme.service_1_runtime_catalog_binding_contract_v1 import (
    CATALOG_BINDING_READY_CANDIDATE,
)
from pymia.smartpyme.service_1_runtime_catalog_to_semantic_binding_handoff_v1 import (
    HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING,
)


PIPELINE_READY_FOR_SEMANTIC_BINDING = "PIPELINE_READY_FOR_SEMANTIC_BINDING"
PIPELINE_BLOCKED_BY_CATALOG = "PIPELINE_BLOCKED_BY_CATALOG"
PIPELINE_BLOCKED_BY_ADAPTER = "PIPELINE_BLOCKED_BY_ADAPTER"
PIPELINE_BLOCKED_BY_HANDOFF = "PIPELINE_BLOCKED_BY_HANDOFF"
PIPELINE_BLOCKED_BY_OWNER_CONFIRMATION = "PIPELINE_BLOCKED_BY_OWNER_CONFIRMATION"
PIPELINE_BLOCKED_BY_EVIDENCE = "PIPELINE_BLOCKED_BY_EVIDENCE"
PIPELINE_BLOCKED_BY_POLICY = "PIPELINE_BLOCKED_BY_POLICY"


@dataclass(frozen=True)
class Service1PipelineReadinessGateResultV1:
    """Governed pipeline readiness gate result."""

    schema_version: str = "SERVICE_1_PIPELINE_READINESS_GATE_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    gate_status: str = PIPELINE_BLOCKED_BY_POLICY
    catalog_binding_status: str = ""
    adapter_status: str = ""
    handoff_status: str = ""
    owner_confirmation_status: str = ""
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    runtime_allowed: bool = False  # Always False per invariant I7
    phase_5_allowed: bool = False  # Always False per invariant I8
    metadata: dict[str, Any] = field(default_factory=dict)


def _has_policy_violation(metadata: Any) -> bool:
    if not isinstance(metadata, dict):
        return False
    return bool(metadata.get("policy_violation"))


def build_pipeline_readiness_gate_result_v1(
    catalog_binding_result,
    adapter_context,
    handoff_context,
    owner_confirmation_result,
) -> Service1PipelineReadinessGateResultV1:
    """
    Pure gate function aggregating four governed layer outputs.

    Implements fail-closed governance:
      I7. runtime_allowed is always false.
      I8. phase_5_allowed is always false.

    Args:
        catalog_binding_result: Service1RuntimeCatalogBindingResultV1
        adapter_context: Service1RuntimeCatalogBindingAdapterContextV1
        handoff_context: Service1SemanticBindingConsiderationContextV1
        owner_confirmation_result: Service1OwnerConfirmationResultV1

    Returns:
        Service1PipelineReadinessGateResultV1 with mapped gate_status.
    """
    pathology_code = getattr(catalog_binding_result, "pathology_code", "")
    catalog_status = catalog_binding_result.readiness_status
    adapter_status = adapter_context.adapter_status
    handoff_status = handoff_context.handoff_status
    owner_status = owner_confirmation_result.confirmation_status

    def _result(gate_status: str, blocking_layer: str | None, reason: str) -> (
        Service1PipelineReadinessGateResultV1
    ):
        return Service1PipelineReadinessGateResultV1(
            pathology_code=pathology_code,
            gate_status=gate_status,
            catalog_binding_status=catalog_status,
            adapter_status=adapter_status,
            handoff_status=handoff_status,
            owner_confirmation_status=owner_status,
            blocking_layer=blocking_layer,
            blocking_reasons=(reason,),
            metadata={"rule": reason},
        )

    # Policy violation takes precedence across all layers
    if (
        _has_policy_violation(catalog_binding_result.metadata)
        or _has_policy_violation(adapter_context.metadata)
        or _has_policy_violation(handoff_context.metadata)
        or _has_policy_violation(owner_confirmation_result.metadata)
    ):
        return _result(PIPELINE_BLOCKED_BY_POLICY, "policy", "policy_violation")

    # Catalog readiness
    if catalog_status != CATALOG_BINDING_READY_CANDIDATE:
        return _result(PIPELINE_BLOCKED_BY_CATALOG, "catalog", "catalog_not_ready")

    # Adapter readiness
    if adapter_status != ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION:
        return _result(PIPELINE_BLOCKED_BY_ADAPTER, "adapter", "adapter_not_ready")

    # Handoff readiness
    if handoff_status != HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING:
        return _result(PIPELINE_BLOCKED_BY_HANDOFF, "handoff", "handoff_not_ready")

    # Owner confirmation
    if owner_status != OWNER_CONFIRMED:
        return _result(
            PIPELINE_BLOCKED_BY_OWNER_CONFIRMATION,
            "owner_confirmation",
            "owner_not_confirmed",
        )

    # Required evidence present in catalog
    if not catalog_binding_result.required_evidence:
        return _result(PIPELINE_BLOCKED_BY_EVIDENCE, "evidence", "required_evidence_missing")

    # All layers ready
    return Service1PipelineReadinessGateResultV1(
        pathology_code=pathology_code,
        gate_status=PIPELINE_READY_FOR_SEMANTIC_BINDING,
        catalog_binding_status=catalog_status,
        adapter_status=adapter_status,
        handoff_status=handoff_status,
        owner_confirmation_status=owner_status,
        blocking_layer=None,
        blocking_reasons=(),
        metadata={"rule": "ready"},
    )

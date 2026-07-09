"""
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_V1

Pure, read-only composition layer for the governed Servicio 1 runtime-catalog
semantic readiness pipeline.

This module composes already-governed upstream outputs into one composition
result. It performs no runtime, no mapper, no engine, no CLI, no delivery,
no case traces, and never mutates JSON.

Mode: PURE COMPOSITION ONLY
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_owner_confirmation_boundary_v1 import OWNER_CONFIRMED
from pymia.smartpyme.service_1_pipeline_readiness_gate_v1 import (
    PIPELINE_READY_FOR_SEMANTIC_BINDING,
)
from pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1 import (
    ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
)
from pymia.smartpyme.service_1_runtime_catalog_binding_contract_v1 import (
    CATALOG_BINDING_READY_CANDIDATE,
)
from pymia.smartpyme.service_1_runtime_catalog_to_semantic_binding_handoff_v1 import (
    HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING,
)


COMPOSITION_READY_FOR_SEMANTIC_BINDING = "COMPOSITION_READY_FOR_SEMANTIC_BINDING"
COMPOSITION_BLOCKED_BY_CATALOG = "COMPOSITION_BLOCKED_BY_CATALOG"
COMPOSITION_BLOCKED_BY_ADAPTER = "COMPOSITION_BLOCKED_BY_ADAPTER"
COMPOSITION_BLOCKED_BY_HANDOFF = "COMPOSITION_BLOCKED_BY_HANDOFF"
COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION = (
    "COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION"
)
COMPOSITION_BLOCKED_BY_GATE = "COMPOSITION_BLOCKED_BY_GATE"
COMPOSITION_BLOCKED_BY_POLICY = "COMPOSITION_BLOCKED_BY_POLICY"


@dataclass(frozen=True)
class Service1RuntimeCatalogPipelineCompositionResultV1:
    """Governed runtime-catalog pipeline composition result."""

    schema_version: str = "SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    composition_status: str = COMPOSITION_BLOCKED_BY_POLICY
    catalog_binding_status: str = ""
    adapter_status: str = ""
    handoff_status: str = ""
    owner_confirmation_status: str = ""
    gate_status: str = ""
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    semantic_binding_consideration_allowed: bool = False
    runtime_allowed: bool = False
    phase_5_allowed: bool = False
    product_ready: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


def _has_policy_violation(metadata: Any) -> bool:
    if not isinstance(metadata, dict):
        return False
    return bool(metadata.get("policy_violation"))


def build_runtime_catalog_pipeline_composition_result_v1(
    catalog_binding_result,
    adapter_context,
    handoff_context,
    owner_confirmation_result,
    readiness_gate_result,
) -> Service1RuntimeCatalogPipelineCompositionResultV1:
    """
    Pure fail-closed composition of governed Servicio 1 readiness outputs.

    This function authorizes only semantic binding consideration when every
    upstream governed layer and the readiness gate are ready. It never
    authorizes runtime, Phase 5, or product-ready status.
    """
    pathology_code = getattr(catalog_binding_result, "pathology_code", "")
    catalog_status = catalog_binding_result.readiness_status
    adapter_status = adapter_context.adapter_status
    handoff_status = handoff_context.handoff_status
    owner_status = owner_confirmation_result.confirmation_status
    gate_status = readiness_gate_result.gate_status

    def _blocked(
        composition_status: str,
        blocking_layer: str,
        reason: str,
    ) -> Service1RuntimeCatalogPipelineCompositionResultV1:
        return Service1RuntimeCatalogPipelineCompositionResultV1(
            pathology_code=pathology_code,
            composition_status=composition_status,
            catalog_binding_status=catalog_status,
            adapter_status=adapter_status,
            handoff_status=handoff_status,
            owner_confirmation_status=owner_status,
            gate_status=gate_status,
            blocking_layer=blocking_layer,
            blocking_reasons=(reason,),
            semantic_binding_consideration_allowed=False,
            runtime_allowed=False,
            phase_5_allowed=False,
            product_ready=False,
            metadata={"rule": reason},
        )

    if (
        _has_policy_violation(getattr(catalog_binding_result, "metadata", None))
        or _has_policy_violation(getattr(adapter_context, "metadata", None))
        or _has_policy_violation(getattr(handoff_context, "metadata", None))
        or _has_policy_violation(getattr(owner_confirmation_result, "metadata", None))
        or _has_policy_violation(getattr(readiness_gate_result, "metadata", None))
    ):
        return _blocked(COMPOSITION_BLOCKED_BY_POLICY, "policy", "policy_violation")

    if catalog_status != CATALOG_BINDING_READY_CANDIDATE:
        return _blocked(
            COMPOSITION_BLOCKED_BY_CATALOG,
            "catalog",
            "catalog_not_ready",
        )

    if adapter_status != ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION:
        return _blocked(
            COMPOSITION_BLOCKED_BY_ADAPTER,
            "adapter",
            "adapter_not_ready",
        )

    if handoff_status != HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING:
        return _blocked(
            COMPOSITION_BLOCKED_BY_HANDOFF,
            "handoff",
            "handoff_not_ready",
        )

    if owner_status != OWNER_CONFIRMED:
        return _blocked(
            COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION,
            "owner_confirmation",
            "owner_not_confirmed",
        )

    if gate_status != PIPELINE_READY_FOR_SEMANTIC_BINDING:
        return _blocked(
            COMPOSITION_BLOCKED_BY_GATE,
            "readiness_gate",
            "gate_not_ready",
        )

    return Service1RuntimeCatalogPipelineCompositionResultV1(
        pathology_code=pathology_code,
        composition_status=COMPOSITION_READY_FOR_SEMANTIC_BINDING,
        catalog_binding_status=catalog_status,
        adapter_status=adapter_status,
        handoff_status=handoff_status,
        owner_confirmation_status=owner_status,
        gate_status=gate_status,
        blocking_layer=None,
        blocking_reasons=(),
        semantic_binding_consideration_allowed=True,
        runtime_allowed=False,
        phase_5_allowed=False,
        product_ready=False,
        metadata={"rule": "ready"},
    )

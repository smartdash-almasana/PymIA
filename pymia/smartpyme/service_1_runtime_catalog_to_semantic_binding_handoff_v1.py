"""
SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_V1

Pure, read-only handoff layer between
Service1RuntimeCatalogBindingAdapterContextV1 and a future semantic
evidence binding consideration context.

This module is a governance boundary, not an execution bridge. It
consumes only the adapter context and emits a governed handoff context.
It never imports runtime, mapper, engine, CLI, or case traces, and never
mutates JSON.

Mode: PURE HANDOFF ONLY
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1 import (
    ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED,
    ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
    Service1RuntimeCatalogBindingAdapterContextV1,
)


HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING = (
    "HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING"
)
HANDOFF_BLOCKED_BY_ADAPTER_STATUS = "HANDOFF_BLOCKED_BY_ADAPTER_STATUS"
HANDOFF_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED = (
    "HANDOFF_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED"
)
HANDOFF_BLOCKED_BY_MISSING_FORMULA_REFS = "HANDOFF_BLOCKED_BY_MISSING_FORMULA_REFS"
HANDOFF_BLOCKED_BY_MISSING_REQUIRED_VARIABLES = (
    "HANDOFF_BLOCKED_BY_MISSING_REQUIRED_VARIABLES"
)
HANDOFF_BLOCKED_BY_MISSING_REQUIRED_EVIDENCE = (
    "HANDOFF_BLOCKED_BY_MISSING_REQUIRED_EVIDENCE"
)
HANDOFF_BLOCKED_BY_POLICY = "HANDOFF_BLOCKED_BY_POLICY"


@dataclass(frozen=True)
class Service1SemanticBindingConsiderationContextV1:
    """Governed context prepared for future semantic evidence binding."""

    schema_version: str = "SERVICE_1_SEMANTIC_BINDING_CONSIDERATION_CONTEXT_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    upstream_adapter_status: str = ""
    handoff_status: str = HANDOFF_BLOCKED_BY_POLICY
    formula_refs: tuple[str, ...] = ()
    resolved_formula_ids: tuple[str, ...] = ()
    required_variables: tuple[str, ...] = ()
    resolved_variables: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    minimum_semantic_bindings: tuple[str, ...] = ()
    owner_confirmation_required: bool = False
    semantic_evidence_binding_allowed: bool = False
    semantic_binding_blocking_reasons: tuple[str, ...] = ()
    runtime_allowed: bool = False  # Always False per invariant I1
    phase_5_allowed: bool = False  # Always False per invariant I2
    metadata: dict[str, Any] = field(default_factory=dict)


def build_handoff_context_v1(
    upstream_context: Service1RuntimeCatalogBindingAdapterContextV1,
) -> Service1SemanticBindingConsiderationContextV1:
    """
    Pure handoff function consuming adapter context and emitting governed handoff.

    Implements fail-closed invariants:
      I1. runtime_allowed must remain False.
      I2. phase_5_allowed must remain False.

    Args:
        upstream_context: Service1RuntimeCatalogBindingAdapterContextV1

    Returns:
        Service1SemanticBindingConsiderationContextV1 with mapped handoff_status
    """
    # Invariant I1: upstream runtime_allowed must be False
    if upstream_context.runtime_allowed is not False:
        raise ValueError("Invariant I1 violated: upstream runtime_allowed must be False")

    # Invariant I2: upstream phase_5_allowed must be False
    if upstream_context.phase_5_allowed is not False:
        raise ValueError("Invariant I2 violated: upstream phase_5_allowed must be False")

    blocking_reasons: list[str] = []

    # Owner confirmation required takes precedence over adapter readiness
    if upstream_context.owner_confirmation_required:
        blocking_reasons.append("owner_confirmation_required")
        return Service1SemanticBindingConsiderationContextV1(
            pathology_code=upstream_context.pathology_code,
            upstream_adapter_status=upstream_context.adapter_status,
            handoff_status=HANDOFF_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED,
            formula_refs=upstream_context.formula_refs,
            resolved_formula_ids=upstream_context.resolved_formula_ids,
            required_variables=upstream_context.required_variables,
            resolved_variables=upstream_context.resolved_variables,
            required_evidence=upstream_context.required_evidence,
            minimum_semantic_bindings=upstream_context.minimum_semantic_bindings,
            owner_confirmation_required=True,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"rule": "owner_confirmation"},
        )

    # Adapter not ready -> blocked by adapter status
    if upstream_context.adapter_status != ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION:
        blocking_reasons.append("adapter_status_not_ready")
        return Service1SemanticBindingConsiderationContextV1(
            pathology_code=upstream_context.pathology_code,
            upstream_adapter_status=upstream_context.adapter_status,
            handoff_status=HANDOFF_BLOCKED_BY_ADAPTER_STATUS,
            formula_refs=upstream_context.formula_refs,
            resolved_formula_ids=upstream_context.resolved_formula_ids,
            required_variables=upstream_context.required_variables,
            resolved_variables=upstream_context.resolved_variables,
            required_evidence=upstream_context.required_evidence,
            minimum_semantic_bindings=upstream_context.minimum_semantic_bindings,
            owner_confirmation_required=upstream_context.owner_confirmation_required,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"rule": "adapter_status"},
        )

    # Empty formula_refs -> blocked
    if not upstream_context.formula_refs:
        blocking_reasons.append("empty_formula_refs")
        return Service1SemanticBindingConsiderationContextV1(
            pathology_code=upstream_context.pathology_code,
            upstream_adapter_status=upstream_context.adapter_status,
            handoff_status=HANDOFF_BLOCKED_BY_MISSING_FORMULA_REFS,
            formula_refs=upstream_context.formula_refs,
            resolved_formula_ids=upstream_context.resolved_formula_ids,
            required_variables=upstream_context.required_variables,
            resolved_variables=upstream_context.resolved_variables,
            required_evidence=upstream_context.required_evidence,
            minimum_semantic_bindings=upstream_context.minimum_semantic_bindings,
            owner_confirmation_required=upstream_context.owner_confirmation_required,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"rule": "missing_formula_refs"},
        )

    # Empty required_variables -> blocked
    if not upstream_context.required_variables:
        blocking_reasons.append("empty_required_variables")
        return Service1SemanticBindingConsiderationContextV1(
            pathology_code=upstream_context.pathology_code,
            upstream_adapter_status=upstream_context.adapter_status,
            handoff_status=HANDOFF_BLOCKED_BY_MISSING_REQUIRED_VARIABLES,
            formula_refs=upstream_context.formula_refs,
            resolved_formula_ids=upstream_context.resolved_formula_ids,
            required_variables=upstream_context.required_variables,
            resolved_variables=upstream_context.resolved_variables,
            required_evidence=upstream_context.required_evidence,
            minimum_semantic_bindings=upstream_context.minimum_semantic_bindings,
            owner_confirmation_required=upstream_context.owner_confirmation_required,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"rule": "missing_required_variables"},
        )

    # Empty required_evidence -> blocked
    if not upstream_context.required_evidence:
        blocking_reasons.append("empty_required_evidence")
        return Service1SemanticBindingConsiderationContextV1(
            pathology_code=upstream_context.pathology_code,
            upstream_adapter_status=upstream_context.adapter_status,
            handoff_status=HANDOFF_BLOCKED_BY_MISSING_REQUIRED_EVIDENCE,
            formula_refs=upstream_context.formula_refs,
            resolved_formula_ids=upstream_context.resolved_formula_ids,
            required_variables=upstream_context.required_variables,
            resolved_variables=upstream_context.resolved_variables,
            required_evidence=upstream_context.required_evidence,
            minimum_semantic_bindings=upstream_context.minimum_semantic_bindings,
            owner_confirmation_required=upstream_context.owner_confirmation_required,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"rule": "missing_required_evidence"},
        )

    # Ready: adapter ready + complete formula/variables/evidence + no owner confirmation
    return Service1SemanticBindingConsiderationContextV1(
        pathology_code=upstream_context.pathology_code,
        upstream_adapter_status=upstream_context.adapter_status,
        handoff_status=HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING,
        formula_refs=upstream_context.formula_refs,
        resolved_formula_ids=upstream_context.resolved_formula_ids,
        required_variables=upstream_context.required_variables,
        resolved_variables=upstream_context.resolved_variables,
        required_evidence=upstream_context.required_evidence,
        minimum_semantic_bindings=upstream_context.minimum_semantic_bindings,
        owner_confirmation_required=upstream_context.owner_confirmation_required,
        semantic_evidence_binding_allowed=True,
        semantic_binding_blocking_reasons=tuple(blocking_reasons),
        metadata={"rule": "ready"},
    )

"""
SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_V1

Pure, read-only adapter that consumes Service1RuntimeCatalogBindingResultV1
and emits a non-executing adapter context for future semantic evidence binding consideration.

This adapter is a governance handoff, not a runtime bridge. It preserves fail-closed statuses
and never converts catalog readiness into runtime authorization.

Mode: PURE ADAPTER ONLY
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymia.smartpyme.service_1_runtime_catalog_binding_contract_v1 import (
    Service1RuntimeCatalogBindingResultV1,
    CATALOG_BINDING_READY_CANDIDATE,
    MISSING_FORMULA_REFS,
    UNKNOWN_PATHOLOGY_CODE,
    FORMULA_REF_NOT_FOUND,
    REQUIRED_VARIABLE_NOT_FOUND,
    REQUIRED_EVIDENCE_MISSING,
    OWNER_CONFIRMATION_REQUIRED,
    RUNTIME_BLOCKED_BY_POLICY,
)


# Adapter status constants per adapter plan section 5
ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION = (
    "ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION"
)
ADAPTER_BLOCKED_BY_RUNTIME_CATALOG_STATUS = "ADAPTER_BLOCKED_BY_RUNTIME_CATALOG_STATUS"
ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED = "ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED"
ADAPTER_BLOCKED_BY_POLICY = "ADAPTER_BLOCKED_BY_POLICY"
ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY = "ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY"
ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS = "ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS"
ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND = "ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND"
ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND = "ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND"
ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING = "ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING"

# Status mapping per adapter plan section 6
_UPSTREAM_TO_ADAPTER_STATUS: dict[str, str] = {
    UNKNOWN_PATHOLOGY_CODE: ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY,
    MISSING_FORMULA_REFS: ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS,
    FORMULA_REF_NOT_FOUND: ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND,
    REQUIRED_VARIABLE_NOT_FOUND: ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND,
    REQUIRED_EVIDENCE_MISSING: ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING,
    OWNER_CONFIRMATION_REQUIRED: ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED,
    RUNTIME_BLOCKED_BY_POLICY: ADAPTER_BLOCKED_BY_POLICY,
    CATALOG_BINDING_READY_CANDIDATE: ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
}

# Allowed upstream statuses for validation
_ALLOWED_UPSTREAM_STATUSES = frozenset(_UPSTREAM_TO_ADAPTER_STATUS.keys())


@dataclass(frozen=True)
class Service1RuntimeCatalogBindingAdapterContextV1:
    """
    Adapter output shape per adapter plan section 4.
    
    All authorization flags remain False by invariants I1 and I2.
    semantic_binding_consideration_allowed can be True only when
    upstream_readiness_status is CATALOG_BINDING_READY_CANDIDATE (invariant I13).
    """
    schema_version: str = "SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_CONTEXT_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    upstream_readiness_status: str = ""
    adapter_status: str = ADAPTER_BLOCKED_BY_POLICY
    formula_refs: tuple[str, ...] = ()
    resolved_formula_ids: tuple[str, ...] = ()
    required_variables: tuple[str, ...] = ()
    resolved_variables: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    minimum_semantic_bindings: tuple[str, ...] = ()
    owner_confirmation_required: bool = False
    semantic_binding_consideration_allowed: bool = False
    semantic_binding_blocking_reasons: tuple[str, ...] = ()
    runtime_allowed: bool = False  # Always False per invariant I1
    phase_5_allowed: bool = False  # Always False per invariant I2
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        """Validate invariants after initialization."""
        # I1: runtime_allowed is always false
        if self.runtime_allowed is not False:
            raise ValueError("Invariant I1 violated: runtime_allowed must be False")
        
        # I2: phase_5_allowed is always false
        if self.phase_5_allowed is not False:
            raise ValueError("Invariant I2 violated: phase_5_allowed must be False")


def build_service_1_runtime_catalog_binding_adapter_context_v1(
    upstream_result: Service1RuntimeCatalogBindingResultV1 | None,
) -> Service1RuntimeCatalogBindingAdapterContextV1:
    """
    Pure adapter function that consumes upstream contract result and emits adapter context.
    
    Implements fail-closed behavior per adapter plan section 8.
    Status mapping per adapter plan section 6.
    
    Args:
        upstream_result: Service1RuntimeCatalogBindingResultV1 from contract, or None
    
    Returns:
        Service1RuntimeCatalogBindingAdapterContextV1 with mapped status and fields
    """
    blocking_reasons: list[str] = []
    
    # Fail-closed rule F1: Missing upstream result
    if upstream_result is None:
        blocking_reasons.append("missing_upstream_result")
        return Service1RuntimeCatalogBindingAdapterContextV1(
            adapter_status=ADAPTER_BLOCKED_BY_POLICY,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F1"},
        )
    
    # Fail-closed rule F3: upstream runtime_allowed not false
    if upstream_result.runtime_allowed is not False:
        blocking_reasons.append("upstream_runtime_allowed_not_false")
        return Service1RuntimeCatalogBindingAdapterContextV1(
            pathology_code=upstream_result.pathology_code,
            upstream_readiness_status=upstream_result.readiness_status,
            adapter_status=ADAPTER_BLOCKED_BY_POLICY,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F3"},
        )
    
    # Fail-closed rule F4: upstream phase_5_allowed not false
    if upstream_result.phase_5_allowed is not False:
        blocking_reasons.append("upstream_phase_5_allowed_not_false")
        return Service1RuntimeCatalogBindingAdapterContextV1(
            pathology_code=upstream_result.pathology_code,
            upstream_readiness_status=upstream_result.readiness_status,
            adapter_status=ADAPTER_BLOCKED_BY_POLICY,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F4"},
        )
    
    # Fail-closed rule F2: Unknown upstream readiness_status
    if upstream_result.readiness_status not in _ALLOWED_UPSTREAM_STATUSES:
        blocking_reasons.append("unknown_upstream_status")
        return Service1RuntimeCatalogBindingAdapterContextV1(
            pathology_code=upstream_result.pathology_code,
            upstream_readiness_status=upstream_result.readiness_status,
            adapter_status=ADAPTER_BLOCKED_BY_POLICY,
            semantic_binding_blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F2"},
        )
    
    # Map upstream status to adapter status per section 6
    adapter_status = _UPSTREAM_TO_ADAPTER_STATUS[upstream_result.readiness_status]
    
    # Determine semantic_binding_consideration_allowed per invariant I13
    # True only when upstream is CATALOG_BINDING_READY_CANDIDATE AND passes fail-closed checks
    semantic_consideration_allowed = False
    
    if upstream_result.readiness_status == CATALOG_BINDING_READY_CANDIDATE:
        # Fail-closed rule F6: Empty required_variables blocks semantic consideration
        if not upstream_result.required_variables:
            blocking_reasons.append("empty_required_variables")
            adapter_status = ADAPTER_BLOCKED_BY_POLICY
        # Fail-closed rule F7: Empty required_evidence blocks semantic consideration
        elif not upstream_result.required_evidence:
            blocking_reasons.append("empty_required_evidence")
            adapter_status = ADAPTER_BLOCKED_BY_POLICY
        else:
            # Ready candidate with non-empty variables and evidence
            semantic_consideration_allowed = True
    
    return Service1RuntimeCatalogBindingAdapterContextV1(
        pathology_code=upstream_result.pathology_code,
        upstream_readiness_status=upstream_result.readiness_status,
        adapter_status=adapter_status,
        formula_refs=upstream_result.formula_refs,
        resolved_formula_ids=upstream_result.resolved_formula_ids,
        required_variables=upstream_result.required_variables,
        resolved_variables=upstream_result.resolved_variables,
        required_evidence=upstream_result.required_evidence,
        minimum_semantic_bindings=upstream_result.minimum_semantic_bindings,
        owner_confirmation_required=upstream_result.owner_confirmation_required,
        semantic_binding_consideration_allowed=semantic_consideration_allowed,
        semantic_binding_blocking_reasons=tuple(blocking_reasons),
        metadata={
            "adapter_version": "V1",
            "upstream_catalog_origin": upstream_result.catalog_origin,
            "upstream_blocking_reasons": upstream_result.blocking_reasons,
        },
    )

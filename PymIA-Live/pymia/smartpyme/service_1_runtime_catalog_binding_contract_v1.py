"""
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1

Pure, fail-closed, non-executing contract boundary for catalog governance.

This module implements the contract boundary governing:
  pathology_code -> formula_refs -> required_variables -> required_evidence -> readiness_status

It does not authorize runtime connection, mapper changes, engine changes,
CLI changes, JSON mutation, Phase 5, or product-ready claims.

Mode: PURE CONTRACT ONLY
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Status constants per contract section 7
CATALOG_BINDING_READY_CANDIDATE = "CATALOG_BINDING_READY_CANDIDATE"
MISSING_FORMULA_REFS = "MISSING_FORMULA_REFS"
UNKNOWN_PATHOLOGY_CODE = "UNKNOWN_PATHOLOGY_CODE"
FORMULA_REF_NOT_FOUND = "FORMULA_REF_NOT_FOUND"
REQUIRED_VARIABLE_NOT_FOUND = "REQUIRED_VARIABLE_NOT_FOUND"
REQUIRED_EVIDENCE_MISSING = "REQUIRED_EVIDENCE_MISSING"
OWNER_CONFIRMATION_REQUIRED = "OWNER_CONFIRMATION_REQUIRED"
RUNTIME_BLOCKED_BY_POLICY = "RUNTIME_BLOCKED_BY_POLICY"

ALLOWED_STATUSES = frozenset({
    CATALOG_BINDING_READY_CANDIDATE,
    MISSING_FORMULA_REFS,
    UNKNOWN_PATHOLOGY_CODE,
    FORMULA_REF_NOT_FOUND,
    REQUIRED_VARIABLE_NOT_FOUND,
    REQUIRED_EVIDENCE_MISSING,
    OWNER_CONFIRMATION_REQUIRED,
    RUNTIME_BLOCKED_BY_POLICY,
})


@dataclass(frozen=True)
class Service1RuntimeCatalogBindingResultV1:
    """
    Contract output shape (documental).
    
    All authorization flags remain False by invariant I1 and I2.
    """
    schema_version: str = "SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    catalog_origin: str = "unknown"  # runtime_json_overlap | runtime_only_candidate | json_catalog
    formula_refs: tuple[str, ...] = ()
    resolved_formula_ids: tuple[str, ...] = ()
    missing_formula_refs: tuple[str, ...] = ()
    required_variables: tuple[str, ...] = ()
    resolved_variables: tuple[str, ...] = ()
    missing_variables: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    minimum_semantic_bindings: tuple[str, ...] = ()
    owner_confirmation_required: bool = False
    readiness_status: str = UNKNOWN_PATHOLOGY_CODE
    blocking_reasons: tuple[str, ...] = ()
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
        
        # Validate readiness_status is allowed
        if self.readiness_status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid readiness_status: {self.readiness_status}")


def _load_json(path: Path) -> dict[str, Any] | None:
    """
    Load and parse a JSON artifact file.
    
    Returns None if file cannot be loaded (fail-closed).
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def load_service_1_runtime_catalog_binding_inputs_v1(
    repo_root: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    """
    Load all four input artifacts consumed by the contract.
    
    Returns:
        Tuple of (enriched_pathology_catalog, formula_catalog, variable_catalog, evidence_matrix)
        Each element is None if the artifact cannot be loaded.
    """
    enriched_path = repo_root / "PymIA-Live/docs/pathology_catalog.enriched.v1.json"
    formula_path = repo_root / "PymIA-Live/docs/formula_catalog.v1.json"
    variable_path = repo_root / "PymIA-Live/docs/service_1_semantic_variable_catalog.v1.json"
    matrix_path = repo_root / "PymIA-Live/docs/service_1_formula_pathology_evidence_matrix.v1.json"
    
    enriched_catalog = _load_json(enriched_path)
    formula_catalog = _load_json(formula_path)
    variable_catalog = _load_json(variable_path)
    evidence_matrix = _load_json(matrix_path)
    
    return enriched_catalog, formula_catalog, variable_catalog, evidence_matrix


def build_service_1_runtime_catalog_binding_result_v1(
    pathology_code: str,
    enriched_catalog: dict[str, Any] | None,
    formula_catalog: dict[str, Any] | None,
    variable_catalog: dict[str, Any] | None,
    evidence_matrix: dict[str, Any] | None,
) -> Service1RuntimeCatalogBindingResultV1:
    """
    Pure resolver for runtime catalog binding contract.
    
    Implements fail-closed behavior per contract section 9.
    Priority order per contract section 7:
      1. UNKNOWN_PATHOLOGY_CODE (highest priority)
      2. MISSING_FORMULA_REFS
      3. FORMULA_REF_NOT_FOUND
      4. REQUIRED_VARIABLE_NOT_FOUND
      5. REQUIRED_EVIDENCE_MISSING
      6. OWNER_CONFIRMATION_REQUIRED
      7. RUNTIME_BLOCKED_BY_POLICY
      8. CATALOG_BINDING_READY_CANDIDATE (lowest priority)
    
    Args:
        pathology_code: The pathology code to resolve
        enriched_catalog: Loaded pathology_catalog.enriched.v1.json or None
        formula_catalog: Loaded formula_catalog.v1.json or None
        variable_catalog: Loaded service_1_semantic_variable_catalog.v1.json or None
        evidence_matrix: Loaded service_1_formula_pathology_evidence_matrix.v1.json or None
    
    Returns:
        Service1RuntimeCatalogBindingResultV1 with resolved status and fields
    """
    blocking_reasons: list[str] = []
    
    # Fail-closed rule F1: enriched catalog unavailable
    if enriched_catalog is None:
        blocking_reasons.append("enriched_catalog_unavailable")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            readiness_status=UNKNOWN_PATHOLOGY_CODE,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F1"},
        )
    
    # Fail-closed rule F4: evidence matrix unavailable
    if evidence_matrix is None:
        blocking_reasons.append("evidence_matrix_unavailable")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            readiness_status=RUNTIME_BLOCKED_BY_POLICY,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F4"},
        )
    
    # Priority 1: UNKNOWN_PATHOLOGY_CODE
    pathologies = enriched_catalog.get("pathologies", [])
    pathology_entry = None
    for p in pathologies:
        if p.get("pathology_code") == pathology_code:
            pathology_entry = p
            break
    
    if pathology_entry is None:
        blocking_reasons.append("pathology_code_not_in_enriched_catalog")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            readiness_status=UNKNOWN_PATHOLOGY_CODE,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_1"},
        )
    
    # Find corresponding entry in evidence matrix
    matrix_entries = evidence_matrix.get("entries", [])
    matrix_entry = None
    for e in matrix_entries:
        if e.get("pathology_code") == pathology_code:
            matrix_entry = e
            break
    
    if matrix_entry is None:
        # Matrix entry missing - treat as unknown
        blocking_reasons.append("pathology_code_not_in_evidence_matrix")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            readiness_status=UNKNOWN_PATHOLOGY_CODE,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "matrix_entry_missing"},
        )
    
    # Extract fields from matrix entry
    formula_refs = tuple(matrix_entry.get("formula_refs", []))
    required_variables = tuple(matrix_entry.get("required_variables", []))
    required_evidence = tuple(matrix_entry.get("required_evidence", []))
    minimum_semantic_bindings = tuple(matrix_entry.get("semantic_bindings", []))
    owner_confirmation_required = matrix_entry.get("owner_confirmation_required", False)
    
    # Priority 2: MISSING_FORMULA_REFS
    if not formula_refs:
        blocking_reasons.append("formula_refs_empty")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            required_variables=required_variables,
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=MISSING_FORMULA_REFS,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_2"},
        )
    
    # Fail-closed rule F2: formula catalog unavailable
    if formula_catalog is None:
        blocking_reasons.append("formula_catalog_unavailable")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            required_variables=required_variables,
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=FORMULA_REF_NOT_FOUND,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F2"},
        )
    
    # Priority 3: FORMULA_REF_NOT_FOUND
    formula_ids = {f.get("formula_id") for f in formula_catalog.get("formulas", [])}
    resolved_formula_ids: list[str] = []
    missing_formula_refs: list[str] = []
    
    for formula_ref in formula_refs:
        if formula_ref in formula_ids:
            resolved_formula_ids.append(formula_ref)
        else:
            missing_formula_refs.append(formula_ref)
    
    if missing_formula_refs:
        blocking_reasons.append("formula_ref_not_in_formula_catalog")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            resolved_formula_ids=tuple(resolved_formula_ids),
            missing_formula_refs=tuple(missing_formula_refs),
            required_variables=required_variables,
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=FORMULA_REF_NOT_FOUND,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_3"},
        )
    
    # Fail-closed rule F3: variable catalog unavailable
    if variable_catalog is None:
        blocking_reasons.append("variable_catalog_unavailable")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            resolved_formula_ids=tuple(resolved_formula_ids),
            missing_formula_refs=tuple(missing_formula_refs),
            required_variables=required_variables,
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=REQUIRED_VARIABLE_NOT_FOUND,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "F3"},
        )
    
    # Priority 4: REQUIRED_VARIABLE_NOT_FOUND
    variable_names = {v.get("variable_name") for v in variable_catalog.get("variables", [])}
    resolved_variables: list[str] = []
    missing_variables: list[str] = []
    
    for variable in required_variables:
        if variable in variable_names:
            resolved_variables.append(variable)
        else:
            missing_variables.append(variable)
    
    if missing_variables:
        blocking_reasons.append("required_variable_not_in_variable_catalog")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            resolved_formula_ids=tuple(resolved_formula_ids),
            missing_formula_refs=tuple(missing_formula_refs),
            required_variables=required_variables,
            resolved_variables=tuple(resolved_variables),
            missing_variables=tuple(missing_variables),
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=REQUIRED_VARIABLE_NOT_FOUND,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_4"},
        )
    
    # Priority 5: REQUIRED_EVIDENCE_MISSING
    if not required_evidence:
        blocking_reasons.append("required_evidence_empty_for_pathology_with_formula_refs")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            resolved_formula_ids=tuple(resolved_formula_ids),
            missing_formula_refs=tuple(missing_formula_refs),
            required_variables=required_variables,
            resolved_variables=tuple(resolved_variables),
            missing_variables=tuple(missing_variables),
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=REQUIRED_EVIDENCE_MISSING,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_5"},
        )
    
    # Priority 6: OWNER_CONFIRMATION_REQUIRED
    if owner_confirmation_required:
        blocking_reasons.append("owner_confirmation_required_by_evidence_matrix")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            resolved_formula_ids=tuple(resolved_formula_ids),
            missing_formula_refs=tuple(missing_formula_refs),
            required_variables=required_variables,
            resolved_variables=tuple(resolved_variables),
            missing_variables=tuple(missing_variables),
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=OWNER_CONFIRMATION_REQUIRED,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_6"},
        )
    
    # Priority 7: RUNTIME_BLOCKED_BY_POLICY
    runtime_connection_allowed_enriched = enriched_catalog.get("runtime_connection_allowed", False)
    runtime_connection_allowed_matrix = evidence_matrix.get("runtime_connection_allowed", False)
    runtime_allowed_entry = matrix_entry.get("runtime_allowed", False)
    
    if not (runtime_connection_allowed_enriched and runtime_connection_allowed_matrix and runtime_allowed_entry):
        blocking_reasons.append("runtime_connection_blocked_by_policy")
        return Service1RuntimeCatalogBindingResultV1(
            pathology_code=pathology_code,
            catalog_origin=pathology_entry.get("status", "unknown"),
            formula_refs=formula_refs,
            resolved_formula_ids=tuple(resolved_formula_ids),
            missing_formula_refs=tuple(missing_formula_refs),
            required_variables=required_variables,
            resolved_variables=tuple(resolved_variables),
            missing_variables=tuple(missing_variables),
            required_evidence=required_evidence,
            minimum_semantic_bindings=minimum_semantic_bindings,
            owner_confirmation_required=owner_confirmation_required,
            readiness_status=RUNTIME_BLOCKED_BY_POLICY,
            blocking_reasons=tuple(blocking_reasons),
            metadata={"fail_closed": True, "rule": "priority_7"},
        )
    
    # Priority 8: CATALOG_BINDING_READY_CANDIDATE
    # All checks passed, but runtime_allowed and phase_5_allowed remain False by invariant
    return Service1RuntimeCatalogBindingResultV1(
        pathology_code=pathology_code,
        catalog_origin=pathology_entry.get("status", "unknown"),
        formula_refs=formula_refs,
        resolved_formula_ids=tuple(resolved_formula_ids),
        missing_formula_refs=tuple(missing_formula_refs),
        required_variables=required_variables,
        resolved_variables=tuple(resolved_variables),
        missing_variables=tuple(missing_variables),
        required_evidence=required_evidence,
        minimum_semantic_bindings=minimum_semantic_bindings,
        owner_confirmation_required=owner_confirmation_required,
        readiness_status=CATALOG_BINDING_READY_CANDIDATE,
        blocking_reasons=tuple(blocking_reasons),
        metadata={"pass_through": True, "rule": "priority_8"},
    )

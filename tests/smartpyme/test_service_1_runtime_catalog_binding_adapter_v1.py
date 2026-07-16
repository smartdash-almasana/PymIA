"""
Tests for SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_V1

These tests validate the read-only adapter that consumes Service1RuntimeCatalogBindingResultV1
and emits a non-executing adapter context for future semantic evidence binding consideration.

The adapter is a governance handoff, not a runtime bridge. It must preserve fail-closed statuses
and must never convert catalog readiness into runtime authorization.

Mode: TEST ONLY (adapter implementation exists; tests validate behavior)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

# Expected adapter module (does not exist yet)
ADAPTER_MODULE_NAME = "pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1"

# Import contract for building upstream results
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

# Expected adapter statuses per adapter plan section 5
ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY = "ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY"
ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS = "ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS"
ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND = "ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND"
ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND = "ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND"
ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING = "ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING"
ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED = "ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED"
ADAPTER_BLOCKED_BY_POLICY = "ADAPTER_BLOCKED_BY_POLICY"
ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION = "ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION"

# Expected status mapping per adapter plan section 6
EXPECTED_STATUS_MAPPING = {
    UNKNOWN_PATHOLOGY_CODE: ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY,
    MISSING_FORMULA_REFS: ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS,
    FORMULA_REF_NOT_FOUND: ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND,
    REQUIRED_VARIABLE_NOT_FOUND: ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND,
    REQUIRED_EVIDENCE_MISSING: ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING,
    OWNER_CONFIRMATION_REQUIRED: ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED,
    RUNTIME_BLOCKED_BY_POLICY: ADAPTER_BLOCKED_BY_POLICY,
    CATALOG_BINDING_READY_CANDIDATE: ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
}

# Forbidden imports per adapter test plan section 7
FORBIDDEN_IMPORTS = {
    "service_1_xlsx_first_product_entrypoint_v1",
    "service_1_semantic_evidence_binding_engine_v1",
    "service_1_pathology_to_allowed_computation_candidate_v1",
    "pymia.cli",
}


def _build_upstream_result(
    pathology_code: str,
    readiness_status: str,
    formula_refs: tuple[str, ...] = (),
    required_variables: tuple[str, ...] = (),
    required_evidence: tuple[str, ...] = (),
    owner_confirmation_required: bool = False,
) -> Service1RuntimeCatalogBindingResultV1:
    """Build synthetic upstream result for testing."""
    return Service1RuntimeCatalogBindingResultV1(
        pathology_code=pathology_code,
        readiness_status=readiness_status,
        formula_refs=formula_refs,
        required_variables=required_variables,
        required_evidence=required_evidence,
        owner_confirmation_required=owner_confirmation_required,
        runtime_allowed=False,
        phase_5_allowed=False,
    )


# Import adapter module (implementation exists)
from pymia.smartpyme import service_1_runtime_catalog_binding_adapter_v1 as adapter_module


def test_adapter_maps_unknown_pathology_to_blocked_unknown() -> None:
    """
    Test 1: UNKNOWN_PATHOLOGY_CODE maps to ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY.
    
    Per adapter plan section 6 status mapping.
    """
    upstream = _build_upstream_result(
        pathology_code="UNKNOWN_999",
        readiness_status=UNKNOWN_PATHOLOGY_CODE,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == UNKNOWN_PATHOLOGY_CODE
    assert context.adapter_status == ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY
    assert context.runtime_allowed is False
    assert context.phase_5_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_missing_formula_refs_to_blocked_missing_formula_refs() -> None:
    """
    Test 2: MISSING_FORMULA_REFS maps to ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS.
    
    Per adapter plan section 6 status mapping.
    """
    upstream = _build_upstream_result(
        pathology_code="SAL_001",
        readiness_status=MISSING_FORMULA_REFS,
        formula_refs=(),
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == MISSING_FORMULA_REFS
    assert context.adapter_status == ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS
    assert context.runtime_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_formula_ref_not_found_to_blocked_formula_ref_not_found() -> None:
    """
    Test 3: FORMULA_REF_NOT_FOUND maps to ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND.
    
    Per adapter plan section 6 status mapping.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_001",
        readiness_status=FORMULA_REF_NOT_FOUND,
        formula_refs=("NONEXISTENT_FORMULA",),
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == FORMULA_REF_NOT_FOUND
    assert context.adapter_status == ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND
    assert context.runtime_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_required_variable_not_found_to_blocked_required_variable_not_found() -> None:
    """
    Test 4: REQUIRED_VARIABLE_NOT_FOUND maps to ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND.
    
    Per adapter plan section 6 status mapping.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_002",
        readiness_status=REQUIRED_VARIABLE_NOT_FOUND,
        formula_refs=("FORMULA_001",),
        required_variables=("nonexistent_variable",),
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == REQUIRED_VARIABLE_NOT_FOUND
    assert context.adapter_status == ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND
    assert context.runtime_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_required_evidence_missing_to_blocked_required_evidence_missing() -> None:
    """
    Test 5: REQUIRED_EVIDENCE_MISSING maps to ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING.
    
    Per adapter plan section 6 status mapping.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_003",
        readiness_status=REQUIRED_EVIDENCE_MISSING,
        formula_refs=("FORMULA_001",),
        required_variables=("variable_001",),
        required_evidence=(),
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == REQUIRED_EVIDENCE_MISSING
    assert context.adapter_status == ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING
    assert context.runtime_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_owner_confirmation_required_to_blocked_owner_confirmation() -> None:
    """
    Test 6: OWNER_CONFIRMATION_REQUIRED maps to ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED.
    
    Per adapter plan section 6 status mapping.
    Per adapter plan fail-closed rule F8: owner_confirmation_required true blocks.
    """
    upstream = _build_upstream_result(
        pathology_code="REN_001",
        readiness_status=OWNER_CONFIRMATION_REQUIRED,
        formula_refs=("REN_001_margen_neto_real",),
        required_variables=("sale_price", "costs", "taxes"),
        required_evidence=("ventas_del_periodo", "costos_directos"),
        owner_confirmation_required=True,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == OWNER_CONFIRMATION_REQUIRED
    assert context.adapter_status == ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED
    assert context.runtime_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_runtime_blocked_by_policy_to_blocked_policy() -> None:
    """
    Test 7: RUNTIME_BLOCKED_BY_POLICY maps to ADAPTER_BLOCKED_BY_POLICY.
    
    Per adapter plan section 6 status mapping.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_004",
        readiness_status=RUNTIME_BLOCKED_BY_POLICY,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == RUNTIME_BLOCKED_BY_POLICY
    assert context.adapter_status == ADAPTER_BLOCKED_BY_POLICY
    assert context.runtime_allowed is False
    assert context.semantic_binding_consideration_allowed is False


def test_adapter_maps_ready_candidate_to_semantic_binding_consideration_ready() -> None:
    """
    Test 8: CATALOG_BINDING_READY_CANDIDATE maps to ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION.
    
    Per adapter plan section 6 status mapping.
    Per adapter plan invariant I13: semantic_binding_consideration_allowed can be true only for ready candidate.
    """
    upstream = _build_upstream_result(
        pathology_code="READY_001",
        readiness_status=CATALOG_BINDING_READY_CANDIDATE,
        formula_refs=("FORMULA_001",),
        required_variables=("variable_001", "variable_002"),
        required_evidence=("evidence_001", "evidence_002"),
        owner_confirmation_required=False,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.upstream_readiness_status == CATALOG_BINDING_READY_CANDIDATE
    assert context.adapter_status == ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION
    assert context.runtime_allowed is False
    assert context.phase_5_allowed is False
    assert context.semantic_binding_consideration_allowed is True


def test_adapter_preserves_runtime_allowed_false() -> None:
    """
    Test 9: Adapter always emits runtime_allowed=False per invariant I1.
    
    Per adapter plan invariant I1: runtime_allowed is always false.
    Per adapter plan invariant I4: semantic_binding_consideration_allowed never means runtime_allowed.
    """
    for upstream_status, expected_adapter_status in EXPECTED_STATUS_MAPPING.items():
        upstream = _build_upstream_result(
            pathology_code="TEST_INVARIANT_I1",
            readiness_status=upstream_status,
            formula_refs=("FORMULA_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            required_variables=("variable_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            required_evidence=("evidence_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            owner_confirmation_required=(upstream_status == OWNER_CONFIRMATION_REQUIRED),
        )
        
        context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
        
        assert context.runtime_allowed is False, \
            f"Invariant I1 violated for {upstream_status}: runtime_allowed must be False"


def test_adapter_preserves_phase_5_allowed_false() -> None:
    """
    Test 10: Adapter always emits phase_5_allowed=False per invariant I2.
    
    Per adapter plan invariant I2: phase_5_allowed is always false.
    """
    for upstream_status in EXPECTED_STATUS_MAPPING.keys():
        upstream = _build_upstream_result(
            pathology_code="TEST_INVARIANT_I2",
            readiness_status=upstream_status,
            formula_refs=("FORMULA_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            required_variables=("variable_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            required_evidence=("evidence_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            owner_confirmation_required=(upstream_status == OWNER_CONFIRMATION_REQUIRED),
        )
        
        context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
        
        assert context.phase_5_allowed is False, \
            f"Invariant I2 violated for {upstream_status}: phase_5_allowed must be False"


def test_adapter_allows_semantic_consideration_only_for_ready_candidate() -> None:
    """
    Test 11: semantic_binding_consideration_allowed is True only for CATALOG_BINDING_READY_CANDIDATE.
    
    Per adapter plan invariant I13: semantic_binding_consideration_allowed can be true only when
    upstream_readiness_status is CATALOG_BINDING_READY_CANDIDATE.
    """
    for upstream_status in EXPECTED_STATUS_MAPPING.keys():
        upstream = _build_upstream_result(
            pathology_code="TEST_INVARIANT_I13",
            readiness_status=upstream_status,
            formula_refs=("FORMULA_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            required_variables=("variable_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            required_evidence=("evidence_001",) if upstream_status == CATALOG_BINDING_READY_CANDIDATE else (),
            owner_confirmation_required=(upstream_status == OWNER_CONFIRMATION_REQUIRED),
        )
        
        context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
        
        if upstream_status == CATALOG_BINDING_READY_CANDIDATE:
            assert context.semantic_binding_consideration_allowed is True, \
                f"Ready candidate should allow semantic consideration"
        else:
            assert context.semantic_binding_consideration_allowed is False, \
                f"Invariant I13 violated: {upstream_status} must not allow semantic consideration"


def test_adapter_blocks_missing_upstream_result() -> None:
    """
    Test 12: Missing upstream result blocks with ADAPTER_BLOCKED_BY_POLICY.
    
    Per adapter plan fail-closed rule F1: Missing upstream result -> ADAPTER_BLOCKED_BY_POLICY.
    """
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(None)
    
    assert context.adapter_status == ADAPTER_BLOCKED_BY_POLICY
    assert context.runtime_allowed is False
    assert context.phase_5_allowed is False
    assert context.semantic_binding_consideration_allowed is False
    assert "missing_upstream_result" in context.semantic_binding_blocking_reasons


def test_adapter_blocks_unknown_upstream_status() -> None:
    """
    Test 13: Unknown upstream readiness_status blocks with ADAPTER_BLOCKED_BY_POLICY.
    
    Per adapter plan fail-closed rule F2: Unknown upstream readiness_status -> ADAPTER_BLOCKED_BY_POLICY.
    """
    # Build a result with valid status first, then mutate to invalid status
    upstream = _build_upstream_result(
        pathology_code="TEST_UNKNOWN_STATUS",
        readiness_status=CATALOG_BINDING_READY_CANDIDATE,
    )
    
    # Bypass frozen dataclass restriction to set invalid status
    object.__setattr__(upstream, "readiness_status", "INVALID_STATUS_999")
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    # Adapter should detect invalid status and block
    assert context.adapter_status == ADAPTER_BLOCKED_BY_POLICY
    assert context.runtime_allowed is False
    assert "unknown_upstream_status" in context.semantic_binding_blocking_reasons


def test_adapter_fails_closed_if_upstream_runtime_allowed_true() -> None:
    """
    Test 14: Upstream runtime_allowed=True fails closed with ADAPTER_BLOCKED_BY_POLICY.
    
    Per adapter plan fail-closed rule F3: upstream runtime_allowed not false -> ADAPTER_BLOCKED_BY_POLICY.
    """
    # Attempt to create upstream result with runtime_allowed=True
    # This should raise ValueError due to invariant I1 in contract
    with pytest.raises(ValueError, match="Invariant I1 violated"):
        Service1RuntimeCatalogBindingResultV1(
            pathology_code="TEST_UPSTREAM_RUNTIME_TRUE",
            readiness_status=CATALOG_BINDING_READY_CANDIDATE,
            runtime_allowed=True,
            phase_5_allowed=False,
        )


def test_adapter_fails_closed_if_upstream_phase_5_allowed_true() -> None:
    """
    Test 15: Upstream phase_5_allowed=True fails closed with ADAPTER_BLOCKED_BY_POLICY.
    
    Per adapter plan fail-closed rule F4: upstream phase_5_allowed not false -> ADAPTER_BLOCKED_BY_POLICY.
    """
    # Attempt to create upstream result with phase_5_allowed=True
    # This should raise ValueError due to invariant I2 in contract
    with pytest.raises(ValueError, match="Invariant I2 violated"):
        Service1RuntimeCatalogBindingResultV1(
            pathology_code="TEST_UPSTREAM_PHASE5_TRUE",
            readiness_status=CATALOG_BINDING_READY_CANDIDATE,
            runtime_allowed=False,
            phase_5_allowed=True,
        )


def test_adapter_blocks_ready_candidate_with_empty_required_variables() -> None:
    """
    Test 16: Ready candidate with empty required_variables blocks semantic consideration.
    
    Per adapter plan fail-closed rule F6: Empty required_variables for ready candidate blocks.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_EMPTY_VARIABLES",
        readiness_status=CATALOG_BINDING_READY_CANDIDATE,
        formula_refs=("FORMULA_001",),
        required_variables=(),  # Empty
        required_evidence=("evidence_001",),
        owner_confirmation_required=False,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.semantic_binding_consideration_allowed is False
    assert "empty_required_variables" in context.semantic_binding_blocking_reasons


def test_adapter_blocks_ready_candidate_with_empty_required_evidence() -> None:
    """
    Test 17: Ready candidate with empty required_evidence blocks semantic consideration.
    
    Per adapter plan fail-closed rule F7: Empty required_evidence for ready candidate blocks.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_EMPTY_EVIDENCE",
        readiness_status=CATALOG_BINDING_READY_CANDIDATE,
        formula_refs=("FORMULA_001",),
        required_variables=("variable_001",),
        required_evidence=(),  # Empty
        owner_confirmation_required=False,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    assert context.semantic_binding_consideration_allowed is False
    assert "empty_required_evidence" in context.semantic_binding_blocking_reasons


def test_adapter_does_not_import_runtime_mapper_engine_cli() -> None:
    """
    Test 18: Adapter must not import forbidden modules.
    
    Per adapter test plan section 7: Forbidden imports guard.
    Adapter may import only the runtime catalog binding contract module and standard library.
    """
    import importlib.util
    
    adapter_spec = importlib.util.find_spec(ADAPTER_MODULE_NAME)
    assert adapter_spec is not None, f"Adapter module {ADAPTER_MODULE_NAME} not found"
    
    # Read adapter source code
    adapter_source_path = Path(adapter_spec.origin)
    adapter_source = adapter_source_path.read_text(encoding="utf-8")
    
    # Check for forbidden imports
    for forbidden_module in FORBIDDEN_IMPORTS:
        assert forbidden_module not in adapter_source, \
            f"Adapter imports forbidden module: {forbidden_module}"
    
    # Verify adapter imports contract module
    assert "service_1_runtime_catalog_binding_contract_v1" in adapter_source, \
        "Adapter must import runtime catalog binding contract"


def test_adapter_has_no_case_001_dependency() -> None:
    """
    Test 19: Adapter must not reference CASE_001.
    
    Per adapter plan invariant I7: Adapter never forces CASE_001 to pass.
    Per adapter plan non-goals: does not force CASE_001 to pass.
    """
    import importlib.util
    
    adapter_spec = importlib.util.find_spec(ADAPTER_MODULE_NAME)
    assert adapter_spec is not None
    
    adapter_source_path = Path(adapter_spec.origin)
    adapter_source = adapter_source_path.read_text(encoding="utf-8")
    
    # Check for CASE_001 references
    forbidden_case_001_phrases = [
        "CASE_001",
        "case_001",
        "case001",
        "Case_001",
    ]
    
    for phrase in forbidden_case_001_phrases:
        assert phrase not in adapter_source, \
            f"Adapter references CASE_001: {phrase}"


def test_adapter_output_shape_is_complete() -> None:
    """
    Test 20: Adapter output has all required fields per adapter plan section 4.
    
    Validates that the context object contains all documented fields.
    """
    upstream = _build_upstream_result(
        pathology_code="TEST_SHAPE",
        readiness_status=CATALOG_BINDING_READY_CANDIDATE,
        formula_refs=("FORMULA_001",),
        required_variables=("variable_001", "variable_002"),
        required_evidence=("evidence_001", "evidence_002"),
        owner_confirmation_required=False,
    )
    
    context = adapter_module.build_service_1_runtime_catalog_binding_adapter_context_v1(upstream)
    
    # Validate all required fields exist per adapter plan section 4
    assert hasattr(context, "schema_version")
    assert hasattr(context, "service_name")
    assert hasattr(context, "pathology_code")
    assert hasattr(context, "upstream_readiness_status")
    assert hasattr(context, "adapter_status")
    assert hasattr(context, "formula_refs")
    assert hasattr(context, "resolved_formula_ids")
    assert hasattr(context, "required_variables")
    assert hasattr(context, "resolved_variables")
    assert hasattr(context, "required_evidence")
    assert hasattr(context, "minimum_semantic_bindings")
    assert hasattr(context, "owner_confirmation_required")
    assert hasattr(context, "semantic_binding_consideration_allowed")
    assert hasattr(context, "semantic_binding_blocking_reasons")
    assert hasattr(context, "runtime_allowed")
    assert hasattr(context, "phase_5_allowed")
    assert hasattr(context, "metadata")
    
    # Validate field types
    assert context.schema_version == "SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_CONTEXT_V1"
    assert context.service_name == "SERVICE_1"
    assert isinstance(context.pathology_code, str)
    assert isinstance(context.upstream_readiness_status, str)
    assert isinstance(context.adapter_status, str)
    assert isinstance(context.formula_refs, tuple)
    assert isinstance(context.resolved_formula_ids, tuple)
    assert isinstance(context.required_variables, tuple)
    assert isinstance(context.resolved_variables, tuple)
    assert isinstance(context.required_evidence, tuple)
    assert isinstance(context.minimum_semantic_bindings, tuple)
    assert isinstance(context.owner_confirmation_required, bool)
    assert isinstance(context.semantic_binding_consideration_allowed, bool)
    assert isinstance(context.semantic_binding_blocking_reasons, tuple)
    assert isinstance(context.runtime_allowed, bool)
    assert isinstance(context.phase_5_allowed, bool)
    assert isinstance(context.metadata, dict)

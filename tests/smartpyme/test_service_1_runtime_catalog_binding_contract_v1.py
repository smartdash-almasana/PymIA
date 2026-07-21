"""
Tests for SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1

These tests validate the contract boundary governing:
  pathology_code -> formula_refs -> required_variables -> required_evidence -> readiness_status

This is a pure, fail-closed, non-executing contract boundary. It does not authorize
runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching,
JSON mutation, Phase 5, or product-ready claims.

Mode: TEST ONLY (documental/catalogal validation)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

# Input artifacts consumed by the contract
VARIABLE_CATALOG_PATH = REPO_ROOT / "docs/service_1_semantic_variable_catalog.v1.json"
ENRICHED_PATHOLOGY_CATALOG_PATH = REPO_ROOT / "docs/pathology_catalog.enriched.v1.json"
MATRIX_PATH = REPO_ROOT / "docs/service_1_formula_pathology_evidence_matrix.v1.json"
FORMULA_CATALOG_PATH = REPO_ROOT / "docs/formula_catalog.v1.json"

# Physical contract implementation; obsolete documentary mirrors were removed.
CONTRACT_SOURCE_PATH = (
    REPO_ROOT
    / "pymia/smartpyme/service_1_runtime_catalog_binding_contract_v1.py"
)

# Fixed scope: six-code baseline
EXPECTED_PATHOLOGY_CODES = ("REN_001", "LIQ_001", "LIQ_002", "PYME_011", "SAL_001", "STK_001", "CST_001", "CSH_001")
EXPECTED_FORMULA_REFS = {
    "REN_001": ["REN_001_margen_neto_real"],
    "LIQ_001": ["LIQ_001_vendido_cobrado"],
    "LIQ_002": ["LIQ_002_saldo_final_proyectado"],
    "PYME_011": ["PYME_011_dso"],
    "SAL_001": [],
    "STK_001": [],
    "CST_001": [],
    "CSH_001": [],
}

# Allowed readiness statuses per contract section 7
ALLOWED_READINESS_STATUSES = {
    "CATALOG_BINDING_READY_CANDIDATE",
    "MISSING_FORMULA_REFS",
    "UNKNOWN_PATHOLOGY_CODE",
    "FORMULA_REF_NOT_FOUND",
    "REQUIRED_VARIABLE_NOT_FOUND",
    "REQUIRED_EVIDENCE_MISSING",
    "OWNER_CONFIRMATION_REQUIRED",
    "RUNTIME_BLOCKED_BY_POLICY",
}


def _load_json(path: Path) -> dict:
    """Load and parse a JSON artifact file."""
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_input_artifacts_exist() -> None:
    """
    Test 1: All four input artifacts consumed by the contract must exist.
    
    The contract consumes exactly:
      - pathology_catalog.enriched.v1.json
      - formula_catalog.v1.json
      - service_1_semantic_variable_catalog.v1.json
      - service_1_formula_pathology_evidence_matrix.v1.json
    """
    assert VARIABLE_CATALOG_PATH.exists(), f"Variable catalog missing: {VARIABLE_CATALOG_PATH}"
    assert ENRICHED_PATHOLOGY_CATALOG_PATH.exists(), f"Enriched pathology catalog missing: {ENRICHED_PATHOLOGY_CATALOG_PATH}"
    assert MATRIX_PATH.exists(), f"Evidence matrix missing: {MATRIX_PATH}"
    assert FORMULA_CATALOG_PATH.exists(), f"Formula catalog missing: {FORMULA_CATALOG_PATH}"


def test_six_code_baseline_is_fixed() -> None:
    """
    Test 2: Six-code baseline is fixed per contract invariant I10.
    
    The baseline codes are: REN_001, LIQ_001, SAL_001, STK_001, CST_001, CSH_001.
    """
    enriched_catalog = _load_json(ENRICHED_PATHOLOGY_CATALOG_PATH)
    matrix = _load_json(MATRIX_PATH)
    
    enriched_codes = tuple(p["pathology_code"] for p in enriched_catalog["pathologies"])
    matrix_codes = tuple(e["pathology_code"] for e in matrix["entries"])
    
    assert enriched_codes == EXPECTED_PATHOLOGY_CODES, \
        f"Enriched catalog codes {enriched_codes} do not match baseline {EXPECTED_PATHOLOGY_CODES}"
    assert matrix_codes == EXPECTED_PATHOLOGY_CODES, \
        f"Matrix codes {matrix_codes} do not match baseline {EXPECTED_PATHOLOGY_CODES}"


def test_ren_001_formula_refs_resolve() -> None:
    """
    Test 3: REN_001 formula_refs resolve in formula_catalog.v1.json.
    
    REN_001 has formula_refs = ["REN_001_margen_neto_real"] which must exist in formula catalog.
    """
    matrix = _load_json(MATRIX_PATH)
    formula_catalog = _load_json(FORMULA_CATALOG_PATH)
    
    ren_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "REN_001")
    formula_ids = {f["formula_id"] for f in formula_catalog["formulas"]}
    
    assert ren_001_entry["formula_refs"] == ["REN_001_margen_neto_real"]
    assert "REN_001_margen_neto_real" in formula_ids, \
        "REN_001_margen_neto_real not found in formula catalog"


def test_liq_001_formula_refs_resolve() -> None:
    """
    Test 4: LIQ_001 formula_refs resolve in formula_catalog.v1.json.
    
    LIQ_001 has formula_refs = ["LIQ_001_vendido_cobrado"] which must exist in formula catalog.
    """
    matrix = _load_json(MATRIX_PATH)
    formula_catalog = _load_json(FORMULA_CATALOG_PATH)
    
    liq_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "LIQ_001")
    formula_ids = {f["formula_id"] for f in formula_catalog["formulas"]}
    
    assert liq_001_entry["formula_refs"] == ["LIQ_001_vendido_cobrado"]
    assert "LIQ_001_vendido_cobrado" in formula_ids, \
        "LIQ_001_vendido_cobrado not found in formula catalog"


def test_sal_001_missing_formula_refs_fails_closed() -> None:
    """
    Test 5: SAL_001 has empty formula_refs and must emit MISSING_FORMULA_REFS.
    
    SAL_001 exists in runtime triage but not in allowed-computation and not in JSON
    pathology catalog. It has no formula refs and no required_variables in evidence matrix.
    Contract must fail closed with MISSING_FORMULA_REFS.
    """
    matrix = _load_json(MATRIX_PATH)
    
    sal_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "SAL_001")
    
    assert sal_001_entry["formula_refs"] == [], \
        "SAL_001 must have empty formula_refs per contract invariant I5"
    assert sal_001_entry["runtime_allowed"] is False, \
        "SAL_001 runtime_allowed must be False per contract invariant I1"
    assert sal_001_entry["phase_5_allowed"] is False, \
        "SAL_001 phase_5_allowed must be False per contract invariant I2"


def test_stk_001_missing_formula_refs_fails_closed() -> None:
    """
    Test 6: STK_001 has empty formula_refs and must emit MISSING_FORMULA_REFS.
    
    STK_001 is hardcoded in runtime _PATHOLOGY_TO_COMPUTATION but has no formula refs
    in semantic baseline. Contract must not fallback to runtime hardcoding.
    """
    matrix = _load_json(MATRIX_PATH)
    
    stk_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "STK_001")
    
    assert stk_001_entry["formula_refs"] == [], \
        "STK_001 must have empty formula_refs per contract invariant I5"
    assert stk_001_entry["runtime_allowed"] is False, \
        "STK_001 runtime_allowed must be False per contract invariant I1"
    assert stk_001_entry["phase_5_allowed"] is False, \
        "STK_001 phase_5_allowed must be False per contract invariant I2"


def test_cst_001_missing_formula_refs_fails_closed() -> None:
    """
    Test 7: CST_001 has empty formula_refs and must emit MISSING_FORMULA_REFS.
    
    CST_001 has no formula refs and no required_variables in evidence matrix.
    Contract must fail closed with MISSING_FORMULA_REFS.
    """
    matrix = _load_json(MATRIX_PATH)
    
    cst_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "CST_001")
    
    assert cst_001_entry["formula_refs"] == [], \
        "CST_001 must have empty formula_refs per contract invariant I5"
    assert cst_001_entry["runtime_allowed"] is False, \
        "CST_001 runtime_allowed must be False per contract invariant I1"
    assert cst_001_entry["phase_5_allowed"] is False, \
        "CST_001 phase_5_allowed must be False per contract invariant I2"


def test_csh_001_missing_formula_refs_fails_closed() -> None:
    """
    Test 8: CSH_001 has empty formula_refs and must emit MISSING_FORMULA_REFS.
    
    CSH_001 is hardcoded in runtime _PATHOLOGY_TO_COMPUTATION but has no formula refs
    in semantic baseline. Contract must not fallback to runtime hardcoding.
    """
    matrix = _load_json(MATRIX_PATH)
    
    csh_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "CSH_001")
    
    assert csh_001_entry["formula_refs"] == [], \
        "CSH_001 must have empty formula_refs per contract invariant I5"
    assert csh_001_entry["runtime_allowed"] is False, \
        "CSH_001 runtime_allowed must be False per contract invariant I1"
    assert csh_001_entry["phase_5_allowed"] is False, \
        "CSH_001 phase_5_allowed must be False per contract invariant I2"


def test_non_empty_formula_refs_exist_in_formula_catalog() -> None:
    """
    Test 9: All non-empty formula_refs in matrix must exist in formula_catalog.v1.json.
    
    Contract invariant: never invent formula ref.
    """
    matrix = _load_json(MATRIX_PATH)
    formula_catalog = _load_json(FORMULA_CATALOG_PATH)
    
    formula_ids = {f["formula_id"] for f in formula_catalog["formulas"]}
    
    for entry in matrix["entries"]:
        for formula_ref in entry["formula_refs"]:
            assert formula_ref in formula_ids, \
                f"Formula ref {formula_ref} for {entry['pathology_code']} not found in formula catalog"


def test_required_variables_exist_in_semantic_variable_catalog() -> None:
    """
    Test 10: All required_variables in matrix must exist in service_1_semantic_variable_catalog.v1.json.
    
    Contract invariant: never invent variable.
    """
    matrix = _load_json(MATRIX_PATH)
    variable_catalog = _load_json(VARIABLE_CATALOG_PATH)
    
    variable_names = {v["variable_name"] for v in variable_catalog["variables"]}
    
    for entry in matrix["entries"]:
        for variable in entry["required_variables"]:
            assert variable in variable_names, \
                f"Required variable {variable} for {entry['pathology_code']} not found in variable catalog"


def test_runtime_and_phase_5_flags_remain_false() -> None:
    """
    Test 11: All input artifacts have runtime_allowed=false and phase_5_allowed=false.
    
    Contract invariants I1 and I2: runtime_allowed and phase_5_allowed are always false.
    """
    enriched_catalog = _load_json(ENRICHED_PATHOLOGY_CATALOG_PATH)
    matrix = _load_json(MATRIX_PATH)
    
    assert enriched_catalog["runtime_connection_allowed"] is False
    assert enriched_catalog["phase_5_allowed"] is False
    
    assert matrix["runtime_connection_allowed"] is False
    assert matrix["phase_5_allowed"] is False
    
    for entry in matrix["entries"]:
        assert entry["runtime_allowed"] is False, \
            f"{entry['pathology_code']} runtime_allowed must be False"
        assert entry["phase_5_allowed"] is False, \
            f"{entry['pathology_code']} phase_5_allowed must be False"


def test_contract_rejects_runtime_authorization_flags() -> None:
    """Test 12: the executable contract must reject authorization flags."""
    with pytest.raises(ValueError, match="runtime_allowed must be False"):
        Service1RuntimeCatalogBindingResultV1(runtime_allowed=True)

    with pytest.raises(ValueError, match="phase_5_allowed must be False"):
        Service1RuntimeCatalogBindingResultV1(phase_5_allowed=True)


def test_allowed_computation_hardcoding_not_used_as_catalog_authority() -> None:
    """
    Test 13: Contract must not use runtime _PATHOLOGY_TO_COMPUTATION as catalog authority.
    
    Contract invariant I3: No new hardcoding of pathology-to-computation mappings.
    Contract invariant I4: No expansion of _PATHOLOGY_TO_COMPUTATION to make catalog gaps disappear.
    
    STK_001 and CSH_001 are hardcoded in runtime but have empty formula_refs in catalog.
    Contract must not fallback to runtime hardcoding.
    """
    matrix = _load_json(MATRIX_PATH)
    
    # STK_001 and CSH_001 have empty formula_refs despite runtime hardcoding
    stk_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "STK_001")
    csh_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "CSH_001")
    
    assert stk_001_entry["formula_refs"] == [], \
        "STK_001 must have empty formula_refs; contract must not fallback to runtime hardcoding"
    assert csh_001_entry["formula_refs"] == [], \
        "CSH_001 must have empty formula_refs; contract must not fallback to runtime hardcoding"
    
    # SAL_001 and CST_001 also have empty formula_refs
    sal_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "SAL_001")
    cst_001_entry = next(e for e in matrix["entries"] if e["pathology_code"] == "CST_001")
    
    assert sal_001_entry["formula_refs"] == []
    assert cst_001_entry["formula_refs"] == []


def test_contract_source_has_no_case_001_or_product_ready_dependency() -> None:
    """Test 14: the contract source remains case-agnostic and non-product-ready."""
    contract_source = CONTRACT_SOURCE_PATH.read_text(encoding="utf-8").lower()

    assert "case_001" not in contract_source
    assert "product is ready" not in contract_source
    assert "ready for production" not in contract_source


# ============================================================================
# CONTRACT IMPLEMENTATION TESTS
# ============================================================================
# These tests validate the actual implementation of the contract boundary.
# They import and call the pure resolver function to verify fail-closed behavior.

from pymia.smartpyme.service_1_runtime_catalog_binding_contract_v1 import (
    Service1RuntimeCatalogBindingResultV1,
    build_service_1_runtime_catalog_binding_result_v1,
    load_service_1_runtime_catalog_binding_inputs_v1,
    CATALOG_BINDING_READY_CANDIDATE,
    MISSING_FORMULA_REFS,
    UNKNOWN_PATHOLOGY_CODE,
    FORMULA_REF_NOT_FOUND,
    REQUIRED_VARIABLE_NOT_FOUND,
    REQUIRED_EVIDENCE_MISSING,
    OWNER_CONFIRMATION_REQUIRED,
    RUNTIME_BLOCKED_BY_POLICY,
)


def test_contract_implementation_has_no_case_001_dependency() -> None:
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_runtime_catalog_binding_contract_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content


def test_contract_resolver_unknown_pathology_code() -> None:
    """
    Test: Unknown pathology code emits UNKNOWN_PATHOLOGY_CODE.
    
    Scenario: pathology_code not in enriched catalog.
    Expected: readiness_status = UNKNOWN_PATHOLOGY_CODE, runtime_allowed=False, phase_5_allowed=False.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="UNKNOWN_999",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "UNKNOWN_999"
    assert result.readiness_status == UNKNOWN_PATHOLOGY_CODE
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert "pathology_code_not_in_enriched_catalog" in result.blocking_reasons


def test_contract_resolver_sal_001_missing_formula_refs() -> None:
    """
    Test: SAL_001 emits MISSING_FORMULA_REFS (fail-closed).
    
    Scenario: SAL_001 has empty formula_refs in evidence matrix.
    Expected: readiness_status = MISSING_FORMULA_REFS, runtime_allowed=False.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="SAL_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "SAL_001"
    assert result.readiness_status == MISSING_FORMULA_REFS
    assert result.formula_refs == ()
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert "formula_refs_empty" in result.blocking_reasons


def test_contract_resolver_stk_001_missing_formula_refs() -> None:
    """
    Test: STK_001 emits MISSING_FORMULA_REFS (fail-closed).
    
    Scenario: STK_001 has empty formula_refs despite runtime hardcoding.
    Expected: readiness_status = MISSING_FORMULA_REFS, no fallback to runtime.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="STK_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "STK_001"
    assert result.readiness_status == MISSING_FORMULA_REFS
    assert result.formula_refs == ()
    assert result.runtime_allowed is False
    assert "formula_refs_empty" in result.blocking_reasons


def test_contract_resolver_cst_001_missing_formula_refs() -> None:
    """
    Test: CST_001 emits MISSING_FORMULA_REFS (fail-closed).
    
    Scenario: CST_001 has empty formula_refs.
    Expected: readiness_status = MISSING_FORMULA_REFS.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="CST_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "CST_001"
    assert result.readiness_status == MISSING_FORMULA_REFS
    assert result.formula_refs == ()
    assert result.runtime_allowed is False


def test_contract_resolver_csh_001_missing_formula_refs() -> None:
    """
    Test: CSH_001 emits MISSING_FORMULA_REFS (fail-closed).
    
    Scenario: CSH_001 has empty formula_refs despite runtime hardcoding.
    Expected: readiness_status = MISSING_FORMULA_REFS, no fallback to runtime.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="CSH_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "CSH_001"
    assert result.readiness_status == MISSING_FORMULA_REFS
    assert result.formula_refs == ()
    assert result.runtime_allowed is False


def test_contract_resolver_ren_001_owner_confirmation_required() -> None:
    """
    Test: REN_001 emits OWNER_CONFIRMATION_REQUIRED.
    
    Scenario: REN_001 has formula_refs that resolve, variables that resolve,
              evidence present, but owner_confirmation_required=true.
    Expected: readiness_status = OWNER_CONFIRMATION_REQUIRED, runtime_allowed=False.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="REN_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "REN_001"
    assert result.readiness_status == OWNER_CONFIRMATION_REQUIRED
    assert result.formula_refs == ("REN_001_margen_neto_real",)
    assert result.resolved_formula_ids == ("REN_001_margen_neto_real",)
    assert result.required_variables == ("sale_price", "costs", "taxes")
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.owner_confirmation_required is True
    assert "owner_confirmation_required_by_evidence_matrix" in result.blocking_reasons


def test_contract_resolver_liq_001_owner_confirmation_required() -> None:
    """
    Test: LIQ_001 emits OWNER_CONFIRMATION_REQUIRED.
    
    Scenario: LIQ_001 has formula_refs that resolve, variables that resolve,
              evidence present, but owner_confirmation_required=true.
    Expected: readiness_status = OWNER_CONFIRMATION_REQUIRED.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="LIQ_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    assert result.pathology_code == "LIQ_001"
    assert result.readiness_status == OWNER_CONFIRMATION_REQUIRED
    assert result.formula_refs == ("LIQ_001_vendido_cobrado",)
    assert result.resolved_formula_ids == ("LIQ_001_vendido_cobrado",)
    assert result.required_variables == ("sold_amount", "collected_amount")
    assert result.runtime_allowed is False
    assert result.owner_confirmation_required is True


def test_contract_resolver_invariants_always_false() -> None:
    """
    Test: All contract results have runtime_allowed=False and phase_5_allowed=False.
    
    Invariant I1: runtime_allowed is always false.
    Invariant I2: phase_5_allowed is always false.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    # Test all six-code baseline
    for pathology_code in EXPECTED_PATHOLOGY_CODES:
        result = build_service_1_runtime_catalog_binding_result_v1(
            pathology_code=pathology_code,
            enriched_catalog=enriched_catalog,
            formula_catalog=formula_catalog,
            variable_catalog=variable_catalog,
            evidence_matrix=evidence_matrix,
        )
        
        assert result.runtime_allowed is False, \
            f"{pathology_code} violates invariant I1: runtime_allowed must be False"
        assert result.phase_5_allowed is False, \
            f"{pathology_code} violates invariant I2: phase_5_allowed must be False"


def test_contract_resolver_fail_closed_enriched_catalog_unavailable() -> None:
    """
    Test: Fail-closed when enriched catalog is unavailable.
    
    Scenario: enriched_catalog is None.
    Expected: readiness_status = UNKNOWN_PATHOLOGY_CODE with blocking_reason "enriched_catalog_unavailable".
    """
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="REN_001",
        enriched_catalog=None,
        formula_catalog=None,
        variable_catalog=None,
        evidence_matrix=None,
    )
    
    assert result.readiness_status == UNKNOWN_PATHOLOGY_CODE
    assert result.runtime_allowed is False
    assert "enriched_catalog_unavailable" in result.blocking_reasons


def test_contract_resolver_fail_closed_evidence_matrix_unavailable() -> None:
    """
    Test: Fail-closed when evidence matrix is unavailable.
    
    Scenario: evidence_matrix is None but enriched_catalog is available.
    Expected: readiness_status = RUNTIME_BLOCKED_BY_POLICY with blocking_reason "evidence_matrix_unavailable".
    """
    enriched_catalog = _load_json(ENRICHED_PATHOLOGY_CATALOG_PATH)
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="REN_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=None,
        variable_catalog=None,
        evidence_matrix=None,
    )
    
    assert result.readiness_status == RUNTIME_BLOCKED_BY_POLICY
    assert result.runtime_allowed is False
    assert "evidence_matrix_unavailable" in result.blocking_reasons


def test_contract_resolver_output_shape_completeness() -> None:
    """
    Test: Contract output has all required fields per contract section 6.
    
    Validates that the result object contains all documented fields.
    """
    enriched_catalog, formula_catalog, variable_catalog, evidence_matrix = (
        load_service_1_runtime_catalog_binding_inputs_v1(REPO_ROOT)
    )
    
    result = build_service_1_runtime_catalog_binding_result_v1(
        pathology_code="REN_001",
        enriched_catalog=enriched_catalog,
        formula_catalog=formula_catalog,
        variable_catalog=variable_catalog,
        evidence_matrix=evidence_matrix,
    )
    
    # Validate all required fields exist
    assert hasattr(result, "schema_version")
    assert hasattr(result, "service_name")
    assert hasattr(result, "pathology_code")
    assert hasattr(result, "catalog_origin")
    assert hasattr(result, "formula_refs")
    assert hasattr(result, "resolved_formula_ids")
    assert hasattr(result, "missing_formula_refs")
    assert hasattr(result, "required_variables")
    assert hasattr(result, "resolved_variables")
    assert hasattr(result, "missing_variables")
    assert hasattr(result, "required_evidence")
    assert hasattr(result, "minimum_semantic_bindings")
    assert hasattr(result, "owner_confirmation_required")
    assert hasattr(result, "readiness_status")
    assert hasattr(result, "blocking_reasons")
    assert hasattr(result, "runtime_allowed")
    assert hasattr(result, "phase_5_allowed")
    assert hasattr(result, "metadata")
    
    # Validate field types
    assert result.schema_version == "SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1"
    assert result.service_name == "SERVICE_1"
    assert isinstance(result.formula_refs, tuple)
    assert isinstance(result.resolved_formula_ids, tuple)
    assert isinstance(result.missing_formula_refs, tuple)
    assert isinstance(result.required_variables, tuple)
    assert isinstance(result.resolved_variables, tuple)
    assert isinstance(result.missing_variables, tuple)
    assert isinstance(result.required_evidence, tuple)
    assert isinstance(result.minimum_semantic_bindings, tuple)
    assert isinstance(result.owner_confirmation_required, bool)
    assert isinstance(result.blocking_reasons, tuple)
    assert isinstance(result.runtime_allowed, bool)
    assert isinstance(result.phase_5_allowed, bool)
    assert isinstance(result.metadata, dict)

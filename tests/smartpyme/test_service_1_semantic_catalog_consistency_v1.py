from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

VARIABLE_CATALOG_PATH = REPO_ROOT / "docs/service_1_semantic_variable_catalog.v1.json"
ENRICHED_PATHOLOGY_CATALOG_PATH = REPO_ROOT / "docs/pathology_catalog.enriched.v1.json"
MATRIX_PATH = REPO_ROOT / "docs/service_1_formula_pathology_evidence_matrix.v1.json"
FORMULA_CATALOG_PATH = REPO_ROOT / "docs/formula_catalog.v1.json"
SOURCE_PATHOLOGY_CATALOG_PATH = REPO_ROOT / "docs/pathology_catalog.v1.json"

EXPECTED_PATHOLOGY_CODES = ("REN_001", "LIQ_001", "LIQ_002", "SAL_001", "STK_001", "CST_001", "CSH_001")
EXPECTED_FORMULA_REFS = {
    "REN_001": ["REN_001_margen_neto_real"],
    "LIQ_001": ["LIQ_001_vendido_cobrado"],
    "LIQ_002": ["LIQ_002_saldo_final_proyectado"],
    "SAL_001": [],
    "STK_001": [],
    "CST_001": [],
    "CSH_001": [],
}
BASELINE_ONLY_PATHOLOGY_CODES = {"SAL_001", "STK_001", "CST_001", "CSH_001"}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_required_catalog_files_exist() -> None:
    assert VARIABLE_CATALOG_PATH.exists()
    assert ENRICHED_PATHOLOGY_CATALOG_PATH.exists()
    assert MATRIX_PATH.exists()
    assert FORMULA_CATALOG_PATH.exists()


def test_variable_catalog_has_expected_shape_and_time_model() -> None:
    variable_catalog = _load_json(VARIABLE_CATALOG_PATH)
    variables = variable_catalog["variables"]
    by_name = {variable["variable_name"]: variable for variable in variables}

    assert len(variables) == 43
    assert len(by_name) == 43
    assert all(variable["required_data_type"] != "time" for variable in variables)
    assert by_name["manual_time"]["required_data_type"] == "number"
    assert by_name["automated_time"]["required_data_type"] == "number"
    assert by_name["manual_time"]["unit"] == "time"
    assert by_name["automated_time"]["unit"] == "time"


def test_enriched_pathology_catalog_is_catalog_only_for_expected_scope() -> None:
    enriched_catalog = _load_json(ENRICHED_PATHOLOGY_CATALOG_PATH)
    pathologies = enriched_catalog["pathologies"]

    assert tuple(pathology["pathology_code"] for pathology in pathologies) == EXPECTED_PATHOLOGY_CODES
    assert enriched_catalog["status"] == "CATALOG_ONLY_NOT_RUNTIME"
    assert enriched_catalog["runtime_connection_allowed"] is False
    assert enriched_catalog["phase_5_allowed"] is False
    assert all(pathology["runtime_status"] == "not_allowed" for pathology in pathologies)


def test_matrix_is_catalog_only_for_expected_scope() -> None:
    matrix = _load_json(MATRIX_PATH)
    entries = matrix["entries"]

    assert tuple(entry["pathology_code"] for entry in entries) == EXPECTED_PATHOLOGY_CODES
    assert matrix["runtime_connection_allowed"] is False
    assert matrix["phase_5_allowed"] is False

    governed_codes = {"REN_001", "LIQ_001", "LIQ_002"}
    for entry in entries:
        assert entry["runtime_allowed"] is False
        assert entry["phase_5_allowed"] is False
        if entry["pathology_code"] in governed_codes:
            assert entry["readiness_status"] == "governed_computation_candidate"
        else:
            assert entry["readiness_status"] == "not_runtime_ready"
        assert entry["owner_confirmation_required"] is True


def test_matrix_formula_refs_match_fixed_scope() -> None:
    matrix = _load_json(MATRIX_PATH)
    formula_refs_by_pathology = {
        entry["pathology_code"]: entry["formula_refs"]
        for entry in matrix["entries"]
    }

    assert formula_refs_by_pathology == EXPECTED_FORMULA_REFS


def test_non_empty_formula_refs_exist_in_formula_catalog() -> None:
    matrix = _load_json(MATRIX_PATH)
    formula_catalog = _load_json(FORMULA_CATALOG_PATH)
    formula_ids = {formula["formula_id"] for formula in formula_catalog["formulas"]}

    formula_refs = {
        formula_ref
        for entry in matrix["entries"]
        for formula_ref in entry["formula_refs"]
    }

    assert formula_refs <= formula_ids


def test_semantic_bindings_exist_in_variable_catalog() -> None:
    variable_catalog = _load_json(VARIABLE_CATALOG_PATH)
    enriched_catalog = _load_json(ENRICHED_PATHOLOGY_CATALOG_PATH)
    matrix = _load_json(MATRIX_PATH)
    variable_names = {variable["variable_name"] for variable in variable_catalog["variables"]}

    enriched_bindings = {
        binding
        for pathology in enriched_catalog["pathologies"]
        for binding in pathology["minimum_semantic_bindings"]
    }
    matrix_bindings = {
        binding
        for entry in matrix["entries"]
        for binding in entry["required_variables"] + entry["semantic_bindings"]
    }

    assert enriched_bindings <= variable_names
    assert matrix_bindings <= variable_names


def test_no_confirmed_suffix_or_uncataloged_business_period_reference() -> None:
    variable_catalog = _load_json(VARIABLE_CATALOG_PATH)
    variable_names = {variable["variable_name"] for variable in variable_catalog["variables"]}
    catalog_text = "\n".join(
        [
            ENRICHED_PATHOLOGY_CATALOG_PATH.read_text(encoding="utf-8"),
            MATRIX_PATH.read_text(encoding="utf-8"),
        ]
    )

    assert "_confirmed" not in catalog_text
    if "business_period" not in variable_names:
        assert "business_period" not in catalog_text


def test_baseline_semantic_pathologies_do_not_require_source_catalog_presence() -> None:
    source_catalog = _load_json(SOURCE_PATHOLOGY_CATALOG_PATH)
    enriched_catalog = _load_json(ENRICHED_PATHOLOGY_CATALOG_PATH)
    source_codes = {pathology["pathology_code"] for pathology in source_catalog["pathologies"]}
    enriched_codes = {pathology["pathology_code"] for pathology in enriched_catalog["pathologies"]}

    assert {"REN_001", "LIQ_001"} <= source_codes
    assert BASELINE_ONLY_PATHOLOGY_CODES <= enriched_codes

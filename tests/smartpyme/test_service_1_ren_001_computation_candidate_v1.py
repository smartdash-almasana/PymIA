from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = REPO_ROOT / "docs/service_1_formula_pathology_evidence_matrix.v1.json"
FORMULA_CATALOG_PATH = REPO_ROOT / "docs/formula_catalog.v1.json"
VARIABLE_CATALOG_PATH = REPO_ROOT / "docs/service_1_semantic_variable_catalog.v1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _matrix_entry() -> dict:
    return next(
        item
        for item in _load(MATRIX_PATH)["entries"]
        if item["pathology_code"] == "REN_001"
    )


def _formula() -> dict:
    return next(
        item
        for item in _load(FORMULA_CATALOG_PATH)["formulas"]
        if item["formula_id"] == "REN_001_margen_neto_real"
    )


def test_ren_001_candidate_matches_canonical_formula() -> None:
    entry = _matrix_entry()
    formula = _formula()

    assert formula["calculation_state"] == "CALCULABLE"
    assert formula["expression"] == "((sale_price - costs - taxes) / sale_price) * 100"
    assert formula["output_unit"] == "percentage"
    assert entry["formula_refs"] == [formula["formula_id"]]
    assert entry["required_variables"] == ["sale_price", "costs", "taxes"]
    assert entry["semantic_bindings"] == entry["required_variables"]
    assert entry["capability_refs"] == ["net_margin_real"]


def test_ren_001_required_variables_are_numeric_currency_evidence() -> None:
    catalog = _load(VARIABLE_CATALOG_PATH)
    by_name = {item["variable_name"]: item for item in catalog["variables"]}

    for variable_name in ("sale_price", "costs", "taxes"):
        assert by_name[variable_name] == {
            "variable_name": variable_name,
            "required_data_type": "number",
            "unit": "currency",
        }


def test_ren_001_computation_preconditions_are_explicit() -> None:
    entry = _matrix_entry()

    assert entry["computation_candidate_allowed"] is True
    assert entry["computation_preconditions"] == [
        "sale_price > 0",
        "costs >= 0",
        "taxes >= 0",
        "all required values are finite numeric evidence",
    ]


def test_ren_001_candidate_does_not_open_runtime_or_diagnosis_authority() -> None:
    matrix = _load(MATRIX_PATH)
    entry = _matrix_entry()

    assert matrix["status"] == "GOVERNED_COMPUTATION_PLANNING_ONLY"
    assert matrix["runtime_connection_allowed"] is False
    assert matrix["phase_5_allowed"] is False
    assert entry["runtime_allowed"] is False
    assert entry["phase_5_allowed"] is False
    assert entry["readiness_status"] == "governed_computation_candidate"
    assert entry["owner_confirmation_required"] is True

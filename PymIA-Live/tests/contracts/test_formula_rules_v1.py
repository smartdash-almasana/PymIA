from __future__ import annotations

import json
from pathlib import Path
from pymia.contracts.formula_contract import SUPPORTED_FORMULAS
from pymia.contracts.formula_rules_v1 import load_formula_rules


def test_formula_rules_v1_loads_valid_json():
    rules_data = load_formula_rules()
    assert isinstance(rules_data, dict)
    assert rules_data.get("schema_version") == "1.0"
    assert "rules_by_formula" in rules_data
    assert isinstance(rules_data["rules_by_formula"], dict)
    assert len(rules_data["rules_by_formula"]) > 0


def test_formula_rules_cover_supported_formulas():
    rules_data = load_formula_rules()
    rules_by_formula = rules_data["rules_by_formula"]
    for formula_id in SUPPORTED_FORMULAS:
        assert formula_id in rules_by_formula


def test_formula_rules_required_inputs_match_supported_formulas():
    rules_data = load_formula_rules()
    rules_by_formula = rules_data["rules_by_formula"]
    for formula_id in SUPPORTED_FORMULAS:
        rule = rules_by_formula[formula_id]
        assert set(rule["required_inputs"]) == set(SUPPORTED_FORMULAS[formula_id].required_inputs)


def test_formula_rules_have_expression():
    rules_data = load_formula_rules()
    rules_by_formula = rules_data["rules_by_formula"]
    for formula_id in SUPPORTED_FORMULAS:
        rule = rules_by_formula[formula_id]
        assert "expression" in rule
        assert isinstance(rule["expression"], str)
        assert len(rule["expression"].strip()) > 0


def test_formula_rules_have_blocking_metadata_for_known_divisions():
    rules_data = load_formula_rules()
    rules_by_formula = rules_data["rules_by_formula"]

    known_divisions = {
        "margen_bruto": "ventas",
        "REN_001_margen_neto_real": "sale_price",
        "INV_002_rotacion_stock": "average_stock",
        "PYME_011_dso": "sales",
        "PYME_024_liquidez_corriente": "current_liabilities",
        "PYME_017_pricing_drift": "market_price",
        "punto_equilibrio_ventas": "contribution_margin_rate",
        "PYME_027_intereses_ebitda": "ebitda",
        "PYME_033_concentracion_sku": "total_sales",
        "REN_002_coeficiente_reposicion": "origin_index",
    }

    for formula_id, divisor in known_divisions.items():
        rule = rules_by_formula[formula_id]
        blocking_rules = rule.get("blocking_rules", [])
        # Find a blocking rule that checks for equal to 0 on divisor
        matched = False
        for br in blocking_rules:
            if br.get("field") == divisor and br.get("operator") == "eq" and br.get("value") == 0:
                assert br.get("blocking_reason") == f"DIVISION_BY_ZERO: {divisor}"
                matched = True
                break
        assert matched, f"Missing DIVISION_BY_ZERO rule for {formula_id} on divisor field {divisor}"


def test_formula_rules_do_not_include_unimplemented_catalog_formulas():
    # Read docs/formula_catalog.v1.json
    catalog_path = Path(__file__).resolve().parents[2] / "docs" / "formula_catalog.v1.json"
    assert catalog_path.exists()
    catalog_data = json.loads(catalog_path.read_text(encoding="utf-8"))

    catalog_formula_ids = [f["formula_id"] for f in catalog_data.get("formulas", [])]

    rules_data = load_formula_rules()
    rules_by_formula = rules_data["rules_by_formula"]

    # Fórmulas in catalog but not in supported engine must not be in rules
    unimplemented_expected = [
        "OPE_001_decisiones_centralizadas",
        "PYME_004_recpam_basico",
        "PYME_047_tiempo_manual_automatizado",
        "M05_roi_automatizacion",
    ]

    for fid in unimplemented_expected:
        assert fid in catalog_formula_ids, f"Expected {fid} to be in the catalog JSON"
        assert fid not in SUPPORTED_FORMULAS
        assert fid not in rules_by_formula


def test_formula_rules_mark_engine_only_formulas():
    rules_data = load_formula_rules()
    rules_by_formula = rules_data["rules_by_formula"]

    engine_only = ["margen_bruto", "ganancia_bruta", "punto_equilibrio_ventas"]
    for fid in engine_only:
        assert fid in rules_by_formula
        rule = rules_by_formula[fid]
        assert rule.get("source_catalog_ref") is None
        assert rule.get("source_status") == "ENGINE_IMPLEMENTED_NOT_IN_JSON_CATALOG"

from __future__ import annotations

import inspect
import json
from pathlib import Path

from pymia.contracts.formula_contract import FormulaInput, SUPPORTED_FORMULAS
from pymia.contracts.formula_rules_v1 import load_formula_rules
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme import service_1_capability_contracts_v1 as contracts
from pymia.smartpyme import service_1_capability_registry_v1 as registry
from pymia.smartpyme import service_1_computability_v1 as computability


ROOT = Path(__file__).resolve().parents[2]


def _rules() -> dict[str, dict[str, object]]:
    payload = load_formula_rules()
    assert payload["authority"] == "CANONICAL_PRODUCTIVE_FORMULA_SPEC"
    return payload["rules_by_formula"]


def test_canonical_rules_are_the_only_supported_formula_definitions() -> None:
    rules = _rules()
    assert set(SUPPORTED_FORMULAS) == set(rules)
    assert all(str(rule.get("formula_version") or "").strip() for rule in rules.values())
    assert all(definition.formula_version for definition in SUPPORTED_FORMULAS.values())


def test_formula_catalog_is_reference_only_and_has_zero_canonical_drift() -> None:
    rules = _rules()
    catalog = json.loads((ROOT / "docs" / "formula_catalog.v1.json").read_text(encoding="utf-8"))
    by_id = {entry["formula_id"]: entry for entry in catalog["formulas"]}
    for formula_id, rule in rules.items():
        if rule.get("source_status") != "CATALOG_MATCH":
            continue
        entry = by_id[formula_id]
        assert rule["source_catalog_ref"] == formula_id
        assert rule["pathology_code"] == entry["pathology_code"]
        assert rule["expression"] == entry["expression"]
        assert rule["required_inputs"] == entry["required_variables"]
        assert rule["output_unit"] == entry["output_unit"]


def test_evidence_matrix_formula_refs_have_zero_rule_drift() -> None:
    matrix = json.loads((ROOT / "docs" / "service_1_formula_pathology_evidence_matrix.v2.json").read_text(encoding="utf-8"))
    assert computability._validate_matrix_against_formula_rules(matrix) is None


def test_registry_is_formula_ref_only_and_has_no_ast_contract() -> None:
    registry_source = inspect.getsource(registry)
    contract_source = inspect.getsource(contracts)
    assert "FormulaNodeV1" not in registry_source
    assert "formula=" not in registry_source
    assert "FormulaNodeV1" not in contract_source
    assert not hasattr(FormulaEngineService, "evaluate_ast")


def test_dpo_prerequisite_is_canonical_and_engine_executable() -> None:
    rule = _rules()["PYME_013_PREREQUISITE_dpo"]
    assert rule["required_inputs"] == ["accounts_payable", "purchases", "days"]
    assert rule["expression"] == "(accounts_payable / purchases) * days"
    result = FormulaEngineService().calculate(
        "PYME_013_PREREQUISITE_dpo",
        [
            FormulaInput(name="accounts_payable", value=500),
            FormulaInput(name="purchases", value=1000),
            FormulaInput(name="days", value=30),
        ],
    )
    assert result.status == "OK"
    assert result.value == 15.0


def test_pyme_013_and_pyme_026_registry_drift_is_closed() -> None:
    dpo = registry.get_capability_definition_v1("dpo")
    composite = registry.get_capability_definition_v1("payment_collection_gap")
    cash_flow = registry.get_capability_definition_v1("adjusted_operating_cash_flow")
    assert dpo is not None and dpo.formula_ref == "PYME_013_PREREQUISITE_dpo"
    assert composite is not None and composite.formula_ref == "PYME_013_dso_dpo_gap"
    assert tuple(variable.name for variable in composite.variables) == ("dso", "dpo")
    assert tuple(variable.source_result_key for variable in composite.variables) == ("dso_days", "dpo_days")
    assert cash_flow is not None and cash_flow.formula_ref == "PYME_026_flujo_operativo"


def test_p8_composite_projection_uses_canonical_expression_and_variables() -> None:
    governed = computability.build_service_1_composite_governed_computation_input_v1(
        case_id="case_f2",
        capability_ref="payment_collection_gap",
    )
    rule = _rules()["PYME_013_dso_dpo_gap"]
    assert governed.formula_expression == rule["expression"]
    assert governed.required_variables == tuple(rule["required_inputs"])

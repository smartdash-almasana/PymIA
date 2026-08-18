from __future__ import annotations

import inspect

import pymia.smartpyme.service_1_generic_capability_engine_v1 as generic_engine
import pymia.smartpyme.service_1_liq_001_evaluator_v1 as liq_001
import pymia.smartpyme.service_1_ren_001_evaluator_v1 as ren_001
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_generic_capability_engine_v1 import execute_generic_capability_v1


def _dso_governed_input() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1",
        "case_id": "case_f1",
        "requested_capability": "dso",
        "pathology_code": "PYME_011",
        "formula_id": "PYME_011_dso",
        "required_variables": ["accounts_receivable", "sales", "days"],
        "source_bindings": {"accounts_receivable": "receivables", "sales": "sales", "days": "days"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _dso_tables() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    return (
        [{"sheet_name": "sheet1", "rows": [{"receivables": 40, "sales": 100, "days": 30}]}],
        [
            {"sheet_name": "sheet1", "column_name": "receivables", "normalized_column_name": "receivables"},
            {"sheet_name": "sheet1", "column_name": "sales", "normalized_column_name": "sales"},
            {"sheet_name": "sheet1", "column_name": "days", "normalized_column_name": "days"},
        ],
    )


def test_formula_engine_has_no_separate_ast_facade() -> None:
    assert not hasattr(FormulaEngineService, "evaluate_ast")


def test_generic_capability_delegates_formula_math_to_formula_engine(monkeypatch) -> None:
    calls: list[tuple[str, list[object]]] = []
    original = generic_engine.calculate_formula

    def spy(formula_id, inputs):
        calls.append((formula_id, list(inputs)))
        return original(formula_id, inputs)

    monkeypatch.setattr(generic_engine, "calculate_formula", spy)
    tables, refs = _dso_tables()
    result = execute_generic_capability_v1(
        capability_ref="dso",
        computation_plan=None,
        governed_computation_input=_dso_governed_input(),
        normalized_tables=tables,
        column_refs=refs,
    )

    assert result["status"] == "EVALUATED"
    assert result["computed"]["dso_days"] == 12.0
    assert calls and calls[0][0] == "PYME_011_dso"
    assert not hasattr(generic_engine, "_evaluate_formula")


def test_liq_001_delegates_gap_to_formula_engine(monkeypatch) -> None:
    calls: list[tuple[str, list[object]]] = []
    original = liq_001.calculate_formula

    def spy(formula_id, inputs):
        calls.append((formula_id, list(inputs)))
        return original(formula_id, inputs)

    monkeypatch.setattr(liq_001, "calculate_formula", spy)
    result = liq_001.evaluate_liq_001_v1(sold_amount=1000, collected_amount=700)

    assert result["status"] == "EVALUATED"
    assert result["computed"]["gap_amount"] == 300.0
    assert calls and calls[0][0] == liq_001.FORMULA_REF


def test_liq_001_equivalence_cases_preserve_before_after_outputs() -> None:
    expected = {
        (1000, 700): (300.0, "SALES_PENDING_COLLECTION"),
        (1000, 1000): (0.0, "NO_GAP"),
        (1000, 1200): (-200.0, "COLLECTIONS_EXCEED_PERIOD_SALES"),
        (0, 0): (0.0, "NO_ACTIVITY"),
        (0, 250): (-250.0, "COLLECTIONS_WITHOUT_PERIOD_SALES"),
    }

    for (sold, collected), (gap, classification) in expected.items():
        result = liq_001.evaluate_liq_001_v1(sold_amount=sold, collected_amount=collected)
        assert result["computed"]["gap_amount"] == gap
        assert result["classification"] == classification


def test_ren_001_remains_delegated_and_generic_has_no_math_runtime() -> None:
    source = inspect.getsource(ren_001.evaluate_ren_001_v1)
    assert "calculate_formula(" in source
    assert not hasattr(generic_engine, "_evaluate_formula")

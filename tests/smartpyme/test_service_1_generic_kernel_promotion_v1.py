from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import list_capability_refs_v1
from pymia.smartpyme.service_1_generic_capability_engine_v1 import execute_generic_capability_v1
from pymia.smartpyme.service_1_liq_002_evaluator_v1 import evaluate_liq_002_v1
from pymia.smartpyme.service_1_liq_002_normalized_evidence_v1 import evaluate_liq_002_from_normalized_tables_v1
from pymia.smartpyme.service_1_liq_002_outcome_v1 import STATUS_READY as LIQ_002_OUTCOME_READY, build_liq_002_outcome_v1
from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import evaluate_pyme_011_v1
from pymia.smartpyme.service_1_pyme_011_normalized_evidence_v1 import evaluate_pyme_011_from_normalized_tables_v1
from pymia.smartpyme.service_1_pyme_011_outcome_v1 import STATUS_READY as PYME_011_OUTCOME_READY, build_pyme_011_outcome_v1
from tests.smartpyme.service_1_p8_test_support import computable_decision_from_legacy_fixture


def _plan(capability: str) -> dict[str, object]:
    base = {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    if capability == "projected_closing_cash_balance":
        base["requested_capability"] = "projected_closing_cash_balance"
        base["pathology_code"] = "LIQ_002"
        base["formula_id"] = "LIQ_002_saldo_final_proyectado"
        base["required_variables"] = ["initial_balance", "expected_collections", "expected_payments"]
        base["source_bindings"] = {
            "initial_balance": "saldo",
            "expected_collections": "cobros",
            "expected_payments": "pagos",
        }
    else:
        base["requested_capability"] = "dso"
        base["pathology_code"] = "PYME_011"
        base["formula_id"] = "PYME_011_dso"
        base["required_variables"] = ["accounts_receivable", "sales", "days"]
        base["source_bindings"] = {
            "accounts_receivable": "ctas_cobrar",
            "sales": "ventas",
            "days": "dias",
        }
    base["governed_computation_input"] = {
        "schema_version": "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1",
        "case_id": "case_generic_kernel_promotion",
        "requested_capability": base["requested_capability"],
        "family_id": "TEST_FAMILY",
        "pathology_code": base["pathology_code"],
        "formula_id": base["formula_id"],
        "formula_expression": "fixture_expression",
        "required_variables": list(base["required_variables"]),
        "required_evidence": [],
        "source_bindings": dict(base["source_bindings"]),
        "grain": {"structural_scope": "REGION", "business_entity_grain": "NONE", "temporal_grain": "NONE", "aggregation_grain": "ATOMIC"},
        "catalog_versions": {},
        "provenance": {"source": "TEST_P8"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    return base


def _decision(capability: str):
    return computable_decision_from_legacy_fixture(_plan(capability))


def _liq_tables() -> tuple[list[dict], list[dict]]:
    tables = [{"sheet_name": "sheet1", "rows": [{"saldo": 100, "cobros": 50, "pagos": 30}]}]
    refs = [
        {"sheet_name": "sheet1", "column_name": "saldo", "normalized_column_name": "saldo"},
        {"sheet_name": "sheet1", "column_name": "cobros", "normalized_column_name": "cobros"},
        {"sheet_name": "sheet1", "column_name": "pagos", "normalized_column_name": "pagos"},
    ]
    return tables, refs


def _pyme_tables() -> tuple[list[dict], list[dict]]:
    tables = [{"sheet_name": "sheet1", "rows": [{"ctas_cobrar": 600, "ventas": 400, "dias": 30}]}]
    refs = [
        {"sheet_name": "sheet1", "column_name": "ctas_cobrar", "normalized_column_name": "ctas_cobrar"},
        {"sheet_name": "sheet1", "column_name": "ventas", "normalized_column_name": "ventas"},
        {"sheet_name": "sheet1", "column_name": "dias", "normalized_column_name": "dias"},
    ]
    return tables, refs


def _confirmed() -> dict:
    return {"status": product.STATUS_CONFIRMED_BINDINGS, "schema_version": "TEST", "service_name": "SERVICE_1"}






def test_legacy_adapters_are_not_root_imports() -> None:
    import pymia.smartpyme.service_1_product_pipeline_v1 as mod
    source = mod.__file__ or ""
    content = open(source, encoding="utf-8").read()
    assert "evaluate_liq_002_from_normalized_tables_v1" not in content
    assert "evaluate_pyme_011_from_normalized_tables_v1" not in content
    assert "build_liq_002_outcome_v1" not in content
    assert "build_pyme_011_outcome_v1" not in content












def test_legacy_modules_remain_importable() -> None:
    assert evaluate_liq_002_v1(initial_balance=100, expected_collections=50, expected_payments=30)["status"] == "EVALUATED"
    tables = [{"sheet_name": "s", "rows": [{"saldo": 100, "cobros": 50, "pagos": 30}]}]
    refs = [{"sheet_name": "s", "column_name": "saldo", "normalized_column_name": "saldo"},
            {"sheet_name": "s", "column_name": "cobros", "normalized_column_name": "cobros"},
            {"sheet_name": "s", "column_name": "pagos", "normalized_column_name": "pagos"}]
    ev = evaluate_liq_002_from_normalized_tables_v1(computation_plan=_plan("projected_closing_cash_balance"), normalized_tables=tables, column_refs=refs)
    outcome = build_liq_002_outcome_v1(computation_result=ev)
    assert outcome["status"] == LIQ_002_OUTCOME_READY
    assert evaluate_pyme_011_v1(accounts_receivable=100, sales=50, days=30)["status"] == "EVALUATED"
    pt = [{"sheet_name": "s", "rows": [{"ctas_cobrar": 600, "ventas": 400, "dias": 30}]}]
    pref = [{"sheet_name": "s", "column_name": "ctas_cobrar", "normalized_column_name": "ctas_cobrar"},
            {"sheet_name": "s", "column_name": "ventas", "normalized_column_name": "ventas"},
            {"sheet_name": "s", "column_name": "dias", "normalized_column_name": "dias"}]
    pv = evaluate_pyme_011_from_normalized_tables_v1(computation_plan=_plan("dso"), normalized_tables=pt, column_refs=pref)
    poutcome = build_pyme_011_outcome_v1(computation_result=pv)
    assert poutcome["status"] == PYME_011_OUTCOME_READY


def test_product_root_no_longer_exposes_legacy_plan_builder() -> None:
    assert not hasattr(product, "build_computation_plan")




def test_root_unchanged_for_liq_001_and_ren_001(monkeypatch, tmp_path) -> None:
    import pymia.smartpyme.service_1_product_pipeline_v1 as mod
    source = mod.__file__ or ""
    content = open(source, encoding="utf-8").read()
    assert "evaluate_liq_001_from_normalized_tables_v1" in content
    assert "LIQ_001_OUTCOME_READY" in content
    assert "evaluate_ren_001_from_normalized_tables_v1" in content
    assert "REN_001_OUTCOME_READY" in content


def test_registry_contains_dpo_dso_and_projected_closing() -> None:
    refs = list_capability_refs_v1()
    assert "dpo" in refs
    assert "dso" in refs
    assert "projected_closing_cash_balance" in refs


def test_no_pyme_013_in_registry() -> None:
    refs = list_capability_refs_v1()
    assert "pyme_013" not in refs
    assert "PYME_013" not in str(refs)

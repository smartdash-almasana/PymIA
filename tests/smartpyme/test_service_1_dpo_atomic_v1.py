from __future__ import annotations

from decimal import Decimal

from pymia.smartpyme.service_1_capability_registry_v1 import DPO, list_capability_refs_v1
from pymia.smartpyme.service_1_capability_contracts_v1 import ClassificationRuleV1, FormulaNodeV1, OutcomePolicyV1, VariableRequirementV1
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    execute_generic_capability_v1,
)
from tests.smartpyme.service_1_p8_test_support import computable_decision_from_governed_payload

_ENGINE_SCHEMA = "SERVICE_1_GENERIC_CAPABILITY_ENGINE_V1"


def _assert_closed(outcome: dict) -> None:
    assert outcome.get("bounded_finding_generated") is True
    assert outcome.get("causal_diagnosis_generated") is False
    assert outcome.get("runtime_authorized") is False
    assert outcome.get("delivery_authorized") is False


def _plan(
    accounts_payable_source: str = "ctas_pagar",
    purchases_source: str = "compras",
    days_source: str = "dias",
    **overrides: object,
) -> dict[str, object]:
    base = {
        "schema_version": "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1",
        "case_id": "case_dpo_atomic",
        "requested_capability": "dpo",
        "family_id": "TEST_FAMILY",
        "pathology_code": "PYME_013_PREREQUISITE_DPO",
        "formula_id": "PYME_013_PREREQUISITE_dpo",
        "formula_expression": "accounts_payable / purchases * days",
        "required_variables": ["accounts_payable", "purchases", "days"],
        "required_evidence": [],
        "source_bindings": {
            "accounts_payable": accounts_payable_source,
            "purchases": purchases_source,
            "days": days_source,
        },
        "grain": {"structural_scope": "REGION", "business_entity_grain": "NONE", "temporal_grain": "PERIOD", "aggregation_grain": "ATOMIC"},
        "catalog_versions": {},
        "provenance": {"source": "TEST_P8_FIXTURE"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    base.update(overrides)
    return base


def _tables(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"sheet_name": "data", "rows": rows}]


def _refs(*columns: str) -> list[dict[str, str]]:
    return [{"sheet_name": "data", "column_name": c, "normalized_column_name": c} for c in columns]


def test_dpo_registry_contains_explicit_capabilities() -> None:
    refs = list_capability_refs_v1()
    assert "dpo" in refs
    assert "dso" in refs
    assert "projected_closing_cash_balance" in refs


def test_dpo_below_period() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "DPO_BELOW_PERIOD"
    assert result["computed"]["dpo_days"] == 15.0


def test_dpo_equals_period() -> None:
    tables = _tables([{"ctas_pagar": 100, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "DPO_EQUALS_PERIOD"
    assert result["computed"]["dpo_days"] == 30.0


def test_dpo_above_period() -> None:
    tables = _tables([{"ctas_pagar": 150, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "DPO_ABOVE_PERIOD"
    assert result["computed"]["dpo_days"] == 45.0


def test_dpo_sums_accounts_payable() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 200, "dias": 30}, {"ctas_pagar": 70, "compras": 0, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["inputs"]["accounts_payable"] == 120.0


def test_dpo_sums_purchases() -> None:
    tables = _tables([{"ctas_pagar": 0, "compras": 200, "dias": 30}, {"ctas_pagar": 0, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["inputs"]["purchases"] == 300.0


def test_dpo_single_value_consistent_days() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}, {"ctas_pagar": 70, "compras": 50, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_EVALUATED
    assert result["computed"]["dpo_days"] == (120 / 150) * 30


def test_dpo_blocks_inconsistent_days() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}, {"ctas_pagar": 70, "compras": 50, "dias": 60}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED
    assert any("consistent" in e for e in result["errors"])


def test_dpo_blocks_zero_purchases() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 0, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED


def test_dpo_blocks_negative_purchases() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": -5, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED


def test_dpo_blocks_negative_accounts_payable() -> None:
    tables = _tables([{"ctas_pagar": -1, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED


def test_dpo_blocks_zero_days() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 0}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED


def test_dpo_blocks_absent_flag() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    plan = _plan()
    del plan["delivery_authorized"]
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=plan, normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED


def test_dpo_blocks_true_flag() -> None:
    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    plan = _plan(delivery_authorized=True)
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=plan, normalized_tables=tables, column_refs=refs)
    assert result["status"] == STATUS_BLOCKED


def test_dpo_typed_result() -> None:
    tables = _tables([{"ctas_pagar": 100, "compras": 200, "dias": 60}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    typed = result["computed"]["typed_result"]
    assert typed["value"] == 30.0
    assert typed["unit"] == "days"
    assert typed["period"] == 60.0
    assert typed["provenance"] == "owner_confirmed_normalized_evidence"


def test_dpo_outcome_invariants() -> None:
    tables = _tables([{"ctas_pagar": 100, "compras": 200, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")
    result = execute_generic_capability_v1(capability_ref="dpo", computation_plan=None, governed_computation_input=_plan(), normalized_tables=tables, column_refs=refs)
    outcome = result["outcome"]
    assert outcome["status"] == "OUTCOME_READY"
    assert outcome["capability_ref"] == "dpo"
    assert outcome["classification"] == "DPO_BELOW_PERIOD"
    assert outcome["bounded_finding_generated"] is True
    assert outcome["causal_diagnosis_generated"] is False
    assert outcome["runtime_authorized"] is False
    assert outcome["delivery_authorized"] is False
    assert "inputs_used" in outcome
    assert "computed_results" in outcome
    _assert_closed(outcome)


def test_root_executes_dpo_once(monkeypatch, tmp_path) -> None:
    from pymia.smartpyme import service_1_product_pipeline_v1 as product
    from pymia.smartpyme.service_1_generic_capability_engine_v1 import execute_generic_capability_v1 as real_engine

    calls = []

    def tracking(*, capability_ref, governed_computation_input, normalized_tables, column_refs, governed_results=None):
        calls.append(capability_ref)
        return real_engine(capability_ref=capability_ref, computation_plan=None, governed_computation_input=governed_computation_input, normalized_tables=normalized_tables, column_refs=column_refs, governed_results=governed_results)

    monkeypatch.setattr(product, "execute_generic_capability_v1", tracking)
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: {"status": product.STATUS_CONFIRMED_BINDINGS, "schema_version": "TEST", "service_name": "SERVICE_1"})

    plan = _plan()
    monkeypatch.setattr(
        product,
        "build_computability_decision_from_confirmed_bindings_v1",
        lambda **_: computable_decision_from_governed_payload(plan),
    )

    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")

    product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dpo",
    )
    assert len(calls) == 1
    assert calls[0] == "dpo"


def test_root_does_not_execute_dso_or_pyme_013_implicitly(monkeypatch, tmp_path) -> None:
    from pymia.smartpyme import service_1_product_pipeline_v1 as product
    from pymia.smartpyme.service_1_generic_capability_engine_v1 import execute_generic_capability_v1 as real_engine

    calls = []

    def tracking(*, capability_ref, governed_computation_input, normalized_tables, column_refs, governed_results=None):
        calls.append(capability_ref)
        return real_engine(capability_ref=capability_ref, computation_plan=None, governed_computation_input=governed_computation_input, normalized_tables=normalized_tables, column_refs=column_refs, governed_results=governed_results)

    monkeypatch.setattr(product, "execute_generic_capability_v1", tracking)
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: {"status": product.STATUS_CONFIRMED_BINDINGS, "schema_version": "TEST", "service_name": "SERVICE_1"})
    monkeypatch.setattr(
        product,
        "build_computability_decision_from_confirmed_bindings_v1",
        lambda **_: computable_decision_from_governed_payload(_plan()),
    )

    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dpo",
    )
    assert result["computation_executed"] is True
    assert result["computation_result"]["capability_ref"] == "dpo"
    called = [c for c in calls]
    assert called == ["dpo"]


def test_root_blocks_dpo_delivery(monkeypatch, tmp_path) -> None:
    from pymia.smartpyme import service_1_product_pipeline_v1 as product

    monkeypatch.setattr(product, "run_initial_pass", lambda **_: {"status": product.STATUS_CONFIRMED_BINDINGS, "schema_version": "TEST", "service_name": "SERVICE_1"})
    monkeypatch.setattr(
        product,
        "build_computability_decision_from_confirmed_bindings_v1",
        lambda **_: computable_decision_from_governed_payload(_plan()),
    )

    tables = _tables([{"ctas_pagar": 50, "compras": 100, "dias": 30}])
    refs = _refs("ctas_pagar", "compras", "dias")

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dpo",
        deliver_result=True,
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "DPO_DELIVERY_NOT_AUTHORIZED"
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False


def test_dpo_remains_an_explicit_atomic_capability() -> None:
    refs = list_capability_refs_v1()
    assert "dpo" in refs
    from pymia.smartpyme import service_1_product_pipeline_v1 as product
    source = open(product.__file__ or "", encoding="utf-8").read()
    assert "DPO_CAPABILITY_REF" not in source

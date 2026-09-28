from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import (
    get_capability_definition_v1,
    list_capability_refs_v1,
)
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    execute_generic_capability_v1,
)
from tests.smartpyme.service_1_p8_test_support import (
    computable_decision_from_governed_payload,
    governed_payload_from_legacy_plan,
)


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "adjusted_operating_cash_flow",
        "pathology_code": "PYME_026",
        "formula_id": "PYME_026_flujo_operativo",
        "required_variables": [
            "net_income",
            "depreciation",
            "amortization",
            "working_capital_change",
        ],
        "source_bindings": {
            "net_income": "net_income",
            "depreciation": "depreciation",
            "amortization": "amortization",
            "working_capital_change": "working_capital_change",
        },
        "working_capital_sign_convention": (
            "positive means working-capital increase; negative means working-capital release"
        ),
        "comparability_required": "two comparable periods",
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _refs() -> list[dict[str, str]]:
    return [
        {"sheet_name": "cash_flow", "column_name": name, "normalized_column_name": name}
        for name in (
            "net_income",
            "depreciation",
            "amortization",
            "working_capital_change",
        )
    ]


def _tables(
    *,
    net_income: object = 100,
    depreciation: object = 20,
    amortization: object = 10,
    working_capital_change: object = 30,
) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "cash_flow",
            "rows": [
                {
                    "net_income": net_income,
                    "depreciation": depreciation,
                    "amortization": amortization,
                    "working_capital_change": working_capital_change,
                }
            ],
        }
    ]


def _execute(
    *,
    net_income: object = 100,
    depreciation: object = 20,
    amortization: object = 10,
    working_capital_change: object = 30,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="adjusted_operating_cash_flow",
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(plan or _plan()),
        normalized_tables=_tables(
            net_income=net_income,
            depreciation=depreciation,
            amortization=amortization,
            working_capital_change=working_capital_change,
        ),
        column_refs=_refs(),
    )


def test_pyme_026_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("adjusted_operating_cash_flow")

    assert definition is not None
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "PYME_026"
    assert definition.formula_ref == "PYME_026_flujo_operativo"
    assert definition.result_key == "adjusted_operating_cash_flow_value"
    assert definition.result_unit == "currency"
    assert tuple(variable.name for variable in definition.variables) == (
        "net_income",
        "depreciation",
        "amortization",
        "working_capital_change",
    )
    assert "adjusted_operating_cash_flow" in list_capability_refs_v1()


def test_pyme_026_calculates_adjusted_operating_cash_flow() -> None:
    result = _execute(
        net_income=100,
        depreciation=20,
        amortization=10,
        working_capital_change=30,
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "POSITIVE_ADJUSTED_OPERATING_CASH_FLOW"
    assert result["computed"]["adjusted_operating_cash_flow_value"] == 100.0


def test_pyme_026_accepts_negative_net_income() -> None:
    result = _execute(
        net_income=-100,
        depreciation=20,
        amortization=10,
        working_capital_change=0,
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "NEGATIVE_ADJUSTED_OPERATING_CASH_FLOW"
    assert result["computed"]["adjusted_operating_cash_flow_value"] == -70.0


def test_pyme_026_applies_signed_working_capital_convention() -> None:
    increase = _execute(working_capital_change=30)
    release = _execute(working_capital_change=-30)

    assert increase["computed"]["adjusted_operating_cash_flow_value"] == 100.0
    assert release["computed"]["adjusted_operating_cash_flow_value"] == 160.0


def test_pyme_026_classifies_zero_result() -> None:
    result = _execute(
        net_income=-30,
        depreciation=20,
        amortization=10,
        working_capital_change=0,
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "ZERO_ADJUSTED_OPERATING_CASH_FLOW"
    assert result["computed"]["adjusted_operating_cash_flow_value"] == 0.0


def test_pyme_026_blocks_negative_depreciation_or_amortization() -> None:
    negative_depreciation = _execute(depreciation=-1)
    negative_amortization = _execute(amortization=-1)

    assert negative_depreciation["status"] == STATUS_BLOCKED
    assert negative_amortization["status"] == STATUS_BLOCKED


def test_pyme_026_blocks_non_finite_values() -> None:
    result = _execute(working_capital_change="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_pyme_026_requires_single_consistent_values() -> None:
    tables = _tables()
    tables[0]["rows"].append(
        {
            "net_income": 101,
            "depreciation": 20,
            "amortization": 10,
            "working_capital_change": 30,
        }
    )

    result = execute_generic_capability_v1(
        capability_ref="adjusted_operating_cash_flow",
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(_plan()),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "net_income must resolve to one consistent confirmed value." in result["errors"]


def test_pyme_026_requires_explicitly_false_safety_flags() -> None:
    plan = _plan()
    del plan["delivery_authorized"]
    absent = _execute(plan=plan)

    plan = _plan()
    plan["runtime_authorized"] = True
    opened = _execute(plan=plan)

    assert absent["status"] == STATUS_BLOCKED
    assert opened["status"] == STATUS_BLOCKED
    assert absent["errors"] == ["governed input safety flags must be explicitly false."]
    assert opened["errors"] == ["governed input safety flags must be explicitly false."]


def test_pyme_026_outcome_remains_non_causal() -> None:
    result = _execute()

    assert result["status"] == STATUS_EVALUATED
    assert result["outcome"]["causal_diagnosis_generated"] is False
    assert result["outcome"]["delivery_authorized"] is False


def test_product_root_executes_pyme_026_once(monkeypatch, tmp_path) -> None:
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    calls: list[str] = []
    real_execute = product.execute_generic_capability_v1

    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(
        product,
        "build_computability_decision_from_confirmed_bindings_v1",
        lambda **_: computable_decision_from_governed_payload(governed_payload_from_legacy_plan(_plan())),
    )

    def counted_execute(**kwargs):
        calls.append(str(kwargs["capability_ref"]))
        return real_execute(**kwargs)

    monkeypatch.setattr(product, "execute_generic_capability_v1", counted_execute)
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": _tables(), "column_refs": _refs()},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="adjusted_operating_cash_flow",
    )

    assert calls == ["adjusted_operating_cash_flow"]
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["diagnosis_generated"] is False


def test_product_root_keeps_pyme_026_delivery_blocked(monkeypatch, tmp_path) -> None:
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(
        product,
        "build_computability_decision_from_confirmed_bindings_v1",
        lambda **_: computable_decision_from_governed_payload(governed_payload_from_legacy_plan(_plan())),
    )

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": _tables(), "column_refs": _refs()},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="adjusted_operating_cash_flow",
        deliver_result=True,
    )

    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "PYME_026_DELIVERY_NOT_AUTHORIZED"
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False

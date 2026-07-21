from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import (
    INV_002,
    get_capability_definition_v1,
    list_capability_refs_v1,
)
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    execute_generic_capability_v1,
)


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "inventory_turnover",
        "pathology_code": "INV_002",
        "formula_id": "INV_002_inventory_turnover",
        "required_variables": ["cost_of_goods_sold", "average_stock"],
        "source_bindings": {
            "cost_of_goods_sold": "cost_of_goods_sold",
            "average_stock": "average_stock",
        },
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _refs() -> list[dict[str, str]]:
    return [
        {
            "sheet_name": "inventory",
            "column_name": name,
            "normalized_column_name": name,
        }
        for name in ("cost_of_goods_sold", "average_stock")
    ]


def _tables(
    *,
    cost_of_goods_sold: object = 1200,
    average_stock: object = 300,
) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "inventory",
            "rows": [
                {
                    "cost_of_goods_sold": cost_of_goods_sold,
                    "average_stock": average_stock,
                }
            ],
        }
    ]


def _execute(
    *,
    cost_of_goods_sold: object = 1200,
    average_stock: object = 300,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="inventory_turnover",
        computation_plan=plan or _plan(),
        normalized_tables=_tables(
            cost_of_goods_sold=cost_of_goods_sold,
            average_stock=average_stock,
        ),
        column_refs=_refs(),
    )


def test_inv_002_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("inventory_turnover")

    assert definition is INV_002
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "INV_002"
    assert definition.formula_ref == "INV_002_inventory_turnover"
    assert definition.result_key == "inventory_turnover_ratio"
    assert definition.result_unit == "ratio"
    assert tuple(variable.name for variable in definition.variables) == (
        "cost_of_goods_sold",
        "average_stock",
    )
    assert "inventory_turnover" in list_capability_refs_v1()


def test_inv_002_calculates_inventory_turnover() -> None:
    result = _execute(cost_of_goods_sold=1200, average_stock=300)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "POSITIVE_RECORDED_TURNOVER"
    assert result["inputs"] == {
        "cost_of_goods_sold": 1200.0,
        "average_stock": 300.0,
    }
    assert result["computed"]["inventory_turnover_ratio"] == 4.0


def test_inv_002_classifies_zero_turnover() -> None:
    result = _execute(cost_of_goods_sold=0, average_stock=300)

    assert result["status"] == STATUS_EVALUATED
    assert result["computed"]["inventory_turnover_ratio"] == 0.0
    assert result["classification"] == "NO_RECORDED_TURNOVER"


def test_inv_002_requires_one_governed_average_stock_value() -> None:
    tables = _tables()
    tables[0]["rows"].append(
        {"cost_of_goods_sold": 600, "average_stock": 301}
    )

    result = execute_generic_capability_v1(
        capability_ref="inventory_turnover",
        computation_plan=_plan(),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "average_stock must resolve to one consistent confirmed value." in result["errors"]


def test_inv_002_sums_cost_of_goods_sold_rows() -> None:
    tables = _tables(cost_of_goods_sold=600, average_stock=300)
    tables[0]["rows"].append(
        {"cost_of_goods_sold": 600, "average_stock": 300}
    )

    result = execute_generic_capability_v1(
        capability_ref="inventory_turnover",
        computation_plan=_plan(),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["computed"]["inventory_turnover_ratio"] == 4.0


def test_inv_002_blocks_zero_average_stock() -> None:
    result = _execute(average_stock=0)

    assert result["status"] == STATUS_BLOCKED
    assert "average_stock must be greater than 0." in result["errors"]


def test_inv_002_blocks_negative_inputs() -> None:
    negative_cost = _execute(cost_of_goods_sold=-1)
    negative_stock = _execute(average_stock=-1)

    assert negative_cost["status"] == STATUS_BLOCKED
    assert negative_stock["status"] == STATUS_BLOCKED
    assert "cost_of_goods_sold must be greater than or equal to 0." in negative_cost["errors"]
    assert "average_stock must be greater than 0." in negative_stock["errors"]


def test_inv_002_blocks_non_finite_values() -> None:
    result = _execute(cost_of_goods_sold="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_inv_002_requires_explicitly_false_safety_flags() -> None:
    plan = _plan()
    del plan["delivery_authorized"]
    absent = _execute(plan=plan)

    plan = _plan()
    plan["runtime_authorized"] = True
    opened = _execute(plan=plan)

    assert absent["status"] == STATUS_BLOCKED
    assert opened["status"] == STATUS_BLOCKED
    assert absent["errors"] == ["computation_plan safety flags must be explicitly false."]
    assert opened["errors"] == ["computation_plan safety flags must be explicitly false."]


def test_inv_002_result_is_typed_and_bounded() -> None:
    result = _execute()

    assert result["computed"]["typed_result"] == {
        "value": 4.0,
        "unit": "ratio",
        "period": None,
        "provenance": "owner_confirmed_normalized_evidence",
    }
    assert result["outcome"]["status"] == "OUTCOME_READY"
    assert result["outcome"]["bounded_finding_generated"] is True
    assert result["outcome"]["causal_diagnosis_generated"] is False
    assert result["runtime_authorized"] is False
    assert result["tool_execution_authorized"] is False
    assert result["product_ready"] is False
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False


def test_product_root_executes_inv_002_once(monkeypatch, tmp_path) -> None:
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    calls: list[str] = []
    real_execute = product.execute_generic_capability_v1

    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan())

    def counted_execute(**kwargs):
        calls.append(str(kwargs["capability_ref"]))
        return real_execute(**kwargs)

    monkeypatch.setattr(product, "execute_generic_capability_v1", counted_execute)

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": _tables(), "column_refs": _refs()},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="inventory_turnover",
    )

    assert calls == ["inventory_turnover"]
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["tools_executed"] is False
    assert result["diagnosis_generated"] is False


def test_product_root_keeps_inv_002_delivery_blocked(monkeypatch, tmp_path) -> None:
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan())

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": _tables(), "column_refs": _refs()},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="inventory_turnover",
        deliver_result=True,
    )

    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "INV_002_DELIVERY_NOT_AUTHORIZED"
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False

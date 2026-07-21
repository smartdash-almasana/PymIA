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


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "index_update_ratio",
        "pathology_code": "REN_002",
        "formula_id": "REN_002_index_update_ratio",
        "required_variables": ["closing_index", "origin_index"],
        "source_bindings": {
            "closing_index": "closing_index",
            "origin_index": "origin_index",
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
            "sheet_name": "indexes",
            "column_name": name,
            "normalized_column_name": name,
        }
        for name in ("closing_index", "origin_index")
    ]


def _tables(*, closing_index: object = 150, origin_index: object = 100) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "indexes",
            "rows": [{"closing_index": closing_index, "origin_index": origin_index}],
        }
    ]


def _execute(
    *,
    closing_index: object = 150,
    origin_index: object = 100,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="index_update_ratio",
        computation_plan=plan or _plan(),
        normalized_tables=_tables(closing_index=closing_index, origin_index=origin_index),
        column_refs=_refs(),
    )


def test_ren_002_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("index_update_ratio")

    assert definition is not None
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "REN_002"
    assert definition.formula_ref == "REN_002_index_update_ratio"
    assert definition.result_key == "index_update_ratio"
    assert definition.result_unit == "ratio"
    assert tuple(variable.name for variable in definition.variables) == (
        "closing_index",
        "origin_index",
    )
    assert "index_update_ratio" in list_capability_refs_v1()


def test_ren_002_calculates_ratio_above_origin() -> None:
    result = _execute(closing_index=150, origin_index=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "INDEX_ABOVE_ORIGIN"
    assert result["computed"]["index_update_ratio"] == 1.5


def test_ren_002_classifies_equal_indexes() -> None:
    result = _execute(closing_index=100, origin_index=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "INDEX_EQUALS_ORIGIN"
    assert result["computed"]["index_update_ratio"] == 1.0


def test_ren_002_classifies_below_origin() -> None:
    result = _execute(closing_index=75, origin_index=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "INDEX_BELOW_ORIGIN"
    assert result["computed"]["index_update_ratio"] == 0.75


def test_ren_002_blocks_zero_origin_index() -> None:
    result = _execute(origin_index=0)

    assert result["status"] == STATUS_BLOCKED
    assert "origin_index must be greater than 0." in result["errors"]


def test_ren_002_blocks_negative_values() -> None:
    negative_closing = _execute(closing_index=-1)
    negative_origin = _execute(origin_index=-1)

    assert negative_closing["status"] == STATUS_BLOCKED
    assert negative_origin["status"] == STATUS_BLOCKED


def test_ren_002_blocks_non_finite_values() -> None:
    result = _execute(closing_index="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_ren_002_requires_single_consistent_values() -> None:
    tables = _tables()
    tables[0]["rows"].append({"closing_index": 160, "origin_index": 100})

    result = execute_generic_capability_v1(
        capability_ref="index_update_ratio",
        computation_plan=_plan(),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "closing_index must resolve to one consistent confirmed value." in result["errors"]


def test_ren_002_requires_explicitly_false_safety_flags() -> None:
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


def test_ren_002_result_is_bounded_and_non_causal() -> None:
    result = _execute()

    assert result["computed"]["typed_result"]["unit"] == "ratio"
    assert result["outcome"]["status"] == "OUTCOME_READY"
    assert result["outcome"]["causal_diagnosis_generated"] is False
    assert result["diagnosis_generated"] is False


def test_product_root_executes_ren_002_once(monkeypatch, tmp_path) -> None:
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
        requested_capability="index_update_ratio",
    )

    assert calls == ["index_update_ratio"]
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["diagnosis_generated"] is False


def test_product_root_keeps_ren_002_delivery_blocked(monkeypatch, tmp_path) -> None:
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
        requested_capability="index_update_ratio",
        deliver_result=True,
    )

    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "REN_002_DELIVERY_NOT_AUTHORIZED"
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False

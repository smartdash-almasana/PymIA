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
        "requested_capability": "sales_concentration",
        "pathology_code": "PYME_033",
        "formula_id": "PYME_033_concentracion_sku",
        "required_variables": ["main_sku_sales", "total_sales"],
        "source_bindings": {
            "main_sku_sales": "main_sku_sales",
            "total_sales": "total_sales",
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
            "sheet_name": "sales",
            "column_name": name,
            "normalized_column_name": name,
        }
        for name in ("main_sku_sales", "total_sales")
    ]


def _tables(
    *,
    main_sku_sales: object = 250,
    total_sales: object = 1000,
) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "sales",
            "rows": [
                {
                    "main_sku_sales": main_sku_sales,
                    "total_sales": total_sales,
                }
            ],
        }
    ]


def _execute(
    *,
    main_sku_sales: object = 250,
    total_sales: object = 1000,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="sales_concentration",
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(plan or _plan()),
        normalized_tables=_tables(
            main_sku_sales=main_sku_sales,
            total_sales=total_sales,
        ),
        column_refs=_refs(),
    )


def test_pyme_033_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("sales_concentration")

    assert definition is not None
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "PYME_033"
    assert definition.formula_ref == "PYME_033_concentracion_sku"
    assert definition.result_key == "sales_concentration_percentage"
    assert definition.result_unit == "percentage"
    assert tuple(variable.name for variable in definition.variables) == (
        "main_sku_sales",
        "total_sales",
    )
    assert "sales_concentration" in list_capability_refs_v1()


def test_pyme_033_calculates_sales_concentration_percentage() -> None:
    result = _execute(main_sku_sales=250, total_sales=1000)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "CONCENTRATION_WITHIN_RECORDED_TOTAL"
    assert result["computed"]["sales_concentration_percentage"] == 25.0


def test_pyme_033_classifies_zero_concentration() -> None:
    result = _execute(main_sku_sales=0, total_sales=1000)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "ZERO_RECORDED_CONCENTRATION"
    assert result["computed"]["sales_concentration_percentage"] == 0.0


def test_pyme_033_classifies_exact_total() -> None:
    result = _execute(main_sku_sales=1000, total_sales=1000)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "CONCENTRATION_WITHIN_RECORDED_TOTAL"
    assert result["computed"]["sales_concentration_percentage"] == 100.0


def test_pyme_033_flags_concentration_above_recorded_total() -> None:
    result = _execute(main_sku_sales=1200, total_sales=1000)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "CONCENTRATION_ABOVE_RECORDED_TOTAL"
    assert result["computed"]["sales_concentration_percentage"] == 120.0
    assert result["outcome"]["causal_diagnosis_generated"] is False


def test_pyme_033_blocks_zero_total_sales() -> None:
    result = _execute(total_sales=0)

    assert result["status"] == STATUS_BLOCKED
    assert "total_sales must be greater than 0." in result["errors"]


def test_pyme_033_blocks_negative_values() -> None:
    negative_main = _execute(main_sku_sales=-1)
    negative_total = _execute(total_sales=-1)

    assert negative_main["status"] == STATUS_BLOCKED
    assert negative_total["status"] == STATUS_BLOCKED


def test_pyme_033_blocks_non_finite_values() -> None:
    result = _execute(main_sku_sales="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_pyme_033_requires_single_consistent_values() -> None:
    tables = _tables()
    tables[0]["rows"].append({"main_sku_sales": 300, "total_sales": 1000})

    result = execute_generic_capability_v1(
        capability_ref="sales_concentration",
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(_plan()),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "main_sku_sales must resolve to one consistent confirmed value." in result["errors"]


def test_pyme_033_requires_explicitly_false_safety_flags() -> None:
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


def test_product_root_executes_pyme_033_once(monkeypatch, tmp_path) -> None:
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
        requested_capability="sales_concentration",
    )

    assert calls == ["sales_concentration"]
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["diagnosis_generated"] is False


def test_product_root_keeps_pyme_033_delivery_blocked(monkeypatch, tmp_path) -> None:
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
        requested_capability="sales_concentration",
        deliver_result=True,
    )

    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "PYME_033_DELIVERY_NOT_AUTHORIZED"
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False

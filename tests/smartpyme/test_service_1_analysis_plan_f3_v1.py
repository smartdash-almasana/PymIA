from __future__ import annotations

import inspect

import pytest

import pymia.smartpyme.service_1_analysis_plan_v1 as analysis_plan_module
from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisFilterV1,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1


def _grain(*, business: str, temporal: str, aggregation: str) -> Service1RequestedAnalysisGrainV1:
    return Service1RequestedAnalysisGrainV1(
        business_entity_grain=business,
        temporal_grain=temporal,
        aggregation_grain=aggregation,
    )


def _reference_plans() -> tuple[Service1AnalysisPlanV1, ...]:
    return (
        Service1AnalysisPlanV1(
            analysis_id="sales_total",
            kind=AnalysisKind.SINGLE_VALUE,
            measures=("sales",),
            dimensions=(),
            relationship_refs=(),
            requested_grain=_grain(business="NONE", temporal="PERIOD", aggregation="AGGREGATED"),
        ),
        Service1AnalysisPlanV1(
            analysis_id="sales_by_product",
            kind=AnalysisKind.GROUPED,
            measures=("sales",),
            dimensions=("product",),
            relationship_refs=(),
            requested_grain=_grain(business="PRODUCT", temporal="PERIOD", aggregation="GROUPED"),
        ),
        Service1AnalysisPlanV1(
            analysis_id="sales_by_branch",
            kind=AnalysisKind.GROUPED,
            measures=("sales",),
            dimensions=("branch",),
            relationship_refs=(),
            requested_grain=_grain(business="BRANCH", temporal="PERIOD", aggregation="GROUPED"),
        ),
        Service1AnalysisPlanV1(
            analysis_id="sales_series_by_day",
            kind=AnalysisKind.SERIES,
            measures=("sales",),
            dimensions=("time",),
            relationship_refs=(),
            requested_grain=_grain(business="NONE", temporal="DAY", aggregation="GROUPED"),
            order_by=(Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),),
        ),
    )


def test_analysis_plan_contract_and_four_reference_plans() -> None:
    plans = _reference_plans()
    assert len(plans) == 4
    assert [plan.analysis_id for plan in plans] == [
        "sales_total",
        "sales_by_product",
        "sales_by_branch",
        "sales_series_by_day",
    ]
    assert all(plan.schema_version == "SERVICE_1_ANALYSIS_PLAN_V1" for plan in plans)
    assert plans[0].to_dict()["dimensions"] == []
    assert plans[1].to_dict()["dimensions"] == ["product"]
    assert plans[2].to_dict()["dimensions"] == ["branch"]
    assert plans[3].to_dict()["order_by"] == [{"field_ref": "time", "direction": "ASC"}]
    assert all(plan.to_dict()["runtime_authorized"] is False for plan in plans)
    assert all(plan.to_dict()["tool_execution_authorized"] is False for plan in plans)
    assert all(plan.to_dict()["product_ready"] is False for plan in plans)
    assert all(plan.to_dict()["delivery_authorized"] is False for plan in plans)
    assert all(plan.to_dict()["diagnosis_generated"] is False for plan in plans)


def test_analysis_plan_is_immutable_and_fail_closed() -> None:
    plan = _reference_plans()[0]
    with pytest.raises((AttributeError, TypeError)):
        plan.analysis_id = "other"  # type: ignore[misc]

    invalid_cases = (
        dict(kind=AnalysisKind.SINGLE_VALUE, dimensions=("product",), requested_grain=_grain(business="NONE", temporal="PERIOD", aggregation="AGGREGATED")),
        dict(kind=AnalysisKind.GROUPED, dimensions=(), requested_grain=_grain(business="PRODUCT", temporal="PERIOD", aggregation="GROUPED")),
        dict(kind=AnalysisKind.SERIES, dimensions=("time",), requested_grain=_grain(business="NONE", temporal="PERIOD", aggregation="GROUPED")),
        dict(kind=AnalysisKind.RANKED, dimensions=("product",), requested_grain=_grain(business="PRODUCT", temporal="PERIOD", aggregation="GROUPED")),
    )
    for case in invalid_cases:
        with pytest.raises(ValueError):
            Service1AnalysisPlanV1(
                analysis_id="invalid",
                measures=("sales",),
                relationship_refs=(),
                order_by=case.pop("order_by", ()),
                **case,
            )
    with pytest.raises(ValueError):
        Service1AnalysisPlanV1(
            analysis_id="invalid",
            kind=AnalysisKind.SINGLE_VALUE,
            measures=("sales", "sales"),
            dimensions=(),
            relationship_refs=(),
            requested_grain=_grain(business="NONE", temporal="PERIOD", aggregation="AGGREGATED"),
        )
    with pytest.raises(ValueError):
        Service1AnalysisPlanV1(
            analysis_id="invalid",
            kind=AnalysisKind.SINGLE_VALUE,
            measures=("sales",),
            dimensions=(),
            relationship_refs=(),
            requested_grain=_grain(business="NONE", temporal="PERIOD", aggregation="AGGREGATED"),
            provenance={"runtime_authorized": True},
        )
    with pytest.raises(ValueError):
        Service1AnalysisOrderByV1(field_ref="time", direction="SIDEWAYS")
    with pytest.raises(ValueError):
        Service1AnalysisPlanV1(
            analysis_id="invalid",
            kind=AnalysisKind.SINGLE_VALUE,
            measures=("sales",),
            dimensions=(),
            relationship_refs=(),
            requested_grain=_grain(business="NONE", temporal="PERIOD", aggregation="AGGREGATED"),
            limit=0,
        )


def test_analysis_plan_has_no_runtime_or_product_authority() -> None:
    source = inspect.getsource(analysis_plan_module)
    assert "FormulaEngineService" not in source
    assert "service_1_product_pipeline_v1" not in source
    assert "service_1_variable_family_bindings_v1" not in source
    assert "service_1_computability_v1" not in source
    assert "xlsx" not in source.lower()
    assert "llm" not in source.lower()
    assert "source_bindings" not in source
    assert "formula_expression" not in source
    assert "computed_values" not in source


def test_requested_grain_is_distinct_from_p7_resolved_grain() -> None:
    requested = _reference_plans()[1].requested_grain
    assert type(requested) is Service1RequestedAnalysisGrainV1
    assert type(requested) is not Service1GrainV1
    assert requested.aggregation_grain == "GROUPED"


def test_product_root_has_no_analysis_plan_branch() -> None:
    from pymia.smartpyme import service_1_product_pipeline_v1 as product_pipeline

    assert "AnalysisPlan" not in inspect.getsource(product_pipeline)


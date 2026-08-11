from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_radar_observable_v1 import (
    KIND_METRIC,
    KIND_OPERATION,
    OP_EQ,
    OP_GT,
    OP_GTE,
    OP_LT,
    RadarObservableV1,
    build_radar_observable_v1,
)


def test_metric_observable_is_neutral_and_serializable() -> None:
    observable = build_radar_observable_v1(
        observable_ref="consorcios.collection_rate_pct",
        vertical_ref="consorcios",
        display_name="Porcentaje cobrado del mes",
        observable_kind=KIND_METRIC,
        source_capability_ref="collection_aging",
        value_field_ref="collection_rate_pct",
        unit="percent",
        entity_scope="consorcio_period",
        supported_operators=(OP_GT, OP_GTE, OP_LT),
        description="Porcentaje matemático disponible para radarización opcional.",
    )

    payload = observable.to_dict()
    assert payload["schema_version"] == "SERVICE_1_RADAR_OBSERVABLE_V1"
    assert payload["observable_ref"] == "consorcios.collection_rate_pct"
    assert payload["supported_operators"] == ["GT", "GTE", "LT"]
    for forbidden in (
        "risk", "severity", "urgency", "threshold", "boundary", "communication_level",
        "alert", "default_action", "positive", "negative",
    ):
        assert forbidden not in payload


def test_operation_observable_is_supported_without_predeclared_business_meaning() -> None:
    observable = RadarObservableV1(
        observable_ref="consorcios.bank_unmatched_operation",
        vertical_ref="consorcios",
        display_name="Movimiento bancario sin imputar",
        observable_kind=KIND_OPERATION,
        source_capability_ref="bank_reconciliation",
        value_field_ref="operation_present",
        unit="boolean",
        entity_scope="bank_movement",
        supported_operators=(OP_EQ,),
    )
    assert observable.observable_kind == KIND_OPERATION
    assert observable.to_dict()["supported_operators"] == ["EQ"]


def test_observable_requires_explicit_vertical_source_and_value_contract() -> None:
    with pytest.raises(ValueError, match="vertical_ref is required"):
        build_radar_observable_v1(
            observable_ref="x",
            vertical_ref="",
            display_name="X",
            observable_kind=KIND_METRIC,
            source_capability_ref="cap",
            value_field_ref="value",
            unit="currency",
            entity_scope="tenant",
            supported_operators=(OP_GT,),
        )


def test_observable_rejects_unknown_or_duplicate_operators() -> None:
    with pytest.raises(ValueError, match="unsupported operators"):
        build_radar_observable_v1(
            observable_ref="x",
            vertical_ref="consorcios",
            display_name="X",
            observable_kind=KIND_METRIC,
            source_capability_ref="cap",
            value_field_ref="value",
            unit="currency",
            entity_scope="tenant",
            supported_operators=("BETWEEN",),
        )
    with pytest.raises(ValueError, match="must be unique"):
        build_radar_observable_v1(
            observable_ref="x",
            vertical_ref="consorcios",
            display_name="X",
            observable_kind=KIND_METRIC,
            source_capability_ref="cap",
            value_field_ref="value",
            unit="currency",
            entity_scope="tenant",
            supported_operators=(OP_GT, OP_GT),
        )

from dataclasses import asdict

import pytest

from pymia.smartpyme.service_1_radar_observable_v1 import (
    KIND_METRIC,
    KIND_OPERATION,
    OP_EQ,
    OP_GT,
    OP_GTE,
    OP_LT,
    build_radar_observable_v1,
)
from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    COMM_ALERT,
    COMM_NOTIFICATION,
    COMM_URGENCY,
    build_radar_observation_policy_v1,
)


def _observable():
    return build_radar_observable_v1(
        observable_ref="consorcios.collection_rate_pct",
        vertical_ref="consorcios",
        display_name="Porcentaje de cobranza mensual",
        observable_kind=KIND_METRIC,
        source_capability_ref="collection_aging",
        value_field_ref="collection_rate_pct",
        unit="percent",
        entity_scope="consorcio_period",
        supported_operators=(OP_GT, OP_GTE, OP_LT),
    )


def test_owner_policy_binds_observable_condition_and_communication_level():
    observable = _observable()
    policy = build_radar_observation_policy_v1(
        tenant_id="tenant-a",
        policy_ref="policy-collection-alert",
        observable=observable,
        enabled=True,
        operator=OP_LT,
        comparison_value="90",
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )

    assert policy.observable_ref == observable.observable_ref
    assert policy.operator == OP_LT
    assert policy.comparison_value == "90"
    assert policy.communication_level == COMM_ALERT
    assert policy.confirmed_by_owner is True


def test_same_observable_accepts_multiple_owner_defined_policies():
    observable = _observable()
    policies = [
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-positive",
            observable=observable,
            enabled=True,
            operator=OP_GTE,
            comparison_value="97",
            communication_level=COMM_NOTIFICATION,
            confirmed_by_owner=True,
        ),
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-alert",
            observable=observable,
            enabled=True,
            operator=OP_LT,
            comparison_value="90",
            communication_level=COMM_ALERT,
            confirmed_by_owner=True,
        ),
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-urgent",
            observable=observable,
            enabled=True,
            operator=OP_LT,
            comparison_value="80",
            communication_level=COMM_URGENCY,
            confirmed_by_owner=True,
        ),
    ]

    assert [p.policy_ref for p in policies] == ["policy-positive", "policy-alert", "policy-urgent"]


def test_policy_fails_closed_without_explicit_owner_confirmation():
    observable = _observable()

    with pytest.raises(ValueError, match="confirmed_by_owner must be true"):
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-unconfirmed",
            observable=observable,
            enabled=True,
            operator=OP_LT,
            comparison_value="90",
            communication_level=COMM_ALERT,
            confirmed_by_owner=False,
        )


def test_policy_fails_closed_when_operator_is_not_exposed_by_vertical_plug():
    observable = _observable()

    with pytest.raises(ValueError, match="operator not supported by observable"):
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-invalid-operator",
            observable=observable,
            enabled=True,
            operator="EQ",
            comparison_value="90",
            communication_level=COMM_ALERT,
            confirmed_by_owner=True,
        )


def test_policy_fails_closed_for_non_numeric_comparison_value():
    observable = _observable()

    with pytest.raises(ValueError, match="comparison_value must be numeric"):
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-invalid-value",
            observable=observable,
            enabled=True,
            operator=OP_LT,
            comparison_value="noventa",
            communication_level=COMM_ALERT,
            confirmed_by_owner=True,
        )


def test_policy_contract_contains_no_pymia_assigned_business_meaning():
    observable = _observable()
    policy = build_radar_observation_policy_v1(
        tenant_id="tenant-a",
        policy_ref="policy-neutral",
        observable=observable,
        enabled=True,
        operator=OP_LT,
        comparison_value="90",
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )

    payload = asdict(policy)
    forbidden = {
        "risk",
        "severity",
        "positive",
        "negative",
        "default_action",
        "business_meaning",
    }
    assert forbidden.isdisjoint(payload)


def test_operation_policy_accepts_boolean_comparison_value():
    observable = build_radar_observable_v1(
        observable_ref="consorcios.bank_unmatched_operation",
        vertical_ref="consorcios",
        display_name="Movimiento bancario sin referencia",
        observable_kind=KIND_OPERATION,
        source_capability_ref="bank_reconciliation",
        value_field_ref="has_unmatched_operation",
        unit="boolean",
        entity_scope="consorcio_period",
        supported_operators=(OP_EQ,),
    )

    policy = build_radar_observation_policy_v1(
        tenant_id="tenant-a",
        policy_ref="policy-unmatched-operation",
        observable=observable,
        enabled=True,
        operator=OP_EQ,
        comparison_value=True,
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )

    assert policy.comparison_value is True


def test_operation_policy_rejects_non_boolean_comparison_value():
    observable = build_radar_observable_v1(
        observable_ref="consorcios.bank_unmatched_operation",
        vertical_ref="consorcios",
        display_name="Movimiento bancario sin referencia",
        observable_kind=KIND_OPERATION,
        source_capability_ref="bank_reconciliation",
        value_field_ref="has_unmatched_operation",
        unit="boolean",
        entity_scope="consorcio_period",
        supported_operators=(OP_EQ,),
    )

    with pytest.raises(ValueError, match="operation comparison_value must be boolean"):
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref="policy-invalid-operation",
            observable=observable,
            enabled=True,
            operator=OP_EQ,
            comparison_value="true",
            communication_level=COMM_ALERT,
            confirmed_by_owner=True,
        )


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_metric_policy_rejects_non_finite_values(value):
    observable = _observable()

    with pytest.raises(ValueError, match="metric comparison_value must be finite"):
        build_radar_observation_policy_v1(
            tenant_id="tenant-a",
            policy_ref=f"policy-non-finite-{value}",
            observable=observable,
            enabled=True,
            operator=OP_LT,
            comparison_value=value,
            communication_level=COMM_ALERT,
            confirmed_by_owner=True,
        )

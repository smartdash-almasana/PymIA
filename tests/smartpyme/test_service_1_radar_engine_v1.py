from decimal import Decimal

import pytest

from pymia.smartpyme.service_1_radar_engine_v1 import (
    evaluate_persisted_radar_observation_v1,
    evaluate_radar_observation_v1,
)
from pymia.smartpyme.service_1_radar_observable_v1 import (
    KIND_METRIC,
    KIND_OPERATION,
    OP_EQ,
    OP_GTE,
    OP_LT,
    OP_NEQ,
    build_radar_observable_v1,
)
from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    COMM_ALERT,
    COMM_NOTIFICATION,
    COMM_URGENCY,
    build_radar_observation_policy_v1,
)


def metric_observable():
    return build_radar_observable_v1(
        observable_ref="consorcios.collection_rate_pct",
        vertical_ref="consorcios",
        display_name="Porcentaje de cobranza",
        observable_kind=KIND_METRIC,
        source_capability_ref="collection_aging",
        value_field_ref="collection_rate_pct",
        unit="percent",
        entity_scope="consorcio_period",
        supported_operators=(OP_GTE, OP_LT),
    )


def operation_observable():
    return build_radar_observable_v1(
        observable_ref="consorcios.bank_unmatched_operation",
        vertical_ref="consorcios",
        display_name="Movimiento bancario sin referencia",
        observable_kind=KIND_OPERATION,
        source_capability_ref="bank_reconciliation",
        value_field_ref="has_unmatched_operation",
        unit="boolean",
        entity_scope="consorcio_period",
        supported_operators=(OP_EQ, OP_NEQ),
    )


def metric_policy(ref, operator, value, level, *, enabled=True, tenant="tenant-a"):
    return build_radar_observation_policy_v1(
        tenant_id=tenant,
        policy_ref=ref,
        observable=metric_observable(),
        enabled=enabled,
        operator=operator,
        comparison_value=value,
        communication_level=level,
        confirmed_by_owner=True,
    )


def operation_policy(ref, operator, value, level, *, tenant="tenant-a"):
    return build_radar_observation_policy_v1(
        tenant_id=tenant,
        policy_ref=ref,
        observable=operation_observable(),
        enabled=True,
        operator=operator,
        comparison_value=value,
        communication_level=level,
        confirmed_by_owner=True,
    )


def test_metric_engine_emits_only_matched_owner_policies():
    observable = metric_observable()
    policies = (
        metric_policy("notify-good", OP_GTE, "97", COMM_NOTIFICATION),
        metric_policy("alert-low", OP_LT, "90", COMM_ALERT),
        metric_policy("urgent-low", OP_LT, "80", COMM_URGENCY),
    )
    events = evaluate_radar_observation_v1(
        tenant_id="tenant-a", observable=observable, observed_value=85, policies=policies
    )
    assert [event.policy_ref for event in events] == ["alert-low"]
    assert events[0].communication_level == COMM_ALERT
    assert events[0].observed_value == "85"


def test_metric_engine_accepts_decimal_and_boundaries_deterministically():
    observable = metric_observable()
    policies = (metric_policy("notify-good", OP_GTE, "97.5", COMM_NOTIFICATION),)
    events = evaluate_radar_observation_v1(
        tenant_id="tenant-a",
        observable=observable,
        observed_value=Decimal("97.5"),
        policies=policies,
    )
    assert len(events) == 1
    assert events[0].comparison_value == "97.5"


def test_operation_engine_supports_boolean_eq_and_neq_only():
    observable = operation_observable()
    policies = (
        operation_policy("alert-unmatched", OP_EQ, True, COMM_ALERT),
        operation_policy("notify-clear", OP_NEQ, True, COMM_NOTIFICATION),
    )
    events = evaluate_radar_observation_v1(
        tenant_id="tenant-a", observable=observable, observed_value=True, policies=policies
    )
    assert [event.policy_ref for event in events] == ["alert-unmatched"]
    assert events[0].observed_value is True


def test_disabled_policy_is_not_evaluated_or_emitted():
    observable = metric_observable()
    policies = (metric_policy("disabled", OP_LT, "90", COMM_ALERT, enabled=False),)
    assert evaluate_radar_observation_v1(
        tenant_id="tenant-a", observable=observable, observed_value=10, policies=policies
    ) == ()


def test_engine_fails_closed_on_cross_tenant_policy():
    observable = metric_observable()
    policies = (metric_policy("foreign", OP_LT, "90", COMM_ALERT, tenant="tenant-b"),)
    with pytest.raises(ValueError, match="crossed tenant boundary"):
        evaluate_radar_observation_v1(
            tenant_id="tenant-a", observable=observable, observed_value=85, policies=policies
        )


def test_engine_fails_closed_on_duplicate_policy_identity():
    observable = metric_observable()
    p = metric_policy("same", OP_LT, "90", COMM_ALERT)
    with pytest.raises(ValueError, match="duplicate RADAR policy_ref"):
        evaluate_radar_observation_v1(
            tenant_id="tenant-a", observable=observable, observed_value=85, policies=(p, p)
        )


def test_engine_rejects_non_finite_or_wrong_observed_types():
    observable = metric_observable()
    p = metric_policy("alert", OP_LT, "90", COMM_ALERT)
    for bad in ("NaN", "Infinity", True):
        with pytest.raises(ValueError):
            evaluate_radar_observation_v1(
                tenant_id="tenant-a", observable=observable, observed_value=bad, policies=(p,)
            )

    op_observable = operation_observable()
    op_policy = operation_policy("op", OP_EQ, True, COMM_ALERT)
    with pytest.raises(ValueError, match="must be boolean"):
        evaluate_radar_observation_v1(
            tenant_id="tenant-a", observable=op_observable, observed_value="true", policies=(op_policy,)
        )


class Store:
    def __init__(self, policies):
        self.policies = policies
        self.calls = []

    def list_policies(self, *, tenant_id, enabled_only=False):
        self.calls.append((tenant_id, enabled_only))
        return self.policies


def test_persisted_engine_loads_enabled_policies_and_filters_by_observable():
    observable = metric_observable()
    unrelated_observable = build_radar_observable_v1(
        observable_ref="consorcios.other_metric",
        vertical_ref="consorcios",
        display_name="Otra métrica",
        observable_kind=KIND_METRIC,
        source_capability_ref="other",
        value_field_ref="other_metric",
        unit="count",
        entity_scope="consorcio_period",
        supported_operators=(OP_LT,),
    )
    related = metric_policy("related", OP_LT, "90", COMM_ALERT)
    unrelated = build_radar_observation_policy_v1(
        tenant_id="tenant-a",
        policy_ref="unrelated",
        observable=unrelated_observable,
        enabled=True,
        operator=OP_LT,
        comparison_value="10",
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )
    store = Store((related, unrelated))

    events = evaluate_persisted_radar_observation_v1(
        tenant_id="tenant-a",
        observable=observable,
        observed_value=85,
        policy_store=store,
    )
    assert store.calls == [("tenant-a", True)]
    assert [event.policy_ref for event in events] == ["related"]


def test_radar_event_contains_no_pymia_assigned_risk_or_severity():
    event = evaluate_radar_observation_v1(
        tenant_id="tenant-a",
        observable=metric_observable(),
        observed_value=85,
        policies=(metric_policy("alert", OP_LT, "90", COMM_ALERT),),
    )[0]
    payload = event.to_dict()
    assert {"risk", "severity", "positive", "negative", "business_meaning"}.isdisjoint(payload)

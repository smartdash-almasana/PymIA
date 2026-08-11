"""Independent deterministic RADAR engine for Servicio 1.

The engine evaluates already-computed observable values against owner-confirmed
policies. It does not calculate source capabilities, assign risk/severity,
infer owner intent, or choose communication levels.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Final, Iterable, Protocol

from pymia.smartpyme.service_1_radar_observable_v1 import (
    KIND_METRIC,
    KIND_OPERATION,
    OP_EQ,
    OP_GT,
    OP_GTE,
    OP_LT,
    OP_LTE,
    OP_NEQ,
    RadarObservableV1,
)
from pymia.smartpyme.service_1_radar_observation_policy_v1 import RadarObservationPolicyV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_RADAR_EVENT_V1"


class RadarPolicyStoreV1(Protocol):
    def list_policies(
        self,
        *,
        tenant_id: str,
        enabled_only: bool = False,
    ) -> tuple[RadarObservationPolicyV1, ...]: ...


@dataclass(frozen=True)
class RadarEventV1:
    tenant_id: str
    policy_ref: str
    observable_ref: str
    observable_kind: str
    observed_value: str | bool
    operator: str
    comparison_value: str | bool
    communication_level: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "tenant_id": self.tenant_id,
            "policy_ref": self.policy_ref,
            "observable_ref": self.observable_ref,
            "observable_kind": self.observable_kind,
            "observed_value": self.observed_value,
            "operator": self.operator,
            "comparison_value": self.comparison_value,
            "communication_level": self.communication_level,
        }


def _finite_decimal(value: object, *, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be numeric") from None
    if not parsed.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return parsed


def _compare_metric(observed: object, policy: RadarObservationPolicyV1) -> tuple[bool, str]:
    left = _finite_decimal(observed, field_name="metric observed_value")
    right = _finite_decimal(policy.comparison_value, field_name="metric comparison_value")
    operations = {
        OP_GT: left > right,
        OP_GTE: left >= right,
        OP_LT: left < right,
        OP_LTE: left <= right,
        OP_EQ: left == right,
        OP_NEQ: left != right,
    }
    if policy.operator not in operations:
        raise ValueError("unsupported metric operator")
    return operations[policy.operator], str(observed)


def _compare_operation(observed: object, policy: RadarObservationPolicyV1) -> tuple[bool, bool]:
    if not isinstance(observed, bool):
        raise ValueError("operation observed_value must be boolean")
    if not isinstance(policy.comparison_value, bool):
        raise ValueError("operation comparison_value must be boolean")
    if policy.operator == OP_EQ:
        return observed is policy.comparison_value, observed
    if policy.operator == OP_NEQ:
        return observed is not policy.comparison_value, observed
    raise ValueError("operation policies support only EQ or NEQ in V1")


def evaluate_radar_observation_v1(
    *,
    tenant_id: str,
    observable: RadarObservableV1,
    observed_value: str | int | float | Decimal | bool,
    policies: Iterable[RadarObservationPolicyV1],
) -> tuple[RadarEventV1, ...]:
    tenant = str(tenant_id or "").strip()
    if not tenant:
        raise ValueError("tenant_id is required")

    events: list[RadarEventV1] = []
    seen_policy_refs: set[str] = set()
    for policy in policies:
        if policy.tenant_id != tenant:
            raise ValueError("RADAR policy crossed tenant boundary")
        if policy.policy_ref in seen_policy_refs:
            raise ValueError("duplicate RADAR policy_ref for tenant")
        seen_policy_refs.add(policy.policy_ref)
        policy.validate_against(observable)
        if not policy.enabled:
            continue

        if observable.observable_kind == KIND_METRIC:
            matched, normalized_observed = _compare_metric(observed_value, policy)
        elif observable.observable_kind == KIND_OPERATION:
            matched, normalized_observed = _compare_operation(observed_value, policy)
        else:
            raise ValueError("unsupported observable_kind")

        if not matched:
            continue
        events.append(
            RadarEventV1(
                tenant_id=tenant,
                policy_ref=policy.policy_ref,
                observable_ref=observable.observable_ref,
                observable_kind=observable.observable_kind,
                observed_value=normalized_observed,
                operator=policy.operator,
                comparison_value=policy.comparison_value,
                communication_level=policy.communication_level,
            )
        )
    return tuple(events)


def evaluate_persisted_radar_observation_v1(
    *,
    tenant_id: str,
    observable: RadarObservableV1,
    observed_value: str | int | float | Decimal | bool,
    policy_store: RadarPolicyStoreV1,
) -> tuple[RadarEventV1, ...]:
    policies = policy_store.list_policies(tenant_id=tenant_id, enabled_only=True)
    relevant = tuple(p for p in policies if p.observable_ref == observable.observable_ref)
    return evaluate_radar_observation_v1(
        tenant_id=tenant_id,
        observable=observable,
        observed_value=observed_value,
        policies=relevant,
    )


__all__ = [
    "SCHEMA_VERSION",
    "RadarEventV1",
    "RadarPolicyStoreV1",
    "evaluate_radar_observation_v1",
    "evaluate_persisted_radar_observation_v1",
]

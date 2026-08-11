"""Owner-defined observation policy for the independent Service 1 RADAR engine.

A policy binds one existing RADAR observable to one owner-selected condition and
one owner-selected communication level. It does not assign risk, severity,
positivity, urgency, or business meaning on behalf of the owner.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Final

from pymia.smartpyme.service_1_radar_observable_v1 import (
    KIND_METRIC,
    KIND_OPERATION,
    RadarObservableV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_RADAR_OBSERVATION_POLICY_V1"

COMM_REPORT: Final[str] = "REPORT"
COMM_NOTIFICATION: Final[str] = "NOTIFICATION"
COMM_ALERT: Final[str] = "ALERT"
COMM_URGENCY: Final[str] = "URGENCY"
SUPPORTED_COMMUNICATION_LEVELS: Final[frozenset[str]] = frozenset(
    {COMM_REPORT, COMM_NOTIFICATION, COMM_ALERT, COMM_URGENCY}
)


@dataclass(frozen=True)
class RadarObservationPolicyV1:
    tenant_id: str
    policy_ref: str
    observable_ref: str
    enabled: bool
    operator: str
    comparison_value: str | bool
    communication_level: str
    confirmed_by_owner: bool

    def __post_init__(self) -> None:
        for field_name in ("tenant_id", "policy_ref", "observable_ref", "operator"):
            if not str(getattr(self, field_name) or "").strip():
                raise ValueError(f"{field_name} is required")
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be boolean")
        if self.communication_level not in SUPPORTED_COMMUNICATION_LEVELS:
            raise ValueError("unsupported communication_level")
        if self.confirmed_by_owner is not True:
            raise ValueError("confirmed_by_owner must be true")

    def validate_against(self, observable: RadarObservableV1) -> None:
        if self.observable_ref != observable.observable_ref:
            raise ValueError("policy observable_ref does not match observable")
        if self.operator not in observable.supported_operators:
            raise ValueError("operator not supported by observable")
        if observable.observable_kind == KIND_METRIC:
            if isinstance(self.comparison_value, bool):
                raise ValueError("metric comparison_value must be numeric")
            try:
                value = Decimal(str(self.comparison_value))
            except (InvalidOperation, ValueError):
                raise ValueError("metric comparison_value must be numeric") from None
            if not value.is_finite():
                raise ValueError("metric comparison_value must be finite")
        elif observable.observable_kind == KIND_OPERATION:
            if not isinstance(self.comparison_value, bool):
                raise ValueError("operation comparison_value must be boolean")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "tenant_id": self.tenant_id,
            "policy_ref": self.policy_ref,
            "observable_ref": self.observable_ref,
            "enabled": self.enabled,
            "operator": self.operator,
            "comparison_value": self.comparison_value,
            "communication_level": self.communication_level,
            "confirmed_by_owner": self.confirmed_by_owner,
        }


def build_radar_observation_policy_v1(
    *,
    tenant_id: str,
    policy_ref: str,
    observable: RadarObservableV1,
    enabled: bool,
    operator: str,
    comparison_value: str | bool,
    communication_level: str,
    confirmed_by_owner: bool,
) -> RadarObservationPolicyV1:
    policy = RadarObservationPolicyV1(
        tenant_id=tenant_id,
        policy_ref=policy_ref,
        observable_ref=observable.observable_ref,
        enabled=enabled,
        operator=operator,
        comparison_value=comparison_value,
        communication_level=communication_level,
        confirmed_by_owner=confirmed_by_owner,
    )
    policy.validate_against(observable)
    return policy


__all__ = [
    "SCHEMA_VERSION",
    "COMM_REPORT",
    "COMM_NOTIFICATION",
    "COMM_ALERT",
    "COMM_URGENCY",
    "RadarObservationPolicyV1",
    "build_radar_observation_policy_v1",
]

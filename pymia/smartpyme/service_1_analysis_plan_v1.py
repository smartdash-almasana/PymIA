"""Immutable declarative analytic intent for Service 1 F3.

This module is intentionally dependency-free.  It describes requested
analysis shape only; it does not resolve evidence, compute values, or grant
any runtime authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


SCHEMA_VERSION = "SERVICE_1_ANALYSIS_PLAN_V1"

_AUTHORITY_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


class AnalysisKind(StrEnum):
    SINGLE_VALUE = "SINGLE_VALUE"
    GROUPED = "GROUPED"
    SERIES = "SERIES"
    RANKED = "RANKED"


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _identifiers(values: object, field_name: str, *, required: bool) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)):
        raise ValueError(f"{field_name} must be a tuple or list of identifiers")
    result = tuple(_required_text(value, f"{field_name} item") for value in values)
    if required and not result:
        raise ValueError(f"{field_name} must not be empty")
    if len(set(result)) != len(result):
        raise ValueError(f"{field_name} must not contain duplicates")
    return result


@dataclass(frozen=True)
class Service1RequestedAnalysisGrainV1:
    business_entity_grain: str
    temporal_grain: str
    aggregation_grain: str

    def __post_init__(self) -> None:
        for name in ("business_entity_grain", "temporal_grain", "aggregation_grain"):
            object.__setattr__(self, name, _required_text(getattr(self, name), name))

    def to_dict(self) -> dict[str, str]:
        return {
            "business_entity_grain": self.business_entity_grain,
            "temporal_grain": self.temporal_grain,
            "aggregation_grain": self.aggregation_grain,
        }


@dataclass(frozen=True)
class Service1AnalysisFilterV1:
    field_ref: str
    operator: str
    value: Any

    def __post_init__(self) -> None:
        object.__setattr__(self, "field_ref", _required_text(self.field_ref, "field_ref"))
        object.__setattr__(self, "operator", _required_text(self.operator, "operator"))

    def to_dict(self) -> dict[str, Any]:
        return {"field_ref": self.field_ref, "operator": self.operator, "value": self.value}


@dataclass(frozen=True)
class Service1AnalysisOrderByV1:
    field_ref: str
    direction: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "field_ref", _required_text(self.field_ref, "field_ref"))
        direction = _required_text(self.direction, "direction")
        if direction not in {"ASC", "DESC"}:
            raise ValueError("direction must be ASC or DESC")
        object.__setattr__(self, "direction", direction)

    def to_dict(self) -> dict[str, str]:
        return {"field_ref": self.field_ref, "direction": self.direction}


@dataclass(frozen=True)
class Service1AnalysisPlanV1:
    analysis_id: str
    kind: AnalysisKind
    measures: tuple[str, ...]
    dimensions: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    requested_grain: Service1RequestedAnalysisGrainV1
    filters: tuple[Service1AnalysisFilterV1, ...] = ()
    order_by: tuple[Service1AnalysisOrderByV1, ...] = ()
    limit: int | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "analysis_id", _required_text(self.analysis_id, "analysis_id"))
        try:
            kind = self.kind if isinstance(self.kind, AnalysisKind) else AnalysisKind(self.kind)
        except (TypeError, ValueError) as exc:
            raise ValueError("kind must be a supported AnalysisKind") from exc
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "measures", _identifiers(self.measures, "measures", required=True))
        object.__setattr__(self, "dimensions", _identifiers(self.dimensions, "dimensions", required=False))
        object.__setattr__(self, "relationship_refs", _identifiers(self.relationship_refs, "relationship_refs", required=False))
        if not isinstance(self.requested_grain, Service1RequestedAnalysisGrainV1):
            raise ValueError("requested_grain must be Service1RequestedAnalysisGrainV1")
        filters = self.filters if isinstance(self.filters, tuple) else tuple(self.filters) if isinstance(self.filters, list) else None
        if filters is None or any(not isinstance(item, Service1AnalysisFilterV1) for item in filters):
            raise ValueError("filters must contain Service1AnalysisFilterV1 values")
        object.__setattr__(self, "filters", filters)
        order_by = self.order_by if isinstance(self.order_by, tuple) else tuple(self.order_by) if isinstance(self.order_by, list) else None
        if order_by is None or any(not isinstance(item, Service1AnalysisOrderByV1) for item in order_by):
            raise ValueError("order_by must contain Service1AnalysisOrderByV1 values")
        object.__setattr__(self, "order_by", order_by)
        if self.limit is not None and (isinstance(self.limit, bool) or not isinstance(self.limit, int) or self.limit <= 0):
            raise ValueError("limit must be None or an integer greater than zero")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if any(flag in self.provenance and self.provenance[flag] is not False for flag in _AUTHORITY_FLAGS):
            raise ValueError("analysis plan cannot authorize runtime, tools, product, delivery, or diagnosis")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        aggregation = self.requested_grain.aggregation_grain
        if kind is AnalysisKind.SINGLE_VALUE:
            if self.dimensions or aggregation != "AGGREGATED":
                raise ValueError("SINGLE_VALUE requires empty dimensions and AGGREGATED grain")
        elif kind is AnalysisKind.GROUPED:
            if not self.dimensions or aggregation != "GROUPED":
                raise ValueError("GROUPED requires dimensions and GROUPED aggregation grain")
        elif kind is AnalysisKind.SERIES:
            if "time" not in self.dimensions or self.requested_grain.temporal_grain in {"NONE", "PERIOD"} or aggregation != "GROUPED":
                raise ValueError("SERIES requires time, a requested temporal grain, and GROUPED aggregation grain")
        elif kind is AnalysisKind.RANKED:
            if not self.dimensions or not self.order_by:
                raise ValueError("RANKED requires dimensions and order_by")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "analysis_id": self.analysis_id,
            "kind": self.kind.value,
            "measures": list(self.measures),
            "dimensions": list(self.dimensions),
            "relationship_refs": list(self.relationship_refs),
            "requested_grain": self.requested_grain.to_dict(),
            "filters": [item.to_dict() for item in self.filters],
            "order_by": [item.to_dict() for item in self.order_by],
            "limit": self.limit,
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }


__all__ = [
    "AnalysisKind",
    "Service1RequestedAnalysisGrainV1",
    "Service1AnalysisFilterV1",
    "Service1AnalysisOrderByV1",
    "Service1AnalysisPlanV1",
]

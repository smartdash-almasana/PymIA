"""Neutral observable contract for the independent Service 1 RADAR engine.

A RADAR observable describes something a vertical plug can expose for optional
owner monitoring. It contains no risk, urgency, threshold, communication level,
or default business meaning. Those belong to owner-selected policy layers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_RADAR_OBSERVABLE_V1"

KIND_METRIC: Final[str] = "METRIC"
KIND_OPERATION: Final[str] = "OPERATION"
SUPPORTED_KINDS: Final[frozenset[str]] = frozenset({KIND_METRIC, KIND_OPERATION})

OP_GT: Final[str] = "GT"
OP_GTE: Final[str] = "GTE"
OP_LT: Final[str] = "LT"
OP_LTE: Final[str] = "LTE"
OP_EQ: Final[str] = "EQ"
OP_NEQ: Final[str] = "NEQ"
SUPPORTED_OPERATORS: Final[frozenset[str]] = frozenset({OP_GT, OP_GTE, OP_LT, OP_LTE, OP_EQ, OP_NEQ})


@dataclass(frozen=True)
class RadarObservableV1:
    observable_ref: str
    vertical_ref: str
    display_name: str
    observable_kind: str
    source_capability_ref: str
    value_field_ref: str
    unit: str
    entity_scope: str
    supported_operators: tuple[str, ...]
    description: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "observable_ref",
            "vertical_ref",
            "display_name",
            "source_capability_ref",
            "value_field_ref",
            "unit",
            "entity_scope",
        ):
            if not str(getattr(self, field_name) or "").strip():
                raise ValueError(f"{field_name} is required")
        if self.observable_kind not in SUPPORTED_KINDS:
            raise ValueError("unsupported observable_kind")
        if not self.supported_operators:
            raise ValueError("supported_operators must not be empty")
        unknown = [op for op in self.supported_operators if op not in SUPPORTED_OPERATORS]
        if unknown:
            raise ValueError(f"unsupported operators: {','.join(unknown)}")
        if len(set(self.supported_operators)) != len(self.supported_operators):
            raise ValueError("supported_operators must be unique")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "observable_ref": self.observable_ref,
            "vertical_ref": self.vertical_ref,
            "display_name": self.display_name,
            "observable_kind": self.observable_kind,
            "source_capability_ref": self.source_capability_ref,
            "value_field_ref": self.value_field_ref,
            "unit": self.unit,
            "entity_scope": self.entity_scope,
            "supported_operators": list(self.supported_operators),
            "description": self.description,
        }


def build_radar_observable_v1(
    *,
    observable_ref: str,
    vertical_ref: str,
    display_name: str,
    observable_kind: str,
    source_capability_ref: str,
    value_field_ref: str,
    unit: str,
    entity_scope: str,
    supported_operators: tuple[str, ...],
    description: str = "",
) -> RadarObservableV1:
    return RadarObservableV1(
        observable_ref=observable_ref,
        vertical_ref=vertical_ref,
        display_name=display_name,
        observable_kind=observable_kind,
        source_capability_ref=source_capability_ref,
        value_field_ref=value_field_ref,
        unit=unit,
        entity_scope=entity_scope,
        supported_operators=supported_operators,
        description=description,
    )


__all__ = [
    "SCHEMA_VERSION",
    "KIND_METRIC",
    "KIND_OPERATION",
    "OP_GT",
    "OP_GTE",
    "OP_LT",
    "OP_LTE",
    "OP_EQ",
    "OP_NEQ",
    "RadarObservableV1",
    "build_radar_observable_v1",
]

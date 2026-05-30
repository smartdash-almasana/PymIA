"""Minimal contracts for pluggable MicroSaaS modules."""

from dataclasses import dataclass


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True)
class MicroSaaSDescriptor:
    microsaas_id: str
    name: str
    version: str
    description: str
    category: str
    enabled: bool

    def __post_init__(self) -> None:
        _require_non_empty(self.microsaas_id, "microsaas_id")
        _require_non_empty(self.version, "version")
        _require_non_empty(self.category, "category")


@dataclass(frozen=True)
class MicroSaaSCapability:
    capability_id: str
    microsaas_id: str
    input_kind: str
    output_kind: str

    def __post_init__(self) -> None:
        _require_non_empty(self.capability_id, "capability_id")
        _require_non_empty(self.microsaas_id, "microsaas_id")

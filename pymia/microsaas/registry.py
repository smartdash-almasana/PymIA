"""Deterministic in-memory registry for MicroSaaS descriptors."""

from .contracts import MicroSaaSDescriptor

_registry: dict[str, MicroSaaSDescriptor] = {}


def register_microsaas(descriptor: MicroSaaSDescriptor) -> None:
    if descriptor.microsaas_id in _registry:
        raise ValueError(f"MicroSaaS already registered: {descriptor.microsaas_id}")
    _registry[descriptor.microsaas_id] = descriptor


def get_microsaas(microsaas_id: str) -> MicroSaaSDescriptor | None:
    return _registry.get(microsaas_id)


def list_microsaas() -> list[MicroSaaSDescriptor]:
    return [_registry[microsaas_id] for microsaas_id in sorted(_registry)]


def clear_registry() -> None:
    _registry.clear()

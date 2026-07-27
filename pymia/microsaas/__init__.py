"""Internal plugin bay for future MicroSaaS modules."""

from .contracts import MicroSaaSCapability, MicroSaaSDescriptor
from .registry import clear_registry, get_microsaas, list_microsaas, register_microsaas

__all__ = [
    "MicroSaaSCapability",
    "MicroSaaSDescriptor",
    "clear_registry",
    "get_microsaas",
    "list_microsaas",
    "register_microsaas",
]

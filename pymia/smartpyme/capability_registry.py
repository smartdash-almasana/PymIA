from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ALLOWED_CAPABILITY_STATUSES: tuple[str, ...] = (
    "PIPELINE_CERTIFIED",
    "AVAILABLE",
    "PARTIALLY_AVAILABLE_BY_PATH",
    "UNSUPPORTED_IN_DISPATCHER",
    "DOCUMENTED_NOT_IMPLEMENTED",
    "NOT_FOUND",
    "CONCEPTUAL",
)

_MIN_CAPABILITY_FIELDS: tuple[str, ...] = (
    "capability_id",
    "status",
    "pipeline_certified",
    "dispatcher_available",
    "cli_available",
    "plugin_module",
    "plugin_function",
    "dispatcher_classification",
    "tests",
    "docs",
)


def _default_registry_path() -> Path:
    return Path(__file__).resolve().with_name("capabilities.yaml")


def _validate_capability(capability: dict[str, Any]) -> dict[str, Any]:
    for field in _MIN_CAPABILITY_FIELDS:
        if field not in capability:
            raise ValueError(f"Capability missing required field: {field}")

    capability_id = capability.get("capability_id")
    if not isinstance(capability_id, str) or not capability_id.strip():
        raise ValueError("capability_id must be a non-empty string")

    status = capability.get("status")
    if status not in ALLOWED_CAPABILITY_STATUSES:
        raise ValueError(f"Unsupported capability status: {status!r}")

    for boolean_field in ("pipeline_certified", "dispatcher_available", "cli_available"):
        if not isinstance(capability.get(boolean_field), bool):
            raise ValueError(f"{capability_id}.{boolean_field} must be bool")

    plugin_module = capability.get("plugin_module")
    plugin_function = capability.get("plugin_function")
    if (plugin_module is None) ^ (plugin_function is None):
        raise ValueError(
            f"{capability_id} must define plugin_module and plugin_function together"
        )
    if plugin_module is not None and not isinstance(plugin_module, str):
        raise ValueError(f"{capability_id}.plugin_module must be string or null")
    if plugin_function is not None and not isinstance(plugin_function, str):
        raise ValueError(f"{capability_id}.plugin_function must be string or null")

    dispatcher_classification = capability.get("dispatcher_classification")
    if dispatcher_classification is not None and not isinstance(dispatcher_classification, str):
        raise ValueError(
            f"{capability_id}.dispatcher_classification must be string or null"
        )

    for list_field in ("tests", "docs"):
        value = capability.get(list_field)
        if not isinstance(value, list):
            raise ValueError(f"{capability_id}.{list_field} must be a list")

    return dict(capability)


def load_registry() -> dict[str, Any]:
    registry_path = _default_registry_path()
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Registry root must be a mapping")

    capabilities_raw = data.get("capabilities")
    if not isinstance(capabilities_raw, list):
        raise ValueError("Registry must define a capabilities list")

    validated_capabilities: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in capabilities_raw:
        if not isinstance(item, dict):
            raise ValueError("Each capability entry must be a mapping")
        capability = _validate_capability(item)
        capability_id = capability["capability_id"]
        if capability_id in seen_ids:
            raise ValueError(f"Duplicate capability_id: {capability_id}")
        seen_ids.add(capability_id)
        validated_capabilities.append(capability)

    return {
        "version": data.get("version"),
        "capabilities": validated_capabilities,
    }


def list_capabilities() -> list[dict[str, Any]]:
    registry = load_registry()
    return [dict(item) for item in registry["capabilities"]]


def get_capability(capability_id: str) -> dict[str, Any]:
    for capability in list_capabilities():
        if capability["capability_id"] == capability_id:
            return capability
    raise KeyError(capability_id)


def is_pipeline_certified(capability_id: str) -> bool:
    return bool(get_capability(capability_id)["pipeline_certified"])


def is_dispatcher_available(capability_id: str) -> bool:
    return bool(get_capability(capability_id)["dispatcher_available"])


__all__ = [
    "ALLOWED_CAPABILITY_STATUSES",
    "get_capability",
    "is_dispatcher_available",
    "is_pipeline_certified",
    "list_capabilities",
    "load_registry",
]

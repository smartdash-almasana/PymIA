from __future__ import annotations

import json
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]

_ALLOWED_KEYS = {
    "$schema",
    "$id",
    "title",
    "type",
    "description",
    "properties",
    "items",
    "required",
    "enum",
    "default",
    "format",
    "pattern",
    "minimum",
    "maximum",
    "minItems",
    "maxItems",
    "minLength",
    "maxLength",
}

_TOP_LEVEL_REQUIRED = [
    "document_identity",
    "curation_status",
    "items",
    "extraction_quality",
]


class BemSchemaCompatError(ValueError):
    """Raised when candidate schema is not a valid JSON object."""


def build_bem_compatible_schema(candidate: JsonObject) -> JsonObject:
    if not isinstance(candidate, dict):
        raise BemSchemaCompatError("candidate schema must be a JSON object")

    cleaned = _clean_node(candidate, path="$")
    if not isinstance(cleaned, dict):
        raise BemSchemaCompatError("cleaned schema must be a JSON object")

    cleaned["$schema"] = "http://json-schema.org/draft-07/schema#"
    cleaned.setdefault("title", "PymIA BEM Compatible Output Schema")
    cleaned.setdefault("type", "object")

    properties = cleaned.get("properties")
    if not isinstance(properties, dict):
        cleaned["properties"] = {}
        properties = cleaned["properties"]

    top_required = [name for name in _TOP_LEVEL_REQUIRED if name in properties]
    cleaned["required"] = top_required

    _ensure_descriptions(cleaned, path="$")

    return cleaned


def build_bem_compatible_from_file(candidate_path: str | Path, output_path: str | Path) -> JsonObject:
    candidate_data = json.loads(Path(candidate_path).read_text(encoding="utf-8"))
    if not isinstance(candidate_data, dict):
        raise BemSchemaCompatError("candidate file must contain a JSON object")

    compatible = build_bem_compatible_schema(candidate_data)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(compatible, ensure_ascii=False, indent=2), encoding="utf-8")
    return compatible


def _clean_node(node: Any, *, path: str) -> Any:
    if isinstance(node, dict):
        if path.endswith(".properties"):
            return {
                str(key): _clean_node(value, path=f"{path}.{key}")
                for key, value in node.items()
                if isinstance(key, str) and not key.startswith("x_")
            }

        if "type" in node:
            node = dict(node)
            node["type"] = _normalize_type(node.get("type"), path=path)

        result: dict[str, Any] = {}
        for key, value in node.items():
            if key.startswith("x_"):
                continue
            if key == "additionalProperties":
                continue
            if key not in _ALLOWED_KEYS:
                continue
            result[key] = _clean_node(value, path=f"{path}.{key}")

        if isinstance(result.get("items"), list):
            result["items"] = result["items"][0] if result["items"] else {"type": "object"}

        if "required" in result and isinstance(result["required"], list):
            if path.endswith(".items") or path.endswith(".items.items"):
                result["required"] = []

        return result

    if isinstance(node, list):
        return [_clean_node(item, path=f"{path}[]") for item in node]

    return node


def _normalize_type(type_value: Any, *, path: str) -> str:
    if isinstance(type_value, str):
        return type_value
    if isinstance(type_value, list):
        filtered = [t for t in type_value if t != "null"]
        if not filtered:
            return "string"
        primary = filtered[0]
        if primary in {"string", "number", "integer", "boolean", "object", "array"}:
            return primary
        return "string"
    return "string"


def _ensure_descriptions(node: Any, *, path: str) -> None:
    if not isinstance(node, dict):
        return

    if "properties" in node and isinstance(node["properties"], dict):
        for name, child in node["properties"].items():
            if isinstance(child, dict):
                if not child.get("description"):
                    child["description"] = _default_description(name=name, path=f"{path}.properties.{name}", child=child)
                _ensure_descriptions(child, path=f"{path}.properties.{name}")

    items = node.get("items")
    if isinstance(items, dict):
        if not items.get("description"):
            items["description"] = f"Array item extracted at {path}.items."
        _ensure_descriptions(items, path=f"{path}.items")


def _default_description(*, name: str, path: str, child: dict[str, Any]) -> str:
    t = child.get("type", "value")
    nullable_note = " This field may be absent when it cannot be extracted from the source document."
    return f"Extracted {t} field '{name}' from {path}.{nullable_note}"

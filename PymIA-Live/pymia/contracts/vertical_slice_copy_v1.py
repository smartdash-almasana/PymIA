from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


VERTICAL_SLICE_COPY_CONTRACT_PATH = Path(__file__).resolve().with_name("vertical_slice_copy_v1.json")

_REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "status",
    "owner_simple_understanding_by_axis",
    "owner_simple_readable_areas",
    "copy_by_key",
)

_REQUIRED_COPY_KEYS = (
    "owner_question_missing_field",
    "owner_question_missing_generic",
    "owner_simple_readable_summary_template",
    "owner_simple_minimal_signals",
    "owner_simple_unreadable",
    "owner_simple_unknown_assertion",
    "missing_data_rows_question",
    "missing_operational_columns_question",
    "blocked_summary",
    "candidate_summary",
    "next_step_review_with_owner",
    "forbidden_inference_from_column_names",
    "evidence_request_reason",
    "next_question_fallback",
    "final_limit_warning",
)


class VerticalSliceCopyContractError(ValueError):
    """Raised when the vertical slice copy contract is invalid."""


def validate_vertical_slice_copy_contract(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise VerticalSliceCopyContractError("vertical slice copy contract must be an object")

    missing = [key for key in _REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise VerticalSliceCopyContractError(f"missing required keys: {', '.join(missing)}")

    if data["status"] != "ACTIVE":
        raise VerticalSliceCopyContractError("vertical slice copy contract status must be ACTIVE")

    if not isinstance(data["owner_simple_understanding_by_axis"], dict):
        raise VerticalSliceCopyContractError("owner_simple_understanding_by_axis must be an object")

    if not isinstance(data["owner_simple_readable_areas"], dict):
        raise VerticalSliceCopyContractError("owner_simple_readable_areas must be an object")

    copy_by_key = data["copy_by_key"]
    if not isinstance(copy_by_key, dict):
        raise VerticalSliceCopyContractError("copy_by_key must be an object")

    missing_copy_keys = [key for key in _REQUIRED_COPY_KEYS if key not in copy_by_key]
    if missing_copy_keys:
        raise VerticalSliceCopyContractError(
            f"missing required copy keys: {', '.join(missing_copy_keys)}"
        )

    return data


@lru_cache(maxsize=1)
def load_vertical_slice_copy_contract() -> dict[str, Any]:
    data = json.loads(VERTICAL_SLICE_COPY_CONTRACT_PATH.read_text(encoding="utf-8"))
    return validate_vertical_slice_copy_contract(data)


def vertical_slice_copy_for(key: str) -> str:
    data = load_vertical_slice_copy_contract()
    copy_by_key = data["copy_by_key"]
    if key not in copy_by_key:
        raise KeyError(f"unknown vertical slice copy key: {key}")
    return str(copy_by_key[key])


def owner_simple_understanding_by_axis() -> dict[str, str]:
    data = load_vertical_slice_copy_contract()
    return {
        str(key): str(value)
        for key, value in (data.get("owner_simple_understanding_by_axis") or {}).items()
    }


def owner_simple_readable_areas() -> dict[str, dict[str, list[str]]]:
    data = load_vertical_slice_copy_contract()
    raw = data.get("owner_simple_readable_areas") or {}
    normalized: dict[str, dict[str, list[str]]] = {}
    for label, payload in raw.items():
        keywords = payload.get("keywords") if isinstance(payload, dict) else []
        normalized[str(label)] = {"keywords": [str(item) for item in keywords]}
    return normalized


__all__ = [
    "VERTICAL_SLICE_COPY_CONTRACT_PATH",
    "VerticalSliceCopyContractError",
    "load_vertical_slice_copy_contract",
    "owner_simple_readable_areas",
    "owner_simple_understanding_by_axis",
    "validate_vertical_slice_copy_contract",
    "vertical_slice_copy_for",
]

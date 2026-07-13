from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


OWNER_FACING_REPORT_COPY_CONTRACT_PATH = Path(__file__).resolve().with_name("owner_facing_report_copy_v1.json")

_REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "status",
    "warnings_by_operational_status",
)


class OwnerFacingReportCopyContractError(ValueError):
    """Raised when the owner-facing report copy contract is invalid."""


def validate_owner_facing_report_copy_contract(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise OwnerFacingReportCopyContractError("owner-facing report copy contract must be an object")

    missing = [key for key in _REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise OwnerFacingReportCopyContractError(f"missing required keys: {', '.join(missing)}")

    if data["status"] != "ACTIVE":
        raise OwnerFacingReportCopyContractError("owner-facing report copy contract status must be ACTIVE")

    warnings_by_operational_status = data["warnings_by_operational_status"]
    if not isinstance(warnings_by_operational_status, dict):
        raise OwnerFacingReportCopyContractError("warnings_by_operational_status must be an object")

    return data


@lru_cache(maxsize=1)
def load_owner_facing_report_copy_contract() -> dict[str, Any]:
    data = json.loads(OWNER_FACING_REPORT_COPY_CONTRACT_PATH.read_text(encoding="utf-8"))
    return validate_owner_facing_report_copy_contract(data)


def warning_for_operational_status(status: str) -> str | None:
    data = load_owner_facing_report_copy_contract()
    warnings_by_operational_status = data.get("warnings_by_operational_status") or {}
    warning = warnings_by_operational_status.get(status)
    return str(warning) if warning else None


__all__ = [
    "OWNER_FACING_REPORT_COPY_CONTRACT_PATH",
    "OwnerFacingReportCopyContractError",
    "load_owner_facing_report_copy_contract",
    "validate_owner_facing_report_copy_contract",
    "warning_for_operational_status",
]

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

EvidenceAvailabilityStatus = Literal[
    "MEASURED",
    "ZERO_REAL",
    "NOT_AVAILABLE",
    "PARTIAL",
    "CAPPED",
    "AMBIGUOUS",
    "EXCLUDED",
]


@lru_cache(maxsize=1)
def load_evidence_availability_contract() -> dict[str, Any]:
    """Load the Evidence Availability V1 declarative contract.

    This loader is contract-only. It does not normalize evidence, calculate formulas,
    diagnose, persist state, or call runtime services.
    """
    contract_path = Path(__file__).resolve().parent / "evidence_availability_v1.json"
    if not contract_path.exists():
        return {}
    return json.loads(contract_path.read_text(encoding="utf-8"))


def list_availability_statuses() -> list[str]:
    contract = load_evidence_availability_contract()
    return list(contract.get("availability_statuses", {}).keys())


def get_availability_status(status: str) -> dict[str, Any] | None:
    normalized_status = _required_text(status, field_name="status")
    contract = load_evidence_availability_contract()
    return contract.get("availability_statuses", {}).get(normalized_status)


def get_reason_code(reason_code: str) -> dict[str, Any] | None:
    normalized_reason_code = _required_text(reason_code, field_name="reason_code")
    contract = load_evidence_availability_contract()
    return contract.get("reason_codes", {}).get(normalized_reason_code)


def default_status_for_reason(reason_code: str) -> str | None:
    reason = get_reason_code(reason_code)
    if reason is None:
        return None
    return reason.get("default_status")


def allows_calculation(status: EvidenceAvailabilityStatus | str) -> bool:
    status_spec = get_availability_status(str(status))
    if status_spec is None:
        return False
    return bool(status_spec.get("allows_calculation"))


def requires_owner_disclosure(status: EvidenceAvailabilityStatus | str) -> bool:
    status_spec = get_availability_status(str(status))
    if status_spec is None:
        return False
    return bool(status_spec.get("requires_owner_disclosure"))


def is_excluded_from_calculation(status: EvidenceAvailabilityStatus | str) -> bool:
    status_spec = get_availability_status(str(status))
    if status_spec is None:
        return False
    return bool(status_spec.get("excluded_from_calculation"))


def blocks_required_field(status: EvidenceAvailabilityStatus | str) -> bool:
    contract = load_evidence_availability_contract()
    blocking_statuses = set(contract.get("field_policy", {}).get("required_field_blocking_statuses", []))
    return str(status) in blocking_statuses


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


__all__ = [
    "EvidenceAvailabilityStatus",
    "allows_calculation",
    "blocks_required_field",
    "default_status_for_reason",
    "get_availability_status",
    "get_reason_code",
    "is_excluded_from_calculation",
    "list_availability_statuses",
    "load_evidence_availability_contract",
    "requires_owner_disclosure",
]

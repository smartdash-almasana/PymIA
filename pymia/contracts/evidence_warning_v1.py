from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

EvidenceWarningSeverity = Literal["INFO", "CAUTION", "BLOCKING"]


@lru_cache(maxsize=1)
def load_evidence_warning_contract() -> dict[str, Any]:
    """Load the Evidence Warning V1 declarative contract.

    This loader is contract-only. It does not create warnings, normalize evidence,
    calculate formulas, diagnose, persist state, or call runtime services.
    """
    contract_path = Path(__file__).resolve().parent / "evidence_warning_v1.json"
    if not contract_path.exists():
        return {}
    return json.loads(contract_path.read_text(encoding="utf-8"))


def list_warning_severities() -> list[str]:
    contract = load_evidence_warning_contract()
    return list(contract.get("severities", {}).keys())


def get_warning_severity(severity: str) -> dict[str, Any] | None:
    normalized_severity = _required_text(severity, field_name="severity")
    contract = load_evidence_warning_contract()
    return contract.get("severities", {}).get(normalized_severity)


def list_warning_fields() -> list[str]:
    contract = load_evidence_warning_contract()
    return list(contract.get("warning_fields", []))


def default_severity_for_reason(reason_code: str) -> str | None:
    normalized_reason_code = _required_text(reason_code, field_name="reason_code")
    contract = load_evidence_warning_contract()
    return contract.get("reason_code_severity_defaults", {}).get(normalized_reason_code)


def blocks_calculation(severity: EvidenceWarningSeverity | str) -> bool:
    severity_spec = get_warning_severity(str(severity))
    if severity_spec is None:
        return False
    return bool(severity_spec.get("blocks_calculation"))


def requires_owner_disclosure(severity: EvidenceWarningSeverity | str) -> bool:
    severity_spec = get_warning_severity(str(severity))
    if severity_spec is None:
        return False
    return bool(severity_spec.get("requires_owner_disclosure"))


def is_owner_message_allowed(owner_message: str) -> bool:
    normalized_owner_message = _required_text(owner_message, field_name="owner_message")
    contract = load_evidence_warning_contract()
    forbidden_terms = contract.get("owner_message_policy", {}).get("forbidden_terms", [])
    lowered_message = normalized_owner_message.lower()
    return all(str(term).lower() not in lowered_message for term in forbidden_terms)


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


__all__ = [
    "EvidenceWarningSeverity",
    "blocks_calculation",
    "default_severity_for_reason",
    "get_warning_severity",
    "is_owner_message_allowed",
    "list_warning_fields",
    "list_warning_severities",
    "load_evidence_warning_contract",
    "requires_owner_disclosure",
]

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


EVIDENCE_REQUIREMENT_COPY_CONTRACT_PATH = Path(__file__).resolve().with_name("evidence_requirement_copy_v1.json")

_REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "status",
    "copy_templates",
    "fallbacks",
)

_REQUIRED_COPY_TEMPLATES = ("missing_evidence_question",)
_REQUIRED_FALLBACKS = ("missing_evidence",)


class EvidenceRequirementCopyContractError(ValueError):
    """Raised when the evidence requirement copy contract is invalid."""


def validate_evidence_requirement_copy_contract(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise EvidenceRequirementCopyContractError("evidence requirement copy contract must be an object")

    missing = [key for key in _REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise EvidenceRequirementCopyContractError(f"missing required keys: {', '.join(missing)}")

    if data["status"] != "ACTIVE":
        raise EvidenceRequirementCopyContractError("evidence requirement copy contract status must be ACTIVE")

    copy_templates = data["copy_templates"]
    if not isinstance(copy_templates, dict):
        raise EvidenceRequirementCopyContractError("copy_templates must be an object")

    missing_templates = [key for key in _REQUIRED_COPY_TEMPLATES if key not in copy_templates]
    if missing_templates:
        raise EvidenceRequirementCopyContractError(
            f"missing required copy templates: {', '.join(missing_templates)}"
        )

    fallbacks = data["fallbacks"]
    if not isinstance(fallbacks, dict):
        raise EvidenceRequirementCopyContractError("fallbacks must be an object")

    missing_fallbacks = [key for key in _REQUIRED_FALLBACKS if key not in fallbacks]
    if missing_fallbacks:
        raise EvidenceRequirementCopyContractError(
            f"missing required fallbacks: {', '.join(missing_fallbacks)}"
        )

    return data


@lru_cache(maxsize=1)
def load_evidence_requirement_copy_contract() -> dict[str, Any]:
    data = json.loads(EVIDENCE_REQUIREMENT_COPY_CONTRACT_PATH.read_text(encoding="utf-8"))
    return validate_evidence_requirement_copy_contract(data)


def build_missing_evidence_question(pathology_code: str, missing_evidence: list[str]) -> str:
    data = load_evidence_requirement_copy_contract()
    template = data["copy_templates"]["missing_evidence_question"]
    fallback = data["fallbacks"]["missing_evidence"]
    missing_text = ", ".join(missing_evidence[:2]) if missing_evidence else fallback
    return template.format(pathology_code=pathology_code, missing_evidence=missing_text)


__all__ = [
    "EVIDENCE_REQUIREMENT_COPY_CONTRACT_PATH",
    "EvidenceRequirementCopyContractError",
    "build_missing_evidence_question",
    "load_evidence_requirement_copy_contract",
    "validate_evidence_requirement_copy_contract",
]

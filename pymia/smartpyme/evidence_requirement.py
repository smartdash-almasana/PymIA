"""Evidence requirement contract for SmartPyme.

Pure contract module. It does NOT persist or execute runtime actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class EvidenceRequirement:
    requirement_id: str
    tenant_id: str
    intake_id: str
    hypothesis_id: str
    evidence_type: str
    description: str
    required_fields: list[str]
    reason: str
    blocks_analysis: bool
    priority: int
    telegram_message: str
    enables_classification: str | None = None
    source_tank: str | None = None
    formula_id: str | None = None
    formula_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_evidence_requirement(
    *,
    requirement_id: str,
    tenant_id: str,
    intake_id: str,
    hypothesis_id: str,
    evidence_type: str,
    description: str,
    required_fields: list[str],
    reason: str,
    blocks_analysis: bool,
    priority: int,
    telegram_message: str,
    enables_classification: str | None = None,
    source_tank: str | None = None,
    formula_id: str | None = None,
    formula_ids: list[str] | None = None,
) -> EvidenceRequirement:
    """Create a validated evidence requirement contract.

    Does NOT persist data or invoke kernel logic.
    """
    required_text_fields = {
        "requirement_id": requirement_id,
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "hypothesis_id": hypothesis_id,
        "evidence_type": evidence_type,
        "description": description,
        "reason": reason,
        "telegram_message": telegram_message,
    }
    for name, value in required_text_fields.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    if not isinstance(required_fields, list):
        raise ValueError("required_fields must be a list")
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ValueError("priority must be an int")
    if priority < 1 or priority > 3:
        raise ValueError("priority must be between 1 and 3")

    normalized_formula_ids = list(dict.fromkeys(
        value.strip()
        for value in ([formula_id] if formula_id else []) + list(formula_ids or [])
        if isinstance(value, str) and value.strip()
    ))

    return EvidenceRequirement(
        requirement_id=requirement_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        hypothesis_id=hypothesis_id,
        evidence_type=evidence_type,
        description=description,
        required_fields=list(required_fields),
        reason=reason,
        blocks_analysis=bool(blocks_analysis),
        priority=priority,
        telegram_message=telegram_message,
        enables_classification=enables_classification,
        source_tank=source_tank,
        formula_id=normalized_formula_ids[0] if normalized_formula_ids else None,
        formula_ids=normalized_formula_ids,
    )


__all__ = [
    "EvidenceRequirement",
    "create_evidence_requirement",
]

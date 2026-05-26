"""Operational hypothesis contract for SmartPyme.

Pure model helpers. It does NOT persist or execute analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HypothesisStatus(str, Enum):
    ABIERTA = "ABIERTA"
    EN_CONTRASTE = "EN_CONTRASTE"
    CONFIRMADA = "CONFIRMADA"
    DESCARTADA = "DESCARTADA"
    EVIDENCIA_INSUFICIENTE = "EVIDENCIA_INSUFICIENTE"


@dataclass
class OperationalHypothesis:
    hypothesis_id: str
    tenant_id: str
    intake_id: str
    formulation: str
    source: str
    domain: str
    related_symptoms: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.ABIERTA
    findings_refs: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    closed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_hypothesis(
    *,
    hypothesis_id: str,
    tenant_id: str,
    intake_id: str,
    formulation: str,
    source: str,
    domain: str,
    related_symptoms: list[str] | None = None,
    required_evidence: list[str] | None = None,
) -> OperationalHypothesis:
    """Create an operational hypothesis contract object.

    Does NOT execute any kernel logic.
    """
    for name, value in {
        "hypothesis_id": hypothesis_id,
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "formulation": formulation,
        "source": source,
        "domain": domain,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    return OperationalHypothesis(
        hypothesis_id=hypothesis_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        formulation=formulation,
        source=source,
        domain=domain,
        related_symptoms=list(related_symptoms or []),
        required_evidence=list(required_evidence or []),
    )


def update_hypothesis_status(
    hypothesis: OperationalHypothesis,
    new_status: HypothesisStatus | str,
    *,
    closed_at: str | None = None,
) -> OperationalHypothesis:
    """Return a new hypothesis with updated status.

    Does NOT mutate the input hypothesis.
    """
    if not isinstance(hypothesis, OperationalHypothesis):
        raise ValueError("hypothesis must be OperationalHypothesis")

    if isinstance(new_status, str):
        try:
            new_status = HypothesisStatus(new_status)
        except ValueError as exc:
            raise ValueError(f"invalid new_status: {new_status!r}") from exc

    if closed_at is None and new_status in {
        HypothesisStatus.CONFIRMADA,
        HypothesisStatus.DESCARTADA,
        HypothesisStatus.EVIDENCIA_INSUFICIENTE,
    }:
        closed_at = datetime.now(timezone.utc).isoformat()

    return replace(hypothesis, status=new_status, closed_at=closed_at)


__all__ = [
    "HypothesisStatus",
    "OperationalHypothesis",
    "create_hypothesis",
    "update_hypothesis_status",
]

"""Anamnesis readiness gate for SmartPyme.

Pure deterministic gate. It does NOT persist, execute analysis, or call Hermes.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pymia.smartpyme.interrogation import InterrogationResult, SYMPTOM_DESCONOCIDO
from pymia.smartpyme.taxonomy import BusinessTaxonomySnapshot, TAXONOMY_READY_THRESHOLD


class ReadinessStatus(str, Enum):
    READY = "READY"
    NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
    BLOCKED = "BLOCKED"


@dataclass
class AnamnesisReadiness:
    tenant_id: str
    anamnesis_id: str
    status: ReadinessStatus
    taxonomy_complete: bool
    narrative_sufficient: bool
    blocking_reasons: list[str] = field(default_factory=list)
    missing_taxonomy_fields: list[str] = field(default_factory=list)
    open_hypotheses_count: int = 0
    pending_evidence_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_interrogation_dict(interrogation_result: InterrogationResult | dict[str, Any]) -> dict[str, Any]:
    if isinstance(interrogation_result, dict):
        return dict(interrogation_result)
    if isinstance(interrogation_result, InterrogationResult):
        return interrogation_result.to_dict()
    if hasattr(interrogation_result, "to_dict") and callable(interrogation_result.to_dict):
        result = interrogation_result.to_dict()
        if not isinstance(result, dict):
            raise ValueError("interrogation_result.to_dict() must return dict")
        return dict(result)
    raise ValueError("interrogation_result must be dict or InterrogationResult")


def evaluate_anamnesis_readiness(
    snapshot: BusinessTaxonomySnapshot,
    interrogation_result: InterrogationResult | dict[str, Any],
) -> AnamnesisReadiness:
    """Evaluate whether anamnesis is ready to proceed.

    Does NOT execute kernel analysis.
    """
    try:
        if not isinstance(snapshot, BusinessTaxonomySnapshot):
            raise ValueError("snapshot must be BusinessTaxonomySnapshot")
        ir = _as_interrogation_dict(interrogation_result)

        candidate_symptoms = list(ir.get("candidate_symptoms") or [])
        taxonomy_complete = float(snapshot.confidence) >= TAXONOMY_READY_THRESHOLD

        required_fields = [
            "organism_type",
            "operational_flow_stages",
            "sales_channels",
            "systems_available",
        ]
        missing_taxonomy_fields: list[str] = []
        for field_name in required_fields:
            value = getattr(snapshot, field_name)
            if isinstance(value, list):
                if len(value) == 0:
                    missing_taxonomy_fields.append(field_name)
            else:
                if value in (None, ""):
                    missing_taxonomy_fields.append(field_name)

        if len(candidate_symptoms) == 0:
            return AnamnesisReadiness(
                tenant_id=snapshot.tenant_id,
                anamnesis_id="anamnesis_pending",
                status=ReadinessStatus.NEEDS_MORE_INFO,
                taxonomy_complete=taxonomy_complete,
                narrative_sufficient=False,
                blocking_reasons=[],
                missing_taxonomy_fields=missing_taxonomy_fields,
            )

        narrative_sufficient = not (
            len(candidate_symptoms) == 1 and str(candidate_symptoms[0]) == SYMPTOM_DESCONOCIDO
        )

        if taxonomy_complete and narrative_sufficient and not missing_taxonomy_fields:
            return AnamnesisReadiness(
                tenant_id=snapshot.tenant_id,
                anamnesis_id="anamnesis_ready",
                status=ReadinessStatus.READY,
                taxonomy_complete=True,
                narrative_sufficient=True,
                blocking_reasons=[],
                missing_taxonomy_fields=[],
            )

        return AnamnesisReadiness(
            tenant_id=snapshot.tenant_id,
            anamnesis_id="anamnesis_needs_info",
            status=ReadinessStatus.NEEDS_MORE_INFO,
            taxonomy_complete=taxonomy_complete,
            narrative_sufficient=narrative_sufficient,
            blocking_reasons=[],
            missing_taxonomy_fields=missing_taxonomy_fields,
        )
    except ValueError as exc:
        return AnamnesisReadiness(
            tenant_id=getattr(snapshot, "tenant_id", "unknown") if snapshot is not None else "unknown",
            anamnesis_id="anamnesis_blocked",
            status=ReadinessStatus.BLOCKED,
            taxonomy_complete=False,
            narrative_sufficient=False,
            blocking_reasons=[str(exc)],
            missing_taxonomy_fields=[],
        )


__all__ = [
    "ReadinessStatus",
    "AnamnesisReadiness",
    "evaluate_anamnesis_readiness",
]

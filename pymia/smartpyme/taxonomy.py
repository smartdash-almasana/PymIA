"""Business taxonomy snapshot contract for SmartPyme.

Pure contract module. It does NOT persist, execute analysis, or call Hermes.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


TAXONOMY_READY_THRESHOLD = 0.7


class TaxonomyType(str, Enum):
    comercio = "comercio"
    servicios = "servicios"
    produccion_fabrica = "produccion_fabrica"
    distribucion = "distribucion"
    gastronomia = "gastronomia"
    textil = "textil"
    salud_estetica = "salud_estetica"
    profesional = "profesional"
    mixto = "mixto"


@dataclass
class BusinessTaxonomySnapshot:
    """Snapshot of business taxonomy captured during conversational anamnesis."""

    tenant_id: str
    organism_type: TaxonomyType
    industry: str
    size: str
    complexity: str
    sales_channels: list[str] = field(default_factory=list)
    operational_flow_stages: list[str] = field(default_factory=list)
    areas_present: list[str] = field(default_factory=list)
    systems_available: list[str] = field(default_factory=list)
    jurisdiction: str = ""
    currency: str = ""
    confidence: float = 0.0
    source: str = "conversational_anamnesis"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_taxonomy_snapshot(
    *,
    tenant_id: str,
    organism_type: TaxonomyType | str,
    industry: str,
    size: str,
    complexity: str,
    sales_channels: list[str] | None = None,
    operational_flow_stages: list[str] | None = None,
    areas_present: list[str] | None = None,
    systems_available: list[str] | None = None,
    jurisdiction: str = "",
    currency: str = "",
    confidence: float = 0.0,
    source: str = "conversational_anamnesis",
) -> BusinessTaxonomySnapshot:
    """Create a validated business taxonomy snapshot.

    Does NOT persist or execute any kernel logic.
    """
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id must be a non-empty string")
    if not (0.0 <= float(confidence) <= 1.0):
        raise ValueError("confidence must be between 0.0 and 1.0")
    if isinstance(organism_type, str):
        try:
            organism_type = TaxonomyType(organism_type)
        except ValueError as exc:
            raise ValueError(f"invalid organism_type: {organism_type!r}") from exc

    return BusinessTaxonomySnapshot(
        tenant_id=tenant_id.strip(),
        organism_type=organism_type,
        industry=str(industry),
        size=str(size),
        complexity=str(complexity),
        sales_channels=list(sales_channels or []),
        operational_flow_stages=list(operational_flow_stages or []),
        areas_present=list(areas_present or []),
        systems_available=list(systems_available or []),
        jurisdiction=str(jurisdiction),
        currency=str(currency),
        confidence=float(confidence),
        source=str(source),
    )


def confirm_field(
    snapshot: BusinessTaxonomySnapshot,
    field_name: str,
    confirmed_value: Any,
    *,
    increment: float = 0.1,
) -> BusinessTaxonomySnapshot:
    """Return a new snapshot with one confirmed field and increased confidence.

    Does NOT mutate the input snapshot.
    """
    if not isinstance(snapshot, BusinessTaxonomySnapshot):
        raise ValueError("snapshot must be BusinessTaxonomySnapshot")
    if not isinstance(field_name, str) or not field_name.strip():
        raise ValueError("field_name must be a non-empty string")
    if field_name not in snapshot.to_dict():
        raise ValueError(f"unknown field_name: {field_name}")
    if field_name in {"created_at", "tenant_id"}:
        raise ValueError(f"field {field_name!r} is not confirmable")

    value = confirmed_value
    if field_name == "organism_type":
        if isinstance(value, str):
            try:
                value = TaxonomyType(value)
            except ValueError as exc:
                raise ValueError(f"invalid organism_type: {value!r}") from exc
        elif not isinstance(value, TaxonomyType):
            raise ValueError("organism_type must be TaxonomyType or valid str")

    if not isinstance(increment, (int, float)):
        raise ValueError("increment must be numeric")
    if increment < 0:
        raise ValueError("increment must be >= 0")

    updated = replace(snapshot, **{field_name: value})
    updated.confidence = min(1.0, float(snapshot.confidence) + float(increment))
    return updated


__all__ = [
    "TAXONOMY_READY_THRESHOLD",
    "TaxonomyType",
    "BusinessTaxonomySnapshot",
    "create_taxonomy_snapshot",
    "confirm_field",
]

"""Contrato mínimo para lifecycle de taxonomía preliminar SmartPyme.

Este módulo no diagnostica, no confirma taxonomía y no habilita ejecución.
Solo modela señales preliminares capturadas antes de la confirmación del dueño.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PreliminaryTaxonomyStatus(str, Enum):
    PRELIMINARY = "PRELIMINARY"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


@dataclass(frozen=True)
class PreliminaryTaxonomySignal:
    tenant_id: str
    source: str
    status: PreliminaryTaxonomyStatus
    organism_type: str | None
    sales_channels: tuple[str, ...]
    confidence: float
    created_from: str

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, str) or not self.tenant_id.strip():
            raise ValueError("tenant_id obligatorio")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source obligatorio")
        if not isinstance(self.created_from, str) or not self.created_from.strip():
            raise ValueError("created_from obligatorio")
        if not isinstance(self.status, PreliminaryTaxonomyStatus):
            raise ValueError("status inválido")
        if not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence inválida")
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("confidence fuera de rango")
        if self.status is PreliminaryTaxonomyStatus.PRELIMINARY and self.confidence >= 1.0:
            raise ValueError("PRELIMINARY exige confidence < 1.0")
        if not isinstance(self.sales_channels, tuple):
            raise ValueError("sales_channels debe ser tuple")

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "source": self.source,
            "status": self.status.value,
            "organism_type": self.organism_type,
            "sales_channels": list(self.sales_channels),
            "confidence": float(self.confidence),
            "created_from": self.created_from,
        }

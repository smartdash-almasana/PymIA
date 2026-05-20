from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


EvidenceSource = Literal["xlsx_upload", "csv_upload", "pdf_upload", "manual_entry", "unknown"]


class EvidenceTable(BaseModel):
    """Tabla extraída de una evidencia documental.

    Este contrato transporta estructura. No diagnostica.
    """

    sheet_name: str = Field(..., description="Nombre de hoja o tabla de origen.")
    columns: list[str] = Field(default_factory=list, description="Columnas detectadas.")
    rows: list[list[Any]] = Field(default_factory=list, description="Filas extraídas.")


class StructuredEvidence(BaseModel):
    """Evidencia estructurada recibida desde Hermes/conversa-engine.

    Boundary: Hermes puede parsear documentos y poblar este contrato.
    PymIA puede contrastar variables, pero no debe depender de texto narrativo
    para reconocer evidencia ya recibida.
    """

    tenant_id: str = Field(..., description="Identificador del tenant asociado a la evidencia.")
    document_type: str = Field(..., description="Tipo documental curado usado para routing clinico-operacional.")
    source: EvidenceSource = Field(default="unknown")
    file_name: str | None = None
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO UTC de extracción.",
    )
    tables: list[EvidenceTable] = Field(default_factory=list)
    computed_variables: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def has_variable(self, key: str) -> bool:
        return key in self.computed_variables

    def get_number(self, key: str) -> float | None:
        value = self.computed_variables.get(key)
        if value is None:
            return None
        return float(value)

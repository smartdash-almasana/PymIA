from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class IngestionRoute(StrEnum):
    BEM_AI = "bem_ai"
    INTERNAL_FACT = "internal"
    NARRATIVE = "narrative"


@dataclass(frozen=True)
class EvidenceTriage:
    evidence_id: str
    file_extension: str
    mime_type: str
    expected_schema: str
    entropy_level: float

    def get_route(self) -> IngestionRoute:
        mime = self.mime_type.lower().strip()
        ext = self.file_extension.lower().strip()
        schema = self.expected_schema.lower().strip()

        if mime in {"application/pdf", "image/jpeg", "image/png"}:
            return IngestionRoute.BEM_AI

        if ext in {".xlsx", ".xls", ".csv"} and self.entropy_level > 0.3:
            return IngestionRoute.BEM_AI

        if schema == "human_claim":
            return IngestionRoute.NARRATIVE

        return IngestionRoute.INTERNAL_FACT


def route_evidence(
    *,
    evidence_id: str,
    file_extension: str,
    mime_type: str,
    expected_schema: str,
    entropy_level: float,
) -> IngestionRoute:
    return EvidenceTriage(
        evidence_id=evidence_id,
        file_extension=file_extension,
        mime_type=mime_type,
        expected_schema=expected_schema,
        entropy_level=entropy_level,
    ).get_route()

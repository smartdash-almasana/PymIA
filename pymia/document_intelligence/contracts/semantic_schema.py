"""Semantic schema contracts produced by document intelligence."""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from .field_binding import FieldBinding


class EvidenceQuality(str, Enum):
    """Quality of evidence supporting inferred schema semantics."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class SemanticSchema(BaseModel):
    """Schema-level semantic inference with global confidence metadata."""

    table_name: str = Field(min_length=1)
    bindings: List[FieldBinding] = Field(default_factory=list)
    global_confidence: float = Field(ge=0.0, le=1.0)
    evidence_quality: EvidenceQuality

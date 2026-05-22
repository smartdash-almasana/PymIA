"""Field-level mapping contracts for inferred semantic bindings."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ColumnRole(str, Enum):
    """Role of a source column in business semantics."""

    DIMENSION = "dimension"
    METRIC = "metric"
    IDENTIFIER = "identifier"
    DATE = "date"
    UNKNOWN = "unknown"


class BusinessVariable(str, Enum):
    """Canonical business variable targeted by a mapping."""

    REVENUE = "revenue"
    COST = "cost"
    MARGIN = "margin"
    QUANTITY = "quantity"
    UNIT_PRICE = "unit_price"
    UNKNOWN = "unknown"


class AmbiguityStatus(str, Enum):
    """Ambiguity status for an inferred field mapping."""

    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class ConfidenceScore(BaseModel):
    """Normalized confidence value for inference decisions."""

    value: float = Field(ge=0.0, le=1.0)
    reason: str = Field(default="", description="Short explanation for confidence level.")


class FieldBinding(BaseModel):
    """Binding between a source column and canonical business variable."""

    source_column: str = Field(min_length=1)
    target_variable: BusinessVariable
    column_role: ColumnRole
    confidence: ConfidenceScore
    ambiguity_status: AmbiguityStatus

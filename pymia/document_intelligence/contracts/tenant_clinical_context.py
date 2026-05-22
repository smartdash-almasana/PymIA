"""Business context contracts used by document intelligence inference."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BusinessIdentity(BaseModel):
    """Identity and operational metadata for the tenant business."""

    tenant_id: str = Field(min_length=1)
    business_name: str = Field(min_length=1)
    industry: str = Field(min_length=1)


class OperationalProfile(BaseModel):
    """Operational profile with basic process and scale indicators."""

    business_unit: str = Field(min_length=1)
    operation_model: str = Field(min_length=1)
    monthly_document_volume: Optional[int] = Field(default=None, ge=0)


class ActivePathology(BaseModel):
    """Active business pathology that can influence schema interpretation."""

    code: str = Field(min_length=1)
    severity: Optional[str] = None


class ClinicalHypothesis(BaseModel):
    """Hypothesis describing likely structural issues in business data."""

    statement: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class FormulaContext(BaseModel):
    """Formula metadata used as a future hook for consistency checks."""

    formula_ids: List[str] = Field(default_factory=list)
    constraints: Dict[str, str] = Field(default_factory=dict)


class EvidencePlan(BaseModel):
    """Plan indicating which evidence is required for inference confidence."""

    required_tables: List[str] = Field(default_factory=list)
    required_columns: List[str] = Field(default_factory=list)


class TenantVocabulary(BaseModel):
    """Tenant-specific aliases for semantic matching of columns."""

    aliases: Dict[str, List[str]] = Field(default_factory=dict)


class HistoricalColumnMapping(BaseModel):
    """Historical mappings to improve continuity across document versions."""

    source_column: str = Field(min_length=1)
    target_variable: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class ContextConfidencePolicy(BaseModel):
    """Confidence thresholds for context-aware inference decisions."""

    minimum_global_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    minimum_field_confidence: float = Field(default=0.4, ge=0.0, le=1.0)


class TenantClinicalContext(BaseModel):
    """Aggregate tenant context required for schema inference viability."""

    business_identity: BusinessIdentity
    operational_profile: Optional[OperationalProfile] = None
    active_pathologies: List[ActivePathology] = Field(default_factory=list)
    clinical_hypotheses: List[ClinicalHypothesis] = Field(default_factory=list)
    formula_context: Optional[FormulaContext] = None
    evidence_plan: Optional[EvidencePlan] = None
    tenant_vocabulary: Optional[TenantVocabulary] = None
    historical_column_mappings: List[HistoricalColumnMapping] = Field(default_factory=list)
    confidence_policy: ContextConfidencePolicy = Field(default_factory=ContextConfidencePolicy)

    def has_minimum_context(self) -> bool:
        """Return True when mandatory business identity context is present."""
        return bool(
            self.business_identity.tenant_id
            and self.business_identity.business_name
            and self.business_identity.industry
        )

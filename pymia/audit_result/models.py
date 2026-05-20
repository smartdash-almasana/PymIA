from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, model_validator


AuditStatus = Literal["partial", "complete", "blocked"]
ConfidenceLevel = Literal["high", "medium", "low"]
PriorityLevel = Literal["critical", "high", "medium", "low"]
ThreadStatus = Literal["open", "closed", "paused"]


class DocumentRef(BaseModel):
    name: str
    type: str
    sheets: list[str] = Field(default_factory=list)


class PeriodAnalyzed(BaseModel):
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")
    granularity: str = "monthly"


class BusinessContext(BaseModel):
    business_type: str = "unknown"
    period_analyzed: PeriodAnalyzed
    documents_used: list[DocumentRef] = Field(default_factory=list)


class TaxonomyDimension(BaseModel):
    key: str
    value: str
    source: Literal["anamnesis", "evidence", "inference"] = "inference"


class SymptomTaxonomyPathologyLink(BaseModel):
    symptom_text: str
    operational_type: str
    candidate_pathology: str
    evidence_required: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class OperationalTaxonomy(BaseModel):
    taxonomy_version: str = "v1"
    dimensions: list[TaxonomyDimension] = Field(default_factory=list)
    triage_level: Literal["sangria", "inestabilidad", "optimizacion"] = "inestabilidad"
    symptom_links: list[SymptomTaxonomyPathologyLink] = Field(default_factory=list)


class ComputedMetric(BaseModel):
    metric_id: str
    name: str
    value: float
    unit: str = "ARS"
    period: str
    formula_id: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "medium"


class Impact(BaseModel):
    type: str
    description: str
    estimated_amount: float | None = None
    unit: str = "ARS"


class Risk(BaseModel):
    description: str
    time_horizon: str = "short_term"


class SuggestedAction(BaseModel):
    action_id: str
    description: str
    timeframe: str = "7_days"
    source: str = "signal"
    evidence_ids: list[str] = Field(default_factory=list)


class NextAuditQuestion(BaseModel):
    question_id: str
    question: str
    reason: str
    requires_data: list[str] = Field(default_factory=list)
    priority: PriorityLevel = "medium"


class PathologyFindingResult(BaseModel):
    finding_id: str
    pathology_code: str
    pathology_name: str
    formula_id: str
    status: Literal["calculable", "candidate", "pending_data", "blocked", "not_applicable"] = "pending_data"
    severity: PriorityLevel
    summary: str
    available_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    matched_sources: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    required_variables: list[str] = Field(default_factory=list)
    impact: Impact
    risk: Risk
    evidence_ids: list[str] = Field(default_factory=list)
    related_metrics: list[str] = Field(default_factory=list)
    suggested_actions: list[SuggestedAction] = Field(default_factory=list)
    next_audit_questions: list[NextAuditQuestion] = Field(default_factory=list)


class OperationalSignal(BaseModel):
    signal_id: str
    signal_type: str
    severity: PriorityLevel
    description: str
    suggested_action: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    linked_pathologies: list[str] = Field(default_factory=list)
    opens_audit_threads: list[str] = Field(default_factory=list)


class PriorityProblem(BaseModel):
    priority: int
    title: str
    severity: PriorityLevel
    why_it_matters: str
    linked_findings: list[str] = Field(default_factory=list)
    linked_pathologies: list[str] = Field(default_factory=list)
    recommended_focus: str


class ExpectedBenefit(BaseModel):
    type: str
    description: str


class OpenAuditThread(BaseModel):
    thread_id: str
    title: str
    status: ThreadStatus = "open"
    opened_by: list[str] = Field(default_factory=list)
    business_question: str
    next_steps: list[str] = Field(default_factory=list)
    required_data: list[str] = Field(default_factory=list)
    expected_benefit: ExpectedBenefit
    priority: PriorityLevel


class ImprovementOpportunity(BaseModel):
    opportunity_id: str
    type: str
    description: str
    linked_threads: list[str] = Field(default_factory=list)
    estimated_benefit: str
    priority: PriorityLevel


class PathologyRoutingSummary(BaseModel):
    pathology_code: str
    status: Literal["calculable", "candidate", "pending_data", "blocked", "not_applicable"]
    category: str
    thread_id: str
    missing_evidence: list[str] = Field(default_factory=list)
    next_question: str


class AllowedMessage(BaseModel):
    message_id: str
    text: str
    evidence_ids: list[str] = Field(default_factory=list)


class NarrativePayload(BaseModel):
    allowed_messages: list[AllowedMessage] = Field(default_factory=list)
    forbidden_inferences: list[str] = Field(default_factory=list)
    tone: str = "dueño_pyme_directo"


class AuditTrail(BaseModel):
    sheet_reports: dict[str, str] = Field(default_factory=dict)
    validation_issues_count: int = 0
    source_evidence_count: int = 0
    grounding_status: Literal["valid", "invalid", "partial"] = "partial"


class OperationalAuditResult(BaseModel):
    audit_id: str
    tenant_id: str
    source_file: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    audit_status: AuditStatus = "partial"
    confidence: ConfidenceLevel = "medium"

    business_context: BusinessContext
    taxonomy: OperationalTaxonomy
    computed_metrics: list[ComputedMetric] = Field(default_factory=list)
    pathology_findings: list[PathologyFindingResult] = Field(default_factory=list)
    operational_signals: list[OperationalSignal] = Field(default_factory=list)
    priority_problems: list[PriorityProblem] = Field(default_factory=list)
    pathology_routing_summary: list[PathologyRoutingSummary] = Field(default_factory=list)
    open_audit_threads: list[OpenAuditThread] = Field(default_factory=list)
    improvement_opportunities: list[ImprovementOpportunity] = Field(default_factory=list)
    narrative_payload: NarrativePayload
    audit_trail: AuditTrail

    @model_validator(mode="after")
    def validate_internal_references(self) -> "OperationalAuditResult":
        signal_ids = {s.signal_id for s in self.operational_signals}
        finding_ids = {f.finding_id for f in self.pathology_findings}
        thread_ids = {t.thread_id for t in self.open_audit_threads}
        known_pathologies = {f.pathology_code for f in self.pathology_findings}

        for metric in self.computed_metrics:
            if not metric.evidence_ids:
                raise ValueError(f"Computed metric without evidence_ids: {metric.metric_id}")

        for link in self.taxonomy.symptom_links:
            if not link.evidence_ids:
                raise ValueError("Taxonomy symptom link without evidence_ids")
            if link.candidate_pathology not in known_pathologies:
                raise ValueError(f"Taxonomy link references unknown pathology: {link.candidate_pathology}")

        for finding in self.pathology_findings:
            if not finding.evidence_ids:
                raise ValueError(f"Pathology finding without evidence_ids: {finding.finding_id}")
            for action in finding.suggested_actions:
                if not action.evidence_ids:
                    raise ValueError(f"Suggested action without evidence_ids: {action.action_id}")

        for signal in self.operational_signals:
            if not signal.evidence_ids:
                raise ValueError(f"Signal without evidence_ids: {signal.signal_id}")

        for message in self.narrative_payload.allowed_messages:
            if not message.evidence_ids:
                raise ValueError(f"Narrative message without evidence_ids: {message.message_id}")

        for thread in self.open_audit_threads:
            if not thread.opened_by:
                raise ValueError(f"Open thread without opened_by refs: {thread.thread_id}")
            for ref in thread.opened_by:
                if ref not in finding_ids and ref not in signal_ids:
                    raise ValueError(f"Thread {thread.thread_id} references unknown opener: {ref}")

        for opp in self.improvement_opportunities:
            for tid in opp.linked_threads:
                if tid not in thread_ids:
                    raise ValueError(f"Opportunity {opp.opportunity_id} references unknown thread: {tid}")

        for route in self.pathology_routing_summary:
            if route.thread_id not in thread_ids:
                raise ValueError(f"Routing summary references unknown thread: {route.thread_id}")

        return self

"""Service 1 — Column Understanding Corpus Report V1.

Pure observational report derived from the corpus evaluation result.
No I/O, no frontend wiring, no orchestrator, no runtime authorization.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1 import (
    OUTCOME_EXACT_MATCH,
    OUTCOME_FALSE_CONFIDENT,
    OUTCOME_MISSED_QUESTION,
    OUTCOME_SAFE_QUESTION,
    OUTCOME_SAFE_UNKNOWN,
    Service1ColumnUnderstandingCorpusEvaluationV1,
    evaluate_service_1_column_understanding_corpus_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_CORPUS_REPORT_V1"
STATUS_READY: Final[str] = "CORPUS_REPORT_READY"
PRIORITY_CRITICAL: Final[str] = "CRITICAL"
PRIORITY_HIGH: Final[str] = "HIGH"
PRIORITY_MEDIUM: Final[str] = "MEDIUM"


@dataclass(frozen=True)
class Service1ColumnUnderstandingCorpusReportFindingV1:
    case_id: str
    column_name: str
    outcome: str
    expected_semantic_role: str
    predicted_semantic_role: str
    confidence: float
    dangerous_if_wrong: bool
    priority: str
    recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnUnderstandingCorpusReportV1:
    schema_version: str
    status: str
    evaluation_verdict: str
    frontend_wiring_allowed: bool
    cases_count: int
    columns_count: int
    exact_matches: int
    safe_questions: int
    safe_unknowns: int
    false_confident: int
    missed_questions: int
    dangerous_errors: int
    exact_match_rate: float
    safe_resolution_rate: float
    findings: tuple[Service1ColumnUnderstandingCorpusReportFindingV1, ...]
    critical_columns: tuple[str, ...]
    recommended_next_slice: str
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_column_understanding_corpus_report_v1(
    evaluation: Service1ColumnUnderstandingCorpusEvaluationV1 | None = None,
) -> Service1ColumnUnderstandingCorpusReportV1:
    source = evaluation or evaluate_service_1_column_understanding_corpus_v1()
    findings = tuple(
        _build_finding(row)
        for row in source.rows
        if row.outcome != OUTCOME_EXACT_MATCH
    )
    critical_columns = tuple(
        f"{finding.case_id}:{finding.column_name}"
        for finding in findings
        if finding.priority == PRIORITY_CRITICAL
    )
    frontend_wiring_allowed = bool(source.metadata.get("frontend_wiring_allowed", False))
    next_slice = (
        "SERVICE_1_COLUMN_UNDERSTANDING_OWNER_QUESTION_ADAPTER_V1"
        if frontend_wiring_allowed
        else "SERVICE_1_COLUMN_UNDERSTANDING_RULE_EXPANSION_V1"
    )
    return Service1ColumnUnderstandingCorpusReportV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        evaluation_verdict=source.verdict,
        frontend_wiring_allowed=frontend_wiring_allowed,
        cases_count=source.cases_count,
        columns_count=source.columns_count,
        exact_matches=source.exact_matches,
        safe_questions=source.safe_questions,
        safe_unknowns=source.safe_unknowns,
        false_confident=source.false_confident,
        missed_questions=source.missed_questions,
        dangerous_errors=source.dangerous_errors,
        exact_match_rate=source.exact_match_rate,
        safe_resolution_rate=source.safe_resolution_rate,
        findings=findings,
        critical_columns=critical_columns,
        recommended_next_slice=next_slice,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "source_schema_version": source.schema_version,
            "observational_only": True,
            "report_policy": "derive_only_from_corpus_evaluation",
            "supported_scope_columns_count": source.metadata.get("supported_scope_columns_count"),
            "supported_scope_exact_matches": source.metadata.get("supported_scope_exact_matches"),
            "supported_scope_exact_match_rate": source.metadata.get("supported_scope_exact_match_rate"),
            "direct_resolution_coverage": source.metadata.get("direct_resolution_coverage"),
            "intentional_unknown_columns_count": source.metadata.get("intentional_unknown_columns_count"),
        },
    )


def _build_finding(row: Any) -> Service1ColumnUnderstandingCorpusReportFindingV1:
    if row.outcome in {OUTCOME_FALSE_CONFIDENT, OUTCOME_MISSED_QUESTION} and row.dangerous_if_wrong:
        priority = PRIORITY_CRITICAL
        action = "Add a fail-closed ambiguity rule before any frontend wiring."
    elif row.outcome in {OUTCOME_FALSE_CONFIDENT, OUTCOME_MISSED_QUESTION}:
        priority = PRIORITY_HIGH
        action = "Require an owner question before accepting the semantic hypothesis."
    elif row.outcome == OUTCOME_SAFE_QUESTION:
        priority = PRIORITY_MEDIUM
        action = "Keep owner confirmation and improve the offered alternatives."
    elif row.outcome == OUTCOME_SAFE_UNKNOWN:
        priority = PRIORITY_MEDIUM
        action = "Keep unknown until domain evidence supports a new rule."
    else:
        priority = PRIORITY_HIGH
        action = "Review the evaluation classification."
    return Service1ColumnUnderstandingCorpusReportFindingV1(
        case_id=row.case_id,
        column_name=row.column_name,
        outcome=row.outcome,
        expected_semantic_role=row.expected_semantic_role,
        predicted_semantic_role=row.predicted_semantic_role,
        confidence=row.confidence,
        dangerous_if_wrong=row.dangerous_if_wrong,
        priority=priority,
        recommended_action=action,
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "PRIORITY_CRITICAL",
    "PRIORITY_HIGH",
    "PRIORITY_MEDIUM",
    "Service1ColumnUnderstandingCorpusReportFindingV1",
    "Service1ColumnUnderstandingCorpusReportV1",
    "build_service_1_column_understanding_corpus_report_v1",
]

"""Service 1 — Owner Question Corpus Audit V1.

Pure observational audit of owner-facing question views generated from the
column-understanding corpus. No I/O, no frontend wiring, no orchestration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1 import (
    build_default_service_1_column_understanding_corpus_v1,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understandings_from_matrix_v1,
)
from pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1 import (
    build_service_1_column_owner_question_views_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_OWNER_QUESTION_CORPUS_AUDIT_V1"
STATUS_READY: Final[str] = "OWNER_QUESTION_CORPUS_AUDIT_READY"
VERDICT_PASS: Final[str] = "PASS"
VERDICT_NEEDS_FIXES: Final[str] = "NEEDS_FIXES"

_FORBIDDEN_JARGON: Final[tuple[str, ...]] = (
    "rol semantico",
    "semantic role",
    "variable_name",
    "primary_hypothesis",
    "candidate_meanings",
)


@dataclass(frozen=True)
class Service1OwnerQuestionCorpusAuditFindingV1:
    case_id: str
    column_name: str
    issue_code: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1OwnerQuestionCorpusAuditV1:
    schema_version: str
    status: str
    verdict: str
    cases_count: int
    question_views_count: int
    covered_question_views: int
    findings: tuple[Service1OwnerQuestionCorpusAuditFindingV1, ...]
    missing_other_option: int
    missing_risk_note: int
    empty_question: int
    duplicate_option_labels: int
    jargon_hits: int
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def audit_service_1_column_understanding_owner_questions_v1() -> Service1OwnerQuestionCorpusAuditV1:
    findings: list[Service1OwnerQuestionCorpusAuditFindingV1] = []
    question_views_count = 0
    covered_question_views = 0
    cases = build_default_service_1_column_understanding_corpus_v1()

    for case in cases:
        understandings = build_column_understandings_from_matrix_v1(case.to_matrix())
        views = build_service_1_column_owner_question_views_v1(understandings)
        for view in views:
            if not view.question_required:
                continue
            question_views_count += 1
            issue_count_before = len(findings)

            if not view.question or not view.question.strip():
                findings.append(_finding(case.case_id, view.column_name, "EMPTY_QUESTION", "Question text is empty."))
            if not view.risk_note or not view.risk_note.strip():
                findings.append(_finding(case.case_id, view.column_name, "MISSING_RISK_NOTE", "Risk note is missing."))
            if not any(option.option_id == "OTHER" for option in view.options):
                findings.append(_finding(case.case_id, view.column_name, "MISSING_OTHER_OPTION", "Owner cannot choose another meaning."))

            labels = [option.label.strip().casefold() for option in view.options]
            if len(labels) != len(set(labels)):
                findings.append(_finding(case.case_id, view.column_name, "DUPLICATE_OPTION_LABEL", "Option labels are duplicated."))

            rendered = " ".join(
                [view.title, view.context, view.question or "", view.risk_note or ""]
                + [f"{option.label} {option.description}" for option in view.options]
            ).casefold()
            for token in _FORBIDDEN_JARGON:
                if token in rendered:
                    findings.append(_finding(case.case_id, view.column_name, "JARGON_HIT", f"Forbidden jargon found: {token}"))

            if len(findings) == issue_count_before:
                covered_question_views += 1

    counts = {
        "MISSING_OTHER_OPTION": 0,
        "MISSING_RISK_NOTE": 0,
        "EMPTY_QUESTION": 0,
        "DUPLICATE_OPTION_LABEL": 0,
        "JARGON_HIT": 0,
    }
    for finding in findings:
        counts[finding.issue_code] += 1

    verdict = VERDICT_PASS if not findings else VERDICT_NEEDS_FIXES
    return Service1OwnerQuestionCorpusAuditV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        verdict=verdict,
        cases_count=len(cases),
        question_views_count=question_views_count,
        covered_question_views=covered_question_views,
        findings=tuple(findings),
        missing_other_option=counts["MISSING_OTHER_OPTION"],
        missing_risk_note=counts["MISSING_RISK_NOTE"],
        empty_question=counts["EMPTY_QUESTION"],
        duplicate_option_labels=counts["DUPLICATE_OPTION_LABEL"],
        jargon_hits=counts["JARGON_HIT"],
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "observational_only": True,
            "audit_policy": "structural_owner_question_quality",
        },
    )


def _finding(case_id: str, column_name: str, issue_code: str, detail: str) -> Service1OwnerQuestionCorpusAuditFindingV1:
    return Service1OwnerQuestionCorpusAuditFindingV1(
        case_id=case_id,
        column_name=column_name,
        issue_code=issue_code,
        detail=detail,
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "VERDICT_PASS",
    "VERDICT_NEEDS_FIXES",
    "Service1OwnerQuestionCorpusAuditFindingV1",
    "Service1OwnerQuestionCorpusAuditV1",
    "audit_service_1_column_understanding_owner_questions_v1",
]

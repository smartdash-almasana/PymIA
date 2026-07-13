"""Service 1 — Owner Question Semantic Audit V1.

Pure observational audit of semantic alignment between corpus column headers
and owner-facing answer options. It does not define business meanings, mutate
the engine, wire frontend code, or authorize runtime/delivery.
"""

from __future__ import annotations

import re
import unicodedata
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

SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_OWNER_QUESTION_SEMANTIC_AUDIT_V1"
STATUS_READY: Final[str] = "OWNER_QUESTION_SEMANTIC_AUDIT_READY"
VERDICT_PASS: Final[str] = "PASS"
VERDICT_NEEDS_FIXES: Final[str] = "NEEDS_FIXES"
ISSUE_NO_SEMANTIC_ALIGNMENT: Final[str] = "NO_SEMANTIC_ALIGNMENT"

_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")
_STOPWORDS: Final[frozenset[str]] = frozenset(
    {
        "a", "al", "algo", "como", "con", "cosa", "de", "del", "el", "en",
        "esta", "este", "indica", "la", "las", "lo", "los", "o", "otra",
        "final", "inicial", "medio", "por", "que", "se", "un", "una", "y",
    }
)
# Short opaque headers do not contain enough lexical evidence for this audit.
_OPAQUE_HEADERS: Final[frozenset[str]] = frozenset({"x1", "ref", "obs"})


@dataclass(frozen=True)
class Service1OwnerQuestionSemanticAuditFindingV1:
    case_id: str
    column_name: str
    issue_code: str
    header_tokens: tuple[str, ...]
    option_tokens: tuple[str, ...]
    option_labels: tuple[str, ...]
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1OwnerQuestionSemanticAuditV1:
    schema_version: str
    status: str
    verdict: str
    question_views_count: int
    auditable_views_count: int
    aligned_views_count: int
    unaligned_views_count: int
    findings: tuple[Service1OwnerQuestionSemanticAuditFindingV1, ...]
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def audit_service_1_column_understanding_owner_question_semantics_v1() -> Service1OwnerQuestionSemanticAuditV1:
    findings: list[Service1OwnerQuestionSemanticAuditFindingV1] = []
    question_views_count = 0
    auditable_views_count = 0
    aligned_views_count = 0

    for case in build_default_service_1_column_understanding_corpus_v1():
        understandings = build_column_understandings_from_matrix_v1(case.to_matrix())
        views = build_service_1_column_owner_question_views_v1(understandings)
        for view in views:
            if not view.question_required:
                continue
            question_views_count += 1
            normalized_header = _normalize(view.source_normalized_header)
            if normalized_header in _OPAQUE_HEADERS:
                continue
            header_tokens = _tokens(normalized_header)
            if not header_tokens:
                continue
            auditable_views_count += 1

            semantic_options = tuple(option for option in view.options if option.option_id != "OTHER")
            option_labels = tuple(option.label for option in semantic_options)
            option_tokens = _tokens(
                " ".join(
                    f"{option.label} {option.description}"
                    for option in semantic_options
                )
            )
            if set(header_tokens).intersection(option_tokens):
                aligned_views_count += 1
                continue

            findings.append(
                Service1OwnerQuestionSemanticAuditFindingV1(
                    case_id=case.case_id,
                    column_name=view.column_name,
                    issue_code=ISSUE_NO_SEMANTIC_ALIGNMENT,
                    header_tokens=header_tokens,
                    option_tokens=option_tokens,
                    option_labels=option_labels,
                    detail=(
                        "No owner option shares a meaningful lexical signal with the "
                        "column header; alternatives may be generic or misleading."
                    ),
                )
            )

    verdict = VERDICT_PASS if not findings else VERDICT_NEEDS_FIXES
    return Service1OwnerQuestionSemanticAuditV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        verdict=verdict,
        question_views_count=question_views_count,
        auditable_views_count=auditable_views_count,
        aligned_views_count=aligned_views_count,
        unaligned_views_count=len(findings),
        findings=tuple(findings),
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "observational_only": True,
            "audit_policy": "lexical_semantic_alignment_without_parallel_catalog",
            "opaque_headers_skipped": tuple(sorted(_OPAQUE_HEADERS)),
        },
    )


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value).strip().lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(
        token
        for token in _TOKEN_RE.findall(_normalize(value).replace("_", " "))
        if token not in _STOPWORDS and len(token) > 1
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "VERDICT_PASS",
    "VERDICT_NEEDS_FIXES",
    "ISSUE_NO_SEMANTIC_ALIGNMENT",
    "Service1OwnerQuestionSemanticAuditFindingV1",
    "Service1OwnerQuestionSemanticAuditV1",
    "audit_service_1_column_understanding_owner_question_semantics_v1",
]

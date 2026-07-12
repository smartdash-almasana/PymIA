"""Service 1 — canonical coverage audit for unresolved column meanings.

Pure audit. It receives canonical variable names as data and compares them
lexically with unresolved corpus headers. It does not create mappings.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Iterable

from pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1 import (
    OUTCOME_SAFE_QUESTION,
    evaluate_service_1_column_understanding_corpus_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_CANONICAL_GAP_AUDIT_V1"
STATUS_READY: Final[str] = "CANONICAL_GAP_AUDIT_READY"
VERDICT_GAPS_REMAIN: Final[str] = "GAPS_REMAIN"
VERDICT_COVERED: Final[str] = "CANONICALLY_COVERED"

_STOP_TOKENS: Final[frozenset[str]] = frozenset(
    {"amount", "value", "total", "initial", "final", "current", "average"}
)


@dataclass(frozen=True)
class Service1ColumnCanonicalGapFindingV1:
    case_id: str
    column_name: str
    lexical_candidates: tuple[str, ...]
    canonical_mapping_authorized: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnCanonicalGapAuditV1:
    schema_version: str
    status: str
    verdict: str
    unresolved_columns_count: int
    columns_with_lexical_candidates: int
    columns_without_lexical_candidates: int
    findings: tuple[Service1ColumnCanonicalGapFindingV1, ...]
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def audit_service_1_column_understanding_canonical_gaps_v1(
    canonical_variable_names: Iterable[str],
) -> Service1ColumnCanonicalGapAuditV1:
    canonical = tuple(sorted({_clean_name(name) for name in canonical_variable_names if _clean_name(name)}))
    evaluation = evaluate_service_1_column_understanding_corpus_v1()
    findings: list[Service1ColumnCanonicalGapFindingV1] = []

    for row in evaluation.rows:
        if row.outcome != OUTCOME_SAFE_QUESTION:
            continue
        candidates = tuple(
            variable
            for variable in canonical
            if _shares_meaningful_token(row.column_name, variable)
        )
        findings.append(
            Service1ColumnCanonicalGapFindingV1(
                case_id=row.case_id,
                column_name=row.column_name,
                lexical_candidates=candidates,
                canonical_mapping_authorized=False,
                reason=(
                    "Lexical candidates are evidence leads only; mapping still requires explicit semantic evidence."
                    if candidates
                    else "No canonical variable shares a meaningful lexical signal with the column header."
                ),
            )
        )

    with_candidates = sum(1 for finding in findings if finding.lexical_candidates)
    without_candidates = len(findings) - with_candidates
    verdict = VERDICT_COVERED if findings and without_candidates == 0 else VERDICT_GAPS_REMAIN
    return Service1ColumnCanonicalGapAuditV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        verdict=verdict,
        unresolved_columns_count=len(findings),
        columns_with_lexical_candidates=with_candidates,
        columns_without_lexical_candidates=without_candidates,
        findings=tuple(findings),
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "observational_only": True,
            "mapping_policy": "lexical_candidates_never_authorize_mapping",
        },
    )


def _clean_name(value: object) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _tokens(value: str) -> frozenset[str]:
    return frozenset(
        token
        for token in _clean_name(value).split("_")
        if len(token) >= 4 and token not in _STOP_TOKENS
    )


def _shares_meaningful_token(column_name: str, variable_name: str) -> bool:
    return bool(_tokens(column_name) & _tokens(variable_name))


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "VERDICT_GAPS_REMAIN",
    "VERDICT_COVERED",
    "Service1ColumnCanonicalGapFindingV1",
    "Service1ColumnCanonicalGapAuditV1",
    "audit_service_1_column_understanding_canonical_gaps_v1",
]

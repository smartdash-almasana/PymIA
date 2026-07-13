"""Adapter from Chain A (vertical_pipeline.build_report) to owner pure view input.

The report produced by Chain A carries a richer, nested shape than the flat
OwnerPureViewInput that ``build_owner_pure_view`` consumes. This adapter performs
a minimal, pure-dict mapping without recomputing rows/columns/headers (those are
re-derived elsewhere by the curation layers, not here).

This module is deliberately thin: no IO, no pipeline calls, no LLM, no runtime.
It only rephrases an existing report dict into the flat input expected by the
owner pure view builder.
"""

from __future__ import annotations

import os
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "OWNER_PURE_VIEW_CHAIN_A_ADAPTER_V1"

# Internal warnings that are not owner-facing and must be filtered out before
# the owner pure view sees them.
_INTERNAL_WARNINGS: Final[frozenset[str]] = frozenset(
    {
        "Slice local; no es canal productivo.",
    }
)


def adapt_chain_a_report_to_owner_pure_view_input(report: dict[str, Any]) -> dict[str, Any]:
    """Map a Chain A report dict to the flat input expected by build_owner_pure_view.

    Only rephrases already-available fields. Does not recompute rows, columns or
    headers.
    """
    status = report.get("status")
    owner_summary = report.get("summary")

    next_questions = _resolve_next_questions(report)
    table_sheets = _resolve_table_sheets(report)
    file_name = _resolve_file_name(report)
    limit_warnings = _filter_internal_warnings(report.get("limit_warnings"))

    return {
        "status": status,
        "owner_summary": owner_summary,
        "missing_evidence": report.get("missing_evidence"),
        "next_questions": next_questions,
        "limit_warnings": limit_warnings,
        "table_sheets": table_sheets,
        "file_name": file_name,
    }


def _resolve_next_questions(report: dict[str, Any]) -> list[str]:
    """Prefer the resolved owner_question over the raw next_questions list."""
    owner_question = _normalize_optional_text(report.get("owner_question"))
    if owner_question:
        return [owner_question]
    return _normalize_text_list(report.get("next_questions"))


def _resolve_table_sheets(report: dict[str, Any]) -> list[dict[str, Any]]:
    structured_summary = report.get("structured_evidence_summary")
    if not isinstance(structured_summary, dict):
        return []
    table_sheets = structured_summary.get("table_sheets")
    if not isinstance(table_sheets, list):
        return []
    return [dict(item) for item in table_sheets if isinstance(item, dict)]


def _resolve_file_name(report: dict[str, Any]) -> str | None:
    references = report.get("references")
    if isinstance(references, list) and references:
        first = references[0]
        if first:
            return os.path.basename(str(first))
    return None


def _filter_internal_warnings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    filtered: list[str] = []
    for item in value:
        text = _normalize_optional_text(item)
        if text and text not in _INTERNAL_WARNINGS:
            filtered.append(text)
    return filtered


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = _normalize_optional_text(item)
        if text:
            normalized.append(text)
    return normalized


__all__ = [
    "SCHEMA_VERSION",
    "adapt_chain_a_report_to_owner_pure_view_input",
]

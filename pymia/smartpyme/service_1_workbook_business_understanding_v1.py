"""Servicio 1 — F3 closed workbook business-understanding contract.

This is a semantic hypothesis produced before column interpretation. It is
context-only: no mathematics, owner confirmation, runtime or delivery authority.
The deterministic validator below only verifies shape, workbook references and
safety boundaries; it does not declare the LLM hypothesis true.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_WORKBOOK_BUSINESS_UNDERSTANDING_V1"
STATUS_READY: Final[str] = "WORKBOOK_BUSINESS_UNDERSTANDING_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"
AUTHORITY: Final[str] = "CONTEXT_ONLY"


def validate_service_1_workbook_business_understanding_v1(
    *,
    candidate: Any,
    workbook_semantic_context: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(candidate, Mapping):
        return _blocked("BUSINESS_UNDERSTANDING_NOT_MAPPING")
    if candidate.get("schema_version") != SCHEMA_VERSION:
        return _blocked("BUSINESS_UNDERSTANDING_SCHEMA_INVALID")
    if candidate.get("authority") != AUTHORITY:
        return _blocked("BUSINESS_UNDERSTANDING_AUTHORITY_INVALID")
    if any(bool(candidate.get(flag)) for flag in (
        "runtime_authorized", "tool_execution_authorized", "product_ready",
        "delivery_authorized", "diagnosis_generated",
    )):
        return _blocked("BUSINESS_UNDERSTANDING_AUTHORITY_ESCALATION")

    workbook_tables = {
        str(item.get("sheet_name") or "").strip()
        for item in (workbook_semantic_context.get("tables") or [])
        if isinstance(item, Mapping) and str(item.get("sheet_name") or "").strip()
    }
    raw_tables = candidate.get("tables")
    if not isinstance(raw_tables, Sequence) or isinstance(raw_tables, (str, bytes)):
        return _blocked("BUSINESS_UNDERSTANDING_TABLES_INVALID")

    seen: set[str] = set()
    tables: list[dict[str, Any]] = []
    try:
        for raw in raw_tables:
            if not isinstance(raw, Mapping):
                return _blocked("BUSINESS_UNDERSTANDING_TABLE_INVALID")
            sheet_name = str(raw.get("sheet_name") or "").strip()
            if not sheet_name or sheet_name not in workbook_tables or sheet_name in seen:
                return _blocked("BUSINESS_UNDERSTANDING_TABLE_REF_INVALID")
            seen.add(sheet_name)
            meaning = str(raw.get("table_meaning") or "").strip()
            grain = str(raw.get("grain") or "").strip()
            if not meaning:
                return _blocked("BUSINESS_UNDERSTANDING_MEANING_REQUIRED")
            tables.append({
                "sheet_name": sheet_name,
                "table_meaning": meaning,
                "grain": grain or None,
                "business_objects": _text_list(raw.get("business_objects")),
                "processes": _text_list(raw.get("processes")),
                "semantic_groups": _text_list(raw.get("semantic_groups")),
                "confidence": _confidence(raw.get("confidence")),
            })
        material_ambiguities = _text_list(candidate.get("material_ambiguities"))
    except (TypeError, ValueError):
        return _blocked("BUSINESS_UNDERSTANDING_FIELD_INVALID")

    if seen != workbook_tables:
        return _blocked("BUSINESS_UNDERSTANDING_MUST_COVER_ALL_TABLES")
    summary = str(candidate.get("workbook_summary") or "").strip()
    if not summary:
        return _blocked("BUSINESS_UNDERSTANDING_SUMMARY_REQUIRED")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "authority": AUTHORITY,
        "workbook_summary": summary,
        "tables": tables,
        "material_ambiguities": material_ambiguities,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("business understanding list field must be a sequence")
    result = [str(item or "").strip() for item in value]
    return [item for item in result if item]


def _confidence(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0.0 or number > 1.0:
        raise ValueError("confidence outside [0,1]")
    return number


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "authority": AUTHORITY,
        "workbook_summary": None,
        "tables": [],
        "material_ambiguities": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "AUTHORITY", "SCHEMA_VERSION", "STATUS_BLOCKED", "STATUS_READY",
    "validate_service_1_workbook_business_understanding_v1",
]

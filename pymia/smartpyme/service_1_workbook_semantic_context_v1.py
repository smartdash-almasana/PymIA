"""Servicio 1 — bounded workbook semantic context for LLM understanding.

F1 of C2 Workbook Semantic Understanding. This module does not open XLSX files,
does not infer business meaning, does not call an LLM and grants no authority.
It reorganizes already-canonical deterministic workbook evidence into a compact,
table-oriented context suitable for semantic reasoning.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_WORKBOOK_SEMANTIC_CONTEXT_V1"
STATUS_READY: Final[str] = "WORKBOOK_SEMANTIC_CONTEXT_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_PROFILE_INVALID: Final[str] = "BLOCK_WORKBOOK_SEMANTIC_CONTEXT_PROFILE_INVALID"
BLOCK_CASE_ID_REQUIRED: Final[str] = "BLOCK_WORKBOOK_SEMANTIC_CONTEXT_CASE_ID_REQUIRED"
BLOCK_COLUMNS_MISSING: Final[str] = "BLOCK_WORKBOOK_SEMANTIC_CONTEXT_COLUMNS_MISSING"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_workbook_semantic_context_v1(*, workbook_profile: Any) -> dict[str, Any]:
    """Project a ready workbook profile into table-first semantic context."""
    if not isinstance(workbook_profile, Mapping):
        return _blocked(BLOCK_PROFILE_INVALID)
    profile = dict(workbook_profile)
    if profile.get("status") != "WORKBOOK_PROFILE_READY":
        return _blocked(BLOCK_PROFILE_INVALID)
    if any(bool(profile.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked(BLOCK_PROFILE_INVALID)

    case_id = str(profile.get("case_id") or "").strip()
    if not case_id:
        return _blocked(BLOCK_CASE_ID_REQUIRED)

    columns = [dict(item) for item in (profile.get("columns") or []) if isinstance(item, Mapping)]
    if not columns:
        return _blocked(BLOCK_COLUMNS_MISSING, case_id=case_id)

    logical_scope_by_ref: dict[str, dict[str, Any]] = {}
    for raw in profile.get("logical_table_scopes") or []:
        if not isinstance(raw, Mapping):
            continue
        ref = str(raw.get("column_ref") or "").strip()
        if ref:
            logical_scope_by_ref[ref] = dict(raw)

    tables: dict[str, dict[str, Any]] = {}
    for column in columns:
        sheet_name = str(column.get("sheet_name") or "").strip()
        column_ref = str(column.get("column_ref") or "").strip()
        column_name = str(column.get("column_name") or "").strip()
        if not sheet_name or not column_ref or not column_name:
            return _blocked(BLOCK_PROFILE_INVALID, case_id=case_id)

        table = tables.setdefault(
            sheet_name,
            {
                "sheet_name": sheet_name,
                "row_count": int(column.get("row_count") or 0),
                "column_count": 0,
                "columns": [],
                "logical_table_refs": [],
                "grain_refs": [],
            },
        )
        table["column_count"] += 1
        scope = logical_scope_by_ref.get(column_ref, {})
        logical_table_ref = str(scope.get("logical_table_ref") or "").strip()
        grain_ref = str(scope.get("grain_ref") or "").strip()
        if logical_table_ref and logical_table_ref not in table["logical_table_refs"]:
            table["logical_table_refs"].append(logical_table_ref)
        if grain_ref and grain_ref not in table["grain_refs"]:
            table["grain_refs"].append(grain_ref)

        table["columns"].append(
            {
                "column_ref": column_ref,
                "column_name": column_name,
                "normalized_header": column.get("normalized_header"),
                "inferred_type": column.get("inferred_type"),
                "sample_values": list(column.get("sample_values") or []),
                "row_count": int(column.get("row_count") or 0),
                "non_null_count": int(column.get("non_null_count") or 0),
                "null_ratio": float(column.get("null_ratio") or 0.0),
                "cardinality": int(column.get("cardinality") or 0),
                "unique_ratio": float(column.get("unique_ratio") or 0.0),
                "uniqueness_class": column.get("uniqueness_class"),
                "candidate_primary_key": bool(column.get("candidate_primary_key")),
                "numeric_range": column.get("numeric_range"),
                "date_range": column.get("date_range"),
                "logical_table_ref": logical_table_ref or None,
                "grain_ref": grain_ref or None,
                "grain_state": scope.get("grain_state"),
                "relationship_context_refs": list(scope.get("relationship_context_refs") or []),
            }
        )

    relationships = []
    for raw in profile.get("relationships") or []:
        if not isinstance(raw, Mapping):
            continue
        relationships.append(
            {
                "relationship_ref": raw.get("relationship_ref"),
                "left_column_ref": raw.get("left_column_ref"),
                "right_column_ref": raw.get("right_column_ref"),
                "relationship_kind": raw.get("relationship_kind"),
                "same_normalized_header": bool(raw.get("same_normalized_header")),
                "left_value_coverage": raw.get("left_value_coverage"),
                "right_value_coverage": raw.get("right_value_coverage"),
                "candidate_foreign_key": bool(raw.get("candidate_foreign_key")),
                "candidate_primary_key_ref": raw.get("candidate_primary_key_ref"),
                "intersection_cardinality": raw.get("intersection_cardinality"),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "source_file_ref": profile.get("source_file_ref"),
        "sheet_count": len(tables),
        "column_count": len(columns),
        "relationship_count": len(relationships),
        "tables": list(tables.values()),
        "relationships": relationships,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(reason: str, *, case_id: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "tables": [],
        "relationships": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "build_service_1_workbook_semantic_context_v1",
]

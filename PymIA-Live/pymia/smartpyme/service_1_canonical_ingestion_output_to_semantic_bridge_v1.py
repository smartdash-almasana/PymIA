"""
Service 1 Canonical Ingestion Output -> Semantic Bridge V1

Minimal, deterministic connector for the Servicio 1 assisted flow.

Flow implemented (connector only):

    canonical ingestion_output -> existing column-semantic mapper
                               -> semantic column candidates
                               (ready input for the semantic evidence
                                binding engine)

This module reuses existing modules and DUPLICATES NO LOGIC:
- pymia.contracts.column_confirmation_v1 (ColumnConfirmationEntry / Matrix)
- pymia.smartpyme.service_1_column_semantic_mapper_v1 (candidate builder)

It consumes the ingestion_output produced by
``service_1_owner_confirmation_to_canonical_ingestion_output_v1`` and produces
the ``column_candidates`` tuple that
``service_1_semantic_evidence_binding_engine_v1`` accepts as input.

This module DOES NOT:
- execute tools,
- authorize runtime, product or delivery,
- create a delivery folder,
- re-open or re-read the XLSX,
- touch the legacy CLI,
- implement any web UI,
- run the full binding engine (formula/pathology catalogs are out of scope
  for this slice).
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_semantic_mapper_v1 import (
    build_service_1_column_semantic_candidates_from_matrix_v1,
)

SCHEMA_VERSION = "SERVICE_1_CANONICAL_INGESTION_OUTPUT_TO_SEMANTIC_BRIDGE_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "CANONICAL_INGESTION_OUTPUT_TO_SEMANTIC_BRIDGE"

STATUS_READY = "SEMANTIC_CANDIDATES_READY"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_INGESTION_NOT_DICT = "INGESTION_OUTPUT_NOT_DICT"
BLOCK_INGESTION_FLAGS_FORBIDDEN = "INGESTION_SAFETY_FLAGS_FORBIDDEN"
BLOCK_NO_COLUMNS = "NO_COLUMNS"
BLOCK_NO_INPUT_VALUES = "NO_INPUT_VALUES"
BLOCK_COLUMNS_VALUES_MISMATCH = "COLUMNS_VALUES_MISMATCH"
BLOCK_DUPLICATE_COLUMNS = "DUPLICATE_COLUMNS"


def build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
    *,
    ingestion_output: Any,
    sheet_name: str = "sheet1",
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    """Turn a canonical ingestion_output into semantic column candidates.

    Args:
        ingestion_output: The ``ingestion_output`` dict produced by
            ``service_1_owner_confirmation_to_canonical_ingestion_output_v1``.
        sheet_name: Sheet label to stamp on the confirmation entries. The
            boundary does not carry a per-column sheet, so a single sheet ref
            is used; defaults to ``"sheet1"``.
        runtime_authorized / product_ready / delivery_authorized: Must remain
            False. Passing any as True is itself a blocking condition.

    Returns:
        A connector packet dict. On success, status is
        ``SEMANTIC_CANDIDATES_READY`` and ``column_candidates`` is a tuple of
        ``Service1ColumnSemanticCandidateV1`` ready for the semantic engine.
        On any blocking condition, status is ``BLOCKED`` with a
        ``blocked_reason`` and ``column_candidates`` is an empty tuple.
    """
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(ingestion_output, dict) or not ingestion_output:
        return _blocked(BLOCK_INGESTION_NOT_DICT)

    # The upstream ingestion_output must not carry runtime authorization.
    if ingestion_output.get("runtime_authorized"):
        return _blocked(BLOCK_INGESTION_FLAGS_FORBIDDEN)

    case_id = ingestion_output.get("case_id")
    source_kind = ingestion_output.get("source_kind")
    filename = ingestion_output.get("filename")

    columns = _extract_columns(ingestion_output)
    input_values = _extract_input_values(ingestion_output)

    if not columns:
        return _blocked(
            BLOCK_NO_COLUMNS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )
    if not input_values:
        return _blocked(
            BLOCK_NO_INPUT_VALUES,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    duplicates = _duplicates(columns)
    if duplicates:
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=duplicates,
        )

    # Every declared column must have a confirmed owner value.
    if set(columns) != set(input_values.keys()) or len(columns) != len(input_values):
        return _blocked(
            BLOCK_COLUMNS_VALUES_MISMATCH,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    matrix = _build_confirmation_matrix(
        filename=filename or "uploaded.xlsx",
        sheet_name=sheet_name,
        columns=columns,
        owner_values=input_values,
    )

    column_candidates = build_service_1_column_semantic_candidates_from_matrix_v1(matrix)

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "columns": list(columns),
        "column_candidate_count": len(column_candidates),
        "column_candidates": column_candidates,
        "confirmation_matrix": matrix,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _build_confirmation_matrix(
    *,
    filename: str,
    sheet_name: str,
    columns: list[str],
    owner_values: dict[str, Any],
) -> ColumnConfirmationMatrix:
    entries = [
        ColumnConfirmationEntry(
            original_column_name=column,
            sheet_name=sheet_name,
            sample_values=[owner_values.get(column)],
            suggested_semantic_role="unknown",
            owner_confirmed_role=str(owner_values.get(column)).strip() or None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
        )
        for column in columns
    ]
    return ColumnConfirmationMatrix(file_name=filename, entries=entries)


def _extract_columns(ingestion_output: dict[str, Any]) -> list[str]:
    for key in ("available_data_fields", "columns", "confirmed_columns"):
        value = ingestion_output.get(key)
        if isinstance(value, (list, tuple)) and value:
            return [str(item).strip() for item in value if str(item).strip()]
    return []


def _extract_input_values(ingestion_output: dict[str, Any]) -> dict[str, Any]:
    for key in ("input_values", "normalized_values", "owner_answers"):
        value = ingestion_output.get(key)
        if isinstance(value, dict) and value:
            return {str(k).strip(): v for k, v in value.items() if str(k).strip()}
    return {}


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen and value not in result:
            result.append(value)
        seen.add(value)
    return result


def _blocked(
    reason: str,
    *,
    case_id: Optional[str] = None,
    source_kind: Optional[str] = None,
    filename: Optional[str] = None,
    detail: Optional[list[str]] = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "columns": [],
        "column_candidate_count": 0,
        "column_candidates": (),
        "confirmation_matrix": None,
        "detail": list(detail or []),
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_INGESTION_NOT_DICT",
    "BLOCK_INGESTION_FLAGS_FORBIDDEN",
    "BLOCK_NO_COLUMNS",
    "BLOCK_NO_INPUT_VALUES",
    "BLOCK_COLUMNS_VALUES_MISMATCH",
    "BLOCK_DUPLICATE_COLUMNS",
    "build_service_1_semantic_bridge_from_canonical_ingestion_output_v1",
]

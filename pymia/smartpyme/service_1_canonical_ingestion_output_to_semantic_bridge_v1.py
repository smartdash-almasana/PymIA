"""
Service 1 Canonical Ingestion Output -> Semantic Bridge V1

Minimal, deterministic connector for the Servicio 1 assisted flow.

Flow implemented (connector only):

    canonical ingestion_output -> column understanding engine
                               -> owner-facing question projection
                               -> semantic column candidates
                               (ready input for the semantic evidence
                                binding engine)

This module reuses existing modules and DUPLICATES NO LOGIC:
- pymia.contracts.column_confirmation_v1 (ColumnConfirmationEntry / Matrix)
- pymia.smartpyme.service_1_column_understanding_engine_v1
- pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1

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
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understandings_from_matrix_v1,
)
from pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1 import (
    build_service_1_column_owner_question_views_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
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
        sheet_name: Legacy fallback used only when ingestion_output does not
            carry sheet-qualified ``column_refs``. Canonical multisheet intake
            supplies the real worksheet identity for every column.
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
    column_refs = _extract_column_refs(
        ingestion_output,
        columns=columns,
        fallback_sheet_name=sheet_name,
    )

    if not columns or not column_refs:
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
    duplicate_identities = _duplicates(
        [f"{ref['sheet_name']}\x00{ref['column_name']}" for ref in column_refs]
    )
    if duplicates or duplicate_identities:
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=duplicates or duplicate_identities,
        )

    # Every declared column must have a confirmed owner value.
    if set(columns) != set(input_values.keys()) or len(columns) != len(input_values):
        return _blocked(
            BLOCK_COLUMNS_VALUES_MISMATCH,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    matrix_owner_values = dict(input_values)
    matrix_owner_values["__column_evidence__"] = (
        ingestion_output.get("column_evidence") or {}
    )
    matrix = _build_confirmation_matrix(
        filename=filename or "uploaded.xlsx",
        column_refs=column_refs,
        owner_values=matrix_owner_values,
    )

    understandings = build_column_understandings_from_matrix_v1(matrix)
    owner_question_views = build_service_1_column_owner_question_views_v1(understandings)
    column_candidates = tuple(
        _candidate_from_understanding(item, column_ref=ref)
        for item, ref in zip(understandings, column_refs)
    )
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
        "column_refs": [dict(ref) for ref in column_refs],
        "column_candidate_count": len(column_candidates),
        "column_candidates": column_candidates,
        "variable_family_count": 0,
        "variable_family_bindings": (),
        "ready_variable_family_ids": [],
        "confirmation_matrix": matrix,
        "column_understandings": understandings,
        "owner_question_views": owner_question_views,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _build_confirmation_matrix(
    *,
    filename: str,
    column_refs: list[dict[str, str]],
    owner_values: dict[str, Any],
) -> ColumnConfirmationMatrix:
    evidence = owner_values.get("__column_evidence__", {})
    entries: list[ColumnConfirmationEntry] = []
    for ref in column_refs:
        field_id = ref["field_id"]
        item = evidence.get(field_id, {}) if isinstance(evidence, dict) else {}
        entries.append(
            ColumnConfirmationEntry(
                original_column_name=ref["column_name"],
                sheet_name=ref["sheet_name"],
                sample_values=list(item.get("sample_values") or []),
                inferred_type=item.get("inferred_type") or "unknown",
                suggested_semantic_role="unknown",
                owner_confirmed_role=str(owner_values.get(field_id)).strip() or None,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            )
        )
    return ColumnConfirmationMatrix(file_name=filename, entries=entries)

def _candidate_from_understanding(
    understanding: Any,
    *,
    column_ref: dict[str, str],
) -> Service1ColumnSemanticCandidateV1:
    hypotheses = tuple(understanding.candidate_meanings or ())
    roles = tuple(item.semantic_role for item in hypotheses) or ("unknown",)
    variables = tuple(item.variable_name for item in hypotheses) or ("unknown",)
    primary = understanding.primary_hypothesis

    return Service1ColumnSemanticCandidateV1(
        source_column_name=understanding.column_name,
        normalized_column_name=understanding.normalized_header,
        sheet_name=understanding.sheet_name,
        observed_data_type=understanding.inferred_data_type,
        sample_values=tuple(understanding.sample_values),
        candidate_semantic_roles=roles,
        candidate_variable_names=variables,
        confidence=understanding.confidence,
        ambiguity_reason=(
            understanding.risk_if_wrong
            if understanding.owner_question_needed
            else None
        ),
        owner_confirmation_required=bool(understanding.owner_question_needed),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={
            "source_engine": "service_1_column_understanding_engine_v1",
            "column_ref_id": column_ref["field_id"],
            "question_id": column_ref["question_id"],
            "sheet_name": column_ref["sheet_name"],
            "source_column_name": column_ref["column_name"],
            "primary_semantic_role": (
                primary.semantic_role if primary is not None else None
            ),
            "primary_variable_name": (
                primary.variable_name if primary is not None else None
            ),
            "owner_question_text": understanding.owner_question_text,
            "allowed_owner_answers": [
                option.to_dict() for option in understanding.allowed_owner_answers
            ],
            "evidence": list(understanding.evidence),
        },
    )


def _extract_columns(ingestion_output: dict[str, Any]) -> list[str]:
    for key in ("available_data_fields", "columns", "confirmed_columns"):
        value = ingestion_output.get(key)
        if isinstance(value, (list, tuple)) and value:
            return [str(item).strip() for item in value if str(item).strip()]
    return []


def _extract_column_refs(
    ingestion_output: dict[str, Any],
    *,
    columns: list[str],
    fallback_sheet_name: str,
) -> list[dict[str, str]]:
    raw_refs = ingestion_output.get("column_refs")
    if isinstance(raw_refs, list) and raw_refs:
        refs: list[dict[str, str]] = []
        for raw in raw_refs:
            if not isinstance(raw, dict):
                return []
            ref = {
                "field_id": str(raw.get("field_id") or "").strip(),
                "question_id": str(raw.get("question_id") or raw.get("field_id") or "").strip(),
                "sheet_name": str(raw.get("sheet_name") or "").strip(),
                "column_name": str(raw.get("column_name") or "").strip(),
                "normalized_column_name": str(
                    raw.get("normalized_column_name") or raw.get("column_name") or ""
                ).strip(),
            }
            if any(not ref[key] for key in ("field_id", "question_id", "sheet_name", "column_name")):
                return []
            refs.append(ref)
        if [ref["field_id"] for ref in refs] != columns:
            return []
        return refs

    sheet = str(ingestion_output.get("sheet_name") or fallback_sheet_name).strip()
    return [
        {
            "field_id": column,
            "question_id": column,
            "sheet_name": sheet,
            "column_name": column,
            "normalized_column_name": column,
        }
        for column in columns
    ]


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
        "column_refs": [],
        "column_candidate_count": 0,
        "column_candidates": (),
        "variable_family_count": 0,
        "variable_family_bindings": (),
        "ready_variable_family_ids": [],
        "confirmation_matrix": None,
        "column_understandings": (),
        "owner_question_views": (),
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

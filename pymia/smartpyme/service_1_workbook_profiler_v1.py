"""Servicio 1 — deterministic workbook profiler V1.

Post-ingestion enrichment for ADR-029 / SEM-1.

Consumes only the canonical ``ingestion_output`` already produced by Servicio 1.
It never opens or reparses XLSX files, never calls an LLM, never interprets owner
answers, and never grants runtime/product/delivery authority.
"""
from __future__ import annotations

from datetime import date, datetime
from math import isfinite
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_WORKBOOK_PROFILE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
STATUS_READY: Final[str] = "WORKBOOK_PROFILE_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_INPUT_NOT_DICT: Final[str] = "BLOCK_PROFILE_INPUT_NOT_DICT"
BLOCK_INPUT_AUTHORITY_FORBIDDEN: Final[str] = "BLOCK_PROFILE_INPUT_AUTHORITY_FORBIDDEN"
BLOCK_SOURCE_TABLES_MISSING: Final[str] = "BLOCK_PROFILE_SOURCE_TABLES_MISSING"
BLOCK_SOURCE_TABLE_INVALID: Final[str] = "BLOCK_PROFILE_SOURCE_TABLE_INVALID"
BLOCK_COLUMN_REFS_MISSING: Final[str] = "BLOCK_PROFILE_COLUMN_REFS_MISSING"
BLOCK_COLUMN_REF_INVALID: Final[str] = "BLOCK_PROFILE_COLUMN_REF_INVALID"
BLOCK_COLUMN_REF_NOT_FOUND: Final[str] = "BLOCK_PROFILE_COLUMN_REF_NOT_FOUND"
BLOCK_DUPLICATE_COLUMN_REF: Final[str] = "BLOCK_PROFILE_DUPLICATE_COLUMN_REF"
BLOCK_WORKBOOK_CONTEXT_REQUIRED: Final[str] = "BLOCK_PROFILE_WORKBOOK_CONTEXT_REQUIRED"
BLOCK_PROVENANCE_REQUIRED: Final[str] = "BLOCK_PROFILE_PROVENANCE_REQUIRED"

MAX_SAMPLE_VALUES: Final[int] = 5
RELATIONSHIP_OVERLAP_THRESHOLD: Final[float] = 0.80

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_workbook_profile_v1(*, ingestion_output: Any) -> dict[str, Any]:
    """Build deterministic column and cross-sheet structural evidence.

    The function is deliberately pure with respect to its input object. It reads
    ``normalized_tables`` and ``column_refs`` and emits a self-contained profile
    plus a closed ``evidence_registry`` for later LLM proposal validation.
    """
    if not isinstance(ingestion_output, dict) or not ingestion_output:
        return _blocked(BLOCK_INPUT_NOT_DICT)
    if any(bool(ingestion_output.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked(BLOCK_INPUT_AUTHORITY_FORBIDDEN, ingestion_output=ingestion_output)

    raw_tables = ingestion_output.get("normalized_tables")
    if not isinstance(raw_tables, list) or not raw_tables:
        return _blocked(BLOCK_SOURCE_TABLES_MISSING, ingestion_output=ingestion_output)

    tables: dict[str, dict[str, Any]] = {}
    for raw_table in raw_tables:
        if not _valid_table(raw_table):
            return _blocked(BLOCK_SOURCE_TABLE_INVALID, ingestion_output=ingestion_output)
        sheet_name = str(raw_table.get("sheet_name") or "").strip()
        if sheet_name in tables:
            return _blocked(BLOCK_SOURCE_TABLE_INVALID, ingestion_output=ingestion_output, detail=sheet_name)
        tables[sheet_name] = raw_table

    raw_refs = ingestion_output.get("column_refs")
    if not isinstance(raw_refs, list) or not raw_refs:
        return _blocked(BLOCK_COLUMN_REFS_MISSING, ingestion_output=ingestion_output)

    workbook_context = ingestion_output.get("workbook_context")
    if not isinstance(workbook_context, dict):
        return _blocked(BLOCK_WORKBOOK_CONTEXT_REQUIRED, ingestion_output=ingestion_output)
    provenance = ingestion_output.get("provenance")
    if not isinstance(provenance, dict):
        return _blocked(BLOCK_PROVENANCE_REQUIRED, ingestion_output=ingestion_output)

    refs: list[dict[str, str]] = []
    seen_refs: set[str] = set()
    for raw_ref in raw_refs:
        ref = _clean_column_ref(raw_ref)
        if ref is None:
            return _blocked(BLOCK_COLUMN_REF_INVALID, ingestion_output=ingestion_output)
        identity = _column_identity(ref["sheet_name"], ref["column_name"])
        if identity in seen_refs:
            return _blocked(BLOCK_DUPLICATE_COLUMN_REF, ingestion_output=ingestion_output, detail=identity)
        seen_refs.add(identity)
        table = tables.get(ref["sheet_name"])
        if table is None or not _ref_exists_in_table(ref, table):
            return _blocked(BLOCK_COLUMN_REF_NOT_FOUND, ingestion_output=ingestion_output, detail=identity)
        refs.append(ref)

    evidence_registry: dict[str, dict[str, Any]] = {}
    column_profiles: list[dict[str, Any]] = []
    values_by_identity: dict[str, tuple[str, ...]] = {}

    for ref in refs:
        table = tables[ref["sheet_name"]]
        profile, evidence, canonical_values = _profile_column(ref=ref, table=table)
        column_profiles.append(profile)
        evidence_registry.update(evidence)
        values_by_identity[profile["column_ref"]] = canonical_values

    profiles_by_identity = {profile["column_ref"]: profile for profile in column_profiles}
    relationships: list[dict[str, Any]] = []
    for left in column_profiles:
        for right in column_profiles:
            if left["sheet_name"] == right["sheet_name"]:
                continue
            if left["column_ref"] == right["column_ref"]:
                continue
            relationship = _candidate_relationship(
                left=left,
                right=right,
                left_values=values_by_identity[left["column_ref"]],
                right_values=values_by_identity[right["column_ref"]],
            )
            if relationship is None:
                continue
            # Directed FK -> PK candidates are naturally unique. For ONE_TO_ONE,
            # keep only lexical identity order to avoid mirrored duplicates.
            if relationship["relationship_kind"] == "ONE_TO_ONE" and left["column_ref"] > right["column_ref"]:
                continue
            relationships.append(relationship)
            evidence_registry.update(_relationship_evidence(relationship))

    relationships.sort(key=lambda item: (item["left_column_ref"], item["right_column_ref"]))

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": ((ingestion_output.get("workbook_context") or {}).get("case_id") if isinstance(ingestion_output.get("workbook_context"), dict) else None),
        "source_file_ref": ((ingestion_output.get("provenance") or {}).get("source_file_ref") if isinstance(ingestion_output.get("provenance"), dict) else None),
        "sheet_names": list(tables),
        "column_count": len(column_profiles),
        "relationship_count": len(relationships),
        "columns": column_profiles,
        "relationships": relationships,
        "evidence_registry": evidence_registry,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _valid_table(raw: Any) -> bool:
    if not isinstance(raw, dict) or raw.get("status") != "OK":
        return False
    sheet_name = str(raw.get("sheet_name") or "").strip()
    headers = raw.get("headers")
    normalized_headers = raw.get("normalized_headers")
    rows = raw.get("rows")
    if not sheet_name or not isinstance(headers, list) or not isinstance(normalized_headers, list) or not isinstance(rows, list):
        return False
    if len(headers) != len(normalized_headers) or not headers:
        return False
    return all(isinstance(row, dict) for row in rows)


def _clean_column_ref(raw: Any) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    sheet_name = str(raw.get("sheet_name") or "").strip()
    column_name = str(raw.get("column_name") or "").strip()
    normalized = str(raw.get("normalized_column_name") or column_name).strip()
    field_id = str(raw.get("field_id") or "").strip()
    question_id = str(raw.get("question_id") or "").strip()
    if not sheet_name or not column_name or not normalized:
        return None
    return {
        "sheet_name": sheet_name,
        "column_name": column_name,
        "normalized_column_name": normalized,
        "field_id": field_id,
        "question_id": question_id,
    }


def _ref_exists_in_table(ref: dict[str, str], table: dict[str, Any]) -> bool:
    headers = [str(value).strip() for value in table.get("headers") or []]
    normalized = [str(value).strip() for value in table.get("normalized_headers") or []]
    return ref["column_name"] in headers and ref["normalized_column_name"] in normalized


def _profile_column(*, ref: dict[str, str], table: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]], tuple[str, ...]]:
    rows = list(table.get("rows") or [])
    normalized_name = ref["normalized_column_name"]
    raw_values = [row.get(normalized_name) for row in rows]
    non_empty = [value for value in raw_values if not _is_empty(value)]
    canonical_values = tuple(_canonical_scalar(value) for value in non_empty)
    distinct_values = set(canonical_values)
    row_count = len(rows)
    non_null_count = len(non_empty)
    cardinality = len(distinct_values)
    null_count = row_count - non_null_count
    null_ratio = (null_count / row_count) if row_count else 0.0
    unique_ratio = (cardinality / non_null_count) if non_null_count else 0.0
    uniqueness_class = _uniqueness_class(
        row_count=row_count,
        non_null_count=non_null_count,
        cardinality=cardinality,
        unique_ratio=unique_ratio,
    )
    inferred_type = _infer_type(non_empty)
    numeric_range = _numeric_range(non_empty) if inferred_type == "number" else None
    date_range = _date_range(non_empty) if inferred_type == "date" else None
    samples = _bounded_samples(non_empty)
    column_ref = _column_identity(ref["sheet_name"], ref["column_name"])
    candidate_primary_key = bool(row_count and null_count == 0 and uniqueness_class == "UNIQUE")

    profile = {
        "column_ref": column_ref,
        "sheet_name": ref["sheet_name"],
        "column_name": ref["column_name"],
        "normalized_header": normalized_name,
        "field_id": ref["field_id"],
        "question_id": ref["question_id"],
        "inferred_type": inferred_type,
        "row_count": row_count,
        "non_null_count": non_null_count,
        "null_count": null_count,
        "null_ratio": null_ratio,
        "cardinality": cardinality,
        "unique_ratio": unique_ratio,
        "uniqueness_class": uniqueness_class,
        "candidate_primary_key": candidate_primary_key,
        "sample_values": samples,
        "numeric_range": numeric_range,
        "date_range": date_range,
    }

    prefix = f"ev:column:{column_ref}"
    evidence = {
        f"{prefix}:type": {"kind": "COLUMN_TYPE", "column_ref": column_ref, "value": inferred_type},
        f"{prefix}:row_count": {"kind": "ROW_COUNT", "column_ref": column_ref, "value": row_count},
        f"{prefix}:null_ratio": {"kind": "NULL_RATIO", "column_ref": column_ref, "value": null_ratio},
        f"{prefix}:cardinality": {"kind": "CARDINALITY", "column_ref": column_ref, "value": cardinality},
        f"{prefix}:uniqueness": {"kind": "UNIQUENESS", "column_ref": column_ref, "value": uniqueness_class},
    }
    if numeric_range is not None:
        evidence[f"{prefix}:range"] = {"kind": "NUMERIC_RANGE", "column_ref": column_ref, "value": dict(numeric_range)}
    if date_range is not None:
        evidence[f"{prefix}:range"] = {"kind": "DATE_RANGE", "column_ref": column_ref, "value": dict(date_range)}
    return profile, evidence, canonical_values


def _candidate_relationship(
    *,
    left: dict[str, Any],
    right: dict[str, Any],
    left_values: tuple[str, ...],
    right_values: tuple[str, ...],
) -> dict[str, Any] | None:
    if not left_values or not right_values:
        return None
    left_set = set(left_values)
    right_set = set(right_values)
    if not left_set or not right_set:
        return None
    intersection = left_set.intersection(right_set)
    if not intersection:
        return None

    left_coverage = len(intersection) / len(left_set)
    right_coverage = len(intersection) / len(right_set)
    same_header = left["normalized_header"] == right["normalized_header"]
    right_is_key = bool(right["candidate_primary_key"])
    left_is_key = bool(left["candidate_primary_key"])

    relationship_kind: str | None = None
    candidate_foreign_key = False
    if right_is_key and left_coverage >= RELATIONSHIP_OVERLAP_THRESHOLD:
        candidate_foreign_key = True
        relationship_kind = "ONE_TO_ONE" if left_is_key else "MANY_TO_ONE"
    elif (
        same_header
        and not left_is_key
        and not right_is_key
        and min(left_coverage, right_coverage) >= RELATIONSHIP_OVERLAP_THRESHOLD
    ):
        relationship_kind = "STRUCTURAL_OVERLAP"
    else:
        return None

    return {
        "relationship_ref": f"{left['column_ref']}->{right['column_ref']}",
        "left_column_ref": left["column_ref"],
        "right_column_ref": right["column_ref"],
        "relationship_kind": relationship_kind,
        "same_normalized_header": same_header,
        "left_value_coverage": left_coverage,
        "right_value_coverage": right_coverage,
        "candidate_foreign_key": candidate_foreign_key,
        "candidate_primary_key_ref": right["column_ref"] if candidate_foreign_key else None,
        "intersection_cardinality": len(intersection),
    }


def _relationship_evidence(relationship: dict[str, Any]) -> dict[str, dict[str, Any]]:
    ref = relationship["relationship_ref"]
    prefix = f"ev:relationship:{ref}"
    return {
        f"{prefix}:overlap": {
            "kind": "RELATIONSHIP_OVERLAP",
            "relationship_ref": ref,
            "left_value_coverage": relationship["left_value_coverage"],
            "right_value_coverage": relationship["right_value_coverage"],
            "intersection_cardinality": relationship["intersection_cardinality"],
        },
        f"{prefix}:kind": {
            "kind": "RELATIONSHIP_KIND",
            "relationship_ref": ref,
            "value": relationship["relationship_kind"],
        },
    }


def _column_identity(sheet_name: str, column_name: str) -> str:
    return f"{sheet_name}.{column_name}"


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _canonical_scalar(value: Any) -> str:
    return str(value).strip().casefold()


def _bounded_samples(values: list[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values:
        key = _canonical_scalar(value)
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
        if len(result) >= MAX_SAMPLE_VALUES:
            break
    return result


def _uniqueness_class(*, row_count: int, non_null_count: int, cardinality: int, unique_ratio: float) -> str:
    if non_null_count == 0:
        return "EMPTY"
    if cardinality == 1:
        return "CONSTANT"
    if cardinality == non_null_count:
        return "UNIQUE"
    if unique_ratio >= 0.90:
        return "MOSTLY_UNIQUE"
    return "NON_UNIQUE"


def _infer_type(values: list[Any]) -> str:
    if not values:
        return "empty"
    kinds: set[str] = set()
    for value in values:
        if _parse_date(value) is not None:
            kinds.add("date")
            continue
        if _parse_number(value) is not None:
            kinds.add("number")
            continue
        kinds.add("text")
    return next(iter(kinds)) if len(kinds) == 1 else "mixed"


def _parse_number(value: Any) -> float | None:
    try:
        number = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def _numeric_range(values: list[Any]) -> dict[str, float] | None:
    numbers = [_parse_number(value) for value in values]
    if not numbers or any(value is None for value in numbers):
        return None
    clean = [float(value) for value in numbers if value is not None]
    return {"min": min(clean), "max": max(clean)}


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for candidate in (text, text[:10]):
        try:
            return date.fromisoformat(candidate)
        except ValueError:
            pass
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def _date_range(values: list[Any]) -> dict[str, str] | None:
    parsed = [_parse_date(value) for value in values]
    if not parsed or any(value is None for value in parsed):
        return None
    clean = [value for value in parsed if value is not None]
    return {"min": min(clean).isoformat(), "max": max(clean).isoformat()}


def _blocked(reason: str, *, ingestion_output: dict[str, Any] | None = None, detail: Any = None) -> dict[str, Any]:
    source = ingestion_output or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": detail,
        "case_id": source.get("case_id"),
        "source_file_ref": source.get("source_file_ref") or source.get("filename"),
        "sheet_names": [],
        "column_count": 0,
        "relationship_count": 0,
        "columns": [],
        "relationships": [],
        "evidence_registry": {},
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
    "BLOCK_INPUT_NOT_DICT",
    "BLOCK_INPUT_AUTHORITY_FORBIDDEN",
    "BLOCK_SOURCE_TABLES_MISSING",
    "BLOCK_SOURCE_TABLE_INVALID",
    "BLOCK_COLUMN_REFS_MISSING",
    "BLOCK_COLUMN_REF_INVALID",
    "BLOCK_COLUMN_REF_NOT_FOUND",
    "BLOCK_DUPLICATE_COLUMN_REF",
    "RELATIONSHIP_OVERLAP_THRESHOLD",
    "build_service_1_workbook_profile_v1",
]

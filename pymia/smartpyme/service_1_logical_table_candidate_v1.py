"""Minimum logical-table candidate contract for Workbook Logical Model D2.

The contract is evidence-only. It projects physical regions and existing
WorkbookProfiler evidence into stable candidates without assigning business
meaning, executing joins, or changing P7 grain authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from itertools import combinations
from typing import Any, Final, Mapping, Literal

from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    STATUS_READY as WORKBOOK_PROFILE_READY,
    build_service_1_workbook_profile_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_LOGICAL_TABLE_CANDIDATE_V1"
STATUS_READY: Final[str] = "LOGICAL_TABLE_CANDIDATES_READY"
STATUS_UNRESOLVED: Final[str] = "UNRESOLVED"
STATUS_BLOCKED: Final[str] = "BLOCKED"

GRAIN_RESOLVED: Final[str] = "RESOLVED"
GRAIN_UNRESOLVED: Final[str] = "UNRESOLVED"
GrainState = Literal["RESOLVED", "UNRESOLVED"]


@dataclass(frozen=True)
class Service1LogicalTableCandidateV1:
    candidate_id: str
    logical_table_id: str
    workbook_ref: str
    source_region_refs: tuple[str, ...]
    source_sheet_refs: tuple[str, ...]
    structural_signature: str
    grain_state: GrainState
    grain_candidate: dict[str, Any] | None
    primary_key_candidates: tuple[dict[str, Any], ...] = ()
    unique_key_candidates: tuple[dict[str, Any], ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "logical_table_id",
            "workbook_ref",
            "structural_signature",
        ):
            value = str(getattr(self, name) or "").strip()
            if not value:
                raise ValueError(f"{name} must be a non-empty string")
            object.__setattr__(self, name, value)
        for name in ("source_region_refs", "source_sheet_refs"):
            values = tuple(str(item).strip() for item in getattr(self, name))
            if not values or any(not item for item in values) or len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique non-empty values")
            object.__setattr__(self, name, values)
        if self.grain_state not in {GRAIN_RESOLVED, GRAIN_UNRESOLVED}:
            raise ValueError("unsupported grain_state")
        if self.grain_state == GRAIN_RESOLVED and not isinstance(self.grain_candidate, dict):
            raise ValueError("resolved grain requires grain_candidate evidence")
        if self.grain_state == GRAIN_UNRESOLVED and self.grain_candidate is not None and not isinstance(self.grain_candidate, dict):
            raise ValueError("unresolved grain_candidate must be a mapping or None")
        object.__setattr__(
            self,
            "primary_key_candidates",
            tuple(dict(item) for item in self.primary_key_candidates),
        )
        object.__setattr__(
            self,
            "unique_key_candidates",
            tuple(dict(item) for item in self.unique_key_candidates),
        )
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        ):
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


LogicalTableCandidateV1 = Service1LogicalTableCandidateV1


def build_service_1_logical_table_candidates_v1(
    *,
    canonical_packet: Mapping[str, Any],
    region_evidence: Mapping[str, Any],
    workbook_profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Project region evidence and profiler evidence into D2 candidates."""
    if not isinstance(canonical_packet, Mapping):
        return _blocked("CANONICAL_PACKET_NOT_DICT")
    if canonical_packet.get("status") != "INGESTION_OUTPUT_READY":
        return _blocked("CANONICAL_PACKET_NOT_READY")
    if _authority_flags_forbidden(canonical_packet):
        return _blocked("CANONICAL_PACKET_SAFETY_FLAGS_FORBIDDEN")
    if not isinstance(region_evidence, Mapping):
        return _blocked("REGION_EVIDENCE_NOT_DICT")
    if region_evidence.get("status") == STATUS_UNRESOLVED:
        return _unresolved(str(region_evidence.get("blocked_reason") or "REGION_EVIDENCE_UNRESOLVED"))
    if region_evidence.get("status") != "REGION_EVIDENCE_READY":
        return _blocked("REGION_EVIDENCE_NOT_READY")
    if any(bool(region_evidence.get(flag)) for flag in (
        "runtime_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    )):
        return _blocked("REGION_EVIDENCE_SAFETY_FLAGS_FORBIDDEN")

    output = canonical_packet.get("ingestion_output")
    if not isinstance(output, Mapping):
        return _blocked("INGESTION_OUTPUT_REQUIRED")
    tables = output.get("normalized_tables")
    regions = region_evidence.get("regions")
    if not isinstance(tables, list) or not tables or not isinstance(regions, list) or not regions:
        return _unresolved("REGIONS_REQUIRED")

    profile = workbook_profile
    if profile is None:
        profile = _build_profile_from_canonical_output(output)
    if not isinstance(profile, Mapping) or profile.get("status") != WORKBOOK_PROFILE_READY:
        return _unresolved("WORKBOOK_PROFILE_UNAVAILABLE")

    tables_by_sheet = {
        str(table.get("sheet_name") or "").strip(): table
        for table in tables
        if isinstance(table, Mapping)
    }
    profile_columns = [
        item for item in profile.get("columns") or [] if isinstance(item, Mapping)
    ]
    candidates: list[Service1LogicalTableCandidateV1] = []
    for region_index, region in enumerate(regions, start=1):
        if not isinstance(region, Mapping):
            return _unresolved("REGION_RECORD_INVALID")
        sheet = str(region.get("sheet_ref") or "").strip()
        region_ref = str(region.get("region_ref") or "").strip()
        table = tables_by_sheet.get(sheet)
        if not sheet or not region_ref or table is None:
            return _unresolved("REGION_SOURCE_NOT_FOUND")
        region_profile_columns = _profile_columns_for_region(
            region=region,
            table=table,
            profile_columns=profile_columns,
            workbook_ref=str(output.get("source_file_ref") or output.get("filename") or "").strip(),
        )
        if region_profile_columns is None:
            return _unresolved("REGION_PROFILE_UNAVAILABLE")
        candidate = _build_candidate(
            region=region,
            table=table,
            profile_columns=region_profile_columns,
            workbook_ref=str(output.get("source_file_ref") or output.get("filename") or "").strip(),
            region_index=region_index,
        )
        if candidate is None:
            return _unresolved("LOGICAL_TABLE_CANDIDATE_UNRESOLVED")
        candidates.append(candidate)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "workbook_ref": str(output.get("source_file_ref") or output.get("filename") or "").strip(),
        "candidates": [candidate.to_dict() for candidate in candidates],
        "candidate_count": len(candidates),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _build_candidate(
    *,
    region: Mapping[str, Any],
    table: Mapping[str, Any],
    profile_columns: list[Mapping[str, Any]],
    workbook_ref: str,
    region_index: int,
) -> Service1LogicalTableCandidateV1 | None:
    sheet = str(region.get("sheet_ref") or "").strip()
    region_ref = str(region.get("region_ref") or "").strip()
    column_refs = tuple(str(value).strip() for value in region.get("column_refs") or ())
    if not sheet or not region_ref or not column_refs or not workbook_ref:
        return None
    matching = [
        item
        for item in profile_columns
        if str(item.get("sheet_name") or "").strip() == sheet
        and str(item.get("normalized_header") or "").strip() in set(column_refs)
    ]
    by_header = {
        str(item.get("normalized_header") or "").strip(): item
        for item in matching
    }
    if any(header not in by_header for header in column_refs):
        return None

    primary_candidates: list[dict[str, Any]] = []
    unique_candidates: list[dict[str, Any]] = []
    for header in column_refs:
        profile = by_header[header]
        column_ref = f"{region_ref}.{header}"
        evidence_ref = f"ev:column:{profile.get('column_ref')}:" + "uniqueness"
        key_record = {
            "column_refs": [column_ref],
            "key_kind": "SINGLE_COLUMN",
            "evidence_refs": [evidence_ref],
            "candidate_primary_key": bool(profile.get("candidate_primary_key") is True),
            "authoritative": False,
        }
        if profile.get("uniqueness_class") == "UNIQUE":
            unique_candidates.append(dict(key_record))
        if profile.get("candidate_primary_key") is True:
            primary_candidates.append(dict(key_record))

    rows = _region_rows(table=table, region=region, column_refs=column_refs)
    composite_candidates = _composite_key_candidates(rows=rows, column_refs=column_refs, region_ref=region_ref)
    unique_candidates.extend(composite_candidates)
    if not primary_candidates:
        primary_candidates.extend(composite_candidates)

    grain_state: GrainState
    grain_candidate: dict[str, Any] | None
    if len(primary_candidates) == 1:
        grain_state = GRAIN_RESOLVED
        grain_candidate = {
            "kind": "ROW_KEYED_BY_CANDIDATE",
            "key_refs": list(primary_candidates[0]["column_refs"]),
            "evidence_refs": list(primary_candidates[0]["evidence_refs"]),
            "authoritative": False,
        }
    elif len(primary_candidates) > 1:
        grain_state = GRAIN_UNRESOLVED
        grain_candidate = {
            "kind": "AMBIGUOUS_CANDIDATE_KEYS",
            "candidate_key_refs": [list(item["column_refs"]) for item in primary_candidates],
            "authoritative": False,
        }
    else:
        grain_state = GRAIN_UNRESOLVED
        grain_candidate = None

    structural_payload = {
        "contract": SCHEMA_VERSION,
        "region_shape": str(region.get("region_shape") or ""),
        "columns": [
            {
                "position": index,
                "normalized_header": header,
                "inferred_type": str(by_header[header].get("inferred_type") or "unknown"),
                "nullability_class": _nullability_class(by_header[header].get("null_ratio")),
                "uniqueness_class": str(by_header[header].get("uniqueness_class") or "UNKNOWN"),
                "candidate_primary_key": bool(by_header[header].get("candidate_primary_key") is True),
            }
            for index, header in enumerate(column_refs)
        ],
    }
    structural_signature = build_service_1_structural_digest_v1(
        payload=structural_payload,
        prefix="ltf_",
    )
    logical_table_id = f"lt_{structural_signature[4:28]}_r{region_index}"
    provenance = {
        "source": SCHEMA_VERSION,
        "workbook_ref": workbook_ref,
        "sheet_ref": sheet,
        "region_ref": region_ref,
        "physical_row_numbers": list(region.get("provenance", {}).get("data_row_numbers") or ()),
        "structural_payload": structural_payload,
        "authority": "EVIDENCE_ONLY",
    }
    return Service1LogicalTableCandidateV1(
        candidate_id=logical_table_id,
        logical_table_id=logical_table_id,
        workbook_ref=workbook_ref,
        source_region_refs=(region_ref,),
        source_sheet_refs=(sheet,),
        structural_signature=structural_signature,
        grain_state=grain_state,
        grain_candidate=grain_candidate,
        primary_key_candidates=tuple(primary_candidates),
        unique_key_candidates=tuple(unique_candidates),
        provenance=provenance,
    )


def _profile_columns_for_region(
    *,
    region: Mapping[str, Any],
    table: Mapping[str, Any],
    profile_columns: list[Mapping[str, Any]],
    workbook_ref: str,
) -> list[Mapping[str, Any]] | None:
    sheet = str(region.get("sheet_ref") or "").strip()
    headers = {str(value).strip() for value in region.get("column_refs") or ()}
    matching = [
        item
        for item in profile_columns
        if str(item.get("sheet_name") or "").strip() == sheet
        and str(item.get("normalized_header") or "").strip() in headers
    ]
    if len(matching) == len(headers):
        return matching
    local_profile = _build_profile_for_region(
        region=region,
        table=table,
        workbook_ref=workbook_ref,
    )
    if local_profile is None:
        return None
    return [
        item
        for item in local_profile.get("columns") or []
        if isinstance(item, Mapping)
    ]


def _build_profile_for_region(
    *,
    region: Mapping[str, Any],
    table: Mapping[str, Any],
    workbook_ref: str,
) -> dict[str, Any] | None:
    headers = tuple(str(value).strip() for value in region.get("column_refs") or ())
    rows = _region_rows(table=table, region=region, column_refs=headers)
    if not headers or not rows:
        return None
    sheet = str(region.get("sheet_ref") or "").strip()
    source_rows = [
        int(value)
        for value in (region.get("provenance", {}).get("data_row_numbers") or ())
    ]
    if len(source_rows) != len(rows):
        source_rows = list(range(2, 2 + len(rows)))
    table_payload = {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": "OK",
        "source_kind": "xlsx",
        "source_path": workbook_ref,
        "sheet_name": sheet,
        "headers": list(headers),
        "normalized_headers": list(headers),
        "rows": rows,
        "header_row_number": int((region.get("header_rows") or [1])[0]),
        "source_row_numbers": source_rows,
        "row_count": len(rows),
        "column_count": len(headers),
        "warnings": [],
        "blocking_errors": [],
        "runtime_authorized": False,
    }
    profile_input = {
        "case_id": "d2-region-profile",
        "source_file_ref": workbook_ref,
        "normalized_tables": [table_payload],
        "column_refs": [
            {
                "sheet_name": sheet,
                "column_name": header,
                "normalized_column_name": header,
                "field_id": f"d2:{sheet}:{header}",
                "question_id": f"d2:{sheet}:{header}",
            }
            for header in headers
        ],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    profile = build_service_1_workbook_profile_v1(ingestion_output=profile_input)
    return profile if profile.get("status") == WORKBOOK_PROFILE_READY else None


def _build_profile_from_canonical_output(output: Mapping[str, Any]) -> dict[str, Any]:
    profile_input = dict(output)
    column_refs: list[dict[str, str]] = []
    for table in output.get("normalized_tables") or []:
        if not isinstance(table, Mapping):
            continue
        sheet = str(table.get("sheet_name") or "").strip()
        for header, normalized in zip(
            table.get("headers") or (),
            table.get("normalized_headers") or (),
        ):
            column_refs.append(
                {
                    "sheet_name": sheet,
                    "column_name": str(header),
                    "normalized_column_name": str(normalized),
                    "field_id": f"d2:{sheet}:{normalized}",
                    "question_id": f"d2:{sheet}:{normalized}",
                }
            )
    profile_input["column_refs"] = column_refs
    return build_service_1_workbook_profile_v1(ingestion_output=profile_input)


def _region_rows(
    *,
    table: Mapping[str, Any],
    region: Mapping[str, Any],
    column_refs: tuple[str, ...],
) -> list[dict[str, str]]:
    provenance = region.get("provenance") if isinstance(region.get("provenance"), Mapping) else {}
    positions = [int(value) for value in provenance.get("physical_column_indexes") or ()]
    requested_numbers = [int(value) for value in provenance.get("data_row_numbers") or ()]
    physical_rows = table.get("physical_rows")
    if isinstance(physical_rows, list) and positions and requested_numbers:
        by_number = {
            int(item.get("row_number")): list(item.get("cells") or [])
            for item in physical_rows
            if isinstance(item, Mapping) and item.get("row_number") is not None
        }
        return [
            {
                header: _clean(cells[position]) if position < len(cells) else ""
                for header, position in zip(column_refs, positions)
            }
            for number in requested_numbers
            if (cells := by_number.get(number)) is not None
        ]
    normalized_headers = [str(value).strip() for value in table.get("normalized_headers") or ()]
    rows = [row for row in table.get("rows") or () if isinstance(row, Mapping)]
    source_numbers = [int(value) for value in table.get("source_row_numbers") or ()]
    requested = set(requested_numbers)
    return [
        {header: _clean(row.get(header, "")) for header in column_refs}
        for number, row in zip(source_numbers, rows)
        if not requested or number in requested
        and all(header in normalized_headers for header in column_refs)
    ]


def _composite_key_candidates(
    *,
    rows: list[dict[str, str]],
    column_refs: tuple[str, ...],
    region_ref: str,
) -> list[dict[str, Any]]:
    if len(column_refs) < 2 or not rows:
        return []
    candidates: list[dict[str, Any]] = []
    for left, right in combinations(column_refs[:12], 2):
        pairs = [(row.get(left, ""), row.get(right, "")) for row in rows]
        if not pairs or any(not left_value or not right_value for left_value, right_value in pairs):
            continue
        if len(set(pairs)) != len(pairs):
            continue
        candidates.append(
            {
                "column_refs": [f"{region_ref}.{left}", f"{region_ref}.{right}"],
                "key_kind": "COMPOSITE_UNIQUE",
                "evidence_refs": [f"ev:region:{region_ref}:composite:{left}+{right}"],
                "candidate_primary_key": True,
                "authoritative": False,
            }
        )
        if len(candidates) >= 8:
            break
    return candidates


def _nullability_class(value: Any) -> str:
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        return "UNKNOWN"
    if ratio <= 0:
        return "NONE"
    if ratio <= 0.05:
        return "LOW"
    if ratio < 1:
        return "MATERIAL"
    return "ALL_NULL"


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _authority_flags_forbidden(value: Mapping[str, Any]) -> bool:
    return any(
        bool(value.get(flag))
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        )
    )


def _unresolved(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_UNRESOLVED,
        "blocked_reason": reason,
        "candidates": [],
        "candidate_count": 0,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    payload = _unresolved(reason)
    payload["status"] = STATUS_BLOCKED
    return payload


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_UNRESOLVED",
    "STATUS_BLOCKED",
    "GRAIN_RESOLVED",
    "GRAIN_UNRESOLVED",
    "Service1LogicalTableCandidateV1",
    "LogicalTableCandidateV1",
    "build_service_1_logical_table_candidates_v1",
]

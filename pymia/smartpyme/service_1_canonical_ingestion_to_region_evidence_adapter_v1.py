"""Temporary canonical-ingestion projection for Stage 2 Package 1.

Consumes normalized tables already produced by the canonical XLSX path. It does
not read files and cannot authorize runtime, tools, diagnosis or delivery.
"""
from __future__ import annotations

from datetime import datetime
from math import isclose
from typing import Any

from pymia.smartpyme.service_1_region_physical_evidence_contracts_v1 import (
    REGION_SHAPE_RECTANGULAR,
    Service1ColumnPhysicalEvidenceV1,
    Service1RegionRelationalEvidenceV1,
    Service1RegionV1,
)

SCHEMA_VERSION = "SERVICE_1_CANONICAL_INGESTION_TO_REGION_EVIDENCE_ADAPTER_V1"
STATUS_READY = "REGION_EVIDENCE_READY"
STATUS_BLOCKED = "BLOCKED"


def build_service_1_region_evidence_from_canonical_ingestion_v1(
    *,
    canonical_packet: Any,
    region_specs: list[dict[str, Any]] | None = None,
    identity_specs: list[dict[str, Any]] | None = None,
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked("REQUEST_SAFETY_FLAGS_FORBIDDEN")
    if not isinstance(canonical_packet, dict) or canonical_packet.get("status") != "INGESTION_OUTPUT_READY":
        return _blocked("CANONICAL_PACKET_NOT_READY")
    if canonical_packet.get("runtime_authorized") or canonical_packet.get("product_ready") or canonical_packet.get("delivery_authorized"):
        return _blocked("CANONICAL_PACKET_SAFETY_FLAGS_FORBIDDEN")
    output = canonical_packet.get("ingestion_output")
    if not isinstance(output, dict):
        return _blocked("INGESTION_OUTPUT_REQUIRED")
    tables = output.get("normalized_tables")
    if not isinstance(tables, list) or not tables:
        return _blocked("NORMALIZED_TABLES_REQUIRED")

    case_id = str(output.get("case_id") or canonical_packet.get("case_id") or "").strip()
    file_ref = str(output.get("source_file_ref") or canonical_packet.get("filename") or "").strip()
    if not case_id or not file_ref:
        return _blocked("CASE_AND_FILE_REF_REQUIRED")

    table_by_sheet = {str(t.get("sheet_name") or "sheet1").strip(): t for t in tables if isinstance(t, dict)}
    specs = region_specs or [_default_spec(sheet, table) for sheet, table in table_by_sheet.items()]
    regions: list[Service1RegionV1] = []
    columns: list[Service1ColumnPhysicalEvidenceV1] = []
    relations: list[Service1RegionRelationalEvidenceV1] = []

    try:
        for index, spec in enumerate(specs, start=1):
            sheet = str(spec.get("sheet_ref") or "").strip()
            table = table_by_sheet.get(sheet)
            if table is None:
                return _blocked("REGION_SHEET_NOT_FOUND", detail=[sheet])
            if spec.get("region_shape", REGION_SHAPE_RECTANGULAR) != REGION_SHAPE_RECTANGULAR:
                return _blocked("UNSUPPORTED_REGION_SHAPE")
            normalized_headers = [str(v).strip() for v in table.get("normalized_headers") or []]
            selected = [str(v).strip() for v in spec.get("column_refs") or normalized_headers]
            if not selected or any(ref not in normalized_headers for ref in selected):
                return _blocked("INVALID_REGION_COLUMNS")
            positions = [normalized_headers.index(ref) for ref in selected]
            if positions != list(range(min(positions), max(positions) + 1)):
                return _blocked("DISCONTIGUOUS_REGION_COLUMNS")
            rows = [row for row in table.get("rows") or [] if isinstance(row, dict)]
            first_data_row = int(spec.get("first_data_row", 2))
            last_data_row = int(spec.get("last_data_row", len(rows) + 1))
            excluded = tuple(int(v) for v in spec.get("excluded_rows") or ())
            region_ref = str(spec.get("region_ref") or f"{sheet}:region:{index}")
            region = Service1RegionV1(
                case_id=case_id, file_ref=file_ref, workbook_ref=file_ref,
                sheet_ref=sheet, region_ref=region_ref,
                header_rows=tuple(spec.get("header_rows") or (1,)),
                first_data_row=first_data_row, last_data_row=last_data_row,
                column_refs=tuple(selected), excluded_rows=excluded,
                region_shape=REGION_SHAPE_RECTANGULAR,
                provenance={"source": SCHEMA_VERSION, "canonical_schema": canonical_packet.get("schema_version")},
                grain=dict(spec.get("grain") or {}),
            )
            regions.append(region)
            selected_rows = [
                (row_number, rows[row_number - 2])
                for row_number in range(first_data_row, last_data_row + 1)
                if row_number not in excluded and 0 <= row_number - 2 < len(rows)
            ]
            for pos, ref in enumerate(selected):
                values = [row.get(ref, "") for _, row in selected_rows]
                columns.append(_column_evidence(region, ref, values, selected, pos))
            for identity_index, identity in enumerate(identity_specs or (), start=1):
                target_region = identity.get("region_ref")
                if target_region and target_region != region_ref:
                    continue
                relations.append(_relational_evidence(region, selected_rows, identity, identity_index))
    except (TypeError, ValueError) as exc:
        return _blocked("CONTRACT_VALIDATION_FAILED", detail=[str(exc)])

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "regions": [item.to_dict() for item in regions],
        "column_evidence": [item.to_dict() for item in columns],
        "relational_evidence": [item.to_dict() for item in relations],
        "temporary_adapter": True,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _default_spec(sheet: str, table: dict[str, Any]) -> dict[str, Any]:
    return {"sheet_ref": sheet, "region_ref": f"{sheet}:region:1", "column_refs": list(table.get("normalized_headers") or [])}


def _column_evidence(region: Service1RegionV1, ref: str, values: list[Any], selected: list[str], pos: int) -> Service1ColumnPhysicalEvidenceV1:
    nonempty = [value for value in values if str(value).strip()]
    numbers: list[float] = []
    dates = 0
    for value in nonempty:
        text = str(value).strip()
        try:
            numbers.append(float(text.replace(",", ".")))
        except ValueError:
            try:
                datetime.fromisoformat(text)
            except ValueError:
                pass
            else:
                dates += 1
    if not nonempty:
        observed = "empty"
    elif len(numbers) == len(nonempty):
        observed = "number"
    elif dates == len(nonempty):
        observed = "date"
    elif not numbers and not dates:
        observed = "text"
    else:
        observed = "mixed"
    neighbors = tuple(selected[i] for i in (pos - 1, pos + 1) if 0 <= i < len(selected))
    return Service1ColumnPhysicalEvidenceV1(
        region_ref=region.region_ref, column_ref=ref, normalized_header=ref,
        observed_data_type=observed, sample_values=tuple(nonempty[:5]),
        null_ratio=(len(values) - len(nonempty)) / len(values) if values else 1.0,
        cardinality=len({str(v) for v in nonempty}),
        numeric_min=min(numbers) if numbers else None, numeric_max=max(numbers) if numbers else None,
        negative_count=sum(v < 0 for v in numbers), zero_count=sum(v == 0 for v in numbers),
        positive_count=sum(v > 0 for v in numbers), date_parseable_count=dates,
        neighbor_column_refs=neighbors,
        provenance={"region_ref": region.region_ref, "source_rows": [region.first_data_row, region.last_data_row]},
    )


def _relational_evidence(region: Service1RegionV1, rows: list[tuple[int, dict[str, Any]]], spec: dict[str, Any], index: int) -> Service1RegionRelationalEvidenceV1:
    kind = str(spec.get("evidence_kind") or "MULTIPLICATION_EQUALS")
    inputs = [str(v) for v in spec.get("input_column_refs") or []]
    target = str(spec.get("target_column_ref") or "")
    tolerance = float(spec.get("tolerance", 0.01))
    if kind != "MULTIPLICATION_EQUALS" or len(inputs) != 2 or not target:
        raise ValueError("unsupported identity specification")
    evaluated = matching = 0
    contradicting: list[int] = []
    for row_number, row in rows:
        try:
            left = float(str(row.get(inputs[0], "")).replace(",", "."))
            right = float(str(row.get(inputs[1], "")).replace(",", "."))
            expected = float(str(row.get(target, "")).replace(",", "."))
        except ValueError:
            continue
        evaluated += 1
        if isclose(left * right, expected, rel_tol=tolerance, abs_tol=tolerance):
            matching += 1
        else:
            contradicting.append(row_number)
    coverage = matching / evaluated if evaluated else 0.0
    result = "INSUFFICIENT_EVIDENCE" if evaluated == 0 else ("SUPPORTED" if coverage >= float(spec.get("minimum_coverage", 0.8)) else "CONTRADICTED")
    return Service1RegionRelationalEvidenceV1(
        region_ref=region.region_ref,
        evidence_ref=str(spec.get("evidence_ref") or f"{region.region_ref}:identity:{index}"),
        evidence_kind=kind,
        participating_column_refs=tuple(inputs + [target]),
        rows_evaluated=evaluated, rows_matching=matching, coverage_ratio=coverage,
        tolerance=tolerance, result=result, contradicting_rows=tuple(contradicting),
        provenance={"region_ref": region.region_ref, "identity_spec": dict(spec)},
    )


def _blocked(reason: str, detail: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "status": STATUS_BLOCKED,
        "blocked_reason": reason, "detail": list(detail or []),
        "regions": [], "column_evidence": [], "relational_evidence": [],
        "temporary_adapter": True, "runtime_authorized": False,
        "product_ready": False, "delivery_authorized": False,
    }


__all__ = ["SCHEMA_VERSION", "STATUS_READY", "STATUS_BLOCKED", "build_service_1_region_evidence_from_canonical_ingestion_v1"]

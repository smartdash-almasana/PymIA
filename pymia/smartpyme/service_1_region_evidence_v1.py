"""Canonical region-evidence projection for Servicio 1.

Consumes normalized tables already produced by the single canonical XLSX path,
uses the deterministic D1 physical-region detector, and materializes the
existing Service1RegionV1 evidence contracts.  It does not read files and
cannot authorize runtime, tools, diagnosis, computation, joins, or delivery.
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
from pymia.smartpyme.service_1_physical_region_detection_v1 import (
    STATUS_READY as PHYSICAL_REGIONS_READY,
    STATUS_UNRESOLVED as PHYSICAL_REGIONS_UNRESOLVED,
    detect_service_1_physical_regions_v1,
)

SCHEMA_VERSION = "SERVICE_1_REGION_EVIDENCE_V1"
STATUS_READY = "REGION_EVIDENCE_READY"
STATUS_UNRESOLVED = "UNRESOLVED"
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

    workbook_context = output.get("workbook_context")
    provenance = output.get("provenance")
    if not isinstance(workbook_context, dict) or not isinstance(provenance, dict):
        return _blocked("CANONICAL_IDENTITY_PROVENANCE_REQUIRED")
    case_id = str(workbook_context.get("case_id") or "").strip()
    file_ref = str(provenance.get("source_file_ref") or provenance.get("filename") or "").strip()
    if not case_id or not file_ref:
        return _blocked("CASE_AND_FILE_REF_REQUIRED")

    table_by_sheet: dict[str, dict[str, Any]] = {}
    for raw_table in tables:
        if not isinstance(raw_table, dict):
            return _blocked("NORMALIZED_TABLE_RECORD_INVALID")
        sheet = str(raw_table.get("sheet_name") or "").strip()
        if not sheet:
            return _blocked("NORMALIZED_TABLE_SHEET_REF_REQUIRED")
        if sheet in table_by_sheet:
            return _blocked("NORMALIZED_TABLE_SHEET_REF_AMBIGUOUS", detail=[sheet])
        table_by_sheet[sheet] = raw_table
    detection_results: list[dict[str, Any]] = []
    if region_specs is None:
        auto_specs: list[dict[str, Any]] = []
        for table in table_by_sheet.values():
            detection = detect_service_1_physical_regions_v1(normalized_table=table)
            detection_results.append(detection)
            if detection.get("status") == PHYSICAL_REGIONS_UNRESOLVED:
                return _unresolved(
                    "PHYSICAL_REGION_BOUNDARY_UNRESOLVED",
                    detail=[str(detection.get("detail") or "")],
                )
            if detection.get("status") != PHYSICAL_REGIONS_READY:
                return _blocked(
                    "PHYSICAL_REGION_DETECTION_FAILED",
                    detail=[str(detection.get("blocked_reason") or "")],
                )
            auto_specs.extend(detection.get("region_specs") or [])
        specs = auto_specs
    else:
        specs = list(region_specs)
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
            if not selected:
                return _blocked("INVALID_REGION_COLUMNS")
            positions = _physical_positions(table=table, spec=spec, selected=selected, normalized_headers=normalized_headers)
            if positions is None:
                return _blocked("INVALID_REGION_COLUMNS")
            if positions != list(range(min(positions), max(positions) + 1)):
                return _blocked("DISCONTIGUOUS_REGION_COLUMNS")
            rows = [row for row in table.get("rows") or [] if isinstance(row, dict)]
            source_row_numbers = [int(v) for v in table.get("source_row_numbers") or []]
            header_row_number = table.get("header_row_number")
            if len(source_row_numbers) != len(rows) and not table.get("physical_rows"):
                return _blocked("ROW_PROVENANCE_REQUIRED")
            header_rows = tuple(spec.get("header_rows") or ((int(header_row_number),) if header_row_number is not None else ()))
            if not header_rows:
                return _blocked("ROW_PROVENANCE_REQUIRED")
            selected_rows = _selected_rows(
                table=table,
                spec=spec,
                selected=selected,
                positions=positions,
                rows=rows,
                source_row_numbers=source_row_numbers,
            )
            selected_numbers = [row_number for row_number, _ in selected_rows]
            if not selected_numbers:
                return _unresolved("REGION_DATA_ROWS_UNRESOLVED", detail=[sheet])
            first_data_row = int(spec.get("first_data_row", min(selected_numbers)))
            last_data_row = int(spec.get("last_data_row", max(selected_numbers)))
            excluded = tuple(int(v) for v in spec.get("excluded_rows") or ())
            region_ref = str(spec.get("region_ref") or f"{sheet}:region:{index}")
            region = Service1RegionV1(
                case_id=case_id, file_ref=file_ref, workbook_ref=file_ref,
                sheet_ref=sheet, region_ref=region_ref,
                header_rows=header_rows,
                first_data_row=first_data_row, last_data_row=last_data_row,
                column_refs=tuple(selected), excluded_rows=excluded,
                region_shape=REGION_SHAPE_RECTANGULAR,
                provenance={
                    "source": SCHEMA_VERSION,
                    "canonical_schema": canonical_packet.get("schema_version"),
                    "detection_evidence": dict(spec.get("detection_evidence") or {}),
                    "physical_column_indexes": list(spec.get("physical_column_indexes") or positions),
                    "data_row_numbers": list(spec.get("data_row_numbers") or selected_numbers),
                },
                grain=dict(spec.get("grain") or {}),
            )
            regions.append(region)
            selected_rows = [
                (source_row_number, row)
                for source_row_number, row in selected_rows
                if first_data_row <= source_row_number <= last_data_row and source_row_number not in excluded
            ]
            for pos, ref in enumerate(selected):
                values = [row.get(ref, "") for _, row in selected_rows]
                source_rows = [row_number for row_number, _ in selected_rows]
                columns.append(_column_evidence(region, ref, values, source_rows, selected, pos))
            for identity_index, identity in enumerate(identity_specs or (), start=1):
                target_region = identity.get("region_ref")
                if target_region and target_region != region_ref:
                    continue
                identity_columns = [str(v).strip() for v in identity.get("input_column_refs") or []] + [str(identity.get("target_column_ref") or "").strip()]
                if any(not ref or ref not in region.column_refs for ref in identity_columns):
                    return _blocked("INVALID_IDENTITY_COLUMNS", detail=identity_columns)
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
        "physical_region_detection": detection_results,
        "canonical_region_evidence": True,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _default_spec(sheet: str, table: dict[str, Any]) -> dict[str, Any]:
    return {"sheet_ref": sheet, "region_ref": f"{sheet}:region:1", "column_refs": list(table.get("normalized_headers") or [])}


def _physical_positions(
    *,
    table: dict[str, Any],
    spec: dict[str, Any],
    selected: list[str],
    normalized_headers: list[str],
) -> list[int] | None:
    explicit_positions = spec.get("physical_column_indexes")
    if isinstance(explicit_positions, list) and len(explicit_positions) == len(selected):
        try:
            positions = [int(value) for value in explicit_positions]
        except (TypeError, ValueError):
            return None
        return positions if all(value >= 0 for value in positions) else None
    if any(ref not in normalized_headers for ref in selected):
        return None
    return [normalized_headers.index(ref) for ref in selected]


def _selected_rows(
    *,
    table: dict[str, Any],
    spec: dict[str, Any],
    selected: list[str],
    positions: list[int],
    rows: list[dict[str, Any]],
    source_row_numbers: list[int],
) -> list[tuple[int, dict[str, Any]]]:
    physical_rows = table.get("physical_rows")
    requested_numbers = spec.get("data_row_numbers")
    if isinstance(physical_rows, list) and isinstance(requested_numbers, list):
        by_number = {
            int(item.get("row_number")): list(item.get("cells") or [])
            for item in physical_rows
            if isinstance(item, dict) and item.get("row_number") is not None
        }
        selected_rows: list[tuple[int, dict[str, Any]]] = []
        for raw_number in requested_numbers:
            number = int(raw_number)
            cells = by_number.get(number)
            if cells is None:
                continue
            selected_rows.append(
                (
                    number,
                    {
                        ref: _clean(cells[position]) if position < len(cells) else ""
                        for ref, position in zip(selected, positions)
                    },
                )
            )
        return selected_rows
    return [
        (source_row_number, row)
        for source_row_number, row in zip(source_row_numbers, rows)
    ]


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _column_evidence(region: Service1RegionV1, ref: str, values: list[Any], source_rows: list[int], selected: list[str], pos: int) -> Service1ColumnPhysicalEvidenceV1:
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
        provenance={"region_ref": region.region_ref, "source_row_numbers": list(source_rows)},
    )


def _relational_evidence(region: Service1RegionV1, rows: list[tuple[int, dict[str, Any]]], spec: dict[str, Any], index: int) -> Service1RegionRelationalEvidenceV1:
    kind = str(spec.get("evidence_kind") or "MULTIPLICATION_EQUALS")
    inputs = [str(v) for v in spec.get("input_column_refs") or []]
    target = str(spec.get("target_column_ref") or "")
    tolerance = float(spec.get("tolerance", 0.01))
    if kind != "MULTIPLICATION_EQUALS" or len(inputs) != 2 or not target:
        raise ValueError("unsupported identity specification")
    eligible = len(rows)
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
    evaluation_coverage = evaluated / eligible if eligible else 0.0
    match_ratio = matching / evaluated if evaluated else 0.0
    minimum_evaluation_coverage = float(spec.get("minimum_evaluation_coverage", 0.8))
    minimum_match_ratio = float(spec.get("minimum_match_ratio", spec.get("minimum_coverage", 0.8)))
    if evaluated == 0 or evaluation_coverage < minimum_evaluation_coverage:
        result = "INSUFFICIENT_EVIDENCE"
    else:
        result = "SUPPORTED" if match_ratio >= minimum_match_ratio else "CONTRADICTED"
    return Service1RegionRelationalEvidenceV1(
        region_ref=region.region_ref,
        evidence_ref=str(spec.get("evidence_ref") or f"{region.region_ref}:identity:{index}"),
        evidence_kind=kind,
        participating_column_refs=tuple(inputs + [target]),
        rows_eligible=eligible, rows_evaluated=evaluated, rows_matching=matching,
        evaluation_coverage_ratio=evaluation_coverage, match_ratio=match_ratio,
        tolerance=tolerance, result=result, contradicting_rows=tuple(contradicting),
        provenance={"region_ref": region.region_ref, "source_row_numbers": [n for n, _ in rows], "identity_spec": dict(spec)},
    )


def _unresolved(reason: str, detail: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "status": STATUS_UNRESOLVED,
        "blocked_reason": reason, "detail": list(detail or []),
        "regions": [], "column_evidence": [], "relational_evidence": [],
        "physical_region_detection": [], "canonical_region_evidence": True,
        "runtime_authorized": False, "product_ready": False,
        "delivery_authorized": False,
    }


def _blocked(reason: str, detail: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "status": STATUS_BLOCKED,
        "blocked_reason": reason, "detail": list(detail or []),
        "regions": [], "column_evidence": [], "relational_evidence": [],
        "physical_region_detection": [],
        "canonical_region_evidence": True, "runtime_authorized": False,
        "product_ready": False, "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_UNRESOLVED",
    "STATUS_BLOCKED",
    "build_service_1_region_evidence_from_canonical_ingestion_v1",
]

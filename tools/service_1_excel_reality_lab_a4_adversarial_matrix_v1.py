from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.excel_lab_ingestion_v1 import curate_xlsx_document
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import build_service_1_p6_approval_decisions_v1
from pymia.smartpyme.service_1_variable_family_bindings_v1 import build_service_1_requirement_matches_v1
from pymia.smartpyme.service_1_computability_v1 import build_service_1_computability_decision_v1

SCHEMA_VERSION: Final[str] = "SERVICE_1_EXCEL_REALITY_LAB_A4_ADVERSARIAL_MATRIX_V1"
VERDICT_PASS: Final[str] = "PASS_ADVERSARIAL_MATRIX_V1"
VERDICT_FAIL: Final[str] = "FAIL_ADVERSARIAL_MATRIX_V1"
ROOT_DIR: Final[str] = "excel-prueba"

PASS_COMPUTABLE = "PASS_COMPUTABLE"
PASS_NEEDS_OWNER = "PASS_NEEDS_OWNER"
PASS_NEEDS_EVIDENCE = "PASS_NEEDS_EVIDENCE"
PASS_BLOCKED_FAIL_CLOSED = "PASS_BLOCKED_FAIL_CLOSED"
FAIL_DEFECT = "FAIL_DEFECT"


@dataclass(frozen=True)
class Spec:
    case_id: str
    filename: str
    pathology: str
    sheet_name: str
    capability: str | None = None
    expected_role_map: dict[str, str] | None = None


SPECS: Final[tuple[Spec, ...]] = (
    Spec("S1-A4-001", "S1_A4_ADV_001_mixed_currency.xlsx", "MIXED_CURRENCY", "Ventas"),
    Spec("S1-A4-002", "S1_A4_ADV_002_subtotal_as_operation.xlsx", "SUBTOTAL_AS_OPERATION", "Ventas"),
    Spec("S1-A4-003", "S1_A4_ADV_003_zero_vs_blank.xlsx", "ZERO_VS_BLANK", "Resumen"),
    Spec("S1-A4-004", "S1_A4_ADV_004_inverted_signs.xlsx", "INVERTED_SIGNS", "Caja"),
    Spec("S1-A4-005", "S1_A4_ADV_005_out_of_period_dates.xlsx", "OUT_OF_PERIOD_DATES", "Ventas"),
    Spec("S1-A4-006", "S1_A4_ADV_006_duplicate_rows.xlsx", "DUPLICATE_ROWS", "Ventas"),
    Spec("S1-A4-007", "S1_A4_ADV_007_mixed_granularity.xlsx", "MIXED_GRANULARITY", "Ventas"),
    Spec("S1-A4-008", "S1_A4_ADV_008_missing_material_input.xlsx", "MISSING_MATERIAL_INPUT", "Resumen", "net_margin_real", {
        "ventas_periodo": "period_sales_total", "cmv_total": "period_costs_total",
    }),
    Spec("S1-A4-009", "S1_A4_ADV_009_extreme_values.xlsx", "EXTREME_VALUES", "Resumen", "net_margin_real", {
        "ventas_periodo": "period_sales_total", "cmv_total": "period_costs_total", "impuestos_periodo": "period_taxes_total",
    }),
    Spec("S1-A4-010", "S1_A4_ADV_010_semantic_decoy_columns.xlsx", "SEMANTIC_DECOYS", "Ventas"),
    Spec("S1-A4-011", "S1_A4_ADV_011_incomplete_relationships.xlsx", "INCOMPLETE_RELATIONSHIPS", "Ventas"),
)


def _owner_answers(boundary: dict) -> dict[str, str]:
    return {
        str(q["field_id"]): f"La columna {q['column_name']} representa {q['column_name']}"
        for q in boundary.get("owner_questions", [])
    }


def _p8_for_spec(source: Path, spec: Spec) -> tuple[str | None, bool, str | None]:
    if spec.capability is None or spec.expected_role_map is None:
        return None, False, None
    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=source, sheet_name=spec.sheet_name
    )
    if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
        return None, False, f"INTAKE:{boundary.get('status')}:{boundary.get('blocked_reason')}"
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=boundary, owner_answers=_owner_answers(boundary)
    )
    if connector.get("status") != "INGESTION_OUTPUT_READY":
        return None, False, f"CONNECTOR:{connector.get('status')}:{connector.get('blocked_reason')}"
    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=connector["ingestion_output"], sheet_name=spec.sheet_name
    )
    candidates = tuple(bridge.get("column_candidates") or ())
    events = []
    for candidate in candidates:
        role = spec.expected_role_map.get(candidate.source_column_name)
        if role is None:
            continue
        events.append({
            "question_ref": candidate.metadata["column_ref_id"],
            "sheet_ref": candidate.sheet_name,
            "column_ref": candidate.source_column_name,
            "confirmed_by_owner": True,
            "confirmation_scope": "SEMANTIC_ROLE",
            "confirmed_role": role,
        })
    p6 = build_service_1_p6_approval_decisions_v1(
        case_id=bridge["case_id"], candidates=candidates, owner_confirmation_events=tuple(events)
    )
    p7 = build_service_1_requirement_matches_v1(p6)
    decision = build_service_1_computability_decision_v1(
        case_id=str(bridge["case_id"]), requested_capability=spec.capability,
        p6_decisions=[item.to_dict() for item in p6],
        requirement_matches=[item.to_dict() for item in p7],
    )
    return decision.status, decision.governed_computation_input is not None, None


def _has_duplicate_raw_rows(curated) -> bool:
    for table in curated.raw_tables:
        seen: set[str] = set()
        for record in table.records:
            key = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
            if key in seen:
                return True
            seen.add(key)
    return False


def _classify(spec: Spec, curated, p8_status: str | None, governed: bool, p8_error: str | None) -> tuple[str, str]:
    report = curated.report
    unknown = set(report.unknown_fields)
    ambiguous = set(report.ambiguous_fields)
    safe_signal = report.status == "BLOCKED" or bool(unknown or ambiguous)

    if p8_error is not None:
        return FAIL_DEFECT, p8_error

    if spec.pathology == "MISSING_MATERIAL_INPUT":
        return (PASS_NEEDS_EVIDENCE, "P8_NEEDS_EVIDENCE") if p8_status == "NEEDS_EVIDENCE" and not governed else (FAIL_DEFECT, f"P8={p8_status},governed={governed}")

    if spec.pathology == "EXTREME_VALUES":
        return (PASS_COMPUTABLE, "FINITE_EXTREME_VALUE_PRESERVED") if p8_status == "COMPUTABLE" and governed else (FAIL_DEFECT, f"P8={p8_status},governed={governed}")

    if spec.pathology == "ZERO_VS_BLANK":
        records = [record for table in curated.raw_tables for record in table.records]
        if not records:
            return FAIL_DEFECT, "ZERO_VS_BLANK_FIXTURE_NOT_INGESTED"
        record = records[0]
        zero_preserved = record.get("cobros_periodo") == 0
        blank_preserved = record.get("impuestos_periodo") is None
        if zero_preserved and blank_preserved:
            return PASS_NEEDS_EVIDENCE, "ZERO_PRESERVED_AND_BLANK_REMAINS_ABSENT"
        return FAIL_DEFECT, f"ZERO_PRESERVED={zero_preserved},BLANK_PRESERVED={blank_preserved}"

    if spec.pathology == "DUPLICATE_ROWS":
        duplicated = _has_duplicate_raw_rows(curated)
        if duplicated and safe_signal:
            return PASS_NEEDS_OWNER, "DUPLICATE_ROWS_PRESENT_WITH_SAFE_SIGNAL"
        if duplicated:
            return FAIL_DEFECT, "DUPLICATE_ROWS_PRESENT_WITHOUT_OWNER_OR_BLOCK_SIGNAL"
        return FAIL_DEFECT, "FIXTURE_DUPLICATE_ROWS_NOT_OBSERVED"

    if spec.pathology == "SUBTOTAL_AS_OPERATION":
        labels = {
            str(record.get("comprobante") or "").strip().upper()
            for table in curated.raw_tables for record in table.records
        }
        has_total_rows = bool(labels & {"SUBTOTAL", "TOTAL"})
        if has_total_rows and safe_signal:
            return PASS_NEEDS_OWNER, "TOTAL_ROWS_PRESENT_WITH_SAFE_SIGNAL"
        if has_total_rows:
            return FAIL_DEFECT, "TOTAL_ROWS_CAN_FLOW_AS_OPERATIONS_WITHOUT_SAFE_SIGNAL"
        return FAIL_DEFECT, "FIXTURE_TOTAL_ROWS_NOT_OBSERVED"

    if spec.pathology == "MIXED_CURRENCY":
        currencies = {
            str(record.get("moneda") or "").strip().upper()
            for table in curated.raw_tables for record in table.records
            if record.get("moneda") is not None
        }
        if len(currencies) > 1 and safe_signal:
            return PASS_NEEDS_OWNER, "MIXED_CURRENCY_WITH_SAFE_SIGNAL"
        if len(currencies) > 1:
            return FAIL_DEFECT, "MIXED_CURRENCY_WITHOUT_OWNER_OR_BLOCK_SIGNAL"
        return FAIL_DEFECT, "FIXTURE_MIXED_CURRENCY_NOT_OBSERVED"

    if spec.pathology in {"INVERTED_SIGNS", "OUT_OF_PERIOD_DATES", "MIXED_GRANULARITY", "SEMANTIC_DECOYS", "INCOMPLETE_RELATIONSHIPS"}:
        if report.status == "BLOCKED":
            return PASS_BLOCKED_FAIL_CLOSED, "CURATION_BLOCKED"
        if safe_signal:
            return PASS_NEEDS_OWNER, "UNKNOWN_OR_AMBIGUOUS_EVIDENCE_REQUIRES_OWNER"
        return FAIL_DEFECT, f"{spec.pathology}_WITHOUT_SAFE_SIGNAL"

    return FAIL_DEFECT, "UNCLASSIFIED_PATHOLOGY"


def evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    rows: list[dict] = []
    for spec in SPECS:
        source = repo / ROOT_DIR / spec.filename
        try:
            curated = curate_xlsx_document(source)
            p8_status, governed, p8_error = _p8_for_spec(source, spec)
            terminal, reason = _classify(spec, curated, p8_status, governed, p8_error)
            rows.append({
                "case_id": spec.case_id,
                "fixture": spec.filename,
                "pathology": spec.pathology,
                "curation_status": curated.report.status,
                "unknown_fields": list(curated.report.unknown_fields),
                "ambiguous_fields": list(curated.report.ambiguous_fields),
                "p8_status": p8_status,
                "governed_input_present": governed,
                "execution_attempted": False,
                "terminal_class": terminal,
                "reason": reason,
                "error": None,
            })
        except Exception as exc:
            rows.append({
                "case_id": spec.case_id, "fixture": spec.filename, "pathology": spec.pathology,
                "curation_status": "CRASH", "unknown_fields": [], "ambiguous_fields": [],
                "p8_status": None, "governed_input_present": False, "execution_attempted": False,
                "terminal_class": FAIL_DEFECT, "reason": "UNCONTROLLED_EXCEPTION",
                "error": f"{type(exc).__name__}: {exc}",
            })

    defects = [row for row in rows if row["terminal_class"] == FAIL_DEFECT]
    counts = {key: sum(row["terminal_class"] == key for row in rows) for key in (
        PASS_COMPUTABLE, PASS_NEEDS_OWNER, PASS_NEEDS_EVIDENCE, PASS_BLOCKED_FAIL_CLOSED, FAIL_DEFECT
    )}
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_PASS if not defects else VERDICT_FAIL,
        "cases": len(rows),
        "terminal_counts": counts,
        "unsafe_executions": sum(bool(row["execution_attempted"] and not row["governed_input_present"]) for row in rows),
        "uncontrolled_crashes": sum(row["curation_status"] == "CRASH" for row in rows),
        "defects": defects,
        "rows": rows,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
        "second_xlsx_parser_created": False,
    }


def main() -> int:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())

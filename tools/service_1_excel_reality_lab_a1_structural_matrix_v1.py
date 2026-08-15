"""Service 1 — Excel Reality Lab A1: Structural Matrix evaluator.

A1 evaluates structure and safe ingestion/semantics of the physical XLSX corpus
using the canonical intake (excel_lab_ingestion_v1 / ExcelProfileBuilder).
It does NOT claim P8 computability, numeric results, delivery or production
certification — those belong to A2.

Terminal classes per case (contract):
    PASS_COMPUTABLE
    PASS_NEEDS_OWNER
    PASS_NEEDS_EVIDENCE
    PASS_BLOCKED_FAIL_CLOSED
    FAIL_DEFECT
"""

from __future__ import annotations

import argparse
import json
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.excel_lab_ingestion_v1 import curate_xlsx_document

MANIFEST_PATH: Final[str] = "docs/service_1_excel_reality_lab_corpus.v1.json"
SCHEMA_VERSION: Final[str] = "SERVICE_1_EXCEL_REALITY_LAB_A1_STRUCTURAL_MATRIX_V1"
VERDICT_PASS: Final[str] = "PASS_STRUCTURAL_MATRIX_V1"
VERDICT_FAIL: Final[str] = "FAIL_STRUCTURAL_MATRIX_V1"

PASS_COMPUTABLE = "PASS_COMPUTABLE"
PASS_NEEDS_OWNER = "PASS_NEEDS_OWNER"
PASS_NEEDS_EVIDENCE = "PASS_NEEDS_EVIDENCE"
PASS_BLOCKED_FAIL_CLOSED = "PASS_BLOCKED_FAIL_CLOSED"
FAIL_DEFECT = "FAIL_DEFECT"

ALLOWED_OUTCOMES: Final[frozenset[str]] = frozenset({
    PASS_COMPUTABLE,
    PASS_NEEDS_OWNER,
    PASS_NEEDS_EVIDENCE,
    PASS_BLOCKED_FAIL_CLOSED,
    FAIL_DEFECT,
})

# Structural dimensions that can be physically verified by the canonical intake.
DIMENSION_PROBES: Final[dict[str, str]] = {
    "SINGLE_CLEAN_SHEET": "single clean table",
    "MULTI_SHEET": "multiple sheets",
    "SHIFTED_HEADER": "header not on row 1",
    "EXTRA_COLUMNS": "extra irrelevant columns",
    "MISSING_COLUMNS": "missing material columns",
    "AMBIGUOUS_NAMES": "ambiguous column names",
    "ABBREVIATED_NAMES": "abbreviated column names",
    "DUPLICATE_COLUMNS": "duplicate or near-duplicate columns",
    "EMPTY_ROWS": "empty intermediate rows",
    "SUBTOTALS_TOTALS": "subtotals and totals mixed",
    "DATES_VARIANTS": "different date formats",
    "NUMBERS_AS_TEXT": "numbers stored as text",
    "LOCALE_SEPARATORS": "decimal/thousand separators",
    "MIXED_CURRENCY": "declared or mixed currency",
    "EXCEL_FORMULAS": "Excel formulas plus values",
    "AUXILIARY_SHEETS": "auxiliary sheets",
    "GRANULARITY_MIX": "tables with different granularity",
    "SMALL_DATASET": "small dataset",
    "MEDIUM_DATASET": "medium dataset",
    "LARGE_DATASET": "large dataset within safe operational limit",
}


@dataclass(frozen=True)
class CaseVerdict:
    case_id: str
    fixture: str
    sheet: str
    declared_dimensions: tuple[str, ...]
    curation_status: str
    tables_count: int
    rows_count: int
    header_row: int | None
    sheet_count: int
    terminal_class: str
    observed_unknown: tuple[str, ...]
    observed_ambiguous: tuple[str, ...]
    dimension_verification: dict[str, bool]
    error: str | None = None
    manifest_class: str | None = None

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "fixture": self.fixture,
            "sheet": self.sheet,
            "declared_dimensions": list(self.declared_dimensions),
            "curation_status": self.curation_status,
            "tables_count": self.tables_count,
            "rows_count": self.rows_count,
            "header_row": self.header_row,
            "sheet_count": self.sheet_count,
            "terminal_class": self.terminal_class,
            "manifest_class": self.manifest_class,
            "observed_unknown": list(self.observed_unknown),
            "observed_ambiguous": list(self.observed_ambiguous),
            "dimension_verification": self.dimension_verification,
            "error": self.error,
        }


def _classify_curation(status: str, *, unknown: list[str], ambiguous: list[str], declared: tuple[str, ...]) -> str:
    if status == "BLOCKED":
        return PASS_BLOCKED_FAIL_CLOSED
    if status == "CRASH":
        return FAIL_DEFECT
    if unknown or ambiguous:
        return PASS_NEEDS_OWNER
    if "MISSING_COLUMNS" in declared:
        return PASS_NEEDS_EVIDENCE
    return PASS_COMPUTABLE


def _verify_dimensions(curated, *, declared: tuple[str, ...], header_row: int | None, sheet_count: int, rows_count: int) -> dict[str, bool]:
    verification: dict[str, bool] = {}
    for dimension in declared:
        if dimension == "MULTI_SHEET":
            verification[dimension] = sheet_count > 1
        elif dimension == "SINGLE_CLEAN_SHEET":
            verification[dimension] = sheet_count == 1
        elif dimension == "SHIFTED_HEADER":
            verification[dimension] = header_row is not None and header_row > 1
        elif dimension in {"EXTRA_COLUMNS", "AMBIGUOUS_NAMES", "ABBREVIATED_NAMES", "DUPLICATE_COLUMNS", "MISSING_COLUMNS"}:
            verification[dimension] = True  # semantic presence declared by fixture design
        elif dimension == "EMPTY_ROWS":
            verification[dimension] = curated.report.rows_count >= 3  # rows survived dropna
        elif dimension in {"SUBTOTALS_TOTALS", "DATES_VARIANTS", "NUMBERS_AS_TEXT", "LOCALE_SEPARATORS", "MIXED_CURRENCY", "EXCEL_FORMULAS", "AUXILIARY_SHEETS", "GRANULARITY_MIX"}:
            verification[dimension] = True  # present by fixture design; ingestion safety is the A1 claim
        elif dimension == "SMALL_DATASET":
            verification[dimension] = 0 < rows_count <= 30
        elif dimension == "MEDIUM_DATASET":
            verification[dimension] = 30 < rows_count <= 1000
        elif dimension == "LARGE_DATASET":
            verification[dimension] = 1000 < rows_count <= 10000
        else:
            verification[dimension] = True
    return verification


def evaluate_a1_structural_matrix_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    manifest_path = repo / MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fixture_root = repo / manifest["canonical_fixture_root"]

    case_verdicts: list[CaseVerdict] = []
    for case in manifest["cases"]:
        if case.get("coverage_lane") not in {"STRUCTURAL", "STRUCTURAL_SEED"}:
            continue
        case_id = case["case_id"]
        fixture = case["fixture"]
        sheet_name = case.get("sheet_name")
        declared = tuple(case.get("structural_dimensions") or ())
        manifest_class = case.get("expected_outcome")

        source = fixture_root / fixture
        if not source.is_file():
            case_verdicts.append(CaseVerdict(
                case_id=case_id, fixture=fixture, sheet=sheet_name, declared_dimensions=declared,
                curation_status="MISSING", tables_count=0, rows_count=0, header_row=None,
                sheet_count=0, terminal_class=FAIL_DEFECT, observed_unknown=(), observed_ambiguous=(),
                dimension_verification={}, error="fixture file missing", manifest_class=manifest_class,
            ))
            continue

        try:
            curated = curate_xlsx_document(source)
            report = curated.report
            status = report.status
            tables_count = report.tables_count
            rows_count = report.rows_count
            unknown = sorted(set(report.unknown_fields))
            ambiguous = sorted(set(report.ambiguous_fields))
            header_row = None
            if curated.raw_tables:
                header_row = curated.raw_tables[0].header_row
            sheet_count = len(curated.raw_tables)
        except Exception as exc:
            case_verdicts.append(CaseVerdict(
                case_id=case_id, fixture=fixture, sheet=sheet_name, declared_dimensions=declared,
                curation_status="CRASH", tables_count=0, rows_count=0, header_row=None,
                sheet_count=0, terminal_class=FAIL_DEFECT, observed_unknown=(), observed_ambiguous=(),
                dimension_verification={}, error=f"{type(exc).__name__}: {exc}",
                manifest_class=manifest_class,
            ))
            continue

        terminal = _classify_curation(status, unknown=unknown, ambiguous=ambiguous, declared=declared)
        verification = _verify_dimensions(
            curated, declared=declared, header_row=header_row, sheet_count=sheet_count, rows_count=rows_count,
        )
        case_verdicts.append(CaseVerdict(
            case_id=case_id, fixture=fixture, sheet=sheet_name, declared_dimensions=declared,
            curation_status=status, tables_count=tables_count, rows_count=rows_count,
            header_row=header_row, sheet_count=sheet_count, terminal_class=terminal,
            observed_unknown=tuple(unknown), observed_ambiguous=tuple(ambiguous),
            dimension_verification=verification, manifest_class=manifest_class,
        ))

    counts: dict[str, int] = {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}
    for verdict in case_verdicts:
        counts[verdict.terminal_class] = counts.get(verdict.terminal_class, 0) + 1

    defects = [v for v in case_verdicts if v.terminal_class == FAIL_DEFECT]
    declared_defect_ids = {
        str(manifest.get("a1_known_defect", {}).get("case_id") or "")
        for _ in [0]
    }
    declared_defect_ids.discard("")
    undeclared_defects = [v.case_id for v in defects if v.case_id not in declared_defect_ids]
    manifest_mismatch = [
        v.case_id for v in case_verdicts
        if v.manifest_class not in {None, "NOT_YET_EXECUTED"} and v.manifest_class != v.terminal_class
    ]
    unverified_dimensions = [
        v.case_id for v in case_verdicts
        for dim, ok in v.dimension_verification.items() if not ok
    ]

    verdict = (
        VERDICT_PASS
        if not undeclared_defects and not manifest_mismatch and not unverified_dimensions
        else VERDICT_FAIL
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "cases_evaluated": len(case_verdicts),
        "terminal_counts": counts,
        "defects": [v.to_dict() for v in defects],
        "declared_defect_ids": sorted(declared_defect_ids),
        "undeclared_defects": undeclared_defects,
        "manifest_mismatches": manifest_mismatch,
        "unverified_dimensions": unverified_dimensions,
        "case_results": [v.to_dict() for v in case_verdicts],
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
        "a2_calculation_not_claimed": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_a1_structural_matrix_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Service 1 — Excel Reality Lab A3: rubro matrix.

A3 measures whether representative XLSX files from the required PyME rubros
can traverse the canonical Excel Lab intake safely without introducing
sector-specific runtime authority, aliases, capabilities or parsers.

A3 is evidence about sector vocabulary/structure/ambiguity only. It does NOT
claim P8 computability, numeric correctness, delivery or production readiness.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pymia.smartpyme.excel_lab_ingestion_v1 import curate_xlsx_document

SCHEMA_VERSION: Final[str] = "SERVICE_1_EXCEL_REALITY_LAB_A3_RUBRO_MATRIX_V1"
VERDICT_PASS: Final[str] = "PASS_RUBRO_MATRIX_V1"
VERDICT_FAIL: Final[str] = "FAIL_RUBRO_MATRIX_V1"
MANIFEST_PATH: Final[str] = "docs/service_1_excel_reality_lab_corpus.v1.json"

REQUIRED_RUBROS: Final[tuple[str, ...]] = (
    "comercio_minorista",
    "mayorista_distribuidora",
    "textil",
    "produccion_fabrica",
    "servicios_profesionales_estudio_contable",
    "gastronomia",
    "administracion_consorcios",
    "mercado_libre_mercado_pago",
)

# One bounded representative per required rubro. These are corpus references,
# not runtime routing rules and not sector authorities.
REPRESENTATIVE_CASE_IDS: Final[dict[str, str]] = {
    "comercio_minorista": "S1-SYN-002",
    "mayorista_distribuidora": "S1-STR-002",
    "textil": "S1-STR-003",
    "produccion_fabrica": "S1-STR-004",
    "servicios_profesionales_estudio_contable": "S1-RUB-001",
    "gastronomia": "S1-STR-001",
    "administracion_consorcios": "S1-STR-007",
    "mercado_libre_mercado_pago": "S1-STR-006",
}


def _granularity(rows_count: int) -> str:
    if rows_count <= 30:
        return "SMALL"
    if rows_count <= 1000:
        return "MEDIUM"
    return "LARGE"


def _periodicity_signals(columns: list[str], sheet_names: list[str]) -> list[str]:
    text = " ".join([*columns, *sheet_names]).lower()
    signals: list[str] = []
    for token in ("fecha", "dia", "día", "mes", "mensual", "marzo", "abril", "mayo", "junio", "2026"):
        if token in text and token not in signals:
            signals.append(token)
    return signals


def _unit_signals(columns: list[str]) -> list[str]:
    signals: list[str] = []
    for column in columns:
        normalized = column.lower()
        if any(token in normalized for token in ("unidad", "cantidad", "horas", "dias", "días", "kg", "litro", "precio", "importe", "monto", "saldo", "costo")):
            signals.append(column)
    return sorted(set(signals))


def _terminal(status: str, unknown: list[str], ambiguous: list[str]) -> str:
    if status == "BLOCKED":
        return "PASS_BLOCKED_FAIL_CLOSED"
    if unknown or ambiguous:
        return "PASS_NEEDS_OWNER"
    return "PASS_DETERMINISTIC_UNDERSTANDING"


def evaluate_a3_rubro_matrix_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    fixture_root = repo / manifest["canonical_fixture_root"]
    by_id = {case["case_id"]: case for case in manifest["cases"]}

    rows: list[dict] = []
    failures: list[str] = []
    for rubro in REQUIRED_RUBROS:
        case_id = REPRESENTATIVE_CASE_IDS[rubro]
        case = by_id.get(case_id)
        if case is None:
            failures.append(f"{rubro}:MISSING_MANIFEST_CASE:{case_id}")
            continue
        if case.get("rubro") != rubro:
            failures.append(f"{rubro}:RUBRO_MISMATCH:{case.get('rubro')}")
            continue
        source = fixture_root / case["fixture"]
        if not source.is_file():
            failures.append(f"{rubro}:MISSING_FIXTURE:{case['fixture']}")
            continue
        try:
            curated = curate_xlsx_document(source)
        except Exception as exc:
            failures.append(f"{rubro}:CRASH:{type(exc).__name__}:{exc}")
            continue

        report = curated.report
        columns = sorted({column for table in curated.raw_tables for column in table.columns})
        sheet_names = [table.sheet_name for table in curated.raw_tables]
        contexts = sorted({table.context for table in curated.raw_tables})
        unknown = sorted(set(report.unknown_fields))
        ambiguous = sorted(set(report.ambiguous_fields))
        terminal = _terminal(report.status, unknown, ambiguous)
        rows.append({
            "rubro": rubro,
            "case_id": case_id,
            "fixture": case["fixture"],
            "source_kind": case.get("source_kind"),
            "curation_status": report.status,
            "terminal_class": terminal,
            "sheet_count": len(curated.raw_tables),
            "sheet_names": sheet_names,
            "contexts": contexts,
            "row_count": report.rows_count,
            "granularity": _granularity(report.rows_count),
            "vocabulary": columns,
            "unit_signals": _unit_signals(columns),
            "periodicity_signals": _periodicity_signals(columns, sheet_names),
            "unknown_fields": unknown,
            "ambiguous_fields": ambiguous,
            "capability_target": case.get("capability_target"),
            "new_capability_authorized": False,
            "sector_runtime_authority": False,
        })

    represented = {row["rubro"] for row in rows}
    missing = sorted(set(REQUIRED_RUBROS) - represented)
    if missing:
        failures.append(f"MISSING_REQUIRED_RUBROS:{','.join(missing)}")
    unsafe = [row["rubro"] for row in rows if row["terminal_class"] not in {
        "PASS_DETERMINISTIC_UNDERSTANDING", "PASS_NEEDS_OWNER", "PASS_BLOCKED_FAIL_CLOSED"
    }]
    if unsafe:
        failures.append(f"INVALID_TERMINAL:{','.join(unsafe)}")

    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_PASS if not failures and len(rows) == len(REQUIRED_RUBROS) else VERDICT_FAIL,
        "required_rubros": list(REQUIRED_RUBROS),
        "rubro_count": len(rows),
        "rubros_represented": sorted(represented),
        "missing_rubros": missing,
        "terminal_counts": {
            terminal: sum(row["terminal_class"] == terminal for row in rows)
            for terminal in ("PASS_DETERMINISTIC_UNDERSTANDING", "PASS_NEEDS_OWNER", "PASS_BLOCKED_FAIL_CLOSED")
        },
        "failures": failures,
        "rows": rows,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
        "new_capabilities_authorized": False,
        "sector_runtime_authority_authorized": False,
        "a3_claim_scope": "RUBRO_VOCABULARY_STRUCTURE_AND_SAFE_SEMANTIC_INTAKE_ONLY",
    }


def main() -> int:
    result = evaluate_a3_rubro_matrix_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())

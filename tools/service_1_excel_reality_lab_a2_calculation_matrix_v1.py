from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from tools.service_1_physical_computable_positive_controls_v1 import evaluate_physical_computable_positive_controls_v1
from tools.service_1_bounded_six_physical_computable_controls_v1 import evaluate_service_1_bounded_six_physical_computable_controls_v1
from tools.service_1_capability_physical_coverage_gate_v1 import (
    PHYSICAL_E2E_PASS,
    evaluate_service_1_capability_physical_coverage_gate_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_EXCEL_REALITY_LAB_A2_CALCULATION_MATRIX_V1"
VERDICT_PASS: Final[str] = "PASS_CALCULATION_MATRIX_V1"
VERDICT_FAIL: Final[str] = "FAIL_CALCULATION_MATRIX_V1"
MANIFEST_PATH: Final[str] = "docs/service_1_excel_reality_lab_corpus.v1.json"

TARGETS: Final[tuple[str, ...]] = (
    "sold_vs_collected_gap",
    "net_margin_real",
    "projected_closing_cash_balance",
    "dso",
    "current_ratio",
)


def evaluate_a2_calculation_matrix_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    structural_corpus_cases = sum(
        case.get("coverage_lane") == "STRUCTURAL" for case in manifest["cases"]
    )

    positive = evaluate_physical_computable_positive_controls_v1(root)
    bounded = evaluate_service_1_bounded_six_physical_computable_controls_v1(root)
    coverage = evaluate_service_1_capability_physical_coverage_gate_v1(root)

    rows: list[dict] = []
    failures: list[str] = []

    positive_by_capability = {row["capability"]: row for row in positive["rows"]}
    for capability in ("sold_vs_collected_gap", "projected_closing_cash_balance", "dso"):
        row = positive_by_capability.get(capability) or {}
        ok = bool(row.get("p6_ok") and row.get("p7_ok") and row.get("p8_ok") and row.get("execution_ok"))
        rows.append({
            "capability": capability,
            "source": "SERVICE_1_PHYSICAL_COMPUTABLE_POSITIVE_CONTROLS_V1",
            "p6": "APPROVED" if row.get("p6_ok") else None,
            "p7": "REQUIREMENT_MATCHED" if row.get("p7_ok") else None,
            "p8": row.get("p8_status"),
            "governed_input": row.get("governed_input_present"),
            "execution": row.get("execution_status"),
            "classification": row.get("classification"),
            "computed": row.get("computed"),
            "numeric_or_bounded_result_verified": bool(row.get("execution_ok")),
            "ok": ok,
        })
        if not ok:
            failures.append(f"{capability}:CONTROL_FAILED")

    current = next((row for row in bounded["positive_rows"] if row["capability"] == "current_ratio"), {})
    current_ok = bool(current.get("ok"))
    rows.append({
        "capability": "current_ratio",
        "source": "SERVICE_1_BOUNDED_SIX_PHYSICAL_COMPUTABLE_CONTROLS_V1",
        "p6": "APPROVED" if current_ok else None,
        "p7": "REQUIREMENT_MATCHED" if current_ok else None,
        "p8": current.get("p8_status"),
        "governed_input": current.get("governed_input_present"),
        "execution": current.get("execution_status"),
        "classification": current.get("classification"),
        "computed": {current.get("result_key"): current.get("result_value")} if current else {},
        "numeric_or_bounded_result_verified": current_ok,
        "ok": current_ok,
    })
    if not current_ok:
        failures.append("current_ratio:CONTROL_FAILED")

    capability_rows = {row["capability"]: row for row in coverage["productive_capabilities"]}
    ren = capability_rows.get("net_margin_real") or {}
    ren_ok = (
        ren.get("coverage_status") == PHYSICAL_E2E_PASS
        and ren.get("p6") == "APPROVED"
        and ren.get("p7") == "REQUIREMENT_MATCHED"
        and ren.get("p8") == "COMPUTABLE"
        and ren.get("governed_input") is True
        and ren.get("p9") == "EVALUATED"
        and isinstance(ren.get("result"), dict)
    )
    rows.append({
        "capability": "net_margin_real",
        "source": "SERVICE_1_CAPABILITY_PHYSICAL_COVERAGE_GATE_V1",
        "p6": ren.get("p6"),
        "p7": ren.get("p7"),
        "p8": ren.get("p8"),
        "governed_input": ren.get("governed_input"),
        "execution": ren.get("p9"),
        "classification": ren.get("classification"),
        "computed": ren.get("result"),
        "numeric_or_bounded_result_verified": ren_ok,
        "ok": ren_ok,
    })
    if not ren_ok:
        failures.append("net_margin_real:CONTROL_FAILED")

    by_capability = {row["capability"]: row for row in rows}
    passed = not failures and set(by_capability) == set(TARGETS) and all(row["ok"] for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_PASS if passed else VERDICT_FAIL,
        "targets": list(TARGETS),
        "targets_count": len(TARGETS),
        "targets_passed": sum(bool(row["ok"]) for row in rows),
        "failures": failures,
        "rows": rows,
        "structural_corpus_cases": structural_corpus_cases,
        "structural_cases_not_forced_into_calculation": True,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }


def main() -> int:
    result = evaluate_a2_calculation_matrix_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())

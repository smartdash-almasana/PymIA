from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import build_service_1_web_column_confirmation_intake_boundary_v1
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import build_service_1_canonical_ingestion_output_from_owner_confirmation_v1
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import run_initial_pass, run_owner_reentry, build_computability_decision_from_confirmed_bindings_v1
from pymia.smartpyme.service_1_product_pipeline_v1 import run_service_1_product_pipeline_v1
from pymia.smartpyme.service_1_legacy_semantic_reentry_compat_v1 import run_service_1_product_pipeline_with_legacy_owner_answers_v1

SCHEMA_VERSION: Final[str] = "SERVICE_1_BOUNDED_SIX_PHYSICAL_COMPUTABLE_CONTROLS_V1"
VERDICT_PASS: Final[str] = "PASS_BOUNDED_SIX_PHYSICAL_COMPUTABLE_CONTROLS_V1"
VERDICT_FAIL: Final[str] = "FAIL_BOUNDED_SIX_PHYSICAL_COMPUTABLE_CONTROLS_V1"
FIXTURE: Final[str] = "SERVICE_1_BOUNDED_SIX_PHYSICAL_CONTROLS.xlsx"

@dataclass(frozen=True)
class PositiveSpec:
    sheet: str
    capability: str
    classification: str
    result_key: str
    expected_value: float

POSITIVES: Final[tuple[PositiveSpec, ...]] = (
    PositiveSpec("POS_REORDER", "reorder_point", "REORDER_POINT_CALCULATED", "reorder_point_units", 70.0),
    PositiveSpec("POS_INV_TURN", "inventory_turnover", "POSITIVE_RECORDED_TURNOVER", "inventory_turnover_ratio", 4.0),
    PositiveSpec("POS_CURRENT_RATIO", "current_ratio", "POSITIVE_CURRENT_RATIO", "current_ratio_value", 1.5),
    PositiveSpec("POS_CONCENTRATION", "sales_concentration", "CONCENTRATION_WITHIN_RECORDED_TOTAL", "sales_concentration_percentage", 40.0),
    PositiveSpec("POS_INTEREST", "interest_burden_ratio", "POSITIVE_INTEREST_BURDEN", "interest_burden_ratio_value", 0.2),
    PositiveSpec("POS_INDEX", "index_update_ratio", "INDEX_ABOVE_ORIGIN", "index_update_ratio", 1.5),
)
NEGATIVES: Final[tuple[tuple[str, str], ...]] = (
    ("NEG_REORDER", "reorder_point"),
    ("NEG_INV_TURN", "inventory_turnover"),
    ("NEG_CURRENT_RATIO", "current_ratio"),
    ("NEG_CONCENTRATION", "sales_concentration"),
    ("NEG_INTEREST", "interest_burden_ratio"),
    ("NEG_INDEX", "index_update_ratio"),
)

def _answers(boundary: dict) -> dict[str, str]:
    return {str(q["field_id"]): f"La columna {q['column_name']} representa {q['column_name']}" for q in boundary["owner_questions"]}

def _canonical_answers(questions: list[dict]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for question in questions:
        option = next(
            (
                item
                for item in question.get("options", [])
                if item.get("option_id") not in {"OTHER", "IGNORE"}
            ),
            None,
        )
        if option is not None:
            answers[str(question["question_id"])] = str(option["option_id"])
    return answers


def _semantic_state(repo: Path, sheet: str) -> tuple[dict, dict]:
    source = repo / "prueba_excels" / FIXTURE
    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(local_xlsx_path=source, sheet_name=sheet)
    if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
        raise AssertionError(f"{sheet}:INTAKE:{boundary.get('blocked_reason')}")
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(owner_question_packet=boundary, owner_answers=_answers(boundary))
    if connector.get("status") != "INGESTION_OUTPUT_READY":
        raise AssertionError(f"{sheet}:CONNECTOR:{connector.get('blocked_reason')}")
    ingestion = connector["ingestion_output"]
    semantic = run_initial_pass(ingestion_output=ingestion, sheet_name=sheet)
    if semantic.get("status") == "OWNER_QUESTIONS":
        answers = {
            str(question["column_name"]): next(
                item["option_id"]
                for item in question["options"]
                if item["option_id"] not in {"OTHER", "IGNORE"}
            )
            for question in semantic["owner_questions"]
        }
        semantic = run_owner_reentry(previous_run=semantic, owner_answers=answers)
    return ingestion, semantic

def evaluate_service_1_bounded_six_physical_computable_controls_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    positive_rows: list[dict] = []
    negative_rows: list[dict] = []
    failures: list[str] = []

    for spec in POSITIVES:
        ingestion, semantic = _semantic_state(repo, spec.sheet)
        if semantic.get("status") != "CONFIRMED_BINDINGS":
            failures.append(f"{spec.sheet}:P6:{semantic.get('status')}")
            continue
        decision = build_computability_decision_from_confirmed_bindings_v1(confirmed_bindings=semantic, requested_capability=spec.capability)
        product = run_service_1_product_pipeline_v1(
            ingestion_output=ingestion,
            tool_requests=(),
            output_dir=repo / ".tmp" / "bounded_six_physical" / spec.sheet,
            sheet_name=spec.sheet,
            requested_capability=spec.capability,
            deliver_result=False,
        )
        if product.get("status") == "NEEDS_OWNER_CONFIRMATION":
            product = run_service_1_product_pipeline_with_legacy_owner_answers_v1(
                ingestion_output=ingestion,
                tool_requests=(),
                output_dir=repo / ".tmp" / "bounded_six_physical" / spec.sheet,
                sheet_name=spec.sheet,
                requested_capability=spec.capability,
                owner_answers=_canonical_answers(
                    list(product.get("owner_questions") or [])
                ),
                deliver_result=False,
            ) if decision.status == "COMPUTABLE" else {}
        computation = product.get("computation_result") or {}
        observed = (computation.get("computed") or {}).get(spec.result_key)
        ok = (
            decision.status == "COMPUTABLE"
            and decision.governed_computation_input is not None
            and product.get("status") == "COMPUTATION_PLAN_READY"
            and computation.get("status") == "EVALUATED"
            and computation.get("classification") == spec.classification
            and float(observed) == spec.expected_value
        )
        positive_rows.append({
            "sheet": spec.sheet,
            "capability": spec.capability,
            "p8_status": decision.status,
            "governed_input_present": decision.governed_computation_input is not None,
            "execution_status": computation.get("status"),
            "classification": computation.get("classification"),
            "result_key": spec.result_key,
            "result_value": observed,
            "ok": ok,
        })
        if not ok:
            failures.append(f"{spec.sheet}:POSITIVE_FAILED")

    for sheet, capability in NEGATIVES:
        _, semantic = _semantic_state(repo, sheet)
        if semantic.get("status") != "CONFIRMED_BINDINGS":
            failures.append(f"{sheet}:P6:{semantic.get('status')}")
            continue
        decision = build_computability_decision_from_confirmed_bindings_v1(confirmed_bindings=semantic, requested_capability=capability)
        ok = decision.status == "NEEDS_EVIDENCE" and decision.governed_computation_input is None
        negative_rows.append({
            "sheet": sheet,
            "capability": capability,
            "p8_status": decision.status,
            "reason": decision.reason,
            "governed_input_present": decision.governed_computation_input is not None,
            "execution_attempted": False,
            "ok": ok,
        })
        if not ok:
            failures.append(f"{sheet}:NEGATIVE_FAILED")

    passed = not failures and len(positive_rows) == 6 and len(negative_rows) == 6
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_PASS if passed else VERDICT_FAIL,
        "fixture": FIXTURE,
        "positive_controls": len(positive_rows),
        "positive_passed": sum(bool(row["ok"]) for row in positive_rows),
        "negative_controls": len(negative_rows),
        "negative_passed": sum(bool(row["ok"]) for row in negative_rows),
        "unsafe_executions": 0,
        "failures": failures,
        "positive_rows": positive_rows,
        "negative_rows": negative_rows,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }

def main() -> int:
    result = evaluate_service_1_bounded_six_physical_computable_controls_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_PASS else 2

if __name__ == "__main__":
    raise SystemExit(main())

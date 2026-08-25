from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_computability_v1 import (
    build_computability_decision_from_confirmed_bindings_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_CONFIRMED as ASSISTED_SEMANTIC_CONFIRMED,
    STATUS_OWNER_DIALOGUE_FOLLOWUP as ASSISTED_SEMANTIC_FOLLOWUP,
    STATUS_OWNER_DIALOGUE_REQUIRED as ASSISTED_SEMANTIC_OWNER_REQUIRED,
    run_service_1_assisted_semantic_initial_v1,
    run_service_1_assisted_semantic_reentry_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import build_service_1_web_column_confirmation_intake_boundary_v1
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import build_service_1_canonical_ingestion_output_from_owner_confirmation_v1
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    Service1ProductExecutionDependenciesV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookSemanticStartRequestV1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_NEEDS_OWNER,
    run_service_1_product_pipeline_v1,
)

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


def _run_product_request(
    *,
    ingestion: dict,
    output_dir: Path,
    requested_capability: str | None,
    semantic_assistance_state: dict | None = None,
    semantic_dialogue_responses: tuple[dict, ...] = (),
) -> dict:
    dependencies = Service1ProductExecutionDependenciesV1(
        output_dir=output_dir,
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
        semantic_owner_actor_id="service-1-physical-controls-owner",
        semantic_owner_actor_role="OWNER",
    )
    if semantic_assistance_state is None:
        request = WorkbookSemanticStartRequestV1(
            ingestion_output=ingestion,
            requested_capability=requested_capability,
        )
    else:
        request = WorkbookSemanticContinueRequestV1(
            ingestion_output=ingestion,
            requested_capability=(requested_capability or ""),
            semantic_assistance_state=semantic_assistance_state,
            semantic_dialogue_responses=semantic_dialogue_responses,
        )
    return run_service_1_product_pipeline_v1(request, dependencies=dependencies)


def _accept_owner_questions(
    *,
    ingestion: dict,
    output_dir: Path,
    requested_capability: str | None,
    initial: dict,
) -> dict:
    current = initial
    for _ in range(20):
        if current.get("status") != STATUS_NEEDS_OWNER:
            return current
        state = current.get("semantic_assistance_state")
        questions = [
            item
            for item in current.get("owner_questions") or []
            if isinstance(item, dict) and str(item.get("decision_id") or "").strip()
        ]
        if not isinstance(state, dict) or not questions:
            return current
        responses = tuple(
            {"decision_id": str(item["decision_id"]), "action": "ACCEPT"}
            for item in questions
        )
        current = _run_product_request(
            ingestion=ingestion,
            output_dir=output_dir,
            requested_capability=requested_capability,
            semantic_assistance_state=state,
            semantic_dialogue_responses=responses,
        )
    return current


def _run_semantic_pass(
    *,
    ingestion: dict,
    requested_capability: str | None = None,
) -> dict:
    current = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability=requested_capability,
        provider=build_service_1_deterministic_semantic_proposal_v1,
    )
    for _ in range(20):
        if current.get("status") not in {
            ASSISTED_SEMANTIC_OWNER_REQUIRED,
            ASSISTED_SEMANTIC_FOLLOWUP,
        }:
            nested = current.get("semantic_run")
            return nested if current.get("status") == ASSISTED_SEMANTIC_CONFIRMED and isinstance(nested, dict) else current
        questions = [
            item
            for item in current.get("owner_questions") or []
            if isinstance(item, dict) and str(item.get("decision_id") or "").strip()
        ]
        if not questions:
            return current
        current = run_service_1_assisted_semantic_reentry_v1(
            previous_state=current,
            owner_responses=tuple(
                {"decision_id": str(item["decision_id"]), "action": "ACCEPT"}
                for item in questions
            ),
            owner_actor_id="service-1-physical-controls-owner",
            owner_actor_role="OWNER",
        )
    return current


def _semantic_state(repo: Path, sheet: str) -> tuple[dict, dict]:
    source = repo / "prueba_excels" / FIXTURE
    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(local_xlsx_path=source, sheet_name=sheet)
    if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
        raise AssertionError(f"{sheet}:INTAKE:{boundary.get('blocked_reason')}")
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(owner_question_packet=boundary, owner_answers=_answers(boundary))
    if connector.get("status") != "INGESTION_OUTPUT_READY":
        raise AssertionError(f"{sheet}:CONNECTOR:{connector.get('blocked_reason')}")
    ingestion = connector["ingestion_output"]
    semantic = _run_semantic_pass(ingestion=ingestion)
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
        product = _accept_owner_questions(
            ingestion=ingestion,
            output_dir=repo / ".tmp" / "bounded_six_physical" / spec.sheet,
            requested_capability=spec.capability,
            initial=_run_product_request(
                ingestion=ingestion,
                output_dir=repo / ".tmp" / "bounded_six_physical" / spec.sheet,
                requested_capability=spec.capability,
            ),
        )
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

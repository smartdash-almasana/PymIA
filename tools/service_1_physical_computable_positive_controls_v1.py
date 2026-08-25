from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_computability_v1 import (
    build_computability_decision_from_confirmed_bindings_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_CONFIRMED as ASSISTED_SEMANTIC_CONFIRMED,
    STATUS_OWNER_DIALOGUE_FOLLOWUP as ASSISTED_SEMANTIC_FOLLOWUP,
    STATUS_OWNER_DIALOGUE_REQUIRED as ASSISTED_SEMANTIC_OWNER_REQUIRED,
    run_service_1_assisted_semantic_initial_v1,
    run_service_1_assisted_semantic_reentry_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    Service1ProductExecutionDependenciesV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookSemanticStartRequestV1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_NEEDS_OWNER,
    run_service_1_product_pipeline_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PHYSICAL_COMPUTABLE_POSITIVE_CONTROLS_V1"
VERDICT_PASS: Final[str] = "PASS_PHYSICAL_COMPUTABLE_POSITIVE_CONTROLS_V1"
VERDICT_FAIL: Final[str] = "FAIL_PHYSICAL_COMPUTABLE_POSITIVE_CONTROLS_V1"


@dataclass(frozen=True)
class PositiveControlSpec:
    control_id: str
    filename: str
    sheet_name: str
    capability: str
    expected_family_id: str
    expected_classification: str
    expected_inputs: dict[str, float]
    expected_computed: dict[str, float]


CONTROLS: Final[tuple[PositiveControlSpec, ...]] = (
    PositiveControlSpec(
        control_id="S1-POS-001-LIQ001",
        filename="SERVICE_1_PHYSICAL_POSITIVE_LIQ_001_SOLD_VS_COLLECTED.xlsx",
        sheet_name="Ventas_Cobros",
        capability="sold_vs_collected_gap",
        expected_family_id="CASH_COLLECTIONS",
        expected_classification="SALES_PENDING_COLLECTION",
        expected_inputs={"sold_amount": 4600.0, "collected_amount": 4000.0},
        expected_computed={"gap_amount": 600.0},
    ),
    PositiveControlSpec(
        control_id="S1-POS-002-LIQ002",
        filename="SERVICE_1_PHYSICAL_POSITIVE_LIQ_002_PROJECTED_CASH.xlsx",
        sheet_name="Proyeccion_Caja",
        capability="projected_closing_cash_balance",
        expected_family_id="CASH_PROJECTION",
        expected_classification="POSITIVE_PROJECTED_BALANCE",
        expected_inputs={"initial_balance": 1000.0, "expected_collections": 2500.0, "expected_payments": 1800.0},
        expected_computed={"projected_closing_balance": 1700.0},
    ),
    PositiveControlSpec(
        control_id="S1-POS-003-DSO",
        filename="SERVICE_1_PHYSICAL_POSITIVE_DSO.xlsx",
        sheet_name="DSO",
        capability="dso",
        expected_family_id="RECEIVABLES_DSO",
        expected_classification="DSO_WITHIN_PERIOD",
        expected_inputs={"accounts_receivable": 3000.0, "sales": 9000.0, "days": 30.0},
        expected_computed={"dso_days": 10.0},
    ),
)


def _owner_answers(boundary: dict) -> dict[str, str]:
    return {
        str(q["field_id"]): f"La columna {q['column_name']} representa {q['column_name']}"
        for q in boundary["owner_questions"]
    }


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
    requested_capability: str | None,
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


def evaluate_physical_computable_positive_controls_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    rows: list[dict] = []
    failures: list[str] = []

    for control in CONTROLS:
        source = repo / "prueba_excels" / control.filename
        boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
            local_xlsx_path=source,
            sheet_name=control.sheet_name,
        )
        if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
            failures.append(f"{control.control_id}:INTAKE:{boundary.get('blocked_reason')}")
            continue
        connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
            owner_question_packet=boundary,
            owner_answers=_owner_answers(boundary),
        )
        if connector.get("status") != "INGESTION_OUTPUT_READY":
            failures.append(f"{control.control_id}:CONNECTOR:{connector.get('blocked_reason')}")
            continue
        ingestion = connector["ingestion_output"]
        semantic = _run_semantic_pass(
            ingestion=ingestion,
            requested_capability=control.capability,
        )
        if semantic.get("status") != "CONFIRMED_BINDINGS":
            failures.append(f"{control.control_id}:P6:{semantic.get('status')}")
            continue

        gate = semantic.get("reentry_packet") or semantic.get("gate_packet") or {}
        p6 = list(gate.get("p6_decisions") or [])
        candidate = gate.get("controlled_execution_candidate") or {}
        p7 = list(candidate.get("requirement_matches") or [])
        expected_family = next((m for m in p7 if m.get("family_id") == control.expected_family_id), None)
        p6_ok = bool(p6) and all(d.get("status") == "APPROVED" for d in p6)
        p7_ok = isinstance(expected_family, dict) and expected_family.get("status") == "REQUIREMENT_MATCHED"

        decision = build_computability_decision_from_confirmed_bindings_v1(
            confirmed_bindings=semantic,
            requested_capability=control.capability,
        )
        p8_ok = decision.status == "COMPUTABLE" and decision.governed_computation_input is not None

        product = _accept_owner_questions(
            ingestion=ingestion,
            output_dir=repo / ".tmp" / "service_1_positive_controls" / control.control_id,
            requested_capability=control.capability,
            initial=_run_product_request(
                ingestion=ingestion,
                output_dir=repo / ".tmp" / "service_1_positive_controls" / control.control_id,
                requested_capability=control.capability,
            ),
        )
        computation = product.get("computation_result") or {}
        inputs = computation.get("inputs") or {}
        computed = computation.get("computed") or {}
        execution_ok = (
            product.get("status") == "COMPUTATION_PLAN_READY"
            and computation.get("status") == "EVALUATED"
            and computation.get("classification") == control.expected_classification
            and all(float(inputs.get(k)) == v for k, v in control.expected_inputs.items())
            and all(float(computed.get(k)) == v for k, v in control.expected_computed.items())
        )
        row = {
            "control_id": control.control_id,
            "filename": control.filename,
            "sheet_name": control.sheet_name,
            "capability": control.capability,
            "p6_ok": p6_ok,
            "p7_ok": p7_ok,
            "p8_status": decision.status,
            "p8_ok": p8_ok,
            "governed_input_present": decision.governed_computation_input is not None,
            "product_status": product.get("status"),
            "execution_status": computation.get("status"),
            "classification": computation.get("classification"),
            "inputs": inputs,
            "computed": computed,
            "execution_ok": execution_ok,
        }
        rows.append(row)
        if not all((p6_ok, p7_ok, p8_ok, execution_ok)):
            failures.append(f"{control.control_id}:CONTROL_FAILED")

    passed = len(rows) == len(CONTROLS) and not failures
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_PASS if passed else VERDICT_FAIL,
        "controls_count": len(CONTROLS),
        "controls_passed": sum(
            all((r["p6_ok"], r["p7_ok"], r["p8_ok"], r["execution_ok"])) for r in rows
        ),
        "computable_positive_cases": sum(r["p8_ok"] for r in rows),
        "executed_positive_cases": sum(r["execution_ok"] for r in rows),
        "failures": failures,
        "rows": rows,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }


def main() -> int:
    result = evaluate_physical_computable_positive_controls_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    build_computability_decision_from_confirmed_bindings_v1,
    run_initial_pass,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
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
        semantic = run_initial_pass(ingestion_output=ingestion, sheet_name=control.sheet_name)
        if semantic.get("status") != "CONFIRMED_BINDINGS":
            failures.append(f"{control.control_id}:P6:{semantic.get('status')}")
            continue

        gate = semantic.get("gate_packet") or {}
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

        product = run_service_1_product_pipeline_v1(
            ingestion_output=ingestion,
            tool_requests=(),
            output_dir=repo / ".tmp" / "service_1_positive_controls" / control.control_id,
            sheet_name=control.sheet_name,
            requested_capability=control.capability,
            deliver_result=False,
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

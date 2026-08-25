from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED as P6_APPROVED,
    build_service_1_p6_approval_decisions_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    P7_STATUS_NOT_OBSERVED,
    build_service_1_requirement_matches_v1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE,
    STATUS_UNSUPPORTED_CAPABILITY,
    build_service_1_computability_decision_v1,
)
from tools.service_1_physical_xlsx_product_readiness_corpus_v1 import CASES
from tools.service_1_physical_computable_positive_controls_v1 import (
    VERDICT_PASS as POSITIVE_CONTROLS_PASS,
    evaluate_physical_computable_positive_controls_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PHYSICAL_P6_P7_P8_CAPABILITY_READINESS_MATRIX_V1"
VERDICT_READY: Final[str] = "READY"
VERDICT_NOT_READY_NO_POSITIVE: Final[str] = "NOT_READY_MISSING_POSITIVE_COMPUTABLE_CASE"
VERDICT_FAIL: Final[str] = "FAIL"


@dataclass(frozen=True)
class P8Probe:
    capability: str
    expected_status: str


@dataclass(frozen=True)
class MatrixCaseSpec:
    case_id: str
    expected_matched_families: tuple[str, ...]
    expected_missing_families: tuple[str, ...]
    p8_probes: tuple[P8Probe, ...]


# Ground truth is deliberately explicit. It is not derived from current runtime output.
MATRIX_CASES: Final[dict[str, MatrixCaseSpec]] = {
    "S1-PHY-001": MatrixCaseSpec(
        case_id="S1-PHY-001",
        expected_matched_families=("OPERATION_CORE", "SALES_MARGIN"),
        expected_missing_families=("CASH_COLLECTIONS",),
        p8_probes=(
            P8Probe("gross_margin", STATUS_UNSUPPORTED_CAPABILITY),
            P8Probe("sold_vs_collected_gap", STATUS_NEEDS_EVIDENCE),
            P8Probe("dso", STATUS_NEEDS_EVIDENCE),
        ),
    ),
    "S1-PHY-002": MatrixCaseSpec(
        case_id="S1-PHY-002",
        expected_matched_families=("OPERATION_CORE",),
        expected_missing_families=("SALES_MARGIN", "CASH_COLLECTIONS"),
        p8_probes=(
            P8Probe("sold_vs_collected_gap", STATUS_NEEDS_EVIDENCE),
            P8Probe("dso", STATUS_NEEDS_EVIDENCE),
        ),
    ),
    "S1-PHY-003": MatrixCaseSpec(
        case_id="S1-PHY-003",
        expected_matched_families=("PURCHASES_SUPPLIERS",),
        expected_missing_families=("OPERATION_CORE",),
        p8_probes=(
            P8Probe("dpo", STATUS_UNSUPPORTED_CAPABILITY),
        ),
    ),
    "S1-PHY-004": MatrixCaseSpec(
        case_id="S1-PHY-004",
        expected_matched_families=(),
        expected_missing_families=("INVENTORY_CONTROL",),
        p8_probes=(
            P8Probe("reorder_point", STATUS_NEEDS_EVIDENCE),
            P8Probe("inventory_turnover", STATUS_NEEDS_EVIDENCE),
        ),
    ),
    "S1-PHY-005": MatrixCaseSpec(
        case_id="S1-PHY-005",
        expected_matched_families=(),
        expected_missing_families=("CASH_COLLECTIONS",),
        p8_probes=(
            P8Probe("sold_vs_collected_gap", STATUS_NEEDS_EVIDENCE),
            P8Probe("dso", STATUS_NEEDS_EVIDENCE),
        ),
    ),
    "S1-PHY-006": MatrixCaseSpec(
        case_id="S1-PHY-006",
        expected_matched_families=("INVENTORY_CONTROL",),
        expected_missing_families=("SALES_MARGIN",),
        p8_probes=(
            P8Probe("reorder_point", STATUS_NEEDS_EVIDENCE),
            P8Probe("inventory_turnover", STATUS_NEEDS_EVIDENCE),
        ),
    ),
    "S1-PHY-007": MatrixCaseSpec(
        case_id="S1-PHY-007",
        expected_matched_families=(),
        expected_missing_families=(),
        p8_probes=(
            P8Probe("sold_vs_collected_gap", STATUS_NEEDS_EVIDENCE),
            P8Probe("projected_closing_cash_balance", STATUS_NEEDS_EVIDENCE),
        ),
    ),
}


def _owner_column_answers(boundary: dict) -> dict[str, str]:
    return {
        str(question["field_id"]): f"La columna {question['column_name']} representa {question['column_name']}"
        for question in boundary["owner_questions"]
    }


def _owner_events_for_known_roles(case, candidates) -> tuple[dict, ...]:
    events: list[dict] = []
    by_column = {candidate.source_column_name: candidate for candidate in candidates}
    for column, expected_role in case.expected_roles.items():
        if expected_role == "unknown":
            continue
        candidate = by_column[column]
        metadata = dict(candidate.metadata or {})
        question_ref = str(metadata.get("column_ref_id") or metadata.get("question_id") or column)
        events.append({
            "question_ref": question_ref,
            "sheet_ref": candidate.sheet_name,
            "column_ref": column,
            "confirmed_by_owner": True,
            "confirmation_scope": "SEMANTIC_ROLE",
            "confirmed_role": expected_role,
        })
    return tuple(events)


def _physical_semantic_state(repo: Path, case):
    source = repo / "prueba_excels" / case.filename
    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=source,
        sheet_name=case.sheet_name,
    )
    if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
        raise AssertionError(f"{case.case_id}: intake blocked: {boundary.get('blocked_reason')}")
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=boundary,
        owner_answers=_owner_column_answers(boundary),
    )
    if connector.get("status") != "INGESTION_OUTPUT_READY":
        raise AssertionError(f"{case.case_id}: connector blocked: {connector.get('blocked_reason')}")
    ingestion_output = dict(connector["ingestion_output"])
    ingestion_output["normalized_tables"] = boundary.get("normalized_tables")
    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=ingestion_output,
    )
    if bridge.get("status") != "SEMANTIC_CANDIDATES_READY":
        raise AssertionError(f"{case.case_id}: semantic bridge blocked: {bridge.get('blocked_reason')}")
    candidates = tuple(bridge["column_candidates"])
    known_columns = {column for column, role in case.expected_roles.items() if role != "unknown"}
    active_candidates = tuple(candidate for candidate in candidates if candidate.source_column_name in known_columns)
    events = _owner_events_for_known_roles(case, active_candidates)
    p6 = build_service_1_p6_approval_decisions_v1(
        case_id=str(bridge["case_id"]),
        candidates=active_candidates,
        owner_confirmation_events=events,
    )
    return ingestion_output, bridge, p6


def evaluate_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    case_rows: list[dict] = []
    p8_rows: list[dict] = []
    failures: list[str] = []
    computable_count = 0
    unsafe_execution_count = 0

    by_id = {case.case_id: case for case in CASES}
    for case_id, spec in MATRIX_CASES.items():
        case = by_id[case_id]
        _, bridge, p6 = _physical_semantic_state(repo, case)
        p6_all_approved = bool(p6) and all(decision.status == P6_APPROVED for decision in p6)
        if not p6_all_approved:
            failures.append(f"{case_id}:P6_NOT_ALL_APPROVED")
            case_rows.append({"case_id": case_id, "p6_all_approved": False})
            continue

        p7 = build_service_1_requirement_matches_v1(p6)
        p7_by_family = {match.family_id: match for match in p7}
        observed_matched = tuple(sorted(family for family, match in p7_by_family.items() if match.status == P7_STATUS_MATCHED))
        observed_missing = tuple(sorted(family for family, match in p7_by_family.items() if match.status == P7_STATUS_MISSING_REQUIREMENTS))
        expected_matched = tuple(sorted(spec.expected_matched_families))
        expected_missing = tuple(sorted(spec.expected_missing_families))
        matched_ok = all(p7_by_family.get(family) is not None and p7_by_family[family].status == P7_STATUS_MATCHED for family in expected_matched)
        missing_ok = all(p7_by_family.get(family) is not None and p7_by_family[family].status == P7_STATUS_MISSING_REQUIREMENTS for family in expected_missing)
        if not matched_ok:
            failures.append(f"{case_id}:P7_MATCHED_FAMILY_MISMATCH")
        if not missing_ok:
            failures.append(f"{case_id}:P7_MISSING_FAMILY_MISMATCH")

        p6_payload = [decision.to_dict() for decision in p6]
        p7_payload = [match.to_dict() for match in p7]
        for probe in spec.p8_probes:
            decision = build_service_1_computability_decision_v1(
                case_id=str(bridge["case_id"]),
                requested_capability=probe.capability,
                p6_decisions=p6_payload,
                requirement_matches=p7_payload,
            )
            status_ok = decision.status == probe.expected_status
            if not status_ok:
                failures.append(
                    f"{case_id}:P8:{probe.capability}:expected={probe.expected_status}:observed={decision.status}"
                )
            if decision.status == STATUS_COMPUTABLE:
                computable_count += 1
                # Execution is deliberately not attempted unless P8 produced governed input.
                if decision.governed_computation_input is None:
                    unsafe_execution_count += 1
                    failures.append(f"{case_id}:P8_COMPUTABLE_WITHOUT_GOVERNED_INPUT")
            p8_rows.append({
                "case_id": case_id,
                "capability": probe.capability,
                "expected_status": probe.expected_status,
                "observed_status": decision.status,
                "status_ok": status_ok,
                "reason": decision.reason,
                "family_id": decision.family_id,
                "governed_input_present": decision.governed_computation_input is not None,
                "execution_attempted": decision.status == STATUS_COMPUTABLE,
            })

        case_rows.append({
            "case_id": case_id,
            "sector": case.sector,
            "filename": case.filename,
            "sheet_name": case.sheet_name,
            "known_columns": sum(role != "unknown" for role in case.expected_roles.values()),
            "p6_all_approved": p6_all_approved,
            "p7_expected_matched": list(expected_matched),
            "p7_observed_matched": list(observed_matched),
            "p7_expected_missing": list(expected_missing),
            "p7_observed_missing": list(observed_missing),
            "p7_expectations_ok": matched_ok and missing_ok,
        })

    positive_controls = evaluate_physical_computable_positive_controls_v1(root=repo)
    positive_controls_ok = positive_controls.get("verdict") == POSITIVE_CONTROLS_PASS
    computable_count += int(positive_controls.get("computable_positive_cases") or 0)
    if not positive_controls_ok:
        failures.append("PHYSICAL_COMPUTABLE_POSITIVE_CONTROLS_FAILED")

    structural_ok = not failures and unsafe_execution_count == 0
    if not structural_ok:
        verdict = VERDICT_FAIL
    elif computable_count == 0:
        verdict = VERDICT_NOT_READY_NO_POSITIVE
    else:
        verdict = VERDICT_READY

    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "cases_count": len(MATRIX_CASES),
        "p8_probes_count": len(p8_rows),
        "p6_cases_passed": sum(bool(row.get("p6_all_approved")) for row in case_rows),
        "p7_cases_passed": sum(bool(row.get("p7_expectations_ok")) for row in case_rows),
        "p8_probes_passed": sum(bool(row["status_ok"]) for row in p8_rows),
        "computable_positive_cases": computable_count,
        "unsafe_executions": unsafe_execution_count,
        "failures": failures,
        "case_rows": case_rows,
        "p8_rows": p8_rows,
        "positive_controls": positive_controls,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.parse_args()
    result = evaluate_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] in {VERDICT_READY, VERDICT_NOT_READY_NO_POSITIVE} else 2


if __name__ == "__main__":
    raise SystemExit(main())

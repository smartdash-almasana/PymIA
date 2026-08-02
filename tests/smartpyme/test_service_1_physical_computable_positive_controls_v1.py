from __future__ import annotations

from openpyxl import Workbook

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as SEMANTIC_CANDIDATES_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE,
    build_service_1_computability_decision_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED,
    build_service_1_p6_approval_decisions_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_PERIOD_NET_MARGIN,
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    build_service_1_requirement_matches_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from tools.service_1_physical_computable_positive_controls_v1 import (
    VERDICT_PASS,
    evaluate_physical_computable_positive_controls_v1,
)


def test_physical_positive_controls_reach_computable_and_execute() -> None:
    result = evaluate_physical_computable_positive_controls_v1()

    assert result["verdict"] == VERDICT_PASS
    assert result["controls_count"] == 3
    assert result["controls_passed"] == 3
    assert result["computable_positive_cases"] == 3
    assert result["executed_positive_cases"] == 3
    assert result["failures"] == []

    rows = {row["capability"]: row for row in result["rows"]}
    assert set(rows) == {"sold_vs_collected_gap", "projected_closing_cash_balance", "dso"}
    assert all(row["p6_ok"] is True for row in rows.values())
    assert all(row["p7_ok"] is True for row in rows.values())
    assert all(row["p8_status"] == "COMPUTABLE" for row in rows.values())
    assert all(row["governed_input_present"] is True for row in rows.values())
    assert all(row["execution_status"] == "EVALUATED" for row in rows.values())
    assert all(row["execution_ok"] is True for row in rows.values())

    liq001 = rows["sold_vs_collected_gap"]
    assert liq001["classification"] == "SALES_PENDING_COLLECTION"
    assert liq001["inputs"] == {"sold_amount": 4600.0, "collected_amount": 4000.0}
    assert liq001["computed"]["gap_amount"] == 600.0

    liq002 = rows["projected_closing_cash_balance"]
    assert liq002["classification"] == "POSITIVE_PROJECTED_BALANCE"
    assert liq002["inputs"] == {
        "initial_balance": 1000.0,
        "expected_collections": 2500.0,
        "expected_payments": 1800.0,
    }
    assert liq002["computed"]["projected_closing_balance"] == 1700.0

    dso = rows["dso"]
    assert dso["classification"] == "DSO_WITHIN_PERIOD"
    assert dso["inputs"] == {"accounts_receivable": 3000.0, "sales": 9000.0, "days": 30.0}
    assert dso["computed"]["dso_days"] == 10.0


def _write_ren_001_xlsx(tmp_path, *, include_taxes: bool):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Resumen"
    headers = ["ventas_periodo", "cmv_total"]
    values = [100000, 60000]
    if include_taxes:
        headers.append("impuestos_periodo")
        values.append(10000)
    sheet.append(headers)
    sheet.append(values)
    path = tmp_path / (
        "ren_001_positive.xlsx" if include_taxes else "ren_001_missing_taxes.xlsx"
    )
    workbook.save(path)
    return path


def _build_ren_001_semantic_chain(*, xlsx_path, expected_roles: dict[str, str]):
    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx_path,
        sheet_name="Resumen",
    )
    assert boundary["status"] == "NEEDS_OWNER_CONFIRMATION"
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=boundary,
        owner_answers={
            question["field_id"]: f"La columna {question['column_name']} representa {question['column_name']}"
            for question in boundary["owner_questions"]
        },
    )
    assert connector["status"] == "INGESTION_OUTPUT_READY"
    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=connector["ingestion_output"],
        sheet_name="Resumen",
    )
    assert bridge["status"] == SEMANTIC_CANDIDATES_READY
    candidates = tuple(bridge["column_candidates"])
    owner_events = tuple(
        {
            "question_ref": candidate.metadata["column_ref_id"],
            "sheet_ref": candidate.sheet_name,
            "column_ref": candidate.source_column_name,
            "confirmed_by_owner": True,
            "confirmation_scope": "SEMANTIC_ROLE",
            "confirmed_role": expected_roles[candidate.source_column_name],
        }
        for candidate in candidates
        if candidate.owner_confirmation_required
    )
    p6 = build_service_1_p6_approval_decisions_v1(
        case_id=bridge["case_id"],
        candidates=candidates,
        owner_confirmation_events=owner_events,
    )
    assert all(decision.status == STATUS_APPROVED for decision in p6)
    return p6, build_service_1_requirement_matches_v1(p6)


def test_ren_001_physical_xlsx_reaches_p8_and_missing_taxes_needs_evidence(
    tmp_path,
) -> None:
    positive_p6, positive_p7 = _build_ren_001_semantic_chain(
        xlsx_path=_write_ren_001_xlsx(tmp_path, include_taxes=True),
        expected_roles={
            "ventas_periodo": "period_sales_total",
            "cmv_total": "period_costs_total",
            "impuestos_periodo": "period_taxes_total",
        },
    )
    positive_family = next(
        match for match in positive_p7 if match.family_id == FAMILY_PERIOD_NET_MARGIN
    )
    positive = build_service_1_computability_decision_v1(
        case_id="case_ren_001_positive",
        requested_capability="net_margin_real",
        p6_decisions=[decision.to_dict() for decision in positive_p6],
        requirement_matches=[match.to_dict() for match in positive_p7],
    )

    assert positive_family.status == P7_STATUS_MATCHED
    assert positive.status == STATUS_COMPUTABLE
    assert positive.governed_computation_input is not None
    assert dict(positive.governed_computation_input.source_bindings) == {
        "sale_price": "ventas_periodo",
        "costs": "cmv_total",
        "taxes": "impuestos_periodo",
    }

    negative_p6, negative_p7 = _build_ren_001_semantic_chain(
        xlsx_path=_write_ren_001_xlsx(tmp_path, include_taxes=False),
        expected_roles={
            "ventas_periodo": "sales_amount",
            "cmv_total": "period_costs_total",
        },
    )
    negative_family = next(
        match for match in negative_p7 if match.family_id == FAMILY_PERIOD_NET_MARGIN
    )
    negative = build_service_1_computability_decision_v1(
        case_id="case_ren_001_missing_taxes",
        requested_capability="net_margin_real",
        p6_decisions=[decision.to_dict() for decision in negative_p6],
        requirement_matches=[match.to_dict() for match in negative_p7],
    )

    assert negative_family.status == P7_STATUS_MISSING_REQUIREMENTS
    assert negative.status == STATUS_NEEDS_EVIDENCE

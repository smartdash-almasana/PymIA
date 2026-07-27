from __future__ import annotations

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

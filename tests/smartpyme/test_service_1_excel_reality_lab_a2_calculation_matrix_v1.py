from tools.service_1_excel_reality_lab_a2_calculation_matrix_v1 import (
    TARGETS,
    VERDICT_PASS,
    evaluate_a2_calculation_matrix_v1,
)


def test_a2_calculation_matrix_reuses_governed_physical_controls() -> None:
    result = evaluate_a2_calculation_matrix_v1()
    assert result["verdict"] == VERDICT_PASS, result
    assert result["targets_count"] == 5
    assert result["targets_passed"] == 5
    assert set(result["targets"]) == set(TARGETS)
    assert result["failures"] == []
    assert result["structural_corpus_cases"] == 23
    assert result["structural_cases_not_forced_into_calculation"] is True

    rows = {row["capability"]: row for row in result["rows"]}
    assert set(rows) == set(TARGETS)
    for row in rows.values():
        assert row["p8"] == "COMPUTABLE"
        assert row["governed_input"] is True
        assert row["execution"] == "EVALUATED"
        assert row["numeric_or_bounded_result_verified"] is True
        assert row["ok"] is True

    assert rows["sold_vs_collected_gap"]["computed"]["gap_amount"] == 600.0
    assert rows["projected_closing_cash_balance"]["computed"]["projected_closing_balance"] == 1700.0
    assert rows["dso"]["computed"]["dso_days"] == 10.0
    assert rows["current_ratio"]["computed"]["current_ratio_value"] == 1.5
    assert "net_margin_amount" in rows["net_margin_real"]["computed"]
    assert "net_margin_percentage" in rows["net_margin_real"]["computed"]


def test_a2_is_measurement_not_new_runtime_authority() -> None:
    result = evaluate_a2_calculation_matrix_v1()
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["product_ready"] is False

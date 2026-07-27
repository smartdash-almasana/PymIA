from __future__ import annotations

from tools.service_1_remaining_capability_governance_convergence_audit_v1 import (
    VERDICT_GAPS,
    evaluate_service_1_remaining_capability_governance_convergence_audit_v1,
)


def test_remaining_capabilities_are_not_falsely_declared_physically_governed() -> None:
    result = evaluate_service_1_remaining_capability_governance_convergence_audit_v1()

    assert result["verdict"] == VERDICT_GAPS
    assert result["registry_capabilities"] == 11
    assert result["physical_positive_certified"] == 2  # LIQ_002 + DSO live in registry; LIQ_001 is specialized outside it.
    assert result["remaining_governance_gaps"] == 3
    assert result["scope_fixed"] is True
    assert result["scope_not_reopened"] is True
    assert set(result["gap_capabilities"]) == {
        "adjusted_operating_cash_flow",
        "dpo",
        "payment_collection_gap",
    }
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["product_ready"] is False


def test_only_current_p8_governed_registry_capabilities_are_physically_certified() -> None:
    result = evaluate_service_1_remaining_capability_governance_convergence_audit_v1()
    by_capability = {row["capability"]: row for row in result["rows"]}

    for capability in ("projected_closing_cash_balance", "dso"):
        row = by_capability[capability]
        assert row["exact_formula_in_catalog"] is True
        assert row["pathology_in_enriched_catalog"] is True
        assert row["p7_governed"] is True
        assert row["p8_matrix_governed"] is True
        assert row["fully_governed_for_physical_p8"] is True
        assert row["physical_positive_certified"] is True

    assert by_capability["adjusted_operating_cash_flow"]["catalog_calculation_states"] == ["CALCULABLE_CON_SUPUESTOS"]

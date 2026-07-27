from __future__ import annotations

from tools.service_1_remaining_capability_governance_expansion_plan_v1 import (
    DEFERRED,
    PROMOTE_NOW,
    VERDICT,
    build_service_1_remaining_capability_governance_expansion_plan_v1,
)


def test_bounded_governance_expansion_authorizes_only_calculable_aligned_capabilities() -> None:
    result = build_service_1_remaining_capability_governance_expansion_plan_v1()

    assert result["verdict"] == VERDICT == "AUTHORIZED_BOUNDED_EXPANSION"
    assert result["promote_now_count"] == 6
    assert set(PROMOTE_NOW) == {
        "reorder_point",
        "inventory_turnover",
        "current_ratio",
        "sales_concentration",
        "interest_burden_ratio",
        "index_update_ratio",
    }
    assert all(spec["calculation_state"] == "CALCULABLE" for spec in PROMOTE_NOW.values())
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["product_ready"] is False


def test_governance_expansion_keeps_assumption_and_dependency_gaps_fail_closed() -> None:
    assert set(DEFERRED) == {
        "adjusted_operating_cash_flow",
        "dpo",
        "payment_collection_gap",
    }
    assert DEFERRED["adjusted_operating_cash_flow"]["reason"] == "FORMULA_CALCULABLE_CON_SUPUESTOS"
    assert DEFERRED["dpo"]["reason"] == "NO_CANONICAL_FORMULA_ENTRY_FOR_PREREQUISITE_PATHOLOGY"
    assert DEFERRED["payment_collection_gap"]["reason"] == "COMPOSITE_DEPENDS_ON_UNGOVERNED_DPO"

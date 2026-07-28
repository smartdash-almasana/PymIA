from __future__ import annotations

from pymia.smartpyme.service_1_p6_approval_decision_v1 import Service1P6ApprovalDecisionV1
from pymia.smartpyme.service_1_variable_family_bindings_v1 import build_service_1_requirement_matches_v1
from pymia.smartpyme.service_1_computability_v1 import STATUS_COMPUTABLE, build_service_1_computability_decision_v1
from tools.service_1_remaining_capability_governance_expansion_plan_v1 import PROMOTE_NOW, DEFERRED


def _p6(variable: str) -> Service1P6ApprovalDecisionV1:
    return Service1P6ApprovalDecisionV1(
        case_id="bounded-governance-v1",
        sheet_ref="Governed",
        column_ref=variable,
        status="APPROVED",
        approved_role=variable,
        approved_variable=variable,
        reason="GOVERNANCE_EXPANSION_TEST_EVIDENCE",
        confidence=1.0,
        provenance={"candidate_ref": variable},
    )


def test_six_authorized_capabilities_reach_p8_computable() -> None:
    for capability, spec in PROMOTE_NOW.items():
        p6 = [_p6(variable) for variable in spec["required_variables"]]
        p7 = build_service_1_requirement_matches_v1(p6)
        decision = build_service_1_computability_decision_v1(
            case_id=f"case-{capability}",
            requested_capability=capability,
            p6_decisions=[item.to_dict() for item in p6],
            requirement_matches=[item.to_dict() for item in p7],
        )
        assert decision.status == STATUS_COMPUTABLE, (capability, decision.to_dict())
        assert decision.governed_computation_input is not None
        assert decision.governed_computation_input.formula_id == spec["canonical_formula_id"]
        assert tuple(decision.governed_computation_input.required_variables) == tuple(spec["required_variables"])


def test_three_deferred_capabilities_are_not_promoted() -> None:
    assert set(DEFERRED) == {"adjusted_operating_cash_flow", "dpo", "payment_collection_gap"}
    assert not set(DEFERRED).intersection(PROMOTE_NOW)

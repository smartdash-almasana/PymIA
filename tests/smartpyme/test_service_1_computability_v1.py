from __future__ import annotations

from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE,
    STATUS_UNSUPPORTED_CAPABILITY,
    Service1GovernedComputationInputV1,
    build_service_1_computability_decision_v1,
)


def _p6() -> list[dict]:
    return [
        {"status": "APPROVED", "approved_variable": "sold_amount", "column_ref": "venta_total", "reason": "UNAMBIGUOUS_SEMANTIC_HYPOTHESIS"},
        {"status": "APPROVED", "approved_variable": "collected_amount", "column_ref": "cobrado", "reason": "OWNER_CONFIRMED_SEMANTIC_ROLE"},
    ]


def _p7(*, status: str = "REQUIREMENT_MATCHED") -> list[dict]:
    return [{
        "family_id": "CASH_COLLECTIONS",
        "status": status,
        "missing_role_groups": [] if status == "REQUIREMENT_MATCHED" else [["collected_amount"]],
        "target_capabilities": ["sold_vs_collected_gap"],
        "grain": {
            "structural_scope": "REGION",
            "business_entity_grain": "NONE",
            "temporal_grain": "NONE",
            "aggregation_grain": "ATOMIC",
        },
    }]


def test_p8_emits_governed_computation_input_without_runtime_authority() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8",
        requested_capability="sold_vs_collected_gap",
        p6_decisions=_p6(),
        requirement_matches=_p7(),
    )
    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_computation_input
    assert isinstance(governed, Service1GovernedComputationInputV1)
    assert governed.formula_id == "LIQ_001_vendido_cobrado"
    assert dict(governed.source_bindings) == {"sold_amount": "venta_total", "collected_amount": "cobrado"}
    payload = governed.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["delivery_authorized"] is False


def test_p8_rejects_nonapproved_p6_input() -> None:
    p6 = _p6()
    p6[1]["status"] = "AMBIGUOUS"
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8", requested_capability="sold_vs_collected_gap", p6_decisions=p6, requirement_matches=_p7()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P6_APPROVAL_REQUIRED"


def test_p8_reports_missing_p7_requirements() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8", requested_capability="sold_vs_collected_gap", p6_decisions=_p6(), requirement_matches=_p7(status="MISSING_REQUIREMENTS")
    )
    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.reason == "REQUIREMENTS_NOT_MATCHED"
    assert decision.missing_role_groups == (("collected_amount",),)


def test_p8_does_not_infer_unknown_capability() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8", requested_capability="invented_magic", p6_decisions=_p6(), requirement_matches=_p7()
    )
    assert decision.status == STATUS_UNSUPPORTED_CAPABILITY
    assert decision.reason == "CAPABILITY_NOT_GOVERNED"


def test_governed_input_requires_exact_source_binding_coverage() -> None:
    try:
        Service1GovernedComputationInputV1(
            case_id="case_p8",
            requested_capability="sold_vs_collected_gap",
            family_id="CASH_COLLECTIONS",
            pathology_code="LIQ_001",
            formula_id="LIQ_001_vendido_cobrado",
            formula_expression="sold_amount - collected_amount",
            required_variables=("sold_amount", "collected_amount"),
            required_evidence=(),
            source_bindings={"sold_amount": "venta_total"},
            grain={}, catalog_versions={}, provenance={},
        )
    except ValueError as exc:
        assert "source_bindings" in str(exc)
    else:
        raise AssertionError("incomplete governed source bindings must fail closed")

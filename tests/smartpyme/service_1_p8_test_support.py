from __future__ import annotations

from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_COMPUTABLE,
    Service1ComputabilityDecisionV1,
    Service1GovernedComputationInputV1,
)


def computable_decision_from_governed_payload(payload: dict[str, object], *, case_id: str = "case_test_p8") -> Service1ComputabilityDecisionV1:
    """Build a canonical P8 decision from a governed-input test payload."""
    governed = Service1GovernedComputationInputV1(
        case_id=str(payload.get("case_id") or case_id),
        requested_capability=str(payload.get("requested_capability") or ""),
        family_id=str(payload.get("family_id") or "TEST_FAMILY"),
        pathology_code=str(payload.get("pathology_code") or ""),
        formula_id=str(payload.get("formula_id") or ""),
        formula_expression=str(payload.get("formula_expression") or "fixture_expression"),
        required_variables=tuple(payload.get("required_variables") or ()),
        required_evidence=tuple(payload.get("required_evidence") or ()),
        source_bindings=dict(payload.get("source_bindings") or {}),
        grain=dict(payload.get("grain") or {"structural_scope": "REGION"}),
        catalog_versions=dict(payload.get("catalog_versions") or {}),
        provenance={"source": "TEST_P8_FIXTURE"},
    )
    return Service1ComputabilityDecisionV1(
        case_id=governed.case_id,
        requested_capability=governed.requested_capability,
        status=STATUS_COMPUTABLE,
        reason=None,
        family_id=governed.family_id,
        governed_computation_input=governed,
        provenance={"source": "TEST_P8_FIXTURE"},
    )


def computable_decision_from_legacy_fixture(plan: dict[str, object], *, case_id: str = "case_test_p8") -> Service1ComputabilityDecisionV1:
    """Temporary test migration bridge; remove when no test fixture nests governed input."""
    payload = plan.get("governed_computation_input")
    if not isinstance(payload, dict):
        raise ValueError("test fixture requires governed_computation_input")
    return computable_decision_from_governed_payload(payload, case_id=case_id)


def governed_payload_from_legacy_plan(plan: dict[str, object], *, case_id: str = "case_test_p8") -> dict[str, object]:
    """Project a legacy test fixture into the canonical governed-input payload only."""
    nested = plan.get("governed_computation_input")
    if isinstance(nested, dict):
        return dict(nested)
    required_variables = list(plan.get("required_variables") or [])
    payload = {
        "schema_version": "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1",
        "case_id": case_id,
        "requested_capability": plan.get("requested_capability"),
        "family_id": "TEST_FAMILY",
        "pathology_code": plan.get("pathology_code"),
        "formula_id": plan.get("formula_id"),
        "formula_expression": "fixture_expression",
        "required_variables": required_variables,
        "required_evidence": [],
        "source_bindings": dict(plan.get("source_bindings") or {}),
        "grain": {"structural_scope": "REGION", "business_entity_grain": "NONE", "temporal_grain": "NONE", "aggregation_grain": "ATOMIC"},
        "catalog_versions": {},
        "provenance": {"source": "TEST_P8_FIXTURE"},
    }
    for flag in ("runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated"):
        if flag in plan:
            payload[flag] = plan[flag]
    return payload

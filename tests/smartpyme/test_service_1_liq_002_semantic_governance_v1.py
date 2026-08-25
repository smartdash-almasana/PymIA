from __future__ import annotations

from pymia.smartpyme.service_1_computability_v1 import (
    CONFIRMED_BINDINGS_SCHEMA_VERSION,
    CONFIRMED_BINDINGS_STATUS,
    STATUS_COMPUTABLE,
    build_computability_decision_from_confirmed_bindings_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_CASH_PROJECTION,
    STATUS_READY,
    build_service_1_variable_family_bindings_v1,
)


def _candidate(column: str, variable: str) -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name=column,
        normalized_column_name=column,
        sheet_name="Caja",
        observed_data_type="number",
        sample_values=(),
        candidate_semantic_roles=(variable,),
        candidate_variable_names=(variable,),
        confidence=1.0,
        ambiguity_reason=None,
        owner_confirmation_required=False,
        metadata={
            "primary_semantic_role": variable,
            "owner_confirmed": True,
            "sample_based": False,
        },
    )


def _p6_decision(variable: str, column: str) -> dict[str, object]:
    return {
        "status": "APPROVED",
        "approved_variable": variable,
        "column_ref": column,
        "approved_role": variable,
        "confidence": 1.0,
    }


def _requirement_match() -> dict[str, object]:
    return {
        "status": "REQUIREMENT_MATCHED",
        "target_capabilities": ("projected_closing_cash_balance",),
        "family_id": FAMILY_CASH_PROJECTION,
        "missing_role_groups": [],
    }


def _confirmed_packet() -> dict[str, object]:
    candidates = (
        _candidate("saldo_inicial", "initial_balance"),
        _candidate("cobros_esperados", "expected_collections"),
        _candidate("pagos_esperados", "expected_payments"),
    )
    families = build_service_1_variable_family_bindings_v1(candidates)
    return {
        "schema_version": CONFIRMED_BINDINGS_SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "status": CONFIRMED_BINDINGS_STATUS,
        "bridge_packet": {
            "case_id": "case_liq_002_real_semantic_governance",
            "column_candidates": candidates,
        },
        "gate_packet": {
            "variable_family_bindings": families,
            "ready_variable_family_ids": [
                item.family_id for item in families if item.status == STATUS_READY
            ],
            "p6_decisions": [
                _p6_decision("initial_balance", "saldo_inicial"),
                _p6_decision("expected_collections", "cobros_esperados"),
                _p6_decision("expected_payments", "pagos_esperados"),
            ],
            "requirement_matches": [_requirement_match()],
        },
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def test_cash_projection_family_is_ready_only_with_three_confirmed_roles() -> None:
    packet = _confirmed_packet()
    families = packet["gate_packet"]["variable_family_bindings"]
    cash_projection = next(
        item for item in families if item.family_id == FAMILY_CASH_PROJECTION
    )

    assert cash_projection.status == STATUS_READY
    assert cash_projection.coverage_ratio == 1.0
    assert cash_projection.target_variable_names == (
        "initial_balance",
        "expected_collections",
        "expected_payments",
    )
    assert cash_projection.target_capabilities == (
        "projected_closing_cash_balance",
    )
    assert cash_projection.runtime_authorized is False
    assert cash_projection.delivery_authorized is False


def test_liq_002_builds_real_governed_p8_input_without_monkeypatch() -> None:
    decision = build_computability_decision_from_confirmed_bindings_v1(
        confirmed_bindings=_confirmed_packet(),
        requested_capability="projected_closing_cash_balance",
    )

    assert decision.status == STATUS_COMPUTABLE
    assert decision.family_id == FAMILY_CASH_PROJECTION
    governed = decision.governed_computation_input
    assert governed is not None
    assert governed.pathology_code == "LIQ_002"
    assert governed.formula_id == "LIQ_002_saldo_final_proyectado"
    assert list(governed.required_variables) == [
        "initial_balance",
        "expected_collections",
        "expected_payments",
    ]
    assert dict(governed.source_bindings) == {
        "initial_balance": "saldo_inicial",
        "expected_collections": "cobros_esperados",
        "expected_payments": "pagos_esperados",
    }
    assert governed.catalog_versions["evidence_matrix"] == "2.0"
    payload = governed.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["tool_execution_authorized"] is False
    assert payload["product_ready"] is False
    assert payload["delivery_authorized"] is False
    assert payload["diagnosis_generated"] is False

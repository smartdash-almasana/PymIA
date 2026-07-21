from __future__ import annotations

from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    STATUS_READY_FOR_COMPUTATION,
    build_computation_plan,
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


def _confirmed_packet() -> dict[str, object]:
    candidates = (
        _candidate("saldo_inicial", "initial_balance"),
        _candidate("cobros_esperados", "expected_collections"),
        _candidate("pagos_esperados", "expected_payments"),
    )
    families = build_service_1_variable_family_bindings_v1(candidates)
    return {
        "schema_version": "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1",
        "service_name": "SERVICE_1",
        "status": STATUS_CONFIRMED_BINDINGS,
        "bridge_packet": {
            "case_id": "case_liq_002_real_semantic_governance",
            "column_candidates": candidates,
        },
        "gate_packet": {
            "variable_family_bindings": families,
            "ready_variable_family_ids": [
                item.family_id for item in families if item.status == STATUS_READY
            ],
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


def test_liq_002_builds_real_governed_plan_without_monkeypatch() -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_packet(),
        requested_capability="projected_closing_cash_balance",
    )

    assert plan["status"] == STATUS_READY_FOR_COMPUTATION
    assert plan["family_id"] == FAMILY_CASH_PROJECTION
    assert plan["family_status"] == STATUS_READY
    assert plan["pathology_code"] == "LIQ_002"
    assert plan["formula_id"] == "LIQ_002_saldo_final_proyectado"
    assert plan["required_variables"] == [
        "initial_balance",
        "expected_collections",
        "expected_payments",
    ]
    assert plan["source_bindings"] == {
        "initial_balance": "saldo_inicial",
        "expected_collections": "cobros_esperados",
        "expected_payments": "pagos_esperados",
    }
    assert plan["catalog_versions"]["evidence_matrix"] == "1.1"
    assert plan["computation_candidate_ready"] is True
    assert plan["runtime_authorized"] is False
    assert plan["tool_execution_authorized"] is False
    assert plan["product_ready"] is False
    assert plan["delivery_authorized"] is False
    assert plan["diagnosis_generated"] is False
    assert plan["computation_executed"] is False

from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_computability_v1 import STATUS_COMPUTABLE
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    build_computability_decision_from_confirmed_bindings_v1,
)
from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import (
    CLASS_EXCEEDS_PERIOD,
    STATUS_INVALID_INPUT,
    evaluate_pyme_011_v1,
)
from pymia.smartpyme.service_1_pyme_011_normalized_evidence_v1 import (
    evaluate_pyme_011_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_pyme_011_outcome_v1 import (
    STATUS_READY,
    build_pyme_011_outcome_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    build_service_1_p6_approval_decisions_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_RECEIVABLES_DSO,
    build_service_1_requirement_matches_v1,
)
from tests.smartpyme.service_1_p8_test_support import computable_decision_from_legacy_fixture


def _candidate(column: str, role: str, variable: str) -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name=column,
        normalized_column_name=column,
        sheet_name="Cobranzas",
        observed_data_type="number",
        sample_values=(),
        candidate_semantic_roles=(role,),
        candidate_variable_names=(variable,),
        confidence=1.0,
        ambiguity_reason=None,
        owner_confirmation_required=False,
        metadata={"primary_semantic_role": role, "sample_based": False},
    )


def _confirmed_packet() -> dict[str, object]:
    candidates = (
        _candidate("cuentas_por_cobrar", "accounts_receivable_amount", "accounts_receivable"),
        _candidate("ventas_periodo", "sales_amount", "sales"),
        _candidate("dias_periodo", "period_days", "days"),
    )
    case_id = "case_pyme_011_real_governance"
    owner_events = tuple(
        {
            "confirmed_by_owner": True,
            "question_ref": f"Cobranzas::{candidate.source_column_name}",
            "sheet_ref": "Cobranzas",
            "column_ref": candidate.source_column_name,
            "confirmation_scope": "SEMANTIC_ROLE",
            "confirmed_role": candidate.candidate_semantic_roles[0],
        }
        for candidate in candidates
    )
    p6 = build_service_1_p6_approval_decisions_v1(
        case_id=case_id,
        candidates=candidates,
        owner_confirmation_events=owner_events,
    )
    requirements = build_service_1_requirement_matches_v1(p6)
    return {
        "schema_version": "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1",
        "service_name": "SERVICE_1",
        "status": STATUS_CONFIRMED_BINDINGS,
        "bridge_packet": {"case_id": case_id, "column_candidates": candidates},
        "gate_packet": {
            "p6_decisions": [item.to_dict() for item in p6],
            "requirement_matches": [item.to_dict() for item in requirements],
        },
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _plan() -> dict[str, object]:
    bindings = {
        "accounts_receivable": "cuentas_por_cobrar",
        "sales": "ventas_periodo",
        "days": "dias_periodo",
    }
    required = ["accounts_receivable", "sales", "days"]
    governed = {
        "schema_version": "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1",
        "requested_capability": "dso",
        "pathology_code": "PYME_011",
        "formula_id": "PYME_011_dso",
        "required_variables": required,
        "source_bindings": bindings,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "dso",
        "pathology_code": "PYME_011",
        "formula_id": "PYME_011_dso",
        "required_variables": required,
        "source_bindings": bindings,
        "governed_computation_input": governed,
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _evidence() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    tables = [{"sheet_name": "Cobranzas", "rows": [
        {"cuentas_por_cobrar": 600, "ventas_periodo": 400, "dias_periodo": 30},
        {"cuentas_por_cobrar": 300, "ventas_periodo": 200, "dias_periodo": 30},
    ]}]
    refs = [
        {"sheet_name": "Cobranzas", "column_name": "cuentas_por_cobrar", "normalized_column_name": "cuentas_por_cobrar"},
        {"sheet_name": "Cobranzas", "column_name": "ventas_periodo", "normalized_column_name": "ventas_periodo"},
        {"sheet_name": "Cobranzas", "column_name": "dias_periodo", "normalized_column_name": "dias_periodo"},
    ]
    return tables, refs


def test_pyme_011_math_blocks_zero_sales() -> None:
    result = evaluate_pyme_011_v1(accounts_receivable=100, sales=0, days=30)
    assert result["status"] == STATUS_INVALID_INPUT
    assert any("sales must be greater than 0" in error for error in result["errors"])


def test_pyme_011_builds_real_governed_p8_input_without_monkeypatch() -> None:
    decision = build_computability_decision_from_confirmed_bindings_v1(
        confirmed_bindings=_confirmed_packet(),
        requested_capability="dso",
    )
    assert decision.status == STATUS_COMPUTABLE
    assert decision.family_id == FAMILY_RECEIVABLES_DSO
    governed = decision.governed_computation_input
    assert governed is not None
    assert governed.pathology_code == "PYME_011"
    assert governed.formula_id == "PYME_011_dso"
    assert dict(governed.source_bindings) == {
        "accounts_receivable": "cuentas_por_cobrar",
        "sales": "ventas_periodo",
        "days": "dias_periodo",
    }
    assert governed.catalog_versions["evidence_matrix"] == "2.0"


def test_pyme_011_aggregates_confirmed_evidence_and_builds_bounded_outcome() -> None:
    tables, refs = _evidence()
    evaluation = evaluate_pyme_011_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )
    assert evaluation["status"] == "EVALUATED"
    assert evaluation["classification"] == CLASS_EXCEEDS_PERIOD
    assert evaluation["computed"]["dso_days"] == 45.0
    assert evaluation["aggregation"]["sample_based"] is False
    outcome = build_pyme_011_outcome_v1(computation_result=evaluation)
    assert outcome["status"] == STATUS_READY
    assert outcome["bounded_finding_generated"] is True
    assert outcome["causal_diagnosis_generated"] is False
    assert outcome["forbidden_claims"]


def test_product_root_executes_only_explicit_pyme_011_and_blocks_delivery(monkeypatch, tmp_path) -> None:
    tables, refs = _evidence()
    confirmed = {"status": product.STATUS_CONFIRMED_BINDINGS, "schema_version": "TEST", "service_name": "SERVICE_1"}
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computability_decision_from_confirmed_bindings_v1", lambda **_: computable_decision_from_legacy_fixture(_plan()))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
        deliver_result=True,
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "PYME_011_DELIVERY_NOT_AUTHORIZED"
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["diagnosis_generated"] is False

from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_ren_001_normalized_evidence_v1 import (
    STATUS_EVIDENCE_BLOCKED,
    evaluate_ren_001_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_ren_001_outcome_v1 import (
    STATUS_READY,
    build_ren_001_outcome_v1,
)


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "net_margin_real",
        "pathology_code": "REN_001",
        "formula_id": "REN_001_margen_neto_real",
        "required_variables": ["sale_price", "costs", "taxes"],
        "source_bindings": {
            "sale_price": "ventas",
            "costs": "costos",
            "taxes": "impuestos",
        },
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _evidence() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    tables = [
        {
            "sheet_name": "ventas",
            "rows": [
                {"ventas": 1000, "costos": 600, "impuestos": 100},
                {"ventas": 500, "costos": 350, "impuestos": 50},
            ],
        }
    ]
    refs = [
        {"sheet_name": "ventas", "column_name": "ventas", "normalized_column_name": "ventas"},
        {"sheet_name": "ventas", "column_name": "costos", "normalized_column_name": "costos"},
        {"sheet_name": "ventas", "column_name": "impuestos", "normalized_column_name": "impuestos"},
    ]
    return tables, refs


def test_ren_001_aggregates_confirmed_normalized_rows() -> None:
    tables, refs = _evidence()
    result = evaluate_ren_001_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )

    assert result["status"] == "EVALUATED"
    assert result["classification"] == "POSITIVE_MARGIN"
    assert result["inputs"] == {"sale_price": 1500.0, "costs": 950.0, "taxes": 150.0}
    assert result["computed"]["net_margin_amount"] == 400.0
    assert result["aggregation"]["sample_based"] is False


def test_ren_001_blocks_ambiguous_column_resolution() -> None:
    tables, refs = _evidence()
    refs.append(dict(refs[0]))
    result = evaluate_ren_001_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )

    assert result["status"] == STATUS_EVIDENCE_BLOCKED
    assert result["diagnosis_generated"] is False
    assert any("must resolve exactly once" in error for error in result["errors"])


def test_ren_001_outcome_is_bounded_and_non_causal() -> None:
    tables, refs = _evidence()
    evaluation = evaluate_ren_001_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )
    outcome = build_ren_001_outcome_v1(computation_result=evaluation)

    assert outcome["status"] == STATUS_READY
    assert outcome["bounded_finding_generated"] is True
    assert outcome["causal_diagnosis_generated"] is False
    assert outcome["runtime_authorized"] is False
    assert outcome["delivery_authorized"] is False
    assert outcome["treatment_actions"]
    assert outcome["forbidden_claims"]


def test_product_root_absorbs_only_explicit_ren_001_capability(monkeypatch, tmp_path) -> None:
    tables, refs = _evidence()
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan())

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
    )

    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["tools_executed"] is False
    assert result["diagnosis_generated"] is False
    assert result["runtime_authorized"] is False


def test_ren_001_delivery_remains_blocked(monkeypatch, tmp_path) -> None:
    tables, refs = _evidence()
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan())

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
        deliver_result=True,
    )

    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "REN_001_DELIVERY_NOT_AUTHORIZED"
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False

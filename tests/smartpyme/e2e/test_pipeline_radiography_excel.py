from __future__ import annotations

from pathlib import Path

from pymia.pipeline_radiography import (
    PipelineScenario,
    ScenarioEvidence,
    ScenarioExpectation,
    run_pipeline_scenario,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "smartpyme"
    / "ventas_costos_margen.xlsx"
)


def test_excel_pipeline_happy_path_reaches_ready_to_deliver(tmp_path: Path) -> None:
    scenario = PipelineScenario(
        scenario_id="margin_excel_happy_path",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_ventas_costos",
                source_kind="uploaded_file",
                source_ref=str(FIXTURE_PATH),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
            ScenarioEvidence(
                evidence_type="ventas_del_periodo",
                source_kind="uploaded_file",
                source_ref=str(FIXTURE_PATH),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
            ScenarioEvidence(
                evidence_type="costos_directos",
                source_kind="uploaded_file",
                source_ref=str(FIXTURE_PATH),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="READY_TO_DELIVER",
            runtime_classification="excel_diagnostic",
            dispatch_status="EXECUTED",
            min_findings_count=1,
        ),
    )

    result = run_pipeline_scenario(scenario, output_root=tmp_path)

    assert result.trace.overall_status == "PASS"
    assert result.trace.final_summary["final_status"] == "READY_TO_DELIVER"
    assert result.trace.final_summary["runtime_classification"] == "excel_diagnostic"
    assert result.trace.final_summary["dispatch_status"] == "EXECUTED"
    assert result.trace.final_summary["findings_count"] >= 1
    assert result.execution_gate_verdict is not None
    assert result.execution_gate_verdict["verdict"] == "PASS"
    assert result.delivery_package is not None
    assert result.delivery_package["status"] == "READY_TO_DELIVER"
    assert result.execution_result is not None
    assert result.execution_result["output_refs"]
    assert all(Path(ref).exists() for ref in result.execution_result["output_refs"])
    stage_names = [stage.name for stage in result.trace.stages]
    assert "microservice_dispatcher" in stage_names


def test_margin_without_evidence_blocks_before_dispatch(tmp_path: Path) -> None:
    scenario = PipelineScenario(
        scenario_id="margin_excel_missing_evidence",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(),
        expected=ScenarioExpectation(
            final_status="NEEDS_EVIDENCE",
            must_not_dispatch=True,
        ),
    )

    result = run_pipeline_scenario(scenario, output_root=tmp_path)

    assert result.trace.overall_status == "BLOCKED_EXPECTED"
    assert result.trace.blocked_at in {"evidence_gate", "readiness"}
    assert result.trace.final_summary["must_not_dispatch"] is True
    assert result.execution_result is None
    assert result.execution_gate_verdict is None
    assert result.delivery_package is None
    stage_names = [stage.name for stage in result.trace.stages]
    assert "microservice_dispatcher" not in stage_names

from __future__ import annotations

import json
from pathlib import Path

from pymia.pipeline_radiography import (
    PipelineScenario,
    ScenarioEvidence,
    ScenarioExpectation,
    generate_developer_report,
    run_pipeline_scenario,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "smartpyme"
    / "ventas_costos_margen.xlsx"
)


def _assert_developer_report(result, output_dir: Path) -> None:
    generate_developer_report(result, output_dir)
    report_path = output_dir / "report.md"
    trace_path = output_dir / "trace.json"
    assert report_path.exists()
    assert trace_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "Expected vs Actual" in report_text
    assert result.trace.overall_status in report_text
    trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace_data["trace_id"] == result.trace.trace_id
    assert trace_data["trace"]["overall_status"] == result.trace.overall_status


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
    _assert_developer_report(result, tmp_path / result.trace.trace_id)

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
    _assert_developer_report(result, tmp_path / result.trace.trace_id)

    assert result.trace.overall_status == "BLOCKED_EXPECTED"
    assert result.trace.blocked_at in {"evidence_gate", "readiness"}
    assert result.trace.final_summary["must_not_dispatch"] is True
    assert result.execution_result is None
    assert result.execution_gate_verdict is None
    assert result.delivery_package is None
    stage_names = [stage.name for stage in result.trace.stages]
    assert "microservice_dispatcher" not in stage_names


def test_evidence_type_mismatch_blocks_at_gate(tmp_path: Path) -> None:
    scenario = PipelineScenario(
        scenario_id="evidence_type_mismatch",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_proveedores",
                source_kind="uploaded_file",
                source_ref=str(FIXTURE_PATH),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="NEEDS_EVIDENCE",
            must_not_dispatch=True,
        ),
    )

    result = run_pipeline_scenario(scenario, output_root=tmp_path)
    _assert_developer_report(result, tmp_path / result.trace.trace_id)

    assert result.trace.overall_status == "BLOCKED_EXPECTED"
    assert result.trace.blocked_at == "evidence_gate"
    assert result.trace.final_summary["must_not_dispatch"] is True
    stage_names = [stage.name for stage in result.trace.stages]
    assert "microservice_dispatcher" not in stage_names


def test_unsupported_runtime_classification(tmp_path: Path) -> None:
    scenario = PipelineScenario(
        scenario_id="unsupported_runtime_classification",
        tenant_id="tenant_demo",
        owner_message="Quiero revisar duplicados de proveedores",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_proveedores",
                source_kind="uploaded_file",
                source_ref=str(FIXTURE_PATH),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="BLOCKED",
            dispatch_status="UNSUPPORTED",
        ),
    )

    result = run_pipeline_scenario(scenario, output_root=tmp_path)
    _assert_developer_report(result, tmp_path / result.trace.trace_id)

    assert result.trace.final_summary["final_status"] != "READY_TO_DELIVER"
    if result.trace.overall_status == "BLOCKED_EXPECTED":
        assert result.trace.blocked_at in {"readiness", "runtime_bridge"}
    else:
        assert result.trace.final_summary["dispatch_status"] == "UNSUPPORTED"
        stage_names = [stage.name for stage in result.trace.stages]
        assert "microservice_dispatcher" in stage_names

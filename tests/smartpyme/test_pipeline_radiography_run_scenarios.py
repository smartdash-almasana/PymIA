from __future__ import annotations

import json
from pathlib import Path

from pymia.pipeline_radiography import (
    PipelineScenario,
    PipelineStageTrace,
    PipelineTrace,
    ScenarioExpectation,
)
from pymia.pipeline_radiography.run_scenarios import main


def _scenario(scenario_id: str) -> PipelineScenario:
    return PipelineScenario(
        scenario_id=scenario_id,
        tenant_id="tenant_demo",
        owner_message="test",
        evidence_items=(),
        expected=ScenarioExpectation(final_status="READY_TO_DELIVER"),
    )


def _result_for(scenario: PipelineScenario, status: str):
    trace = PipelineTrace(
        trace_id=f"trace_{scenario.scenario_id}",
        scenario_id=scenario.scenario_id,
        overall_status=status,
        blocked_at="evidence_gate" if status == "BLOCKED_EXPECTED" else None,
        final_summary={
            "final_status": "READY_TO_DELIVER" if status == "PASS" else "NEEDS_EVIDENCE",
            "runtime_classification": "excel_diagnostic",
            "dispatch_status": None,
            "findings_count": 0,
            "must_not_dispatch": status == "BLOCKED_EXPECTED",
        },
        duration_ms=12,
    )
    trace.add_stage(PipelineStageTrace(name="intake", status="OK", duration_ms=1))

    class DummyResult:
        def __init__(self):
            self.scenario = scenario
            self.trace = trace
            self.intake_record = {}
            self.evidence_records = []
            self.sufficiency_result = {}
            self.readiness_result = {}
            self.runtime_candidate = {}
            self.execution_result = None
            self.execution_gate_verdict = None
            self.delivery_package = None

    return DummyResult()


def test_main_returns_zero_for_pass_and_blocked_expected(monkeypatch, tmp_path: Path) -> None:
    scenarios = [_scenario("one"), _scenario("two")]
    results = {
        "one": _result_for(scenarios[0], "PASS"),
        "two": _result_for(scenarios[1], "BLOCKED_EXPECTED"),
    }
    report_calls: list[Path] = []

    monkeypatch.setattr(
        "pymia.pipeline_radiography.run_scenarios.get_all_scenarios",
        lambda: scenarios,
    )
    monkeypatch.setattr(
        "pymia.pipeline_radiography.run_scenarios.run_pipeline_scenario",
        lambda scenario, output_root: results[scenario.scenario_id],
    )
    monkeypatch.setattr(
        "pymia.pipeline_radiography.run_scenarios.generate_developer_report",
        lambda result, output_dir: report_calls.append(Path(output_dir)),
    )

    output_dir = tmp_path / "custom-output"
    exit_code = main(["--output-dir", str(output_dir)])

    assert exit_code == 0
    assert report_calls == [output_dir / "one", output_dir / "two"]
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "index.md").exists()
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["total_scenarios"] == 2
    assert summary["passed"] == 1
    assert summary["blocked_expected"] == 1


def test_main_returns_one_when_any_scenario_fails(monkeypatch, tmp_path: Path) -> None:
    scenarios = [_scenario("one"), _scenario("two")]
    results = {
        "one": _result_for(scenarios[0], "PASS"),
        "two": _result_for(scenarios[1], "FAIL"),
    }

    monkeypatch.setattr(
        "pymia.pipeline_radiography.run_scenarios.get_all_scenarios",
        lambda: scenarios,
    )
    monkeypatch.setattr(
        "pymia.pipeline_radiography.run_scenarios.run_pipeline_scenario",
        lambda scenario, output_root: results[scenario.scenario_id],
    )
    monkeypatch.setattr(
        "pymia.pipeline_radiography.run_scenarios.generate_developer_report",
        lambda result, output_dir: None,
    )

    exit_code = main(["--output-dir", str(tmp_path / "cli-output")])

    assert exit_code == 1

from __future__ import annotations

import json
from pathlib import Path

from .runner import PipelineRunResult


def _render_expected_vs_actual_table(result: PipelineRunResult) -> str:
    expected = result.scenario.expected.to_dict()
    actual = result.trace.final_summary
    rows = [
        ("final_status", expected.get("final_status"), actual.get("final_status")),
        (
            "runtime_classification",
            expected.get("runtime_classification"),
            actual.get("runtime_classification"),
        ),
        ("dispatch_status", expected.get("dispatch_status"), actual.get("dispatch_status")),
        (
            "findings_count",
            f">= {expected.get('min_findings_count', 0)}",
            actual.get("findings_count"),
        ),
        (
            "must_not_dispatch",
            expected.get("must_not_dispatch", False),
            actual.get("must_not_dispatch"),
        ),
    ]
    lines = [
        "| Field | Expected | Actual | Match |",
        "|---|---|---|---|",
    ]
    for field, exp, act in rows:
        if field == "findings_count":
            match = "YES" if int(actual.get("findings_count", 0) or 0) >= int(expected.get("min_findings_count", 0) or 0) else "NO"
        else:
            match = "YES" if exp == act else "NO"
        lines.append(f"| {field} | {exp} | {act} | {match} |")
    return "\n".join(lines)


def _render_errors_and_warnings(result: PipelineRunResult) -> str:
    messages: list[str] = []
    for stage in result.trace.stages:
        if stage.error:
            messages.append(f"- {stage.name} error: {stage.error}")
        warnings = stage.summary.get("warnings")
        if isinstance(warnings, list):
            for item in warnings:
                messages.append(f"- {stage.name} warning: {item}")
    if not messages:
        messages.append("- None")
    return "\n".join(messages)


def _render_report_markdown(result: PipelineRunResult) -> str:
    scenario = result.scenario
    evidence_lines = [
        f"- `{item.evidence_type}`: `{item.source_ref}`"
        for item in scenario.evidence_items
    ] or ["- None"]
    stage_lines: list[str] = []
    for index, stage in enumerate(result.trace.stages, start=1):
        stage_lines.extend(
            [
                f"### {index}. {stage.name}",
                f"- Status: {stage.status}",
                f"- Input: {stage.input_type or 'N/A'}",
                f"- Output: {stage.output_type or 'N/A'}",
                f"- Duration: {stage.duration_ms}ms",
                f"- Summary: `{json.dumps(stage.summary, ensure_ascii=False, default=str)}`",
            ]
        )
        if stage.error:
            stage_lines.append(f"- Error: {stage.error}")
        stage_lines.append("")
    blocked_at = result.trace.blocked_at or "N/A"
    return "\n".join(
        [
            "# Pipeline Radiography Report",
            "",
            "## Summary",
            f"- Scenario ID: `{scenario.scenario_id}`",
            f"- Trace ID: `{result.trace.trace_id}`",
            f"- Overall Status: `{result.trace.overall_status}`",
            f"- Blocked At: `{blocked_at}`",
            f"- Execution Time: `{result.trace.duration_ms}`ms",
            "",
            "## Scenario Context",
            f"- Tenant ID: `{scenario.tenant_id}`",
            f"- Owner Message: `{scenario.owner_message}`",
            f"- Evidence Items: `{len(scenario.evidence_items)}`",
            *evidence_lines,
            "",
            "## Expected vs Actual",
            _render_expected_vs_actual_table(result),
            "",
            "## Stage-by-Stage Execution",
            *stage_lines,
            "## Errors/Warnings",
            _render_errors_and_warnings(result),
        ]
    ).rstrip() + "\n"


def generate_developer_report(result: PipelineRunResult, output_dir: Path | str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / "report.md"
    trace_path = output_path / "trace.json"

    report_path.write_text(_render_report_markdown(result), encoding="utf-8")
    trace_payload = {
        "trace_id": result.trace.trace_id,
        "scenario_id": result.scenario.scenario_id,
        "scenario": result.scenario.to_dict(),
        "trace": result.trace.to_dict(),
        "result": {
            "intake_record": result.intake_record,
            "evidence_records": result.evidence_records,
            "sufficiency_result": result.sufficiency_result,
            "readiness_result": result.readiness_result,
            "runtime_candidate": result.runtime_candidate,
            "execution_result": result.execution_result,
            "execution_gate_verdict": result.execution_gate_verdict,
            "delivery_package": result.delivery_package,
        },
    }
    trace_path.write_text(
        json.dumps(trace_payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


__all__ = ["generate_developer_report"]

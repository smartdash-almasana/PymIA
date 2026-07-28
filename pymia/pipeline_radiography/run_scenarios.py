from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .report import generate_developer_report
from .runner import PipelineRunResult, run_pipeline_scenario
from .scenarios_registry import get_all_scenarios


def _build_summary(results: list[PipelineRunResult]) -> dict:
    counts = {
        "PASS": 0,
        "BLOCKED_EXPECTED": 0,
        "FAIL": 0,
        "AMBIGUOUS": 0,
    }
    scenarios: list[dict] = []
    for result in results:
        overall_status = result.trace.overall_status
        counts[overall_status] = counts.get(overall_status, 0) + 1
        scenarios.append(
            {
                "scenario_id": result.scenario.scenario_id,
                "trace_id": result.trace.trace_id,
                "overall_status": overall_status,
                "blocked_at": result.trace.blocked_at,
                "duration_ms": result.trace.duration_ms,
            }
        )
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scenarios": len(results),
        "passed": counts["PASS"],
        "blocked_expected": counts["BLOCKED_EXPECTED"],
        "failed": counts["FAIL"],
        "ambiguous": counts["AMBIGUOUS"],
        "scenarios": scenarios,
    }


def _build_index_markdown(results: list[PipelineRunResult]) -> str:
    lines = [
        "# Pipeline Radiography Index",
        "",
        "| Scenario ID | Trace ID | Overall Status | Blocked At | Duration (ms) |",
        "|---|---|---|---|---|",
    ]
    for result in results:
        blocked_at = result.trace.blocked_at or "N/A"
        lines.append(
            f"| {result.scenario.scenario_id} | {result.trace.trace_id} | "
            f"{result.trace.overall_status} | {blocked_at} | {result.trace.duration_ms} |"
        )
    return "\n".join(lines) + "\n"


def run_all_scenarios(*, output_dir: Path | str) -> int:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results: list[PipelineRunResult] = []
    for scenario in get_all_scenarios():
        result = run_pipeline_scenario(scenario, output_root=output_path)
        scenario_output_dir = output_path / scenario.scenario_id
        generate_developer_report(result, scenario_output_dir)
        results.append(result)

    summary = _build_summary(results)
    (output_path / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (output_path / "index.md").write_text(
        _build_index_markdown(results),
        encoding="utf-8",
    )

    has_failure = any(
        result.trace.overall_status in {"FAIL", "AMBIGUOUS"}
        for result in results
    )
    return 1 if has_failure else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=".pipeline_radiography",
    )
    args = parser.parse_args(argv)
    return run_all_scenarios(output_dir=args.output_dir)


if __name__ == "__main__":
    sys.exit(main())

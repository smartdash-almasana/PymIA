from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pymia.smartpyme.capability_registry import load_registry


class HarnessInputError(Exception):
    pass


_PARTIAL_STATUSES: tuple[str, ...] = (
    "PARTIALLY_AVAILABLE_BY_PATH",
    "UNSUPPORTED_IN_DISPATCHER",
    "AVAILABLE",
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HarnessInputError(f"Missing required file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise HarnessInputError(f"Expected JSON object in: {path}")
    return data


def _require_fields(data: dict[str, Any], fields: tuple[str, ...], *, label: str) -> None:
    for field in fields:
        if field not in data:
            raise HarnessInputError(f"{label} missing required field: {field}")


def _normalize_trace_entry(trace_payload: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    trace = trace_payload.get("trace")
    if not isinstance(trace, dict):
        raise HarnessInputError(f"trace payload missing trace object for scenario {scenario_id}")

    _require_fields(
        trace,
        ("overall_status", "blocked_at", "final_summary"),
        label=f"trace[{scenario_id}]",
    )
    final_summary = trace.get("final_summary")
    if not isinstance(final_summary, dict):
        raise HarnessInputError(f"trace[{scenario_id}].final_summary must be an object")

    return {
        "trace_id": str(trace_payload.get("trace_id") or ""),
        "scenario_id": scenario_id,
        "overall_status": str(trace.get("overall_status") or ""),
        "blocked_at": trace.get("blocked_at"),
        "duration_ms": int(trace.get("duration_ms") or 0),
        "runtime_classification": final_summary.get("runtime_classification"),
        "final_status": final_summary.get("final_status"),
        "dispatch_status": final_summary.get("dispatch_status"),
        "findings_count": int(final_summary.get("findings_count") or 0),
        "must_not_dispatch": bool(final_summary.get("must_not_dispatch")),
    }


def load_radiography_bundle(output_dir: Path | str) -> dict[str, Any]:
    base_dir = Path(output_dir)
    summary = _read_json(base_dir / "summary.json")
    _require_fields(
        summary,
        (
            "total_scenarios",
            "passed",
            "blocked_expected",
            "failed",
            "ambiguous",
            "scenarios",
        ),
        label="summary",
    )
    scenarios = summary.get("scenarios")
    if not isinstance(scenarios, list):
        raise HarnessInputError("summary.scenarios must be a list")

    traces: list[dict[str, Any]] = []
    for row in scenarios:
        if not isinstance(row, dict):
            raise HarnessInputError("summary.scenarios entries must be objects")
        scenario_id = str(row.get("scenario_id") or "").strip()
        if not scenario_id:
            raise HarnessInputError("summary.scenarios entry missing scenario_id")
        trace_payload = _read_json(base_dir / scenario_id / "trace.json")
        traces.append(_normalize_trace_entry(trace_payload, scenario_id))

    return {
        "summary": summary,
        "traces": sorted(traces, key=lambda item: item["scenario_id"]),
    }


def build_operational_status(output_dir: Path | str) -> dict[str, Any]:
    registry = load_registry()
    capabilities = sorted(
        [dict(item) for item in registry["capabilities"]],
        key=lambda item: item["capability_id"],
    )
    bundle = load_radiography_bundle(output_dir)
    traces = bundle["traces"]

    capability_by_classification = {
        capability["dispatcher_classification"]: capability
        for capability in capabilities
        if isinstance(capability.get("dispatcher_classification"), str)
        and capability["dispatcher_classification"]
    }

    certified_capabilities: list[dict[str, Any]] = []
    for capability in capabilities:
        if capability["status"] != "PIPELINE_CERTIFIED":
            continue
        matching_traces = [
            trace for trace in traces
            if trace["runtime_classification"] == capability["dispatcher_classification"]
        ]
        certified_capabilities.append(
            {
                "capability_id": capability["capability_id"],
                "label": capability.get("label"),
                "status": capability["status"],
                "trace_ids": sorted(
                    trace["trace_id"] for trace in matching_traces if trace["trace_id"]
                ),
                "scenario_ids": sorted(
                    trace["scenario_id"] for trace in matching_traces
                ),
            }
        )

    partial_capabilities = [
        {
            "capability_id": capability["capability_id"],
            "label": capability.get("label"),
            "status": capability["status"],
        }
        for capability in capabilities
        if capability["status"] in _PARTIAL_STATUSES
    ]

    failed_scenarios = sorted(
        [
            {
                "scenario_id": trace["scenario_id"],
                "trace_id": trace["trace_id"],
                "overall_status": trace["overall_status"],
                "blocked_at": trace["blocked_at"],
            }
            for trace in traces
            if trace["overall_status"] == "FAIL"
        ],
        key=lambda item: item["scenario_id"],
    )

    blocked_expected_scenarios = sorted(
        [
            {
                "scenario_id": trace["scenario_id"],
                "trace_id": trace["trace_id"],
                "blocked_at": trace["blocked_at"],
                "duration_ms": trace["duration_ms"],
            }
            for trace in traces
            if trace["overall_status"] == "BLOCKED_EXPECTED"
        ],
        key=lambda item: item["scenario_id"],
    )

    ambiguous_scenarios = [
        {
            "scenario_id": trace["scenario_id"],
            "trace_id": trace["trace_id"],
            "reason": "overall_status_ambiguous",
        }
        for trace in traces
        if trace["overall_status"] == "AMBIGUOUS"
    ]

    for trace in traces:
        classification = trace["runtime_classification"]
        if classification is None or str(classification).strip() == "":
            continue
        if classification not in capability_by_classification:
            ambiguous_scenarios.append(
                {
                    "scenario_id": trace["scenario_id"],
                    "trace_id": trace["trace_id"],
                    "reason": "orphan_classification",
                    "runtime_classification": classification,
                }
            )

    ambiguous_scenarios = sorted(
        ambiguous_scenarios,
        key=lambda item: (item["scenario_id"], item.get("reason", "")),
    )

    failed_count = len(failed_scenarios)
    ambiguous_count = len(ambiguous_scenarios)
    partial_count = len(partial_capabilities)
    has_orphan = any(item.get("reason") == "orphan_classification" for item in ambiguous_scenarios)

    if failed_count > 0:
        pipeline_status = "RED"
    elif ambiguous_count > 0 or partial_count > 0:
        pipeline_status = "YELLOW"
    else:
        pipeline_status = "GREEN"

    if failed_count > 1:
        next_action = "FIX_SCENARIOS"
    elif failed_count == 1:
        next_action = "FIX_SCENARIO"
    elif has_orphan:
        next_action = "REVIEW_REGISTRY"
    elif ambiguous_count > 0:
        next_action = "RE_RUN_RADIOGRAPHY"
    elif partial_count > 0:
        next_action = "REVIEW_PARTIAL_CAPABILITY"
    else:
        next_action = "NONE"

    return {
        "harness_version": "1.0",
        "pipeline_status": pipeline_status,
        "next_action": next_action,
        "counts": {
            "total_scenarios": int(bundle["summary"]["total_scenarios"]),
            "failed_scenarios": failed_count,
            "blocked_expected_scenarios": len(blocked_expected_scenarios),
            "ambiguous_scenarios": ambiguous_count,
            "certified_capabilities": len(certified_capabilities),
            "partial_capabilities": partial_count,
        },
        "certified_capabilities": certified_capabilities,
        "partial_capabilities": partial_capabilities,
        "failed_scenarios": failed_scenarios,
        "blocked_expected_scenarios": blocked_expected_scenarios,
        "ambiguous_scenarios": ambiguous_scenarios,
    }


__all__ = [
    "HarnessInputError",
    "build_operational_status",
    "load_radiography_bundle",
]

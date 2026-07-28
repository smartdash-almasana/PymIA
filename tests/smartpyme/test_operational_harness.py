from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

import pytest

from pymia.operational_harness.harness import (
    HarnessInputError,
    build_operational_status,
    load_radiography_bundle,
)


def _registry(
    *,
    partial: bool = False,
    include_supplier: bool = False,
    include_orphan_target: bool = False,
) -> dict:
    capabilities = [
        {
            "capability_id": "excel_diagnostic",
            "label": "Diagnostico Excel",
            "status": "PIPELINE_CERTIFIED",
            "pipeline_certified": True,
            "dispatcher_available": True,
            "cli_available": True,
            "plugin_module": "module.excel",
            "plugin_function": "fn_excel",
            "dispatcher_classification": "excel_diagnostic",
            "tests": [],
            "docs": [],
        },
    ]
    if include_supplier:
        capabilities.append(
            {
                "capability_id": "supplier_duplicate_check",
                "label": "Revision proveedores",
                "status": "PIPELINE_CERTIFIED",
                "pipeline_certified": True,
                "dispatcher_available": True,
                "cli_available": True,
                "plugin_module": "module.suppliers",
                "plugin_function": "fn_suppliers",
                "dispatcher_classification": "supplier_duplicate_check",
                "tests": [],
                "docs": [],
            }
        )
    if partial:
        capabilities.append(
            {
                "capability_id": "partial_capability",
                "label": "Parcial",
                "status": "PARTIALLY_AVAILABLE_BY_PATH",
                "pipeline_certified": False,
                "dispatcher_available": False,
                "cli_available": True,
                "plugin_module": "module.partial",
                "plugin_function": "fn_partial",
                "dispatcher_classification": "partial_capability",
                "tests": [],
                "docs": [],
            }
        )
    if include_orphan_target:
        capabilities.append(
            {
                "capability_id": "other_capability",
                "label": "Otra",
                "status": "PIPELINE_CERTIFIED",
                "pipeline_certified": True,
                "dispatcher_available": True,
                "cli_available": True,
                "plugin_module": "module.other",
                "plugin_function": "fn_other",
                "dispatcher_classification": "other_capability",
                "tests": [],
                "docs": [],
            }
        )
    return {"version": "1.0", "capabilities": capabilities}


def _trace_payload(
    *,
    trace_id: str,
    scenario_id: str,
    overall_status: str,
    runtime_classification: str | None,
    blocked_at: str | None = None,
) -> dict:
    return {
        "trace_id": trace_id,
        "scenario_id": scenario_id,
        "trace": {
            "stages": [],
            "overall_status": overall_status,
            "blocked_at": blocked_at,
            "final_summary": {
                "final_status": "READY_TO_DELIVER" if overall_status == "PASS" else "BLOCKED",
                "runtime_classification": runtime_classification,
                "dispatch_status": "EXECUTED" if overall_status == "PASS" else None,
                "findings_count": 1 if overall_status == "PASS" else 0,
                "must_not_dispatch": overall_status != "PASS",
            },
            "duration_ms": 12,
        },
    }


def _write_bundle(
    base_dir: Path,
    *,
    scenarios: list[dict],
    traces: dict[str, dict],
) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "total_scenarios": len(scenarios),
        "passed": sum(1 for row in scenarios if row["overall_status"] == "PASS"),
        "blocked_expected": sum(1 for row in scenarios if row["overall_status"] == "BLOCKED_EXPECTED"),
        "failed": sum(1 for row in scenarios if row["overall_status"] == "FAIL"),
        "ambiguous": sum(1 for row in scenarios if row["overall_status"] == "AMBIGUOUS"),
        "scenarios": scenarios,
    }
    (base_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    for scenario_id, trace_payload in traces.items():
        scenario_dir = base_dir / scenario_id
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "trace.json").write_text(
            json.dumps(trace_payload, indent=2),
            encoding="utf-8",
        )


def test_reads_registry_via_capability_registry(monkeypatch, tmp_path: Path) -> None:
    calls = {"count": 0}

    def _fake_registry() -> dict:
        calls["count"] += 1
        return _registry()

    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", _fake_registry)
    scenarios = [
        {
            "scenario_id": "happy",
            "trace_id": "trace_happy",
            "overall_status": "PASS",
            "blocked_at": None,
            "duration_ms": 1,
        }
    ]
    traces = {
        "happy": _trace_payload(
            trace_id="trace_happy",
            scenario_id="happy",
            overall_status="PASS",
            runtime_classification="excel_diagnostic",
        )
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    build_operational_status(tmp_path)

    assert calls["count"] == 1


def test_loads_summary_and_traces_successfully(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry())
    scenarios = [
        {
            "scenario_id": "happy",
            "trace_id": "trace_happy",
            "overall_status": "PASS",
            "blocked_at": None,
            "duration_ms": 1,
        }
    ]
    traces = {
        "happy": _trace_payload(
            trace_id="trace_happy",
            scenario_id="happy",
            overall_status="PASS",
            runtime_classification="excel_diagnostic",
        )
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    bundle = load_radiography_bundle(tmp_path)

    assert bundle["summary"]["total_scenarios"] == 1
    assert bundle["traces"][0]["scenario_id"] == "happy"


def test_green_when_no_fail_and_no_ambiguous(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry(include_supplier=True))
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
        {"scenario_id": "s2", "trace_id": "t2", "overall_status": "PASS", "blocked_at": None, "duration_ms": 2},
        {"scenario_id": "s3", "trace_id": "t3", "overall_status": "BLOCKED_EXPECTED", "blocked_at": "evidence_gate", "duration_ms": 3},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
        "s2": _trace_payload(trace_id="t2", scenario_id="s2", overall_status="PASS", runtime_classification="supplier_duplicate_check"),
        "s3": _trace_payload(trace_id="t3", scenario_id="s3", overall_status="BLOCKED_EXPECTED", runtime_classification=None, blocked_at="evidence_gate"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "GREEN"
    assert result["next_action"] == "NONE"
    assert result["stale_certified_capabilities"] == []


def test_yellow_when_ambiguous_exists(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry())
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "AMBIGUOUS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="AMBIGUOUS", runtime_classification=None),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "YELLOW"
    assert result["next_action"] == "RE_RUN_RADIOGRAPHY"


def test_yellow_when_partial_capability_exists(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry(partial=True))
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "YELLOW"
    assert result["next_action"] == "REVIEW_PARTIAL_CAPABILITY"
    assert result["counts"]["partial_capabilities"] == 1


def test_red_when_failed_scenario_exists(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry())
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "FAIL", "blocked_at": "delivery_package", "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="FAIL", runtime_classification="excel_diagnostic", blocked_at="delivery_package"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "RED"
    assert result["next_action"] == "FIX_SCENARIO"


def test_detects_orphan_classification(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry())
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="unknown_classification"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "YELLOW"
    assert result["next_action"] == "REVIEW_REGISTRY"
    assert result["ambiguous_scenarios"][0]["reason"] == "orphan_classification"


def test_fails_loud_when_summary_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry())
    with pytest.raises(HarnessInputError):
        build_operational_status(tmp_path)


def test_fails_loud_when_trace_missing_for_summary_entry(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("pymia.operational_harness.harness.load_registry", lambda: _registry())
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    _write_bundle(tmp_path, scenarios=scenarios, traces={})

    with pytest.raises(HarnessInputError):
        build_operational_status(tmp_path)


def test_deterministic_output(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "pymia.operational_harness.harness.load_registry",
        lambda: _registry(partial=True, include_supplier=True),
    )
    scenarios = [
        {"scenario_id": "s3", "trace_id": "t3", "overall_status": "BLOCKED_EXPECTED", "blocked_at": "evidence_gate", "duration_ms": 3},
        {"scenario_id": "s2", "trace_id": "t2", "overall_status": "PASS", "blocked_at": None, "duration_ms": 2},
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
        "s2": _trace_payload(trace_id="t2", scenario_id="s2", overall_status="PASS", runtime_classification="supplier_duplicate_check"),
        "s3": _trace_payload(trace_id="t3", scenario_id="s3", overall_status="BLOCKED_EXPECTED", runtime_classification=None, blocked_at="evidence_gate"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    first = build_operational_status(tmp_path)
    second = build_operational_status(tmp_path)

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_detects_stale_certified_capability(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "pymia.operational_harness.harness.load_registry",
        lambda: _registry(include_supplier=True),
    )
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "YELLOW"
    assert result["next_action"] == "REVIEW_REGISTRY"
    assert result["stale_certified_capabilities"] == [
        {
            "capability_id": "supplier_duplicate_check",
            "label": "Revision proveedores",
        }
    ]


def test_no_stale_certified_capability_when_traces_exist(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "pymia.operational_harness.harness.load_registry",
        lambda: _registry(include_supplier=True),
    )
    scenarios = [
        {"scenario_id": "s2", "trace_id": "t2", "overall_status": "PASS", "blocked_at": None, "duration_ms": 2},
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
        "s2": _trace_payload(trace_id="t2", scenario_id="s2", overall_status="PASS", runtime_classification="supplier_duplicate_check"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["stale_certified_capabilities"] == []


def test_stale_takes_precedence_over_partial(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "pymia.operational_harness.harness.load_registry",
        lambda: _registry(partial=True, include_supplier=True),
    )
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["next_action"] == "REVIEW_REGISTRY"


def test_fails_take_precedence_over_stale(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "pymia.operational_harness.harness.load_registry",
        lambda: _registry(include_supplier=True),
    )
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "FAIL", "blocked_at": "delivery_package", "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="FAIL", runtime_classification="excel_diagnostic", blocked_at="delivery_package"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "RED"
    assert result["next_action"] == "FIX_SCENARIO"


def test_ambiguous_take_precedence_over_stale(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "pymia.operational_harness.harness.load_registry",
        lambda: _registry(include_supplier=True),
    )
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "AMBIGUOUS", "blocked_at": None, "duration_ms": 1},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="AMBIGUOUS", runtime_classification="excel_diagnostic"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = build_operational_status(tmp_path)

    assert result["pipeline_status"] == "YELLOW"
    assert result["next_action"] == "RE_RUN_RADIOGRAPHY"


def test_harness_main_writes_status_json(tmp_path: Path) -> None:
    scenarios = [
        {"scenario_id": "s1", "trace_id": "t1", "overall_status": "PASS", "blocked_at": None, "duration_ms": 1},
        {"scenario_id": "s2", "trace_id": "t2", "overall_status": "PASS", "blocked_at": None, "duration_ms": 2},
    ]
    traces = {
        "s1": _trace_payload(trace_id="t1", scenario_id="s1", overall_status="PASS", runtime_classification="excel_diagnostic"),
        "s2": _trace_payload(trace_id="t2", scenario_id="s2", overall_status="PASS", runtime_classification="supplier_duplicate_check"),
    }
    _write_bundle(tmp_path, scenarios=scenarios, traces=traces)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pymia.operational_harness",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=Path.cwd(),
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    status_path = tmp_path / "harness_status.json"
    assert status_path.exists()
    data = json.loads(status_path.read_text(encoding="utf-8"))
    assert data["harness_version"] == "1.0"
    assert "pipeline_status" in data
    assert "next_action" in data
    assert "counts" in data
    assert "certified_capabilities" in data
    assert "partial_capabilities" in data
    assert "failed_scenarios" in data
    assert "blocked_expected_scenarios" in data
    assert "ambiguous_scenarios" in data
    assert "stale_certified_capabilities" in data


def test_forbidden_imports_not_present() -> None:
    forbidden_roots = {
        "requ" "ests",
        "htt" "px",
        "lang" "chain",
    }
    forbidden_prefixes = (
        "open" "ai",
        "tele" "gram",
        "microservice" "_dispatcher",
    )
    for source_path in Path("pymia/operational_harness").glob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in forbidden_roots
                    assert not alias.name.startswith(forbidden_prefixes)
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                root = module.split(".")[0] if module else ""
                assert root not in forbidden_roots
                assert not module.startswith(forbidden_prefixes)

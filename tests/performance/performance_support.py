"""Support for collecting report-only pytest-benchmark measurements."""

from __future__ import annotations

import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path
from collections.abc import Mapping
from typing import Any

REPORT_PATH = Path(r"E:\BuenosPasos\smartbridge\PYMIA_PERFORMANCE_BASELINE_V1.json")
BENCHMARKS: list[dict[str, Any]] = []


def record_benchmark(
    *,
    name: str,
    target: str,
    boundary: str,
    fixture_input: str,
    stats: Any,
) -> None:
    """Record only metrics provided by pytest-benchmark."""
    fields = ("min", "max", "mean", "stddev", "median", "rounds", "iterations", "ops")
    if isinstance(stats, Mapping):
        measured = {field: stats[field] for field in fields if field in stats}
    elif hasattr(stats, "get"):
        measured = {
            field: stats.get(field)
            for field in fields
            if stats.get(field) is not None
        }
    else:
        measured = {
            field: getattr(stats, field)
            for field in fields
            if hasattr(stats, field)
        }
    BENCHMARKS.append(
        {
            "name": name,
            "target": target,
            "boundary": boundary,
            "fixture_input": fixture_input,
            "stats": measured,
        }
    )


def write_report() -> None:
    REPORT_PATH.write_text(
        json.dumps(
            {
                "schema_version": "PYMIA_PERFORMANCE_BASELINE_V1",
                "pytest_benchmark_version": version("pytest-benchmark"),
                "environment_summary": {
                    "python": sys.version.split()[0],
                    "platform": platform.platform(),
                    "system": platform.system(),
                },
                "benchmarks": BENCHMARKS,
                "stats_unit": "seconds",
                "mode": "REPORT_ONLY",
                "thresholds_enabled": False,
                "product_code_changed": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

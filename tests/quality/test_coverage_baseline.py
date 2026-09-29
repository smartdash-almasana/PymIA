from __future__ import annotations

import sys
from pathlib import Path

from scripts.quality.coverage_baseline import SCHEMA_VERSION, build_command


def test_coverage_baseline_is_report_only_command(tmp_path: Path) -> None:
    report = tmp_path / "coverage.json"
    command = build_command(report_path=report)
    assert command[0:3] == [sys.executable, "-m", "pytest"]
    assert "--cov=pymia" in command
    assert "--cov-branch" in command
    assert f"--cov-report=json:{report}" in command
    assert not any(arg.startswith("--cov-fail-under") for arg in command)


def test_coverage_schema_version_is_stable() -> None:
    assert SCHEMA_VERSION == "PYMIA_COVERAGE_BASELINE_V1"


def test_pytest_cov_quality_requirement_is_pinned() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    manifest = (repo_root / "requirements-quality.txt").read_text(encoding="utf-8")
    lines = [
        line.strip()
        for line in manifest.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert "pytest-cov==7.1.0" in lines

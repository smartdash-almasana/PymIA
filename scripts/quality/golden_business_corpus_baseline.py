from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Sequence

import pytest


SCHEMA_VERSION = "PYMIA_GOLDEN_BUSINESS_CORPUS_BASELINE_V1"

COMPONENTS = (
    ("C2_MULTI_BUSINESS", 7, "tests/smartpyme/test_service_1_c2_golden_business_corpus_v1.py"),
    ("LA_TEXTIL_REPLAY", 1, "tests/test_golden_replay.py"),
    ("PHYSICAL_XLSX_READINESS", 7, "tests/smartpyme/test_service_1_physical_xlsx_product_readiness_corpus_v1.py"),
)


class _OutcomePlugin:
    def __init__(self) -> None:
        self.outcomes: dict[str, str] = {}

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when == "call":
            self.outcomes[report.nodeid] = report.outcome
        elif report.when == "setup" and report.failed:
            self.outcomes[report.nodeid] = "error"


def _component_status(test_ids: list[str], outcomes: dict[str, str]) -> str:
    if not test_ids:
        return "BLOCKED_ENVIRONMENT"
    statuses = {outcomes.get(test_id, "error") for test_id in test_ids}
    if statuses == {"passed"}:
        return "PASS"
    if "skipped" in statuses:
        return "BLOCKED_ENVIRONMENT"
    return "DRIFT"


def run_baseline(*, repo_root: Path, report_path: Path) -> dict[str, object]:
    os.environ.setdefault("PYTHONPATH", str(repo_root))
    os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    plugin = _OutcomePlugin()
    exit_code = int(pytest.main(["-q", "-m", "golden"], plugins=[plugin]))

    suite_components: list[dict[str, object]] = []
    cases_pass = cases_fail = cases_blocked = 0
    for name, case_count, path_prefix in COMPONENTS:
        test_ids = sorted(test_id for test_id in plugin.outcomes if test_id.startswith(path_prefix))
        status = _component_status(test_ids, plugin.outcomes)
        if status == "PASS":
            cases_pass += case_count
        elif status == "DRIFT":
            cases_fail += case_count
        else:
            cases_blocked += case_count
        suite_components.append(
            {
                "name": name,
                "status": status,
                "cases": case_count,
                "test_identifiers": test_ids,
            }
        )

    report = {
        "schema_version": SCHEMA_VERSION,
        "mode": "BASELINE",
        "cases_total": sum(component[1] for component in COMPONENTS),
        "cases_pass": cases_pass,
        "cases_fail": cases_fail,
        "cases_blocked": cases_blocked,
        "suite_components": suite_components,
        "test_identifiers": sorted(plugin.outcomes),
        "execution_command": "python -m pytest -q -m golden",
        "pytest_returncode": exit_code,
        "oracle_update": False,
        "report_path": str(report_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    repo_root = Path(__file__).resolve().parents[2]
    report_path = repo_root.parent / "PYMIA_GOLDEN_BUSINESS_CORPUS_BASELINE_V1.json"
    report = run_baseline(repo_root=repo_root, report_path=report_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["cases_fail"] == 0 and report["cases_blocked"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

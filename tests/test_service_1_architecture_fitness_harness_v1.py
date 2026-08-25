from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from pymia.architecture_guard import run_architecture_guard


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_architecture_fitness_harness_passes_current_service_1_invariants() -> None:
    report = run_architecture_guard(_repo_root())

    assert report["verdict"] == "PASS"
    gates = {gate["gate_id"]: gate for gate in report["gates"]}
    expected = {
        "ONE_CANONICAL_PRODUCT_ROOT",
        "FOUR_EXPLICIT_EXECUTION_COMMANDS",
        "ONE_CANONICAL_XLSX_READER",
        "ONE_SEMANTIC_FSM",
        "NO_PRODUCTIVE_LEGACY_CALLERS",
        "NO_PRODUCTIVE_SHEET1_FALLBACK",
        "NO_WEB_ANALYSIS_BYPASSES",
        "D4_TO_P8_PROVENANCE",
        "F7_ONLY_JOIN_MATERIALIZATION",
        "ONE_MATH_ENGINE",
        "DECLARATIVE_CLASSIFICATION",
        "NO_LLM_MATH_RUNTIME_AUTHORITY",
        "NO_POST_BUILD_ENVELOPE_MUTATION",
        "RESULT_READ_NO_RECALCULATION",
        "D7_EVIDENCE_ONLY",
        "REGISTRY_DRIFT_ZERO",
    }
    assert set(gates) == expected
    assert all(gate["passed"] for gate in gates.values())


def test_architecture_fitness_harness_cli_emits_machine_readable_pass() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "pymia.architecture_guard", "--json"],
        cwd=_repo_root(),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema_version"] == "SERVICE_1_ARCHITECTURE_FITNESS_HARNESS_V1"
    assert report["verdict"] == "PASS"
    assert all(gate["passed"] for gate in report["gates"])

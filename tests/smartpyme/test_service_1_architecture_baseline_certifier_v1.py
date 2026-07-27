from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_architecture_baseline_certifier_emits_machine_readable_report() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "tools" / "service_1_architecture_baseline_v1.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--report-only", "--skip-behavior", "--json"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema_version"] == "SERVICE_1_ARCHITECTURE_BASELINE_CERTIFICATION_V1"
    assert report["verdict"] in {
        "PASS_ARCHITECTURE_BASELINE_V1",
        "BLOCK_ARCHITECTURE_BASELINE_V1",
    }
    checks = {item["check_id"]: item for item in report["structural_checks"]}
    assert checks["ONE_CANONICAL_PRODUCT_ROOT"]["passed"] is True
    assert checks["TEMPORARY_PACKAGE1_ADAPTER_OUTSIDE_PRODUCTIVE_PATH"]["passed"] is True
    assert "NO_SEMANTIC_REBIND_AFTER_P6" in checks
    assert "P7_P8_BOUNDARIES_NOT_FUSED" in checks
    assert checks["OWNER_CONFIRMATION_NOT_OWNED_BY_CONTROLLED_EXECUTION_GATE"]["passed"] is True
    assert "P6_GATE_DOES_NOT_OWN_P7_FAMILY_MATCHING" in checks
    assert checks["CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION"]["passed"] is True

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

from scripts.quality.fast_quality_gate import run_gate


def _version(command: str) -> str | None:
    path = shutil.which(command)
    if path is None:
        return None
    completed = subprocess.run([command, "--version"], capture_output=True, text=True, check=False)
    text = (completed.stdout or completed.stderr).strip()
    return text or None


def test_emit_real_fast_quality_report() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = run_gate(repo_root=repo_root)
    environment = {
        "ruff_executable": shutil.which("ruff"),
        "ruff_version": _version("ruff"),
        "pyright_executable": shutil.which("pyright"),
        "pyright_module_available": importlib.util.find_spec("pyright") is not None,
        "semgrep_executable": shutil.which("semgrep"),
        "semgrep_version": _version("semgrep"),
        "bandit_executable": shutil.which("bandit"),
        "bandit_version": _version("bandit"),
        "pip_audit_executable": shutil.which("pip-audit"),
        "pip_audit_version": _version("pip-audit"),
        "gitleaks_executable": shutil.which("gitleaks"),
        "gitleaks_version": _version("gitleaks"),
    }
    report["environment"] = environment
    out = repo_root.parent / "PYMIA_FAST_QUALITY_REPORT_V1.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gitleaks = next(item for item in report["results"] if item["tool"] == "gitleaks")
    gitleaks_report = json.loads(gitleaks["stdout"] or "[]")
    rule_ids = sorted({item.get("RuleID") for item in gitleaks_report if item.get("RuleID")})
    files = sorted({item.get("File") for item in gitleaks_report if item.get("File")})
    repo_scope_out = repo_root.parent / "PYMIA_GITLEAKS_REPO_SCOPE_BASELINE_V1.json"
    repo_scope_out.write_text(
        json.dumps(
            {
                "schema_version": "PYMIA_GITLEAKS_REPO_SCOPE_BASELINE_V1",
                "scope": "git-owned-unignored-worktree",
                "method": "git ls-files -co --exclude-standard staged outside repository",
                "total": len(gitleaks_report),
                "rule_ids": rule_ids,
                "files": files,
                "classification": "CLEAN_REPO_SCOPE" if not gitleaks_report else "REPO_SECRET_FINDING",
                "findings": gitleaks_report,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    summary = {
        "tools": {
            item["tool"]: {
                "status": item["status"],
                "returncode": item["returncode"],
            }
            for item in report["results"]
        },
        "environment": environment,
    }
    print(json.dumps(summary, ensure_ascii=False))
    assert report["mode"] == "REPORT_ONLY"
    assert report["autofix"] is False
    assert report["blocking"] is False

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.quality import fast_quality_gate as gate


def test_missing_tool_is_reported_not_available(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)
    result = gate.run_tool(
        gate.ToolSpec("ruff", ("ruff", "check", "."), "ruff", ("ruff", "--version")),
        cwd=tmp_path,
    )
    assert result["status"] == "NOT_AVAILABLE"
    assert result["version"] is None
    assert result["returncode"] is None


def test_return_code_one_is_findings_not_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "C:/tool.exe")
    responses = iter(
        [
            SimpleNamespace(returncode=1, stdout="finding", stderr=""),
            SimpleNamespace(returncode=0, stdout="pyright 1.2.3", stderr=""),
        ]
    )
    monkeypatch.setattr(gate.subprocess, "run", lambda *args, **kwargs: next(responses))
    result = gate.run_tool(
        gate.ToolSpec("pyright", ("pyright",), "pyright", ("pyright", "--version")),
        cwd=tmp_path,
    )
    assert result["status"] == "FINDINGS"
    assert result["version"] == "pyright 1.2.3"
    assert result["returncode"] == 1


def test_nonstandard_return_code_is_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "C:/tool.exe")
    responses = iter(
        [
            SimpleNamespace(returncode=2, stdout="", stderr="boom"),
            SimpleNamespace(returncode=0, stdout="ruff 0.0.0", stderr=""),
        ]
    )
    monkeypatch.setattr(gate.subprocess, "run", lambda *args, **kwargs: next(responses))
    result = gate.run_tool(
        gate.ToolSpec("ruff", ("ruff",), "ruff", ("ruff", "--version")),
        cwd=tmp_path,
    )
    assert result["status"] == "ERROR"


def test_gate_is_explicitly_report_only(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gate, "run_tool", lambda spec, cwd: {"tool": spec.name, "status": "PASS"})
    report = gate.run_gate(repo_root=tmp_path, tools=["architecture"])
    assert report["mode"] == "REPORT_ONLY"
    assert report["autofix"] is False
    assert report["blocking"] is False
    assert report["results"] == [{"tool": "architecture", "status": "PASS"}]


def test_unknown_tool_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown tools"):
        gate.run_gate(repo_root=tmp_path, tools=["unknown"])


def test_default_specs_include_all_quality_tools_and_architecture() -> None:
    assert [spec.name for spec in gate.TOOL_SPECS] == [
        "ruff",
        "pyright",
        "semgrep",
        "bandit",
        "pip-audit",
        "gitleaks",
        "architecture",
    ]
    semgrep = gate.TOOL_SPECS[2]
    assert "docs/quality/semgrep-baseline.yml" in semgrep.command
    assert "--error" in semgrep.command
    bandit = gate.TOOL_SPECS[3]
    assert bandit.command == ("bandit", "-r", "pymia", "-f", "json")
    assert bandit.version_command == ("bandit", "--version")
    pip_audit = gate.TOOL_SPECS[4]
    assert pip_audit.command == ("pip-audit", ".", "--format", "json", "--progress-spinner", "off")
    assert pip_audit.version_command == ("pip-audit", "--version")
    gitleaks = gate.TOOL_SPECS[5]
    assert gitleaks.command[0:3] == ("gitleaks", "dir", "<git-owned-staging>")
    assert "--redact" in gitleaks.command
    assert gitleaks.version_command == ("gitleaks", "version")
    architecture = gate.TOOL_SPECS[6]
    assert "tests/architecture" in architecture.command
    assert architecture.version_command is not None


def test_pyright_quality_requirement_is_pinned() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    manifest = (repo_root / "requirements-quality.txt").read_text(encoding="utf-8")
    lines = [
        line.strip()
        for line in manifest.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert lines == [
        "pyright==1.1.414",
        "semgrep==1.178.0",
        "bandit==1.9.4",
        "pip-audit==2.10.1",
        "pytest-cov==7.1.0",
        "import-linter==2.15",
        "hypothesis==6.168.3",
        "mutmut==3.8.0",
        "vulture==2.16",
        "pytest-benchmark==5.3.0",
    ]


def test_semgrep_baseline_is_local_and_report_only() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    config = (repo_root / "docs" / "quality" / "semgrep-baseline.yml").read_text(encoding="utf-8")
    assert "hashlib.sha1" in config
    assert "severity: WARNING" in config


def test_gitleaks_file_selection_excludes_ignored_workspace_content(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    response = SimpleNamespace(returncode=0, stdout=b"tracked.py\0quality.txt\0", stderr=b"")
    calls: list[tuple[str, ...]] = []

    def fake_run(command: tuple[str, ...], **_kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return response

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    owned = gate._git_owned_paths(cwd=tmp_path)
    assert owned == [Path("tracked.py"), Path("quality.txt")]
    assert calls == [("git", "ls-files", "-co", "--exclude-standard", "-z")]
    assert ".env.local" not in {str(path) for path in owned}
    assert ".venv" not in {str(path) for path in owned}


def test_gitleaks_evidence_redacts_secret_fields(tmp_path: Path) -> None:
    report = tmp_path / "gitleaks.json"
    report.write_text(
        '[{"RuleID":"generic-api-key","Match":"do-not-print","Secret":"do-not-print","File":"x.py"}]',
        encoding="utf-8",
    )
    safe = gate._safe_gitleaks_report(report)
    assert "do-not-print" not in safe
    assert "REDACTED" in safe

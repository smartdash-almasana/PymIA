from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

SCHEMA_VERSION = "PYMIA_FAST_QUALITY_GATE_V1"


@dataclass(frozen=True)
class ToolSpec:
    name: str
    command: tuple[str, ...]
    executable: str | None = None
    version_command: tuple[str, ...] | None = None


TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        "ruff",
        ("ruff", "check", "."),
        executable="ruff",
        version_command=("ruff", "--version"),
    ),
    ToolSpec(
        "pyright",
        ("pyright",),
        executable="pyright",
        version_command=("pyright", "--version"),
    ),
    ToolSpec(
        "semgrep",
        (
            "semgrep",
            "scan",
            "--config",
            "docs/quality/semgrep-baseline.yml",
            "--json",
            "--error",
            "pymia",
        ),
        executable="semgrep",
        version_command=("semgrep", "--version"),
    ),
    ToolSpec(
        "bandit",
        ("bandit", "-r", "pymia", "-f", "json"),
        executable="bandit",
        version_command=("bandit", "--version"),
    ),
    ToolSpec(
        "pip-audit",
        ("pip-audit", ".", "--format", "json", "--progress-spinner", "off"),
        executable="pip-audit",
        version_command=("pip-audit", "--version"),
    ),
    ToolSpec(
        "gitleaks",
        (
            "gitleaks",
            "dir",
            "<git-owned-staging>",
            "--report-format",
            "json",
            "--report-path",
            "<temporary-report>",
            "--redact",
            "--no-banner",
            "--no-color",
            "--log-level",
            "error",
            "--exit-code",
            "1",
        ),
        executable="gitleaks",
        version_command=("gitleaks", "version"),
    ),
    ToolSpec(
        "architecture",
        (sys.executable, "-m", "pytest", "-q", "tests/architecture"),
        executable=None,
        version_command=(sys.executable, "-m", "pytest", "--version"),
    ),
)


def _available(spec: ToolSpec) -> bool:
    if spec.executable is None:
        return True
    return shutil.which(spec.executable) is not None


def _version(spec: ToolSpec, *, cwd: Path) -> str | None:
    if spec.version_command is None or not _available(spec):
        return None
    completed = subprocess.run(
        spec.version_command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    text = (completed.stdout or completed.stderr).strip()
    return text or None


def _git_owned_paths(*, cwd: Path) -> list[Path]:
    """Return tracked and unignored untracked paths, excluding local-only files."""
    completed = subprocess.run(
        ("git", "ls-files", "-co", "--exclude-standard", "-z"),
        cwd=cwd,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "git ls-files failed")
    return [
        Path(raw.decode("utf-8"))
        for raw in completed.stdout.split(b"\0")
        if raw
    ]


def _safe_gitleaks_report(report_path: Path) -> str:
    """Keep only metadata; never expose Match or Secret values in evidence."""
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = []
    safe = []
    for finding in payload if isinstance(payload, list) else []:
        if not isinstance(finding, dict):
            continue
        safe.append(
            {
                key: ("REDACTED" if key in {"Match", "Secret"} else value)
                for key, value in finding.items()
                if key
                in {
                    "RuleID",
                    "Description",
                    "StartLine",
                    "EndLine",
                    "StartColumn",
                    "EndColumn",
                    "File",
                    "SymlinkFile",
                    "Commit",
                    "Author",
                    "Email",
                    "Date",
                    "Fingerprint",
                    "Tags",
                    "Match",
                    "Secret",
                }
            }
        )
    return json.dumps(safe, ensure_ascii=False, indent=2)


def _run_gitleaks_repo_scope(spec: ToolSpec, *, cwd: Path) -> dict[str, object]:
    """Scan only Git-owned/versionable content using an external staging tree."""
    try:
        owned_paths = _git_owned_paths(cwd=cwd)
    except (OSError, RuntimeError) as exc:
        return {
            "tool": spec.name,
            "status": "ERROR",
            "version": _version(spec, cwd=cwd),
            "returncode": None,
            "command": list(spec.command),
            "stdout": "",
            "stderr": str(exc),
        }

    with tempfile.TemporaryDirectory(prefix="pymia-gitleaks-repo-scope-") as temporary:
        staging = Path(temporary) / "repo"
        report_path = Path(temporary) / "gitleaks-report.json"
        for relative_path in owned_paths:
            source = cwd / relative_path
            if source.is_symlink() or not source.is_file():
                continue
            destination = staging / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        command = [
            "gitleaks",
            "dir",
            str(staging),
            "--report-format",
            "json",
            "--report-path",
            str(report_path),
            "--redact",
            "--no-banner",
            "--no-color",
            "--log-level",
            "error",
            "--exit-code",
            "1",
        ]
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            status = "PASS"
        elif completed.returncode == 1:
            status = "FINDINGS"
        else:
            status = "ERROR"
        return {
            "tool": spec.name,
            "status": status,
            "version": _version(spec, cwd=cwd),
            "returncode": completed.returncode,
            "command": command,
            "stdout": _safe_gitleaks_report(report_path),
            "stderr": completed.stderr,
        }


def run_tool(spec: ToolSpec, *, cwd: Path) -> dict[str, object]:
    if not _available(spec):
        return {
            "tool": spec.name,
            "status": "NOT_AVAILABLE",
            "version": None,
            "returncode": None,
            "command": list(spec.command),
            "stdout": "",
            "stderr": "",
        }

    if spec.name == "gitleaks":
        return _run_gitleaks_repo_scope(spec, cwd=cwd)

    completed = subprocess.run(
        spec.command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        status = "PASS"
    elif completed.returncode == 1:
        status = "FINDINGS"
    else:
        status = "ERROR"

    return {
        "tool": spec.name,
        "status": status,
        "version": _version(spec, cwd=cwd),
        "returncode": completed.returncode,
        "command": list(spec.command),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_gate(*, repo_root: Path, tools: Sequence[str] | None = None) -> dict[str, object]:
    selected = set(tools or [spec.name for spec in TOOL_SPECS])
    unknown = sorted(selected.difference(spec.name for spec in TOOL_SPECS))
    if unknown:
        raise ValueError(f"unknown tools: {', '.join(unknown)}")

    results = [
        run_tool(spec, cwd=repo_root)
        for spec in TOOL_SPECS
        if spec.name in selected
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "REPORT_ONLY",
        "autofix": False,
        "blocking": False,
        "results": results,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PymIA Fast Quality Gate — report-only.")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root.",
    )
    parser.add_argument(
        "--tool",
        action="append",
        choices=[spec.name for spec in TOOL_SPECS],
        help="Run only the selected tool. Repeat for multiple tools.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output path. If omitted, JSON is printed to stdout.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = run_gate(repo_root=Path(args.repo_root).resolve(), tools=args.tool)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

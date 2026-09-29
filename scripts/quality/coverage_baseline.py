from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

SCHEMA_VERSION = "PYMIA_COVERAGE_BASELINE_V1"


def build_command(*, report_path: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--cov=pymia",
        "--cov-branch",
        f"--cov-report=json:{report_path}",
        "--cov-report=term",
    ]


def run_coverage(*, repo_root: Path, report_path: Path) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    command = build_command(report_path=report_path)
    completed = subprocess.run(
        command,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "REPORT_ONLY",
        "blocking": False,
        "fail_under": None,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "coverage_report_path": str(report_path),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PymIA coverage baseline — report-only.")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
    )
    parser.add_argument(
        "--output",
        default="",
        help="Coverage JSON path. Defaults to repo parent / PYMIA_COVERAGE_BASELINE_V1.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    report_path = Path(args.output).resolve() if args.output else repo_root.parent / "PYMIA_COVERAGE_BASELINE_V1.json"
    result = run_coverage(repo_root=repo_root, report_path=report_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

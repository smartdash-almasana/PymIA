#!/usr/bin/env python3
"""Sandbox-only smoke test.

This script is authorized ONLY by the Runtime Gate document:
    docs/hermes/HERMES_LOCAL_RUNTIME_GATE.md

Scope:
    - Validates existence of sandbox artifacts.
    - Writes a minimal JSON evidence file inside the sandbox.
    - Does NOT import Hermes, does NOT read .env, does NOT use secrets,
      does NOT touch network, does NOT touch production.

Usage:
    python scripts/sandbox_smoke_test.py --sandbox-path <path>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "sandbox/HERMES_HOME/README.md",
    "sandbox/config/sandbox_config.yaml",
    "sandbox/config/allowlist.yaml",
    "sandbox/config/denylist.yaml",
    "sandbox/scripts/rollback.md",
    "sandbox/logs/README.md",
)

FORBIDDEN_PATH_MARKERS: tuple[str, ...] = (
    "hermes-agent",
    "PymIA",
)

ALLOWED_SANDBOX_ROOT_SUFFIX: str = ".tmp/hermes-scn-local"
ALLOWED_SANDBOX_ROOT_SUFFIX_ALT: str = ".tmp\\hermes-scn-local"


def _resolve(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path


def _is_within_sandbox_scope(sandbox: Path) -> bool:
    """Sandbox must be located under .tmp/hermes-scn-local."""
    raw = str(_resolve(sandbox))
    normalized = raw.replace("\\", "/")
    return ALLOWED_SANDBOX_ROOT_SUFFIX in normalized or ALLOWED_SANDBOX_ROOT_SUFFIX_ALT in raw


def _contains_forbidden_marker(sandbox: Path) -> str | None:
    raw = str(_resolve(sandbox))
    normalized = raw.replace("\\", "/")
    for marker in FORBIDDEN_PATH_MARKERS:
        # marker "PymIA" only forbidden if it is a directory component,
        # not substring of another word (avoid false positives).
        if marker == "PymIA":
            parts = normalized.split("/")
            if marker in parts:
                return marker
        elif marker in normalized:
            return marker
    return None


def validate_sandbox_path(sandbox: Path) -> tuple[bool, str]:
    """Validate sandbox path is safe and within scope."""
    if not sandbox.exists():
        return False, f"sandbox path does not exist: {sandbox}"
    if not sandbox.is_dir():
        return False, f"sandbox path is not a directory: {sandbox}"

    if not _is_within_sandbox_scope(sandbox):
        return False, (
            f"sandbox path must be located under {ALLOWED_SANDBOX_ROOT_SUFFIX}"
        )

    forbidden = _contains_forbidden_marker(sandbox)
    if forbidden is not None:
        return False, f"sandbox path contains forbidden marker: {forbidden}"

    return True, "ok"


def validate_artifacts(sandbox: Path) -> tuple[list[str], list[str]]:
    """Return (passed, blocked) artifact relative paths."""
    passed: list[str] = []
    blocked: list[str] = []
    for rel in REQUIRED_ARTIFACTS:
        candidate = sandbox / rel
        if candidate.exists() and candidate.is_file():
            passed.append(rel)
        else:
            blocked.append(rel)
    return passed, blocked


def build_evidence(
    sandbox: Path,
    path_ok: bool,
    path_reason: str,
    artifacts_passed: list[str],
    artifacts_blocked: list[str],
) -> dict[str, Any]:
    """Build minimal evidence payload."""
    overall_pass = path_ok and len(artifacts_blocked) == 0
    return {
        "schema_version": "sandbox-smoke-test-v1",
        "test": "sandbox_smoke_test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sandbox_path": str(sandbox),
        "sandbox_path_ok": path_ok,
        "sandbox_path_reason": path_reason,
        "artifacts_required": list(REQUIRED_ARTIFACTS),
        "artifacts_passed": artifacts_passed,
        "artifacts_blocked": artifacts_blocked,
        "no_runtime_real": True,
        "no_secrets": True,
        "no_telegram": True,
        "no_production": True,
        "no_network": True,
        "no_subprocess": True,
        "no_env_read": True,
        "no_hermes_import": True,
        "overall": "PASS" if overall_pass else "BLOCKED",
    }


def write_evidence(sandbox: Path, evidence: dict[str, Any]) -> Path:
    """Write evidence JSON inside sandbox/logs only."""
    logs_dir = sandbox / "sandbox" / "logs"
    if not logs_dir.exists() or not logs_dir.is_dir():
        raise RuntimeError(f"sandbox logs dir not found: {logs_dir}")
    target = logs_dir / "sandbox_smoke_test_result.json"
    # Defensive: ensure resolved target is still inside sandbox.
    resolved_target = _resolve(target)
    resolved_sandbox = _resolve(sandbox)
    try:
        resolved_target.relative_to(resolved_sandbox)
    except ValueError as exc:
        raise RuntimeError(
            f"evidence target escapes sandbox: {resolved_target}"
        ) from exc

    with target.open("w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2, ensure_ascii=False)
    return target


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sandbox-only smoke test.")
    parser.add_argument(
        "--sandbox-path",
        required=True,
        help="Absolute path to the sandbox root (must be under .tmp/hermes-scn-local).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sandbox = Path(args.sandbox_path)

    path_ok, path_reason = validate_sandbox_path(sandbox)

    if not path_ok:
        evidence = build_evidence(sandbox, path_ok, path_reason, [], [])
        # Still attempt to print evidence; do NOT write outside sandbox.
        print(json.dumps(evidence, indent=2, ensure_ascii=False))
        print(f"BLOCKED: {path_reason}", file=sys.stderr)
        return 2

    artifacts_passed, artifacts_blocked = validate_artifacts(sandbox)
    evidence = build_evidence(sandbox, path_ok, path_reason, artifacts_passed, artifacts_blocked)

    try:
        written = write_evidence(sandbox, evidence)
    except OSError as exc:
        print(f"BLOCKED: could not write evidence: {exc}", file=sys.stderr)
        return 3

    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    print(f"Evidence written to: {written}")

    if evidence["overall"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    sys.exit(main())

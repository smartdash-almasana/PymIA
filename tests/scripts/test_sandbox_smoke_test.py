"""Unit tests for scripts/sandbox_smoke_test.py.

These tests use pytest tmp_path and do NOT touch real sandbox,
hermes-agent, production, secrets, network, or .env files.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "sandbox_smoke_test.py"


@pytest.fixture(scope="module")
def smoke_module():
    spec = importlib.util.spec_from_file_location("sandbox_smoke_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def valid_sandbox(tmp_path: Path) -> Path:
    """Create a fake sandbox under .tmp/hermes-scn-local with all artifacts."""
    root = tmp_path / ".tmp" / "hermes-scn-local"
    root.mkdir(parents=True)
    (root / "sandbox" / "HERMES_HOME").mkdir(parents=True)
    (root / "sandbox" / "HERMES_HOME" / "README.md").write_text("home", encoding="utf-8")
    (root / "sandbox" / "config").mkdir(parents=True)
    (root / "sandbox" / "config" / "sandbox_config.yaml").write_text("dummy", encoding="utf-8")
    (root / "sandbox" / "config" / "allowlist.yaml").write_text("dummy", encoding="utf-8")
    (root / "sandbox" / "config" / "denylist.yaml").write_text("dummy", encoding="utf-8")
    (root / "sandbox" / "scripts").mkdir(parents=True)
    (root / "sandbox" / "scripts" / "rollback.md").write_text("rollback", encoding="utf-8")
    (root / "sandbox" / "logs").mkdir(parents=True)
    (root / "sandbox" / "logs" / "README.md").write_text("logs", encoding="utf-8")
    return root


@pytest.fixture
def hermes_agent_path(tmp_path: Path) -> Path:
    p = tmp_path / "hermes-agent"
    p.mkdir()
    return p


@pytest.fixture
def pymia_path(tmp_path: Path) -> Path:
    p = tmp_path / "PymIA"
    p.mkdir()
    return p


def test_parse_args_requires_sandbox_path(smoke_module) -> None:
    with pytest.raises(SystemExit):
        smoke_module.parse_args([])
    ns = smoke_module.parse_args(["--sandbox-path", "/tmp/x"])
    assert ns.sandbox_path == "/tmp/x"


def test_validate_rejects_hermes_agent(smoke_module, hermes_agent_path: Path) -> None:
    ok, reason = smoke_module.validate_sandbox_path(hermes_agent_path)
    assert ok is False
    assert "forbidden" in reason.lower() or "hermes-agent" in reason


def test_validate_rejects_pymia_repo(smoke_module, pymia_path: Path) -> None:
    ok, reason = smoke_module.validate_sandbox_path(pymia_path)
    assert ok is False
    assert "forbidden" in reason.lower() or "PymIA" in reason


def test_validate_rejects_outside_scope(smoke_module, tmp_path: Path) -> None:
    outside = tmp_path / "random_dir"
    outside.mkdir()
    ok, reason = smoke_module.validate_sandbox_path(outside)
    assert ok is False
    assert ".tmp/hermes-scn-local" in reason


def test_validate_accepts_valid_sandbox(smoke_module, valid_sandbox: Path) -> None:
    ok, reason = smoke_module.validate_sandbox_path(valid_sandbox)
    assert ok is True
    assert reason == "ok"


def test_validate_artifacts_all_present(smoke_module, valid_sandbox: Path) -> None:
    passed, blocked = smoke_module.validate_artifacts(valid_sandbox)
    assert len(passed) == len(smoke_module.REQUIRED_ARTIFACTS)
    assert blocked == []


def test_validate_artifacts_missing(smoke_module, tmp_path: Path) -> None:
    empty = tmp_path / ".tmp" / "hermes-scn-local"
    empty.mkdir(parents=True)
    passed, blocked = smoke_module.validate_artifacts(empty)
    assert passed == []
    assert len(blocked) == len(smoke_module.REQUIRED_ARTIFACTS)


def test_build_evidence_pass(smoke_module, valid_sandbox: Path) -> None:
    evidence = smoke_module.build_evidence(
        valid_sandbox,
        path_ok=True,
        path_reason="ok",
        artifacts_passed=list(smoke_module.REQUIRED_ARTIFACTS),
        artifacts_blocked=[],
    )
    assert evidence["overall"] == "PASS"
    assert evidence["no_runtime_real"] is True
    assert evidence["no_secrets"] is True
    assert evidence["no_telegram"] is True
    assert evidence["no_production"] is True
    assert evidence["sandbox_path_ok"] is True


def test_build_evidence_blocked_by_path(smoke_module, tmp_path: Path) -> None:
    evidence = smoke_module.build_evidence(
        tmp_path,
        path_ok=False,
        path_reason="outside scope",
        artifacts_passed=[],
        artifacts_blocked=[],
    )
    assert evidence["overall"] == "BLOCKED"
    assert evidence["sandbox_path_ok"] is False


def test_build_evidence_blocked_by_artifact(smoke_module, valid_sandbox: Path) -> None:
    evidence = smoke_module.build_evidence(
        valid_sandbox,
        path_ok=True,
        path_reason="ok",
        artifacts_passed=[],
        artifacts_blocked=["sandbox/HERMES_HOME/README.md"],
    )
    assert evidence["overall"] == "BLOCKED"


def test_write_evidence_inside_sandbox(smoke_module, valid_sandbox: Path) -> None:
    evidence = smoke_module.build_evidence(
        valid_sandbox,
        path_ok=True,
        path_reason="ok",
        artifacts_passed=list(smoke_module.REQUIRED_ARTIFACTS),
        artifacts_blocked=[],
    )
    target = smoke_module.write_evidence(valid_sandbox, evidence)
    assert target.exists()
    resolved = target.resolve()
    try:
        resolved.relative_to(valid_sandbox.resolve())
    except ValueError:
        pytest.fail("evidence file escaped sandbox root")
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["overall"] == "PASS"


def test_main_happy_path_returns_zero(smoke_module, valid_sandbox: Path, capsys) -> None:
    rc = smoke_module.main(["--sandbox-path", str(valid_sandbox)])
    assert rc == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out.strip().split("\n\n")[0])
    assert parsed["overall"] == "PASS"
    evidence_file = valid_sandbox / "sandbox" / "logs" / "sandbox_smoke_test_result.json"
    assert evidence_file.exists()


def test_main_blocked_path_returns_nonzero(smoke_module, tmp_path: Path, capsys) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    rc = smoke_module.main(["--sandbox-path", str(outside)])
    assert rc != 0
    captured = capsys.readouterr()
    assert "BLOCKED" in captured.err

"""Tests para CLI de auditoría de orquestación."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.orchestration import audit_cli
from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import save_state


def test_help_works(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        audit_cli.main(["--help"])
    out = capsys.readouterr()
    assert exc.value.code == 0
    assert "usage:" in out.out.lower()


def test_list_empty_storage_returns_zero(tmp_path: Path, capsys) -> None:
    code = audit_cli.main(["--base-dir", str(tmp_path), "list", "tenant"])
    out = capsys.readouterr()
    assert code == 0
    assert "No conversations found." in out.out


def test_list_with_data_shows_conversation_and_phase(tmp_path: Path, capsys) -> None:
    state = PymIAState(
        tenant_id="tenant",
        chat_id="chat1",
        conversation_id="conv1",
        phase="DELIVERED",
    )
    save_state("tenant", "chat1", state, tmp_path)

    code = audit_cli.main(["--base-dir", str(tmp_path), "list", "tenant"])
    out = capsys.readouterr()
    assert code == 0
    assert "conv1" in out.out
    assert "DELIVERED" in out.out


def test_show_missing_chat_returns_one(tmp_path: Path, capsys) -> None:
    code = audit_cli.main(["--base-dir", str(tmp_path), "show", "tenant", "missing"])
    out = capsys.readouterr()
    assert code == 1
    assert "Conversation not found." in out.out


def test_show_state_prints_required_fields(tmp_path: Path, capsys) -> None:
    state = PymIAState(
        tenant_id="tenant",
        chat_id="chat1",
        conversation_id="conv1",
        phase="DELIVERED",
        evidence_ids=["ev1", "ev2"],
        delivery_status="READY_TO_DELIVER",
        progressive_context={"step": "intake", "slot": "costs"},
    )
    save_state("tenant", "chat1", state, tmp_path)

    code = audit_cli.main(["--base-dir", str(tmp_path), "show", "tenant", "chat1"])
    out = capsys.readouterr()
    assert code == 0
    assert "phase: DELIVERED" in out.out
    assert "evidence_count: 2" in out.out
    assert "delivery_status: READY_TO_DELIVER" in out.out
    assert "has_progressive_context: True" in out.out
    assert "progressive_context_keys: ['slot', 'step']" in out.out


def test_history_outputs_phases_in_order(tmp_path: Path, capsys) -> None:
    save_state(
        "tenant",
        "chat1",
        PymIAState(tenant_id="tenant", chat_id="chat1", conversation_id="conv1", phase="NEW"),
        tmp_path,
    )
    save_state(
        "tenant",
        "chat1",
        PymIAState(
            tenant_id="tenant",
            chat_id="chat1",
            conversation_id="conv1",
            phase="EXECUTED",
            execution_status="EXECUTED",
        ),
        tmp_path,
    )

    code = audit_cli.main(["--base-dir", str(tmp_path), "history", "tenant", "chat1"])
    out = capsys.readouterr()
    assert code == 0
    lines = [line for line in out.out.splitlines() if line.strip()]
    assert len(lines) == 2
    assert "\tNEW\t" in lines[0]
    assert "\tEXECUTED\t" in lines[1]


def test_export_creates_jsonl_and_reports_count(tmp_path: Path, capsys) -> None:
    save_state(
        "tenant",
        "chat1",
        PymIAState(tenant_id="tenant", chat_id="chat1", conversation_id="conv1", phase="NEW"),
        tmp_path,
    )
    output_path = tmp_path / "exports" / "chat1.jsonl"
    code = audit_cli.main(
        ["--base-dir", str(tmp_path), "export", "tenant", "chat1", str(output_path)]
    )
    out = capsys.readouterr()
    assert code == 0
    assert "exported_lines: 1" in out.out
    assert output_path.exists()
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line]
    assert len(rows) == 1


def test_corrupt_jsonl_returns_exit_code_two(tmp_path: Path, capsys) -> None:
    state_file = tmp_path / "tenant" / "conversation_states.jsonl"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("{invalid json}\n", encoding="utf-8")

    code = audit_cli.main(["--base-dir", str(tmp_path), "list", "tenant"])
    out = capsys.readouterr()
    assert code == 2
    assert "Error:" in out.err


def test_audit_cli_has_no_forbidden_imports() -> None:
    lines = Path("pymia/orchestration/audit_cli.py").read_text(encoding="utf-8").splitlines()
    import_lines = [
        line.strip().lower()
        for line in lines
        if line.strip().startswith("import ") or line.strip().startswith("from ")
    ]
    joined = "\n".join(import_lines)
    forbidden = ("smartpyme", "telegram", "hermes", "langgraph")
    for token in forbidden:
        assert token not in joined

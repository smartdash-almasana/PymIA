from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pymia.telegram_excel_diagnostic import (
    is_diagnostic_request,
    render_dispatch_result,
    run_latest_excel_diagnostic,
)
from pymia.telegram_runtime import SENTINEL


def test_is_diagnostic_request_detects_explicit_diagnostic_intent() -> None:
    assert is_diagnostic_request("diagnosticalo") is True
    assert is_diagnostic_request("hace diagnostico") is True
    assert is_diagnostic_request("analiza el excel") is False


def test_render_dispatch_result_includes_status_and_sentinel() -> None:
    result = SimpleNamespace(
        status="EXECUTED",
        microservice_name="excel_diagnostic_worker",
        findings_count=3,
        output_refs=["out/report.md"],
        warnings=[],
    )
    text = render_dispatch_result(result)
    assert text.startswith(SENTINEL)
    assert "status: EXECUTED" in text
    assert "microservice: excel_diagnostic_worker" in text
    assert "findings_count: 3" in text
    assert "out/report.md" in text


def test_render_dispatch_result_does_not_invent_when_not_executed() -> None:
    result = SimpleNamespace(
        status="FAILED",
        microservice_name="excel_diagnostic_worker",
        findings_count=0,
        output_refs=[],
        warnings=["boom"],
    )
    text = render_dispatch_result(result)
    assert SENTINEL in text
    assert "status: FAILED" in text
    assert "No invento diagnostico" in text
    assert "boom" in text


def test_run_latest_excel_diagnostic_blocks_without_file() -> None:
    with patch("pymia.telegram_excel_diagnostic.resolve_latest_excel", return_value=None), patch(
        "pymia.telegram_excel_diagnostic.dispatch_candidate"
    ) as mocked_dispatch:
        result = run_latest_excel_diagnostic()
    mocked_dispatch.assert_not_called()
    assert result.mode == "blocked"
    assert SENTINEL in result.text
    assert "No encontre un Excel" in result.text


def test_run_latest_excel_diagnostic_dispatches_candidate_for_latest_file(tmp_path: Path) -> None:
    latest = tmp_path / "ventas.xlsx"
    latest.write_bytes(b"fake")
    fake_result = SimpleNamespace(
        status="EXECUTED",
        microservice_name="excel_diagnostic_worker",
        findings_count=2,
        output_refs=[str(tmp_path / "diagnostic_report.md")],
        warnings=[],
    )

    with patch("pymia.telegram_excel_diagnostic.resolve_latest_excel", return_value=latest), patch(
        "pymia.telegram_excel_diagnostic.dispatch_candidate", return_value=fake_result
    ) as mocked_dispatch:
        result = run_latest_excel_diagnostic(output_dir=tmp_path / "out")

    mocked_dispatch.assert_called_once()
    candidate = mocked_dispatch.call_args.args[0]
    assert candidate.runtime_classification == "excel_diagnostic"
    assert candidate.status == "READY_TO_EXECUTE"
    assert candidate.can_dispatch is True
    assert mocked_dispatch.call_args.kwargs["evidence_path"] == latest
    assert SENTINEL in result.text
    assert "status: EXECUTED" in result.text

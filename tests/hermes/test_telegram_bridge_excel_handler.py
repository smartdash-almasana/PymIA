# -*- coding: utf-8 -*-
"""
Unit tests for pymia.hermes.plugins.pymia_telegram_bridge.excel_handler.

These tests validate Excel analysis request processing
without touching AppData, Hermes, Telegram, or LLM.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

import pytest

from pymia.hermes.plugins.pymia_telegram_bridge.excel_handler import (
    AnalysisReply,
    process_excel_analysis_request,
)


@dataclass
class MockFinding:
    """Mock Finding for testing."""
    code: str
    severity: str
    message: str
    count: int


@dataclass
class MockEvidenceRecord:
    """Mock EvidenceRecord for testing."""
    tenant_id: str
    source_file: str
    total_rows: int


@dataclass
class MockExcelDiagnosticResult:
    """Mock ExcelDiagnosticResult for testing."""
    evidence: MockEvidenceRecord
    findings: list
    markdown: str


@pytest.fixture
def temp_excel(tmp_path: Path) -> Path:
    """Create a temporary Excel file for testing."""
    excel_file = tmp_path / "test_report.xlsx"
    excel_file.write_bytes(b"fake excel content")
    return excel_file


def test_handler_fails_if_file_not_found():
    """process_excel_analysis_request returns BLOCKED if file doesn't exist."""
    reply = process_excel_analysis_request(
        file_path="/nonexistent/file.xlsx",
        tenant_id="telegram:test",
        user_id="user123",
        message_text="Analizá rentabilidad",
    )

    assert isinstance(reply, AnalysisReply)
    assert reply.status == "BLOCKED"
    assert reply.findings_count == 0
    assert "no existe" in reply.reply_text.lower()


def test_handler_fails_if_unsupported_extension(tmp_path: Path):
    """process_excel_analysis_request returns BLOCKED if extension is unsupported."""
    # Create a file with unsupported extension
    unsupported_file = tmp_path / "test.pdf"
    unsupported_file.write_bytes(b"fake pdf")

    reply = process_excel_analysis_request(
        file_path=unsupported_file,
        tenant_id="telegram:test",
        user_id="user123",
        message_text="Analizá rentabilidad",
    )

    assert isinstance(reply, AnalysisReply)
    assert reply.status == "BLOCKED"
    assert reply.findings_count == 0
    assert ".xlsx, .xls o .csv" in reply.reply_text


def test_handler_calls_diagnose_excel_on_valid_file(temp_excel: Path):
    """process_excel_analysis_request calls diagnose_excel and returns EXECUTED."""
    # Mock diagnose_excel
    mock_result = MockExcelDiagnosticResult(
        evidence=MockEvidenceRecord(
            tenant_id="telegram:test",
            source_file=str(temp_excel),
            total_rows=100,
        ),
        findings=[
            MockFinding(code="LOW_MARGIN", severity="medium", message="Margen bajo (<10%).", count=5),
            MockFinding(code="DUPLICATE_ROWS", severity="medium", message="Filas duplicadas detectadas.", count=2),
        ],
        markdown="# Mock Report",
    )

    with patch(
        "pymia.hermes.plugins.pymia_telegram_bridge.excel_handler.diagnose_excel",
        return_value=mock_result,
    ):
        reply = process_excel_analysis_request(
            file_path=temp_excel,
            tenant_id="telegram:test",
            user_id="user123",
            message_text="Analizá rentabilidad",
        )

    assert isinstance(reply, AnalysisReply)
    assert reply.status == "EXECUTED"
    assert reply.findings_count == 2
    assert "Hallazgos" in reply.reply_text
    assert "LOW_MARGIN" in reply.reply_text
    assert "DUPLICATE_ROWS" in reply.reply_text
    assert "100" in reply.reply_text  # total_rows


def test_handler_returns_no_findings_message(temp_excel: Path):
    """process_excel_analysis_request returns 'Sin hallazgos' when no findings."""
    mock_result = MockExcelDiagnosticResult(
        evidence=MockEvidenceRecord(
            tenant_id="telegram:test",
            source_file=str(temp_excel),
            total_rows=50,
        ),
        findings=[],
        markdown="# Mock Report",
    )

    with patch(
        "pymia.hermes.plugins.pymia_telegram_bridge.excel_handler.diagnose_excel",
        return_value=mock_result,
    ):
        reply = process_excel_analysis_request(
            file_path=temp_excel,
            tenant_id="telegram:test",
            user_id="user123",
            message_text="Analizá rentabilidad",
        )

    assert reply.status == "EXECUTED"
    assert reply.findings_count == 0
    assert "Sin hallazgos" in reply.reply_text


def test_handler_returns_fallback_on_import_error(temp_excel: Path):
    """process_excel_analysis_request returns FAILED fallback on ImportError."""
    with patch(
        "pymia.hermes.plugins.pymia_telegram_bridge.excel_handler.diagnose_excel",
        side_effect=ImportError("No module named 'pandas'"),
    ):
        reply = process_excel_analysis_request(
            file_path=temp_excel,
            tenant_id="telegram:test",
            user_id="user123",
            message_text="Analizá rentabilidad",
        )

    assert reply.status == "FAILED"
    assert reply.findings_count == 0
    assert "todavía no pude procesarlo" in reply.reply_text
    assert "módulo de diagnóstico no disponible" in reply.reply_text


def test_handler_returns_fallback_on_execution_error(temp_excel: Path):
    """process_excel_analysis_request returns FAILED fallback on execution error."""
    with patch(
        "pymia.hermes.plugins.pymia_telegram_bridge.excel_handler.diagnose_excel",
        side_effect=ValueError("Invalid Excel format"),
    ):
        reply = process_excel_analysis_request(
            file_path=temp_excel,
            tenant_id="telegram:test",
            user_id="user123",
            message_text="Analizá rentabilidad",
        )

    assert reply.status == "FAILED"
    assert reply.findings_count == 0
    assert "todavía no pude procesarlo" in reply.reply_text
    assert "ValueError" in reply.reply_text


def test_handler_supports_csv_extension(tmp_path: Path):
    """process_excel_analysis_request accepts .csv files."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_bytes(b"col1,col2\n1,2\n3,4")

    mock_result = MockExcelDiagnosticResult(
        evidence=MockEvidenceRecord(
            tenant_id="telegram:test",
            source_file=str(csv_file),
            total_rows=2,
        ),
        findings=[],
        markdown="# Mock Report",
    )

    with patch(
        "pymia.hermes.plugins.pymia_telegram_bridge.excel_handler.diagnose_excel",
        return_value=mock_result,
    ):
        reply = process_excel_analysis_request(
            file_path=csv_file,
            tenant_id="telegram:test",
            user_id="user123",
            message_text="Analizá rentabilidad",
        )

    assert reply.status == "EXECUTED"


def test_handler_does_not_use_llm_or_hermes_tools():
    """Verify excel_handler does not import LLM or Hermes tools."""
    import pymia.hermes.plugins.pymia_telegram_bridge.excel_handler as handler_module
    import inspect

    source = inspect.getsource(handler_module)

    # Forbidden imports/patterns
    forbidden = [
        "openai",
        "anthropic",
        "llm",
        "hermes_context",
        "hermes_tool",
        "subprocess",
        "os.system",
        "eval(",
        "exec(",
    ]

    for pattern in forbidden:
        assert pattern not in source.lower(), f"Forbidden pattern found: {pattern}"

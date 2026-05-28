# -*- coding: utf-8 -*-
"""
Tests for the PymIA Telegram Bridge plugin wrapper.

These tests validate:
- handle_pre_gateway_dispatch with Excel intent + existing Excel
- handle_pre_gateway_dispatch without Excel intent (not_handled)
- handle_pre_gateway_dispatch with document upload
- Correct integration between session_builder, document_resolver, intent_router, excel_handler
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from pymia.hermes.plugins.pymia_telegram_bridge.plugin_wrapper import (
    handle_pre_gateway_dispatch,
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repo structure with .runtime/telegram_documents/"""
    runtime_dir = tmp_path / ".runtime" / "telegram_documents"
    runtime_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def sample_excel(temp_repo):
    """Create a sample Excel file in .runtime/telegram_documents/"""
    excel_path = temp_repo / ".runtime" / "telegram_documents" / "123456_test.xlsx"
    excel_path.write_text("dummy excel content")
    return excel_path


class TestHandlePreGatewayDispatch:
    """Tests for handle_pre_gateway_dispatch function."""

    def test_dispatch_handles_excel_intent_with_existing_excel(
        self, temp_repo, sample_excel
    ):
        """Test that dispatch handles Excel analysis request when Excel exists."""
        event = {
            "message_text": "Analizá rentabilidad marzo abril mayo",
            "chat_id": "123456",
            "user_id": "789",
        }

        # Mock process_excel_analysis_request to return success
        with patch(
            "pymia.hermes.plugins.pymia_telegram_bridge.plugin_wrapper.process_excel_analysis_request"
        ) as mock_handler:
            from pymia.hermes.plugins.pymia_telegram_bridge.excel_handler import (
                AnalysisReply,
            )

            mock_handler.return_value = AnalysisReply(
                reply_text="Hallazgos: 3 problemas encontrados",
                status="EXECUTED",
                findings_count=3,
                file_path=sample_excel,
            )

            result = handle_pre_gateway_dispatch(
                event=event,
                adapter=None,
                repo_root=temp_repo,
            )

        assert result["handled"] is True
        assert result["status"] == "EXECUTED"
        assert result["skip_gateway"] is True
        assert "Hallazgos" in result["reply_text"]
        mock_handler.assert_called_once()

    def test_dispatch_returns_not_handled_without_excel(self, temp_repo):
        """Test that dispatch returns not_handled when no Excel exists."""
        event = {
            "message_text": "Analizá rentabilidad marzo abril mayo",
            "chat_id": "123456",
            "user_id": "789",
        }

        result = handle_pre_gateway_dispatch(
            event=event,
            adapter=None,
            repo_root=temp_repo,
        )

        assert result["handled"] is False
        assert result["status"] == "NOT_HANDLED"
        assert result["skip_gateway"] is False
        assert result["reply_text"] == ""

    def test_dispatch_returns_not_handled_without_intent(self, temp_repo, sample_excel):
        """Test that dispatch returns not_handled when message has no Excel intent."""
        event = {
            "message_text": "Hola, ¿cómo estás?",
            "chat_id": "123456",
            "user_id": "789",
        }

        result = handle_pre_gateway_dispatch(
            event=event,
            adapter=None,
            repo_root=temp_repo,
        )

        assert result["handled"] is False
        assert result["status"] == "NOT_HANDLED"
        assert result["skip_gateway"] is False

    def test_dispatch_handles_document_upload(self, temp_repo):
        """Test that dispatch handles document upload event."""
        # Create a temporary source document
        source_doc = temp_repo / "source_document.xlsx"
        source_doc.write_text("dummy excel")

        event = {
            "document_path": str(source_doc),
            "file_name": "test.xlsx",
            "chat_id": "123456",
            "user_id": "789",
        }

        result = handle_pre_gateway_dispatch(
            event=event,
            adapter=None,
            repo_root=temp_repo,
        )

        assert result["handled"] is True
        assert result["status"] == "CACHED"
        assert result["skip_gateway"] is True
        assert "Recibí" in result["reply_text"]

        # Verify file was copied
        copied_path = temp_repo / ".runtime" / "telegram_documents" / "123456_test.xlsx"
        assert copied_path.exists()

    def test_dispatch_handles_document_upload_failure(self, temp_repo):
        """Test that dispatch handles document upload failure gracefully."""
        event = {
            "document_path": "/nonexistent/path.xlsx",
            "file_name": "test.xlsx",
            "chat_id": "123456",
            "user_id": "789",
        }

        result = handle_pre_gateway_dispatch(
            event=event,
            adapter=None,
            repo_root=temp_repo,
        )

        assert result["handled"] is True
        assert result["status"] == "FAILED"
        assert result["skip_gateway"] is True
        assert "Error" in result["reply_text"]

    def test_dispatch_returns_not_handled_for_empty_event(self, temp_repo):
        """Test that dispatch returns not_handled for event with no message or document."""
        event = {
            "chat_id": "123456",
            "user_id": "789",
        }

        result = handle_pre_gateway_dispatch(
            event=event,
            adapter=None,
            repo_root=temp_repo,
        )

        assert result["handled"] is False
        assert result["status"] == "NOT_HANDLED"
        assert result["skip_gateway"] is False

    def test_dispatch_handles_excel_handler_failure(self, temp_repo, sample_excel):
        """Test that dispatch handles Excel handler failure gracefully."""
        event = {
            "message_text": "Analizá rentabilidad marzo abril mayo",
            "chat_id": "123456",
            "user_id": "789",
        }

        # Mock process_excel_analysis_request to raise exception
        with patch(
            "pymia.hermes.plugins.pymia_telegram_bridge.plugin_wrapper.process_excel_analysis_request"
        ) as mock_handler:
            mock_handler.side_effect = RuntimeError("Microservice unavailable")

            result = handle_pre_gateway_dispatch(
                event=event,
                adapter=None,
                repo_root=temp_repo,
            )

        assert result["handled"] is True
        assert result["status"] == "FAILED"
        assert result["skip_gateway"] is True
        assert "Error" in result["reply_text"]

    def test_dispatch_uses_correct_session_keys(self, temp_repo, sample_excel):
        """Test that dispatch builds correct session keys."""
        event = {
            "message_text": "Analizá rentabilidad",
            "chat_id": "123456",
            "user_id": "789",
        }

        with patch(
            "pymia.hermes.plugins.pymia_telegram_bridge.plugin_wrapper.process_excel_analysis_request"
        ) as mock_handler:
            from pymia.hermes.plugins.pymia_telegram_bridge.excel_handler import (
                AnalysisReply,
            )

            mock_handler.return_value = AnalysisReply(
                reply_text="OK",
                status="EXECUTED",
                findings_count=0,
                file_path=sample_excel,
            )

            handle_pre_gateway_dispatch(
                event=event,
                adapter=None,
                repo_root=temp_repo,
            )

        # Verify process_excel_analysis_request was called with correct tenant_id and user_id
        call_args = mock_handler.call_args
        assert call_args.kwargs["tenant_id"] == "telegram:123456"
        assert call_args.kwargs["user_id"] == "789"

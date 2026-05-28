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

    def test_dispatch_returns_fallback_without_excel(self, temp_repo):
        """Test that dispatch returns fallback when no Excel exists."""
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

        assert result["handled"] is True
        assert result["status"] == "FALLBACK"
        assert result["skip_gateway"] is True
        assert result["route"] == "fallback"
        assert "problema operativo" in result["reply_text"]
        assert "PymIA Factory" not in result["reply_text"]
        assert "agente genérico" not in result["reply_text"]

    def test_dispatch_returns_fallback_without_intent(self, temp_repo, sample_excel):
        """Test that dispatch returns fallback when message has no Excel intent."""
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

        assert result["handled"] is True
        assert result["status"] == "FALLBACK"
        assert result["skip_gateway"] is True
        assert result["route"] == "fallback"
        assert "problema operativo" in result["reply_text"]
        assert "PymIA Factory" not in result["reply_text"]
        assert "agente genérico" not in result["reply_text"]

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

    def test_dispatch_returns_fallback_for_empty_event(self, temp_repo):
        """Test that dispatch returns fallback for event with no message or document."""
        event = {
            "chat_id": "123456",
            "user_id": "789",
        }

        result = handle_pre_gateway_dispatch(
            event=event,
            adapter=None,
            repo_root=temp_repo,
        )

        assert result["handled"] is True
        assert result["status"] == "FALLBACK"
        assert result["skip_gateway"] is True
        assert result["route"] == "fallback"
        assert "No entendí el mensaje" in result["reply_text"]

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

    def test_dispatch_never_returns_handled_false_for_on_message(self, temp_repo):
        """Test that dispatch NEVER returns handled=False for on_message events."""
        # Test 1: message without Excel
        event1 = {
            "message_text": "Hola, ¿cómo estás?",
            "chat_id": "123456",
            "user_id": "789",
        }
        result1 = handle_pre_gateway_dispatch(event=event1, adapter=None, repo_root=temp_repo)
        assert result1["handled"] is True, "Escape hatch still open: handled=False for message without Excel"

        # Test 2: message with Excel but no intent
        excel_path = temp_repo / ".runtime" / "telegram_documents" / "123456_test.xlsx"
        excel_path.write_text("dummy")
        
        event2 = {
            "message_text": "Buen día",
            "chat_id": "123456",
            "user_id": "789",
        }
        result2 = handle_pre_gateway_dispatch(event=event2, adapter=None, repo_root=temp_repo)
        assert result2["handled"] is True, "Escape hatch still open: handled=False for message with Excel but no intent"

        # Test 3: empty message
        event3 = {
            "message_text": "",
            "chat_id": "123456",
            "user_id": "789",
        }
        result3 = handle_pre_gateway_dispatch(event=event3, adapter=None, repo_root=temp_repo)
        assert result3["handled"] is True, "Escape hatch still open: handled=False for empty message"

    def test_dispatch_never_returns_skip_gateway_false_for_on_message(self, temp_repo):
        """Test that dispatch NEVER returns skip_gateway=False for on_message events."""
        # Test 1: message without Excel
        event1 = {
            "message_text": "Hola",
            "chat_id": "123456",
            "user_id": "789",
        }
        result1 = handle_pre_gateway_dispatch(event=event1, adapter=None, repo_root=temp_repo)
        assert result1["skip_gateway"] is True, "Escape hatch still open: skip_gateway=False for message without Excel"

        # Test 2: message with Excel but no intent
        excel_path = temp_repo / ".runtime" / "telegram_documents" / "123456_test.xlsx"
        excel_path.write_text("dummy")
        
        event2 = {
            "message_text": "Buen día",
            "chat_id": "123456",
            "user_id": "789",
        }
        result2 = handle_pre_gateway_dispatch(event=event2, adapter=None, repo_root=temp_repo)
        assert result2["skip_gateway"] is True, "Escape hatch still open: skip_gateway=False for message with Excel but no intent"

        # Test 3: empty message
        event3 = {
            "message_text": "",
            "chat_id": "123456",
            "user_id": "789",
        }
        result3 = handle_pre_gateway_dispatch(event=event3, adapter=None, repo_root=temp_repo)
        assert result3["skip_gateway"] is True, "Escape hatch still open: skip_gateway=False for empty message"

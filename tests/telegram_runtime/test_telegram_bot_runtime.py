"""Tests para telegram_bot_runtime."""
from __future__ import annotations

import inspect
import io
import json
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from pymia.telegram_bot_runtime import (
    ANALYSIS_TRIGGERS,
    TELEGRAM_MODE_LEGACY,
    TELEGRAM_MODE_LLM_OPERATOR,
    dry_run,
    get_updates,
    live_loop,
    process_message,
    route_text_message,
    send_message,
)
from pymia.telegram_runtime import SENTINEL
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


class TestDryRun:
    """Tests de modo dry-run."""

    def test_dry_run_contains_sentinel(self, capsys):
        """dry-run debe incluir SENTINEL en output."""
        dry_run(RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
        captured = capsys.readouterr()
        assert SENTINEL in captured.out
        assert "[DRY-RUN]" in captured.out

    def test_dry_run_uses_source_pymia(self, capsys):
        """dry-run debe usar source=pymia (verificable en reply)."""
        dry_run("hola")
        captured = capsys.readouterr()
        # El reply debe venir de handle_telegram_message que retorna source="pymia"
        # Verificamos que el texto contiene SENTINEL (garantía de origen pymia)
        assert SENTINEL in captured.out


class TestProcessMessage:
    """Tests de process_message."""

    def test_process_message_always_includes_sentinel(self):
        """process_message debe garantizar SENTINEL en toda respuesta."""
        reply = process_message(RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
        assert SENTINEL in reply

    def test_process_message_empty_returns_blocked(self):
        """Mensaje vacío debe retornar respuesta de bloqueo."""
        reply = process_message("")
        assert SENTINEL in reply
        assert "No recibí mensaje" in reply

    def test_process_message_profitability_requests_evidence(self):
        """Consulta de rentabilidad debe pedir evidencia."""
        reply = process_message(RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
        assert "ventas del periodo" in reply
        assert "costos" in reply or "compras" in reply
        assert "gastos fijos" in reply


class TestLiveModeTokenValidation:
    """Tests de validación de TELEGRAM_BOT_TOKEN en live mode."""

    def test_live_mode_without_token_exits_with_error(self):
        """Live mode sin TELEGRAM_BOT_TOKEN debe salir con código != 0."""
        # Ejecutar como subprocess para capturar exit code
        env = os.environ.copy()
        env.pop("TELEGRAM_BOT_TOKEN", None)  # Asegurar que no existe

        result = subprocess.run(
            [sys.executable, "-m", "pymia.telegram_bot_runtime"],
            env=env,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "TELEGRAM_BOT_TOKEN" in result.stderr


class TestNoHermesImports:
    """Tests de ausencia de imports de Hermes."""

    def test_module_does_not_import_hermes(self):
        """telegram_bot_runtime no debe importar hermes."""
        from pymia import telegram_bot_runtime

        source = inspect.getsource(telegram_bot_runtime)
        assert "import hermes" not in source
        assert "from hermes" not in source
        assert "from pymia.hermes" not in source


class TestSendMessage:
    """Tests de send_message con mocks."""

    def test_send_message_constructs_correct_payload(self):
        """send_message debe construir payload JSON correcto."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"ok": True}).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            result = send_message("fake_token", 123456, "test message")

            assert result is True
            assert mock_urlopen.called

            # Verificar que se llamó con URL correcta
            call_args = mock_urlopen.call_args
            request = call_args[0][0]
            assert "sendMessage" in request.full_url
            assert "fake_token" in request.full_url

            # Verificar payload
            payload = json.loads(request.data.decode("utf-8"))
            assert payload["chat_id"] == 123456
            assert payload["text"] == "test message"

    def test_send_message_returns_false_on_network_error(self):
        """send_message debe retornar False si hay error de red."""
        import urllib.error

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("network error")):
            result = send_message("fake_token", 123456, "test message")
            assert result is False


class TestGetUpdates:
    """Tests de get_updates con mocks."""

    def test_get_updates_parses_text_and_chat_id(self):
        """get_updates debe parsear texto y chat_id de respuesta fake."""
        fake_response = {
            "ok": True,
            "result": [
                {
                    "update_id": 100,
                    "message": {
                        "message_id": 1,
                        "chat": {"id": 999},
                        "text": "hola mundo",
                    },
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_response).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            updates = get_updates("fake_token", offset=0)

            assert len(updates) == 1
            assert updates[0]["update_id"] == 100
            assert updates[0]["message"]["chat"]["id"] == 999
            assert updates[0]["message"]["text"] == "hola mundo"

    def test_get_updates_returns_empty_on_network_error(self):
        """get_updates debe retornar lista vacía si hay error de red."""
        import urllib.error

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("network error")):
            updates = get_updates("fake_token", offset=0)
            assert updates == []

    def test_get_updates_returns_empty_on_parse_error(self):
        """get_updates debe retornar lista vacía si hay error de parseo."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid json"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            updates = get_updates("fake_token", offset=0)
            assert updates == []


class TestLiveLoopDocumentSupport:
    """Tests de soporte mínimo para documentos en live_loop."""

    def test_live_loop_processes_document_update_before_text(self):
        update = {
            "update_id": 200,
            "message": {
                "chat": {"id": 777},
                "text": "esto no debe usarse si hay document",
                "document": {"file_id": "file-1", "file_name": "ventas.xlsx"},
            },
        }

        with patch("pymia.telegram_bot_runtime.get_updates", side_effect=[[update], KeyboardInterrupt]), patch(
            "pymia.telegram_bot_runtime.handle_document"
        ) as mocked_handle_document, patch("pymia.telegram_bot_runtime.send_message", return_value=True) as mocked_send:
            mocked_handle_document.return_value.text = f"{SENTINEL} Documento recibido"
            live_loop("fake-token")

        mocked_handle_document.assert_called_once_with("fake-token", "file-1", "ventas.xlsx", 777)
        mocked_send.assert_called_once_with("fake-token", 777, f"{SENTINEL} Documento recibido")

    def test_live_loop_text_flow_regression(self):
        update = {
            "update_id": 201,
            "message": {
                "chat": {"id": 778},
                "text": "hola runtime",
            },
        }

        with patch("pymia.telegram_bot_runtime.get_updates", side_effect=[[update], KeyboardInterrupt]), patch(
            "pymia.telegram_bot_runtime.route_text_message", return_value=f"{SENTINEL} ok"
        ) as mocked_process, patch("pymia.telegram_bot_runtime.send_message", return_value=True) as mocked_send:
            live_loop("fake-token")

        mocked_process.assert_called_once_with("hola runtime", chat_id=778)
        mocked_send.assert_called_once_with("fake-token", 778, f"{SENTINEL} ok")

    def test_live_loop_updates_offset_after_document(self):
        offsets: list[int | None] = []
        update = {
            "update_id": 555,
            "message": {
                "chat": {"id": 779},
                "document": {"file_id": "file-2", "file_name": "ventas.xls"},
            },
        }

        def _fake_get_updates(_token: str, offset=None, timeout=30):
            del timeout
            offsets.append(offset)
            if len(offsets) == 1:
                return [update]
            raise KeyboardInterrupt()

        with patch("pymia.telegram_bot_runtime.get_updates", side_effect=_fake_get_updates), patch(
            "pymia.telegram_bot_runtime.handle_document"
        ) as mocked_handle_document, patch("pymia.telegram_bot_runtime.send_message", return_value=True):
            mocked_handle_document.return_value.text = f"{SENTINEL} Documento recibido"
            live_loop("fake-token")

        assert offsets == [None, 556]


class TestExcelSummaryRouting:
    def test_route_text_message_dispatches_excel_summary_for_trigger(self):
        trigger = ANALYSIS_TRIGGERS[0]
        with patch(
            "pymia.telegram_bot_runtime.analyze_latest_excel"
        ) as mocked_summary, patch("pymia.telegram_bot_runtime.process_message") as mocked_process:
            mocked_summary.return_value.text = f"{SENTINEL} Resumen estructural del Excel"
            reply = route_text_message(trigger)
        mocked_summary.assert_called_once()
        mocked_process.assert_not_called()
        assert SENTINEL in reply

    def test_route_text_message_dispatches_process_without_trigger(self):
        with patch("pymia.telegram_bot_runtime.analyze_latest_excel") as mocked_summary, patch(
            "pymia.telegram_bot_runtime.process_message", return_value=f"{SENTINEL} normal"
        ) as mocked_process:
            reply = route_text_message("hola")
        mocked_summary.assert_not_called()
        mocked_process.assert_called_once_with("hola")
        assert reply == f"{SENTINEL} normal"

    def test_route_text_message_dispatches_real_diagnostic_for_diagnostic_trigger(self):
        with patch(
            "pymia.telegram_bot_runtime.run_latest_excel_diagnostic"
        ) as mocked_diagnostic, patch("pymia.telegram_bot_runtime.analyze_latest_excel") as mocked_summary, patch(
            "pymia.telegram_bot_runtime.process_message"
        ) as mocked_process:
            mocked_diagnostic.return_value.text = f"{SENTINEL} Diagnostico Excel via dispatcher\nstatus: EXECUTED"
            reply = route_text_message("diagnosticalo")
        mocked_diagnostic.assert_called_once()
        mocked_summary.assert_not_called()
        mocked_process.assert_not_called()
        assert "Diagnostico Excel via dispatcher" in reply
        assert SENTINEL in reply


class TestLLMOperatorMode:
    def test_legacy_is_default_mode(self):
        with patch.dict("os.environ", {}, clear=False):
            with patch("pymia.telegram_bot_runtime.process_message", return_value=f"{SENTINEL} legacy") as mocked_process:
                reply = route_text_message("hola")
        mocked_process.assert_called_once_with("hola")
        assert reply == f"{SENTINEL} legacy"

    def test_llm_operator_mode_uses_operator_mocked_no_network(self):
        fake_provider = MagicMock()
        fake_operator = MagicMock()
        fake_operator.handle_turn.return_value.reply_text = f"{SENTINEL} operator ok"
        with patch.dict("os.environ", {"PYMIA_TELEGRAM_MODE": TELEGRAM_MODE_LLM_OPERATOR, "OPENROUTER_API_KEY": "x"}, clear=False), patch(
            "pymia.llm_operator.providers_openrouter.OpenRouterProvider", return_value=fake_provider
        ) as mocked_provider_cls, patch("pymia.llm_operator.operator.LLMOperator", return_value=fake_operator) as mocked_operator_cls:
            reply = route_text_message("hola", chat_id=123)
        mocked_provider_cls.assert_called_once()
        mocked_operator_cls.assert_called_once()
        fake_operator.handle_turn.assert_called_once()
        assert SENTINEL in reply

    def test_llm_operator_mode_without_key_fails_controlled(self):
        with patch.dict("os.environ", {"PYMIA_TELEGRAM_MODE": TELEGRAM_MODE_LLM_OPERATOR}, clear=True):
            with patch("pymia.telegram_bot_runtime._load_env_local", return_value={}):
                reply = route_text_message("hola")
        assert SENTINEL in reply
        assert "OPENROUTER_API_KEY" in reply

    def test_documents_do_not_pass_through_operator(self):
        update = {
            "update_id": 300,
            "message": {
                "chat": {"id": 880},
                "document": {"file_id": "file-3", "file_name": "ventas.xlsx"},
            },
        }
        with patch.dict("os.environ", {"PYMIA_TELEGRAM_MODE": TELEGRAM_MODE_LLM_OPERATOR}, clear=False), patch(
            "pymia.telegram_bot_runtime.get_updates", side_effect=[[update], KeyboardInterrupt]
        ), patch("pymia.telegram_bot_runtime.handle_document") as mocked_handle_document, patch(
            "pymia.telegram_bot_runtime.send_message", return_value=True
        ), patch("pymia.telegram_bot_runtime._route_text_with_operator") as mocked_operator_route:
            mocked_handle_document.return_value.text = f"{SENTINEL} Documento recibido"
            live_loop("fake-token")
        mocked_handle_document.assert_called_once()
        mocked_operator_route.assert_not_called()

    def test_excel_triggers_still_use_legacy_paths_in_llm_mode(self):
        with patch.dict("os.environ", {"PYMIA_TELEGRAM_MODE": TELEGRAM_MODE_LLM_OPERATOR, "OPENROUTER_API_KEY": "x"}, clear=False), patch(
            "pymia.telegram_bot_runtime.run_latest_excel_diagnostic"
        ) as mocked_diagnostic, patch("pymia.telegram_bot_runtime._route_text_with_operator") as mocked_operator_route:
            mocked_diagnostic.return_value.text = f"{SENTINEL} Diagnostico Excel via dispatcher"
            reply = route_text_message("diagnosticalo")
        mocked_diagnostic.assert_called_once()
        mocked_operator_route.assert_not_called()
        assert SENTINEL in reply

    def test_dry_run_llm_operator_uses_orientation_mock_instead_of_free_anamnesis(self, capsys):
        fake_provider = MagicMock()
        fake_operator = MagicMock()
        fake_operator.handle_turn.return_value.reply_text = (
            f"{SENTINEL} Antes de empezar, completamos la ficha. Tipo de organizacion/negocio:"
        )
        with patch.dict("os.environ", {"PYMIA_TELEGRAM_MODE": TELEGRAM_MODE_LLM_OPERATOR, "OPENROUTER_API_KEY": "x"}, clear=False), patch(
            "pymia.llm_operator.providers_openrouter.OpenRouterProvider", return_value=fake_provider
        ), patch("pymia.llm_operator.operator.LLMOperator", return_value=fake_operator):
            dry_run("hola")
        captured = capsys.readouterr()
        assert "Tipo de organizacion/negocio" in captured.out
        assert "¿vendés productos, fabricás algo o prestás servicios?" not in captured.out

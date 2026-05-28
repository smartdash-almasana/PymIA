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
    dry_run,
    get_updates,
    process_message,
    send_message,
)
from pymia.telegram_runtime import SENTINEL


class TestDryRun:
    """Tests de modo dry-run."""

    def test_dry_run_contains_sentinel(self, capsys):
        """dry-run debe incluir SENTINEL en output."""
        dry_run("no se si gano plata")
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
        reply = process_message("no se si gano plata")
        assert SENTINEL in reply

    def test_process_message_empty_returns_blocked(self):
        """Mensaje vacío debe retornar respuesta de bloqueo."""
        reply = process_message("")
        assert SENTINEL in reply
        assert "No recibí mensaje" in reply

    def test_process_message_profitability_requests_evidence(self):
        """Consulta de rentabilidad debe pedir evidencia."""
        reply = process_message("no se si gano plata")
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

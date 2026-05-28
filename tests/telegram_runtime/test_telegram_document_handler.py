from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from pymia.telegram_document_handler import (
    DocumentResult,
    download_telegram_file,
    handle_document,
    is_valid_document,
)
from pymia.telegram_runtime import SENTINEL


def _mock_response(payload: dict[str, object] | bytes) -> MagicMock:
    response = MagicMock()
    if isinstance(payload, bytes):
        response.read.return_value = payload
    else:
        response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__ = lambda s: s
    response.__exit__ = MagicMock(return_value=False)
    return response


def test_is_valid_document_accepts_excel_extensions() -> None:
    assert is_valid_document("ventas.xlsx")
    assert is_valid_document("ventas.XLS")
    assert is_valid_document("ventas.xlsm")


def test_is_valid_document_rejects_non_excel_extensions() -> None:
    assert not is_valid_document("ventas.csv")
    assert not is_valid_document("ventas.txt")
    assert not is_valid_document("")


def test_download_telegram_file_success(tmp_path: Path) -> None:
    get_file_response = _mock_response({"ok": True, "result": {"file_path": "docs/file.xlsx"}})
    file_response = _mock_response(b"binary-excel-content")

    with patch("urllib.request.urlopen", side_effect=[get_file_response, file_response]):
        downloaded = download_telegram_file("token", "file-id", "ventas.xlsx", tmp_path)

    assert downloaded is not None
    assert downloaded.exists()
    assert downloaded.suffix.lower() == ".xlsx"
    assert downloaded.read_bytes() == b"binary-excel-content"


def test_download_telegram_file_returns_none_on_getfile_error(tmp_path: Path) -> None:
    bad_response = _mock_response({"ok": False, "description": "bad"})
    with patch("urllib.request.urlopen", return_value=bad_response):
        downloaded = download_telegram_file("token", "file-id", "ventas.xlsx", tmp_path)
    assert downloaded is None


def test_handle_document_blocks_invalid_extension() -> None:
    result = handle_document("token", "file-id", "ventas.csv", chat_id=42)
    assert isinstance(result, DocumentResult)
    assert result.source == "pymia"
    assert result.mode == "blocked"
    assert SENTINEL in result.text
    assert result.file_path is None


def test_handle_document_received_success(tmp_path: Path) -> None:
    absolute_path = (tmp_path / "ok.xlsx").resolve()
    absolute_path.write_bytes(b"x")
    with patch("pymia.telegram_document_handler.download_telegram_file", return_value=absolute_path):
        result = handle_document("token", "file-id", "ventas.xlsx", chat_id=42)
    assert result.source == "pymia"
    assert result.mode == "received"
    assert SENTINEL in result.text
    assert result.file_path == str(absolute_path)
    assert Path(result.file_path).is_absolute()


def test_handle_document_returns_error_on_download_failure() -> None:
    with patch("pymia.telegram_document_handler.download_telegram_file", return_value=None):
        result = handle_document("token", "file-id", "ventas.xlsx", chat_id=42)
    assert result.source == "pymia"
    assert result.mode == "error"
    assert SENTINEL in result.text
    assert result.file_path is None


def test_handle_document_does_not_call_diagnose_excel() -> None:
    with patch("pymia.telegram_document_handler.download_telegram_file", return_value=None), patch(
        "pymia.smartpyme.excel_diagnostic.diagnose_excel"
    ) as mocked_diagnose:
        handle_document("token", "file-id", "ventas.xlsx", chat_id=42)
    mocked_diagnose.assert_not_called()

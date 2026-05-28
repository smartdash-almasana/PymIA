from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from pymia.telegram_runtime import SENTINEL

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"
TELEGRAM_FILE_BASE = "https://api.telegram.org/file/bot{token}/{file_path}"
RUNTIME_DOCUMENTS_DIR = Path(".runtime") / "telegram_documents"
VALID_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}


@dataclass(frozen=True)
class DocumentResult:
    text: str
    source: Literal["pymia"] = "pymia"
    mode: Literal["received", "blocked", "error"] = "received"
    file_path: str | None = None


def is_valid_document(file_name: str) -> bool:
    if not file_name:
        return False
    return Path(file_name).suffix.lower() in VALID_EXTENSIONS


def download_telegram_file(token: str, file_id: str, file_name: str, dest_dir: Path) -> Path | None:
    if not token or not file_id or not file_name:
        return None
    if not is_valid_document(file_name):
        return None

    get_file_url = TELEGRAM_API_BASE.format(token=token, method="getFile")
    params = urllib.parse.urlencode({"file_id": file_id})
    request_url = f"{get_file_url}?{params}"

    try:
        with urllib.request.urlopen(request_url, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("ok"):
            return None
        file_path = str(payload["result"]["file_path"])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, json.JSONDecodeError):
        return None

    sanitized_name = Path(file_name).name
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    output_name = f"{timestamp}_{sanitized_name}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    output_path = (dest_dir / output_name).resolve()

    file_url = TELEGRAM_FILE_BASE.format(token=token, file_path=file_path)
    try:
        with urllib.request.urlopen(file_url, timeout=30) as file_response:
            content = file_response.read()
        output_path.write_bytes(content)
        return output_path
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def handle_document(token: str, file_id: str, file_name: str, chat_id: int | str) -> DocumentResult:
    del chat_id

    if not is_valid_document(file_name):
        return DocumentResult(
            text=f"{SENTINEL} El archivo recibido no es un Excel valido (.xlsx/.xls/.xlsm).",
            mode="blocked",
            file_path=None,
        )

    target_dir = RUNTIME_DOCUMENTS_DIR
    downloaded = download_telegram_file(token, file_id, file_name, target_dir)
    if downloaded is None:
        return DocumentResult(
            text=f"{SENTINEL} Recibi el documento, pero no pude descargarlo todavia. Reintenta en unos segundos.",
            mode="error",
            file_path=None,
        )

    return DocumentResult(
        text=(
            f"{SENTINEL} Documento recibido: {Path(file_name).name}. "
            "Ya lo guarde y podes pedirme el analisis cuando quieras."
        ),
        mode="received",
        file_path=str(downloaded),
    )

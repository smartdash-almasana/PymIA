"""
Telegram Bot Runtime - Conexión directa sin Hermes.

Usa solo stdlib para polling mínimo contra Telegram Bot API.
Cada mensaje pasa por pymia.telegram_runtime.handle_telegram_message.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from pymia.telegram_document_handler import handle_document
from pymia.telegram_excel_summary import analyze_latest_excel
from pymia.telegram_runtime import SENTINEL, handle_telegram_message

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"
POLL_INTERVAL_SECONDS = 1
ANALYSIS_TRIGGERS = (
    "analizá el excel",
    "analiza el excel",
    "resumen del excel",
    "qué tiene el excel",
    "leer el excel",
    "estructura del excel",
)


def get_updates(token: str, offset: int | None = None, timeout: int = 30) -> list[dict[str, Any]]:
    """
    Llama a Telegram getUpdates API.

    Returns:
        Lista de updates (cada uno con update_id, message, etc.)
    """
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset

    url = TELEGRAM_API_BASE.format(token=token, method="getUpdates")
    full_url = f"{url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(full_url, timeout=timeout + 10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if not data.get("ok"):
                print(f"[ERROR] getUpdates failed: {data}", file=sys.stderr)
                return []
            return data.get("result", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"[ERROR] getUpdates network error: {exc}", file=sys.stderr)
        return []
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"[ERROR] getUpdates parse error: {exc}", file=sys.stderr)
        return []


def send_message(token: str, chat_id: int | str, text: str) -> bool:
    """
    Llama a Telegram sendMessage API.

    Returns:
        True si envío exitoso, False si error.
    """
    url = TELEGRAM_API_BASE.format(token=token, method="sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            if not result.get("ok"):
                print(f"[ERROR] sendMessage failed: {result}", file=sys.stderr)
                return False
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"[ERROR] sendMessage network error: {exc}", file=sys.stderr)
        return False
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"[ERROR] sendMessage parse error: {exc}", file=sys.stderr)
        return False


def process_message(text: str) -> str:
    """
    Procesa mensaje usando handle_telegram_message.
    Garantiza que toda respuesta contiene SENTINEL.
    """
    result = handle_telegram_message(text)
    # Garantía: toda respuesta debe contener SENTINEL
    if SENTINEL not in result.text:
        return f"{SENTINEL} {result.text}"
    return result.text


def route_text_message(text: str) -> str:
    lowered = (text or "").strip().lower()
    if any(trigger in lowered for trigger in ANALYSIS_TRIGGERS):
        summary = analyze_latest_excel()
        return summary.text if SENTINEL in summary.text else f"{SENTINEL} {summary.text}"
    return process_message(text)


def dry_run(message: str) -> None:
    """
    Modo dry-run: procesa mensaje sin red.
    """
    reply = route_text_message(message)
    print(f"[DRY-RUN] Message: {message}")
    print(f"[DRY-RUN] Reply: {reply}")


def live_loop(token: str) -> None:
    """
    Polling loop contra Telegram Bot API.
    """
    print(f"[LIVE] Starting Telegram polling loop...")
    print(f"[LIVE] Press Ctrl+C to stop")

    offset = None

    try:
        while True:
            updates = get_updates(token, offset=offset)

            for update in updates:
                update_id = update.get("update_id")
                message = update.get("message")

                if message:
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    document = message.get("document")

                    if chat_id and document:
                        file_id = document.get("file_id", "")
                        file_name = document.get("file_name", "")
                        print(f"[DOC] chat_id={chat_id}, file={file_name[:80]}...")
                        doc_result = handle_document(token, file_id, file_name, chat_id)
                        reply = doc_result.text
                        success = send_message(token, chat_id, reply)
                        if success:
                            print(f"[SENT] Reply sent to {chat_id}")
                        else:
                            print(f"[ERROR] Failed to send reply to {chat_id}")
                    elif chat_id and text:
                        print(f"[MSG] chat_id={chat_id}, text={text[:50]}...")
                        reply = route_text_message(text)
                        success = send_message(token, chat_id, reply)
                        if success:
                            print(f"[SENT] Reply sent to {chat_id}")
                        else:
                            print(f"[ERROR] Failed to send reply to {chat_id}")
                # Actualizar offset para no reprocesar
                if update_id is not None:
                    offset = update_id + 1

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n[LIVE] Polling stopped by user")


def main() -> None:
    """
    CLI entry point.

    Modos:
    - --dry-run "mensaje": procesa sin red
    - (sin args): live mode con TELEGRAM_BOT_TOKEN
    """
    if "--dry-run" in sys.argv:
        index = sys.argv.index("--dry-run")
        message = sys.argv[index + 1] if (index + 1) < len(sys.argv) else ""
        dry_run(message)
        return

    # Live mode: requiere TELEGRAM_BOT_TOKEN
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(
            "[ERROR] TELEGRAM_BOT_TOKEN no está definido en el entorno.\n"
            "Uso:\n"
            '  - Dry-run: python -m pymia.telegram_bot_runtime --dry-run "mensaje"\n'
            "  - Live: TELEGRAM_BOT_TOKEN=<token> python -m pymia.telegram_bot_runtime",
            file=sys.stderr,
        )
        sys.exit(1)

    live_loop(token)


if __name__ == "__main__":
    main()

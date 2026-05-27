# -*- coding: utf-8 -*-
"""
Session builder for the PymIA Telegram Bridge.

Responsibilities:
- Build TelegramSession from chat_id and user_id
- Derive tenant_id, session_key from Telegram context
"""

from pathlib import Path

from pymia.hermes.plugins.pymia_telegram_bridge.document_resolver import (
    TelegramSession,
)


def build_telegram_session(
    chat_id: str,
    user_id: str,
    repo_root: Path | str | None = None,
) -> TelegramSession:
    """
    Build a TelegramSession from Telegram context.

    Args:
        chat_id: Telegram chat ID (unique per conversation)
        user_id: Telegram user ID
        repo_root: Absolute path to PymIA repo root.
                   Defaults to E:\\BuenosPasos\\smartbridge\\PymIA

    Returns:
        TelegramSession with:
        - tenant_id = f"telegram:{chat_id}"
        - user_id = str(user_id)
        - session_key = f"telegram:{chat_id}/{user_id}"
        - chat_id = str(chat_id)
    """
    if repo_root is None:
        repo_root = Path(r"E:\BuenosPasos\smartbridge\PymIA")
    else:
        repo_root = Path(repo_root)

    tenant_id = f"telegram:{chat_id}"

    return TelegramSession(
        tenant_id=tenant_id,
        user_id=str(user_id),
        chat_id=str(chat_id),
        repo_root=repo_root,
    )


__all__ = ["build_telegram_session"]

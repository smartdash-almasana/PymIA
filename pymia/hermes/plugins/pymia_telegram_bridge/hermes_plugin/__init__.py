# -*- coding: utf-8 -*-
"""
PymIA Telegram Bridge — Hermes plugin wrapper (thin).

This file is installed to:
  C:\\Users\\PC\\AppData\\Local\\hermes\\profiles\\pymiafactory\\plugins\\pymia-telegram-bridge\\__init__.py

Responsibilities:
- Import logic from PymIA repo (versioned source of truth)
- Receive Hermes events (on_message, on_document)
- Call repo-side handler via handle_pre_gateway_dispatch
- Send reply via Hermes API
- NO business logic here (all logic is in repo)

Configuration:
- PYMIA_REPO_ROOT: env var or hardcoded path to PymIA repo
- Default: E:\\BuenosPasos\\smartbridge\\PymIA
"""

import os
import sys
from pathlib import Path

# Configure repo root
REPO_ROOT = os.environ.get("PYMIA_REPO_ROOT", r"E:\BuenosPasos\smartbridge\PymIA")
REPO_ROOT = Path(REPO_ROOT)

# Add repo to sys.path if not already there
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import repo-side logic
from pymia.hermes.plugins.pymia_telegram_bridge.plugin_wrapper import (
    handle_pre_gateway_dispatch,
)


def on_message(hermes_context):
    """
    Hermes hook: on_message

    Args:
        hermes_context: Hermes context object with:
            - message_text: str
            - chat_id: str
            - user_id: str
            - tenant_id: str
            - reply(text: str): method to send reply

    Flow:
        1. Build event dict from hermes_context
        2. Call handle_pre_gateway_dispatch
        3. If handled, send reply and skip gateway
        4. If not handled, let Hermes continue normal flow
    """
    event = {
        "message_text": hermes_context.message_text,
        "chat_id": hermes_context.chat_id,
        "user_id": hermes_context.user_id,
    }

    result = handle_pre_gateway_dispatch(
        event=event,
        adapter=None,
        repo_root=REPO_ROOT,
    )

    if result["handled"]:
        hermes_context.reply(result["reply_text"])
        # Skip gateway if handled
        if hasattr(hermes_context, "skip_gateway"):
            hermes_context.skip_gateway = result["skip_gateway"]


def on_document(hermes_context):
    """
    Hermes hook: on_document

    Args:
        hermes_context: Hermes context object with:
            - document_path: str (path to cached document)
            - file_name: str (original file name)
            - chat_id: str
            - user_id: str
            - tenant_id: str
            - reply(text: str): method to send reply

    Flow:
        1. Build event dict from hermes_context
        2. Call handle_pre_gateway_dispatch
        3. Send reply with confirmation
        4. Skip gateway (document caching is handled here)
    """
    event = {
        "document_path": hermes_context.document_path,
        "file_name": hermes_context.file_name,
        "chat_id": hermes_context.chat_id,
        "user_id": hermes_context.user_id,
    }

    result = handle_pre_gateway_dispatch(
        event=event,
        adapter=None,
        repo_root=REPO_ROOT,
    )

    if result["handled"]:
        hermes_context.reply(result["reply_text"])
        # Skip gateway if handled
        if hasattr(hermes_context, "skip_gateway"):
            hermes_context.skip_gateway = result["skip_gateway"]


__all__ = ["on_message", "on_document"]

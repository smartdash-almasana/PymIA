# -*- coding: utf-8 -*-
"""
PymIA Telegram Bridge — repo-side implementation.

This module contains the core logic for bridging Telegram messages
to PymIA's conversa-engine and microservice dispatcher.

Responsibilities:
- Session building (tenant_id, user_id, chat_id)
- Document caching and resolution
- Intent routing (text vs Excel analysis)
- Excel microservice dispatch

Usage:
    from pymia.hermes.plugins.pymia_telegram_bridge import (
        build_telegram_session,
        remember_latest_document,
        resolve_latest_excel,
        should_route_to_excel_microservice,
        route_text_message,
    )
"""

from pymia.hermes.plugins.pymia_telegram_bridge.config import (
    TELEGRAM_DOCUMENTS_DIR,
    INTENT_KEYWORDS,
)
from pymia.hermes.plugins.pymia_telegram_bridge.document_resolver import (
    TelegramSession,
    DocumentRecord,
    ExcelRef,
    remember_latest_document,
    resolve_latest_excel,
)
from pymia.hermes.plugins.pymia_telegram_bridge.plugin_wrapper import (
    handle_pre_gateway_dispatch,
)

__all__ = [
    "TELEGRAM_DOCUMENTS_DIR",
    "INTENT_KEYWORDS",
    "TelegramSession",
    "DocumentRecord",
    "ExcelRef",
    "remember_latest_document",
    "resolve_latest_excel",
    "handle_pre_gateway_dispatch",
]

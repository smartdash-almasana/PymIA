# -*- coding: utf-8 -*-
"""
Plugin wrapper for pre-gateway dispatch.

This module provides a high-level function that orchestrates:
- Session building
- Document resolution
- Intent routing
- Excel analysis handling

It is designed to be called by the Hermes plugin wrapper before
dispatching to the gateway, allowing the bridge to intercept and
handle Excel analysis requests directly.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from pymia.hermes.plugins.pymia_telegram_bridge.session_builder import (
    build_telegram_session,
)
from pymia.hermes.plugins.pymia_telegram_bridge.document_resolver import (
    resolve_latest_excel,
    remember_latest_document,
)
from pymia.hermes.plugins.pymia_telegram_bridge.intent_router import (
    should_route_to_excel_microservice,
)
from pymia.hermes.plugins.pymia_telegram_bridge.excel_handler import (
    process_excel_analysis_request,
)

logger = logging.getLogger(__name__)


def handle_pre_gateway_dispatch(
    event: Dict[str, Any],
    adapter: Optional[Any] = None,
    repo_root: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Handle pre-gateway dispatch for Telegram messages.

    This function is called by the Hermes plugin before dispatching to the gateway.
    It checks if the message should be routed to the Excel microservice and handles
    it directly if so, otherwise returns not_handled to allow normal gateway flow.

    Args:
        event: Dict with event data:
            - message_text: str (required)
            - chat_id: str (required)
            - user_id: str (required)
            - document_path: str (optional, for on_document events)
            - file_name: str (optional, for on_document events)
        adapter: Optional Hermes adapter (not used in current implementation)
        repo_root: Absolute path to PymIA repo root

    Returns:
        Dict with:
            - handled: bool (True if this function handled the event)
            - reply_text: str (text to send back, empty if not handled)
            - status: str ("EXECUTED", "BLOCKED", "FAILED", or "NOT_HANDLED")
            - skip_gateway: bool (True if gateway should be skipped)

    Examples:
        >>> event = {
        ...     "message_text": "Analizá rentabilidad marzo abril mayo",
        ...     "chat_id": "123456",
        ...     "user_id": "789",
        ... }
        >>> result = handle_pre_gateway_dispatch(event)
        >>> result["handled"]
        True
        >>> result["status"]
        "EXECUTED"

    Logs:
        [pymia.bridge] event_type=... chat_id=... user_id=... handled=... status=...
    """
    message_text = event.get("message_text", "")
    chat_id = event.get("chat_id", "")
    user_id = event.get("user_id", "")
    document_path = event.get("document_path")
    file_name = event.get("file_name")

    # Determine event type
    if document_path and file_name:
        event_type = "on_document"
    elif message_text:
        event_type = "on_message"
    else:
        logger.warning(
            "[pymia.bridge] event_type=unknown chat_id=%s user_id=%s reason=no_message_or_document route=fallback",
            chat_id,
            user_id,
        )
        return {
            "handled": True,
            "reply_text": "No entendí el mensaje. ¿Podés reformular?",
            "status": "FALLBACK",
            "skip_gateway": True,
            "route": "fallback",
        }

    # Build session
    session = build_telegram_session(
        chat_id=chat_id,
        user_id=user_id,
        repo_root=repo_root,
    )

    # Handle on_document event
    if event_type == "on_document":
        try:
            source_path = Path(document_path)
            record = remember_latest_document(
                session=session,
                source_path=source_path,
                file_name=file_name,
            )
            logger.info(
                "[pymia.bridge] event_type=on_document chat_id=%s user_id=%s handled=true status=CACHED",
                chat_id,
                user_id,
            )
            return {
                "handled": True,
                "reply_text": f"Recibí {file_name}.",
                "status": "CACHED",
                "skip_gateway": True,
            }
        except Exception as exc:
            logger.error(
                "[pymia.bridge] event_type=on_document chat_id=%s user_id=%s handled=true status=FAILED error=%s",
                chat_id,
                user_id,
                exc,
            )
            return {
                "handled": True,
                "reply_text": f"Error al guardar {file_name}: {type(exc).__name__}",
                "status": "FAILED",
                "skip_gateway": True,
            }

    # Handle on_message event
    # Resolve latest Excel
    excel_ref = resolve_latest_excel(session)
    latest_excel_exists = excel_ref is not None and excel_ref.exists

    # Check if should route to Excel microservice
    should_route = should_route_to_excel_microservice(
        message_text=message_text,
        latest_excel_exists=latest_excel_exists,
    )

    if not should_route:
        logger.info(
            "[pymia.bridge] event_type=on_message chat_id=%s user_id=%s handled=true status=FALLBACK route=fallback",
            chat_id,
            user_id,
        )
        return {
            "handled": True,
            "reply_text": "Para ayudarte necesito entender mejor el problema operativo. ¿Querés revisar ventas, costos, stock, caja o un Excel?",
            "status": "FALLBACK",
            "skip_gateway": True,
            "route": "fallback",
        }

    # Route to Excel microservice
    try:
        result = process_excel_analysis_request(
            file_path=excel_ref.path,
            tenant_id=session.tenant_id,
            user_id=session.user_id,
            message_text=message_text,
        )
        logger.info(
            "[pymia.bridge] event_type=on_message chat_id=%s user_id=%s handled=true status=%s findings_count=%d",
            chat_id,
            user_id,
            result.status,
            result.findings_count,
        )
        return {
            "handled": True,
            "reply_text": result.reply_text,
            "status": result.status,
            "skip_gateway": True,
        }
    except Exception as exc:
        logger.error(
            "[pymia.bridge] event_type=on_message chat_id=%s user_id=%s handled=true status=FAILED error=%s",
            chat_id,
            user_id,
            exc,
        )
        return {
            "handled": True,
            "reply_text": f"Error al procesar el análisis: {type(exc).__name__}",
            "status": "FAILED",
            "skip_gateway": True,
        }


__all__ = ["handle_pre_gateway_dispatch"]

from __future__ import annotations

import os
from typing import Any

FAIL_OPEN_REPLY = "No pude procesar el mensaje en este momento."

_ADAPTER = None
_SUPERMEMORY_CLIENT = None
_SUPERMEMORY_CLIENT_READY = False
_PROGRESSIVE_CONTEXT_BY_SESSION: dict[str, Any] = {}
_TURN_INDEX_BY_SESSION: dict[str, int] = {}


def _get_hermes_adapter():
    global _ADAPTER
    if _ADAPTER is not None:
        return _ADAPTER
    from pymia.hermes.adapter import HermesAdapter

    _ADAPTER = HermesAdapter()
    return _ADAPTER


def _get_supermemory_recall_client():
    global _SUPERMEMORY_CLIENT, _SUPERMEMORY_CLIENT_READY
    if _SUPERMEMORY_CLIENT_READY:
        return _SUPERMEMORY_CLIENT
    _SUPERMEMORY_CLIENT_READY = True
    if not os.environ.get("SUPERMEMORY_API_KEY"):
        return None
    try:
        from pymia.smartpyme.supermemory_tenant_recall import (
            SupermemoryClientConfig,
            SupermemoryTenantRecallClient,
        )

        _SUPERMEMORY_CLIENT = SupermemoryTenantRecallClient(
            SupermemoryClientConfig.from_env()
        )
    except Exception:
        _SUPERMEMORY_CLIENT = None
    return _SUPERMEMORY_CLIENT


def _extract_message_text(update: Any) -> str:
    message = getattr(update, "message", None)
    text = getattr(message, "text", None)
    return text if isinstance(text, str) else ""


def _extract_chat_id(update: Any) -> str:
    chat = getattr(update, "effective_chat", None)
    chat_id = getattr(chat, "id", None)
    return str(chat_id) if chat_id is not None else "unknown_chat"


def _extract_user_id(update: Any) -> str:
    user = getattr(update, "effective_user", None)
    user_id = getattr(user, "id", None)
    return str(user_id) if user_id is not None else "unknown_user"


def _build_session_key(chat_id: str, user_id: str) -> str:
    return f"telegram:{chat_id}:{user_id}"


def _process_telegram_message(*, tenant_id: str, user_id: str, session_key: str, message_text: str) -> str:
    from pymia.hermes.adapter import HermesInput
    from pymia.smartpyme.supermemory_recall_integration import (
        RecallBeforeReplyInput,
        run_recall_before_reply,
    )

    previous_context = _PROGRESSIVE_CONTEXT_BY_SESSION.get(session_key)
    turn_index = _TURN_INDEX_BY_SESSION.get(session_key, 0)
    text_for_adapter = message_text

    client = _get_supermemory_recall_client()
    if client is not None:
        try:
            recall_output = run_recall_before_reply(
                RecallBeforeReplyInput(
                    tenant_id=tenant_id,
                    session_key=session_key,
                    user_message=message_text,
                    turn_index=turn_index,
                ),
                client=client,
            )
            text_for_adapter = recall_output.augmented_message
        except Exception:
            text_for_adapter = message_text

    adapter = _get_hermes_adapter()
    output = adapter.handle(
        HermesInput(
            tenant_id=tenant_id,
            channel="telegram",
            message_text=text_for_adapter,
            metadata={"session_key": session_key},
            previous_progressive_context=previous_context,
        )
    )

    _TURN_INDEX_BY_SESSION[session_key] = turn_index + 1
    if output.payload.progressive_context is not None:
        _PROGRESSIVE_CONTEXT_BY_SESSION[session_key] = output.payload.progressive_context

    if output.status == "ok" and output.reply_text:
        return output.reply_text
    return FAIL_OPEN_REPLY


def route_telegram_text_message(*, telegram_user_id: Any, chat_id: Any, text: str) -> str:
    tenant_id = "telegram"
    user_id = str(telegram_user_id)
    session_key = f"telegram:{chat_id}:{telegram_user_id}"

    try:
        return _process_telegram_message(
            tenant_id=tenant_id,
            user_id=user_id,
            session_key=session_key,
            message_text=text,
        )
    except Exception:
        return FAIL_OPEN_REPLY


async def handle_text_update(update: Any, context: Any) -> str:
    text = _extract_message_text(update)
    chat_id = _extract_chat_id(update)
    user_id = _extract_user_id(update)
    session_key = _build_session_key(chat_id, user_id)

    if not text.strip():
        reply = FAIL_OPEN_REPLY
    else:
        try:
            reply = _process_telegram_message(
                tenant_id="telegram",
                user_id=user_id,
                session_key=session_key,
                message_text=text,
            )
        except Exception:
            reply = FAIL_OPEN_REPLY

    bot = getattr(context, "bot", None)
    if bot is not None and hasattr(bot, "send_message"):
        await bot.send_message(chat_id=chat_id, text=reply)
    return reply

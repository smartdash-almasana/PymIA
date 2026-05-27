# -*- coding: utf-8 -*-
"""
Intent router for the PymIA Telegram Bridge.

Responsibilities:
- Detect if a message should be routed to the Excel microservice
- Match intent keywords from user messages
"""

import logging
from typing import Optional

from pymia.hermes.plugins.pymia_telegram_bridge.config import INTENT_KEYWORDS

logger = logging.getLogger(__name__)


def should_route_to_excel_microservice(
    message_text: str,
    latest_excel_exists: bool,
) -> bool:
    """
    Determine if a message should be routed to the Excel microservice.

    Args:
        message_text: User message text (lowercase normalization applied internally)
        latest_excel_exists: Whether an Excel file exists for this chat_id

    Returns:
        True if:
        - latest_excel_exists is True AND
        - message_text contains ≥1 intent keyword

    Intent keywords (from config.py):
    - analizá, analizar, rentabilidad, ingresos, gastos, comparación,
      marzo, abril, mayo, hallazgos, diferencias, cuantif

    Logs:
        [pymia.intent_router] message_text=... excel_exists=... match_keywords=... route=...
    """
    if not latest_excel_exists:
        logger.info(
            "[pymia.intent_router] message_text=%r excel_exists=false match_keywords=[] route=false",
            message_text,
        )
        return False

    # Normalize message to lowercase for matching
    text_lower = message_text.lower()

    # Find matching keywords
    matched_keywords = [kw for kw in INTENT_KEYWORDS if kw in text_lower]

    if not matched_keywords:
        logger.info(
            "[pymia.intent_router] message_text=%r excel_exists=true match_keywords=[] route=false",
            message_text,
        )
        return False

    logger.info(
        "[pymia.intent_router] message_text=%r excel_exists=true match_keywords=%r route=true",
        message_text,
        matched_keywords,
    )
    return True


__all__ = ["should_route_to_excel_microservice"]

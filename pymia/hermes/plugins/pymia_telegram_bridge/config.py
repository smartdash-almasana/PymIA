# -*- coding: utf-8 -*-
"""
Configuration constants for the PymIA Telegram Bridge.

These constants define paths, keywords, and defaults used throughout
the bridge logic.
"""

from pathlib import Path
from typing import Tuple


# Directory where Telegram documents are cached
# Relative to repo root (E:\BuenosPasos\smartbridge\PymIA)
TELEGRAM_DOCUMENTS_DIR = ".runtime/telegram_documents"

# Supported Excel file extensions
EXCEL_EXTENSIONS: Tuple[str, ...] = (".xlsx", ".xls", ".csv")

# Intent keywords for Excel analysis routing
# If message contains ≥1 of these AND an Excel exists, route to Excel microservice
INTENT_KEYWORDS: Tuple[str, ...] = (
    "analizá",
    "analizar",
    "rentabilidad",
    "ingresos",
    "gastos",
    "comparación",
    "marzo",
    "abril",
    "mayo",
    "hallazgos",
    "diferencias",
    "cuantif",
)

# Default tenant and user IDs (used when not provided by Hermes context)
DEFAULT_TENANT_ID = "telegram:42"
DEFAULT_USER_ID = "42"

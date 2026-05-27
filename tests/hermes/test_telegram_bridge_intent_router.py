# -*- coding: utf-8 -*-
"""
Unit tests for pymia.hermes.plugins.pymia_telegram_bridge.intent_router.

These tests validate intent detection for Excel analysis routing
without touching AppData, Hermes, or Telegram.
"""

import pytest

from pymia.hermes.plugins.pymia_telegram_bridge.intent_router import (
    should_route_to_excel_microservice,
)


def test_route_true_when_excel_exists_and_keyword_match():
    """should_route_to_excel_microservice returns True if Excel exists and keyword matches."""
    message = "Analizá rentabilidad, ingresos, gastos y comparación marzo abril mayo."
    assert should_route_to_excel_microservice(message, latest_excel_exists=True) is True


def test_route_true_with_single_keyword():
    """should_route_to_excel_microservice returns True with ≥1 keyword."""
    assert should_route_to_excel_microservice("hallazgos", latest_excel_exists=True) is True
    assert should_route_to_excel_microservice("analizar", latest_excel_exists=True) is True
    assert should_route_to_excel_microservice("diferencias cuantificadas", latest_excel_exists=True) is True


def test_route_false_when_no_excel():
    """should_route_to_excel_microservice returns False if no Excel exists."""
    message = "Analizá rentabilidad, ingresos, gastos y comparación marzo abril mayo."
    assert should_route_to_excel_microservice(message, latest_excel_exists=False) is False


def test_route_false_when_no_keyword_match():
    """should_route_to_excel_microservice returns False if no keyword matches."""
    message = "Hola, ¿cómo estás?"
    assert should_route_to_excel_microservice(message, latest_excel_exists=True) is False


def test_route_false_when_no_excel_and_no_keyword():
    """should_route_to_excel_microservice returns False if no Excel and no keyword."""
    message = "Hola, ¿cómo estás?"
    assert should_route_to_excel_microservice(message, latest_excel_exists=False) is False


def test_route_case_insensitive():
    """should_route_to_excel_microservice matches keywords case-insensitively."""
    assert should_route_to_excel_microservice("ANALIZÁ RENTABILIDAD", latest_excel_exists=True) is True
    assert should_route_to_excel_microservice("Ingresos Y Gastos", latest_excel_exists=True) is True
    assert should_route_to_excel_microservice("MARZO abril MAYO", latest_excel_exists=True) is True


def test_route_partial_match():
    """should_route_to_excel_microservice matches partial keywords."""
    # "cuantif" matches "cuantificadas"
    assert should_route_to_excel_microservice("dame diferencias cuantificadas", latest_excel_exists=True) is True
    # "comparación" matches
    assert should_route_to_excel_microservice("necesito comparación de meses", latest_excel_exists=True) is True


def test_route_empty_message():
    """should_route_to_excel_microservice returns False for empty message."""
    assert should_route_to_excel_microservice("", latest_excel_exists=True) is False
    assert should_route_to_excel_microservice("   ", latest_excel_exists=True) is False

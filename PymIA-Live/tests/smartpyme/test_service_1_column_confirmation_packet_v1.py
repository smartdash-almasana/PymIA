from __future__ import annotations

import sys

from pymia.smartpyme.service_1_column_confirmation_packet_v1 import (
    build_service_1_column_confirmation_packet_v1,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_detected_structure(sheets: list[dict]) -> dict:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "workbook": {
            "sheet_count": len(sheets),
            "sheets": sheets,
        },
        "warnings": [],
        "runtime_authorized": False,
    }


# ---------------------------------------------------------------------------
# 1. Genera preguntas desde headers detectados
# ---------------------------------------------------------------------------

def test_generates_questions_from_detected_headers() -> None:
    """A non-empty header list produces one question per header."""
    detected = _build_detected_structure(
        [
            {
                "name": "Ventas",
                "headers": ["Fecha", "Producto", "Cantidad"],
            }
        ]
    )

    packet = build_service_1_column_confirmation_packet_v1(detected)

    assert packet["service_name"] == "SERVICE_1"
    assert packet["packet_type"] == "COLUMN_CONFIRMATION"
    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert len(packet["questions"]) == 3

    first = packet["questions"][0]
    assert first["question_id"] == "col_confirm_001"
    assert first["sheet_name"] == "Ventas"
    assert first["column_name"] == "Fecha"
    assert "Fecha" in first["question"]
    assert first["answer_type"] == "owner_text"
    assert first["required"] is True


# ---------------------------------------------------------------------------
# 2. Máximo 12 preguntas
# ---------------------------------------------------------------------------

def test_limits_questions_to_twelve() -> None:
    """No more than 12 questions are generated, even with many headers."""
    headers = [f"Columna_{i}" for i in range(20)]
    detected = _build_detected_structure(
        [
            {
                "name": "Hoja1",
                "headers": headers,
            }
        ]
    )

    packet = build_service_1_column_confirmation_packet_v1(detected)

    assert len(packet["questions"]) == 12
    assert packet["questions"][-1]["question_id"] == "col_confirm_012"


# ---------------------------------------------------------------------------
# 3. runtime_authorized siempre false
# ---------------------------------------------------------------------------

def test_runtime_authorized_is_always_false() -> None:
    """Column confirmation never authorizes runtime execution."""
    detected = _build_detected_structure(
        [
            {
                "name": "Ventas",
                "headers": ["Fecha", "Monto"],
            }
        ]
    )

    packet = build_service_1_column_confirmation_packet_v1(detected)

    assert packet["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 4. No modifica detected_structure original
# ---------------------------------------------------------------------------

def test_does_not_mutate_input_structure() -> None:
    """The function must not mutate the input detected_structure dict."""
    detected = _build_detected_structure(
        [
            {
                "name": "Ventas",
                "headers": ["Fecha"],
            }
        ]
    )
    original = detected.copy()

    build_service_1_column_confirmation_packet_v1(detected)

    assert detected == original


# ---------------------------------------------------------------------------
# 5. Si no hay headers, status NO_COLUMNS_DETECTED
# ---------------------------------------------------------------------------

def test_no_headers_yields_no_columns_detected() -> None:
    """Empty or blank headers result in NO_COLUMNS_DETECTED status."""
    detected = _build_detected_structure(
        [
            {
                "name": "HojaVacia",
                "headers": ["", "   "],
            }
        ]
    )

    packet = build_service_1_column_confirmation_packet_v1(detected)

    assert packet["status"] == "NO_COLUMNS_DETECTED"
    assert packet["questions"] == []
    assert len(packet["warnings"]) == 1


# ---------------------------------------------------------------------------
# 6. No expone claves prohibidas
# ---------------------------------------------------------------------------

def test_packet_does_not_contain_forbidden_keys() -> None:
    """Packet must not contain diagnostic/recommendation/result keys."""
    detected = _build_detected_structure(
        [
            {
                "name": "Ventas",
                "headers": ["Fecha", "Monto"],
            }
        ]
    )

    packet = build_service_1_column_confirmation_packet_v1(detected)
    packet_str = str(packet).lower()

    forbidden_terms = [
        "diagnosis",
        "recommendation",
        "accounting_result",
        "final_result",
        "profit",
        "margin",
    ]
    for term in forbidden_terms:
        assert term not in packet_str, f"packet must not contain {term}"


# ---------------------------------------------------------------------------
# 7. No importa módulos prohibidos
# ---------------------------------------------------------------------------

def test_module_does_not_import_forbidden_modules() -> None:
    """Loading this module must not import pipeline, FSM, reentry, LLM modules."""
    forbidden_modules = [
        "pymia.smartpyme.vertical_pipeline",
        "pymia.smartpyme.service_1_pipeline_v1",
        "pymia.smartpyme.service_1_fsm_decision_patch_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_v1",
        "pymia.application.vertical_pipeline",
        "tools.document_ingestion",
        "openai",
        "chatbot",
    ]

    for mod in forbidden_modules:
        sys.modules.pop(mod, None)

    # Re-import to trigger module loading
    import importlib

    import pymia.smartpyme.service_1_column_confirmation_packet_v1 as cc_mod

    importlib.reload(cc_mod)

    for mod in forbidden_modules:
        assert mod not in sys.modules, f"Module must not import {mod}"

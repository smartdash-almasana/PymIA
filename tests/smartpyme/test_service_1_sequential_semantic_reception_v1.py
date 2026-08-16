from __future__ import annotations

from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
)


def _decision(decision_id: str, column: str) -> dict:
    return {
        "decision_id": decision_id,
        "column_ref": f"Ventas.{column}",
        "column_name": column,
        "proposed_label": column,
        "proposed_meaning": column,
        "confidence": 0.5,
    }


def test_semantic_corroboration_renders_only_one_pending_question() -> None:
    app = Service1SemanticReceptionWebApplicationV1()
    state = app.session("s1")
    state.ingestion_output = {"case_id": "c1"}
    state.semantic_assistance_state = {"status": "PENDING"}
    state.semantic_questions = [
        _decision("d1", "Hora"),
        _decision("d2", "MetodoPago"),
        _decision("d3", "Ciudad"),
    ]

    status, page = app._render_one_pending_question(session_id="s1") or (0, "")

    assert status == 200
    assert len(state.semantic_questions) == 1
    assert state.semantic_questions[0]["decision_id"] == "d1"
    assert "Hora" in page
    assert "MetodoPago" not in page
    assert "Ciudad" not in page


def test_unit_corroboration_renders_only_one_pending_question() -> None:
    app = Service1SemanticReceptionWebApplicationV1()
    state = app.session("s2")
    state.ingestion_output = {"case_id": "c2"}
    state.semantic_assistance_state = {"status": "PENDING"}
    state.semantic_questions = [
        {
            "question_kind": "UNIT_MEANING",
            "question_id": "u1",
            "column_ref": "Ventas.Descuento",
            "column_name": "Descuento",
            "sample_values": [0, 0.1, 0.2],
            "allowed_unit_kinds": ["DISCOUNT_FRACTION_0_1"],
        },
        {
            "question_kind": "UNIT_MEANING",
            "question_id": "u2",
            "column_ref": "Ventas.Otra",
            "column_name": "Otra",
            "sample_values": [1, 2],
            "allowed_unit_kinds": ["DISCOUNT_FRACTION_0_1"],
        },
    ]

    status, page = app._render_one_pending_question(session_id="s2") or (0, "")

    assert status == 200
    assert len(state.semantic_questions) == 1
    assert state.semantic_questions[0]["question_id"] == "u1"
    assert "Descuento" in page
    assert "Otra" not in page

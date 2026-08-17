from __future__ import annotations

from types import SimpleNamespace

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
    assert len(state.semantic_questions) == 3
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
    assert len(state.semantic_questions) == 2
    assert state.semantic_questions[0]["question_id"] == "u1"
    assert "Descuento" in page
    assert "Otra" not in page


def test_sequential_semantic_reception_accumulates_prior_owner_responses(monkeypatch) -> None:
    import pymia.smartpyme.service_1_assisted_web_v1 as base

    app = Service1SemanticReceptionWebApplicationV1()
    state = app.session("s3")
    state.ingestion_output = {"case_id": "c3", "filename": "ventas.xlsx"}
    state.selected_launch_review = "net_margin_real"
    d1 = {
        "decision_id": "d1",
        "column_refs": ["Ventas.Cantidad"],
        "presentation_text": "PymIA interpreta Cantidad como cantidad vendida. ¿Es correcto?",
    }
    d2 = {
        "decision_id": "d2",
        "column_refs": ["Ventas.Precio"],
        "presentation_text": "PymIA interpreta Precio como precio de venta. ¿Es correcto?",
    }
    assistance = {
        "status": "OWNER_DIALOGUE_REQUIRED",
        "case_id": "c3",
        "requested_capability": "net_margin_real",
        "semantic_scope_capabilities": [],
        "dialogue_plan": {"decisions": [d1, d2]},
        "workbook_profile": {"columns": []},
        "validated_packet": {"decisions": []},
    }
    state.semantic_assistance_state = assistance
    state.semantic_questions = [d1, d2]

    calls: list[list[dict]] = []

    def fake_run_product_root(**kwargs):
        calls.append([dict(item) for item in kwargs.get("semantic_dialogue_responses") or []])
        return {
            "status": base.STATUS_NEEDS_OWNER,
            "owner_questions": [d2],
            "semantic_assistance_state": assistance,
        }

    monkeypatch.setattr(base, "_run_product_root", fake_run_product_root)

    status1, page1 = app.confirm_meanings(
        session_id="s3",
        fields={"action_d1": "ACCEPT"},
    )
    assert status1 == 200
    assert "Precio" in page1
    assert calls[0] == [{"decision_id": "d1", "action": "ACCEPT"}]

    status2, _page2 = app.confirm_meanings(
        session_id="s3",
        fields={"action_d2": "ACCEPT"},
    )
    assert status2 == 200
    assert calls[1] == [
        {"decision_id": "d1", "action": "ACCEPT"},
        {"decision_id": "d2", "action": "ACCEPT"},
    ]


def test_semantic_assist_surfaces_bounded_revision_without_confirming() -> None:
    class _Provider:
        def __call__(self, _payload):
            raise AssertionError("semantic classification should not run in this test")

        def assist(self, _payload):
            return {
                "response_text": "Por tu explicación, parece cantidad vendida. Te la propongo para que la revises.",
                "suggested_semantic_role": "quantity",
                "suggested_variable_name": "volume_sold",
                "suggestion_reason": "Owner described sold units.",
            }

    app = Service1SemanticReceptionWebApplicationV1(semantic_provider=_Provider())
    state = app.session("s4")
    decision = {
        "decision_id": "dialogue:atomic:p-qty",
        "proposal_refs": ["p-qty"],
        "column_refs": ["Ventas.Unidades"],
        "relationship_refs": [],
        "presentation_text": "PymIA interpreta Unidades como stock entrante. ¿Es correcto?",
        "materiality_reason": "La columna es material.",
    }
    state.ingestion_output = {"case_id": "c4"}
    state.semantic_questions = [decision]
    state.semantic_assistance_state = {
        "status": "OWNER_DIALOGUE_REQUIRED",
        "dialogue_plan": {"decisions": [decision]},
        "workbook_profile": {
            "columns": [
                {
                    "column_ref": "Ventas.Unidades",
                    "sheet_name": "Ventas",
                    "column_name": "Unidades",
                    "sample_values": [1, 2, 3],
                    "inferred_type": "integer",
                }
            ]
        },
        "validated_packet": {"decisions": []},
        "context": SimpleNamespace(
            deterministic_hypotheses=(
                {
                    "semantic_role": "quantity",
                    "variable_name": "volume_sold",
                    "candidate_meanings": [],
                },
            )
        ),
    }

    status, page = app.semantic_assist(
        session_id="s4",
        fields={
            "decision_id": "dialogue:atomic:p-qty",
            "assistant_message": "Son las unidades que vendimos en esa operación.",
        },
    )

    assert status == 200
    assert state.semantic_dialogue_responses == {}
    assert state.semantic_chat_suggestions["dialogue:atomic:p-qty"] == {
        "semantic_role": "quantity",
        "variable_name": "volume_sold",
        "reason": "Owner described sold units.",
        "owner_text": "Son las unidades que vendimos en esa operación.",
    }
    assert "Propuesta revisada" in page
    assert "Usar esta propuesta y revisarla" in page
    assert "confirmado" in page.lower()

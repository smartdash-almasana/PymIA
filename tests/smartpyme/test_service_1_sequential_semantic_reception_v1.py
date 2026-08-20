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
    assert "No tomes en cuenta esta columna para el análisis que necesito" in page
    assert "Asistente semántico con LLM" in page
    assert "Hablá con PymIA" in page
    assert "MetodoPago" not in page
    assert "Ciudad" not in page


def test_unresolved_material_ambiguity_cannot_offer_accept_or_reach_sem5() -> None:
    import pymia.smartpyme.service_1_assisted_web_v1 as base

    app = Service1SemanticReceptionWebApplicationV1()
    state = app.session("s-unresolved")
    state.ingestion_output = {"case_id": "c-unresolved", "filename": "cafeteria_abc.xlsx"}
    state.selected_launch_review = "net_margin_real"
    decision = {
        "decision_id": "dialogue:atomic:amb-discount",
        "decision_kind": "CONFLICT",
        "proposal_refs": ["amb-discount"],
        "column_refs": ["Ventas.Descuento"],
        "relationship_refs": [],
        "presentation_text": "Hay evidencia incompatible sobre `Ventas.Descuento`. Necesito que confirmes cómo debe interpretarse.",
        "materiality_reason": "La interpretación necesita confirmación empresarial explícita.",
    }
    assistance = {
        "status": "OWNER_DIALOGUE_REQUIRED",
        "case_id": "c-unresolved",
        "requested_capability": "net_margin_real",
        "dialogue_plan": {"decisions": [decision]},
        "workbook_profile": {
            "columns": [
                {
                    "column_ref": "Ventas.Descuento",
                    "sheet_name": "Ventas",
                    "column_name": "Descuento",
                    "sample_values": [0, 0.1, 0.15, 0.05],
                    "inferred_type": "number",
                }
            ]
        },
        "validated_packet": {
            "decisions": [
                {
                    "decision_id": "amb-discount",
                    "source_kind": "MATERIAL_AMBIGUITY",
                    "status": "MATERIAL_AMBIGUOUS",
                    "target_refs": ["Ventas.Descuento"],
                    "semantic_role": None,
                    "variable_name": None,
                    "relationship_type": None,
                }
            ]
        },
    }
    state.semantic_assistance_state = assistance
    state.semantic_questions = [decision]
    state.semantic_dialogue_responses[decision["decision_id"]] = {
        "decision_id": decision["decision_id"],
        "action": "ACCEPT",
    }

    status, page = app._render_one_pending_question(session_id="s-unresolved") or (0, "")
    assert status == 200
    assert "Sí, es correcto: eso significa" not in page
    assert "Todavía no hay una interpretación concreta para confirmar" in page
    assert 'value="CORRECT" required' in page

    def forbidden_product_root(**_kwargs):
        raise AssertionError("unresolved ACCEPT must not reach product root or SEM-5")

    monkeypatch = __import__("pytest").MonkeyPatch()
    monkeypatch.setattr(base, "_run_product_root", forbidden_product_root)
    try:
        status, page = app.confirm_meanings(
            session_id="s-unresolved",
            fields={f"action_{decision['decision_id']}": "ACCEPT"},
        )
    finally:
        monkeypatch.undo()

    assert status == 200
    assert "BLOCK_OWNER_SEMANTIC_ACCEPTED_SEMANTICS_UNRESOLVED" not in page
    assert "Explicame con tus palabras" in page
    assert decision["decision_id"] not in state.semantic_dialogue_responses


def test_stale_unresolved_accept_is_dropped_before_product_reentry(monkeypatch) -> None:
    import pymia.smartpyme.service_1_assisted_web_v1 as base

    app = Service1SemanticReceptionWebApplicationV1()
    state = app.session("s-stale")
    state.ingestion_output = {"case_id": "c-stale", "filename": "cafeteria_abc.xlsx"}
    state.selected_launch_review = "net_margin_real"
    unresolved = {
        "decision_id": "dialogue:atomic:amb-discount",
        "proposal_refs": ["amb-discount"],
        "column_refs": ["Ventas.Descuento"],
        "relationship_refs": [],
        "presentation_text": "Hay evidencia incompatible sobre `Ventas.Descuento`.",
    }
    valid = {
        "decision_id": "dialogue:atomic:p-qty",
        "proposal_refs": ["p-qty"],
        "column_refs": ["Ventas.Cantidad"],
        "relationship_refs": [],
        "presentation_text": "PymIA interpreta `Cantidad` como la cantidad vendida o movida. ¿Es correcto?",
    }
    assistance = {
        "status": "OWNER_DIALOGUE_REQUIRED",
        "case_id": "c-stale",
        "requested_capability": "net_margin_real",
        "dialogue_plan": {"decisions": [unresolved, valid]},
        "workbook_profile": {"columns": []},
        "validated_packet": {
            "decisions": [
                {
                    "decision_id": "amb-discount",
                    "source_kind": "MATERIAL_AMBIGUITY",
                    "status": "MATERIAL_AMBIGUOUS",
                    "target_refs": ["Ventas.Descuento"],
                    "semantic_role": None,
                    "variable_name": None,
                    "relationship_type": None,
                },
                {
                    "decision_id": "p-qty",
                    "source_kind": "CONCEPT",
                    "status": "MATERIAL_CONFIDENT",
                    "target_refs": ["Ventas.Cantidad"],
                    "semantic_role": "quantity",
                    "variable_name": "volume_sold",
                    "relationship_type": None,
                },
            ]
        },
    }
    state.semantic_assistance_state = assistance
    state.semantic_questions = [valid]
    state.semantic_dialogue_responses[unresolved["decision_id"]] = {
        "decision_id": unresolved["decision_id"],
        "action": "ACCEPT",
    }
    captured: list[list[dict]] = []

    def fake_run_product_root(**kwargs):
        captured.append([dict(item) for item in kwargs.get("semantic_dialogue_responses") or []])
        return {
            "status": base.STATUS_NEEDS_OWNER,
            "owner_questions": [unresolved],
            "semantic_assistance_state": assistance,
        }

    monkeypatch.setattr(base, "_run_product_root", fake_run_product_root)

    status, _page = app.confirm_meanings(
        session_id="s-stale",
        fields={f"action_{valid['decision_id']}": "ACCEPT"},
    )

    assert status == 200
    assert captured == [[{"decision_id": valid["decision_id"], "action": "ACCEPT"}]]
    assert unresolved["decision_id"] not in state.semantic_dialogue_responses


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


def test_semantic_assist_conversation_mode_does_not_require_suggestion() -> None:
    class _Provider:
        def __call__(self, _payload):
            raise AssertionError("semantic classification should not run in this test")

        def assist(self, payload):
            assert payload["interaction_mode"] == "CONVERSATION"
            assert {ref for ref in payload["column_refs"]} == {"Ventas.Unidades"}
            return {
                "response_text": "La propuesta actual usa el contexto de stock entrante.",
                "suggested_semantic_role": None,
                "suggested_variable_name": None,
                "suggestion_reason": None,
            }

    app = Service1SemanticReceptionWebApplicationV1(semantic_provider=_Provider())
    state = app.session("s5")
    decision = {
        "decision_id": "dialogue:atomic:p-qty",
        "proposal_refs": ["p-qty"],
        "column_refs": ["Ventas.Unidades"],
        "relationship_refs": [],
        "presentation_text": "PymIA interpreta Unidades como stock entrante. ¿Es correcto?",
        "materiality_reason": "La columna es material.",
    }
    state.ingestion_output = {"case_id": "c5"}
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
                    "sheet_name": "Ventas",
                    "column_name": "Unidades",
                    "semantic_role": "quantity",
                    "variable_name": "volume_sold",
                    "candidate_meanings": [],
                },
                {
                    "sheet_name": "Ventas",
                    "column_name": "Precio",
                    "semantic_role": "unit_sale_price",
                    "variable_name": "sale_price",
                    "candidate_meanings": [],
                },
            )
        ),
    }

    status, page = app.semantic_assist(
        session_id="s5",
        fields={
            "decision_id": "dialogue:atomic:p-qty",
            "assistant_message": "¿Por qué pensás que es stock entrante?",
        },
    )

    assert status == 200
    assert state.semantic_chat_suggestions == {}
    assert "Asistente semántico con LLM" in page
    assert "La propuesta actual usa el contexto de stock entrante." in page


def test_semantic_assist_correction_mode_accepts_only_current_column_pair() -> None:
    seen_payloads: list[dict] = []

    class _Provider:
        def __call__(self, _payload):
            raise AssertionError("semantic classification should not run in this test")

        def assist(self, payload):
            seen_payloads.append(payload)
            assert payload["interaction_mode"] == "CORRECTION"
            assert [ref for ref in payload["column_refs"]] == ["Ventas.Unidades"]
            # only the current column pair is offered; the Precio pair is excluded
            assert payload["allowed_role_variable_pairs"] == [
                {"semantic_role": "quantity", "variable_name": "volume_sold"},
            ]
            return {
                "response_text": "Por tu explicación, es cantidad vendida.",
                "suggested_semantic_role": "quantity",
                "suggested_variable_name": "volume_sold",
                "suggestion_reason": "Owner described sold units.",
            }

    app = Service1SemanticReceptionWebApplicationV1(semantic_provider=_Provider())
    state = app.session("s6")
    decision = {
        "decision_id": "dialogue:atomic:p-qty",
        "proposal_refs": ["p-qty"],
        "column_refs": ["Ventas.Unidades"],
        "relationship_refs": [],
        "presentation_text": "PymIA interpreta Unidades como stock entrante. ¿Es correcto?",
        "materiality_reason": "La columna es material.",
    }
    state.ingestion_output = {"case_id": "c6"}
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
                    "sheet_name": "Ventas",
                    "column_name": "Unidades",
                    "semantic_role": "quantity",
                    "variable_name": "volume_sold",
                    "candidate_meanings": [],
                },
                {
                    "sheet_name": "Ventas",
                    "column_name": "Precio",
                    "semantic_role": "unit_sale_price",
                    "variable_name": "sale_price",
                    "candidate_meanings": [],
                },
            )
        ),
    }

    status, page = app.semantic_assist(
        session_id="s6",
        fields={
            "decision_id": "dialogue:atomic:p-qty",
            "assistant_message": "Son las unidades vendidas en esa operación.",
            "correction_mode": "1",
        },
    )

    assert status == 200
    assert state.semantic_chat_suggestions["dialogue:atomic:p-qty"] == {
        "semantic_role": "quantity",
        "variable_name": "volume_sold",
        "reason": "Owner described sold units.",
        "owner_text": "Son las unidades vendidas en esa operación.",
    }
    assert "Propuesta revisada" in page


def test_semantic_assist_rejects_suggestion_from_other_column() -> None:
    class _Provider:
        def __call__(self, _payload):
            raise AssertionError("semantic classification should not run in this test")

        def assist(self, payload):
            # LLM proposes the Precio pair even though the visible column is Unidades
            return {
                "response_text": "Parece precio unitario.",
                "suggested_semantic_role": "unit_sale_price",
                "suggested_variable_name": "sale_price",
                "suggestion_reason": "Wrong column pair.",
            }

    app = Service1SemanticReceptionWebApplicationV1(semantic_provider=_Provider())
    state = app.session("s7")
    decision = {
        "decision_id": "dialogue:atomic:p-qty",
        "proposal_refs": ["p-qty"],
        "column_refs": ["Ventas.Unidades"],
        "relationship_refs": [],
        "presentation_text": "PymIA interpreta Unidades como stock entrante. ¿Es correcto?",
        "materiality_reason": "La columna es material.",
    }
    state.ingestion_output = {"case_id": "c7"}
    state.semantic_questions = [decision]
    state.semantic_assistance_state = {
        "status": "OWNER_DIALOGUE_REQUIRED",
        "dialogue_plan": {"decisions": [decision]},
        "workbook_profile": {"columns": []},
        "validated_packet": {"decisions": []},
        "context": SimpleNamespace(
            deterministic_hypotheses=(
                {
                    "sheet_name": "Ventas",
                    "column_name": "Unidades",
                    "semantic_role": "quantity",
                    "variable_name": "volume_sold",
                    "candidate_meanings": [],
                },
            )
        ),
    }

    status, page = app.semantic_assist(
        session_id="s7",
        fields={
            "decision_id": "dialogue:atomic:p-qty",
            "assistant_message": "Son unidades vendidas.",
            "correction_mode": "1",
        },
    )

    assert status == 200
    assert state.semantic_chat_suggestions == {}
    assert "Propuesta revisada" not in page


def test_semantic_assist_rejects_suggestion_outside_catalog() -> None:
    class _Provider:
        def __call__(self, _payload):
            raise AssertionError("semantic classification should not run in this test")

        def assist(self, payload):
            return {
                "response_text": "Es el costo total.",
                "suggested_semantic_role": "total_cost",
                "suggested_variable_name": "cost_total",
                "suggestion_reason": "Not in the allowed catalog.",
            }

    app = Service1SemanticReceptionWebApplicationV1(semantic_provider=_Provider())
    state = app.session("s8")
    decision = {
        "decision_id": "dialogue:atomic:p-qty",
        "proposal_refs": ["p-qty"],
        "column_refs": ["Ventas.Unidades"],
        "relationship_refs": [],
        "presentation_text": "PymIA interpreta Unidades como stock entrante. ¿Es correcto?",
        "materiality_reason": "La columna es material.",
    }
    state.ingestion_output = {"case_id": "c8"}
    state.semantic_questions = [decision]
    state.semantic_assistance_state = {
        "status": "OWNER_DIALOGUE_REQUIRED",
        "dialogue_plan": {"decisions": [decision]},
        "workbook_profile": {"columns": []},
        "validated_packet": {"decisions": []},
        "context": SimpleNamespace(
            deterministic_hypotheses=(
                {
                    "sheet_name": "Ventas",
                    "column_name": "Unidades",
                    "semantic_role": "quantity",
                    "variable_name": "volume_sold",
                    "candidate_meanings": [],
                },
            )
        ),
    }

    status, page = app.semantic_assist(
        session_id="s8",
        fields={
            "decision_id": "dialogue:atomic:p-qty",
            "assistant_message": "Es el costo total.",
            "correction_mode": "1",
        },
    )

    assert status == 200
    assert state.semantic_chat_suggestions == {}
    assert "Propuesta revisada" not in page


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
    assert "Revisar esta interpretación" in page
    assert "Owner described sold units." not in page
    assert "Interpretación técnica" not in page
    assert "confirmado" in page.lower()

from http import HTTPStatus

import pymia.smartpyme.service_1_assisted_web_v1 as web


def test_assisted_semantics_can_be_confirmed_before_selecting_analysis(monkeypatch, tmp_path) -> None:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path)
    state = app.session("session-1")
    state.ingestion_output = {"workbook_context": {"case_id": "case-1"}}
    state.semantic_assistance_state = {"status": "OWNER_REQUIRED"}
    state.semantic_questions = [
        {
            "decision_id": "dialogue:semantic-unit:1",
            "question_kind": "SEMANTIC_GROUP",
        }
    ]
    state.selected_launch_review = None

    calls = []

    def fake_product_root(**kwargs):
        calls.append(kwargs)
        return {
            "status": web.STATUS_READY,
            "semantic_run": {"status": "CONFIRMED_BINDINGS", "owner_confirmation_events": []},
            "semantic_assistance_state": {"status": "CONFIRMED"},
        }

    monkeypatch.setattr(web, "_run_product_root", fake_product_root)

    status, page = app.confirm_meanings(
        session_id="session-1",
        fields={"action_dialogue:semantic-unit:1": "ACCEPT"},
    )

    assert status == HTTPStatus.OK
    assert calls and calls[0]["requested_capability"] is None
    assert state.semantic_questions == []
    assert "No hay una interpretación asistida pendiente para confirmar" not in page
    assert "Leí el Excel" in page

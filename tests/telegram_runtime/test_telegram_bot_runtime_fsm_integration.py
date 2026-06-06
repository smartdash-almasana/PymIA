from __future__ import annotations

from pymia.orchestration.state_storage import load_state
from pymia.telegram_bot_runtime import route_text_message
from pymia.telegram_runtime import SENTINEL


def test_first_telegram_text_turn_opens_ficha_and_persists_state(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))

    reply = route_text_message(
        "Hola, tengo una distribuidora y no me cierra la caja.",
        chat_id="telegram-test-001",
    )

    assert SENTINEL in reply
    lowered = reply.lower()
    assert "nombre y apellido" in lowered
    assert "excel" not in lowered
    assert "diagnóstico" not in lowered
    assert "diagnostico" not in lowered

    state = load_state("telegram", "telegram-test-001", tmp_path)
    assert state is not None
    assert state.phase == "FICHA_PYME_INICIAL"
    assert state.progressive_context["phase"] == "FICHA_PYME_INICIAL"
    assert state.progressive_context["has_taxonomy"] is False
    assert state.progressive_context["has_hypotheses"] is False
    assert state.progressive_context["has_evidence_requests"] is False

    fsm_state = state.progressive_context["fsm_state"]
    assert fsm_state["profile_step"] == "ASK_CONTACT_NAME"
    assert fsm_state["profile_data"]["raw_first_message"] == "Hola, tengo una distribuidora y no me cierra la caja."

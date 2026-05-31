from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_conversa_main():
    module_path = Path(__file__).resolve().parents[1] / "conversa-engine" / "main.py"
    spec = importlib.util.spec_from_file_location("conversa_engine_main_for_roundtrip_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_conversa_preserves_progressive_context_between_turns() -> None:
    conversa_main = _load_conversa_main()
    tenant_id = "tenant_conversa_roundtrip"
    user_id = "user_conversa_roundtrip"

    conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION.clear()

    first_reply = conversa_main.run_message(
        "vendo mucho pero no se si gano plata",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    first_reply_lower = first_reply.lower()
    assert "bienvenido a pymia" in first_reply_lower
    assert "nombre y apellido" in first_reply_lower

    session_id = conversa_main._session_id(tenant_id, user_id)
    assert session_id in conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION
    first_context = conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
    
    assert isinstance(first_context, dict)
    fsm_state = first_context.get("fsm_state", {})
    assert fsm_state.get("phase") == "FICHA_PYME_INICIAL"
    assert fsm_state.get("profile_step") == "ASK_CONTACT_NAME"
    assert first_context.get("has_taxonomy") is False
    
    profile_data = fsm_state.get("profile_data", {})
    assert profile_data.get("raw_first_message") == "vendo mucho pero no se si gano plata"

    second_reply = conversa_main.run_message(
        "Juan Perez",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    second_reply_lower = second_reply.lower()
    assert "rol en la empresa" in second_reply_lower

    context = conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
    assert isinstance(context, dict)
    fsm_state2 = context.get("fsm_state", {})
    assert fsm_state2.get("phase") == "FICHA_PYME_INICIAL"
    assert fsm_state2.get("profile_step") == "ASK_CONTACT_ROLE"
    assert context.get("has_taxonomy") is False
    
    profile_data2 = fsm_state2.get("profile_data", {})
    assert profile_data2.get("contact", {}).get("full_name") == "Juan Perez"
    assert profile_data2.get("raw_first_message") == "vendo mucho pero no se si gano plata"

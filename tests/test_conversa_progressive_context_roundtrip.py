from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


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
        RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
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
    assert profile_data.get("raw_first_message") == RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY

    second_reply = conversa_main.run_message(
        "Juan Perez",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    second_reply_lower = second_reply.lower()
    assert "empresa o marca" in second_reply_lower

    context = conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
    assert isinstance(context, dict)
    fsm_state2 = context.get("fsm_state", {})
    assert fsm_state2.get("phase") == "FICHA_PYME_INICIAL"
    assert fsm_state2.get("profile_step") == "ASK_COMPANY_NAME"
    assert context.get("has_taxonomy") is False
    
    profile_data2 = fsm_state2.get("profile_data", {})
    assert profile_data2.get("contact", {}).get("full_name") == "Juan Perez"
    assert profile_data2.get("raw_first_message") == RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


def test_conversa_cli_mode_persists_context_across_module_reloads(tmp_path: Path) -> None:
    previous = os.environ.get("PYMIA_CONVERSA_STATE_BASE_DIR")
    os.environ["PYMIA_CONVERSA_STATE_BASE_DIR"] = str(tmp_path / "conversa_state")
    try:
        tenant_id = "tenant_conversa_cli_persist"
        user_id = "user_conversa_cli_persist"

        first_module = _load_conversa_main()
        first_module._PROGRESSIVE_CONTEXT_BY_SESSION.clear()
        first_reply = first_module.run_message(
            RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
            tenant_id=tenant_id,
            user_id=user_id,
            use_persistent_state=True,
        )
        assert "nombre y apellido" in first_reply.lower()

        second_module = _load_conversa_main()
        second_module._PROGRESSIVE_CONTEXT_BY_SESSION.clear()
        second_reply = second_module.run_message(
            "Juan Perez",
            tenant_id=tenant_id,
            user_id=user_id,
            use_persistent_state=True,
        )

        assert "empresa o marca" in second_reply.lower()
        session_id = second_module._session_id(tenant_id, user_id)
        ctx = second_module._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
        assert ctx.get("fsm_state", {}).get("profile_step") == "ASK_COMPANY_NAME"
    finally:
        if previous is None:
            os.environ.pop("PYMIA_CONVERSA_STATE_BASE_DIR", None)
        else:
            os.environ["PYMIA_CONVERSA_STATE_BASE_DIR"] = previous

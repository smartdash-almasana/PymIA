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
    assert "negocio" in first_reply_lower
    assert (
        "productos" in first_reply_lower
        or "servicios" in first_reply_lower
        or "fabric" in first_reply_lower
    )
    session_id = conversa_main._session_id(tenant_id, user_id)
    assert session_id in conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION
    first_context = conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
    assert isinstance(first_context, dict)
    assert first_context.get("has_taxonomy") is False
    assert first_context.get("phase") == "ANAMNESIS_TAXONOMIA"

    second_reply = conversa_main.run_message(
        "somos una distribuidora de alimentos, 12 empleados, vendemos a comercios",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    context = conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
    assert isinstance(context, dict)
    assert context.get("has_taxonomy") is True
    assert context.get("phase") == "ANAMNESIS_TAXONOMIA"
    assert context.get("tenant_id") == tenant_id
    taxonomy = context.get("fsm_state", {}).get("taxonomy")
    assert isinstance(taxonomy, dict)
    assert taxonomy.get("jurisdiction") == "AR"
    second_reply_lower = second_reply.lower()
    assert not (
        "productos" in second_reply_lower
        or "servicios" in second_reply_lower
        or "fabric" in second_reply_lower
    )

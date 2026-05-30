from __future__ import annotations

import ast
import importlib.util
from pathlib import Path



def _load_conversa_main():
    module_path = Path(__file__).resolve().parents[1] / 'conversa-engine' / 'main.py'
    spec = importlib.util.spec_from_file_location('conversa_engine_main_for_boundary_smoke_test', module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_conversa_engine_boundary_consumption_smoke() -> None:
    conversa_main = _load_conversa_main()
    tenant_id = 'tenant_m20_smoke'
    user_id = 'user_m20_smoke'

    if hasattr(conversa_main, '_PROGRESSIVE_CONTEXT_BY_SESSION'):
        conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION.clear()

    deps = conversa_main.ConversaRuntimeDeps(
        register_text_intake=lambda _text, _tenant, _user: None,
        get_supermemory_recall_client=lambda: None,
    )
    first_reply = conversa_main.run_message(
        'Tengo una fábrica textil y no sé si gano plata',
        tenant_id=tenant_id,
        user_id=user_id,
        deps=deps,
    )
    second_reply = conversa_main.run_message(
        'fabrico ropa y vendo por mayor',
        tenant_id=tenant_id,
        user_id=user_id,
        deps=deps,
    )

    assert isinstance(first_reply, str)
    assert first_reply.strip() != ''
    assert isinstance(second_reply, str)
    assert second_reply.strip() != ''

    session_id = conversa_main._session_id(tenant_id, user_id)
    assert session_id in conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION

    context = conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION[session_id]
    assert isinstance(context, dict)
    assert context.get('has_taxonomy') is True

    fsm_state = context.get('fsm_state')
    assert isinstance(fsm_state, dict)
    assert fsm_state.get('taxonomy') is not None

    if hasattr(conversa_main, '_PROGRESSIVE_CONTEXT_BY_SESSION'):
        conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION.clear()


def test_boundary_smoke_source_has_no_forbidden_imports() -> None:
    source = Path(__file__).read_text(encoding='utf-8')
    tree = ast.parse(source)
    forbidden_roots = {'langgraph', 'telegram', 'hermes', 'pymia.domain'}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported = alias.name.lower()
                assert not any(
                    imported == root or imported.startswith(f'{root}.')
                    for root in forbidden_roots
                )
        elif isinstance(node, ast.ImportFrom):
            imported = (node.module or '').lower()
            assert not any(
                imported == root or imported.startswith(f'{root}.')
                for root in forbidden_roots
            )

from pathlib import Path
import ast

from pymia.orchestration.conversation_adapter import adapt_text_message


def test_conversation_adapter_consumption_smoke_domain_core_v1() -> None:
    original_context = {}
    snapshot_context = {}

    result = adapt_text_message(
        text='fabrico ropa y vendo por mayor',
        tenant_id='tenant_m19_smoke',
        user_id='user_m19_smoke',
        progressive_context=original_context,
    )

    assert isinstance(result.reply_text, str)
    assert result.reply_text.strip() != ''
    assert isinstance(result.updated_progressive_context, dict)
    assert result.updated_progressive_context['has_preliminary_taxonomy'] is True
    assert result.updated_progressive_context['has_confirmed_taxonomy'] is False
    assert result.updated_progressive_context['has_taxonomy'] is False

    fsm_state = result.updated_progressive_context['fsm_state']
    assert isinstance(fsm_state, dict)
    assert fsm_state['taxonomy'] is None
    assert fsm_state['profile_step'] == 'ASK_CONTACT_NAME'
    assert fsm_state['preliminary_taxonomy'] is not None
    assert fsm_state['preliminary_taxonomy']['status'] == 'PRELIMINARY'
    assert fsm_state['preliminary_taxonomy']['source'] == 'raw_first_message'
    assert fsm_state['preliminary_taxonomy']['organism_type'] in {'textil', 'produccion_fabrica'}
    assert 'wholesale' in fsm_state['preliminary_taxonomy']['sales_channels']
    assert float(fsm_state['preliminary_taxonomy']['confidence']) < 1.0

    assert result.phase_hint in {'CONVERSATIONAL', 'NEEDS_EVIDENCE', 'BLOCKED'}
    assert original_context == snapshot_context


def test_conversation_adapter_consumption_smoke_ambiguous_input_has_no_preliminary_taxonomy() -> None:
    result = adapt_text_message(
        text='hola',
        tenant_id='tenant_m19_smoke_ambiguous',
        user_id='user_m19_smoke_ambiguous',
        progressive_context={},
    )

    assert result.updated_progressive_context['has_preliminary_taxonomy'] is False
    assert result.updated_progressive_context['has_confirmed_taxonomy'] is False
    assert result.updated_progressive_context['has_taxonomy'] is False
    assert result.updated_progressive_context['fsm_state']['preliminary_taxonomy'] is None


def test_smoke_test_source_has_no_forbidden_imports() -> None:
    source = Path(__file__).read_text(encoding='utf-8')
    tree = ast.parse(source)
    forbidden_roots = {'pymia.domain', 'langgraph', 'hermes', 'telegram'}

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

from __future__ import annotations

from pymia.smartpyme.conversation_contract import (
    ConversationPhase,
    create_conversation_contract,
    update_contract_phase,
)


def test_create_conversation_contract_valid():
    c = create_conversation_contract(
        contract_id="c1",
        tenant_id="t1",
        anamnesis_ref="a1",
        taxonomy_ref="tx1",
        allowed_actions=["pedir_evidencia"],
        forbidden_actions=["diagnosticar", "saltar_gate"],
    )
    assert c.current_phase == ConversationPhase.ANAMNESIS


def test_update_phase_valid():
    c = create_conversation_contract(
        contract_id="c1",
        tenant_id="t1",
        anamnesis_ref="a1",
        taxonomy_ref="tx1",
    )
    c2 = update_contract_phase(c, ConversationPhase.EVIDENCIA)
    assert c2.current_phase == ConversationPhase.EVIDENCIA


def test_update_does_not_mutate_input():
    c = create_conversation_contract(
        contract_id="c1",
        tenant_id="t1",
        anamnesis_ref="a1",
        taxonomy_ref="tx1",
    )
    before = c.to_dict()
    _ = update_contract_phase(c, "CONTRASTE")
    assert c.to_dict() == before

from __future__ import annotations

from pymia.smartpyme.supermemory_tenant_recall import TenantRecallResult
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
from pymia.smartpyme.supermemory_recall_integration import (
    RecallBeforeReplyInput,
    build_recall_augmented_message,
    build_safe_turn_summary,
    run_recall_before_reply,
)


class FakeRecallClient:
    def __init__(self, memories=None):
        self.recall_calls = []
        self.save_calls = []
        self.memories = memories if memories is not None else [{"content": "El tenant fabrica ropa."}]

    def recall_tenant_context(self, *, tenant_id, query, limit=5):
        self.recall_calls.append({"tenant_id": tenant_id, "query": query, "limit": limit})
        return TenantRecallResult(
            tenant_id=tenant_id,
            query=query,
            memories=tuple(self.memories),
        )

    def save_tenant_turn_summary(self, summary):
        self.save_calls.append(summary)
        return {"id": summary.custom_id}


def test_run_recall_before_reply_no_client_is_noop():
    input_data = RecallBeforeReplyInput(
        tenant_id="T001",
        session_key="telegram:42",
        user_message=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        turn_index=1,
    )

    output = run_recall_before_reply(input_data, client=None)

    assert output.augmented_message == RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
    assert output.recalled_memories_count == 0
    assert output.saved_summary is None


def test_run_recall_before_reply_recalls_same_tenant_and_saves_summary():
    client = FakeRecallClient(memories=[{"content": "El tenant fabrica ropa y vende por Mercado Libre."}])
    input_data = RecallBeforeReplyInput(
        tenant_id="T001",
        session_key="telegram:42",
        user_message=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        turn_index=2,
        phase="ANAMNESIS_TAXONOMIA",
        recall_limit=3,
    )

    output = run_recall_before_reply(input_data, client=client)

    assert output.recalled_memories_count == 1
    assert "Contexto conversacional recuperado del mismo tenant" in output.augmented_message
    assert "El tenant fabrica ropa y vende por Mercado Libre." in output.augmented_message
    assert "Mensaje actual del dueño:" in output.augmented_message
    assert RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY in output.augmented_message
    assert client.recall_calls == [
        {"tenant_id": "T001", "query": RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY, "limit": 3}
    ]
    assert len(client.save_calls) == 1
    saved = client.save_calls[0]
    assert saved.tenant_id == "T001"
    assert saved.session_key == "telegram:42"
    assert saved.turn_index == 2
    assert saved.phase == "ANAMNESIS_TAXONOMIA"
    assert saved.metadata["integration"] == "recall_before_reply"


def test_build_recall_augmented_message_without_memories_returns_original():
    recall = TenantRecallResult(tenant_id="T001", query="x", memories=())
    assert build_recall_augmented_message(user_message="hola", recall=recall) == "hola"


def test_build_recall_augmented_message_marks_context_as_not_operational_truth():
    recall = TenantRecallResult(
        tenant_id="T001",
        query="margen",
        memories=({"content": "El tenant vende por mayor."},),
    )

    augmented = build_recall_augmented_message(user_message="no gano", recall=recall)

    assert "no es verdad operacional confirmada" in augmented
    assert "El tenant vende por mayor." in augmented
    assert augmented.endswith("no gano")


def test_build_safe_turn_summary_uses_safe_non_diagnostic_wording():
    input_data = RecallBeforeReplyInput(
        tenant_id="T001",
        session_key="S001",
        user_message=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        turn_index=5,
    )

    summary = build_safe_turn_summary(input_data)
    payload = summary.to_supermemory_payload()

    assert summary.tenant_id == "T001"
    assert summary.session_key == "S001"
    assert summary.turn_index == 5
    assert "Registro no computacional" in summary.summary
    assert payload["containerTag"] == "tenant:T001"
    assert payload["customId"] == "turn_T001_S001_5"
    assert "/" not in payload["customId"]
    assert ":" not in payload["customId"]


def test_recall_before_reply_input_validates_required_fields():
    try:
        RecallBeforeReplyInput(
            tenant_id="",
            session_key="S001",
            user_message="hola",
            turn_index=0,
        )
    except ValueError as exc:
        assert "tenant_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    try:
        RecallBeforeReplyInput(
            tenant_id="T001",
            session_key="S001",
            user_message="hola",
            turn_index=-1,
        )
    except ValueError as exc:
        assert "turn_index" in str(exc)
    else:
        raise AssertionError("expected ValueError")

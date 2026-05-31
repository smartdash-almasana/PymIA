from __future__ import annotations

import importlib.util
from pathlib import Path

from pymia.smartpyme.supermemory_tenant_recall import TenantRecallResult
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


def _load_conversa_main():
    module_path = Path(__file__).resolve().parents[1] / "conversa-engine" / "main.py"
    spec = importlib.util.spec_from_file_location(
        "conversa_engine_main_for_supermemory_recall_runtime_test",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeSupermemoryRecallClient:
    def __init__(self):
        self.recall_calls = []
        self.save_calls = []

    def recall_tenant_context(self, *, tenant_id: str, query: str, limit: int = 5):
        self.recall_calls.append({"tenant_id": tenant_id, "query": query, "limit": limit})
        return TenantRecallResult(
            tenant_id=tenant_id,
            query=query,
            memories=(
                {
                    "content": (
                        "El tenant declaró que fabrica ropa y vende por Mercado Libre. "
                        "Registro conversacional, no hallazgo confirmado."
                    )
                },
            ),
        )

    def save_tenant_turn_summary(self, summary):
        self.save_calls.append(summary)
        return {"id": summary.custom_id}


def test_conversa_runtime_uses_injected_supermemory_recall_client() -> None:
    conversa_main = _load_conversa_main()
    fake_client = FakeSupermemoryRecallClient()
    tenant_id = "tenant_runtime_recall"
    user_id = "user_runtime_recall"

    conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION.clear()
    conversa_main._SUPERMEMORY_RECALL_CLIENT = fake_client
    conversa_main._SUPERMEMORY_RECALL_INITIALIZED = True

    reply = conversa_main.run_message(
        RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    assert isinstance(reply, str)
    assert reply.strip()
    assert fake_client.recall_calls == [
        {"tenant_id": tenant_id, "query": RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY, "limit": 3}
    ]
    assert len(fake_client.save_calls) == 1
    saved = fake_client.save_calls[0]
    assert saved.tenant_id == tenant_id
    assert saved.session_key == f"{tenant_id}/{user_id}"
    assert saved.container_tag == f"tenant:{tenant_id}"


def test_conversa_runtime_fail_open_when_recall_client_raises() -> None:
    conversa_main = _load_conversa_main()
    tenant_id = "tenant_runtime_fail_open"
    user_id = "user_runtime_fail_open"

    class BrokenClient:
        def recall_tenant_context(self, *, tenant_id: str, query: str, limit: int = 5):
            raise RuntimeError("simulated recall outage")

        def save_tenant_turn_summary(self, summary):
            raise AssertionError("save should not be reached after recall failure")

    conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION.clear()
    conversa_main._SUPERMEMORY_RECALL_CLIENT = BrokenClient()
    conversa_main._SUPERMEMORY_RECALL_INITIALIZED = True

    reply = conversa_main.run_message(
        RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    assert isinstance(reply, str)
    assert reply.strip()

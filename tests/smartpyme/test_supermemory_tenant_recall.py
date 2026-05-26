from __future__ import annotations

import pytest

from pymia.smartpyme.supermemory_tenant_recall import (
    SupermemoryClientConfig,
    SupermemoryTenantRecallClient,
    SupermemoryTransportResponse,
    TenantTurnSummary,
    build_tenant_container_tag,
    validate_safe_conversational_summary,
)


class RecorderTransport:
    def __init__(self, body=None, status_code=200):
        self.calls = []
        self.body = body or {"results": [{"content": "memoria previa"}]}
        self.status_code = status_code

    def __call__(self, *, method, url, api_key, payload):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "api_key": api_key,
                "payload": payload,
            }
        )
        return SupermemoryTransportResponse(status_code=self.status_code, body=self.body)


def test_build_tenant_container_tag_requires_tenant_id():
    assert build_tenant_container_tag("T001") == "tenant:T001"
    with pytest.raises(ValueError):
        build_tenant_container_tag("")
    with pytest.raises(ValueError):
        build_tenant_container_tag("tenant con espacios")


def test_tenant_turn_summary_builds_safe_supermemory_payload():
    summary = TenantTurnSummary(
        tenant_id="T001",
        session_key="telegram:42",
        turn_index=3,
        summary=(
            "El dueño declaró que fabrica ropa y vende por Mercado Libre. "
            "Hipótesis abierta: posible margen erosionado. No hay hallazgos confirmados."
        ),
        phase="ANAMNESIS_TAXONOMIA",
        metadata={"channel": "telegram"},
    )

    payload = summary.to_supermemory_payload()

    assert payload["containerTag"] == "tenant:T001"
    assert payload["customId"] == "turn:T001:telegram:42:3"
    assert payload["content"] == summary.summary
    assert payload["metadata"]["tenant_id"] == "T001"
    assert payload["metadata"]["session_key"] == "telegram:42"
    assert payload["metadata"]["phase"] == "ANAMNESIS_TAXONOMIA"
    assert payload["metadata"]["memory_type"] == "conversation_turn_summary"


def test_tenant_turn_summary_rejects_confirmed_finding_markers():
    with pytest.raises(ValueError):
        TenantTurnSummary(
            tenant_id="T001",
            session_key="S001",
            turn_index=1,
            summary="Hallazgo confirmado: margen real bajo.",
        )


def test_validate_safe_conversational_summary_blocks_gate_pass():
    decision = validate_safe_conversational_summary(
        "El sistema llegó a readiness PASS y gate_verdict=PASS."
    )
    assert decision.status == "BLOCK"
    assert decision.reasons


def test_metadata_must_be_flat_scalars():
    with pytest.raises(ValueError):
        TenantTurnSummary(
            tenant_id="T001",
            session_key="S001",
            turn_index=1,
            summary="El dueño declaró que vende productos.",
            metadata={"nested": {"not": "allowed"}},
        )


def test_save_tenant_turn_summary_uses_tenant_scoped_payload_and_bearer_key():
    transport = RecorderTransport(body={"id": "mem_123"})
    client = SupermemoryTenantRecallClient(
        config=SupermemoryClientConfig(api_key="test-key"),
        transport=transport,
    )
    summary = TenantTurnSummary(
        tenant_id="T001",
        session_key="S001",
        turn_index=2,
        summary="El dueño declaró que fabrica ropa. No hay hallazgos confirmados.",
    )

    result = client.save_tenant_turn_summary(summary)

    assert result == {"id": "mem_123"}
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/memories")
    assert call["api_key"] == "test-key"
    assert call["payload"]["containerTag"] == "tenant:T001"
    assert call["payload"]["customId"] == "turn:T001:S001:2"


def test_recall_tenant_context_always_filters_by_tenant_container_tag():
    transport = RecorderTransport(body={"results": [{"content": "fabrica ropa"}]})
    client = SupermemoryTenantRecallClient(
        config=SupermemoryClientConfig(api_key="test-key"),
        transport=transport,
    )

    result = client.recall_tenant_context(
        tenant_id="T001",
        query="qué negocio declaró",
        limit=4,
    )

    assert result.tenant_id == "T001"
    assert result.query == "qué negocio declaró"
    assert result.memories == ({"content": "fabrica ropa"},)
    call = transport.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/search")
    assert call["payload"] == {
        "q": "qué negocio declaró",
        "containerTag": "tenant:T001",
        "limit": 4,
    }


def test_recall_rejects_missing_query_or_bad_limit():
    client = SupermemoryTenantRecallClient(
        config=SupermemoryClientConfig(api_key="test-key"),
        transport=RecorderTransport(),
    )
    with pytest.raises(ValueError):
        client.recall_tenant_context(tenant_id="T001", query="", limit=5)
    with pytest.raises(ValueError):
        client.recall_tenant_context(tenant_id="T001", query="x", limit=0)


def test_client_raises_on_http_error_status():
    client = SupermemoryTenantRecallClient(
        config=SupermemoryClientConfig(api_key="test-key"),
        transport=RecorderTransport(status_code=500, body={"error": "boom"}),
    )
    with pytest.raises(RuntimeError):
        client.recall_tenant_context(tenant_id="T001", query="x")


def test_config_from_env_reads_api_key_without_logging_it(monkeypatch):
    monkeypatch.setenv("SUPERMEMORY_API_KEY", "secret-key")
    config = SupermemoryClientConfig.from_env()
    assert config.api_key == "secret-key"

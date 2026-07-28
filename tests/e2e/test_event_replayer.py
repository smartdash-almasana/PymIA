from __future__ import annotations

import json
from pathlib import Path

from pymia.cli import event_replayer
from pymia.contracts.events_v1 import WebhookEvent
from pymia.domain.event_transformer import transform_webhook_event


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _webhook(event_id: str, event_type: str = "order_created", aggregate_id: str = "ord-1") -> dict:
    return {
        "event_id": event_id,
        "tenant_id": "tenant_demo_001",
        "source_platform": "manual_fixture",
        "event_type": event_type,
        "occurred_at": "2026-06-11T10:00:00+00:00",
        "received_at": "2026-06-11T10:00:01+00:00",
        "raw_payload": {"aggregate_id": aggregate_id, "amount": 100},
        "metadata": {"fixture": True},
    }


def test_transformer_emits_valid_domain_event_for_supported_webhook():
    event = WebhookEvent.model_validate(_webhook("evt-1"))
    domain_events = transform_webhook_event(event)
    assert len(domain_events) == 1
    domain_event = domain_events[0]
    assert domain_event.tenant_id == "tenant_demo_001"
    assert domain_event.source_event_id == "evt-1"
    assert domain_event.event_name == "order_created"
    assert domain_event.aggregate_type == "order"
    assert domain_event.aggregate_id == "ord-1"
    assert domain_event.schema_version == "events_v1"


def test_replayer_emits_domain_events_and_summary(tmp_path: Path, capsys):
    input_path = tmp_path / "webhooks.jsonl"
    output_path = tmp_path / "domain_events.jsonl"
    _write_jsonl(input_path, [_webhook("evt-1")])
    rc = event_replayer.main(["--input", str(input_path), "--output", str(output_path)])
    out = capsys.readouterr().out
    summary = json.loads(out)
    assert rc == 0
    assert summary["received_count"] == 1
    assert summary["emitted_count"] == 1
    assert summary["skipped_duplicate_count"] == 0
    assert output_path.exists()
    emitted = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert emitted[0]["event_name"] == "order_created"
    assert emitted[0]["source_event_id"] == "evt-1"


def test_replayer_skips_duplicate_idempotency_key(tmp_path: Path):
    input_path = tmp_path / "webhooks.jsonl"
    output_path = tmp_path / "domain_events.jsonl"
    _write_jsonl(input_path, [_webhook("evt-1"), _webhook("evt-2")])
    summary = event_replayer.replay_jsonl(input_path, output_path)
    emitted = output_path.read_text(encoding="utf-8").splitlines()
    assert summary.received_count == 2
    assert summary.emitted_count == 1
    assert summary.skipped_duplicate_count == 1
    assert len(emitted) == 1


def test_replayer_skips_unsupported_webhook_without_crashing(tmp_path: Path):
    input_path = tmp_path / "webhooks.jsonl"
    output_path = tmp_path / "domain_events.jsonl"
    _write_jsonl(input_path, [_webhook("evt-1", event_type="unknown_event")])
    summary = event_replayer.replay_jsonl(input_path, output_path)
    assert summary.received_count == 1
    assert summary.emitted_count == 0
    assert summary.skipped_unsupported_count == 1
    assert output_path.read_text(encoding="utf-8") == ""


def test_replayer_counts_invalid_lines_without_crashing(tmp_path: Path):
    input_path = tmp_path / "webhooks.jsonl"
    output_path = tmp_path / "domain_events.jsonl"
    input_path.write_text("{not-json}\n", encoding="utf-8")
    summary = event_replayer.replay_jsonl(input_path, output_path)
    assert summary.received_count == 1
    assert summary.invalid_count == 1
    assert summary.emitted_count == 0


def test_event_replayer_module_does_not_import_forbidden_runtime_layers():
    sources = [
        Path(event_replayer.__file__).read_text(encoding="utf-8").lower(),
        Path(transform_webhook_event.__code__.co_filename).read_text(encoding="utf-8").lower(),
    ]
    forbidden = ["telegram", "conversa", "pymia.hermes", "pymia.llm_operator", "fastapi", "supabase"]
    for source in sources:
        for token in forbidden:
            assert token not in source

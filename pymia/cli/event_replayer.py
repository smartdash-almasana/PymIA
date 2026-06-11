from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from pymia.contracts.events_v1 import ReplaySummary, WebhookEvent
from pymia.domain.event_transformer import transform_webhook_event


def replay_jsonl(input_path: Path, output_path: Path) -> ReplaySummary:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    emitted: list[dict[str, Any]] = []
    received_count = 0
    skipped_duplicate_count = 0
    skipped_unsupported_count = 0
    invalid_count = 0

    for line in input_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        received_count += 1
        try:
            event = WebhookEvent.model_validate_json(line)
        except (ValidationError, ValueError, json.JSONDecodeError):
            invalid_count += 1
            continue

        domain_events = transform_webhook_event(event)
        if not domain_events:
            skipped_unsupported_count += 1
            continue

        for domain_event in domain_events:
            if domain_event.idempotency_key in seen:
                skipped_duplicate_count += 1
                continue
            seen.add(domain_event.idempotency_key)
            emitted.append(domain_event.model_dump(mode="json"))

    output_path.write_text(
        "".join(json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n" for item in emitted),
        encoding="utf-8",
    )
    return ReplaySummary(
        received_count=received_count,
        emitted_count=len(emitted),
        skipped_duplicate_count=skipped_duplicate_count,
        skipped_unsupported_count=skipped_unsupported_count,
        invalid_count=invalid_count,
        output_path=str(output_path),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    summary = replay_jsonl(Path(args.input), Path(args.output))
    print(json.dumps(summary.model_dump(mode="json"), sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

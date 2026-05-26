from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pymia.smartpyme.supermemory_tenant_recall import (
    SupermemoryClientConfig,
    SupermemoryTenantRecallClient,
    TenantTurnSummary,
)


def _load_env_local(repo_root: Path) -> None:
    env_path = repo_root / ".env.local"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _request_json(
    *,
    method: str,
    url: str,
    api_key: str,
    payload: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url=url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310
            raw = response.read().decode("utf-8")
            body = json.loads(raw) if raw else {}
            return body if isinstance(body, Mapping) else {"raw": body}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"error": raw}
        return body if isinstance(body, Mapping) else {"raw": body}
    except URLError:
        return {}


def _extract_document_id(save_response: Mapping[str, Any]) -> str | None:
    for key in ("id", "documentId", "document_id"):
        value = save_response.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_status(payload: Mapping[str, Any]) -> str:
    value = payload.get("status")
    if isinstance(value, str) and value.strip():
        return value.strip().lower()
    return "unknown"


def _poll_document_status(
    *,
    api_key: str,
    base_url: str,
    document_id: str,
    timeout_seconds: int = 30,
) -> str:
    deadline = time.time() + timeout_seconds
    status = "unknown"
    while time.time() < deadline:
        body = _request_json(
            method="GET",
            url=f"{base_url.rstrip('/')}/documents/{document_id}",
            api_key=api_key,
        )
        status = _extract_status(body)
        if status == "done":
            return status
        if status in {"failed", "error"}:
            return status
        time.sleep(2)
    return status


def _hybrid_recall_count(
    *,
    api_key: str,
    base_url: str,
    tenant_id: str,
    query: str,
    limit: int,
) -> int:
    body = _request_json(
        method="POST",
        url="https://api.supermemory.ai/v4/search",
        api_key=api_key,
        payload={
            "q": query,
            "containerTag": f"tenant:{tenant_id}",
            "limit": limit,
            "searchMode": "hybrid",
            "threshold": 0.3,
        },
    )
    raw = body.get("results") or body.get("memories") or []
    if not isinstance(raw, list):
        return 0
    count = 0
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        for key in ("memory", "chunk", "content", "text", "summary"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                count += 1
                break
    return count


def main() -> int:
    _load_env_local(REPO_ROOT)

    api_key = os.environ.get("SUPERMEMORY_API_KEY", "").strip()
    if not api_key:
        print("STATUS: FAIL")
        print("DOCUMENT_STATUS: unknown")
        print("MEMORIES: 0")
        print("MATCH: NO")
        return 1

    document_status = "unknown"

    try:
        config = SupermemoryClientConfig(api_key=api_key)
        client = SupermemoryTenantRecallClient(config=config)

        tenant_id = "smoke_tenant_memory_match"
        session_key = "smoke_local_match"
        turn_index = int(time.time())

        summary = TenantTurnSummary(
            tenant_id=tenant_id,
            session_key=session_key,
            turn_index=turn_index,
            summary=(
                "El dueno declaro que fabrica ropa, vende por Mercado Libre y "
                "quiere entender si gana plata. Registro no computacional."
            ),
            phase="ANAMNESIS",
            source="smoke_local_match",
            metadata={
                "scope": "local_smoke_match",
                "non_operational_truth": True,
            },
        )

        save_response = client.save_tenant_turn_summary(summary)
        doc_id = _extract_document_id(save_response)
        document_status = _extract_status(save_response)

        if doc_id:
            document_status = _poll_document_status(
                api_key=api_key,
                base_url=config.base_url,
                document_id=doc_id,
                timeout_seconds=30,
            )

        memories_count = _hybrid_recall_count(
            api_key=api_key,
            base_url=config.base_url,
            tenant_id=tenant_id,
            query="fabrica ropa Mercado Libre gana plata",
            limit=5,
        )

        matched = memories_count >= 1
        print("STATUS: OK")
        print(f"DOCUMENT_STATUS: {document_status}")
        print(f"MEMORIES: {memories_count}")
        print(f"MATCH: {'YES' if matched else 'NO'}")
        return 0
    except Exception:
        print("STATUS: FAIL")
        print(f"DOCUMENT_STATUS: {document_status}")
        print("MEMORIES: 0")
        print("MATCH: NO")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

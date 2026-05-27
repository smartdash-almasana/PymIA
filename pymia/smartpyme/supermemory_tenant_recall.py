"""Supermemory tenant-scoped conversational recall for SmartPyme/Hermes.

This module is a minimal, isolated boundary for using Supermemory as
semantic conversational memory. It does not execute PymIA kernel logic, does
not diagnose, and does not replace CMF/Supabase state.

Design invariants
-----------------
- tenant_id is mandatory for every read/write.
- Every read/write is tenant-scoped through containerTag = tenant:{tenant_id}.
- The module stores safe conversational summaries, not confirmed findings.
- Supermemory is recall/context only; PymIA/CMF remain authoritative.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = [
    "FORBIDDEN_MEMORY_MARKERS",
    "SupermemoryClientConfig",
    "SupermemoryTransportResponse",
    "SupermemoryTenantRecallClient",
    "TenantMemoryDecision",
    "TenantRecallResult",
    "TenantTurnSummary",
    "build_tenant_container_tag",
    "validate_safe_conversational_summary",
]


FORBIDDEN_MEMORY_MARKERS: tuple[str, ...] = (
    "gate_verdict=PASS",
    "readiness PASS",
    "READY_FOR_ANALYSIS confirmado",
    "hallazgo confirmado",
    "diagnóstico confirmado",
    "diagnostico confirmado",
    "margen real",
    "output_ref",
    "delivery_package_id",
    "excel crudo",
)


@dataclass(frozen=True)
class TenantMemoryDecision:
    """ALLOW/WARN/BLOCK decision for memory operations."""

    status: str
    reasons: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.status == "ALLOW"

    @staticmethod
    def allow() -> "TenantMemoryDecision":
        return TenantMemoryDecision(status="ALLOW")

    @staticmethod
    def block(*reasons: str) -> "TenantMemoryDecision":
        return TenantMemoryDecision(status="BLOCK", reasons=tuple(reasons))


@dataclass(frozen=True)
class TenantTurnSummary:
    """Safe conversational summary to persist in semantic memory."""

    tenant_id: str
    session_key: str
    turn_index: int
    summary: str
    phase: str | None = None
    source: str = "hermes"
    metadata: Mapping[str, str | int | float | bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty("tenant_id", self.tenant_id)
        _require_non_empty("session_key", self.session_key)
        if not isinstance(self.turn_index, int) or self.turn_index < 0:
            raise ValueError("turn_index must be a non-negative integer")
        _require_non_empty("summary", self.summary)
        decision = validate_safe_conversational_summary(self.summary)
        if not decision.allowed:
            raise ValueError("unsafe conversational summary: " + "; ".join(decision.reasons))
        for key, value in self.metadata.items():
            if not isinstance(key, str) or not key:
                raise ValueError("metadata keys must be non-empty strings")
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError("metadata values must be scalar: str, int, float, bool")

    @property
    def container_tag(self) -> str:
        return build_tenant_container_tag(self.tenant_id)

    @property
    def custom_id(self) -> str:
        return build_safe_custom_id(
            "turn",
            self.tenant_id,
            self.session_key,
            str(self.turn_index),
        )

    def to_supermemory_payload(self) -> dict[str, Any]:
        metadata: dict[str, str | int | float | bool] = {
            "tenant_id": self.tenant_id,
            "session_key": self.session_key,
            "turn_index": self.turn_index,
            "source": self.source,
            "memory_type": "conversation_turn_summary",
        }
        if self.phase:
            metadata["phase"] = self.phase
        metadata.update(dict(self.metadata))
        return {
            "content": self.summary,
            "containerTag": self.container_tag,
            "customId": self.custom_id,
            "metadata": metadata,
        }


@dataclass(frozen=True)
class TenantRecallResult:
    """Normalized recall result returned to Hermes."""

    tenant_id: str
    query: str
    memories: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class SupermemoryClientConfig:
    """Configuration for Supermemory HTTP access."""

    api_key: str
    base_url: str = "https://api.supermemory.ai/v3"

    @staticmethod
    def from_env(env_var: str = "SUPERMEMORY_API_KEY") -> "SupermemoryClientConfig":
        api_key = os.environ.get(env_var, "").strip()
        if not api_key:
            raise ValueError(f"{env_var} is required")
        return SupermemoryClientConfig(api_key=api_key)


@dataclass(frozen=True)
class SupermemoryTransportResponse:
    """Minimal HTTP transport response."""

    status_code: int
    body: Mapping[str, Any]


class SupermemoryTransport(Protocol):
    def __call__(
        self,
        *,
        method: str,
        url: str,
        api_key: str,
        payload: Mapping[str, Any],
    ) -> SupermemoryTransportResponse: ...


class SupermemoryTenantRecallClient:
    """Tenant-scoped Supermemory client.

    The client is intentionally small and transport-injected to keep tests
    deterministic and to avoid real network calls unless explicitly wired by
    the caller.
    """

    def __init__(
        self,
        config: SupermemoryClientConfig,
        transport: SupermemoryTransport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or _default_http_transport

    def save_tenant_turn_summary(self, summary: TenantTurnSummary) -> Mapping[str, Any]:
        payload = summary.to_supermemory_payload()
        _assert_tenant_scoped_payload(summary.tenant_id, payload)
        response = self._transport(
            method="POST",
            url=f"{self._config.base_url.rstrip('/')}/documents",
            api_key=self._config.api_key,
            payload=payload,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Supermemory save failed: HTTP {response.status_code}: "
                f"{_sanitize_response_body(response.body)}"
            )
        return response.body

    def recall_tenant_context(
        self,
        *,
        tenant_id: str,
        query: str,
        limit: int = 5,
        search_mode: str = "hybrid",
        threshold: float = 0.3,
    ) -> TenantRecallResult:
        _require_non_empty("tenant_id", tenant_id)
        _require_non_empty("query", query)
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        _require_non_empty("search_mode", search_mode)
        if not isinstance(threshold, (int, float)) or threshold < 0:
            raise ValueError("threshold must be a non-negative number")

        payload = {
            "q": query,
            "containerTag": build_tenant_container_tag(tenant_id),
            "searchMode": search_mode,
            "limit": limit,
            "threshold": float(threshold),
        }
        _assert_tenant_scoped_payload(tenant_id, payload)
        response = self._transport(
            method="POST",
            url="https://api.supermemory.ai/v4/search",
            api_key=self._config.api_key,
            payload=payload,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Supermemory recall failed: HTTP {response.status_code}: "
                f"{_sanitize_response_body(response.body)}"
            )
        memories = _normalize_search_results(response.body)
        return TenantRecallResult(tenant_id=tenant_id, query=query, memories=memories)


def build_safe_custom_id(*parts: object) -> str:
    """Build a deterministic API-safe customId for Supermemory.

    The resulting identifier intentionally avoids separators that are known to
    cause ambiguity in external APIs, especially `/` and `:`.
    """
    if not parts:
        raise ValueError("at least one custom id part is required")
    raw_parts: list[str] = []
    for index, part in enumerate(parts):
        _require_non_empty(f"custom_id_part_{index}", part)
        raw_parts.append(str(part))
    raw = "::".join(raw_parts)
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", raw).strip("_")
    if not slug:
        raise ValueError("custom id cannot be empty after sanitization")
    if len(slug) <= 120:
        return slug
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{slug[:100]}_{digest}"


def build_tenant_container_tag(tenant_id: str) -> str:
    """Return canonical Supermemory tenant containerTag."""
    _require_non_empty("tenant_id", tenant_id)
    if any(ch.isspace() for ch in tenant_id):
        raise ValueError("tenant_id must not contain whitespace")
    return f"tenant:{tenant_id}"


def validate_safe_conversational_summary(summary: str) -> TenantMemoryDecision:
    """Reject unsafe summaries that would turn memory into truth.

    This is deliberately lexical and conservative. The goal is not to infer
    all possible unsafe statements, but to block the most dangerous markers at
    the Hermes memory boundary.
    """
    _require_non_empty("summary", summary)
    lowered = summary.lower()
    reasons = []
    for marker in FORBIDDEN_MEMORY_MARKERS:
        if marker.lower() in lowered:
            reasons.append(f"forbidden memory marker: {marker}")
    if reasons:
        return TenantMemoryDecision.block(*reasons)
    return TenantMemoryDecision.allow()


def _assert_tenant_scoped_payload(tenant_id: str, payload: Mapping[str, Any]) -> None:
    expected = build_tenant_container_tag(tenant_id)
    if payload.get("containerTag") != expected:
        raise ValueError("Supermemory payload must include tenant-scoped containerTag")


def _normalize_search_results(body: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    raw = body.get("results") or body.get("memories") or []
    if not isinstance(raw, list):
        return ()
    normalized: list[Mapping[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        text = _extract_memory_text(item)
        if text is None:
            continue
        row = dict(item)
        row.setdefault("content", text)
        normalized.append(row)
    return tuple(normalized)


def _extract_memory_text(item: Mapping[str, Any]) -> str | None:
    for key in ("memory", "chunk", "content", "text", "summary"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _sanitize_response_body(body: Any) -> str:
    if isinstance(body, Mapping):
        redacted = dict(body)
        for key in (
            "api_key",
            "authorization",
            "Authorization",
            "token",
            "access_token",
        ):
            if key in redacted:
                redacted[key] = "***"
        rendered = json.dumps(redacted, ensure_ascii=False)
        return rendered[:500]
    return str(body)[:500]


def _default_http_transport(
    *,
    method: str,
    url: str,
    api_key: str,
    payload: Mapping[str, Any],
) -> SupermemoryTransportResponse:
    encoded = json.dumps(payload).encode("utf-8")
    request = Request(
        url=url,
        data=encoded,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - explicit outbound integration boundary
            raw_body = response.read().decode("utf-8")
            body = json.loads(raw_body) if raw_body else {}
            if not isinstance(body, Mapping):
                body = {"raw": body}
            return SupermemoryTransportResponse(status_code=response.status, body=body)
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8") if exc.fp else ""
        parsed: Mapping[str, Any]
        try:
            maybe = json.loads(raw_body) if raw_body else {}
            parsed = maybe if isinstance(maybe, Mapping) else {"raw": maybe}
        except json.JSONDecodeError:
            parsed = {"error": raw_body}
        return SupermemoryTransportResponse(status_code=exc.code, body=parsed)
    except URLError as exc:
        raise RuntimeError(f"Supermemory transport error: {exc.reason}") from exc


def _require_non_empty(name: str, value: str) -> None:
    if value is None or not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")

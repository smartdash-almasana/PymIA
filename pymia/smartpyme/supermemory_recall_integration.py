"""Recall-before-reply integration for SmartPyme conversational memory.

This module prepares Supermemory tenant recall as context for Hermes/FSM
without making Supermemory authoritative. It is intentionally pure except for
an injected recall/save client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from pymia.smartpyme.supermemory_tenant_recall import (
    TenantRecallResult,
    TenantTurnSummary,
)

__all__ = [
    "RecallBeforeReplyInput",
    "RecallBeforeReplyOutput",
    "TenantRecallClientProtocol",
    "build_recall_augmented_message",
    "build_safe_turn_summary",
    "run_recall_before_reply",
]


class TenantRecallClientProtocol(Protocol):
    def recall_tenant_context(
        self,
        *,
        tenant_id: str,
        query: str,
        limit: int = 5,
    ) -> TenantRecallResult: ...

    def save_tenant_turn_summary(self, summary: TenantTurnSummary) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class RecallBeforeReplyInput:
    tenant_id: str
    session_key: str
    user_message: str
    turn_index: int
    phase: str | None = None
    recall_limit: int = 3

    def __post_init__(self) -> None:
        _require_non_empty("tenant_id", self.tenant_id)
        _require_non_empty("session_key", self.session_key)
        _require_non_empty("user_message", self.user_message)
        if not isinstance(self.turn_index, int) or self.turn_index < 0:
            raise ValueError("turn_index must be a non-negative integer")
        if not isinstance(self.recall_limit, int) or self.recall_limit <= 0:
            raise ValueError("recall_limit must be a positive integer")


@dataclass(frozen=True)
class RecallBeforeReplyOutput:
    augmented_message: str
    recalled_memories_count: int
    saved_summary: TenantTurnSummary | None


def run_recall_before_reply(
    input_data: RecallBeforeReplyInput,
    *,
    client: TenantRecallClientProtocol | None,
) -> RecallBeforeReplyOutput:
    """Recall tenant context and produce an augmented user message.

    If no client is supplied, this is a no-op. That keeps the runtime safe when
    SUPERMEMORY_API_KEY is absent or recall is disabled.
    """
    if client is None:
        return RecallBeforeReplyOutput(
            augmented_message=input_data.user_message,
            recalled_memories_count=0,
            saved_summary=None,
        )

    recall = client.recall_tenant_context(
        tenant_id=input_data.tenant_id,
        query=input_data.user_message,
        limit=input_data.recall_limit,
    )
    augmented = build_recall_augmented_message(
        user_message=input_data.user_message,
        recall=recall,
    )
    summary = build_safe_turn_summary(input_data)
    client.save_tenant_turn_summary(summary)
    return RecallBeforeReplyOutput(
        augmented_message=augmented,
        recalled_memories_count=len(recall.memories),
        saved_summary=summary,
    )


def build_recall_augmented_message(
    *,
    user_message: str,
    recall: TenantRecallResult,
) -> str:
    """Build a bounded context preamble for the FSM/Hermes layer.

    The preamble marks memories as contextual, not verified facts.
    """
    _require_non_empty("user_message", user_message)
    safe_memories = _extract_memory_texts(recall.memories)
    if not safe_memories:
        return user_message

    bullet_lines = "\n".join(f"- {text}" for text in safe_memories[:5])
    return (
        "Contexto conversacional recuperado del mismo tenant "
        "(no es verdad operacional confirmada):\n"
        f"{bullet_lines}\n\n"
        "Mensaje actual del dueño:\n"
        f"{user_message}"
    )


def build_safe_turn_summary(input_data: RecallBeforeReplyInput) -> TenantTurnSummary:
    """Build a safe, non-diagnostic summary for Supermemory."""
    summary = (
        "Mensaje conversacional del dueño registrado para continuidad. "
        f"Texto declarado: {input_data.user_message}. "
        "Registro no computacional. Sin resultado del kernel."
    )
    # TenantTurnSummary enforces forbidden markers. The wording above avoids
    # confirmed finding markers while keeping explicit non-authority.
    return TenantTurnSummary(
        tenant_id=input_data.tenant_id,
        session_key=input_data.session_key,
        turn_index=input_data.turn_index,
        summary=summary,
        phase=input_data.phase,
        metadata={"integration": "recall_before_reply"},
    )


def _extract_memory_texts(memories: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
    result: list[str] = []
    for memory in memories:
        raw = (
            memory.get("content")
            or memory.get("text")
            or memory.get("summary")
            or memory.get("memory")
        )
        if isinstance(raw, str) and raw.strip():
            result.append(_single_line(raw.strip()))
    return tuple(result)


def _single_line(value: str) -> str:
    return " ".join(value.split())


def _require_non_empty(name: str, value: str) -> None:
    if value is None or not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")

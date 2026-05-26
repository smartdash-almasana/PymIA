"""Conversation contract snapshot for SmartPyme.

Pure contract object for conversational phase tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ConversationPhase(str, Enum):
    ANAMNESIS = "ANAMNESIS"
    HIPOTESIS = "HIPOTESIS"
    EVIDENCIA = "EVIDENCIA"
    CONTRASTE = "CONTRASTE"
    ENTREGA = "ENTREGA"


@dataclass
class ConversationContract:
    contract_id: str
    tenant_id: str
    anamnesis_ref: str
    taxonomy_ref: str
    hypotheses_open: list[str] = field(default_factory=list)
    hypotheses_closed: list[str] = field(default_factory=list)
    evidence_received: list[str] = field(default_factory=list)
    evidence_pending: list[str] = field(default_factory=list)
    current_phase: ConversationPhase = ConversationPhase.ANAMNESIS
    allowed_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_conversation_contract(
    *,
    contract_id: str,
    tenant_id: str,
    anamnesis_ref: str,
    taxonomy_ref: str,
    current_phase: ConversationPhase | str = ConversationPhase.ANAMNESIS,
    allowed_actions: list[str] | None = None,
    forbidden_actions: list[str] | None = None,
) -> ConversationContract:
    """Create a conversation contract snapshot.

    Does NOT persist state or invoke runtime actions.
    """
    for name, value in {
        "contract_id": contract_id,
        "tenant_id": tenant_id,
        "anamnesis_ref": anamnesis_ref,
        "taxonomy_ref": taxonomy_ref,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    if isinstance(current_phase, str):
        try:
            current_phase = ConversationPhase(current_phase)
        except ValueError as exc:
            raise ValueError(f"invalid current_phase: {current_phase!r}") from exc

    return ConversationContract(
        contract_id=contract_id,
        tenant_id=tenant_id,
        anamnesis_ref=anamnesis_ref,
        taxonomy_ref=taxonomy_ref,
        current_phase=current_phase,
        allowed_actions=list(allowed_actions or []),
        forbidden_actions=list(forbidden_actions or []),
    )


def update_contract_phase(
    contract: ConversationContract,
    new_phase: ConversationPhase | str,
) -> ConversationContract:
    """Return a new contract with updated phase.

    Does NOT mutate the input contract.
    """
    if not isinstance(contract, ConversationContract):
        raise ValueError("contract must be ConversationContract")

    if isinstance(new_phase, str):
        try:
            new_phase = ConversationPhase(new_phase)
        except ValueError as exc:
            raise ValueError(f"invalid new_phase: {new_phase!r}") from exc

    return replace(contract, current_phase=new_phase)


__all__ = [
    "ConversationPhase",
    "ConversationContract",
    "create_conversation_contract",
    "update_contract_phase",
]

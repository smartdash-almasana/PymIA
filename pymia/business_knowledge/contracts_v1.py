"""Governed contracts for external operational knowledge imported into PymIA.

This layer is intentionally outside the Service 1 productive root. It stores
versioned operational knowledge that can later be promoted after validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

KnowledgeKind = Literal["METRIC", "CONTROL", "WORKFLOW"]
KnowledgeStatus = Literal["CANDIDATE", "VALIDATED"]


@dataclass(frozen=True)
class EvidenceFieldV1:
    name: str
    semantic_role: str
    unit: str | None = None
    required: bool = True


@dataclass(frozen=True)
class OperationalKnowledgeSpecV1:
    knowledge_ref: str
    domain: str
    family: str
    kind: KnowledgeKind
    status: KnowledgeStatus
    inputs: tuple[EvidenceFieldV1, ...]
    expression: str
    output_key: str
    output_unit: str
    validations: tuple[str, ...]
    interpretation_limits: tuple[str, ...]
    provenance: tuple[str, ...]
    runtime_authorized: bool = False


@dataclass(frozen=True)
class KnowledgePackV1:
    pack_ref: str
    version: str
    source_family: str
    capabilities: tuple[OperationalKnowledgeSpecV1, ...]
    runtime_authorized: bool = False


__all__ = [
    "EvidenceFieldV1",
    "OperationalKnowledgeSpecV1",
    "KnowledgePackV1",
]

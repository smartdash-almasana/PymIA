"""Explicit command contracts for the single Servicio 1 execution root."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence, Union


@dataclass(frozen=True, slots=True)
class Service1ProductExecutionDependenciesV1:
    """Runtime ports and infrastructure, kept separate from command intent."""

    output_dir: str | Path
    semantic_provider: Any = None
    compatible_tenant_memory_hints: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    semantic_owner_actor_id: str | None = None
    semantic_owner_actor_role: str | None = None
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    semantic_scope_capabilities: Sequence[str] = field(default_factory=tuple)
    tenant_id: str | None = None
    source_system_ref: str | None = None
    source_context_ref: str | None = None
    schema_family_memory_records: Sequence[Mapping[str, Any] | Any] = field(default_factory=tuple)
    governed_results: Any = None
    persist_result_memory: bool = True


@dataclass(frozen=True, slots=True)
class WorkbookSemanticStartRequestV1:
    ingestion_output: Mapping[str, Any]
    requested_capability: str | None = None
    deliver_result: bool = False
    semantic_atomic_confirmation: bool = False


@dataclass(frozen=True, slots=True)
class WorkbookSemanticContinueRequestV1:
    ingestion_output: Mapping[str, Any]
    requested_capability: str | None = None
    semantic_assistance_state: Mapping[str, Any] | None = None
    semantic_dialogue_responses: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    deliver_result: bool = False


@dataclass(frozen=True, slots=True)
class WorkbookAnalysisExecuteRequestV1:
    ingestion_output: Mapping[str, Any]
    confirmed_bindings: Mapping[str, Any]
    analysis_id: str
    tenant_identity_contract: Any = None


SPECIALIZED_DOMAIN_COLLECTION_AGING = "COLLECTION_AGING"
SPECIALIZED_DOMAIN_EXPENSE_VARIANCE = "EXPENSE_VARIANCE"
SPECIALIZED_DOMAIN_RECONCILIATION = "RECONCILIATION"
SPECIALIZED_DOMAIN_SUBTYPES = frozenset(
    {
        SPECIALIZED_DOMAIN_COLLECTION_AGING,
        SPECIALIZED_DOMAIN_EXPENSE_VARIANCE,
        SPECIALIZED_DOMAIN_RECONCILIATION,
    }
)


@dataclass(frozen=True, slots=True)
class SpecializedDomainExecuteRequestV1:
    subtype: str
    payload: Mapping[str, Any]


ProductExecutionRequestV1 = Union[
    WorkbookSemanticStartRequestV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookAnalysisExecuteRequestV1,
    SpecializedDomainExecuteRequestV1,
]


__all__ = [
    "ProductExecutionRequestV1",
    "Service1ProductExecutionDependenciesV1",
    "WorkbookSemanticStartRequestV1",
    "WorkbookSemanticContinueRequestV1",
    "WorkbookAnalysisExecuteRequestV1",
    "SpecializedDomainExecuteRequestV1",
    "SPECIALIZED_DOMAIN_COLLECTION_AGING",
    "SPECIALIZED_DOMAIN_EXPENSE_VARIANCE",
    "SPECIALIZED_DOMAIN_RECONCILIATION",
    "SPECIALIZED_DOMAIN_SUBTYPES",
]

"""Explicit command contracts for the single Servicio 1 execution root."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, Union


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
    persist_result_memory: Callable[[Any], bool] | None = None


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
class WorkbookSemanticAtomicRequestV1:
    ingestion_output: Mapping[str, Any]
    requested_capability: str | None = None
    deliver_result: bool = False
    semantic_atomic_confirmation: bool = True


@dataclass(frozen=True, slots=True)
class TypedAnalysisRequestV1:
    ingestion_output: Mapping[str, Any]
    requested_capability: str
    confirmed_bindings: Mapping[str, Any]
    deliver_result: bool = False
    tenant_identity_contract: Any = None


Service1ProductExecutionRequestV1 = Union[
    WorkbookSemanticStartRequestV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookSemanticAtomicRequestV1,
    TypedAnalysisRequestV1,
]

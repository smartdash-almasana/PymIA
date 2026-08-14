"""Servicio 1 — closed LLM semantic assistance contracts V1.

ADR-029 / SEM-2. Pure contract module: no network, no provider SDK, no XLSX
parsing, no persistence, no owner confirmation, no calculation and no runtime
or delivery authority.

This module validates *shape only*. Whether semantic roles, variables, column
references and evidence references are actually valid belongs to the
SEM-3 deterministic proposal validator.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from types import MappingProxyType
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    SCHEMA_VERSION as WORKBOOK_PROFILE_SCHEMA_VERSION,
    STATUS_READY as WORKBOOK_PROFILE_READY,
)

CONTEXT_SCHEMA_VERSION: Final[str] = "SERVICE_1_LLM_SEMANTIC_CONTEXT_V1"
PROPOSAL_SCHEMA_VERSION: Final[str] = "SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

_FORBIDDEN_AUTHORITY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "owner_confirmed",
        "confirmed_by_owner",
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
        "calculation_result",
        "automatic_reuse_authorized",
        "semantic_rebind_authorized",
    }
)

_CONTEXT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "schema_version",
        "service_name",
        "case_id",
        "requested_capability",
        "workbook_profile",
        "deterministic_hypotheses",
        "allowed_semantic_roles",
        "capability_relevant_roles",
        "compatible_tenant_memory_hints",
        "evidence_registry",
    }
)
_PROPOSAL_KEYS: Final[frozenset[str]] = frozenset(
    {
        "schema_version",
        "concept_proposals",
        "relationship_proposals",
        "duplicate_semantics",
        "irrelevant_refs",
        "material_ambiguities",
    }
)
_CONCEPT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "proposal_id",
        "target_column_refs",
        "semantic_role",
        "variable_name",
        "confidence",
        "rationale",
        "evidence_refs",
    }
)
_RELATIONSHIP_KEYS: Final[frozenset[str]] = frozenset(
    {
        "relationship_id",
        "left_column_ref",
        "right_column_ref",
        "relationship_type",
        "confidence",
        "rationale",
        "evidence_refs",
    }
)
_DUPLICATE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "duplicate_id",
        "column_refs",
        "proposed_shared_role",
        "confidence",
        "rationale",
        "evidence_refs",
    }
)
_AMBIGUITY_KEYS: Final[frozenset[str]] = frozenset(
    {
        "ambiguity_id",
        "target_refs",
        "reason",
        "confidence",
        "evidence_refs",
    }
)


class Service1LLMSemanticContractErrorV1(ValueError):
    """Fail-closed contract error with a stable reason code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _error(code: str, detail: str) -> Service1LLMSemanticContractErrorV1:
    return Service1LLMSemanticContractErrorV1(code, detail)


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error("INVALID_TEXT_FIELD", f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _confidence(value: Any, *, field_name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise _error("INVALID_CONFIDENCE", f"{field_name} must be between 0 and 1") from exc
    if result < 0 or result > 1:
        raise _error("INVALID_CONFIDENCE", f"{field_name} must be between 0 and 1")
    return result


def _text_tuple(value: Any, *, field_name: str, min_items: int = 0) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise _error("INVALID_LIST_FIELD", f"{field_name} must be a list")
    result: list[str] = []
    for item in value:
        text = _required_text(item, field_name=field_name)
        if text in result:
            raise _error("DUPLICATE_LIST_ITEM", f"{field_name} contains duplicate value {text!r}")
        result.append(text)
    if len(result) < min_items:
        raise _error("INVALID_LIST_FIELD", f"{field_name} requires at least {min_items} item(s)")
    return tuple(result)


def _mapping_tuple(value: Any, *, field_name: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        raise _error("INVALID_LIST_FIELD", f"{field_name} must be a list")
    result: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise _error("INVALID_MAPPING_FIELD", f"{field_name} entries must be mappings")
        _reject_true_authority_fields(item, field_name=field_name)
        result.append(MappingProxyType(dict(item)))
    return tuple(result)


def _closed_mapping(value: Any, *, field_name: str, allowed_keys: frozenset[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _error("INVALID_MAPPING_FIELD", f"{field_name} must be a mapping")
    _reject_authority_fields(value, field_name=field_name)
    unknown = set(value) - allowed_keys
    if unknown:
        raise _error("UNKNOWN_FIELD", f"{field_name} contains unknown field(s): {', '.join(sorted(unknown))}")
    return value


def _reject_authority_fields(value: Any, *, field_name: str) -> None:
    if isinstance(value, Mapping):
        forbidden = set(value).intersection(_FORBIDDEN_AUTHORITY_FIELDS)
        if forbidden:
            raise _error(
                "FORBIDDEN_AUTHORITY_FIELD",
                f"{field_name} contains forbidden authority field(s): {', '.join(sorted(forbidden))}",
            )
        for key, item in value.items():
            _reject_authority_fields(item, field_name=f"{field_name}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_authority_fields(item, field_name=f"{field_name}[{index}]")


def _reject_true_authority_fields(value: Any, *, field_name: str) -> None:
    """Allow canonical upstream safety flags only when explicitly False."""
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in _FORBIDDEN_AUTHORITY_FIELDS and item is not False:
                raise _error(
                    "FORBIDDEN_AUTHORITY_FIELD",
                    f"{field_name}.{key} must remain False in semantic context evidence",
                )
            _reject_true_authority_fields(item, field_name=f"{field_name}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_true_authority_fields(item, field_name=f"{field_name}[{index}]")


@dataclass(frozen=True)
class Service1LLMSemanticContextV1:
    case_id: str
    requested_capability: str
    workbook_profile: Mapping[str, Any]
    deterministic_hypotheses: tuple[Mapping[str, Any], ...]
    allowed_semantic_roles: tuple[str, ...]
    capability_relevant_roles: tuple[str, ...]
    compatible_tenant_memory_hints: tuple[Mapping[str, Any], ...]
    evidence_registry: Mapping[str, Any]
    schema_version: str = CONTEXT_SCHEMA_VERSION
    service_name: str = SERVICE_NAME

    def __post_init__(self) -> None:
        if self.schema_version != CONTEXT_SCHEMA_VERSION:
            raise _error("INVALID_CONTEXT_SCHEMA", "invalid semantic context schema")
        if self.service_name != SERVICE_NAME:
            raise _error("INVALID_SERVICE", "semantic context service must be SERVICE_1")
        object.__setattr__(self, "case_id", _required_text(self.case_id, field_name="case_id"))
        object.__setattr__(
            self,
            "requested_capability",
            _required_text(self.requested_capability, field_name="requested_capability"),
        )
        if not isinstance(self.workbook_profile, Mapping):
            raise _error("INVALID_WORKBOOK_PROFILE", "workbook_profile must be a mapping")
        profile = dict(self.workbook_profile)
        _reject_true_authority_fields(profile, field_name="workbook_profile")
        if profile.get("schema_version") != WORKBOOK_PROFILE_SCHEMA_VERSION or profile.get("status") != WORKBOOK_PROFILE_READY:
            raise _error("INVALID_WORKBOOK_PROFILE", "workbook_profile must be a ready V1 profile")
        if str(profile.get("case_id") or "").strip() not in {"", self.case_id}:
            raise _error("CONTEXT_CASE_MISMATCH", "workbook_profile case_id differs from context case_id")
        object.__setattr__(self, "workbook_profile", MappingProxyType(profile))
        object.__setattr__(
            self,
            "deterministic_hypotheses",
            _mapping_tuple(self.deterministic_hypotheses, field_name="deterministic_hypotheses"),
        )
        object.__setattr__(
            self,
            "allowed_semantic_roles",
            _text_tuple(self.allowed_semantic_roles, field_name="allowed_semantic_roles", min_items=1),
        )
        object.__setattr__(
            self,
            "capability_relevant_roles",
            _text_tuple(self.capability_relevant_roles, field_name="capability_relevant_roles"),
        )
        if set(self.capability_relevant_roles) - set(self.allowed_semantic_roles):
            raise _error("RELEVANT_ROLE_OUTSIDE_ALLOWED_SET", "capability_relevant_roles must be a subset of allowed_semantic_roles")
        object.__setattr__(
            self,
            "compatible_tenant_memory_hints",
            _mapping_tuple(self.compatible_tenant_memory_hints, field_name="compatible_tenant_memory_hints"),
        )
        if not isinstance(self.evidence_registry, Mapping):
            raise _error("INVALID_EVIDENCE_REGISTRY", "evidence_registry must be a mapping")
        registry = dict(self.evidence_registry)
        _reject_true_authority_fields(registry, field_name="evidence_registry")
        if registry != dict(profile.get("evidence_registry") or {}):
            raise _error("EVIDENCE_REGISTRY_MISMATCH", "context evidence_registry must equal workbook profile evidence_registry")
        object.__setattr__(self, "evidence_registry", MappingProxyType(registry))

    def to_provider_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "case_id": self.case_id,
            "requested_capability": self.requested_capability,
            "workbook_profile": dict(self.workbook_profile),
            "deterministic_hypotheses": [dict(item) for item in self.deterministic_hypotheses],
            "allowed_semantic_roles": list(self.allowed_semantic_roles),
            "capability_relevant_roles": list(self.capability_relevant_roles),
            "compatible_tenant_memory_hints": [dict(item) for item in self.compatible_tenant_memory_hints],
            "evidence_registry": dict(self.evidence_registry),
        }


@dataclass(frozen=True)
class Service1LLMConceptProposalV1:
    proposal_id: str
    target_column_refs: tuple[str, ...]
    semantic_role: str
    variable_name: str
    confidence: float
    rationale: str | None
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1LLMRelationshipProposalV1:
    relationship_id: str
    left_column_ref: str
    right_column_ref: str
    relationship_type: str
    confidence: float
    rationale: str | None
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1LLMDuplicateSemanticProposalV1:
    duplicate_id: str
    column_refs: tuple[str, ...]
    proposed_shared_role: str
    confidence: float
    rationale: str | None
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1LLMMaterialAmbiguityV1:
    ambiguity_id: str
    target_refs: tuple[str, ...]
    reason: str
    confidence: float
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1LLMSemanticProposalV1:
    concept_proposals: tuple[Service1LLMConceptProposalV1, ...] = field(default_factory=tuple)
    relationship_proposals: tuple[Service1LLMRelationshipProposalV1, ...] = field(default_factory=tuple)
    duplicate_semantics: tuple[Service1LLMDuplicateSemanticProposalV1, ...] = field(default_factory=tuple)
    irrelevant_refs: tuple[str, ...] = field(default_factory=tuple)
    material_ambiguities: tuple[Service1LLMMaterialAmbiguityV1, ...] = field(default_factory=tuple)
    schema_version: str = PROPOSAL_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PROPOSAL_SCHEMA_VERSION:
            raise _error("INVALID_PROPOSAL_SCHEMA", "invalid semantic proposal schema")
        identifiers = [item.proposal_id for item in self.concept_proposals]
        identifiers += [item.relationship_id for item in self.relationship_proposals]
        identifiers += [item.duplicate_id for item in self.duplicate_semantics]
        identifiers += [item.ambiguity_id for item in self.material_ambiguities]
        if len(identifiers) != len(set(identifiers)):
            raise _error("DUPLICATE_PROPOSAL_ID", "all semantic proposal identifiers must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "concept_proposals": [item.to_dict() for item in self.concept_proposals],
            "relationship_proposals": [item.to_dict() for item in self.relationship_proposals],
            "duplicate_semantics": [item.to_dict() for item in self.duplicate_semantics],
            "irrelevant_refs": list(self.irrelevant_refs),
            "material_ambiguities": [item.to_dict() for item in self.material_ambiguities],
        }


def build_service_1_llm_semantic_context_v1(
    *,
    case_id: str,
    requested_capability: str,
    workbook_profile: Mapping[str, Any],
    deterministic_hypotheses: Sequence[Mapping[str, Any]],
    allowed_semantic_roles: Sequence[str],
    capability_relevant_roles: Sequence[str] = (),
    compatible_tenant_memory_hints: Sequence[Mapping[str, Any]] = (),
) -> Service1LLMSemanticContextV1:
    return Service1LLMSemanticContextV1(
        case_id=case_id,
        requested_capability=requested_capability,
        workbook_profile=workbook_profile,
        deterministic_hypotheses=tuple(deterministic_hypotheses),
        allowed_semantic_roles=tuple(allowed_semantic_roles),
        capability_relevant_roles=tuple(capability_relevant_roles),
        compatible_tenant_memory_hints=tuple(compatible_tenant_memory_hints),
        evidence_registry=dict(workbook_profile.get("evidence_registry") or {}),
    )


def parse_service_1_llm_semantic_proposal_v1(payload: Any) -> Service1LLMSemanticProposalV1:
    root = _closed_mapping(payload, field_name="proposal", allowed_keys=_PROPOSAL_KEYS)
    if root.get("schema_version") != PROPOSAL_SCHEMA_VERSION:
        raise _error("INVALID_PROPOSAL_SCHEMA", "proposal schema_version is required and must match V1")

    concepts = tuple(_parse_concept(item, index) for index, item in enumerate(_required_list(root, "concept_proposals")))
    relationships = tuple(
        _parse_relationship(item, index)
        for index, item in enumerate(_required_list(root, "relationship_proposals"))
    )
    duplicates = tuple(
        _parse_duplicate(item, index)
        for index, item in enumerate(_required_list(root, "duplicate_semantics"))
    )
    irrelevant = _text_tuple(root.get("irrelevant_refs"), field_name="irrelevant_refs")
    ambiguities = tuple(
        _parse_ambiguity(item, index)
        for index, item in enumerate(_required_list(root, "material_ambiguities"))
    )
    return Service1LLMSemanticProposalV1(
        concept_proposals=concepts,
        relationship_proposals=relationships,
        duplicate_semantics=duplicates,
        irrelevant_refs=irrelevant,
        material_ambiguities=ambiguities,
    )


def _required_list(mapping: Mapping[str, Any], key: str) -> list[Any]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise _error("INVALID_LIST_FIELD", f"{key} must be a list")
    return value


def _parse_concept(value: Any, index: int) -> Service1LLMConceptProposalV1:
    item = _closed_mapping(value, field_name=f"concept_proposals[{index}]", allowed_keys=_CONCEPT_KEYS)
    return Service1LLMConceptProposalV1(
        proposal_id=_required_text(item.get("proposal_id"), field_name="proposal_id"),
        target_column_refs=_text_tuple(item.get("target_column_refs"), field_name="target_column_refs", min_items=1),
        semantic_role=_required_text(item.get("semantic_role"), field_name="semantic_role"),
        variable_name=_required_text(item.get("variable_name"), field_name="variable_name"),
        confidence=_confidence(item.get("confidence"), field_name="confidence"),
        rationale=_optional_text(item.get("rationale")),
        evidence_refs=_text_tuple(item.get("evidence_refs"), field_name="evidence_refs"),
    )


def _parse_relationship(value: Any, index: int) -> Service1LLMRelationshipProposalV1:
    item = _closed_mapping(value, field_name=f"relationship_proposals[{index}]", allowed_keys=_RELATIONSHIP_KEYS)
    left = _required_text(item.get("left_column_ref"), field_name="left_column_ref")
    right = _required_text(item.get("right_column_ref"), field_name="right_column_ref")
    if left == right:
        raise _error("SELF_RELATIONSHIP_FORBIDDEN", "relationship endpoints must be different")
    return Service1LLMRelationshipProposalV1(
        relationship_id=_required_text(item.get("relationship_id"), field_name="relationship_id"),
        left_column_ref=left,
        right_column_ref=right,
        relationship_type=_required_text(item.get("relationship_type"), field_name="relationship_type"),
        confidence=_confidence(item.get("confidence"), field_name="confidence"),
        rationale=_optional_text(item.get("rationale")),
        evidence_refs=_text_tuple(item.get("evidence_refs"), field_name="evidence_refs"),
    )


def _parse_duplicate(value: Any, index: int) -> Service1LLMDuplicateSemanticProposalV1:
    item = _closed_mapping(value, field_name=f"duplicate_semantics[{index}]", allowed_keys=_DUPLICATE_KEYS)
    return Service1LLMDuplicateSemanticProposalV1(
        duplicate_id=_required_text(item.get("duplicate_id"), field_name="duplicate_id"),
        column_refs=_text_tuple(item.get("column_refs"), field_name="column_refs", min_items=2),
        proposed_shared_role=_required_text(item.get("proposed_shared_role"), field_name="proposed_shared_role"),
        confidence=_confidence(item.get("confidence"), field_name="confidence"),
        rationale=_optional_text(item.get("rationale")),
        evidence_refs=_text_tuple(item.get("evidence_refs"), field_name="evidence_refs"),
    )


def _parse_ambiguity(value: Any, index: int) -> Service1LLMMaterialAmbiguityV1:
    item = _closed_mapping(value, field_name=f"material_ambiguities[{index}]", allowed_keys=_AMBIGUITY_KEYS)
    return Service1LLMMaterialAmbiguityV1(
        ambiguity_id=_required_text(item.get("ambiguity_id"), field_name="ambiguity_id"),
        target_refs=_text_tuple(item.get("target_refs"), field_name="target_refs", min_items=1),
        reason=_required_text(item.get("reason"), field_name="reason"),
        confidence=_confidence(item.get("confidence"), field_name="confidence"),
        evidence_refs=_text_tuple(item.get("evidence_refs"), field_name="evidence_refs"),
    )


__all__ = [
    "CONTEXT_SCHEMA_VERSION",
    "PROPOSAL_SCHEMA_VERSION",
    "SERVICE_NAME",
    "Service1LLMSemanticContractErrorV1",
    "Service1LLMSemanticContextV1",
    "Service1LLMConceptProposalV1",
    "Service1LLMRelationshipProposalV1",
    "Service1LLMDuplicateSemanticProposalV1",
    "Service1LLMMaterialAmbiguityV1",
    "Service1LLMSemanticProposalV1",
    "build_service_1_llm_semantic_context_v1",
    "parse_service_1_llm_semantic_proposal_v1",
]

"""Service 1 — Semantic Concept Catalog Candidate V1.

Pure projection of the semantic concept catalog contract into an inspectable
catalog candidate. It does not mutate JSON catalogs, map columns, authorize
runtime, wire frontend, execute formulas or generate delivery artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_semantic_concept_catalog_contract_v1 import (
    SCHEMA_VERSION as SOURCE_SCHEMA_VERSION,
    Service1SemanticConceptCatalogContractV1,
    Service1SemanticConceptDefinitionV1,
    build_service_1_semantic_concept_catalog_contract_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_CONCEPT_CATALOG_CANDIDATE_V1"
STATUS_READY: Final[str] = "SEMANTIC_CONCEPT_CATALOG_CANDIDATE_READY"


@dataclass(frozen=True)
class Service1SemanticConceptCatalogCandidateEntryV1:
    concept_id: str
    concept_kind: str
    business_definition: str
    exclusions: tuple[str, ...]
    required_data_type: str
    unit: str
    temporal_semantics: str
    formula_policy: str
    minimum_evidence_fields: tuple[str, ...]
    owner_confirmation_required: bool
    risk_if_wrong: str
    source_contract_schema_version: str
    canonical_candidate: bool = False
    engine_mapping_candidate: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "concept_id",
            "concept_kind",
            "business_definition",
            "required_data_type",
            "unit",
            "temporal_semantics",
            "formula_policy",
            "risk_if_wrong",
            "source_contract_schema_version",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not self.exclusions:
            raise ValueError("exclusions must not be empty")
        if not self.minimum_evidence_fields:
            raise ValueError("minimum_evidence_fields must not be empty")
        if self.owner_confirmation_required is not True:
            raise ValueError("owner_confirmation_required must remain True")
        if self.canonical_candidate is not False:
            raise ValueError("canonical_candidate must remain False")
        if self.engine_mapping_candidate is not False:
            raise ValueError("engine_mapping_candidate must remain False")
        if self.source_contract_schema_version != SOURCE_SCHEMA_VERSION:
            raise ValueError("invalid source_contract_schema_version")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1SemanticConceptCatalogCandidateV1:
    schema_version: str
    status: str
    source_contract_schema_version: str
    entries: tuple[Service1SemanticConceptCatalogCandidateEntryV1, ...]
    concept_count: int
    formula_independent_concept_count: int
    catalog_mutation_authorized: bool = False
    variable_catalog_mutation_authorized: bool = False
    formula_catalog_mutation_authorized: bool = False
    engine_mapping_authorized: bool = False
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("invalid schema_version")
        if self.status != STATUS_READY:
            raise ValueError("invalid status")
        if self.source_contract_schema_version != SOURCE_SCHEMA_VERSION:
            raise ValueError("invalid source_contract_schema_version")
        if not self.entries:
            raise ValueError("entries must not be empty")
        if len({entry.concept_id for entry in self.entries}) != len(self.entries):
            raise ValueError("concept_id values must be unique")
        if self.concept_count != len(self.entries):
            raise ValueError("concept_count must match entries")
        expected_formula_independent = sum(
            1 for entry in self.entries if entry.formula_policy == "not_applicable"
        )
        if self.formula_independent_concept_count != expected_formula_independent:
            raise ValueError("invalid formula_independent_concept_count")
        for field_name in (
            "catalog_mutation_authorized",
            "variable_catalog_mutation_authorized",
            "formula_catalog_mutation_authorized",
            "engine_mapping_authorized",
            "runtime_authorized",
            "frontend_wiring_authorized",
            "delivery_authorized",
        ):
            if getattr(self, field_name) is not False:
                raise ValueError(f"{field_name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _project_entry(
    concept: Service1SemanticConceptDefinitionV1,
) -> Service1SemanticConceptCatalogCandidateEntryV1:
    return Service1SemanticConceptCatalogCandidateEntryV1(
        concept_id=concept.concept_id,
        concept_kind=concept.concept_kind,
        business_definition=concept.business_definition,
        exclusions=tuple(concept.exclusions),
        required_data_type=concept.required_data_type,
        unit=concept.unit,
        temporal_semantics=concept.temporal_semantics,
        formula_policy=concept.formula_policy,
        minimum_evidence_fields=tuple(concept.minimum_evidence_fields),
        owner_confirmation_required=concept.owner_confirmation_required,
        risk_if_wrong=concept.risk_if_wrong,
        source_contract_schema_version=SOURCE_SCHEMA_VERSION,
        canonical_candidate=False,
        engine_mapping_candidate=False,
    )


def build_service_1_semantic_concept_catalog_candidate_v1(
    contract: Service1SemanticConceptCatalogContractV1 | None = None,
) -> Service1SemanticConceptCatalogCandidateV1:
    selected_contract = (
        build_service_1_semantic_concept_catalog_contract_v1()
        if contract is None
        else contract
    )
    if not isinstance(selected_contract, Service1SemanticConceptCatalogContractV1):
        raise ValueError("contract must be Service1SemanticConceptCatalogContractV1")

    entries = tuple(_project_entry(concept) for concept in selected_contract.concepts)
    return Service1SemanticConceptCatalogCandidateV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        source_contract_schema_version=SOURCE_SCHEMA_VERSION,
        entries=entries,
        concept_count=len(entries),
        formula_independent_concept_count=sum(
            1 for entry in entries if entry.formula_policy == "not_applicable"
        ),
        catalog_mutation_authorized=False,
        variable_catalog_mutation_authorized=False,
        formula_catalog_mutation_authorized=False,
        engine_mapping_authorized=False,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "projection_only": True,
            "source_contract_status": selected_contract.status,
            "existing_catalogs_mutated": False,
            "candidate_entries_are_not_canonical": True,
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "Service1SemanticConceptCatalogCandidateEntryV1",
    "Service1SemanticConceptCatalogCandidateV1",
    "build_service_1_semantic_concept_catalog_candidate_v1",
]

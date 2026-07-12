"""Service 1 — Semantic Concept Catalog Readiness Gate V1.

Pure fail-closed gate that evaluates whether semantic concept candidates have
sufficient governed evidence to proceed to corpus-binding tests. It does not
mutate catalogs, map columns, authorize runtime, wire frontend, or deliver files.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Mapping

from pymia.smartpyme.service_1_semantic_concept_catalog_candidate_v1 import (
    SCHEMA_VERSION as CANDIDATE_SCHEMA_VERSION,
    Service1SemanticConceptCatalogCandidateV1,
    build_service_1_semantic_concept_catalog_candidate_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_CONCEPT_CATALOG_READINESS_GATE_V1"
STATUS_READY: Final[str] = "SEMANTIC_CONCEPT_CATALOG_READINESS_EVALUATED"
READINESS_CORPUS_TEST_CANDIDATE: Final[str] = "CORPUS_TEST_CANDIDATE"
READINESS_BLOCKED_MISSING_EVIDENCE: Final[str] = "BLOCKED_MISSING_EVIDENCE"

STOCK_EVIDENCE_CONCEPTS: Final[frozenset[str]] = frozenset(
    {"opening_stock_quantity", "closing_stock_quantity"}
)


@dataclass(frozen=True)
class Service1SemanticConceptReadinessResultV1:
    concept_id: str
    readiness_status: str
    governed_definition_present: bool
    evidence_contract_present: bool
    positive_cases_present: bool
    ambiguous_cases_present: bool
    negative_cases_present: bool
    corpus_binding_test_candidate: bool
    blocking_reasons: tuple[str, ...]
    engine_mapping_authorized: bool = False
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.concept_id, str) or not self.concept_id.strip():
            raise ValueError("concept_id must be a non-empty string")
        if self.readiness_status not in {
            READINESS_CORPUS_TEST_CANDIDATE,
            READINESS_BLOCKED_MISSING_EVIDENCE,
        }:
            raise ValueError("unsupported readiness_status")
        if self.governed_definition_present is not True:
            raise ValueError("governed_definition_present must remain True")
        ready = self.readiness_status == READINESS_CORPUS_TEST_CANDIDATE
        required_flags = (
            self.evidence_contract_present,
            self.positive_cases_present,
            self.ambiguous_cases_present,
            self.negative_cases_present,
        )
        if ready:
            if not all(flag is True for flag in required_flags):
                raise ValueError("ready concepts require complete evidence cases")
            if self.corpus_binding_test_candidate is not True:
                raise ValueError("ready concepts must be corpus test candidates")
            if self.blocking_reasons:
                raise ValueError("ready concepts cannot have blocking_reasons")
        else:
            if self.corpus_binding_test_candidate is not False:
                raise ValueError("blocked concepts cannot be corpus test candidates")
            if not self.blocking_reasons:
                raise ValueError("blocked concepts require blocking_reasons")
        for field_name in (
            "engine_mapping_authorized",
            "runtime_authorized",
            "frontend_wiring_authorized",
        ):
            if getattr(self, field_name) is not False:
                raise ValueError(f"{field_name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1SemanticConceptCatalogReadinessGateV1:
    schema_version: str
    status: str
    source_candidate_schema_version: str
    results: tuple[Service1SemanticConceptReadinessResultV1, ...]
    concept_count: int
    corpus_test_candidate_count: int
    blocked_count: int
    catalog_mutation_authorized: bool = False
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
        if self.source_candidate_schema_version != CANDIDATE_SCHEMA_VERSION:
            raise ValueError("invalid source_candidate_schema_version")
        if not self.results:
            raise ValueError("results must not be empty")
        if len({result.concept_id for result in self.results}) != len(self.results):
            raise ValueError("concept_id values must be unique")
        if self.concept_count != len(self.results):
            raise ValueError("concept_count must match results")
        expected_ready = sum(
            1 for result in self.results if result.corpus_binding_test_candidate
        )
        expected_blocked = self.concept_count - expected_ready
        if self.corpus_test_candidate_count != expected_ready:
            raise ValueError("invalid corpus_test_candidate_count")
        if self.blocked_count != expected_blocked:
            raise ValueError("invalid blocked_count")
        for field_name in (
            "catalog_mutation_authorized",
            "engine_mapping_authorized",
            "runtime_authorized",
            "frontend_wiring_authorized",
            "delivery_authorized",
        ):
            if getattr(self, field_name) is not False:
                raise ValueError(f"{field_name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _build_result(
    concept_id: str,
    evidence_state: Mapping[str, bool],
) -> Service1SemanticConceptReadinessResultV1:
    evidence_contract_present = bool(evidence_state.get("evidence_contract_present", False))
    positive_cases_present = bool(evidence_state.get("positive_cases_present", False))
    ambiguous_cases_present = bool(evidence_state.get("ambiguous_cases_present", False))
    negative_cases_present = bool(evidence_state.get("negative_cases_present", False))
    complete = all(
        (
            evidence_contract_present,
            positive_cases_present,
            ambiguous_cases_present,
            negative_cases_present,
        )
    )
    if complete:
        return Service1SemanticConceptReadinessResultV1(
            concept_id=concept_id,
            readiness_status=READINESS_CORPUS_TEST_CANDIDATE,
            governed_definition_present=True,
            evidence_contract_present=True,
            positive_cases_present=True,
            ambiguous_cases_present=True,
            negative_cases_present=True,
            corpus_binding_test_candidate=True,
            blocking_reasons=(),
        )

    missing = tuple(
        field_name
        for field_name, present in (
            ("evidence_contract_missing", evidence_contract_present),
            ("positive_cases_missing", positive_cases_present),
            ("ambiguous_cases_missing", ambiguous_cases_present),
            ("negative_cases_missing", negative_cases_present),
        )
        if not present
    )
    return Service1SemanticConceptReadinessResultV1(
        concept_id=concept_id,
        readiness_status=READINESS_BLOCKED_MISSING_EVIDENCE,
        governed_definition_present=True,
        evidence_contract_present=evidence_contract_present,
        positive_cases_present=positive_cases_present,
        ambiguous_cases_present=ambiguous_cases_present,
        negative_cases_present=negative_cases_present,
        corpus_binding_test_candidate=False,
        blocking_reasons=missing,
    )


def build_service_1_semantic_concept_catalog_readiness_gate_v1(
    candidate: Service1SemanticConceptCatalogCandidateV1 | None = None,
    evidence_by_concept: Mapping[str, Mapping[str, bool]] | None = None,
) -> Service1SemanticConceptCatalogReadinessGateV1:
    selected_candidate = (
        build_service_1_semantic_concept_catalog_candidate_v1()
        if candidate is None
        else candidate
    )
    if not isinstance(selected_candidate, Service1SemanticConceptCatalogCandidateV1):
        raise ValueError("candidate must be Service1SemanticConceptCatalogCandidateV1")

    default_evidence = {
        concept_id: {
            "evidence_contract_present": True,
            "positive_cases_present": True,
            "ambiguous_cases_present": True,
            "negative_cases_present": True,
        }
        for concept_id in STOCK_EVIDENCE_CONCEPTS
    }
    selected_evidence = default_evidence if evidence_by_concept is None else evidence_by_concept

    results = tuple(
        _build_result(entry.concept_id, selected_evidence.get(entry.concept_id, {}))
        for entry in selected_candidate.entries
    )
    ready_count = sum(1 for result in results if result.corpus_binding_test_candidate)
    return Service1SemanticConceptCatalogReadinessGateV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        source_candidate_schema_version=CANDIDATE_SCHEMA_VERSION,
        results=results,
        concept_count=len(results),
        corpus_test_candidate_count=ready_count,
        blocked_count=len(results) - ready_count,
        catalog_mutation_authorized=False,
        engine_mapping_authorized=False,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "readiness_is_for_corpus_tests_only": True,
            "canonicalization_authorized": False,
            "stock_evidence_source": "SERVICE_1_STOCK_MOVEMENT_EVIDENCE_PACKET_V1",
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "READINESS_CORPUS_TEST_CANDIDATE",
    "READINESS_BLOCKED_MISSING_EVIDENCE",
    "Service1SemanticConceptReadinessResultV1",
    "Service1SemanticConceptCatalogReadinessGateV1",
    "build_service_1_semantic_concept_catalog_readiness_gate_v1",
]

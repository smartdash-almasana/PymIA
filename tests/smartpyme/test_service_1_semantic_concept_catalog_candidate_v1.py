from __future__ import annotations

import importlib

import pytest

from pymia.smartpyme.service_1_semantic_concept_catalog_candidate_v1 import (
    SCHEMA_VERSION,
    STATUS_READY,
    Service1SemanticConceptCatalogCandidateEntryV1,
    Service1SemanticConceptCatalogCandidateV1,
    build_service_1_semantic_concept_catalog_candidate_v1,
)
from pymia.smartpyme.service_1_semantic_concept_catalog_contract_v1 import (
    SCHEMA_VERSION as SOURCE_SCHEMA_VERSION,
    build_service_1_semantic_concept_catalog_contract_v1,
)


def test_candidate_projects_every_contract_concept_without_redefinition() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()
    candidate = build_service_1_semantic_concept_catalog_candidate_v1(contract)

    assert candidate.schema_version == SCHEMA_VERSION
    assert candidate.status == STATUS_READY
    assert candidate.source_contract_schema_version == SOURCE_SCHEMA_VERSION
    assert candidate.concept_count == len(contract.concepts) == 6
    assert [entry.concept_id for entry in candidate.entries] == [
        concept.concept_id for concept in contract.concepts
    ]
    assert all(
        entry.source_contract_schema_version == SOURCE_SCHEMA_VERSION
        and entry.canonical_candidate is False
        and entry.engine_mapping_candidate is False
        for entry in candidate.entries
    )


def test_candidate_preserves_contract_semantics_exactly() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()
    candidate = build_service_1_semantic_concept_catalog_candidate_v1(contract)

    for concept, entry in zip(contract.concepts, candidate.entries, strict=True):
        assert entry.concept_id == concept.concept_id
        assert entry.concept_kind == concept.concept_kind
        assert entry.business_definition == concept.business_definition
        assert entry.exclusions == concept.exclusions
        assert entry.required_data_type == concept.required_data_type
        assert entry.unit == concept.unit
        assert entry.temporal_semantics == concept.temporal_semantics
        assert entry.formula_policy == concept.formula_policy
        assert entry.minimum_evidence_fields == concept.minimum_evidence_fields
        assert entry.owner_confirmation_required is True
        assert entry.risk_if_wrong == concept.risk_if_wrong


def test_candidate_counts_formula_independent_concepts() -> None:
    candidate = build_service_1_semantic_concept_catalog_candidate_v1()

    assert candidate.formula_independent_concept_count == 4
    assert {
        entry.concept_id
        for entry in candidate.entries
        if entry.formula_policy == "not_applicable"
    } == {
        "customer_identifier",
        "supplier_identifier",
        "payment_method_classification",
        "business_period",
    }


def test_candidate_is_fail_closed_and_projection_only() -> None:
    candidate = build_service_1_semantic_concept_catalog_candidate_v1()

    assert candidate.catalog_mutation_authorized is False
    assert candidate.variable_catalog_mutation_authorized is False
    assert candidate.formula_catalog_mutation_authorized is False
    assert candidate.engine_mapping_authorized is False
    assert candidate.runtime_authorized is False
    assert candidate.frontend_wiring_authorized is False
    assert candidate.delivery_authorized is False
    assert candidate.metadata["projection_only"] is True
    assert candidate.metadata["existing_catalogs_mutated"] is False
    assert candidate.metadata["candidate_entries_are_not_canonical"] is True
    assert all(entry.canonical_candidate is False for entry in candidate.entries)
    assert all(entry.engine_mapping_candidate is False for entry in candidate.entries)


def test_candidate_is_deterministic_and_does_not_mutate_contract() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()
    before = contract.to_dict()

    first = build_service_1_semantic_concept_catalog_candidate_v1(contract).to_dict()
    second = build_service_1_semantic_concept_catalog_candidate_v1(contract).to_dict()

    assert first == second
    assert contract.to_dict() == before


def test_candidate_rejects_wrong_contract_type() -> None:
    with pytest.raises(ValueError):
        build_service_1_semantic_concept_catalog_candidate_v1({})  # type: ignore[arg-type]


def test_entry_and_catalog_guards_reject_open_authorization() -> None:
    base_entry = build_service_1_semantic_concept_catalog_candidate_v1().entries[0]
    with pytest.raises(ValueError):
        Service1SemanticConceptCatalogCandidateEntryV1(
            **(base_entry.to_dict() | {"canonical_candidate": True})
        )

    candidate = build_service_1_semantic_concept_catalog_candidate_v1()
    with pytest.raises(ValueError):
        Service1SemanticConceptCatalogCandidateV1(
            schema_version=candidate.schema_version,
            status=candidate.status,
            source_contract_schema_version=candidate.source_contract_schema_version,
            entries=candidate.entries,
            concept_count=candidate.concept_count,
            formula_independent_concept_count=candidate.formula_independent_concept_count,
            catalog_mutation_authorized=candidate.catalog_mutation_authorized,
            variable_catalog_mutation_authorized=candidate.variable_catalog_mutation_authorized,
            formula_catalog_mutation_authorized=candidate.formula_catalog_mutation_authorized,
            engine_mapping_authorized=candidate.engine_mapping_authorized,
            runtime_authorized=True,
            frontend_wiring_authorized=candidate.frontend_wiring_authorized,
            delivery_authorized=candidate.delivery_authorized,
            metadata=candidate.metadata,
        )


def test_module_has_no_io_frontend_runtime_or_catalog_writer_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_semantic_concept_catalog_candidate_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_concept_catalog_candidate_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "requests.",
        "urllib",
        "subprocess",
        "os.system",
        "open(",
        "json.dump",
        "write_text",
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
        "import openai",
        "import anthropic",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION

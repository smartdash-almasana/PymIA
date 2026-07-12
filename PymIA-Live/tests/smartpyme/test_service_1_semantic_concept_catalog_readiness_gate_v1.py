from __future__ import annotations

from dataclasses import replace

import pytest

from pymia.smartpyme.service_1_semantic_concept_catalog_candidate_v1 import (
    build_service_1_semantic_concept_catalog_candidate_v1,
)
from pymia.smartpyme.service_1_semantic_concept_catalog_readiness_gate_v1 import (
    READINESS_BLOCKED_MISSING_EVIDENCE,
    READINESS_CORPUS_TEST_CANDIDATE,
    SCHEMA_VERSION,
    STATUS_READY,
    Service1SemanticConceptCatalogReadinessGateV1,
    Service1SemanticConceptReadinessResultV1,
    build_service_1_semantic_concept_catalog_readiness_gate_v1,
)


def test_default_gate_marks_only_stock_boundary_concepts_ready_for_corpus_tests() -> None:
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1()
    by_id = {result.concept_id: result for result in gate.results}

    assert gate.schema_version == SCHEMA_VERSION
    assert gate.status == STATUS_READY
    assert gate.concept_count == 6
    assert gate.corpus_test_candidate_count == 2
    assert gate.blocked_count == 4
    assert by_id["opening_stock_quantity"].readiness_status == READINESS_CORPUS_TEST_CANDIDATE
    assert by_id["closing_stock_quantity"].readiness_status == READINESS_CORPUS_TEST_CANDIDATE
    assert by_id["customer_identifier"].readiness_status == READINESS_BLOCKED_MISSING_EVIDENCE
    assert by_id["supplier_identifier"].readiness_status == READINESS_BLOCKED_MISSING_EVIDENCE
    assert by_id["payment_method_classification"].readiness_status == READINESS_BLOCKED_MISSING_EVIDENCE
    assert by_id["business_period"].readiness_status == READINESS_BLOCKED_MISSING_EVIDENCE


def test_ready_results_require_complete_positive_ambiguous_and_negative_cases() -> None:
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1()
    ready = [result for result in gate.results if result.corpus_binding_test_candidate]

    assert len(ready) == 2
    for result in ready:
        assert result.evidence_contract_present is True
        assert result.positive_cases_present is True
        assert result.ambiguous_cases_present is True
        assert result.negative_cases_present is True
        assert result.blocking_reasons == ()


def test_missing_single_evidence_dimension_blocks_concept() -> None:
    evidence = {
        "opening_stock_quantity": {
            "evidence_contract_present": True,
            "positive_cases_present": True,
            "ambiguous_cases_present": False,
            "negative_cases_present": True,
        }
    }
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1(
        evidence_by_concept=evidence
    )
    result = gate.results[0]

    assert result.readiness_status == READINESS_BLOCKED_MISSING_EVIDENCE
    assert result.corpus_binding_test_candidate is False
    assert result.blocking_reasons == ("ambiguous_cases_missing",)


def test_explicit_evidence_can_prepare_non_stock_concept_for_corpus_tests_only() -> None:
    evidence = {
        "customer_identifier": {
            "evidence_contract_present": True,
            "positive_cases_present": True,
            "ambiguous_cases_present": True,
            "negative_cases_present": True,
        }
    }
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1(
        evidence_by_concept=evidence
    )
    by_id = {result.concept_id: result for result in gate.results}

    assert by_id["customer_identifier"].corpus_binding_test_candidate is True
    assert gate.engine_mapping_authorized is False
    assert gate.runtime_authorized is False
    assert gate.frontend_wiring_authorized is False


def test_wrong_candidate_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_service_1_semantic_concept_catalog_readiness_gate_v1(candidate={})  # type: ignore[arg-type]


def test_result_rejects_ready_status_without_complete_evidence() -> None:
    with pytest.raises(ValueError):
        Service1SemanticConceptReadinessResultV1(
            concept_id="x",
            readiness_status=READINESS_CORPUS_TEST_CANDIDATE,
            governed_definition_present=True,
            evidence_contract_present=True,
            positive_cases_present=True,
            ambiguous_cases_present=False,
            negative_cases_present=True,
            corpus_binding_test_candidate=True,
            blocking_reasons=(),
        )


def test_gate_rejects_open_authorization() -> None:
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1()
    with pytest.raises(ValueError):
        replace(gate, runtime_authorized=True)


def test_gate_counts_are_derived_from_results() -> None:
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1()
    with pytest.raises(ValueError):
        Service1SemanticConceptCatalogReadinessGateV1(
            schema_version=gate.schema_version,
            status=gate.status,
            source_candidate_schema_version=gate.source_candidate_schema_version,
            results=gate.results,
            concept_count=gate.concept_count,
            corpus_test_candidate_count=99,
            blocked_count=gate.blocked_count,
            metadata=gate.metadata,
        )


def test_candidate_order_and_identity_are_preserved() -> None:
    candidate = build_service_1_semantic_concept_catalog_candidate_v1()
    gate = build_service_1_semantic_concept_catalog_readiness_gate_v1(candidate=candidate)

    assert tuple(result.concept_id for result in gate.results) == tuple(
        entry.concept_id for entry in candidate.entries
    )

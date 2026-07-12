from __future__ import annotations

import importlib

import pytest

from pymia.smartpyme.service_1_semantic_concept_catalog_contract_v1 import (
    FORMULA_NOT_APPLICABLE,
    FORMULA_OPTIONAL,
    KIND_CLASSIFICATION,
    KIND_IDENTIFIER,
    KIND_MEASURE,
    KIND_TEMPORAL,
    SCHEMA_VERSION,
    STATUS_READY,
    Service1SemanticConceptCatalogContractV1,
    Service1SemanticConceptDefinitionV1,
    build_service_1_semantic_concept_catalog_contract_v1,
)


def test_contract_separates_semantic_concepts_from_formula_membership() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()

    assert contract.schema_version == SCHEMA_VERSION
    assert contract.status == STATUS_READY
    assert contract.formulas_consume_concepts is True
    assert contract.concepts_require_formula_membership is False
    assert contract.metadata["separates_semantic_concepts_from_formulas"] is True


def test_contract_contains_multiple_semantic_kinds() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()
    by_id = {concept.concept_id: concept for concept in contract.concepts}

    assert by_id["opening_stock_quantity"].concept_kind == KIND_MEASURE
    assert by_id["opening_stock_quantity"].formula_policy == FORMULA_OPTIONAL
    assert by_id["customer_identifier"].concept_kind == KIND_IDENTIFIER
    assert by_id["customer_identifier"].formula_policy == FORMULA_NOT_APPLICABLE
    assert by_id["supplier_identifier"].concept_kind == KIND_IDENTIFIER
    assert by_id["payment_method_classification"].concept_kind == KIND_CLASSIFICATION
    assert by_id["business_period"].concept_kind == KIND_TEMPORAL


def test_non_measure_concepts_can_exist_without_formula() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()

    assert contract.identifiers_may_exist_without_formula is True
    assert contract.classifications_may_exist_without_formula is True
    assert contract.dimensions_may_exist_without_formula is True
    assert contract.temporal_concepts_may_exist_without_formula is True


def test_every_concept_is_fail_closed_and_evidence_bound() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()

    assert contract.concepts
    assert all(concept.owner_confirmation_required is True for concept in contract.concepts)
    assert all(concept.canonical_candidate is False for concept in contract.concepts)
    assert all(concept.minimum_evidence_fields for concept in contract.concepts)
    assert all(concept.exclusions for concept in contract.concepts)
    assert len({concept.concept_id for concept in contract.concepts}) == len(contract.concepts)


def test_all_authorization_flags_remain_false() -> None:
    contract = build_service_1_semantic_concept_catalog_contract_v1()

    assert contract.catalog_mutation_authorized is False
    assert contract.variable_catalog_mutation_authorized is False
    assert contract.formula_catalog_mutation_authorized is False
    assert contract.engine_mapping_authorized is False
    assert contract.runtime_authorized is False
    assert contract.frontend_wiring_authorized is False
    assert contract.delivery_authorized is False


def test_definition_rejects_formula_required_for_identifier() -> None:
    with pytest.raises(ValueError, match="non-measure concepts cannot require a formula"):
        Service1SemanticConceptDefinitionV1(
            concept_id="customer_identifier",
            concept_kind=KIND_IDENTIFIER,
            business_definition="Stable customer identifier.",
            exclusions=("Not free text.",),
            required_data_type="text",
            unit="identifier",
            temporal_semantics="not_applicable",
            formula_policy="required",
            minimum_evidence_fields=("customer_identifier",),
            owner_confirmation_required=True,
            risk_if_wrong="Breaks matching.",
        )


def test_definition_rejects_premature_candidate_authorization() -> None:
    with pytest.raises(ValueError, match="canonical_candidate must remain False"):
        Service1SemanticConceptDefinitionV1(
            concept_id="opening_stock_quantity",
            concept_kind=KIND_MEASURE,
            business_definition="Opening stock.",
            exclusions=("Not average stock.",),
            required_data_type="number",
            unit="quantity",
            temporal_semantics="point_in_time",
            formula_policy=FORMULA_OPTIONAL,
            minimum_evidence_fields=("opening_quantity",),
            owner_confirmation_required=True,
            risk_if_wrong="Breaks reconciliation.",
            canonical_candidate=True,
        )


def test_contract_rejects_open_authorization_flag() -> None:
    baseline = build_service_1_semantic_concept_catalog_contract_v1()

    with pytest.raises(ValueError, match="runtime_authorized must remain False"):
        Service1SemanticConceptCatalogContractV1(
            **{**baseline.to_dict(), "concepts": baseline.concepts, "runtime_authorized": True}
        )


def test_contract_is_deterministic() -> None:
    assert (
        build_service_1_semantic_concept_catalog_contract_v1().to_dict()
        == build_service_1_semantic_concept_catalog_contract_v1().to_dict()
    )


def test_module_has_no_io_frontend_runtime_or_llm_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_semantic_concept_catalog_contract_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_concept_catalog_contract_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "requests.",
        "urllib",
        "subprocess",
        "os.system",
        "import openai",
        "import anthropic",
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION

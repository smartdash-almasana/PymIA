from __future__ import annotations

import importlib

import pytest

from pymia.smartpyme.service_1_stock_movement_semantic_contract_v1 import (
    CONCEPT_ADJUSTMENT,
    CONCEPT_CLOSING_STOCK,
    CONCEPT_INBOUND_MOVEMENT,
    CONCEPT_OPENING_STOCK,
    CONCEPT_OUTBOUND_MOVEMENT,
    RECONCILIATION_IDENTITY,
    SCHEMA_VERSION,
    STATUS_READY,
    TEMPORAL_PERIOD_FLOW,
    TEMPORAL_POINT_IN_TIME,
    Service1StockMovementConceptV1,
    Service1StockMovementSemanticContractV1,
    build_service_1_stock_movement_semantic_contract_v1,
)


def test_contract_builds_exact_stock_movement_sequence() -> None:
    contract = build_service_1_stock_movement_semantic_contract_v1()

    assert contract.schema_version == SCHEMA_VERSION
    assert contract.status == STATUS_READY
    assert tuple(concept.concept_id for concept in contract.concepts) == (
        CONCEPT_OPENING_STOCK,
        CONCEPT_INBOUND_MOVEMENT,
        CONCEPT_OUTBOUND_MOVEMENT,
        CONCEPT_ADJUSTMENT,
        CONCEPT_CLOSING_STOCK,
    )
    assert contract.reconciliation_identity == RECONCILIATION_IDENTITY


def test_contract_distinguishes_point_in_time_from_period_flows() -> None:
    contract = build_service_1_stock_movement_semantic_contract_v1()
    by_id = {concept.concept_id: concept for concept in contract.concepts}

    assert by_id[CONCEPT_OPENING_STOCK].temporal_semantics == TEMPORAL_POINT_IN_TIME
    assert by_id[CONCEPT_CLOSING_STOCK].temporal_semantics == TEMPORAL_POINT_IN_TIME
    assert by_id[CONCEPT_INBOUND_MOVEMENT].temporal_semantics == TEMPORAL_PERIOD_FLOW
    assert by_id[CONCEPT_OUTBOUND_MOVEMENT].temporal_semantics == TEMPORAL_PERIOD_FLOW
    assert by_id[CONCEPT_ADJUSTMENT].temporal_semantics == TEMPORAL_PERIOD_FLOW


def test_contract_requires_item_period_and_movement_classification() -> None:
    contract = build_service_1_stock_movement_semantic_contract_v1()
    by_id = {concept.concept_id: concept for concept in contract.concepts}

    assert contract.mandatory_dimensions == ("item_identifier", "period_reference")
    assert contract.movement_classification_required is True
    assert "movement_class" in by_id[CONCEPT_INBOUND_MOVEMENT].minimum_evidence_fields
    assert "movement_class" in by_id[CONCEPT_OUTBOUND_MOVEMENT].minimum_evidence_fields
    assert "adjustment_reason" in by_id[CONCEPT_ADJUSTMENT].minimum_evidence_fields


def test_contract_is_owner_confirmed_and_fail_closed() -> None:
    contract = build_service_1_stock_movement_semantic_contract_v1()

    assert all(concept.owner_confirmation_required is True for concept in contract.concepts)
    assert all(concept.catalog_extension_candidate is False for concept in contract.concepts)
    assert contract.negative_stock_requires_owner_confirmation is True
    assert contract.missing_movements_block_reconciliation is True
    assert contract.catalog_mutation_authorized is False
    assert contract.engine_mapping_authorized is False
    assert contract.runtime_authorized is False
    assert contract.frontend_wiring_authorized is False
    assert contract.delivery_authorized is False


def test_contract_does_not_claim_physical_stock_confirmation() -> None:
    contract = build_service_1_stock_movement_semantic_contract_v1()

    assert contract.metadata["stock_physical_count_confirmed"] is False
    opening = contract.concepts[0]
    closing = contract.concepts[-1]
    assert any("conteo fisico" in exclusion for exclusion in opening.exclusions)
    assert any("conteo fisico" in exclusion for exclusion in closing.exclusions)


def test_contract_is_deterministic_and_serializable() -> None:
    first = build_service_1_stock_movement_semantic_contract_v1()
    second = build_service_1_stock_movement_semantic_contract_v1()

    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["concepts"][0]["concept_id"] == CONCEPT_OPENING_STOCK


def test_concept_rejects_open_guards_and_missing_evidence() -> None:
    with pytest.raises(ValueError):
        Service1StockMovementConceptV1(
            concept_id="bad",
            business_definition="Definition",
            exclusions=("Not another thing",),
            temporal_semantics=TEMPORAL_PERIOD_FLOW,
            unit="quantity",
            required_data_type="number",
            minimum_evidence_fields=(),
            owner_confirmation_required=True,
            risk_if_wrong="Risk",
        )
    with pytest.raises(ValueError):
        Service1StockMovementConceptV1(
            concept_id="bad",
            business_definition="Definition",
            exclusions=("Not another thing",),
            temporal_semantics=TEMPORAL_PERIOD_FLOW,
            unit="quantity",
            required_data_type="number",
            minimum_evidence_fields=("item_identifier",),
            owner_confirmation_required=False,
            risk_if_wrong="Risk",
        )


def test_contract_rejects_catalog_or_runtime_authorization() -> None:
    base = build_service_1_stock_movement_semantic_contract_v1()
    payload = base.to_dict()
    payload["concepts"] = tuple(base.concepts)
    payload["catalog_mutation_authorized"] = True

    with pytest.raises(ValueError):
        Service1StockMovementSemanticContractV1(**payload)


def test_module_has_no_catalog_io_runtime_or_frontend_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_stock_movement_semantic_contract_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_stock_movement_semantic_contract_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "open(",
        "json.load",
        "requests.",
        "subprocess",
        "formula_catalog.v1.json",
        "service_1_semantic_variable_catalog.v1.json",
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION

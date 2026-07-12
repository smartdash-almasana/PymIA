from __future__ import annotations

import importlib

import pytest

from pymia.smartpyme.service_1_stock_movement_evidence_packet_v1 import (
    SCHEMA_VERSION,
    STATUS_BLOCKED,
    STATUS_READY,
    Service1StockMovementEvidenceInputV1,
    build_service_1_stock_movement_evidence_packet_v1,
)


def _complete_input(**overrides):
    values = {
        "item_identifier": "SKU-1",
        "period_start": "2026-06-01",
        "period_end": "2026-06-30",
        "opening_quantity": 100,
        "inbound_quantity": 20,
        "outbound_quantity": 15,
        "adjustment_quantity": -2,
        "closing_quantity": 103,
        "movement_classification_complete": True,
        "owner_confirmed": True,
        "physical_count_confirmed": False,
    }
    values.update(overrides)
    return Service1StockMovementEvidenceInputV1(**values)


def test_complete_packet_is_reconciliation_ready_but_not_authorized() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(_complete_input())

    assert packet.schema_version == SCHEMA_VERSION
    assert packet.status == STATUS_READY
    assert packet.reconciliation_ready is True
    assert packet.theoretical_closing_quantity == 103.0
    assert packet.declared_closing_quantity == 103.0
    assert packet.reconciliation_difference == 0.0
    assert packet.owner_confirmation_required is False
    assert packet.catalog_extension_candidate is False
    assert packet.catalog_mutation_authorized is False
    assert packet.engine_mapping_authorized is False
    assert packet.runtime_authorized is False
    assert packet.frontend_wiring_authorized is False
    assert packet.delivery_authorized is False


def test_missing_owner_confirmation_blocks_reconciliation() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(
        _complete_input(owner_confirmed=False)
    )

    assert packet.status == STATUS_BLOCKED
    assert packet.reconciliation_ready is False
    assert packet.owner_confirmation_required is True


def test_missing_movement_classification_blocks_reconciliation() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(
        _complete_input(movement_classification_complete=False)
    )

    assert packet.status == STATUS_BLOCKED
    assert "movement_classification_complete" in packet.missing_fields


def test_missing_dimension_and_numeric_fields_are_reported() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(
        Service1StockMovementEvidenceInputV1()
    )

    assert packet.status == STATUS_BLOCKED
    assert set(packet.missing_fields) == {
        "item_identifier",
        "period_start",
        "period_end",
        "opening_quantity",
        "inbound_quantity",
        "outbound_quantity",
        "adjustment_quantity",
        "closing_quantity",
        "movement_classification_complete",
    }
    assert packet.present_concepts == ()


def test_difference_is_observed_without_authorizing_any_action() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(
        _complete_input(closing_quantity=99)
    )

    assert packet.status == STATUS_READY
    assert packet.reconciliation_difference == -4.0
    assert packet.runtime_authorized is False
    assert packet.delivery_authorized is False


def test_negative_closing_stock_is_flagged_but_not_interpreted() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(
        _complete_input(opening_quantity=1, inbound_quantity=0, outbound_quantity=3, adjustment_quantity=0, closing_quantity=-2)
    )

    assert packet.metadata["negative_closing_stock"] is True
    assert packet.reconciliation_difference == 0.0
    assert packet.physical_count_confirmed is False


def test_physical_count_is_separate_from_theoretical_reconciliation() -> None:
    packet = build_service_1_stock_movement_evidence_packet_v1(
        _complete_input(physical_count_confirmed=True)
    )

    assert packet.physical_count_confirmed is True
    assert packet.metadata["physical_count_is_separate_from_theoretical_reconciliation"] is True


def test_invalid_input_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_service_1_stock_movement_evidence_packet_v1({})  # type: ignore[arg-type]


def test_packet_is_deterministic() -> None:
    evidence = _complete_input()
    first = build_service_1_stock_movement_evidence_packet_v1(evidence).to_dict()
    second = build_service_1_stock_movement_evidence_packet_v1(evidence).to_dict()
    assert first == second


def test_module_has_no_io_catalog_mutation_or_frontend_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_stock_movement_evidence_packet_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_stock_movement_evidence_packet_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "requests.",
        "urllib",
        "subprocess",
        "os.system",
        "open(",
        "json.dump",
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
        "import openai",
        "import anthropic",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION

"""Service 1 — Stock Movement Evidence Packet V1.

Pure evidence evaluator for the stock movement semantic contract.
No catalog mutation, engine mapping, runtime, frontend, I/O or delivery.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_stock_movement_semantic_contract_v1 import (
    CONCEPT_ADJUSTMENT,
    CONCEPT_CLOSING_STOCK,
    CONCEPT_INBOUND_MOVEMENT,
    CONCEPT_OPENING_STOCK,
    CONCEPT_OUTBOUND_MOVEMENT,
    RECONCILIATION_IDENTITY,
    build_service_1_stock_movement_semantic_contract_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_STOCK_MOVEMENT_EVIDENCE_PACKET_V1"
STATUS_READY: Final[str] = "STOCK_MOVEMENT_EVIDENCE_PACKET_READY"
STATUS_BLOCKED: Final[str] = "STOCK_MOVEMENT_EVIDENCE_PACKET_BLOCKED"


@dataclass(frozen=True)
class Service1StockMovementEvidenceInputV1:
    item_identifier: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    opening_quantity: float | int | None = None
    inbound_quantity: float | int | None = None
    outbound_quantity: float | int | None = None
    adjustment_quantity: float | int | None = None
    closing_quantity: float | int | None = None
    movement_classification_complete: bool = False
    owner_confirmed: bool = False
    physical_count_confirmed: bool = False


@dataclass(frozen=True)
class Service1StockMovementEvidencePacketV1:
    schema_version: str
    status: str
    present_concepts: tuple[str, ...]
    missing_fields: tuple[str, ...]
    reconciliation_identity: str
    theoretical_closing_quantity: float | None
    declared_closing_quantity: float | None
    reconciliation_difference: float | None
    reconciliation_ready: bool
    owner_confirmation_required: bool
    physical_count_confirmed: bool
    catalog_extension_candidate: bool = False
    catalog_mutation_authorized: bool = False
    engine_mapping_authorized: bool = False
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_stock_movement_evidence_packet_v1(
    evidence: Service1StockMovementEvidenceInputV1,
) -> Service1StockMovementEvidencePacketV1:
    if not isinstance(evidence, Service1StockMovementEvidenceInputV1):
        raise ValueError("evidence must be Service1StockMovementEvidenceInputV1")

    contract = build_service_1_stock_movement_semantic_contract_v1()
    present: list[str] = []
    missing: list[str] = []

    if evidence.item_identifier and evidence.item_identifier.strip():
        pass
    else:
        missing.append("item_identifier")
    if evidence.period_start and evidence.period_start.strip():
        pass
    else:
        missing.append("period_start")
    if evidence.period_end and evidence.period_end.strip():
        pass
    else:
        missing.append("period_end")

    numeric_fields = {
        CONCEPT_OPENING_STOCK: ("opening_quantity", evidence.opening_quantity),
        CONCEPT_INBOUND_MOVEMENT: ("inbound_quantity", evidence.inbound_quantity),
        CONCEPT_OUTBOUND_MOVEMENT: ("outbound_quantity", evidence.outbound_quantity),
        CONCEPT_ADJUSTMENT: ("adjustment_quantity", evidence.adjustment_quantity),
        CONCEPT_CLOSING_STOCK: ("closing_quantity", evidence.closing_quantity),
    }
    for concept_id, (field_name, value) in numeric_fields.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            missing.append(field_name)
        else:
            present.append(concept_id)

    if not evidence.movement_classification_complete:
        missing.append("movement_classification_complete")

    required_for_reconciliation = (
        evidence.opening_quantity,
        evidence.inbound_quantity,
        evidence.outbound_quantity,
        evidence.adjustment_quantity,
        evidence.closing_quantity,
    )
    numerics_complete = all(
        isinstance(value, (int, float)) and not isinstance(value, bool)
        for value in required_for_reconciliation
    )
    dimensions_complete = not any(
        field in missing for field in ("item_identifier", "period_start", "period_end")
    )
    reconciliation_ready = (
        numerics_complete
        and dimensions_complete
        and evidence.movement_classification_complete
        and evidence.owner_confirmed
    )

    theoretical: float | None = None
    declared: float | None = None
    difference: float | None = None
    if numerics_complete:
        theoretical = float(evidence.opening_quantity) + float(evidence.inbound_quantity) - float(evidence.outbound_quantity) + float(evidence.adjustment_quantity)
        declared = float(evidence.closing_quantity)
        difference = round(declared - theoretical, 10)

    return Service1StockMovementEvidencePacketV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY if reconciliation_ready else STATUS_BLOCKED,
        present_concepts=tuple(present),
        missing_fields=tuple(missing),
        reconciliation_identity=RECONCILIATION_IDENTITY,
        theoretical_closing_quantity=theoretical,
        declared_closing_quantity=declared,
        reconciliation_difference=difference,
        reconciliation_ready=reconciliation_ready,
        owner_confirmation_required=not evidence.owner_confirmed,
        physical_count_confirmed=evidence.physical_count_confirmed,
        catalog_extension_candidate=False,
        catalog_mutation_authorized=False,
        engine_mapping_authorized=False,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "contract_schema_version": contract.schema_version,
            "evidence_only": True,
            "negative_closing_stock": bool(declared is not None and declared < 0),
            "physical_count_is_separate_from_theoretical_reconciliation": True,
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "Service1StockMovementEvidenceInputV1",
    "Service1StockMovementEvidencePacketV1",
    "build_service_1_stock_movement_evidence_packet_v1",
]

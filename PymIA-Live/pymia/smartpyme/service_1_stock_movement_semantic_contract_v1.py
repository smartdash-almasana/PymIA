"""Service 1 — Stock Movement Semantic Contract V1.

Pure documentary/semantic contract for future canonical catalog work.
It defines stock movement concepts, evidence requirements and reconciliation
constraints. It does not mutate catalogs, map columns, authorize runtime,
wire frontend, execute formulas or generate delivery artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_STOCK_MOVEMENT_SEMANTIC_CONTRACT_V1"
STATUS_READY: Final[str] = "STOCK_MOVEMENT_SEMANTIC_CONTRACT_READY"

CONCEPT_OPENING_STOCK: Final[str] = "opening_stock_quantity"
CONCEPT_INBOUND_MOVEMENT: Final[str] = "inbound_stock_movement_quantity"
CONCEPT_OUTBOUND_MOVEMENT: Final[str] = "outbound_stock_movement_quantity"
CONCEPT_ADJUSTMENT: Final[str] = "stock_adjustment_quantity"
CONCEPT_CLOSING_STOCK: Final[str] = "closing_stock_quantity"

TEMPORAL_POINT_IN_TIME: Final[str] = "point_in_time"
TEMPORAL_PERIOD_FLOW: Final[str] = "period_flow"
UNIT_QUANTITY: Final[str] = "quantity"
DATA_TYPE_NUMBER: Final[str] = "number"

RECONCILIATION_IDENTITY: Final[str] = (
    "closing_stock_quantity = opening_stock_quantity + "
    "inbound_stock_movement_quantity - outbound_stock_movement_quantity + "
    "stock_adjustment_quantity"
)


@dataclass(frozen=True)
class Service1StockMovementConceptV1:
    concept_id: str
    business_definition: str
    exclusions: tuple[str, ...]
    temporal_semantics: str
    unit: str
    required_data_type: str
    minimum_evidence_fields: tuple[str, ...]
    owner_confirmation_required: bool
    risk_if_wrong: str
    catalog_extension_candidate: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "concept_id",
            "business_definition",
            "temporal_semantics",
            "unit",
            "required_data_type",
            "risk_if_wrong",
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
        if self.catalog_extension_candidate is not False:
            raise ValueError("catalog_extension_candidate must remain False")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1StockMovementSemanticContractV1:
    schema_version: str
    status: str
    concepts: tuple[Service1StockMovementConceptV1, ...]
    reconciliation_identity: str
    mandatory_dimensions: tuple[str, ...]
    movement_classification_required: bool
    negative_stock_requires_owner_confirmation: bool
    missing_movements_block_reconciliation: bool
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
        expected_ids = (
            CONCEPT_OPENING_STOCK,
            CONCEPT_INBOUND_MOVEMENT,
            CONCEPT_OUTBOUND_MOVEMENT,
            CONCEPT_ADJUSTMENT,
            CONCEPT_CLOSING_STOCK,
        )
        if tuple(concept.concept_id for concept in self.concepts) != expected_ids:
            raise ValueError("concepts must preserve the canonical stock movement sequence")
        if self.reconciliation_identity != RECONCILIATION_IDENTITY:
            raise ValueError("invalid reconciliation_identity")
        if self.mandatory_dimensions != ("item_identifier", "period_reference"):
            raise ValueError("mandatory_dimensions must be item_identifier and period_reference")
        for field_name in (
            "movement_classification_required",
            "negative_stock_requires_owner_confirmation",
            "missing_movements_block_reconciliation",
        ):
            if getattr(self, field_name) is not True:
                raise ValueError(f"{field_name} must remain True")
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


def build_service_1_stock_movement_semantic_contract_v1() -> Service1StockMovementSemanticContractV1:
    concepts = (
        Service1StockMovementConceptV1(
            concept_id=CONCEPT_OPENING_STOCK,
            business_definition="Cantidad declarada de cada item al inicio de un periodo definido.",
            exclusions=(
                "No equivale a stock promedio.",
                "No equivale a stock de seguridad.",
                "No confirma conteo fisico.",
                "No equivale a stock disponible para venta.",
            ),
            temporal_semantics=TEMPORAL_POINT_IN_TIME,
            unit=UNIT_QUANTITY,
            required_data_type=DATA_TYPE_NUMBER,
            minimum_evidence_fields=("item_identifier", "period_start", "opening_quantity"),
            owner_confirmation_required=True,
            risk_if_wrong="Distorsiona toda reconciliacion de movimientos y el stock de cierre calculado.",
        ),
        Service1StockMovementConceptV1(
            concept_id=CONCEPT_INBOUND_MOVEMENT,
            business_definition="Cantidad que ingresa al stock de cada item durante un periodo definido.",
            exclusions=(
                "No implica automaticamente una compra.",
                "No mezcla devoluciones, produccion, transferencias y ajustes sin clasificacion.",
                "No representa stock acumulado.",
            ),
            temporal_semantics=TEMPORAL_PERIOD_FLOW,
            unit=UNIT_QUANTITY,
            required_data_type=DATA_TYPE_NUMBER,
            minimum_evidence_fields=(
                "item_identifier",
                "movement_date",
                "movement_class",
                "inbound_quantity",
            ),
            owner_confirmation_required=True,
            risk_if_wrong="Sobreestima o subestima existencias y oculta el origen real del movimiento.",
        ),
        Service1StockMovementConceptV1(
            concept_id=CONCEPT_OUTBOUND_MOVEMENT,
            business_definition="Cantidad que sale del stock de cada item durante un periodo definido.",
            exclusions=(
                "No implica automaticamente una venta.",
                "No mezcla consumo, transferencias, merma, vencimiento y ajustes sin clasificacion.",
                "No representa stock acumulado.",
            ),
            temporal_semantics=TEMPORAL_PERIOD_FLOW,
            unit=UNIT_QUANTITY,
            required_data_type=DATA_TYPE_NUMBER,
            minimum_evidence_fields=(
                "item_identifier",
                "movement_date",
                "movement_class",
                "outbound_quantity",
            ),
            owner_confirmation_required=True,
            risk_if_wrong="Genera stock teorico falso y puede ocultar mermas o movimientos omitidos.",
        ),
        Service1StockMovementConceptV1(
            concept_id=CONCEPT_ADJUSTMENT,
            business_definition="Correccion positiva o negativa aplicada al stock teorico con causa identificada.",
            exclusions=(
                "No sustituye movimientos faltantes sin explicacion.",
                "No equivale automaticamente a merma.",
                "No debe compensar diferencias sin causa documentada.",
            ),
            temporal_semantics=TEMPORAL_PERIOD_FLOW,
            unit=UNIT_QUANTITY,
            required_data_type=DATA_TYPE_NUMBER,
            minimum_evidence_fields=(
                "item_identifier",
                "adjustment_date",
                "adjustment_quantity",
                "adjustment_reason",
            ),
            owner_confirmation_required=True,
            risk_if_wrong="Puede encubrir faltantes, duplicaciones o errores de registracion.",
        ),
        Service1StockMovementConceptV1(
            concept_id=CONCEPT_CLOSING_STOCK,
            business_definition="Cantidad declarada o calculada de cada item al cierre de un periodo definido.",
            exclusions=(
                "No equivale necesariamente al conteo fisico actual.",
                "No equivale a stock promedio.",
                "No puede aceptarse sin distinguir valor declarado de valor calculado.",
            ),
            temporal_semantics=TEMPORAL_POINT_IN_TIME,
            unit=UNIT_QUANTITY,
            required_data_type=DATA_TYPE_NUMBER,
            minimum_evidence_fields=("item_identifier", "period_end", "closing_quantity"),
            owner_confirmation_required=True,
            risk_if_wrong="Invalida alertas de stock, reposicion y reconciliacion del periodo.",
        ),
    )
    return Service1StockMovementSemanticContractV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        concepts=concepts,
        reconciliation_identity=RECONCILIATION_IDENTITY,
        mandatory_dimensions=("item_identifier", "period_reference"),
        movement_classification_required=True,
        negative_stock_requires_owner_confirmation=True,
        missing_movements_block_reconciliation=True,
        catalog_mutation_authorized=False,
        engine_mapping_authorized=False,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "contract_only": True,
            "source_brief": "SERVICE_1_COLUMN_UNDERSTANDING_CANONICAL_EXTENSION_EVIDENCE_BRIEF_V1",
            "stock_physical_count_confirmed": False,
            "formula_catalog_mutated": False,
            "semantic_variable_catalog_mutated": False,
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "CONCEPT_OPENING_STOCK",
    "CONCEPT_INBOUND_MOVEMENT",
    "CONCEPT_OUTBOUND_MOVEMENT",
    "CONCEPT_ADJUSTMENT",
    "CONCEPT_CLOSING_STOCK",
    "TEMPORAL_POINT_IN_TIME",
    "TEMPORAL_PERIOD_FLOW",
    "UNIT_QUANTITY",
    "DATA_TYPE_NUMBER",
    "RECONCILIATION_IDENTITY",
    "Service1StockMovementConceptV1",
    "Service1StockMovementSemanticContractV1",
    "build_service_1_stock_movement_semantic_contract_v1",
]

"""Service 1 — Semantic Concept Catalog Contract V1.

Defines a canonical semantic concept layer separated from formula definitions.
This contract classifies measures, dimensions, identifiers, classifications and
temporal concepts. It does not mutate catalogs, map columns, authorize runtime,
wire frontend, execute formulas or generate delivery artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_CONCEPT_CATALOG_CONTRACT_V1"
STATUS_READY: Final[str] = "SEMANTIC_CONCEPT_CATALOG_CONTRACT_READY"

KIND_MEASURE: Final[str] = "measure"
KIND_DIMENSION: Final[str] = "dimension"
KIND_IDENTIFIER: Final[str] = "identifier"
KIND_CLASSIFICATION: Final[str] = "classification"
KIND_TEMPORAL: Final[str] = "temporal"
ALLOWED_KINDS: Final[frozenset[str]] = frozenset(
    {KIND_MEASURE, KIND_DIMENSION, KIND_IDENTIFIER, KIND_CLASSIFICATION, KIND_TEMPORAL}
)

FORMULA_OPTIONAL: Final[str] = "optional"
FORMULA_REQUIRED: Final[str] = "required"
FORMULA_NOT_APPLICABLE: Final[str] = "not_applicable"
ALLOWED_FORMULA_POLICIES: Final[frozenset[str]] = frozenset(
    {FORMULA_OPTIONAL, FORMULA_REQUIRED, FORMULA_NOT_APPLICABLE}
)


@dataclass(frozen=True)
class Service1SemanticConceptDefinitionV1:
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
    canonical_candidate: bool = False

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
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.concept_kind not in ALLOWED_KINDS:
            raise ValueError("unsupported concept_kind")
        if self.formula_policy not in ALLOWED_FORMULA_POLICIES:
            raise ValueError("unsupported formula_policy")
        if not self.exclusions:
            raise ValueError("exclusions must not be empty")
        if not self.minimum_evidence_fields:
            raise ValueError("minimum_evidence_fields must not be empty")
        if self.owner_confirmation_required is not True:
            raise ValueError("owner_confirmation_required must remain True")
        if self.canonical_candidate is not False:
            raise ValueError("canonical_candidate must remain False")
        if self.concept_kind in {KIND_IDENTIFIER, KIND_CLASSIFICATION, KIND_DIMENSION, KIND_TEMPORAL}:
            if self.formula_policy == FORMULA_REQUIRED:
                raise ValueError("non-measure concepts cannot require a formula")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1SemanticConceptCatalogContractV1:
    schema_version: str
    status: str
    concept_kinds: tuple[str, ...]
    concepts: tuple[Service1SemanticConceptDefinitionV1, ...]
    formulas_consume_concepts: bool
    concepts_require_formula_membership: bool
    identifiers_may_exist_without_formula: bool
    classifications_may_exist_without_formula: bool
    dimensions_may_exist_without_formula: bool
    temporal_concepts_may_exist_without_formula: bool
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
        expected_kinds = (
            KIND_MEASURE,
            KIND_DIMENSION,
            KIND_IDENTIFIER,
            KIND_CLASSIFICATION,
            KIND_TEMPORAL,
        )
        if self.concept_kinds != expected_kinds:
            raise ValueError("concept_kinds must preserve canonical order")
        if len({concept.concept_id for concept in self.concepts}) != len(self.concepts):
            raise ValueError("concept_id values must be unique")
        if {concept.concept_kind for concept in self.concepts} - ALLOWED_KINDS:
            raise ValueError("concepts contain unsupported kinds")
        if self.formulas_consume_concepts is not True:
            raise ValueError("formulas_consume_concepts must remain True")
        if self.concepts_require_formula_membership is not False:
            raise ValueError("concepts_require_formula_membership must remain False")
        for field_name in (
            "identifiers_may_exist_without_formula",
            "classifications_may_exist_without_formula",
            "dimensions_may_exist_without_formula",
            "temporal_concepts_may_exist_without_formula",
        ):
            if getattr(self, field_name) is not True:
                raise ValueError(f"{field_name} must remain True")
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


def build_service_1_semantic_concept_catalog_contract_v1() -> Service1SemanticConceptCatalogContractV1:
    concepts = (
        Service1SemanticConceptDefinitionV1(
            concept_id="opening_stock_quantity",
            concept_kind=KIND_MEASURE,
            business_definition="Cantidad de un item al inicio de un periodo definido.",
            exclusions=("No equivale a stock promedio.", "No confirma conteo fisico."),
            required_data_type="number",
            unit="quantity",
            temporal_semantics="point_in_time",
            formula_policy=FORMULA_OPTIONAL,
            minimum_evidence_fields=("item_identifier", "period_start", "opening_quantity"),
            owner_confirmation_required=True,
            risk_if_wrong="Distorsiona la reconciliacion de stock del periodo.",
        ),
        Service1SemanticConceptDefinitionV1(
            concept_id="closing_stock_quantity",
            concept_kind=KIND_MEASURE,
            business_definition="Cantidad de un item al cierre de un periodo definido.",
            exclusions=("No equivale a stock promedio.", "No confirma conteo fisico actual."),
            required_data_type="number",
            unit="quantity",
            temporal_semantics="point_in_time",
            formula_policy=FORMULA_OPTIONAL,
            minimum_evidence_fields=("item_identifier", "period_end", "closing_quantity"),
            owner_confirmation_required=True,
            risk_if_wrong="Invalida alertas y reconciliaciones de stock.",
        ),
        Service1SemanticConceptDefinitionV1(
            concept_id="customer_identifier",
            concept_kind=KIND_IDENTIFIER,
            business_definition="Identificador estable de la contraparte cliente.",
            exclusions=("No equivale a una descripcion libre.", "No equivale al canal de venta."),
            required_data_type="text",
            unit="identifier",
            temporal_semantics="not_applicable",
            formula_policy=FORMULA_NOT_APPLICABLE,
            minimum_evidence_fields=("customer_identifier",),
            owner_confirmation_required=True,
            risk_if_wrong="Rompe agrupaciones, cobranzas y conciliaciones por cliente.",
        ),
        Service1SemanticConceptDefinitionV1(
            concept_id="supplier_identifier",
            concept_kind=KIND_IDENTIFIER,
            business_definition="Identificador estable de la contraparte proveedora.",
            exclusions=("No equivale a marca de producto.", "No equivale a una nota libre."),
            required_data_type="text",
            unit="identifier",
            temporal_semantics="not_applicable",
            formula_policy=FORMULA_NOT_APPLICABLE,
            minimum_evidence_fields=("supplier_identifier",),
            owner_confirmation_required=True,
            risk_if_wrong="Rompe compras, pagos y consolidaciones por proveedor.",
        ),
        Service1SemanticConceptDefinitionV1(
            concept_id="payment_method_classification",
            concept_kind=KIND_CLASSIFICATION,
            business_definition="Clasificacion controlada del medio utilizado para cobrar o pagar.",
            exclusions=("No equivale a canal de venta.", "No equivale a cuenta bancaria."),
            required_data_type="text",
            unit="category",
            temporal_semantics="per_operation",
            formula_policy=FORMULA_NOT_APPLICABLE,
            minimum_evidence_fields=("payment_method",),
            owner_confirmation_required=True,
            risk_if_wrong="Distorsiona conciliaciones y analisis de cobranzas por medio.",
        ),
        Service1SemanticConceptDefinitionV1(
            concept_id="business_period",
            concept_kind=KIND_TEMPORAL,
            business_definition="Periodo de referencia al que pertenece una observacion o agregado.",
            exclusions=("No equivale necesariamente a fecha de emision.",),
            required_data_type="date_or_period",
            unit="time",
            temporal_semantics="period_reference",
            formula_policy=FORMULA_NOT_APPLICABLE,
            minimum_evidence_fields=("period_reference",),
            owner_confirmation_required=True,
            risk_if_wrong="Mezcla operaciones de periodos incompatibles.",
        ),
    )
    return Service1SemanticConceptCatalogContractV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        concept_kinds=(
            KIND_MEASURE,
            KIND_DIMENSION,
            KIND_IDENTIFIER,
            KIND_CLASSIFICATION,
            KIND_TEMPORAL,
        ),
        concepts=concepts,
        formulas_consume_concepts=True,
        concepts_require_formula_membership=False,
        identifiers_may_exist_without_formula=True,
        classifications_may_exist_without_formula=True,
        dimensions_may_exist_without_formula=True,
        temporal_concepts_may_exist_without_formula=True,
        catalog_mutation_authorized=False,
        variable_catalog_mutation_authorized=False,
        formula_catalog_mutation_authorized=False,
        engine_mapping_authorized=False,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "contract_only": True,
            "separates_semantic_concepts_from_formulas": True,
            "source_stock_contract": "SERVICE_1_STOCK_MOVEMENT_SEMANTIC_CONTRACT_V1",
            "existing_catalogs_mutated": False,
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "KIND_MEASURE",
    "KIND_DIMENSION",
    "KIND_IDENTIFIER",
    "KIND_CLASSIFICATION",
    "KIND_TEMPORAL",
    "FORMULA_OPTIONAL",
    "FORMULA_REQUIRED",
    "FORMULA_NOT_APPLICABLE",
    "Service1SemanticConceptDefinitionV1",
    "Service1SemanticConceptCatalogContractV1",
    "build_service_1_semantic_concept_catalog_contract_v1",
]

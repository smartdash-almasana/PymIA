"""Quotation-calculator knowledge extracted conceptually from OCA/spreadsheet.

The source demonstrates order-line spreadsheet calculators, quotation-scoped
filters and column-oriented field synchronization. PymIA retains only portable
operational patterns and introduces no Odoo dependency.
"""
from __future__ import annotations

from pymia.business_knowledge.contracts_v1 import (
    EvidenceFieldV1,
    KnowledgePackV1,
    OperationalKnowledgeSpecV1,
)

_SOURCE = "OCA/spreadsheet@18.0:spreadsheet_quotation"

QUOTATION_LINE_EXTENDED_AMOUNT = OperationalKnowledgeSpecV1(
    knowledge_ref="quotation_line_extended_amount",
    domain="sales",
    family="quotation",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("product", "product_identifier"),
        EvidenceFieldV1("quantity", "quoted_quantity", "units"),
        EvidenceFieldV1("unit_price", "quoted_unit_price", "currency_per_unit"),
    ),
    expression="quantity * unit_price",
    output_key="quoted_line_amount",
    output_unit="currency",
    validations=(
        "quantity must be non-negative",
        "unit price must be expressed in the quotation currency",
        "product, quantity and price must belong to the same quotation line",
    ),
    interpretation_limits=(
        "line amount is not margin or profit",
        "taxes, discounts and surcharges are excluded unless explicitly supplied",
    ),
    provenance=(_SOURCE,),
)

QUOTATION_SCOPE_FILTER_CONTROL = OperationalKnowledgeSpecV1(
    knowledge_ref="quotation_scope_filter_control",
    domain="sales",
    family="quotation",
    kind="WORKFLOW",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("quotation_id", "quotation_identifier"),
        EvidenceFieldV1("row_identifier", "quotation_line_identifier"),
        EvidenceFieldV1("row_quotation_id", "quotation_identifier_for_line"),
    ),
    expression="FILTER quotation lines WHERE row_quotation_id == quotation_id",
    output_key="quotation_scoped_lines",
    output_unit="records",
    validations=(
        "quotation_id must be explicit before calculator execution",
        "every selected row must belong to the same quotation scope",
    ),
    interpretation_limits=(
        "filtering establishes scope only and does not validate commercial correctness",
        "rows outside the quotation scope must never influence calculations or write-back",
    ),
    provenance=(_SOURCE,),
)

QUOTATION_COLUMN_SYNC_CONTROL = OperationalKnowledgeSpecV1(
    knowledge_ref="quotation_column_sync_control",
    domain="sales",
    family="quotation",
    kind="WORKFLOW",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("source_column", "spreadsheet_column"),
        EvidenceFieldV1("target_field", "quotation_line_field"),
        EvidenceFieldV1("row_identifier", "quotation_line_identifier"),
    ),
    expression="MAP source_column -> target_field BY row_identifier",
    output_key="quotation_field_mapping",
    output_unit="mapping",
    validations=(
        "mapping must be explicit and column-scoped",
        "row identity must be stable before write-back",
        "unmapped columns cannot mutate quotation records",
    ),
    interpretation_limits=(
        "mapping does not authorize automatic write-back",
        "calculated values require validation before persistence",
    ),
    provenance=(_SOURCE,),
)

QUOTATION_CALCULATED_WRITEBACK_CONTROL = OperationalKnowledgeSpecV1(
    knowledge_ref="quotation_calculated_writeback_control",
    domain="sales",
    family="quotation",
    kind="WORKFLOW",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("row_identifier", "quotation_line_identifier"),
        EvidenceFieldV1("target_field", "quotation_line_field"),
        EvidenceFieldV1("calculated_value", "validated_calculated_value"),
        EvidenceFieldV1("mapping_confirmed", "column_mapping_confirmation"),
    ),
    expression="WRITE calculated_value TO target_field ONLY IF mapping_confirmed AND row_identifier stable",
    output_key="validated_writeback_plan",
    output_unit="write_plan",
    validations=(
        "calculated value must pass its own capability validation before persistence",
        "target field must be explicitly mapped",
        "write-back must remain scoped to the identified quotation line",
    ),
    interpretation_limits=(
        "this control does not authorize persistence by itself",
        "write-back cannot create products, prices or commercial conditions that were not explicitly represented",
    ),
    provenance=(_SOURCE,),
)

QUOTATION_OPERATIONS_PACK_V1 = KnowledgePackV1(
    pack_ref="quotation_operations_pack",
    version="1",
    source_family="OCA_SPREADSHEET_CONCEPTUAL_EXTRACTION",
    capabilities=(
        QUOTATION_LINE_EXTENDED_AMOUNT,
        QUOTATION_SCOPE_FILTER_CONTROL,
        QUOTATION_COLUMN_SYNC_CONTROL,
        QUOTATION_CALCULATED_WRITEBACK_CONTROL,
    ),
)


__all__ = [
    "QUOTATION_LINE_EXTENDED_AMOUNT",
    "QUOTATION_SCOPE_FILTER_CONTROL",
    "QUOTATION_COLUMN_SYNC_CONTROL",
    "QUOTATION_CALCULATED_WRITEBACK_CONTROL",
    "QUOTATION_OPERATIONS_PACK_V1",
]

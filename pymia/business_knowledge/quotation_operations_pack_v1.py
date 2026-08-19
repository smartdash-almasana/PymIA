"""Quotation-calculator knowledge extracted conceptually from OCA/spreadsheet.

The source demonstrates order-line spreadsheet calculators, quotation-scoped
filters, isolated calculator copies and column-oriented field synchronization.
PymIA retains only portable operational patterns and introduces no Odoo dependency.
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

QUOTATION_CALCULATOR_INSTANCE_ISOLATION = OperationalKnowledgeSpecV1(
    knowledge_ref="quotation_calculator_instance_isolation",
    domain="sales",
    family="quotation",
    kind="WORKFLOW",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("template_id", "calculator_template_identifier"),
        EvidenceFieldV1("quotation_id", "quotation_identifier"),
        EvidenceFieldV1("calculator_instance_id", "calculator_instance_identifier"),
    ),
    expression="COPY template PER quotation; bind calculator_instance_id exclusively to quotation_id",
    output_key="isolated_calculator_instance",
    output_unit="binding",
    validations=(
        "calculator instance must be distinct from its reusable template",
        "one instance cannot be bound to multiple quotations",
        "quotation identity must be fixed before scoped calculations or write-back",
    ),
    interpretation_limits=(
        "instance isolation prevents cross-quotation contamination but does not validate calculations",
        "copying a template does not authorize persistence of calculated values",
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

QUOTATION_WRITEBACK_STATE_GUARD = OperationalKnowledgeSpecV1(
    knowledge_ref="quotation_writeback_state_guard",
    domain="sales",
    family="quotation",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("quotation_state", "quotation_lifecycle_state"),
        EvidenceFieldV1("writeback_requested", "writeback_request_flag"),
    ),
    expression="ALLOW write-back ONLY for mutable quotation states; BLOCK cancelled or already-confirmed orders",
    output_key="writeback_state_decision",
    output_unit="decision",
    validations=(
        "quotation lifecycle state must be explicit",
        "state guard must execute before any field mutation",
    ),
    interpretation_limits=(
        "state eligibility does not validate the value being written",
        "the guard does not authorize writes outside the mapped quotation scope",
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
        QUOTATION_CALCULATOR_INSTANCE_ISOLATION,
        QUOTATION_COLUMN_SYNC_CONTROL,
        QUOTATION_WRITEBACK_STATE_GUARD,
        QUOTATION_CALCULATED_WRITEBACK_CONTROL,
    ),
)

__all__ = [
    "QUOTATION_LINE_EXTENDED_AMOUNT",
    "QUOTATION_SCOPE_FILTER_CONTROL",
    "QUOTATION_CALCULATOR_INSTANCE_ISOLATION",
    "QUOTATION_COLUMN_SYNC_CONTROL",
    "QUOTATION_WRITEBACK_STATE_GUARD",
    "QUOTATION_CALCULATED_WRITEBACK_CONTROL",
    "QUOTATION_OPERATIONS_PACK_V1",
]

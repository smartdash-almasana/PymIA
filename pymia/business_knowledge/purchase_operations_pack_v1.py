"""Purchase and receiving knowledge extracted conceptually from OCA/spreadsheet.

No Odoo runtime dependency is introduced. The source repository is used as a
reference for business-analysis patterns; these specs are native PymIA data.
"""
from __future__ import annotations

from pymia.business_knowledge.contracts_v1 import (
    EvidenceFieldV1,
    KnowledgePackV1,
    OperationalKnowledgeSpecV1,
)

_PURCHASE_SOURCE = (
    "OCA/spreadsheet@18.0:spreadsheet_dashboard_purchase_stock_oca/"
    "data/files/purchase_dashboard.json"
)
_VENDOR_SOURCE = (
    "OCA/spreadsheet@18.0:spreadsheet_dashboard_purchase_oca/"
    "data/files/vendors_dashboard.json"
)

PURCHASE_AMOUNT_BY_PERIOD = OperationalKnowledgeSpecV1(
    knowledge_ref="purchase_amount_by_period",
    domain="purchases",
    family="spend",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("purchase_date", "purchase_order_date", "date"),
        EvidenceFieldV1("untaxed_amount", "purchase_untaxed_amount", "currency"),
        EvidenceFieldV1("order_state", "purchase_order_state"),
    ),
    expression="SUM(untaxed_amount) GROUP BY confirmed period",
    output_key="purchase_amount",
    output_unit="currency",
    validations=(
        "exclude draft, sent and cancelled purchase orders",
        "all aggregated amounts must belong to the selected period",
        "currency must be normalized before cross-currency aggregation",
    ),
    interpretation_limits=(
        "amount purchased is not cash paid",
        "amount purchased does not establish profitability or supplier performance",
    ),
    provenance=(_PURCHASE_SOURCE,),
)

SUPPLIER_SPEND_BY_VENDOR = OperationalKnowledgeSpecV1(
    knowledge_ref="supplier_spend_by_vendor",
    domain="purchases",
    family="supplier_analysis",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("supplier", "supplier_identifier"),
        EvidenceFieldV1("untaxed_amount", "purchase_untaxed_amount", "currency"),
        EvidenceFieldV1("purchase_date", "purchase_order_date", "date"),
    ),
    expression="SUM(untaxed_amount) GROUP BY supplier WITHIN selected period",
    output_key="supplier_spend",
    output_unit="currency_by_supplier",
    validations=(
        "supplier identity must be stable inside the selected period",
        "currency must be normalized before supplier comparison",
        "all compared suppliers must use the same period scope",
    ),
    interpretation_limits=(
        "high spend does not imply supplier dependency or poor diversification",
        "supplier quality cannot be inferred from spend alone",
    ),
    provenance=(_VENDOR_SOURCE,),
)

OPEN_RFQ_CONTROL = OperationalKnowledgeSpecV1(
    knowledge_ref="open_rfq_control",
    domain="purchases",
    family="procurement_flow",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("rfq_id", "purchase_request_identifier"),
        EvidenceFieldV1("created_at", "purchase_request_created_at", "datetime"),
        EvidenceFieldV1("buyer", "responsible_buyer"),
        EvidenceFieldV1("order_state", "purchase_order_state"),
    ),
    expression="FILTER order_state IN {draft, sent, to_approve}",
    output_key="open_rfq_set",
    output_unit="records",
    validations=("rfq_id must be unique inside the evidence scope",),
    interpretation_limits=(
        "an open RFQ is not evidence of supplier delay",
        "age or urgency requires an explicit comparison date or policy threshold",
    ),
    provenance=(_PURCHASE_SOURCE,),
)

CONFIRMED_PURCHASE_ORDER_REGISTER = OperationalKnowledgeSpecV1(
    knowledge_ref="confirmed_purchase_order_register",
    domain="purchases",
    family="procurement_flow",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("order_id", "purchase_order_identifier"),
        EvidenceFieldV1("approved_at", "purchase_order_approved_at", "datetime"),
        EvidenceFieldV1("buyer", "responsible_buyer"),
        EvidenceFieldV1("order_state", "purchase_order_state"),
    ),
    expression="FILTER order_state IN {purchase, done}; ORDER BY approved_at",
    output_key="confirmed_purchase_orders",
    output_unit="records",
    validations=(
        "order_id must be unique inside the evidence scope",
        "approved_at must be present for chronological comparisons",
    ),
    interpretation_limits=(
        "order date alone does not establish supplier lead time",
        "an old confirmed order is not automatically overdue",
    ),
    provenance=(_PURCHASE_SOURCE, _VENDOR_SOURCE),
)

CONFIRMED_PURCHASE_VOLUME_BY_BUYER = OperationalKnowledgeSpecV1(
    knowledge_ref="confirmed_purchase_volume_by_buyer",
    domain="purchases",
    family="buyer_activity",
    kind="METRIC",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("buyer", "responsible_buyer"),
        EvidenceFieldV1("order_id", "purchase_order_identifier"),
        EvidenceFieldV1("quantity_ordered", "purchase_quantity", "units"),
        EvidenceFieldV1("untaxed_amount", "purchase_untaxed_amount", "currency"),
        EvidenceFieldV1("order_state", "purchase_order_state"),
    ),
    expression="GROUP confirmed orders BY buyer; COUNT(order_id), SUM(quantity_ordered), SUM(untaxed_amount)",
    output_key="buyer_purchase_activity",
    output_unit="recordset",
    validations=(
        "include only confirmed/done purchase orders",
        "quantity aggregation requires compatible units",
        "currency aggregation requires normalized currency",
    ),
    interpretation_limits=(
        "high purchase volume does not imply buyer quality",
        "buyer comparisons require equivalent scope and period",
    ),
    provenance=(_PURCHASE_SOURCE,),
)

LATE_INCOMING_RECEIPT_CONTROL = OperationalKnowledgeSpecV1(
    knowledge_ref="late_incoming_receipt_control",
    domain="inventory",
    family="receiving",
    kind="CONTROL",
    status="CANDIDATE",
    inputs=(
        EvidenceFieldV1("receipt_id", "incoming_receipt_identifier"),
        EvidenceFieldV1("scheduled_date", "planned_receipt_date", "datetime"),
        EvidenceFieldV1("deadline", "receipt_deadline", "datetime", required=False),
        EvidenceFieldV1("receipt_state", "receipt_state"),
        EvidenceFieldV1("movement_type", "inventory_movement_type"),
    ),
    expression=(
        "incoming AND state IN {assigned, waiting, confirmed} AND "
        "(deadline_issue OR deadline < as_of OR scheduled_date < as_of)"
    ),
    output_key="late_receipts",
    output_unit="records",
    validations=(
        "as_of date must be explicit",
        "only incoming movements are eligible",
        "completed and cancelled receipts are excluded",
    ),
    interpretation_limits=(
        "late receipt does not identify who caused the delay",
        "supplier breach cannot be asserted without contractual evidence",
    ),
    provenance=(_PURCHASE_SOURCE,),
)

PURCHASE_OPERATIONS_PACK_V1 = KnowledgePackV1(
    pack_ref="purchase_operations_pack",
    version="1",
    source_family="OCA_SPREADSHEET_CONCEPTUAL_EXTRACTION",
    capabilities=(
        PURCHASE_AMOUNT_BY_PERIOD,
        SUPPLIER_SPEND_BY_VENDOR,
        OPEN_RFQ_CONTROL,
        CONFIRMED_PURCHASE_ORDER_REGISTER,
        CONFIRMED_PURCHASE_VOLUME_BY_BUYER,
        LATE_INCOMING_RECEIPT_CONTROL,
    ),
)


__all__ = [
    "PURCHASE_AMOUNT_BY_PERIOD",
    "SUPPLIER_SPEND_BY_VENDOR",
    "OPEN_RFQ_CONTROL",
    "CONFIRMED_PURCHASE_ORDER_REGISTER",
    "CONFIRMED_PURCHASE_VOLUME_BY_BUYER",
    "LATE_INCOMING_RECEIPT_CONTROL",
    "PURCHASE_OPERATIONS_PACK_V1",
]

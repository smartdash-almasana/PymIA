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

_SOURCE = (
    "OCA/spreadsheet@18.0:spreadsheet_dashboard_purchase_stock_oca/"
    "data/files/purchase_dashboard.json"
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
    provenance=(_SOURCE,),
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
    provenance=(_SOURCE,),
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
    provenance=(_SOURCE,),
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
    provenance=(_SOURCE,),
)

PURCHASE_OPERATIONS_PACK_V1 = KnowledgePackV1(
    pack_ref="purchase_operations_pack",
    version="1",
    source_family="OCA_SPREADSHEET_CONCEPTUAL_EXTRACTION",
    capabilities=(
        PURCHASE_AMOUNT_BY_PERIOD,
        OPEN_RFQ_CONTROL,
        CONFIRMED_PURCHASE_VOLUME_BY_BUYER,
        LATE_INCOMING_RECEIPT_CONTROL,
    ),
)


__all__ = [
    "PURCHASE_AMOUNT_BY_PERIOD",
    "OPEN_RFQ_CONTROL",
    "CONFIRMED_PURCHASE_VOLUME_BY_BUYER",
    "LATE_INCOMING_RECEIPT_CONTROL",
    "PURCHASE_OPERATIONS_PACK_V1",
]

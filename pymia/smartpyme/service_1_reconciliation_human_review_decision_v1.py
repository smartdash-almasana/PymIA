"""Human review decision record for Servicio 1 reconciliation.

Captures an explicit human decision over one review item. It does not mutate
source movements, accept accounting entries, close reconciliation, or grant
runtime/delivery authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, Mapping
from uuid import uuid4

SCHEMA_VERSION: Final[str] = "SERVICE_1_RECONCILIATION_HUMAN_REVIEW_DECISION_V1"
PACKET_TYPE: Final[str] = "RECONCILIATION_HUMAN_REVIEW_DECISION"

DECISION_CONFIRM: Final[str] = "CONFIRM"
DECISION_REJECT: Final[str] = "REJECT"
DECISION_PENDING: Final[str] = "PENDING"
ALLOWED_DECISIONS: Final[frozenset[str]] = frozenset(
    {DECISION_CONFIRM, DECISION_REJECT, DECISION_PENDING}
)


def build_reconciliation_human_review_decision_v1(
    *,
    case_id: str,
    reconciliation_type: str,
    review_item_ref: str,
    review_category: str,
    review_item: Mapping[str, Any],
    decision: str,
    reviewed_by: str,
    observation: str = "",
) -> dict[str, Any]:
    case = str(case_id or "").strip()
    kind = str(reconciliation_type or "").strip()
    item_ref = str(review_item_ref or "").strip()
    category = str(review_category or "").strip()
    chosen = str(decision or "").strip().upper()
    reviewer = str(reviewed_by or "").strip()
    note = str(observation or "").strip()

    if not case:
        raise ValueError("case_id is required")
    if not kind:
        raise ValueError("reconciliation_type is required")
    if not item_ref:
        raise ValueError("review_item_ref is required")
    if not category:
        raise ValueError("review_category is required")
    if not isinstance(review_item, Mapping) or not review_item:
        raise ValueError("review_item is required")
    if chosen not in ALLOWED_DECISIONS:
        raise ValueError("decision is invalid")
    if not reviewer:
        raise ValueError("reviewed_by is required")

    return {
        "schema_version": SCHEMA_VERSION,
        "packet_type": PACKET_TYPE,
        "decision_id": str(uuid4()),
        "case_id": case,
        "reconciliation_type": kind,
        "review_item_ref": item_ref,
        "review_category": category,
        "decision": chosen,
        "reviewed_by": reviewer,
        "observation": note,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "review_item_snapshot": dict(review_item),
        "human_decision": True,
        "source_data_modified": False,
        "accounting_closure_authorized": False,
        "delivery_authorized": False,
        "runtime_authorized": False,
        "llm_used": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "PACKET_TYPE",
    "DECISION_CONFIRM",
    "DECISION_REJECT",
    "DECISION_PENDING",
    "ALLOWED_DECISIONS",
    "build_reconciliation_human_review_decision_v1",
]

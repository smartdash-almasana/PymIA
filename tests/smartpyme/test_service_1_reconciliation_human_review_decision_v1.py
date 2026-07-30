from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_reconciliation_human_review_decision_v1 import (
    build_reconciliation_human_review_decision_v1,
)


def test_builds_traceable_human_decision_without_accounting_authority() -> None:
    record = build_reconciliation_human_review_decision_v1(
        case_id="CASE-1",
        reconciliation_type="BANK_RECONCILIATION",
        review_item_ref="exact:1",
        review_category="exact",
        review_item={"banco_id": "B-1", "interno_id": "C-1"},
        decision="confirm",
        reviewed_by="María Administración",
        observation="Comprobante revisado",
    )

    assert record["decision"] == "CONFIRM"
    assert record["reviewed_by"] == "María Administración"
    assert record["review_item_snapshot"] == {
        "banco_id": "B-1",
        "interno_id": "C-1",
    }
    assert record["human_decision"] is True
    assert record["source_data_modified"] is False
    assert record["accounting_closure_authorized"] is False
    assert record["delivery_authorized"] is False
    assert record["runtime_authorized"] is False
    assert record["llm_used"] is False
    assert record["decision_id"]
    assert record["decided_at"]


def test_rejects_unknown_decision() -> None:
    with pytest.raises(ValueError, match="decision is invalid"):
        build_reconciliation_human_review_decision_v1(
            case_id="CASE-1",
            reconciliation_type="BANK_RECONCILIATION",
            review_item_ref="exact:1",
            review_category="exact",
            review_item={"banco_id": "B-1", "interno_id": "C-1"},
            decision="AUTO_ACCEPT",
            reviewed_by="María Administración",
        )


def test_requires_reviewer_identity() -> None:
    with pytest.raises(ValueError, match="reviewed_by is required"):
        build_reconciliation_human_review_decision_v1(
            case_id="CASE-1",
            reconciliation_type="BANK_RECONCILIATION",
            review_item_ref="exact:1",
            review_category="exact",
            review_item={"banco_id": "B-1", "interno_id": "C-1"},
            decision="CONFIRM",
            reviewed_by="",
        )

import copy

import pytest

from pymia.smartpyme.evidence_request import (
    EVIDENCE_REQUEST_STATUS_FULFILLED,
    EVIDENCE_REQUEST_STATUS_OPEN,
    EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD,
    EvidenceRequestRecord,
    derive_evidence_request_status,
)


@pytest.fixture
def open_request() -> EvidenceRequestRecord:
    return EvidenceRequestRecord(
        request_id="evidence_request_abc123",
        tenant_id="tenant_test",
        intake_id="intake_test",
        anamnesis_id="anamnesis_test",
        investigation_id="inv_test",
        owner_answer_id="owner_answer_test",
        requested_evidence=["lead_time_proveedor", "stock_seguridad"],
        request_reason="Necesitamos datos de reposición de stock",
        status=EVIDENCE_REQUEST_STATUS_OPEN,
        metadata={"origen": "catalog_reconciliation", "formula_id": "INV_001"},
    )


def test_derive_fulfilled_when_matching_registered_evidence(open_request: EvidenceRequestRecord):
    evidence_records = [
        {"request_id": "evidence_request_abc123", "status": "REGISTERED", "evidence_id": "ev_001"},
    ]
    result = derive_evidence_request_status(open_request, evidence_records)
    assert result.status == EVIDENCE_REQUEST_STATUS_FULFILLED
    assert result.metadata["linked_evidence_ids"] == ["ev_001"]


def test_derive_waiting_upload_when_different_request_id(open_request: EvidenceRequestRecord):
    evidence_records = [
        {"request_id": "evidence_request_other", "status": "REGISTERED", "evidence_id": "ev_002"},
    ]
    result = derive_evidence_request_status(open_request, evidence_records)
    assert result.status == EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD
    assert result.metadata["linked_evidence_ids"] == []


def test_derive_waiting_upload_when_rejected_evidence(open_request: EvidenceRequestRecord):
    evidence_records = [
        {"request_id": "evidence_request_abc123", "status": "REJECTED", "evidence_id": "ev_003"},
    ]
    result = derive_evidence_request_status(open_request, evidence_records)
    assert result.status == EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD
    assert result.metadata["linked_evidence_ids"] == []


def test_derive_preserves_metadata_and_adds_linked_ids(open_request: EvidenceRequestRecord):
    evidence_records = [
        {"request_id": "evidence_request_abc123", "status": "REGISTERED", "evidence_id": "ev_004"},
    ]
    result = derive_evidence_request_status(open_request, evidence_records)
    assert result.metadata["origen"] == "catalog_reconciliation"
    assert result.metadata["formula_id"] == "INV_001"
    assert result.metadata["linked_evidence_ids"] == ["ev_004"]


def test_derive_does_not_mutate_original(open_request: EvidenceRequestRecord):
    original_metadata = copy.deepcopy(open_request.metadata)
    evidence_records = [
        {"request_id": "evidence_request_abc123", "status": "REGISTERED", "evidence_id": "ev_005"},
    ]
    derive_evidence_request_status(open_request, evidence_records)
    assert open_request.status == EVIDENCE_REQUEST_STATUS_OPEN
    assert open_request.metadata == original_metadata


def test_derive_rejects_non_list_evidence_records(open_request: EvidenceRequestRecord):
    with pytest.raises(ValueError, match="evidence_records must be a list"):
        derive_evidence_request_status(open_request, "not_a_list")


def test_derive_rejects_non_dict_items(open_request: EvidenceRequestRecord):
    with pytest.raises(ValueError, match="items must be dicts"):
        derive_evidence_request_status(open_request, ["not_a_dict"])

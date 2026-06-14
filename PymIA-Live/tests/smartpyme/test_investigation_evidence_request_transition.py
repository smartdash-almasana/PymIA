import pytest

from pymia.smartpyme.investigation import (
    INVESTIGATION_STATUS_BLOCKED,
    INVESTIGATION_STATUS_OPEN,
    INVESTIGATION_STATUS_READY_FOR_CONTRAST,
    INVESTIGATION_STATUS_WAITING_EVIDENCE,
    InvestigationRecord,
    derive_investigation_status_from_evidence_request,
)


@pytest.fixture
def open_investigation() -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id="inv_001",
        tenant_id="tenant_test",
        intake_id="intake_test",
        anamnesis_id="anamnesis_test",
        owner_prompt="necesito ver los costos",
        investigation_axis="costos_proveedores",
        declared_question="¿Podés detallar los costos directos?",
        status=INVESTIGATION_STATUS_OPEN,
        evidence_required=["costos_directos", "cmv_periodo"],
        metadata={"formula_id": "REN_001"},
    )


def test_fulfilled_transitions_to_ready_for_contrast(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_001",
        "status": "FULFILLED",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.status == INVESTIGATION_STATUS_READY_FOR_CONTRAST


def test_waiting_upload_transitions_to_waiting_evidence(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_002",
        "status": "WAITING_UPLOAD",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.status == INVESTIGATION_STATUS_WAITING_EVIDENCE


def test_open_transitions_to_waiting_evidence(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_003",
        "status": "OPEN",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.status == INVESTIGATION_STATUS_WAITING_EVIDENCE


def test_cancelled_transitions_to_blocked(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_004",
        "status": "CANCELLED",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.status == INVESTIGATION_STATUS_BLOCKED


def test_evidence_request_blocked_transitions_to_investigation_blocked(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_005",
        "status": "BLOCKED",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.status == INVESTIGATION_STATUS_BLOCKED


def test_preserves_investigation_fields(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_006",
        "status": "FULFILLED",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.investigation_id == "inv_001"
    assert result.tenant_id == "tenant_test"
    assert result.intake_id == "intake_test"
    assert result.anamnesis_id == "anamnesis_test"
    assert result.owner_prompt == "necesito ver los costos"
    assert result.investigation_axis == "costos_proveedores"
    assert result.declared_question == "¿Podés detallar los costos directos?"
    assert result.evidence_required == ["costos_directos", "cmv_periodo"]


def test_adds_evidence_request_metadata(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_007",
        "status": "FULFILLED",
    }
    result = derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert result.metadata["evidence_request_id"] == "req_007"
    assert result.metadata["evidence_request_status"] == "FULFILLED"
    assert result.metadata["formula_id"] == "REN_001"


def test_rejects_tenant_id_mismatch(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_other",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "status": "FULFILLED",
    }
    with pytest.raises(ValueError, match="tenant_id does not match"):
        derive_investigation_status_from_evidence_request(open_investigation, ev_request)


def test_rejects_intake_id_mismatch(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_other",
        "investigation_id": "inv_001",
        "status": "FULFILLED",
    }
    with pytest.raises(ValueError, match="intake_id does not match"):
        derive_investigation_status_from_evidence_request(open_investigation, ev_request)


def test_rejects_investigation_id_mismatch(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_other",
        "status": "FULFILLED",
    }
    with pytest.raises(ValueError, match="investigation_id does not match"):
        derive_investigation_status_from_evidence_request(open_investigation, ev_request)


def test_rejects_non_investigation_record():
    with pytest.raises(ValueError, match="investigation must be an InvestigationRecord"):
        derive_investigation_status_from_evidence_request("not_an_investigation", {})


def test_rejects_non_dict_evidence_request(open_investigation: InvestigationRecord):
    with pytest.raises(ValueError, match="evidence_request must be a dict"):
        derive_investigation_status_from_evidence_request(open_investigation, "not_a_dict")


def test_raises_on_unsupported_status(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "status": "UNKNOWN_STATUS",
    }
    with pytest.raises(ValueError, match="status is not supported"):
        derive_investigation_status_from_evidence_request(open_investigation, ev_request)


def test_does_not_mutate_original(open_investigation: InvestigationRecord):
    ev_request = {
        "tenant_id": "tenant_test",
        "intake_id": "intake_test",
        "investigation_id": "inv_001",
        "request_id": "req_008",
        "status": "FULFILLED",
    }
    derive_investigation_status_from_evidence_request(open_investigation, ev_request)
    assert open_investigation.status == INVESTIGATION_STATUS_OPEN
    assert "evidence_request_id" not in open_investigation.metadata

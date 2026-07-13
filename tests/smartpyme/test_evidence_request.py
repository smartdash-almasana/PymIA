from __future__ import annotations

import pytest

from pymia.smartpyme.evidence_request import (
    EVIDENCE_REQUEST_STATUS_OPEN,
    EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD,
    create_evidence_request_record,
)


def test_create_evidence_request_record_defaults_to_open() -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        requested_evidence=["ventas_del_periodo", "costos_directos"],
        request_reason="Faltan datos para contrastar margen.",
    )

    payload = record.to_dict()

    assert record.request_id.startswith("evidence_request_")
    assert payload["tenant_id"] == "tenant_demo"
    assert payload["intake_id"] == "intake_demo"
    assert payload["anamnesis_id"] == "anamnesis_demo"
    assert payload["investigation_id"] == "investigation_demo"
    assert payload["owner_answer_id"] is None
    assert payload["requested_evidence"] == ["ventas_del_periodo", "costos_directos"]
    assert payload["request_reason"] == "Faltan datos para contrastar margen."
    assert payload["status"] == EVIDENCE_REQUEST_STATUS_OPEN
    assert payload["metadata"] == {}


def test_create_evidence_request_record_accepts_owner_answer_status_and_metadata() -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        owner_answer_id="answer_demo",
        requested_evidence=["cobranzas_del_periodo"],
        request_reason="El dueño indicó dónde están las ventas, falta cobranza.",
        status=EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD,
        metadata={"source": "owner_answer"},
    )

    payload = record.to_dict()

    assert payload["owner_answer_id"] == "answer_demo"
    assert payload["status"] == EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD
    assert payload["metadata"] == {"source": "owner_answer"}


def test_create_evidence_request_record_rejects_empty_tenant_id() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        create_evidence_request_record(
            tenant_id="",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence=["ventas"],
            request_reason="Falta ventas.",
        )


def test_create_evidence_request_record_rejects_empty_intake_id() -> None:
    with pytest.raises(ValueError, match="intake_id"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence=["ventas"],
            request_reason="Falta ventas.",
        )


def test_create_evidence_request_record_rejects_empty_anamnesis_id() -> None:
    with pytest.raises(ValueError, match="anamnesis_id"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="",
            investigation_id="investigation_demo",
            requested_evidence=["ventas"],
            request_reason="Falta ventas.",
        )


def test_create_evidence_request_record_rejects_empty_investigation_id() -> None:
    with pytest.raises(ValueError, match="investigation_id"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="",
            requested_evidence=["ventas"],
            request_reason="Falta ventas.",
        )


def test_create_evidence_request_record_rejects_empty_requested_evidence() -> None:
    with pytest.raises(ValueError, match="requested_evidence"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence=[],
            request_reason="Falta ventas.",
        )


def test_create_evidence_request_record_rejects_non_list_requested_evidence() -> None:
    with pytest.raises(ValueError, match="requested_evidence"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence="ventas",  # type: ignore[arg-type]
            request_reason="Falta ventas.",
        )


def test_create_evidence_request_record_rejects_empty_request_reason() -> None:
    with pytest.raises(ValueError, match="request_reason"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence=["ventas"],
            request_reason="",
        )


def test_create_evidence_request_record_rejects_invalid_status() -> None:
    with pytest.raises(ValueError, match="status"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence=["ventas"],
            request_reason="Falta ventas.",
            status="INVALID",
        )


def test_create_evidence_request_record_rejects_non_dict_metadata() -> None:
    with pytest.raises(ValueError, match="metadata"):
        create_evidence_request_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            requested_evidence=["ventas"],
            request_reason="Falta ventas.",
            metadata="operator",  # type: ignore[arg-type]
        )

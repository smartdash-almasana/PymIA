from __future__ import annotations

import pytest

from pymia.smartpyme.investigation import (
    INVESTIGATION_STATUS_OPEN,
    INVESTIGATION_STATUS_READY_FOR_CONTRAST,
    create_investigation_record,
)


def test_create_investigation_record_defaults_to_open() -> None:
    record = create_investigation_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="Quiero saber si mi negocio deja margen.",
    )

    payload = record.to_dict()

    assert record.tenant_id == "tenant_demo"
    assert record.intake_id == "intake_demo"
    assert record.anamnesis_id == "anamnesis_demo"
    assert record.owner_prompt == "Quiero saber si mi negocio deja margen."
    assert record.declared_question == "Quiero saber si mi negocio deja margen."
    assert record.investigation_axis == "desconocido"
    assert record.status == INVESTIGATION_STATUS_OPEN
    assert record.investigation_id.startswith("investigation_")
    assert payload["evidence_required"] == []
    assert payload["pathology_candidates"] == []
    assert payload["formula_candidates"] == []
    assert payload["metadata"] == {}


def test_create_investigation_record_accepts_candidates_and_metadata() -> None:
    record = create_investigation_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="No me cierra la caja.",
        investigation_axis="caja_liquidez",
        declared_question="¿Por qué falta plata si vendo?",
        status=INVESTIGATION_STATUS_READY_FOR_CONTRAST,
        evidence_required=["ventas", "cobranzas", "cuentas_por_pagar"],
        pathology_candidates=["LIQ_001", "PYME_024"],
        formula_candidates=["PYME_026_flujo_operativo"],
        metadata={"source": "owner_prompt"},
    )

    payload = record.to_dict()

    assert payload["investigation_axis"] == "caja_liquidez"
    assert payload["declared_question"] == "¿Por qué falta plata si vendo?"
    assert payload["status"] == INVESTIGATION_STATUS_READY_FOR_CONTRAST
    assert payload["evidence_required"] == ["ventas", "cobranzas", "cuentas_por_pagar"]
    assert payload["pathology_candidates"] == ["LIQ_001", "PYME_024"]
    assert payload["formula_candidates"] == ["PYME_026_flujo_operativo"]
    assert payload["metadata"] == {"source": "owner_prompt"}


def test_create_investigation_record_rejects_empty_tenant_id() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        create_investigation_record(
            tenant_id="",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            owner_prompt="Necesito revisar margen.",
        )


def test_create_investigation_record_rejects_empty_intake_id() -> None:
    with pytest.raises(ValueError, match="intake_id"):
        create_investigation_record(
            tenant_id="tenant_demo",
            intake_id="",
            anamnesis_id="anamnesis_demo",
            owner_prompt="Necesito revisar margen.",
        )


def test_create_investigation_record_rejects_empty_anamnesis_id() -> None:
    with pytest.raises(ValueError, match="anamnesis_id"):
        create_investigation_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="",
            owner_prompt="Necesito revisar margen.",
        )


def test_create_investigation_record_rejects_empty_owner_prompt() -> None:
    with pytest.raises(ValueError, match="owner_prompt"):
        create_investigation_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            owner_prompt="",
        )


def test_create_investigation_record_rejects_invalid_status() -> None:
    with pytest.raises(ValueError, match="status"):
        create_investigation_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            owner_prompt="Necesito revisar margen.",
            status="INVALID",
        )


def test_create_investigation_record_rejects_non_list_candidates() -> None:
    with pytest.raises(ValueError, match="evidence_required"):
        create_investigation_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            owner_prompt="Necesito revisar margen.",
            evidence_required="ventas",  # type: ignore[arg-type]
        )

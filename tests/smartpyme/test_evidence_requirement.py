from __future__ import annotations

import pytest

from pymia.smartpyme.evidence_requirement import create_evidence_requirement


def test_create_evidence_requirement_valid():
    e = create_evidence_requirement(
        requirement_id="r1",
        tenant_id="t1",
        intake_id="i1",
        hypothesis_id="h1",
        evidence_type="excel_ventas_costos",
        description="Subir excel ventas/costos",
        required_fields=["producto", "ventas", "costo"],
        reason="Validar hipótesis",
        blocks_analysis=True,
        priority=1,
        telegram_message="Por favor subí tu excel de ventas y costos",
    )
    assert e.priority == 1


def test_priority_out_of_range_fails():
    with pytest.raises(ValueError):
        create_evidence_requirement(
            requirement_id="r1",
            tenant_id="t1",
            intake_id="i1",
            hypothesis_id="h1",
            evidence_type="excel_ventas_costos",
            description="Subir excel",
            required_fields=["producto"],
            reason="Validar",
            blocks_analysis=True,
            priority=4,
            telegram_message="Subí el excel",
        )


def test_telegram_message_empty_fails():
    with pytest.raises(ValueError):
        create_evidence_requirement(
            requirement_id="r1",
            tenant_id="t1",
            intake_id="i1",
            hypothesis_id="h1",
            evidence_type="excel_ventas_costos",
            description="Subir excel",
            required_fields=["producto"],
            reason="Validar",
            blocks_analysis=True,
            priority=2,
            telegram_message="",
        )

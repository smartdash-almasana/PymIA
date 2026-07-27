from __future__ import annotations

from pymia.smartpyme.reception import create_reception


def test_create_reception_delivered_shape() -> None:
    rec = create_reception(
        tenant_id="tenant_test",
        message="No sé si vendo con margen",
        classification="margen",
        status="DELIVERED",
        evidence_refs=["input.xlsx"],
        output_refs=["diagnostic_report.md"],
    )
    assert rec.tenant_id == "tenant_test"
    assert rec.status == "DELIVERED"
    assert rec.evidence_refs == ["input.xlsx"]
    assert rec.output_refs == ["diagnostic_report.md"]
    assert rec.created_at


def test_create_reception_requires_tenant_id() -> None:
    try:
        create_reception(
            tenant_id="",
            message="msg",
            classification="margen",
        )
    except ValueError as exc:
        assert "tenant_id is required" in str(exc)
    else:
        raise AssertionError("ValueError expected")

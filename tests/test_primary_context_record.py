from __future__ import annotations

from pymia.contracts.primary_context_v1 import PrimaryContextRecord, PrimaryContextSignal


def test_primary_context_record_defaults_to_pending_data() -> None:
    record = PrimaryContextRecord(
        tenant_id="tenant-1",
        raw_message="vendo mucho pero no se si gano plata",
        expressed_pain=[PrimaryContextSignal(code="margin_uncertainty")],
    )

    assert record.state == "pending_data"
    assert record.evidence_gap.required_evidence == []


def test_primary_context_record_requires_message() -> None:
    try:
        PrimaryContextRecord(tenant_id="tenant-1", raw_message="")
    except Exception as exc:  # pydantic validation error
        assert "raw_message" in str(exc)
    else:
        raise AssertionError("Expected validation error for empty raw_message")


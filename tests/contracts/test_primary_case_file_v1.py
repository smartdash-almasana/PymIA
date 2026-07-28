from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from pymia.contracts.primary_case_file_v1 import (
    PrimaryCaseAuthorization,
    PrimaryCaseFile,
    PrimaryCaseFileError,
    PrimaryCasePeriod,
)


def _valid_pcf(**overrides) -> PrimaryCaseFile:
    payload = {
        "pcf_id": "pcf-001",
        "tenant_id": "tenant-001",
        "case_id": "case-001",
        "operator_id": "operator-001",
        "owner_ref": "owner-001",
        "business_ref": "business-001",
        "period": {
            "start": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "end": datetime(2026, 1, 31, tzinfo=timezone.utc),
        },
        "problem_statement": "No me cierra la caja.",
        "scope": "liquidez operativa",
        "authorization": {"status": "owner_consents"},
        "initial_evidence_refs": ["evidence-001"],
    }
    payload.update(overrides)
    return PrimaryCaseFile.model_validate(payload)


def test_primary_case_file_valid_draft_contract():
    pcf = _valid_pcf()

    assert pcf.status == "draft"
    assert pcf.schema_version == "1.0"
    assert pcf.case_id == "case-001"
    assert pcf.is_sealed() is False


@pytest.mark.parametrize(
    "field_name",
    [
        "tenant_id",
        "case_id",
        "operator_id",
        "owner_ref",
        "business_ref",
        "problem_statement",
        "scope",
    ],
)
def test_primary_case_file_rejects_missing_required_string(field_name: str):
    with pytest.raises(ValidationError):
        _valid_pcf(**{field_name: "   "})


def test_primary_case_file_requires_period():
    with pytest.raises(ValidationError):
        _valid_pcf(period=None)


def test_primary_case_file_rejects_invalid_period_order():
    with pytest.raises(ValidationError):
        _valid_pcf(
            period={
                "start": datetime(2026, 2, 1, tzinfo=timezone.utc),
                "end": datetime(2026, 1, 1, tzinfo=timezone.utc),
            }
        )


def test_primary_case_file_rejects_invalid_authorization_status():
    with pytest.raises(ValidationError):
        _valid_pcf(authorization={"status": "approved"})


def test_primary_case_file_rejects_unknown_schema_version():
    with pytest.raises(ValidationError):
        _valid_pcf(schema_version="2.0")


def test_primary_case_file_seal_returns_sealed_copy():
    pcf = _valid_pcf()
    sealed = pcf.seal(sealed_at=datetime(2026, 2, 1, tzinfo=timezone.utc))

    assert pcf.status == "draft"
    assert sealed.status == "sealed"
    assert sealed.is_sealed() is True
    assert sealed.sealed_at == datetime(2026, 2, 1, tzinfo=timezone.utc)


def test_primary_case_file_second_seal_fails():
    sealed = _valid_pcf().seal()

    with pytest.raises(PrimaryCaseFileError):
        sealed.seal()


def test_primary_case_file_sealed_fields_are_immutable():
    sealed = _valid_pcf().seal()

    with pytest.raises(TypeError):
        sealed.case_id = "case-002"


@pytest.mark.parametrize("status", ["draft", "superseded"])
def test_primary_case_file_supersede_only_allowed_when_sealed(status: str):
    pcf = _valid_pcf(status=status)

    with pytest.raises(PrimaryCaseFileError):
        pcf.supersede("pcf-002")


def test_primary_case_file_supersede_returns_superseded_copy():
    sealed = _valid_pcf().seal()
    superseded = sealed.supersede("pcf-002")

    assert sealed.status == "sealed"
    assert superseded.status == "superseded"
    assert superseded.superseded_by == "pcf-002"


def test_primary_case_file_roundtrip_preserves_fields():
    pcf = _valid_pcf().seal(sealed_at=datetime(2026, 2, 1, tzinfo=timezone.utc))
    dumped = pcf.model_dump(mode="json")
    loaded = PrimaryCaseFile.model_validate(dumped)

    assert loaded.model_dump(mode="json") == dumped


def test_primary_case_file_period_and_authorization_are_pure_contracts():
    period = PrimaryCasePeriod(
        start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end=datetime(2026, 1, 31, tzinfo=timezone.utc),
    )
    authorization = PrimaryCaseAuthorization(status="operator_assumes")

    pcf = _valid_pcf(period=period, authorization=authorization)

    assert pcf.period == period
    assert pcf.authorization == authorization

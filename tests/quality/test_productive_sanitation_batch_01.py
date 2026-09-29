from __future__ import annotations

from types import SimpleNamespace

import pytest

from pymia.smartpyme import service_1_analysis_evidence_preparation_v1 as f7
from pymia.smartpyme import service_1_result_read_boundary_v1 as read_boundary
from pymia.smartpyme.service_1_computability_v1 import Service1GovernedAnalysisInputV1


def _governed_stub() -> Service1GovernedAnalysisInputV1:
    governed = object.__new__(Service1GovernedAnalysisInputV1)
    object.__setattr__(governed, "case_id", "case-1")
    object.__setattr__(governed, "analysis_plan", SimpleNamespace(analysis_id="analysis-1"))
    object.__setattr__(governed, "source_bindings", {"sales_amount": "Sales.Amount"})
    object.__setattr__(governed, "relationship_bindings", {})
    object.__setattr__(governed, "grain", SimpleNamespace())
    return governed


def test_f7_base_sheet_none_fails_closed_without_assert(monkeypatch: pytest.MonkeyPatch) -> None:
    governed = _governed_stub()
    monkeypatch.setattr(f7, "_table_views", lambda _ingestion: ({}, None))
    monkeypatch.setattr(f7, "_validate_relationship_bindings", lambda *args, **kwargs: None)
    monkeypatch.setattr(f7, "_select_base_sheet", lambda **kwargs: (None, None))

    decision = f7.build_service_1_analysis_evidence_preparation_v1(
        case_id="case-1",
        governed_analysis_input=governed,
        ingestion_output={},
    )

    assert decision.status == f7.STATUS_BLOCKED
    assert decision.reason == "BASE_SHEET_SELECTION_INVALID"


class _RecordStub:
    def __init__(
        self,
        *,
        tenant_id: str = "tenant-a",
        case_id: str = "case-1",
        result_id: str = "s1rm_result",
        digest: str = "digest-1",
    ) -> None:
        self.tenant_id = tenant_id
        self.case_id = case_id
        self.memory_record_id = result_id
        self.result_set_integrity_digest = digest

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "case_id": self.case_id,
            "memory_record_id": self.memory_record_id,
            "result_set_integrity_digest": self.result_set_integrity_digest,
            "result_set": {"immutable": ["value", 1]},
        }


def _boundary_with_record(monkeypatch: pytest.MonkeyPatch, record: _RecordStub) -> read_boundary.ResultReadBoundary:
    monkeypatch.setattr(read_boundary, "_record", lambda _raw: record)
    return read_boundary.ResultReadBoundary(lambda _tenant, _result: object())


def test_result_read_boundary_blocks_cross_tenant_record(monkeypatch: pytest.MonkeyPatch) -> None:
    boundary = _boundary_with_record(monkeypatch, _RecordStub(tenant_id="tenant-b"))

    packet = boundary.read_by_result_id(tenant_id="tenant-a", result_id="s1rm_result")

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "TENANT_BOUNDARY_MISMATCH"


def test_result_read_boundary_blocks_integrity_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    boundary = _boundary_with_record(monkeypatch, _RecordStub(digest="actual-digest"))
    query = read_boundary.Service1ResultQueryV1(
        tenant_id="tenant-a",
        case_id="case-1",
        result_id="s1rm_result",
        expected_integrity_digest="expected-digest",
    )

    packet = boundary.read(query)

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "RESULT_INTEGRITY_MISMATCH"


def test_result_read_boundary_reentry_preserves_result_set(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _RecordStub()
    boundary = _boundary_with_record(monkeypatch, record)

    packet = boundary.read_by_result_id(tenant_id="tenant-a", result_id="s1rm_result")

    assert packet["status"] == read_boundary.STATUS_READY
    assert packet["result_set"] == record.to_dict()["result_set"]
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False

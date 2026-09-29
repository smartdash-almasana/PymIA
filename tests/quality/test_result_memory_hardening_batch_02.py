from __future__ import annotations

import pytest

from pymia.smartpyme import service_1_result_read_boundary_v1 as read_boundary
from tests.quality.test_productive_sanitation_batch_01 import _RecordStub, _boundary_with_record


def test_result_read_boundary_blocks_result_identity_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    boundary = _boundary_with_record(monkeypatch, _RecordStub(result_id="s1rm_other"))

    packet = boundary.read_by_result_id(tenant_id="tenant-a", result_id="s1rm_result")

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "RESULT_IDENTITY_MISMATCH"


def test_result_read_boundary_blocks_case_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    boundary = _boundary_with_record(monkeypatch, _RecordStub(case_id="case-other"))
    query = read_boundary.Service1ResultQueryV1(
        tenant_id="tenant-a",
        case_id="case-1",
        result_id="s1rm_result",
        expected_integrity_digest="digest-1",
    )

    packet = boundary.read(query)

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "CASE_BOUNDARY_MISMATCH"


def test_result_read_boundary_blocks_invalid_persisted_mapping() -> None:
    boundary = read_boundary.ResultReadBoundary(
        lambda _tenant, _result: {"tenant_id": "tenant-a", "memory_record_id": "s1rm_result"}
    )

    packet = boundary.read_by_result_id(tenant_id="tenant-a", result_id="s1rm_result")

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "RESULT_MEMORY_INVALID_RECORD"


def test_result_read_boundary_blocks_loader_failure() -> None:
    def _loader(_tenant: str, _result: str) -> object:
        raise RuntimeError("storage down")

    boundary = read_boundary.ResultReadBoundary(_loader)

    packet = boundary.read_by_result_id(tenant_id="tenant-a", result_id="s1rm_result")

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "RESULT_MEMORY_LOAD_FAILED"


def test_result_read_boundary_blocks_missing_record() -> None:
    boundary = read_boundary.ResultReadBoundary(lambda _tenant, _result: None)

    packet = boundary.read_by_result_id(tenant_id="tenant-a", result_id="s1rm_result")

    assert packet["status"] == read_boundary.STATUS_BLOCKED
    assert packet["blocked_reason"] == "RESULT_NOT_FOUND"


def test_result_read_boundary_complete_query_fails_closed_when_identity_is_incomplete() -> None:
    boundary = read_boundary.ResultReadBoundary(lambda _tenant, _result: object())

    missing_tenant = boundary.read(
        read_boundary.Service1ResultQueryV1(
            case_id="case-1",
            result_id="s1rm_result",
            expected_integrity_digest="digest-1",
        )
    )
    missing_case = boundary.read(
        read_boundary.Service1ResultQueryV1(
            tenant_id="tenant-a",
            result_id="s1rm_result",
            expected_integrity_digest="digest-1",
        )
    )
    missing_result = boundary.read(
        read_boundary.Service1ResultQueryV1(
            tenant_id="tenant-a",
            case_id="case-1",
            expected_integrity_digest="digest-1",
        )
    )
    missing_digest = boundary.read(
        read_boundary.Service1ResultQueryV1(
            tenant_id="tenant-a",
            case_id="case-1",
            result_id="s1rm_result",
        )
    )

    assert missing_tenant["blocked_reason"] == "TENANT_ID_REQUIRED"
    assert missing_case["blocked_reason"] == "CASE_ID_REQUIRED"
    assert missing_result["blocked_reason"] == "RESULT_ID_REQUIRED"
    assert missing_digest["blocked_reason"] == "EXPECTED_INTEGRITY_DIGEST_REQUIRED"

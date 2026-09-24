"""Read-only boundary for persisted Service 1 result memory.

The boundary validates the caller's tenant/case/result/integrity identity and
then projects the immutable F13 record. It deliberately has no imports from
XLSX ingestion, semantic reception, P7/P8, F7/F8/F9, or any LLM provider.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping

from pymia.smartpyme.service_1_result_memory_v1 import (
    Service1ResultMemoryRecordV1,
    service_1_result_memory_record_from_mapping_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_RESULT_READ_BOUNDARY_V1"
STATUS_READY: Final[str] = "READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"


@dataclass(frozen=True, init=False)
class Service1ResultQueryV1:
    """Tenant-scoped immutable-result lookup identity."""

    tenant_id: str
    case_id: str | None
    result_id: str
    expected_integrity_digest: str | None

    def __init__(
        self,
        *,
        tenant_id: str | None = None,
        tenant_identity: object | None = None,
        case_id: str | None = None,
        result_id: str | None = None,
        expected_integrity_digest: str | None = None,
    ) -> None:
        resolved_tenant = str(tenant_id or "").strip()
        if not resolved_tenant and tenant_identity is not None:
            if isinstance(tenant_identity, Mapping):
                resolved_tenant = str(tenant_identity.get("tenant_id") or "").strip()
            else:
                resolved_tenant = str(getattr(tenant_identity, "tenant_id", "") or "").strip()
        object.__setattr__(self, "tenant_id", resolved_tenant)
        object.__setattr__(self, "case_id", _optional_text(case_id))
        object.__setattr__(self, "result_id", str(result_id or "").strip())
        object.__setattr__(
            self,
            "expected_integrity_digest",
            _optional_text(expected_integrity_digest),
        )


class ResultReadBoundary:
    """Single read-only gateway from a result query to F13 persistence."""

    def __init__(
        self,
        load_result_memory_record: Callable[[str, str], object | None] | None = None,
    ) -> None:
        self._load_result_memory_record = load_result_memory_record

    def read(self, query: Service1ResultQueryV1) -> dict[str, Any]:
        """Read one result requiring the complete query identity."""
        if not isinstance(query, Service1ResultQueryV1):
            return _blocked("RESULT_QUERY_REQUIRED")
        if not query.tenant_id:
            return _blocked("TENANT_ID_REQUIRED")
        if not query.case_id:
            return _blocked("CASE_ID_REQUIRED")
        if not query.result_id:
            return _blocked("RESULT_ID_REQUIRED")
        if not query.expected_integrity_digest:
            return _blocked("EXPECTED_INTEGRITY_DIGEST_REQUIRED")
        return self._read(query, require_case=True)

    def read_by_result_id(
        self,
        *,
        tenant_id: str,
        result_id: str,
    ) -> dict[str, Any]:
        """Read by durable ID when the persisted record supplies its case identity."""
        query = Service1ResultQueryV1(tenant_id=tenant_id, result_id=result_id)
        if not query.tenant_id:
            return _blocked("TENANT_ID_REQUIRED")
        if not query.result_id:
            return _blocked("RESULT_ID_REQUIRED")
        return self._read(query, require_case=False)

    def _read(self, query: Service1ResultQueryV1, *, require_case: bool) -> dict[str, Any]:
        if self._load_result_memory_record is None:
            return _blocked("RESULT_MEMORY_LOADER_UNAVAILABLE")
        try:
            raw_record = self._load_result_memory_record(query.tenant_id, query.result_id)
        except Exception:
            return _blocked("RESULT_MEMORY_LOAD_FAILED")
        if raw_record is None:
            return _blocked("RESULT_NOT_FOUND")
        try:
            record = _record(raw_record)
        except Exception:
            return _blocked("RESULT_MEMORY_INVALID_RECORD")
        if record.tenant_id != query.tenant_id:
            return _blocked("TENANT_BOUNDARY_MISMATCH")
        if record.memory_record_id != query.result_id:
            return _blocked("RESULT_IDENTITY_MISMATCH")
        if require_case and record.case_id != query.case_id:
            return _blocked("CASE_BOUNDARY_MISMATCH")
        if query.case_id and record.case_id != query.case_id:
            return _blocked("CASE_BOUNDARY_MISMATCH")
        if (
            query.expected_integrity_digest
            and record.result_set_integrity_digest != query.expected_integrity_digest
        ):
            return _blocked("RESULT_INTEGRITY_MISMATCH")
        payload = record.to_dict()
        return {
            "schema_version": SCHEMA_VERSION,
            "status": STATUS_READY,
            "tenant_id": record.tenant_id,
            "case_id": record.case_id,
            "result_id": record.memory_record_id,
            "result_set_integrity_digest": record.result_set_integrity_digest,
            "result_memory": payload,
            "result_set": payload["result_set"],
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }


def _record(raw_record: object) -> Service1ResultMemoryRecordV1:
    if isinstance(raw_record, Service1ResultMemoryRecordV1):
        return service_1_result_memory_record_from_mapping_v1(raw_record.to_dict())
    if isinstance(raw_record, Mapping):
        return service_1_result_memory_record_from_mapping_v1(raw_record)
    raise TypeError("result memory loader returned an invalid record")


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "Service1ResultQueryV1",
    "ResultReadBoundary",
]

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_xlsx_runtime_bridge_v1 import (
    STATUS_BRIDGE_BLOCKED,
    STATUS_BRIDGE_NEXT_OWNER_QUESTION,
    STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
    Service1XlsxRuntimeBridgeV1,
    build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_DOCUMENT_INGESTION_TO_XLSX_RUNTIME_BRIDGE_ADAPTER_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_ADAPTER_BRIDGE_READY: Final[str] = "ADAPTER_BRIDGE_READY"
STATUS_ADAPTER_NEXT_OWNER_QUESTION: Final[str] = "ADAPTER_NEXT_OWNER_QUESTION"
STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT: Final[str] = "ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT"
STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT: Final[str] = "ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT"
STATUS_ADAPTER_BRIDGE_BLOCKED: Final[str] = "ADAPTER_BRIDGE_BLOCKED"

AdapterStatusV1 = Literal[
    "ADAPTER_BRIDGE_READY",
    "ADAPTER_NEXT_OWNER_QUESTION",
    "ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT",
    "ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT",
    "ADAPTER_BRIDGE_BLOCKED",
]


@dataclass(frozen=True)
class Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1:
    schema_version: str
    service_name: str
    status: AdapterStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    owner_ref: str
    source_file_ref: str | None
    normalized_payload: dict[str, Any]
    bridge_result: Service1XlsxRuntimeBridgeV1 | None
    available_data_fields: tuple[str, ...]
    input_values: dict[str, object]
    missing_adapter_items: tuple[str, ...]
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bridge_result"] = self.bridge_result.to_dict() if self.bridge_result is not None else None
        return data


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values = value if isinstance(value, (list, tuple, set)) else (value,)
    return tuple(text for item in values if (text := _text(item)))


def _dict(value: Any) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items() if isinstance(key, str) and key.strip()}


def _records_fields(records: Any) -> tuple[str, ...]:
    if not isinstance(records, (list, tuple)) or not records:
        return ()
    first = records[0]
    if not isinstance(first, dict):
        return ()
    return tuple(str(key).strip() for key in first.keys() if str(key).strip())


def _records_values(records: Any) -> dict[str, object]:
    if not isinstance(records, (list, tuple)) or not records:
        return {}
    first = records[0]
    if not isinstance(first, dict):
        return {}
    return {str(key): value for key, value in first.items() if str(key).strip()}


def _extract_available_fields(ingestion_output: dict[str, object]) -> tuple[str, ...]:
    for key in ("available_data_fields", "normalized_fields", "columns"):
        fields = _tuple(ingestion_output.get(key))
        if fields:
            return fields
    fields = _records_fields(ingestion_output.get("records"))
    if fields:
        return fields
    fields = _records_fields(ingestion_output.get("rows"))
    if fields:
        return fields
    evidence = ingestion_output.get("evidence")
    if isinstance(evidence, dict):
        fields = _tuple(evidence.get("available_data_fields")) or _tuple(evidence.get("columns"))
        if fields:
            return fields
    return ()


def _extract_input_values(ingestion_output: dict[str, object]) -> dict[str, object]:
    for key in ("input_values", "normalized_values"):
        values = _dict(ingestion_output.get(key))
        if values:
            return values
    values = _records_values(ingestion_output.get("records"))
    if values:
        return values
    values = _records_values(ingestion_output.get("rows"))
    if values:
        return values
    evidence = ingestion_output.get("evidence")
    if isinstance(evidence, dict):
        values = _dict(evidence.get("input_values")) or _dict(evidence.get("normalized_values"))
        if values:
            return values
    return {}


def _extract_declared_sources(ingestion_output: dict[str, object], source_file_ref: str | None) -> tuple[str, ...]:
    sources = _tuple(ingestion_output.get("declared_data_sources"))
    if sources:
        return sources
    return (source_file_ref,) if source_file_ref else ()


def _source_file_ref(ingestion_output: dict[str, object]) -> str | None:
    return _text(ingestion_output.get("source_file_ref")) or _text(ingestion_output.get("file_ref"))


def _blocked_result(
    *,
    status: AdapterStatusV1,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    source_file_ref: str | None,
    normalized_payload: dict[str, Any],
    available_data_fields: tuple[str, ...],
    input_values: dict[str, object],
    missing_adapter_items: tuple[str, ...],
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1:
    return Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        source_file_ref=source_file_ref,
        normalized_payload=normalized_payload,
        bridge_result=None,
        available_data_fields=available_data_fields,
        input_values=input_values,
        missing_adapter_items=missing_adapter_items,
        blocked_reason=blocked_reason,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def _adapter_status_from_bridge(bridge_result: Service1XlsxRuntimeBridgeV1) -> AdapterStatusV1:
    if bridge_result.status == STATUS_BRIDGE_PACKAGE_CANDIDATE_READY:
        return STATUS_ADAPTER_BRIDGE_READY
    if bridge_result.status == STATUS_BRIDGE_NEXT_OWNER_QUESTION:
        return STATUS_ADAPTER_NEXT_OWNER_QUESTION
    if bridge_result.status == STATUS_BRIDGE_BLOCKED:
        return STATUS_ADAPTER_BRIDGE_BLOCKED
    return STATUS_ADAPTER_BRIDGE_BLOCKED


def build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    raw_owner_narrative: str | None,
    ingestion_output: dict[str, object],
    business_period_reference: str | None = None,
    column_meaning_confirmations: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, object] | None = None,
) -> Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1:
    case_id = _required_text(case_id, field_name="case_id")
    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    intake_id = _required_text(intake_id, field_name="intake_id")
    run_id = _required_text(run_id, field_name="run_id")
    owner_ref = _required_text(owner_ref, field_name="owner_ref")
    metadata_dict = dict(metadata or {})

    if not isinstance(ingestion_output, dict) or not ingestion_output:
        return _blocked_result(
            status=STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT,
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            source_file_ref=None,
            normalized_payload={},
            available_data_fields=(),
            input_values={},
            missing_adapter_items=("ingestion_output",),
            blocked_reason="missing_ingestion_output",
            metadata=metadata_dict,
        )

    source_file_ref = _source_file_ref(ingestion_output)
    available_data_fields = _extract_available_fields(ingestion_output)
    input_values = _extract_input_values(ingestion_output)
    missing_items: list[str] = []
    if not available_data_fields:
        missing_items.append("available_data_fields")
    if not input_values:
        missing_items.append("input_values")

    normalized_payload: dict[str, Any] = {
        "case_id": case_id,
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "run_id": run_id,
        "owner_ref": owner_ref,
        "source_file_ref": source_file_ref,
        "raw_owner_narrative": raw_owner_narrative,
        "business_period_reference": business_period_reference,
        "declared_data_sources": _extract_declared_sources(ingestion_output, source_file_ref),
        "column_meaning_confirmations": _tuple(column_meaning_confirmations),
        "available_data_fields": available_data_fields,
        "input_values": input_values,
    }

    if missing_items:
        return _blocked_result(
            status=STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT,
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            source_file_ref=source_file_ref,
            normalized_payload=normalized_payload,
            available_data_fields=available_data_fields,
            input_values=input_values,
            missing_adapter_items=tuple(missing_items),
            blocked_reason="invalid_ingestion_output",
            metadata=metadata_dict,
        )

    bridge_result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=normalized_payload,
        metadata={"source_schema_version": SCHEMA_VERSION, **metadata_dict},
    )

    return Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=_adapter_status_from_bridge(bridge_result),
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        source_file_ref=source_file_ref,
        normalized_payload=normalized_payload,
        bridge_result=bridge_result,
        available_data_fields=available_data_fields,
        input_values=input_values,
        missing_adapter_items=(),
        blocked_reason=bridge_result.blocked_reason,
        owner_confirmation_required=bridge_result.owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={"source_schema_version": SCHEMA_VERSION, **metadata_dict},
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_ADAPTER_BRIDGE_READY",
    "STATUS_ADAPTER_NEXT_OWNER_QUESTION",
    "STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT",
    "STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT",
    "STATUS_ADAPTER_BRIDGE_BLOCKED",
    "Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1",
    "build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1",
]

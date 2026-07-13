from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_real_client_xlsx_first_pilot_pack_v1 import (
    Service1RealClientXlsxFirstPilotPackV1,
    build_service_1_real_client_xlsx_first_pilot_pack_v1,
)
from pymia.smartpyme.service_1_xlsx_first_product_entrypoint_v1 import (
    STATUS_BLOCKED as ENTRYPOINT_STATUS_BLOCKED,
    STATUS_DELIVERY_PACKAGE_CANDIDATE_READY,
    STATUS_NEXT_OWNER_QUESTION,
    Service1XlsxFirstProductEntrypointV1,
    build_service_1_xlsx_first_product_entrypoint_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_XLSX_RUNTIME_BRIDGE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_BRIDGE_PACKAGE_CANDIDATE_READY: Final[str] = "BRIDGE_PACKAGE_CANDIDATE_READY"
STATUS_BRIDGE_NEXT_OWNER_QUESTION: Final[str] = "BRIDGE_NEXT_OWNER_QUESTION"
STATUS_BRIDGE_BLOCKED: Final[str] = "BRIDGE_BLOCKED"

BridgeStatusV1 = Literal[
    "BRIDGE_PACKAGE_CANDIDATE_READY",
    "BRIDGE_NEXT_OWNER_QUESTION",
    "BRIDGE_BLOCKED",
]


@dataclass(frozen=True)
class Service1XlsxRuntimeBridgeV1:
    schema_version: str
    service_name: str
    status: BridgeStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    owner_ref: str
    source_file_ref: str | None
    entrypoint_status: str | None
    pilot_pack_status: str | None
    selected_primary_pathology: str | None
    allowed_computation_ref: str | None
    next_owner_question: str | None
    package_candidate_ref: str | None
    blocked_reason: str | None
    owner_confirmation_required: bool
    entrypoint_result: Service1XlsxFirstProductEntrypointV1 | None
    pilot_pack_result: Service1RealClientXlsxFirstPilotPackV1 | None
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["entrypoint_result"] = (
            self.entrypoint_result.to_dict() if self.entrypoint_result is not None else None
        )
        data["pilot_pack_result"] = (
            self.pilot_pack_result.to_dict() if self.pilot_pack_result is not None else None
        )
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


def _metadata_bool(metadata: dict[str, Any], key: str) -> bool:
    return metadata.get(key) is True


def _pilot_metadata(
    *,
    source_file_ref: str | None,
    owner_problem_narrative: str | None,
    business_period_reference: str | None,
    column_meaning_confirmations: tuple[str, ...],
    available_data_fields: tuple[str, ...],
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    data = dict(metadata or {})
    data.setdefault("xlsx_file_available", bool(source_file_ref))
    data.setdefault("owner_problem_narrative", bool(owner_problem_narrative))
    data.setdefault("business_period_reference", bool(business_period_reference))
    data.setdefault("column_meaning_confirmations", bool(column_meaning_confirmations))
    data.setdefault("available_data_fields", bool(available_data_fields))
    data["source_file_ref"] = source_file_ref
    data["source_schema_version"] = SCHEMA_VERSION
    return data


def _status_from_entrypoint(entrypoint: Service1XlsxFirstProductEntrypointV1) -> BridgeStatusV1:
    if entrypoint.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_READY:
        return STATUS_BRIDGE_PACKAGE_CANDIDATE_READY
    if entrypoint.status == STATUS_NEXT_OWNER_QUESTION:
        return STATUS_BRIDGE_NEXT_OWNER_QUESTION
    return STATUS_BRIDGE_BLOCKED


def _package_ref(entrypoint: Service1XlsxFirstProductEntrypointV1) -> str | None:
    package = entrypoint.delivery_package_candidate
    if package is None:
        return None
    return package.package_id


def _build_bridge(
    *,
    status: BridgeStatusV1,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    source_file_ref: str | None,
    entrypoint: Service1XlsxFirstProductEntrypointV1 | None,
    pilot_pack: Service1RealClientXlsxFirstPilotPackV1 | None,
    blocked_reason: str | None,
    owner_confirmation_required: bool,
    metadata: dict[str, Any] | None,
) -> Service1XlsxRuntimeBridgeV1:
    return Service1XlsxRuntimeBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        source_file_ref=source_file_ref,
        entrypoint_status=entrypoint.status if entrypoint is not None else None,
        pilot_pack_status=pilot_pack.status if pilot_pack is not None else None,
        selected_primary_pathology=(
            entrypoint.selected_primary_pathology if entrypoint is not None else None
        ),
        allowed_computation_ref=(
            entrypoint.allowed_computation_ref if entrypoint is not None else None
        ),
        next_owner_question=entrypoint.next_owner_question if entrypoint is not None else None,
        package_candidate_ref=_package_ref(entrypoint) if entrypoint is not None else None,
        blocked_reason=blocked_reason,
        owner_confirmation_required=owner_confirmation_required,
        entrypoint_result=entrypoint,
        pilot_pack_result=pilot_pack,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_xlsx_runtime_bridge_v1(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    raw_owner_narrative: str | None,
    source_file_ref: str | None = None,
    business_period_reference: str | None = None,
    declared_data_sources: list[str] | tuple[str, ...] | None = None,
    column_meaning_confirmations: list[str] | tuple[str, ...] | None = None,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    input_values: dict[str, object] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1XlsxRuntimeBridgeV1:
    """Bridge normalized XLSX/case data into the official S1 XLSX-first entrypoint.

    This function is intentionally not an XLSX parser. It receives already-normalized
    fields and values, then delegates to the official product entrypoint and pilot
    pack builder. It performs no IO, no external calls, no API/worker behavior, and
    no real delivery.
    """

    case_id = _required_text(case_id, field_name="case_id")
    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    intake_id = _required_text(intake_id, field_name="intake_id")
    run_id = _required_text(run_id, field_name="run_id")
    owner_ref = _required_text(owner_ref, field_name="owner_ref")
    source_file_ref = _text(source_file_ref)
    narrative = _text(raw_owner_narrative)
    period = _text(business_period_reference)
    fields = _tuple(available_data_fields)
    confirmations = _tuple(column_meaning_confirmations)
    values = _dict(input_values)
    declared_sources = _tuple(declared_data_sources) or ((source_file_ref,) if source_file_ref else ())

    bridge_metadata = {
        "source_schema_version": SCHEMA_VERSION,
        "input_mode": "normalized_xlsx_case_payload",
        "parser_invoked": False,
        **dict(metadata or {}),
    }

    entrypoint = build_service_1_xlsx_first_product_entrypoint_v1(
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        raw_owner_narrative=narrative,
        business_period_reference=period,
        declared_data_sources=declared_sources,
        column_meaning_confirmations=confirmations,
        available_data_fields=fields,
        input_values=values,
        metadata=bridge_metadata,
    )

    pilot_pack = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=entrypoint,
        metadata=_pilot_metadata(
            source_file_ref=source_file_ref,
            owner_problem_narrative=narrative,
            business_period_reference=period,
            column_meaning_confirmations=confirmations,
            available_data_fields=fields,
            metadata=bridge_metadata,
        ),
    )

    status = _status_from_entrypoint(entrypoint)
    blocked_reason = entrypoint.blocked_reason if entrypoint.status == ENTRYPOINT_STATUS_BLOCKED else None

    return _build_bridge(
        status=status,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        source_file_ref=source_file_ref,
        entrypoint=entrypoint,
        pilot_pack=pilot_pack,
        blocked_reason=blocked_reason,
        owner_confirmation_required=entrypoint.owner_confirmation_required,
        metadata=bridge_metadata,
    )


def build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
    *,
    normalized_payload: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> Service1XlsxRuntimeBridgeV1:
    if not isinstance(normalized_payload, dict):
        raise ValueError("normalized_payload must be a dict")
    return build_service_1_xlsx_runtime_bridge_v1(
        case_id=normalized_payload.get("case_id", ""),
        tenant_id=normalized_payload.get("tenant_id", ""),
        intake_id=normalized_payload.get("intake_id", ""),
        run_id=normalized_payload.get("run_id", ""),
        owner_ref=normalized_payload.get("owner_ref", ""),
        raw_owner_narrative=normalized_payload.get("raw_owner_narrative"),
        source_file_ref=normalized_payload.get("source_file_ref"),
        business_period_reference=normalized_payload.get("business_period_reference"),
        declared_data_sources=normalized_payload.get("declared_data_sources"),
        column_meaning_confirmations=normalized_payload.get("column_meaning_confirmations"),
        available_data_fields=normalized_payload.get("available_data_fields"),
        input_values=normalized_payload.get("input_values"),
        metadata={"payload_origin": "normalized_payload", **dict(metadata or {})},
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_BRIDGE_PACKAGE_CANDIDATE_READY",
    "STATUS_BRIDGE_NEXT_OWNER_QUESTION",
    "STATUS_BRIDGE_BLOCKED",
    "Service1XlsxRuntimeBridgeV1",
    "build_service_1_xlsx_runtime_bridge_v1",
    "build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1",
]

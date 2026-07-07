from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1 import (
    STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT,
    STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT,
    STATUS_ADAPTER_BRIDGE_BLOCKED,
    STATUS_ADAPTER_BRIDGE_READY,
    STATUS_ADAPTER_NEXT_OWNER_QUESTION,
    Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1,
    build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_REAL_OWNER_PILOT_CASE_RUN_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY: Final[str] = "REAL_OWNER_PACKAGE_CANDIDATE_READY"
STATUS_REAL_OWNER_NEEDS_OWNER_INPUT: Final[str] = "REAL_OWNER_NEEDS_OWNER_INPUT"
STATUS_REAL_OWNER_BLOCKED: Final[str] = "REAL_OWNER_BLOCKED"

RealOwnerPilotCaseRunStatusV1 = Literal[
    "REAL_OWNER_PACKAGE_CANDIDATE_READY",
    "REAL_OWNER_NEEDS_OWNER_INPUT",
    "REAL_OWNER_BLOCKED",
]

_DECISION_CHECKLIST_ITEMS: Final[tuple[str, ...]] = (
    "owner_narrative_present",
    "business_period_present",
    "column_confirmations_present",
    "ingestion_output_present",
    "adapter_status_checked",
    "bridge_status_checked",
    "package_or_question_present",
)

_DEFAULT_STOP_RULES: Final[tuple[str, ...]] = (
    "detener si falta narrativa del dueno",
    "detener si faltan confirmaciones de columnas",
    "detener si la ingesta no produce available_data_fields",
    "detener si la ingesta no produce input_values",
    "detener si el bridge bloquea",
    "no prometer diagnostico definitivo",
    "no producir delivery autonomo",
)


@dataclass(frozen=True)
class Service1RealOwnerPilotCaseRunV1:
    schema_version: str
    service_name: str
    status: RealOwnerPilotCaseRunStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    owner_ref: str
    source_file_ref: str | None
    pilot_title: str
    owner_narrative: str | None
    business_period_reference: str | None
    adapter_result: Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1 | None
    bridge_status: str | None
    pilot_pack_status: str | None
    selected_primary_pathology: str | None
    allowed_computation_ref: str | None
    next_owner_question: str | None
    package_candidate_ref: str | None
    decision_checklist: dict[str, bool]
    stop_rules: tuple[str, ...]
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["adapter_result"] = (
            self.adapter_result.to_dict() if self.adapter_result is not None else None
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


def _status_from_adapter(
    adapter_status: str,
) -> RealOwnerPilotCaseRunStatusV1:
    if adapter_status == STATUS_ADAPTER_BRIDGE_READY:
        return STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY
    if adapter_status == STATUS_ADAPTER_NEXT_OWNER_QUESTION:
        return STATUS_REAL_OWNER_NEEDS_OWNER_INPUT
    if adapter_status in (
        STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT,
        STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT,
        STATUS_ADAPTER_BRIDGE_BLOCKED,
    ):
        return STATUS_REAL_OWNER_BLOCKED
    return STATUS_REAL_OWNER_BLOCKED


def _build_checklist(
    *,
    owner_narrative: str | None,
    business_period_reference: str | None,
    column_meaning_confirmations: tuple[str, ...],
    ingestion_output: dict[str, object],
    adapter: Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1 | None,
    bridge_status: str | None,
    package_or_question_present: bool,
) -> dict[str, bool]:
    return {
        "owner_narrative_present": bool(owner_narrative),
        "business_period_present": bool(business_period_reference),
        "column_confirmations_present": bool(column_meaning_confirmations),
        "ingestion_output_present": bool(ingestion_output),
        "adapter_status_checked": adapter is not None,
        "bridge_status_checked": bridge_status is not None,
        "package_or_question_present": package_or_question_present,
    }


def _source_file_ref(
    adapter: Service1DocumentIngestionToXlsxRuntimeBridgeAdapterV1 | None,
    ingestion_output: dict[str, object],
) -> str | None:
    if adapter is not None and adapter.source_file_ref is not None:
        return adapter.source_file_ref
    return _text(ingestion_output.get("source_file_ref")) or _text(
        ingestion_output.get("file_ref")
    )


def _pilot_title(owner_narrative: str | None) -> str:
    if owner_narrative:
        return f"Real Owner Pilot: {owner_narrative[:80]}"
    return "Real Owner Pilot: Pyme Operational Diagnosis"


def build_service_1_real_owner_pilot_case_run_v1(
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
) -> Service1RealOwnerPilotCaseRunV1:
    case_id = _required_text(case_id, field_name="case_id")
    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    intake_id = _required_text(intake_id, field_name="intake_id")
    run_id = _required_text(run_id, field_name="run_id")
    owner_ref = _required_text(owner_ref, field_name="owner_ref")
    owner_narrative = _text(raw_owner_narrative)
    period = _text(business_period_reference)
    confirmations = _tuple(column_meaning_confirmations)
    metadata_dict = dict(metadata or {})

    if not owner_narrative:
        checklist = _build_checklist(
            owner_narrative=owner_narrative,
            business_period_reference=period,
            column_meaning_confirmations=confirmations,
            ingestion_output=ingestion_output,
            adapter=None,
            bridge_status=None,
            package_or_question_present=False,
        )
        return Service1RealOwnerPilotCaseRunV1(
            schema_version=SCHEMA_VERSION,
            service_name=SERVICE_NAME,
            status=STATUS_REAL_OWNER_BLOCKED,
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            source_file_ref=_source_file_ref(None, ingestion_output),
            pilot_title=_pilot_title(None),
            owner_narrative=None,
            business_period_reference=period,
            adapter_result=None,
            bridge_status=None,
            pilot_pack_status=None,
            selected_primary_pathology=None,
            allowed_computation_ref=None,
            next_owner_question=None,
            package_candidate_ref=None,
            decision_checklist=checklist,
            stop_rules=_DEFAULT_STOP_RULES,
            blocked_reason="missing_owner_narrative",
            owner_confirmation_required=True,
            runtime_authorized=False,
            reexecution_authorized=False,
            recalculation_authorized=False,
            delivery_authorized=False,
            metadata=metadata_dict,
        )

    adapter = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        raw_owner_narrative=owner_narrative,
        ingestion_output=ingestion_output,
        business_period_reference=period,
        column_meaning_confirmations=confirmations,
        metadata=metadata_dict,
    )

    status = _status_from_adapter(adapter.status)
    bridge = adapter.bridge_result
    bridge_status = bridge.status if bridge is not None else None
    pilot_pack_status = bridge.pilot_pack_status if bridge is not None else None
    selected_primary_pathology = (
        bridge.selected_primary_pathology if bridge is not None else None
    )
    allowed_computation_ref = (
        bridge.allowed_computation_ref if bridge is not None else None
    )
    next_owner_question = (
        bridge.next_owner_question if bridge is not None else None
    )
    package_candidate_ref = (
        bridge.package_candidate_ref if bridge is not None else None
    )
    blocked_reason = adapter.blocked_reason if status == STATUS_REAL_OWNER_BLOCKED else None

    package_or_question = (
        package_candidate_ref is not None or next_owner_question is not None
    )
    checklist = _build_checklist(
        owner_narrative=owner_narrative,
        business_period_reference=period,
        column_meaning_confirmations=confirmations,
        ingestion_output=ingestion_output,
        adapter=adapter,
        bridge_status=bridge_status,
        package_or_question_present=package_or_question,
    )

    return Service1RealOwnerPilotCaseRunV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        source_file_ref=_source_file_ref(adapter, ingestion_output),
        pilot_title=_pilot_title(owner_narrative),
        owner_narrative=owner_narrative,
        business_period_reference=period,
        adapter_result=adapter,
        bridge_status=bridge_status,
        pilot_pack_status=pilot_pack_status,
        selected_primary_pathology=selected_primary_pathology,
        allowed_computation_ref=allowed_computation_ref,
        next_owner_question=next_owner_question,
        package_candidate_ref=package_candidate_ref,
        decision_checklist=checklist,
        stop_rules=_DEFAULT_STOP_RULES,
        blocked_reason=blocked_reason,
        owner_confirmation_required=adapter.owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={**metadata_dict, "source_schema_version": SCHEMA_VERSION},
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY",
    "STATUS_REAL_OWNER_NEEDS_OWNER_INPUT",
    "STATUS_REAL_OWNER_BLOCKED",
    "Service1RealOwnerPilotCaseRunV1",
    "build_service_1_real_owner_pilot_case_run_v1",
]

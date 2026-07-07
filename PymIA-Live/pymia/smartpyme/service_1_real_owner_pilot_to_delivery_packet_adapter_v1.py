from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    build_service_1_delivery_policy_guard_v1,
)
from pymia.smartpyme.service_1_real_owner_pilot_case_run_v1 import (
    STATUS_REAL_OWNER_BLOCKED,
    STATUS_REAL_OWNER_NEEDS_OWNER_INPUT,
    STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY,
    Service1RealOwnerPilotCaseRunV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_REAL_OWNER_PILOT_TO_DELIVERY_PACKET_ADAPTER_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD: Final[str] = "DELIVERY_PACKET_READY_FOR_POLICY_GUARD"
STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT: Final[str] = "DELIVERY_PACKET_NEEDS_OWNER_INPUT"
STATUS_DELIVERY_PACKET_BLOCKED: Final[str] = "DELIVERY_PACKET_BLOCKED"
STATUS_DELIVERY_PACKET_INVALID_INPUT: Final[str] = "DELIVERY_PACKET_INVALID_INPUT"

DeliveryPacketAdapterStatusV1 = Literal[
    "DELIVERY_PACKET_READY_FOR_POLICY_GUARD",
    "DELIVERY_PACKET_NEEDS_OWNER_INPUT",
    "DELIVERY_PACKET_BLOCKED",
    "DELIVERY_PACKET_INVALID_INPUT",
]

_LIMITS: Final[tuple[str, ...]] = (
    "salida operativa preliminar",
    "no es diagnostico definitivo",
    "no reemplaza revision contable",
    "no autoriza entrega autonoma",
)


@dataclass(frozen=True)
class Service1RealOwnerPilotToDeliveryPacketAdapterV1:
    schema_version: str
    service_name: str
    status: DeliveryPacketAdapterStatusV1
    case_id: str | None
    tenant_id: str | None
    intake_id: str | None
    run_id: str | None
    owner_ref: str | None
    source_file_ref: str | None
    delivery_packet: dict[str, Any]
    delivery_policy_guard: dict[str, Any] | None
    owner_message: str | None
    next_owner_question: dict[str, Any] | None
    case_record: dict[str, Any]
    owner_delivery_packet: dict[str, Any]
    product_gate: dict[str, Any]
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _status_from_pilot(pilot_status: str) -> DeliveryPacketAdapterStatusV1:
    if pilot_status == STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY:
        return STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD
    if pilot_status == STATUS_REAL_OWNER_NEEDS_OWNER_INPUT:
        return STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT
    if pilot_status == STATUS_REAL_OWNER_BLOCKED:
        return STATUS_DELIVERY_PACKET_BLOCKED
    return STATUS_DELIVERY_PACKET_INVALID_INPUT


def _case_family(pilot_result: Service1RealOwnerPilotCaseRunV1) -> str:
    return _text(pilot_result.selected_primary_pathology) or "SERVICE_1_XLSX_FIRST"


def _owner_message(pilot_result: Service1RealOwnerPilotCaseRunV1, status: str) -> str:
    if status == STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT:
        return _text(pilot_result.next_owner_question) or "PymIA necesita una confirmacion adicional del dueno antes de continuar."
    if status == STATUS_DELIVERY_PACKET_BLOCKED:
        reason = _text(pilot_result.blocked_reason) or "bloqueo operativo no especificado"
        return f"Servicio 1 queda detenido: {reason}. Proxima accion segura: corregir evidencia o confirmar informacion con el dueno."
    if status == STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD:
        return (
            "Servicio 1 preparo una salida operativa preliminar para revision. "
            "No es diagnostico definitivo, no reemplaza revision contable y requiere control de politica de entrega."
        )
    return "Servicio 1 no puede preparar packet de entrega por input invalido."


def _next_owner_question(pilot_result: Service1RealOwnerPilotCaseRunV1) -> dict[str, Any] | None:
    question = _text(pilot_result.next_owner_question)
    if question is None:
        return None
    return {
        "markdown": question,
        "owner_confirmation_required": True,
    }


def _case_record(pilot_result: Service1RealOwnerPilotCaseRunV1) -> dict[str, Any]:
    return {
        "case_id": pilot_result.case_id,
        "tenant_id": pilot_result.tenant_id,
        "intake_id": pilot_result.intake_id,
        "run_id": pilot_result.run_id,
        "owner_ref": pilot_result.owner_ref,
        "source_file_ref": pilot_result.source_file_ref,
        "owner_narrative": pilot_result.owner_narrative,
        "business_period_reference": pilot_result.business_period_reference,
        "status": pilot_result.status,
        "bridge_status": pilot_result.bridge_status,
        "pilot_pack_status": pilot_result.pilot_pack_status,
        "selected_primary_pathology": pilot_result.selected_primary_pathology,
        "allowed_computation_ref": pilot_result.allowed_computation_ref,
        "blocked_reason": pilot_result.blocked_reason,
        "owner_confirmation_required": pilot_result.owner_confirmation_required,
    }


def _owner_delivery_packet(
    pilot_result: Service1RealOwnerPilotCaseRunV1,
    *,
    owner_message: str,
) -> dict[str, Any]:
    return {
        "status": pilot_result.status,
        "owner_message": owner_message,
        "next_owner_question": pilot_result.next_owner_question,
        "selected_primary_pathology": pilot_result.selected_primary_pathology,
        "allowed_computation_ref": pilot_result.allowed_computation_ref,
        "package_candidate_ref": pilot_result.package_candidate_ref,
        "limits": _LIMITS,
        "stop_rules": pilot_result.stop_rules,
        "owner_confirmation_required": pilot_result.owner_confirmation_required,
    }


def _product_gate(
    pilot_result: Service1RealOwnerPilotCaseRunV1,
    *,
    adapter_status: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": "READY_FOR_DELIVERY_POLICY_GUARD"
        if adapter_status == STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD
        else "BLOCKED",
        "owner_confirmation_required": pilot_result.owner_confirmation_required,
        "blocked_reason": pilot_result.blocked_reason,
        "runtime_authorized": False,
        "reexecution_authorized": False,
        "recalculation_authorized": False,
        "delivery_authorized": False,
    }


def _asset(pilot_result: Service1RealOwnerPilotCaseRunV1) -> dict[str, Any]:
    return {
        "asset_id": pilot_result.case_id,
        "source_file_ref": pilot_result.source_file_ref,
        "case_family": _case_family(pilot_result),
        "period": pilot_result.business_period_reference,
    }


def build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
    *,
    pilot_result: Service1RealOwnerPilotCaseRunV1,
    metadata: dict[str, object] | None = None,
) -> Service1RealOwnerPilotToDeliveryPacketAdapterV1:
    metadata_dict = dict(metadata or {})
    if not isinstance(pilot_result, Service1RealOwnerPilotCaseRunV1):
        return Service1RealOwnerPilotToDeliveryPacketAdapterV1(
            schema_version=SCHEMA_VERSION,
            service_name=SERVICE_NAME,
            status=STATUS_DELIVERY_PACKET_INVALID_INPUT,
            case_id=None,
            tenant_id=None,
            intake_id=None,
            run_id=None,
            owner_ref=None,
            source_file_ref=None,
            delivery_packet={},
            delivery_policy_guard=None,
            owner_message=None,
            next_owner_question=None,
            case_record={},
            owner_delivery_packet={},
            product_gate={
                "schema_version": SCHEMA_VERSION,
                "service_name": SERVICE_NAME,
                "status": "BLOCKED",
                "runtime_authorized": False,
                "reexecution_authorized": False,
                "recalculation_authorized": False,
                "delivery_authorized": False,
            },
            blocked_reason="pilot_result_must_be_Service1RealOwnerPilotCaseRunV1",
            owner_confirmation_required=True,
            runtime_authorized=False,
            reexecution_authorized=False,
            recalculation_authorized=False,
            delivery_authorized=False,
            metadata=metadata_dict,
        )

    adapter_status = _status_from_pilot(pilot_result.status)
    owner_message = _owner_message(pilot_result, adapter_status)
    next_owner_question = _next_owner_question(pilot_result)
    case_record = _case_record(pilot_result)
    owner_delivery_packet = _owner_delivery_packet(pilot_result, owner_message=owner_message)
    product_gate = _product_gate(pilot_result, adapter_status=adapter_status)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "asset": _asset(pilot_result),
        "owner_message": owner_message,
        "next_owner_question": next_owner_question,
        "case_record": case_record,
        "owner_delivery_packet": owner_delivery_packet,
        "product_gate": product_gate,
        "evidence_loop_status": {
            "pilot_status": pilot_result.status,
            "bridge_status": pilot_result.bridge_status,
            "owner_confirmation_required": pilot_result.owner_confirmation_required,
            "blocked_reason": pilot_result.blocked_reason,
        },
        "metadata": {**metadata_dict, "source_schema_version": SCHEMA_VERSION},
    }
    packet["delivery_policy_guard"] = build_service_1_delivery_policy_guard_v1(packet)

    return Service1RealOwnerPilotToDeliveryPacketAdapterV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=adapter_status,
        case_id=pilot_result.case_id,
        tenant_id=pilot_result.tenant_id,
        intake_id=pilot_result.intake_id,
        run_id=pilot_result.run_id,
        owner_ref=pilot_result.owner_ref,
        source_file_ref=pilot_result.source_file_ref,
        delivery_packet=packet,
        delivery_policy_guard=packet["delivery_policy_guard"],
        owner_message=owner_message,
        next_owner_question=next_owner_question,
        case_record=case_record,
        owner_delivery_packet=owner_delivery_packet,
        product_gate=product_gate,
        blocked_reason=pilot_result.blocked_reason
        if adapter_status in (STATUS_DELIVERY_PACKET_BLOCKED, STATUS_DELIVERY_PACKET_INVALID_INPUT)
        else None,
        owner_confirmation_required=pilot_result.owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={**metadata_dict, "source_schema_version": SCHEMA_VERSION},
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD",
    "STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT",
    "STATUS_DELIVERY_PACKET_BLOCKED",
    "STATUS_DELIVERY_PACKET_INVALID_INPUT",
    "Service1RealOwnerPilotToDeliveryPacketAdapterV1",
    "build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1",
]

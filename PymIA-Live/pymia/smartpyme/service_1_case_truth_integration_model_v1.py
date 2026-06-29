from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

SCHEMA_VERSION = "S1_CASE_TRUTH_INTEGRATION_MODEL_V1"
SERVICE_NAME = "SERVICE_1"

STATUS_READY_FOR_TOOL_PLANNING = "READY_FOR_TOOL_PLANNING"
STATUS_NEEDS_OWNER_CONFIRMATION = "NEEDS_OWNER_CONFIRMATION"
STATUS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
STATUS_CONFLICT_OWNER_DATA = "CONFLICT_OWNER_DATA"
STATUS_BLOCKED_BY_PYMIA_GATE = "BLOCKED_BY_PYMIA_GATE"
STATUS_UNKNOWN = "UNKNOWN"

_SAFE_NEXT_ACTION_BY_STATUS = {
    STATUS_READY_FOR_TOOL_PLANNING: "continue_to_auto_tool_selection_and_mapping",
    STATUS_NEEDS_OWNER_CONFIRMATION: "ask_owner_for_operational_confirmation",
    STATUS_NEEDS_EVIDENCE: "request_missing_evidence",
    STATUS_CONFLICT_OWNER_DATA: "ask_owner_to_resolve_data_conflict",
    STATUS_BLOCKED_BY_PYMIA_GATE: "stop_and_resolve_pymia_gate",
    STATUS_UNKNOWN: "manual_review_required",
}

_BLOCKING_PYMIA_GATE_STATUSES = {
    "BLOCKED",
    "BLOCKED_BY_PYMIA_GATE",
    "FAIL",
    "FAILED",
    "DENIED",
    "REJECTED",
}

_READY_PYMIA_GATE_STATUSES = {
    "OK",
    "PASS",
    "PASSED",
    "ALLOWED",
    "READY",
}

_READY_DATA_STATUSES = {
    "OK",
    "PASS",
    "READY",
}

_SUFFICIENT_EVIDENCE_STATUSES = {
    "OK",
    "PASS",
    "SUFFICIENT",
    "READY",
}

_CONFIRMED_COLUMN_STATUSES = {
    "OK",
    "PASS",
    "CONFIRMED",
    "COMPLETE",
    "READY",
}

_PENDING_COLUMN_CONFIRMATION_STATUSES = {
    "NEEDS_OWNER_CONFIRMATION",
    "PENDING",
    "PARTIAL",
    "WAITING_OWNER_ANSWERS",
}


@dataclass(frozen=True)
class Service1CaseTruthIntegrationInputV1:
    owner_intent_present: bool
    owner_axis_confirmed: bool
    owner_axis: str | None
    data_available: bool
    normalized_data_status: str | None
    column_confirmation_status: str | None
    evidence_sufficiency_status: str | None
    supported_family: str | None
    pymia_gate_status: str | None
    detected_data_axis: str | None
    missing_evidence_refs: Sequence[str] = field(default_factory=tuple)
    blockers: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class Service1CaseTruthIntegrationModelV1:
    schema_version: str
    service_name: str
    status: str
    ready_for_tool_planning: bool
    safe_next_action: str
    owner_question_if_needed: str | None
    missing_evidence_refs: tuple[str, ...]
    blocked_reason: str | None
    conflict_reason: str | None
    runtime_authorized: bool
    autonomous_delivery_authorized: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["missing_evidence_refs"] = list(self.missing_evidence_refs)
        return data


def build_service_1_case_truth_integration_model_v1(
    integration_input: Service1CaseTruthIntegrationInputV1,
) -> Service1CaseTruthIntegrationModelV1:
    """Evaluate whether PYMIA + data + PyME owner meaning are ready for tool planning.

    This module is pure: it does not execute tools, generate tool requests, call
    delivery, persist records, authorize runtime, or call conversational services.
    """
    if not isinstance(integration_input, Service1CaseTruthIntegrationInputV1):
        raise ValueError("integration_input must be Service1CaseTruthIntegrationInputV1")

    missing_evidence_refs = tuple(str(ref).strip() for ref in integration_input.missing_evidence_refs if str(ref).strip())
    blockers = tuple(str(blocker).strip() for blocker in integration_input.blockers if str(blocker).strip())

    status = _classify_status(
        integration_input,
        missing_evidence_refs=missing_evidence_refs,
        blockers=blockers,
    )

    return Service1CaseTruthIntegrationModelV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        ready_for_tool_planning=status == STATUS_READY_FOR_TOOL_PLANNING,
        safe_next_action=_SAFE_NEXT_ACTION_BY_STATUS[status],
        owner_question_if_needed=_owner_question_for_status(status, integration_input),
        missing_evidence_refs=missing_evidence_refs,
        blocked_reason=_blocked_reason_for_status(status, integration_input, blockers),
        conflict_reason=_conflict_reason_for_status(status, integration_input),
        runtime_authorized=False,
        autonomous_delivery_authorized=False,
    )


def _classify_status(
    integration_input: Service1CaseTruthIntegrationInputV1,
    *,
    missing_evidence_refs: tuple[str, ...],
    blockers: tuple[str, ...],
) -> str:
    pymia_gate_status = _status_text(integration_input.pymia_gate_status)
    if blockers or pymia_gate_status in _BLOCKING_PYMIA_GATE_STATUSES:
        return STATUS_BLOCKED_BY_PYMIA_GATE

    column_confirmation_status = _status_text(integration_input.column_confirmation_status)
    if (
        not integration_input.owner_intent_present
        or not integration_input.owner_axis_confirmed
        or not _text(integration_input.owner_axis)
        or column_confirmation_status in _PENDING_COLUMN_CONFIRMATION_STATUSES
    ):
        return STATUS_NEEDS_OWNER_CONFIRMATION

    normalized_data_status = _status_text(integration_input.normalized_data_status)
    evidence_sufficiency_status = _status_text(integration_input.evidence_sufficiency_status)
    if (
        not integration_input.data_available
        or normalized_data_status not in _READY_DATA_STATUSES
        or evidence_sufficiency_status not in _SUFFICIENT_EVIDENCE_STATUSES
        or missing_evidence_refs
    ):
        return STATUS_NEEDS_EVIDENCE

    if _has_owner_data_conflict(integration_input):
        return STATUS_CONFLICT_OWNER_DATA

    if _is_ready_for_tool_planning(integration_input):
        return STATUS_READY_FOR_TOOL_PLANNING

    return STATUS_UNKNOWN


def _is_ready_for_tool_planning(integration_input: Service1CaseTruthIntegrationInputV1) -> bool:
    return (
        integration_input.owner_intent_present
        and integration_input.owner_axis_confirmed
        and bool(_text(integration_input.owner_axis))
        and integration_input.data_available
        and _status_text(integration_input.normalized_data_status) in _READY_DATA_STATUSES
        and _column_confirmation_ready(integration_input.column_confirmation_status)
        and _status_text(integration_input.evidence_sufficiency_status) in _SUFFICIENT_EVIDENCE_STATUSES
        and bool(_text(integration_input.supported_family))
        and _status_text(integration_input.pymia_gate_status) in _READY_PYMIA_GATE_STATUSES
        and bool(_text(integration_input.detected_data_axis))
        and not _has_owner_data_conflict(integration_input)
    )


def _column_confirmation_ready(value: str | None) -> bool:
    if value is None:
        return True
    return _status_text(value) in _CONFIRMED_COLUMN_STATUSES


def _has_owner_data_conflict(integration_input: Service1CaseTruthIntegrationInputV1) -> bool:
    owner_axis = _axis(integration_input.owner_axis)
    detected_axis = _axis(integration_input.detected_data_axis)
    return bool(owner_axis and detected_axis and owner_axis != detected_axis)


def _owner_question_for_status(
    status: str,
    integration_input: Service1CaseTruthIntegrationInputV1,
) -> str | None:
    if status == STATUS_NEEDS_OWNER_CONFIRMATION:
        return "¿Qué querés revisar primero y qué representa este eje en tus datos?"
    if status == STATUS_NEEDS_EVIDENCE:
        return "Necesito la evidencia faltante para continuar con seguridad."
    if status == STATUS_CONFLICT_OWNER_DATA:
        return (
            "El eje que confirmaste no coincide con el eje detectado en los datos. "
            "¿Cuál representa mejor el caso real?"
        )
    if status == STATUS_UNKNOWN and _text(integration_input.owner_axis):
        return "Necesito una confirmación adicional para clasificar este caso."
    return None


def _blocked_reason_for_status(
    status: str,
    integration_input: Service1CaseTruthIntegrationInputV1,
    blockers: tuple[str, ...],
) -> str | None:
    if status != STATUS_BLOCKED_BY_PYMIA_GATE:
        return None
    if blockers:
        return "; ".join(blockers)
    return f"PymIA gate status blocks planning: {_text(integration_input.pymia_gate_status)}"


def _conflict_reason_for_status(
    status: str,
    integration_input: Service1CaseTruthIntegrationInputV1,
) -> str | None:
    if status != STATUS_CONFLICT_OWNER_DATA:
        return None
    return (
        f"owner_axis={_text(integration_input.owner_axis)!r} conflicts with "
        f"detected_data_axis={_text(integration_input.detected_data_axis)!r}"
    )


def _axis(value: str | None) -> str:
    return _text(value).lower().replace(" ", "_").replace("-", "_")


def _status_text(value: str | None) -> str:
    return _text(value).upper()


def _text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_READY_FOR_TOOL_PLANNING",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_CONFLICT_OWNER_DATA",
    "STATUS_BLOCKED_BY_PYMIA_GATE",
    "STATUS_UNKNOWN",
    "Service1CaseTruthIntegrationInputV1",
    "Service1CaseTruthIntegrationModelV1",
    "build_service_1_case_truth_integration_model_v1",
]

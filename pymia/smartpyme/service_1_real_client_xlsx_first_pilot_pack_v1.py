from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_xlsx_first_product_entrypoint_v1 import (
    STATUS_BLOCKED as ENTRYPOINT_STATUS_BLOCKED,
    STATUS_DELIVERY_PACKAGE_CANDIDATE_READY,
    STATUS_NEXT_OWNER_QUESTION,
    Service1XlsxFirstProductEntrypointV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_REAL_CLIENT_XLSX_FIRST_PILOT_PACK_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_PILOT_PACK_READY: Final[str] = "PILOT_PACK_READY"
STATUS_PILOT_PACK_NEEDS_OWNER_INPUT: Final[str] = "PILOT_PACK_NEEDS_OWNER_INPUT"
STATUS_PILOT_PACK_BLOCKED: Final[str] = "PILOT_PACK_BLOCKED"

PilotPackStatusV1 = Literal[
    "PILOT_PACK_READY",
    "PILOT_PACK_NEEDS_OWNER_INPUT",
    "PILOT_PACK_BLOCKED",
]

_REQUIRED_INTAKE_ITEMS: Final[tuple[str, ...]] = (
    "xlsx_file_available",
    "owner_problem_narrative",
    "business_period_reference",
    "column_meaning_confirmations",
    "available_data_fields",
)

_DEFAULT_STOP_RULES: Final[tuple[str, ...]] = (
    "Stop if the owner cannot confirm the business meaning of required columns.",
    "Stop if the file does not contain enough evidence for the selected pathology.",
    "Stop if the case expands beyond the selected Servicio 1 XLSX-first scope.",
    "Stop if the result is interpreted as a definitive accounting diagnosis or autonomous delivery.",
)

_DEFAULT_QA_CHECKS: Final[tuple[str, ...]] = (
    "Verify entrypoint status before any pilot conversation output.",
    "Verify owner-facing limits are explicit.",
    "Verify runtime_authorized, reexecution_authorized, recalculation_authorized, and delivery_authorized remain False.",
    "Verify the pilot pack contains either a next owner question or a package candidate summary.",
)


@dataclass(frozen=True)
class Service1RealClientXlsxFirstPilotPackV1:
    schema_version: str
    service_name: str
    status: PilotPackStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    owner_ref: str
    selected_primary_pathology: str | None
    allowed_computation_ref: str | None
    entrypoint_status: str
    pilot_title: str
    intake_checklist: tuple[str, ...]
    missing_intake_items: tuple[str, ...]
    owner_script: tuple[str, ...]
    stop_rules: tuple[str, ...]
    qa_checks: tuple[str, ...]
    pilot_output_summary: str | None
    next_owner_question: str | None
    package_candidate_ref: str | None
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_entrypoint(
    value: Service1XlsxFirstProductEntrypointV1,
) -> Service1XlsxFirstProductEntrypointV1:
    if not isinstance(value, Service1XlsxFirstProductEntrypointV1):
        raise ValueError("entrypoint_result must be a Service1XlsxFirstProductEntrypointV1")
    return value


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values = value if isinstance(value, (list, tuple, set)) else (value,)
    return tuple(text for item in values if (text := _clean_text(item)))


def _bool_item(value: Any) -> bool:
    return value is True


def _metadata_item(metadata: dict[str, Any] | None, key: str) -> Any:
    return dict(metadata or {}).get(key)


def _missing_intake_items(metadata: dict[str, Any] | None) -> tuple[str, ...]:
    return tuple(
        item for item in _REQUIRED_INTAKE_ITEMS if not _bool_item(_metadata_item(metadata, item))
    )


def _pilot_title(entrypoint: Service1XlsxFirstProductEntrypointV1) -> str:
    pathology = entrypoint.selected_primary_pathology or "patología pendiente"
    return f"Piloto real Servicio 1 XLSX-first - {pathology}"


def _owner_script(entrypoint: Service1XlsxFirstProductEntrypointV1) -> tuple[str, ...]:
    if entrypoint.status == STATUS_NEXT_OWNER_QUESTION:
        question = entrypoint.next_owner_question or "Necesito una confirmación adicional del dueño antes de avanzar."
        return (
            "Voy a revisar el archivo sólo dentro del alcance Servicio 1 XLSX-first.",
            "Antes de calcular o empaquetar algo, necesito cerrar una duda de negocio.",
            question,
        )

    if entrypoint.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_READY:
        return (
            "El caso ya produjo un paquete candidato para revisar con el dueño.",
            "El resultado es operativo y acotado al archivo y a la evidencia disponible.",
            "Revisemos juntos los límites antes de tratarlo como salida final.",
        )

    return (
        "El caso no está listo para piloto operativo.",
        "Hay que resolver el bloqueo informado antes de avanzar.",
    )


def _output_summary(entrypoint: Service1XlsxFirstProductEntrypointV1) -> str | None:
    if entrypoint.status == STATUS_NEXT_OWNER_QUESTION:
        return "El piloto queda en modo pregunta al dueño; no hay paquete candidato todavía."
    if entrypoint.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_READY:
        package = entrypoint.delivery_package_candidate
        if package is None:
            return "El entrypoint declaró paquete candidato, pero el paquete no está disponible."
        return package.owner_summary
    if entrypoint.status == ENTRYPOINT_STATUS_BLOCKED:
        return None
    return None


def _package_candidate_ref(entrypoint: Service1XlsxFirstProductEntrypointV1) -> str | None:
    package = entrypoint.delivery_package_candidate
    if package is None:
        return None
    return package.package_id


def _build(
    *,
    entrypoint: Service1XlsxFirstProductEntrypointV1,
    status: PilotPackStatusV1,
    intake_checklist: tuple[str, ...],
    missing_intake_items: tuple[str, ...],
    blocked_reason: str | None,
    owner_confirmation_required: bool,
    metadata: dict[str, Any] | None,
) -> Service1RealClientXlsxFirstPilotPackV1:
    return Service1RealClientXlsxFirstPilotPackV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=entrypoint.case_id,
        tenant_id=entrypoint.tenant_id,
        intake_id=entrypoint.intake_id,
        run_id=entrypoint.run_id,
        owner_ref=entrypoint.owner_ref,
        selected_primary_pathology=entrypoint.selected_primary_pathology,
        allowed_computation_ref=entrypoint.allowed_computation_ref,
        entrypoint_status=entrypoint.status,
        pilot_title=_pilot_title(entrypoint),
        intake_checklist=intake_checklist,
        missing_intake_items=missing_intake_items,
        owner_script=_owner_script(entrypoint),
        stop_rules=_clean_tuple(_metadata_item(metadata, "stop_rules")) or _DEFAULT_STOP_RULES,
        qa_checks=_clean_tuple(_metadata_item(metadata, "qa_checks")) or _DEFAULT_QA_CHECKS,
        pilot_output_summary=_output_summary(entrypoint),
        next_owner_question=entrypoint.next_owner_question,
        package_candidate_ref=_package_candidate_ref(entrypoint),
        blocked_reason=blocked_reason,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_real_client_xlsx_first_pilot_pack_v1(
    *,
    entrypoint_result: Service1XlsxFirstProductEntrypointV1,
    metadata: dict[str, Any] | None = None,
) -> Service1RealClientXlsxFirstPilotPackV1:
    """Build a pure real-client pilot pack around the closed XLSX-first entrypoint.

    The pack is a preparation artifact only. It does not read files, write files,
    publish outputs, call external tools, open SaaS behavior, or authorize delivery.
    """

    entrypoint = _required_entrypoint(entrypoint_result)
    intake_checklist = _clean_tuple(_metadata_item(metadata, "intake_checklist")) or _REQUIRED_INTAKE_ITEMS
    missing_items = _missing_intake_items(metadata)

    if entrypoint.status == ENTRYPOINT_STATUS_BLOCKED:
        return _build(
            entrypoint=entrypoint,
            status=STATUS_PILOT_PACK_BLOCKED,
            intake_checklist=intake_checklist,
            missing_intake_items=missing_items,
            blocked_reason=entrypoint.blocked_reason or "entrypoint_blocked",
            owner_confirmation_required=entrypoint.owner_confirmation_required,
            metadata=metadata,
        )

    if entrypoint.status == STATUS_NEXT_OWNER_QUESTION:
        return _build(
            entrypoint=entrypoint,
            status=STATUS_PILOT_PACK_NEEDS_OWNER_INPUT,
            intake_checklist=intake_checklist,
            missing_intake_items=missing_items,
            blocked_reason=None,
            owner_confirmation_required=True,
            metadata=metadata,
        )

    if entrypoint.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_READY and not missing_items:
        return _build(
            entrypoint=entrypoint,
            status=STATUS_PILOT_PACK_READY,
            intake_checklist=intake_checklist,
            missing_intake_items=(),
            blocked_reason=None,
            owner_confirmation_required=False,
            metadata=metadata,
        )

    return _build(
        entrypoint=entrypoint,
        status=STATUS_PILOT_PACK_NEEDS_OWNER_INPUT,
        intake_checklist=intake_checklist,
        missing_intake_items=missing_items,
        blocked_reason="missing_required_pilot_intake_items" if missing_items else None,
        owner_confirmation_required=True,
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_PILOT_PACK_READY",
    "STATUS_PILOT_PACK_NEEDS_OWNER_INPUT",
    "STATUS_PILOT_PACK_BLOCKED",
    "Service1RealClientXlsxFirstPilotPackV1",
    "build_service_1_real_client_xlsx_first_pilot_pack_v1",
]

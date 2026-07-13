from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_pathology_first_aid_dry_run_candidate_v1 import (
    STATUS_DRY_RUN_CANDIDATE_BUILT,
    Service1PathologyFirstAidDryRunCandidateV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_OPERATIONAL_FINDING_OWNER_VIEW_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_OWNER_VIEW_BUILT: Final[str] = "OWNER_VIEW_BUILT"
STATUS_BLOCKED_DRY_RUN_NOT_BUILT: Final[str] = "BLOCKED_DRY_RUN_NOT_BUILT"
STATUS_BLOCKED_EMPTY_FINDING: Final[str] = "BLOCKED_EMPTY_FINDING"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_OWNER_VIEW_BUILT,
    STATUS_BLOCKED_DRY_RUN_NOT_BUILT,
    STATUS_BLOCKED_EMPTY_FINDING,
)

OwnerViewStatusV1 = Literal[
    "OWNER_VIEW_BUILT",
    "BLOCKED_DRY_RUN_NOT_BUILT",
    "BLOCKED_EMPTY_FINDING",
]


@dataclass(frozen=True)
class Service1OperationalFindingOwnerViewV1:
    schema_version: str
    service_name: str
    status: OwnerViewStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    pathology_code: str | None
    allowed_computation_ref: str | None
    title: str | None
    finding_summary: str | None
    evidence_used: tuple[str, ...]
    computed_values: dict[str, object]
    limits: tuple[str, ...]
    next_recommended_action: str | None
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_dry_run(
    dry_run_candidate_result: Service1PathologyFirstAidDryRunCandidateV1,
) -> Service1PathologyFirstAidDryRunCandidateV1:
    if not isinstance(dry_run_candidate_result, Service1PathologyFirstAidDryRunCandidateV1):
        raise ValueError("dry_run_candidate_result must be a Service1PathologyFirstAidDryRunCandidateV1")
    return dry_run_candidate_result


def _clean_summary(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _build_blocked_result(
    *,
    dry_run: Service1PathologyFirstAidDryRunCandidateV1,
    status: OwnerViewStatusV1,
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1OperationalFindingOwnerViewV1:
    return Service1OperationalFindingOwnerViewV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=dry_run.case_id,
        tenant_id=dry_run.tenant_id,
        intake_id=dry_run.intake_id,
        run_id=dry_run.run_id,
        pathology_code=dry_run.pathology_code,
        allowed_computation_ref=dry_run.allowed_computation_ref,
        title=None,
        finding_summary=None,
        evidence_used=tuple(sorted(dry_run.input_values.keys())),
        computed_values=dict(dry_run.computed_values),
        limits=(),
        next_recommended_action=None,
        blocked_reason=blocked_reason,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def _ren_owner_view(dry_run: Service1PathologyFirstAidDryRunCandidateV1) -> tuple[str, str, tuple[str, ...], str]:
    unit_margin = dry_run.computed_values.get("unit_margin")
    total_margin = dry_run.computed_values.get("total_margin")
    margin_rate = dry_run.computed_values.get("margin_rate")
    summary = (
        f"En este dry-run, el margen unitario estimado es {unit_margin}, "
        f"el margen total estimado es {total_margin} y la tasa de margen estimada es {margin_rate}."
    )
    limits = (
        "Este resultado no confirma la rentabilidad global de la empresa.",
        "Este resultado depende de los valores cargados y no constituye un diagnóstico definitivo.",
    )
    next_action = "Revisá si precio, costo y cantidad representan correctamente el período que querés analizar."
    return "Margen operativo estimado", summary, limits, next_action


def _liq_owner_view(dry_run: Service1PathologyFirstAidDryRunCandidateV1) -> tuple[str, str, tuple[str, ...], str]:
    collection_gap = dry_run.computed_values.get("collection_gap")
    collection_rate = dry_run.computed_values.get("collection_rate")
    summary = (
        f"En este dry-run, la brecha estimada entre ventas y cobros es {collection_gap} "
        f"y la tasa estimada de cobro sobre ventas es {collection_rate}."
    )
    limits = (
        "Este resultado no confirma la contabilidad definitiva del negocio.",
        "Este resultado no afirma un saldo real de caja definitivo.",
    )
    next_action = "Revisá si ventas y cobros corresponden al mismo período y al mismo criterio de registro."
    return "Brecha estimada entre ventas y cobros", summary, limits, next_action


def _stk_owner_view(dry_run: Service1PathologyFirstAidDryRunCandidateV1) -> tuple[str, str, tuple[str, ...], str]:
    stock_gap = dry_run.computed_values.get("stock_gap")
    below_minimum = dry_run.computed_values.get("below_minimum")
    summary = (
        f"En este dry-run, la diferencia estimada contra el stock mínimo es {stock_gap} "
        f"y el indicador de mínimo sugiere below_minimum={below_minimum}."
    )
    limits = (
        "Este resultado no confirma el inventario real definitivo del negocio.",
        "Este resultado depende de los valores cargados y no reemplaza un conteo físico o validación posterior.",
    )
    next_action = "Revisá si stock actual y stock mínimo están expresados en la misma unidad y período."
    return "Diferencia estimada contra stock mínimo", summary, limits, next_action


def _generic_owner_view(dry_run: Service1PathologyFirstAidDryRunCandidateV1) -> tuple[str, str, tuple[str, ...], str]:
    summary = _clean_summary(dry_run.finding_summary) or "Se generó un hallazgo operativo preliminar para revisar con evidencia."
    limits = (
        "Este resultado es preliminar y no constituye un diagnóstico definitivo.",
    )
    next_action = "Revisá que los datos de entrada representen correctamente el problema operativo que querés analizar."
    return "Hallazgo operativo preliminar", summary, limits, next_action


def _owner_view_content(
    dry_run: Service1PathologyFirstAidDryRunCandidateV1,
) -> tuple[str, str, tuple[str, ...], str]:
    if dry_run.pathology_code == "REN_001":
        return _ren_owner_view(dry_run)
    if dry_run.pathology_code == "LIQ_001":
        return _liq_owner_view(dry_run)
    if dry_run.pathology_code == "STK_001":
        return _stk_owner_view(dry_run)
    return _generic_owner_view(dry_run)


def build_service_1_operational_finding_owner_view_v1(
    *,
    dry_run_candidate_result: Service1PathologyFirstAidDryRunCandidateV1,
    metadata: dict[str, Any] | None = None,
) -> Service1OperationalFindingOwnerViewV1:
    dry_run = _required_dry_run(dry_run_candidate_result)

    if dry_run.status != STATUS_DRY_RUN_CANDIDATE_BUILT:
        return _build_blocked_result(
            dry_run=dry_run,
            status=STATUS_BLOCKED_DRY_RUN_NOT_BUILT,
            blocked_reason="dry_run_candidate_not_built",
            metadata=metadata,
        )

    if not dry_run.computed_values and _clean_summary(dry_run.finding_summary) is None:
        return _build_blocked_result(
            dry_run=dry_run,
            status=STATUS_BLOCKED_EMPTY_FINDING,
            blocked_reason="empty_finding_summary_and_computed_values",
            metadata=metadata,
        )

    title, finding_summary, limits, next_recommended_action = _owner_view_content(dry_run)

    return Service1OperationalFindingOwnerViewV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=STATUS_OWNER_VIEW_BUILT,
        case_id=dry_run.case_id,
        tenant_id=dry_run.tenant_id,
        intake_id=dry_run.intake_id,
        run_id=dry_run.run_id,
        pathology_code=dry_run.pathology_code,
        allowed_computation_ref=dry_run.allowed_computation_ref,
        title=title,
        finding_summary=finding_summary,
        evidence_used=tuple(sorted(dry_run.input_values.keys())),
        computed_values=dict(dry_run.computed_values),
        limits=limits,
        next_recommended_action=next_recommended_action,
        blocked_reason=None,
        owner_confirmation_required=False,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_OWNER_VIEW_BUILT",
    "STATUS_BLOCKED_DRY_RUN_NOT_BUILT",
    "STATUS_BLOCKED_EMPTY_FINDING",
    "ALLOWED_STATUSES",
    "Service1OperationalFindingOwnerViewV1",
    "build_service_1_operational_finding_owner_view_v1",
]

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
)
from pymia.smartpyme.service_1_column_confirmation_classifier_v1 import (
    OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED,
    Service1ColumnConfirmationClassificationV1,
)

SCHEMA_VERSION = "SERVICE_1_COLUMN_CONFIRMATION_APPLIER_V1"
SERVICE_NAME = "SERVICE_1"
DEFAULT_VARIABLES_TO_TRACK = (
    "ventas_total",
    "costos_total",
    "cantidad_total",
    "margen_bruto",
    "margen_bruto_pct",
)


@dataclass(frozen=True)
class Service1ColumnConfirmationApplierResultV1:
    schema_version: str
    service_name: str
    case_id: str
    tenant_id: str
    intake_id: str
    target_ref: str
    parsed_target_ref: dict[str, str]
    applied_entry_snapshot: ColumnConfirmationEntry
    matrix_status_before: str
    matrix_status_after: str
    computation_unlocked: bool
    variables_affected: list[str]
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    owner_answer_validation_status: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["applied_entry_snapshot"] = self.applied_entry_snapshot.model_dump()
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _optional_text(value: str | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value).strip()
    return value.strip()


def _tracked_variable_names(variables_to_track: Iterable[str] | None) -> list[str]:
    if variables_to_track is None:
        return list(DEFAULT_VARIABLES_TO_TRACK)
    names = [str(name).strip() for name in variables_to_track if str(name).strip()]
    return sorted(dict.fromkeys(names))


def _variable_gate_snapshot(
    matrix: ColumnConfirmationMatrix,
    variable_names: list[str],
) -> dict[str, bool]:
    return {variable_name: matrix.can_compute_variable(variable_name) for variable_name in variable_names}


def apply_service_1_column_confirmation_v1(
    *,
    classification: Service1ColumnConfirmationClassificationV1,
    matrix: ColumnConfirmationMatrix,
    case_id: str | None = None,
    tenant_id: str | None = None,
    intake_id: str | None = None,
    variables_to_track: Iterable[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnConfirmationApplierResultV1:
    if not isinstance(classification, Service1ColumnConfirmationClassificationV1):
        raise ValueError("classification must be a Service1ColumnConfirmationClassificationV1")
    if not isinstance(matrix, ColumnConfirmationMatrix):
        raise ValueError("matrix must be a ColumnConfirmationMatrix")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    variable_names = _tracked_variable_names(variables_to_track)
    matrix_status_before = matrix.status()
    gate_before = _variable_gate_snapshot(matrix, variable_names)

    applied_entry = matrix.apply_owner_answer(classification.owner_column_confirmation_answer)
    applied_entry_snapshot = applied_entry.model_copy(deep=True)

    matrix_status_after = matrix.status()
    gate_after = _variable_gate_snapshot(matrix, variable_names)

    variables_affected = [
        variable_name
        for variable_name in variable_names
        if gate_before.get(variable_name) != gate_after.get(variable_name)
    ]
    computation_unlocked = any(
        gate_before.get(variable_name) is False and gate_after.get(variable_name) is True
        for variable_name in variable_names
    )

    return Service1ColumnConfirmationApplierResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=_optional_text(case_id),
        tenant_id=_optional_text(tenant_id),
        intake_id=_optional_text(intake_id),
        target_ref=classification.target_ref,
        parsed_target_ref=classification.parsed_target_ref.to_dict(),
        applied_entry_snapshot=applied_entry_snapshot,
        matrix_status_before=matrix_status_before,
        matrix_status_after=matrix_status_after,
        computation_unlocked=computation_unlocked,
        variables_affected=variables_affected,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        owner_answer_validation_status=OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "DEFAULT_VARIABLES_TO_TRACK",
    "Service1ColumnConfirmationApplierResultV1",
    "apply_service_1_column_confirmation_v1",
]

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_V1"
SERVICE_NAME = "SERVICE_1"

OWNER_RESPONSE_SI = "SÍ"
OWNER_RESPONSE_NO = "NO"
OWNER_RESPONSE_TU_RESPUESTA = "TU_RESPUESTA"
ALLOWED_OWNER_RESPONSES = (
    OWNER_RESPONSE_SI,
    OWNER_RESPONSE_NO,
    OWNER_RESPONSE_TU_RESPUESTA,
)

_INTERNAL_ROLE_HINTS = (
    "venta_total",
    "precio_venta",
    "costo_unitario",
    "costo_total",
    "computed_variables",
    "margen_bruto",
    "margen_bruto_pct",
)


@dataclass(frozen=True)
class Service1ColumnConfirmationOwnerPromptV1:
    schema_version: str
    service_name: str
    file_name: str
    sheet_name: str
    column_name: str
    suggested_semantic_role: str
    owner_facing_role_explanation: str
    prompt_text: str
    allowed_owner_responses: tuple[str, ...]
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_owner_responses"] = list(self.allowed_owner_responses)
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _assert_owner_text_does_not_expose_internal_terms(prompt_text: str) -> None:
    lowered = prompt_text.lower()
    leaked = [hint for hint in _INTERNAL_ROLE_HINTS if hint in lowered]
    if leaked:
        raise ValueError(f"owner prompt exposes internal semantic terms: {leaked}")


def build_service_1_column_confirmation_owner_prompt_v1(
    *,
    file_name: str,
    sheet_name: str,
    column_name: str,
    suggested_semantic_role: str,
    owner_facing_role_explanation: str,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnConfirmationOwnerPromptV1:
    """Render an owner-facing semantic confirmation prompt for one Excel column.

    PymIA must interpret first, explain its interpretation in PyME language, and
    ask the owner for a constrained answer: SÍ, NO, or TU_RESPUESTA.

    This function is pure. It does not classify, mutate a matrix, persist, recalc,
    reexecute, or treat owner text as validated evidence.
    """

    file_name = _required_text(file_name, field_name="file_name")
    sheet_name = _required_text(sheet_name, field_name="sheet_name")
    column_name = _required_text(column_name, field_name="column_name")
    suggested_semantic_role = _required_text(
        suggested_semantic_role,
        field_name="suggested_semantic_role",
    )
    owner_facing_role_explanation = _required_text(
        owner_facing_role_explanation,
        field_name="owner_facing_role_explanation",
    )
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    prompt_text = (
        "Dueño, revisé tu Excel y entendí esta columna así:\n\n"
        f"Archivo: \"{file_name}\"\n"
        f"Hoja: \"{sheet_name}\"\n"
        f"Columna: \"{column_name}\"\n\n"
        "Interpretación de PymIA:\n"
        f"{owner_facing_role_explanation}\n\n"
        "Confirmame:\n"
        "SÍ = correcto\n"
        "NO = no es eso\n"
        "TU_RESPUESTA = corregime qué significa"
    )
    _assert_owner_text_does_not_expose_internal_terms(prompt_text)

    return Service1ColumnConfirmationOwnerPromptV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        file_name=file_name,
        sheet_name=sheet_name,
        column_name=column_name,
        suggested_semantic_role=suggested_semantic_role,
        owner_facing_role_explanation=owner_facing_role_explanation,
        prompt_text=prompt_text,
        allowed_owner_responses=ALLOWED_OWNER_RESPONSES,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "OWNER_RESPONSE_SI",
    "OWNER_RESPONSE_NO",
    "OWNER_RESPONSE_TU_RESPUESTA",
    "ALLOWED_OWNER_RESPONSES",
    "Service1ColumnConfirmationOwnerPromptV1",
    "build_service_1_column_confirmation_owner_prompt_v1",
]

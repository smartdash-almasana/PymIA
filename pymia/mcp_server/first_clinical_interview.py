from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pymia.interfaces.conversational_port import (
    ClinicalConversationalPort,
    ConversationalInput,
)
from pymia.services.initial_laboratory_anamnesis_service import (
    LaboratorioInicialContrato,
    AnamnesisOriginaria,
    InitialLaboratoryAnamnesisService,
    ESTADO_ENCUADRE_TAXONOMICO,
    ProgressiveTenantClinicalContext,
)

TOOL_NAME = "pymia.first_clinical_interview.v1"


def _dump_model(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _error(error_code: str, error_message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": "error",
        "error_code": error_code,
        "error_message": error_message,
        "details": details,
    }


def _validate_required_text(value: Any, field_name: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _parse_previous_context(
    *,
    tenant_id: str,
    previous_progressive_context: Any,
) -> ProgressiveTenantClinicalContext | None | dict[str, Any]:
    if previous_progressive_context is None:
        return None
    if isinstance(previous_progressive_context, ProgressiveTenantClinicalContext):
        context = previous_progressive_context
    elif isinstance(previous_progressive_context, dict):
        try:
            context = ProgressiveTenantClinicalContext.model_validate(previous_progressive_context)
        except ValidationError as exc:
            return _error(
                "CONTEXT_SCHEMA_INVALID",
                "El previous_progressive_context no cumple el schema esperado.",
                {"validation_errors": exc.errors()},
            )
    else:
        return _error(
            "CONTEXT_SCHEMA_INVALID",
            "El previous_progressive_context debe ser objeto o null.",
            {"received_type": type(previous_progressive_context).__name__},
        )

    if context.tenant_id != tenant_id:
        return _error(
            "TENANT_ISOLATION_VIOLATION",
            "El tenant_id del contexto progresivo no coincide con el tenant_id del input.",
            {
                "input_tenant_id": tenant_id,
                "context_tenant_id": context.tenant_id,
            },
        )
    return context


def invoke_first_clinical_interview(
    *,
    tenant_id: str,
    channel: str,
    text: str,
    previous_progressive_context: Any = None,
) -> dict[str, Any]:
    """Pure invocation wrapper for MCP tool `pymia.first_clinical_interview.v1`.

    This function is intentionally transport-agnostic so tests can validate the
    PymIA contract without spawning the MCP stdio server.
    """
    clean_tenant_id = _validate_required_text(tenant_id, "tenant_id")
    clean_channel = _validate_required_text(channel, "channel")
    clean_text = _validate_required_text(text, "text")
    if clean_tenant_id is None or clean_channel is None or clean_text is None:
        return _error(
            "INVALID_INPUT",
            "tenant_id, channel y text son obligatorios y no pueden estar vacíos.",
            {
                "tenant_id_valid": clean_tenant_id is not None,
                "channel_valid": clean_channel is not None,
                "text_valid": clean_text is not None,
            },
        )

    previous_context = _parse_previous_context(
        tenant_id=clean_tenant_id,
        previous_progressive_context=previous_progressive_context,
    )
    if isinstance(previous_context, dict) and previous_context.get("status") == "error":
        return previous_context

    output = ClinicalConversationalPort().handle(
        ConversationalInput(
            tenant_id=clean_tenant_id,
            channel=clean_channel,
            text=clean_text,
            previous_progressive_context=previous_context,
        )
    )

    if output.status == "no_signal":
        taxonomic_response = _build_taxonomic_confirmation_response(
            tenant_id=clean_tenant_id,
            channel=clean_channel,
            text=clean_text,
            previous_context=previous_context if isinstance(previous_context, ProgressiveTenantClinicalContext) else None,
        )
        if taxonomic_response is not None:
            return taxonomic_response

    estado_conversacional = None
    if output.anamnesis is not None:
        estado_conversacional = output.anamnesis.estado_conversacional
    elif output.status == "no_signal":
        estado_conversacional = "no_signal"

    response: dict[str, Any] = {
        "status": output.status,
        "estado_conversacional": estado_conversacional,
        "message": output.message,
        "anamnesis": _dump_model(output.anamnesis),
        "laboratorio": _dump_model(output.laboratorio),
        "progressive_context": _dump_model(output.progressive_context),
    }

    return response


def _build_taxonomic_confirmation_response(
    *,
    tenant_id: str,
    channel: str,
    text: str,
    previous_context: ProgressiveTenantClinicalContext | None,
) -> dict[str, Any] | None:
    service = InitialLaboratoryAnamnesisService()
    current_context = service._build_progressive_tenant_context(
        tenant_id=tenant_id,
        channel=channel,
        text=text,
        evidence=None,
    )
    merged_context = service._merge_progressive_context(
        tenant_id=tenant_id,
        previous=previous_context,
        current=current_context,
    )

    identity = merged_context.business_identity
    is_taxonomic_confirmation = (
        identity.taxonomy_phase == "FASE_0_IDENTIDAD"
        and identity.industry_hint is not None
    )
    if not is_taxonomic_confirmation:
        return None

    anamnesis = AnamnesisOriginaria(
        tenant_id=tenant_id,
        canal=channel,
        frases_textuales=[text],
        dolores_detectados=[],
        hipotesis_iniciales=[],
        taxonomia_inicial={
            "rubro": None,
            "tipo_pyme": None,
            "produce_o_revende": None,
            "maneja_stock": None,
        },
        documentos_pedidos=[],
        estado_conversacional=ESTADO_ENCUADRE_TAXONOMICO,
    )
    laboratorio = LaboratorioInicialContrato(
        tenant_id=tenant_id,
        estado_conversacional=ESTADO_ENCUADRE_TAXONOMICO,
        hipotesis_a_contrastar=[],
        evidencia_requerida=[],
        capability="encuadre_taxonomico",
        tipo_documental_esperado=[],
        campos_esperados=[],
        nivel_confianza="sin_contexto_taxonomico",
        limite_actual="No se puede iniciar análisis sin conocer el tipo de organismo.",
    )

    return {
        "status": "ok",
        "estado_conversacional": ESTADO_ENCUADRE_TAXONOMICO,
        "message": "Identidad taxonómica registrada. Ya tengo el encuadre base para continuar sin diagnóstico.",
        "anamnesis": _dump_model(anamnesis),
        "laboratorio": _dump_model(laboratorio),
        "progressive_context": _dump_model(merged_context),
    }

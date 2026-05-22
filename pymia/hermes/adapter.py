"""
adapter.py — Adapter Hermes ↔ ClinicalConversationalPort (offline).

Este módulo es un wrapper transitorio de compatibilidad. No reduce Hermes a
texto plano: cuando Hermes/conversa-engine entrega evidence_bundle, lo preserva
y lo pasa contractualmente al puerto conversacional.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from pymia.contracts.attachment_lifecycle_v1 import EvidenceBundle
from pymia.interfaces.conversational_port import (
    ClinicalConversationalPort,
    ConversationalInput,
)
from pymia.services.initial_laboratory_anamnesis_service import (
    AnamnesisOriginaria,
    LaboratorioInicialContrato,
)


class HermesInput(BaseModel):
    """Entrada en vocabulario Hermes.

    Campos
    ------
    tenant_id:
        Identificador del tenant. Obligatorio. Multi-tenant.

    channel:
        Canal de mensajería Hermes (ej: "telegram", "whatsapp", "api").
        El adapter lo propaga sin interpretación.

    message_text:
        Texto libre del mensaje recibido por Hermes.
        Se mapea directamente a ConversationalInput.text.

    metadata:
        Diccionario opaco de contexto Hermes (message_id, user_id,
        timestamp, etc.). El kernel clínico NUNCA lo lee.
        Se preserva en HermesOutput.payload para trazabilidad.

    evidence_bundle:
        Agrupación de adjuntos recibidos y su estado de procesamiento.
    """

    tenant_id: str = Field(..., description="Identificador del tenant.")
    channel: str = Field(..., description="Canal Hermes de origen.")
    message_text: str = Field(
        ...,
        description="Texto del mensaje recibido por Hermes.",
        min_length=1,
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Contexto opaco de Hermes. Solo trazabilidad.",
    )
    evidence_bundle: EvidenceBundle | None = Field(
        default=None,
        description="Lifecycle contractual de adjuntos y evidencia computable.",
    )
    evidence_bundle: EvidenceBundle | None = Field(
        default=None,
        description="Agrupación de adjuntos recibidos y su estado de procesamiento.",
    )


class HermesPayload(BaseModel):
    """Payload estructurado de salida. Solo lectura para Hermes."""

    anamnesis: AnamnesisOriginaria | None = Field(None)
    laboratorio: LaboratorioInicialContrato | None = Field(None)
    input_metadata: dict[str, Any] = Field(default_factory=dict)
    evidence_bundle: EvidenceBundle | None = Field(
        default=None,
        description="Lifecycle de adjuntos preservado para trazabilidad.",
    )


class HermesOutput(BaseModel):
    """Salida en vocabulario Hermes."""

    status: Literal["ok", "no_signal", "error"] = Field(...)
    mode: Literal["anamnesis_inicial", "no_signal"] = Field(...)
    reply_text: str | None = Field(None)
    payload: HermesPayload = Field(default_factory=HermesPayload)


class HermesAdapter:
    """Wrapper contractual Hermes ↔ ClinicalConversationalPort."""

    def __init__(self) -> None:
        self._port = ClinicalConversationalPort()

    def handle(self, hermes_input: HermesInput) -> HermesOutput:
        """Adapta una entrada Hermes y retorna una salida Hermes."""
        evidence = None
        if hermes_input.evidence_bundle is not None:
            evidence = hermes_input.evidence_bundle.first_structured_evidence()

        clinical_input = ConversationalInput(
            tenant_id=hermes_input.tenant_id,
            channel=hermes_input.channel,
            text=hermes_input.message_text,
            bundle=hermes_input.evidence_bundle,
        )

        clinical_output = self._port.handle(clinical_input)

        payload = HermesPayload(
            anamnesis=clinical_output.anamnesis,
            laboratorio=clinical_output.laboratorio,
            input_metadata=hermes_input.metadata,
            evidence_bundle=hermes_input.evidence_bundle,
        )

        return HermesOutput(
            status=clinical_output.status,
            mode=clinical_output.mode,
            reply_text=clinical_output.message,
            payload=payload,
        )

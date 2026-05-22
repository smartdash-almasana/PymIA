"""
conversational_port.py — Puerto de entrada conversacional clínica de PymIA.

BOUNDARY CONTRACT
=================
Este módulo define la única superficie pública que una interfaz externa
(Hermes, Telegram, API REST, CLI, etc.) puede tocar para hablar con
el kernel clínico de PymIA.

INVARIANTES DEL BOUNDARY
-------------------------
1. El port acepta SOLO contexto clínico de entrada:
   tenant_id, channel, text y evidence estructurada opcional.
   No recibe: job_id, workflow_id, authorization_token, decision_type,
   create_job, orchestration_context ni ningún artefacto de factoría.

2. El port devuelve SOLO (status, mode, message, anamnesis, laboratorio).
   No devuelve: job_created, workflow_step, authorization_result,
   approval_required ni ningún artefacto de orquestación.

3. El port NO contiene lógica clínica. Delega siempre al kernel.
   La lógica clínica vive en:
     pymia.pipeline.admission.v1
     pymia.services.initial_laboratory_anamnesis_service

4. El port es stateless. No persiste, no cachea, no acumula estado.

5. El port no conoce el modelo de lenguaje, el runtime de Hermes
   ni la infraestructura de mensajería.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.attachment_lifecycle_v1 import EvidenceBundle
from pymia.services.initial_laboratory_anamnesis_service import (
    AnamnesisOriginaria,
    InitialLaboratoryAnamnesisService,
    LaboratorioInicialContrato,
)


class ConversationalInput(BaseModel):
    """
    Entrada al puerto conversacional clínico.

    `text` transporta relato del dueño.
    `evidence` transporta hechos documentales estructurados.

    Regla: los documentos no deben convertirse en claims narrativos para
    cruzar este boundary.
    """

    tenant_id: str = Field(..., description="Identificador del tenant.")
    channel: str = Field(..., description="Canal de entrada.")
    text: str = Field(
        ...,
        description="Texto libre del dueño. Relato, no evidencia documental.",
        min_length=1,
    )
    evidence: StructuredEvidence | None = Field(
        default=None,
        description="Evidencia documental estructurada opcional.",
    )
    bundle: EvidenceBundle | None = Field(
        default=None,
        description="Agrupación de adjuntos recibidos y su estado de procesamiento.",
    )


class ConversationalOutput(BaseModel):
    """Salida del puerto conversacional clínico."""

    status: Literal["ok", "no_signal", "error"] = Field(...)
    mode: Literal["anamnesis_inicial", "no_signal"] = Field(...)
    message: str | None = Field(None)
    anamnesis: AnamnesisOriginaria | None = Field(None)
    laboratorio: LaboratorioInicialContrato | None = Field(None)


class ClinicalConversationalPort:
    """Puerto de entrada conversacional para el kernel clínico de PymIA."""

    def __init__(self) -> None:
        self._service = InitialLaboratoryAnamnesisService()

    def handle(self, input: ConversationalInput) -> ConversationalOutput:
        result = self._service.process(
            tenant_id=input.tenant_id,
            channel=input.channel,
            text=input.text,
            evidence=input.evidence,
            bundle=input.bundle,
        )

        if result is None:
            return ConversationalOutput(
                status="no_signal",
                mode="no_signal",
                message=None,
                anamnesis=None,
                laboratorio=None,
            )

        return ConversationalOutput(
            status="ok",
            mode="anamnesis_inicial",
            message=result.message,
            anamnesis=result.anamnesis,
            laboratorio=result.laboratorio,
        )


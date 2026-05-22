from __future__ import annotations

from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field
from pymia.contracts.evidence_v1 import StructuredEvidence


class AttachmentLifecycleState(str, Enum):
    RECEIVED = "RECEIVED"
    DOWNLOADED = "DOWNLOADED"
    PARSE_ATTEMPTED = "PARSE_ATTEMPTED"
    PARSE_FAILED = "PARSE_FAILED"
    PARSE_SUCCEEDED = "PARSE_SUCCEEDED"
    PASSED_TO_PORT = "PASSED_TO_PORT"
    ACKNOWLEDGED_TO_USER = "ACKNOWLEDGED_TO_USER"


class AttachmentParseStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class AttachmentProcessingStatus(BaseModel):
    """Estado y ciclo de vida de un archivo adjunto ingresado como evidencia."""

    attachment_id: str = Field(
        default_factory=lambda: f"att-{uuid4()}",
        description="Identificador único global del archivo adjunto.",
    )
    file_name: str = Field(..., description="Nombre original del archivo.")
    mime_type: str = Field(
        default="application/octet-stream",
        description="Mime-type detectado del archivo.",
    )
    source_channel: str = Field(
        default="telegram",
        description="Canal de origen donde se recibió el adjunto.",
    )
    lifecycle_state: AttachmentLifecycleState = Field(
        ...,
        description="Estado actual del ciclo de vida del adjunto.",
    )
    parse_status: AttachmentParseStatus = Field(
        default=AttachmentParseStatus.PENDING,
        description="Resultado del parseo estructurado.",
    )
    parse_error: str | None = Field(
        default=None,
        description="Detalles internos del error/traceback (auditable, no apto para usuario final).",
    )
    root_cause: str | None = Field(
        default=None,
        description="Causa raíz segura de error para control interno.",
    )
    user_message: str | None = Field(
        default=None,
        description="Mensaje explicativo y amigable para el usuario final.",
    )
    parser_name: str | None = Field(
        default=None,
        description="Nombre del parser utilizado para procesar el adjunto.",
    )
    evidence: StructuredEvidence | None = Field(
        default=None,
        description="Evidencia estructurada resultante si parse_status == SUCCEEDED.",
    )


class EvidenceBundle(BaseModel):
    """Agrupación de adjuntos recibidos en una interacción."""

    attachments: list[AttachmentProcessingStatus] = Field(
        default_factory=list,
        description="Colección de estados de procesamiento de los adjuntos.",
    )


class PymIAIngressEnvelope(BaseModel):
    """Sobre o envelope de ingreso soberano para PymIA."""

    tenant_id: str
    channel: str
    text: str
    bundle: EvidenceBundle

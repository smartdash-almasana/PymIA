from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from pymia.contracts.evidence_v1 import StructuredEvidence


class AttachmentLifecycleState(StrEnum):
    RECEIVED = "RECEIVED"
    DOWNLOADED = "DOWNLOADED"
    PARSE_ATTEMPTED = "PARSE_ATTEMPTED"
    PARSE_FAILED = "PARSE_FAILED"
    PARSE_SUCCEEDED = "PARSE_SUCCEEDED"
    PASSED_TO_PORT = "PASSED_TO_PORT"
    ACKNOWLEDGED_TO_USER = "ACKNOWLEDGED_TO_USER"


class AttachmentParseStatus(StrEnum):
    NOT_ATTEMPTED = "not_attempted"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class AttachmentProcessingStatus(BaseModel):
    """Lifecycle and parsing status for one inbound attachment.

    This contract intentionally keeps processing state outside StructuredEvidence.
    StructuredEvidence carries computable evidence; this contract carries the
    attachment lifecycle, parse status, and safe communication fields.
    """

    attachment_id: str = Field(..., min_length=1)
    file_name: str | None = None
    mime_type: str | None = None
    source_channel: str
    lifecycle_state: AttachmentLifecycleState
    parse_status: AttachmentParseStatus
    parse_error: str | None = Field(
        default=None,
        description="Internal/auditable technical detail. Not safe for direct user display.",
    )
    root_cause: str | None = Field(
        default=None,
        description="Safe, concise, actionable cause suitable for user-level reporting.",
    )
    user_message: str | None = Field(
        default=None,
        description="Sanitized message suitable for the business owner.",
    )
    parser_name: str | None = None
    evidence: StructuredEvidence | None = None

    @model_validator(mode="after")
    def validate_lifecycle_consistency(self) -> "AttachmentProcessingStatus":
        if self.parse_status == AttachmentParseStatus.FAILED and self.evidence is not None:
            raise ValueError("PARSE_FAILED attachments cannot carry valid StructuredEvidence")
        if self.parse_status == AttachmentParseStatus.SUCCEEDED and self.evidence is None:
            raise ValueError("PARSE_SUCCEEDED attachments must carry StructuredEvidence")
        if self.lifecycle_state == AttachmentLifecycleState.PARSE_FAILED and self.parse_status != AttachmentParseStatus.FAILED:
            raise ValueError("PARSE_FAILED lifecycle requires failed parse_status")
        if self.lifecycle_state == AttachmentLifecycleState.PARSE_SUCCEEDED and self.parse_status != AttachmentParseStatus.SUCCEEDED:
            raise ValueError("PARSE_SUCCEEDED lifecycle requires succeeded parse_status")
        return self

    @property
    def is_failed(self) -> bool:
        return self.parse_status == AttachmentParseStatus.FAILED

    @property
    def is_succeeded(self) -> bool:
        return self.parse_status == AttachmentParseStatus.SUCCEEDED

    @property
    def is_pending(self) -> bool:
        return self.parse_status == AttachmentParseStatus.NOT_ATTEMPTED

    def safe_user_message(self) -> str:
        if self.user_message:
            return self.user_message
        if self.is_failed:
            cause = self.root_cause or "no se pudo procesar el archivo con seguridad"
            file_label = self.file_name or "el archivo"
            return f"Recibí {file_label}, pero no pude procesarlo correctamente. Causa: {cause}."
        if self.is_pending:
            file_label = self.file_name or "el archivo"
            return f"Recibí {file_label}, pero todavía no fue procesado."
        file_label = self.file_name or "el archivo"
        return f"Recibí y procesé {file_label}."


class EvidenceBundle(BaseModel):
    """Sovereign ingress container for attachment evidence lifecycle."""

    attachments: list[AttachmentProcessingStatus] = Field(default_factory=list)

    @property
    def has_attachments(self) -> bool:
        return bool(self.attachments)

    def failed_attachments(self) -> list[AttachmentProcessingStatus]:
        return [attachment for attachment in self.attachments if attachment.is_failed]

    def succeeded_attachments(self) -> list[AttachmentProcessingStatus]:
        return [attachment for attachment in self.attachments if attachment.is_succeeded]

    def pending_attachments(self) -> list[AttachmentProcessingStatus]:
        return [attachment for attachment in self.attachments if attachment.is_pending]

    def first_structured_evidence(self) -> StructuredEvidence | None:
        for attachment in self.succeeded_attachments():
            if attachment.evidence is not None:
                return attachment.evidence
        return None

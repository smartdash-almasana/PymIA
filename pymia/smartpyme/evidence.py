"""
SmartPyme Evidence Record — Minimal Contract Slice.

Registra evidencia recibida (o referenciada) por tenant e intake_id.

Este slice SOLO define el contrato de metadata de evidencia:
    IntakeEvidenceRequest  -->  EvidenceRecord (registrada)

NO diagnostica.
NO lee archivos.
NO calcula hash.
NO valida contenido documental.
NO decide si la evidencia satisface una request.
NO cambia intake_state.
NO ejecuta análisis.
NO despacha microservicios.
NO persiste EvidenceRecord (eso es SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE).

Ver: docs/smartpyme/SMARTPYME_EVIDENCE_RECORD_MINIMAL.md
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Estados de EvidenceRecord
# ---------------------------------------------------------------------------
EVIDENCE_STATUS_RECEIVED = "RECEIVED"
EVIDENCE_STATUS_REGISTERED = "REGISTERED"
EVIDENCE_STATUS_REJECTED = "REJECTED"
EVIDENCE_STATUS_LINKED = "LINKED"
EVIDENCE_STATUS_SUPERSEDED = "SUPERSEDED"

ALLOWED_EVIDENCE_STATUSES = (
    EVIDENCE_STATUS_RECEIVED,
    EVIDENCE_STATUS_REGISTERED,
    EVIDENCE_STATUS_REJECTED,
    EVIDENCE_STATUS_LINKED,
    EVIDENCE_STATUS_SUPERSEDED,
)


# ---------------------------------------------------------------------------
# Source kinds
# ---------------------------------------------------------------------------
SOURCE_KIND_UPLOADED_FILE = "uploaded_file"
SOURCE_KIND_MANUAL_TEXT = "manual_text"
SOURCE_KIND_EXTERNAL_REF = "external_ref"
SOURCE_KIND_GENERATED = "generated"
SOURCE_KIND_UNKNOWN = "unknown"

ALLOWED_SOURCE_KINDS = (
    SOURCE_KIND_UPLOADED_FILE,
    SOURCE_KIND_MANUAL_TEXT,
    SOURCE_KIND_EXTERNAL_REF,
    SOURCE_KIND_GENERATED,
    SOURCE_KIND_UNKNOWN,
)


# ---------------------------------------------------------------------------
# Helper interno
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    """Retorna timestamp actual en formato ISO-8601 UTC."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# EvidenceRecord
# ---------------------------------------------------------------------------
@dataclass
class EvidenceRecord:
    """
    Registro inmutable de evidencia recibida o referenciada.

    Es metadata, no contenido:
    - no abre archivos;
    - no lee bytes;
    - no calcula hash;
    - no valida contenido documental.

    Los campos ``content_hash``, ``size_bytes`` y ``mime_type`` son informativos:
    el slice NO los calcula; si el llamante los provee, se conservan.
    """

    evidence_id: str
    tenant_id: str
    intake_id: str
    request_id: Optional[str]
    evidence_type: str
    source_kind: str
    source_ref: str
    original_filename: Optional[str]
    mime_type: Optional[str]
    size_bytes: Optional[int]
    content_hash: Optional[str]
    status: str
    received_at: str
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialización JSON-safe sin encoder custom."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Factory pública
# ---------------------------------------------------------------------------
def create_evidence_record(
    *,
    tenant_id: str,
    intake_id: str,
    evidence_type: str,
    source_kind: str,
    source_ref: str,
    request_id: Optional[str] = None,
    original_filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    size_bytes: Optional[int] = None,
    content_hash: Optional[str] = None,
    status: str = EVIDENCE_STATUS_RECEIVED,
    notes: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> EvidenceRecord:
    """
    Crea un EvidenceRecord validado (fail-closed).

    No lee archivos.
    No calcula hash.
    No infiere MIME.
    No comprueba existencia física de source_ref.
    No decide si la evidencia satisface una IntakeEvidenceRequest.
    """
    # --- validaciones fail-closed -----------------------------------------
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id is required and must be a non-empty string")
    if not isinstance(intake_id, str) or not intake_id.strip():
        raise ValueError("intake_id is required and must be a non-empty string")
    if not isinstance(evidence_type, str) or not evidence_type.strip():
        raise ValueError("evidence_type is required and must be a non-empty string")
    if not isinstance(source_kind, str) or not source_kind.strip():
        raise ValueError("source_kind is required and must be a non-empty string")
    if not isinstance(source_ref, str) or not source_ref.strip():
        raise ValueError("source_ref is required and must be a non-empty string")

    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError(
            f"source_kind {source_kind!r} not in allowed: {ALLOWED_SOURCE_KINDS}"
        )
    if status not in ALLOWED_EVIDENCE_STATUSES:
        raise ValueError(
            f"status {status!r} not in allowed: {ALLOWED_EVIDENCE_STATUSES}"
        )

    if size_bytes is not None:
        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool):
            raise ValueError("size_bytes must be int or None")
        if size_bytes < 0:
            raise ValueError("size_bytes must be >= 0")

    if notes is not None:
        if not isinstance(notes, list):
            raise ValueError("notes must be a list or None")
        # copia defensiva: no mutar input
        notes_copy = list(notes)
    else:
        notes_copy = []

    if metadata is not None:
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be a dict or None")
        # copia defensiva: no mutar input
        metadata_copy = dict(metadata)
    else:
        metadata_copy = {}

    # --- construcción ------------------------------------------------------
    return EvidenceRecord(
        evidence_id=f"evidence_{uuid.uuid4().hex}",
        tenant_id=tenant_id,
        intake_id=intake_id,
        request_id=request_id,
        evidence_type=evidence_type,
        source_kind=source_kind,
        source_ref=source_ref,
        original_filename=original_filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
        content_hash=content_hash,
        status=status,
        received_at=_now_iso(),
        notes=notes_copy,
        metadata=metadata_copy,
    )


__all__ = [
    "EvidenceRecord",
    "create_evidence_record",
    "EVIDENCE_STATUS_RECEIVED",
    "EVIDENCE_STATUS_REGISTERED",
    "EVIDENCE_STATUS_REJECTED",
    "EVIDENCE_STATUS_LINKED",
    "EVIDENCE_STATUS_SUPERSEDED",
    "ALLOWED_EVIDENCE_STATUSES",
    "SOURCE_KIND_UPLOADED_FILE",
    "SOURCE_KIND_MANUAL_TEXT",
    "SOURCE_KIND_EXTERNAL_REF",
    "SOURCE_KIND_GENERATED",
    "SOURCE_KIND_UNKNOWN",
    "ALLOWED_SOURCE_KINDS",
]

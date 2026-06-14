from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


ANAMNESIS_STATUS_DRAFT = "DRAFT"
ANAMNESIS_STATUS_READY_FOR_EVIDENCE = "READY_FOR_EVIDENCE"
ANAMNESIS_STATUS_BLOCKED = "BLOCKED"

ALLOWED_ANAMNESIS_STATUSES = (
    ANAMNESIS_STATUS_DRAFT,
    ANAMNESIS_STATUS_READY_FOR_EVIDENCE,
    ANAMNESIS_STATUS_BLOCKED,
)


@dataclass(frozen=True)
class BusinessTaxonomy:
    empresa_tipo: str = "desconocido"
    industria: str = "desconocido"
    modelo_comercial: str = "desconocido"
    canales_venta: list[str] = field(default_factory=list)
    areas_criticas: list[str] = field(default_factory=list)
    maneja_stock: bool | None = None
    produce_revende_o_servicio: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnamnesisRecord:
    anamnesis_id: str
    tenant_id: str
    intake_id: str
    raw_owner_message: str
    business_taxonomy: BusinessTaxonomy
    declared_pains: list[str]
    owner_hypotheses: list[str]
    declared_documents: list[str]
    requested_documents: list[str]
    status: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["business_taxonomy"] = self.business_taxonomy.to_dict()
        return payload


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _copy_string_list(value: list[str] | None, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list or None")
    copied: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} items must be strings")
        normalized = item.strip()
        if normalized:
            copied.append(normalized)
    return copied


def create_anamnesis_record(
    *,
    tenant_id: str,
    intake_id: str,
    raw_owner_message: str,
    business_taxonomy: BusinessTaxonomy | dict[str, Any] | None = None,
    declared_pains: list[str] | None = None,
    owner_hypotheses: list[str] | None = None,
    declared_documents: list[str] | None = None,
    requested_documents: list[str] | None = None,
    status: str = ANAMNESIS_STATUS_DRAFT,
    metadata: dict[str, Any] | None = None,
) -> AnamnesisRecord:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id is required and must be a non-empty string")
    if not isinstance(intake_id, str) or not intake_id.strip():
        raise ValueError("intake_id is required and must be a non-empty string")
    if not isinstance(raw_owner_message, str) or not raw_owner_message.strip():
        raise ValueError("raw_owner_message is required and must be a non-empty string")
    if status not in ALLOWED_ANAMNESIS_STATUSES:
        raise ValueError(f"status {status!r} not in allowed: {ALLOWED_ANAMNESIS_STATUSES}")

    if business_taxonomy is None:
        taxonomy = BusinessTaxonomy()
    elif isinstance(business_taxonomy, BusinessTaxonomy):
        taxonomy = business_taxonomy
    elif isinstance(business_taxonomy, dict):
        allowed_keys = BusinessTaxonomy.__dataclass_fields__.keys()
        unknown_keys = set(business_taxonomy) - set(allowed_keys)
        if unknown_keys:
            raise ValueError(f"business_taxonomy has unknown fields: {sorted(unknown_keys)}")
        taxonomy = BusinessTaxonomy(**business_taxonomy)
    else:
        raise ValueError("business_taxonomy must be BusinessTaxonomy, dict or None")

    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    return AnamnesisRecord(
        anamnesis_id=f"anamnesis_{uuid.uuid4().hex}",
        tenant_id=tenant_id.strip(),
        intake_id=intake_id.strip(),
        raw_owner_message=raw_owner_message.strip(),
        business_taxonomy=taxonomy,
        declared_pains=_copy_string_list(declared_pains, field_name="declared_pains"),
        owner_hypotheses=_copy_string_list(owner_hypotheses, field_name="owner_hypotheses"),
        declared_documents=_copy_string_list(declared_documents, field_name="declared_documents"),
        requested_documents=_copy_string_list(requested_documents, field_name="requested_documents"),
        status=status,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "AnamnesisRecord",
    "BusinessTaxonomy",
    "create_anamnesis_record",
    "ANAMNESIS_STATUS_DRAFT",
    "ANAMNESIS_STATUS_READY_FOR_EVIDENCE",
    "ANAMNESIS_STATUS_BLOCKED",
    "ALLOWED_ANAMNESIS_STATUSES",
]

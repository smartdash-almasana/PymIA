"""Immutable tenant-scoped projection of Servicio 1 owner confirmation evidence."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    SCHEMA_VERSION as OWNER_CONFIRMATION_SCHEMA_VERSION,
    Service1OwnerConfirmationEventV1,
)

SCHEMA_VERSION = "SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1"
STATUS_READY = "TENANT_SEMANTIC_CONTRACT_READY"
VALIDITY_STATUS = "OWNER_CONFIRMED_EVIDENCE"

_SAFETY_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "automatic_reuse_authorized",
    "semantic_rebind_authorized",
)
_FORBIDDEN_PROVENANCE_KEYS = frozenset(
    {
        *_SAFETY_FLAGS,
        "raw_rows",
        "raw_values",
        "workbook_bytes",
        "credentials",
        "token",
        "tokens",
    }
)
_PROVENANCE = {
    "owner_confirmation_schema": OWNER_CONFIRMATION_SCHEMA_VERSION,
    "projection": "OWNER_CONFIRMATION_EVIDENCE_ONLY",
}


class Service1TenantSemanticContractErrorV1(ValueError):
    """Fail-closed error carrying one governed contract state."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _blocked(code: str, detail: str) -> Service1TenantSemanticContractErrorV1:
    return Service1TenantSemanticContractErrorV1(code, detail)


def _required(value: object, *, field: str, code: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise _blocked(code, f"{field} is required")
    return text


def _optional(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _canonical_hash(prefix: str, payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(encoded).hexdigest()}"


def _event_from_mapping(payload: Mapping[str, object]) -> Service1OwnerConfirmationEventV1:
    try:
        return Service1OwnerConfirmationEventV1(
            case_id=str(payload.get("case_id") or "").strip(),
            file_ref=_optional(payload.get("file_ref")),
            region_ref=_optional(payload.get("region_ref")),
            sheet_ref=str(payload.get("sheet_ref") or "").strip(),
            column_ref=str(payload.get("column_ref") or "").strip(),
            question_ref=str(payload.get("question_ref") or "").strip(),
            proposed_role=_optional(payload.get("proposed_role")),
            proposed_variable=_optional(payload.get("proposed_variable")),
            owner_answer=str(payload.get("owner_answer") or "").strip(),
            confirmed_role=_optional(payload.get("confirmed_role")),
            corrected_meaning=_optional(payload.get("corrected_meaning")),
            confirmation_scope=str(payload.get("confirmation_scope") or "").strip(),
            confirmed_by_owner=payload.get("confirmed_by_owner") is True,
            timestamp=str(payload.get("timestamp") or "").strip(),
            provenance=dict(payload.get("provenance") or {}),
            schema_version=str(payload.get("schema_version") or ""),
        )
    except (TypeError, ValueError) as exc:
        raise _blocked(
            "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
            str(exc),
        ) from exc


def _coerce_event(
    event: Service1OwnerConfirmationEventV1 | Mapping[str, object],
) -> Service1OwnerConfirmationEventV1:
    if isinstance(event, Service1OwnerConfirmationEventV1):
        return event
    if isinstance(event, Mapping):
        return _event_from_mapping(event)
    raise _blocked(
        "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
        "owner_confirmation_event must use the canonical V1 schema",
    )


@dataclass(frozen=True)
class Service1TenantSemanticContractV1:
    schema_version: str
    contract_id: str
    mapping_series_id: str
    tenant_id: str
    case_id: str
    cliente_id: str | None
    source_system_ref: str
    source_context_ref: str
    workbook_ref: str
    sheet_ref: str
    source_column_name: str
    normalized_column_ref: str
    inferred_data_type: str | None
    neighboring_column_refs: tuple[str, ...]
    vertical_ref: str | None
    service_ref: str
    confirmation_scope: str
    confirmed_role: str | None
    confirmed_variable: str | None
    corrected_meaning: str | None
    column_excluded: bool
    confirmation_event_ref: str
    question_ref: str
    owner_actor_id: str
    owner_actor_role: str
    confirmed_at: str
    revision: int
    supersedes_contract_id: str | None
    validity_status: str
    provenance: Mapping[str, str]
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    automatic_reuse_authorized: bool = False
    semantic_rebind_authorized: bool = False
    status: str = STATUS_READY

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise _blocked("BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT", "invalid contract schema")
        if self.status != STATUS_READY:
            raise _blocked("BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT", "invalid contract status")
        if self.validity_status != VALIDITY_STATUS:
            raise _blocked("BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT", "invalid validity status")
        if self.confirmation_scope not in {
            "SEMANTIC_ROLE",
            "COLUMN_EXCLUSION",
            "FREE_TEXT_MEANING",
        }:
            raise _blocked("BLOCKED_EVENT_CONTEXT_MISMATCH", "invalid confirmation scope")
        if any(getattr(self, flag) is not False for flag in _SAFETY_FLAGS):
            raise _blocked(
                "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
                "authority and reuse flags must remain false",
            )
        if _FORBIDDEN_PROVENANCE_KEYS.intersection(self.provenance):
            raise _blocked(
                "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
                "provenance contains forbidden data or authority fields",
            )
        if dict(self.provenance) != _PROVENANCE:
            raise _blocked(
                "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
                "provenance must use the closed safe projection",
            )
        if self.revision < 1:
            raise _blocked("BLOCKED_REVISION_INVALID", "revision must be at least 1")
        if self.revision == 1 and self.supersedes_contract_id is not None:
            raise _blocked("BLOCKED_REVISION_INVALID", "revision 1 cannot supersede a contract")
        if self.revision > 1 and not self.supersedes_contract_id:
            raise _blocked("BLOCKED_REVISION_INVALID", "revision greater than 1 requires a prior contract")
        if self.confirmation_scope == "SEMANTIC_ROLE" and not self.confirmed_role:
            raise _blocked("BLOCKED_EVENT_CONTEXT_MISMATCH", "semantic role is missing")
        if self.confirmation_scope == "COLUMN_EXCLUSION":
            if (
                not self.column_excluded
                or self.confirmed_role is not None
                or self.confirmed_variable is not None
            ):
                raise _blocked("BLOCKED_EVENT_CONTEXT_MISMATCH", "invalid column exclusion")
        elif self.column_excluded:
            raise _blocked("BLOCKED_EVENT_CONTEXT_MISMATCH", "only exclusion may exclude a column")
        if self.confirmation_scope == "FREE_TEXT_MEANING":
            if (
                not self.corrected_meaning
                or self.confirmed_role is not None
                or self.confirmed_variable is not None
            ):
                raise _blocked("BLOCKED_EVENT_CONTEXT_MISMATCH", "invalid free-text meaning")

        expected_series = _mapping_series_id(
            tenant_id=self.tenant_id,
            source_system_ref=self.source_system_ref,
            source_context_ref=self.source_context_ref,
            sheet_ref=self.sheet_ref,
            source_column_name=self.source_column_name,
        )
        if self.mapping_series_id != expected_series:
            raise _blocked(
                "BLOCKED_EVENT_CONTEXT_MISMATCH",
                "mapping_series_id does not match safe source context",
            )
        expected_contract_id = _contract_id(
            mapping_series_id=self.mapping_series_id,
            revision=self.revision,
            confirmation_event_ref=self.confirmation_event_ref,
            supersedes_contract_id=self.supersedes_contract_id,
        )
        if self.contract_id != expected_contract_id:
            raise _blocked(
                "BLOCKED_EVENT_CONTEXT_MISMATCH",
                "contract_id does not match contract lineage",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "mapping_series_id": self.mapping_series_id,
            "tenant_id": self.tenant_id,
            "case_id": self.case_id,
            "cliente_id": self.cliente_id,
            "source_system_ref": self.source_system_ref,
            "source_context_ref": self.source_context_ref,
            "workbook_ref": self.workbook_ref,
            "sheet_ref": self.sheet_ref,
            "source_column_name": self.source_column_name,
            "normalized_column_ref": self.normalized_column_ref,
            "inferred_data_type": self.inferred_data_type,
            "neighboring_column_refs": list(self.neighboring_column_refs),
            "vertical_ref": self.vertical_ref,
            "service_ref": self.service_ref,
            "confirmation_scope": self.confirmation_scope,
            "confirmed_role": self.confirmed_role,
            "confirmed_variable": self.confirmed_variable,
            "corrected_meaning": self.corrected_meaning,
            "column_excluded": self.column_excluded,
            "confirmation_event_ref": self.confirmation_event_ref,
            "question_ref": self.question_ref,
            "owner_actor_id": self.owner_actor_id,
            "owner_actor_role": self.owner_actor_role,
            "confirmed_at": self.confirmed_at,
            "revision": self.revision,
            "supersedes_contract_id": self.supersedes_contract_id,
            "validity_status": self.validity_status,
            "provenance": dict(self.provenance),
            **{flag: False for flag in _SAFETY_FLAGS},
            "status": self.status,
        }


def _mapping_series_id(
    *,
    tenant_id: str,
    source_system_ref: str,
    source_context_ref: str,
    sheet_ref: str,
    source_column_name: str,
) -> str:
    return _canonical_hash(
        "tsm",
        {
            "tenant_id": tenant_id,
            "source_system_ref": source_system_ref,
            "source_context_ref": source_context_ref,
            "sheet_ref": sheet_ref,
            "source_column_name": source_column_name,
        },
    )


def _contract_id(
    *,
    mapping_series_id: str,
    revision: int,
    confirmation_event_ref: str,
    supersedes_contract_id: str | None,
) -> str:
    return _canonical_hash(
        "tsc",
        {
            "mapping_series_id": mapping_series_id,
            "revision": revision,
            "confirmation_event_ref": confirmation_event_ref,
            "supersedes_contract_id": supersedes_contract_id,
        },
    )


def service_1_tenant_semantic_contract_from_mapping_v1(
    payload: Mapping[str, object],
) -> Service1TenantSemanticContractV1:
    if not isinstance(payload, Mapping):
        raise _blocked("BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT", "contract must be a mapping")
    required_serialized_fields = {
        "schema_version",
        "contract_id",
        "mapping_series_id",
        "tenant_id",
        "case_id",
        "cliente_id",
        "source_system_ref",
        "source_context_ref",
        "workbook_ref",
        "sheet_ref",
        "source_column_name",
        "normalized_column_ref",
        "inferred_data_type",
        "neighboring_column_refs",
        "vertical_ref",
        "service_ref",
        "confirmation_scope",
        "confirmed_role",
        "confirmed_variable",
        "corrected_meaning",
        "column_excluded",
        "confirmation_event_ref",
        "question_ref",
        "owner_actor_id",
        "owner_actor_role",
        "confirmed_at",
        "revision",
        "supersedes_contract_id",
        "validity_status",
        "provenance",
        *_SAFETY_FLAGS,
        "status",
    }
    missing = sorted(required_serialized_fields.difference(payload))
    if missing:
        raise _blocked(
            "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
            f"contract payload is missing fields: {', '.join(missing)}",
        )
    try:
        revision = int(payload.get("revision", 0))
    except (TypeError, ValueError) as exc:
        raise _blocked("BLOCKED_REVISION_INVALID", "revision must be an integer") from exc
    neighbors = payload.get("neighboring_column_refs", ())
    if not isinstance(neighbors, (list, tuple)):
        raise _blocked("BLOCKED_MISSING_SOURCE_CONTEXT", "neighboring_column_refs must be a sequence")
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise _blocked("BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT", "provenance must be a mapping")

    return Service1TenantSemanticContractV1(
        schema_version=str(payload.get("schema_version") or ""),
        contract_id=str(payload.get("contract_id") or ""),
        mapping_series_id=str(payload.get("mapping_series_id") or ""),
        tenant_id=_required(payload.get("tenant_id"), field="tenant_id", code="BLOCKED_MISSING_TENANT_ID"),
        case_id=_required(payload.get("case_id"), field="case_id", code="BLOCKED_EVENT_CONTEXT_MISMATCH"),
        cliente_id=_optional(payload.get("cliente_id")),
        source_system_ref=_required(payload.get("source_system_ref"), field="source_system_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        source_context_ref=_required(payload.get("source_context_ref"), field="source_context_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        workbook_ref=_required(payload.get("workbook_ref"), field="workbook_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        sheet_ref=_required(payload.get("sheet_ref"), field="sheet_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        source_column_name=_required(payload.get("source_column_name"), field="source_column_name", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        normalized_column_ref=_required(payload.get("normalized_column_ref"), field="normalized_column_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        inferred_data_type=_optional(payload.get("inferred_data_type")),
        neighboring_column_refs=tuple(
            _required(value, field="neighboring_column_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
            for value in neighbors
        ),
        vertical_ref=_optional(payload.get("vertical_ref")),
        service_ref=_required(payload.get("service_ref"), field="service_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT"),
        confirmation_scope=str(payload.get("confirmation_scope") or ""),
        confirmed_role=_optional(payload.get("confirmed_role")),
        confirmed_variable=_optional(payload.get("confirmed_variable")),
        corrected_meaning=_optional(payload.get("corrected_meaning")),
        column_excluded=payload.get("column_excluded") is True,
        confirmation_event_ref=_required(payload.get("confirmation_event_ref"), field="confirmation_event_ref", code="BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT"),
        question_ref=_required(payload.get("question_ref"), field="question_ref", code="BLOCKED_EVENT_CONTEXT_MISMATCH"),
        owner_actor_id=_required(payload.get("owner_actor_id"), field="owner_actor_id", code="BLOCKED_MISSING_ACTOR_IDENTITY"),
        owner_actor_role=_required(payload.get("owner_actor_role"), field="owner_actor_role", code="BLOCKED_MISSING_ACTOR_IDENTITY"),
        confirmed_at=_required(payload.get("confirmed_at"), field="confirmed_at", code="BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT"),
        revision=revision,
        supersedes_contract_id=_optional(payload.get("supersedes_contract_id")),
        validity_status=str(payload.get("validity_status") or ""),
        provenance=MappingProxyType({str(key): str(value) for key, value in provenance.items()}),
        runtime_authorized=payload.get("runtime_authorized") is True,
        tool_execution_authorized=payload.get("tool_execution_authorized") is True,
        product_ready=payload.get("product_ready") is True,
        delivery_authorized=payload.get("delivery_authorized") is True,
        diagnosis_generated=payload.get("diagnosis_generated") is True,
        automatic_reuse_authorized=payload.get("automatic_reuse_authorized") is True,
        semantic_rebind_authorized=payload.get("semantic_rebind_authorized") is True,
        status=str(payload.get("status") or ""),
    )


def build_service_1_tenant_semantic_contract_v1(
    *,
    tenant_id: str,
    cliente_id: str | None,
    owner_actor_id: str,
    owner_actor_role: str,
    source_system_ref: str,
    source_context_ref: str,
    workbook_ref: str,
    source_column_name: str,
    normalized_column_ref: str,
    owner_confirmation_event: Service1OwnerConfirmationEventV1 | Mapping[str, object],
    revision: int = 1,
    supersedes_contract: Service1TenantSemanticContractV1 | Mapping[str, object] | None = None,
    inferred_data_type: str | None = None,
    neighboring_column_refs: Sequence[str] = (),
    vertical_ref: str | None = None,
    service_ref: str = "SERVICE_1",
) -> Service1TenantSemanticContractV1:
    tenant = _required(tenant_id, field="tenant_id", code="BLOCKED_MISSING_TENANT_ID")
    actor_id = _required(owner_actor_id, field="owner_actor_id", code="BLOCKED_MISSING_ACTOR_IDENTITY")
    actor_role = _required(owner_actor_role, field="owner_actor_role", code="BLOCKED_MISSING_ACTOR_IDENTITY")
    system_ref = _required(source_system_ref, field="source_system_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
    context_ref = _required(source_context_ref, field="source_context_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
    workbook = _required(workbook_ref, field="workbook_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
    source_column = _required(source_column_name, field="source_column_name", code="BLOCKED_MISSING_SOURCE_CONTEXT")
    normalized_column = _required(normalized_column_ref, field="normalized_column_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
    service = _required(service_ref, field="service_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
    event = _coerce_event(owner_confirmation_event)

    if event.schema_version != OWNER_CONFIRMATION_SCHEMA_VERSION or event.confirmed_by_owner is not True:
        raise _blocked("BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT", "canonical owner confirmation is required")
    if event.file_ref != workbook or event.column_ref != normalized_column:
        raise _blocked(
            "BLOCKED_EVENT_CONTEXT_MISMATCH",
            "event workbook or column does not match projection context",
        )

    sheet_ref = _required(event.sheet_ref, field="sheet_ref", code="BLOCKED_EVENT_CONTEXT_MISMATCH")
    mapping_series_id = _mapping_series_id(
        tenant_id=tenant,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
        sheet_ref=sheet_ref,
        source_column_name=source_column,
    )

    prior: Service1TenantSemanticContractV1 | None = None
    if supersedes_contract is not None:
        prior = (
            supersedes_contract
            if isinstance(supersedes_contract, Service1TenantSemanticContractV1)
            else service_1_tenant_semantic_contract_from_mapping_v1(supersedes_contract)
        )
    if revision < 1 or (revision == 1 and prior is not None) or (revision > 1 and prior is None):
        raise _blocked("BLOCKED_REVISION_INVALID", "revision and prior contract are inconsistent")
    if prior is not None:
        if (
            revision != prior.revision + 1
            or tenant != prior.tenant_id
            or mapping_series_id != prior.mapping_series_id
        ):
            raise _blocked(
                "BLOCKED_SUPERSESSION_MISMATCH",
                "supersession must preserve tenant and mapping series and increment one revision",
            )

    event_payload = event.to_dict()
    confirmation_event_ref = _canonical_hash("oce", event_payload)
    supersedes_contract_id = prior.contract_id if prior is not None else None
    contract_id = _contract_id(
        mapping_series_id=mapping_series_id,
        revision=revision,
        confirmation_event_ref=confirmation_event_ref,
        supersedes_contract_id=supersedes_contract_id,
    )
    scope = event.confirmation_scope
    column_excluded = scope == "COLUMN_EXCLUSION"

    return Service1TenantSemanticContractV1(
        schema_version=SCHEMA_VERSION,
        contract_id=contract_id,
        mapping_series_id=mapping_series_id,
        tenant_id=tenant,
        case_id=event.case_id,
        cliente_id=_optional(cliente_id),
        source_system_ref=system_ref,
        source_context_ref=context_ref,
        workbook_ref=workbook,
        sheet_ref=sheet_ref,
        source_column_name=source_column,
        normalized_column_ref=normalized_column,
        inferred_data_type=_optional(inferred_data_type),
        neighboring_column_refs=tuple(
            _required(value, field="neighboring_column_ref", code="BLOCKED_MISSING_SOURCE_CONTEXT")
            for value in neighboring_column_refs
        ),
        vertical_ref=_optional(vertical_ref),
        service_ref=service,
        confirmation_scope=scope,
        confirmed_role=event.confirmed_role,
        confirmed_variable=event.proposed_variable if scope == "SEMANTIC_ROLE" else None,
        corrected_meaning=event.corrected_meaning,
        column_excluded=column_excluded,
        confirmation_event_ref=confirmation_event_ref,
        question_ref=event.question_ref,
        owner_actor_id=actor_id,
        owner_actor_role=actor_role,
        confirmed_at=event.timestamp,
        revision=revision,
        supersedes_contract_id=supersedes_contract_id,
        validity_status=VALIDITY_STATUS,
        provenance=MappingProxyType(dict(_PROVENANCE)),
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "Service1TenantSemanticContractErrorV1",
    "Service1TenantSemanticContractV1",
    "build_service_1_tenant_semantic_contract_v1",
    "service_1_tenant_semantic_contract_from_mapping_v1",
]

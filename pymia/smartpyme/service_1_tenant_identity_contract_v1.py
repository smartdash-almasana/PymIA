"""Immutable tenant-scoped identity envelope for one Servicio 1 first-contact case."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

SCHEMA_VERSION = "SERVICE_1_TENANT_IDENTITY_CONTRACT_V1"
STATUS_READY = "TENANT_IDENTITY_CONTRACT_READY"

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
        "session_id",
        "case_id",
    }
)
_PROVENANCE = {
    "establishment": "EXPLICIT_FIRST_CONTACT",
    "identity_kind": "TECHNICAL_TENANT_SCOPE",
}

# Deterministic identity payload: safe canonical fields only. Explicitly
# excluded: session_id, raw workbook bytes, raw rows, credentials, tokens,
# and unrestricted conversation text. The payload intentionally excludes
# provenance and status (they carry no identity meaning).
_IDENTITY_PAYLOAD_FIELDS = (
    "tenant_id",
    "case_id",
    "cliente_id",
    "owner_actor_id",
    "owner_actor_role",
    "source_system_ref",
    "source_context_ref",
    "workbook_ref",
)


class Service1TenantIdentityContractErrorV1(ValueError):
    """Fail-closed error carrying one governed identity contract state."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _blocked(code: str, detail: str) -> Service1TenantIdentityContractErrorV1:
    return Service1TenantIdentityContractErrorV1(code, detail)


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


def _validate_tenant_id(tenant_id: str) -> str:
    if not tenant_id.strip():
        raise _blocked("BLOCKED_MISSING_TENANT_ID", "tenant_id is required")
    if ".." in tenant_id or "/" in tenant_id or "\\" in tenant_id:
        raise _blocked(
            "BLOCKED_INVALID_TENANT_IDENTITY",
            "tenant_id contains invalid path traversal markers",
        )
    return tenant_id


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"tiic_{hashlib.sha256(encoded).hexdigest()}"


def _identity_contract_id(identity_payload: Mapping[str, object]) -> str:
    canonical: dict[str, object] = {}
    for field in _IDENTITY_PAYLOAD_FIELDS:
        value = identity_payload.get(field)
        if value is not None:
            canonical[field] = value
    return _canonical_hash(canonical)


def _identity_payload(
    *,
    tenant_id: str,
    case_id: str,
    cliente_id: str | None,
    owner_actor_id: str,
    owner_actor_role: str,
    source_system_ref: str,
    source_context_ref: str,
    workbook_ref: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "tenant_id": tenant_id,
        "case_id": case_id,
        "owner_actor_id": owner_actor_id,
        "owner_actor_role": owner_actor_role,
        "source_system_ref": source_system_ref,
        "source_context_ref": source_context_ref,
        "workbook_ref": workbook_ref,
    }
    if cliente_id is not None:
        payload["cliente_id"] = cliente_id
    return payload


@dataclass(frozen=True)
class Service1TenantIdentityContractV1:
    schema_version: str
    identity_contract_id: str
    tenant_id: str
    cliente_id: str | None
    case_id: str
    owner_actor_id: str
    owner_actor_role: str
    source_system_ref: str
    source_context_ref: str
    workbook_ref: str
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
        # int() safety is not applicable here; use strict attrs.
        if self.schema_version != SCHEMA_VERSION:
            raise _blocked("BLOCKED_IDENTITY_CONTEXT_MISMATCH", "invalid identity contract schema")
        if self.status != STATUS_READY:
            raise _blocked("BLOCKED_IDENTITY_CONTEXT_MISMATCH", "invalid identity contract status")
        if any(getattr(self, flag) is not False for flag in _SAFETY_FLAGS):
            raise _blocked(
                "BLOCKED_IDENTITY_CONTEXT_MISMATCH",
                "authority and reuse flags must remain false",
            )
        if _FORBIDDEN_PROVENANCE_KEYS.intersection(self.provenance):
            raise _blocked(
                "BLOCKED_IDENTITY_CONTEXT_MISMATCH",
                "provenance contains forbidden data or authority fields",
            )
        if dict(self.provenance) != _PROVENANCE:
            raise _blocked(
                "BLOCKED_IDENTITY_CONTEXT_MISMATCH",
                "provenance must use the closed safe projection",
            )
        # The identity contract never sources tenant identity from case identity.
        if self.tenant_id == self.case_id:
            raise _blocked(
                "BLOCKED_INVALID_TENANT_IDENTITY",
                "tenant_id must not be sourced from case identity",
            )
        expected_id = _identity_contract_id(
            _identity_payload(
                tenant_id=self.tenant_id,
                case_id=self.case_id,
                cliente_id=self.cliente_id,
                owner_actor_id=self.owner_actor_id,
                owner_actor_role=self.owner_actor_role,
                source_system_ref=self.source_system_ref,
                source_context_ref=self.source_context_ref,
                workbook_ref=self.workbook_ref,
            )
        )
        if self.identity_contract_id != expected_id:
            raise _blocked(
                "BLOCKED_IDENTITY_CONTEXT_MISMATCH",
                "identity_contract_id does not match safe canonical fields",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "identity_contract_id": self.identity_contract_id,
            "tenant_id": self.tenant_id,
            "case_id": self.case_id,
            "cliente_id": self.cliente_id,
            "owner_actor_id": self.owner_actor_id,
            "owner_actor_role": self.owner_actor_role,
            "source_system_ref": self.source_system_ref,
            "source_context_ref": self.source_context_ref,
            "workbook_ref": self.workbook_ref,
            "provenance": dict(self.provenance),
            **{flag: False for flag in _SAFETY_FLAGS},
            "status": self.status,
        }


_SERIALIZED_FIELDS = frozenset(
    {
        "schema_version",
        "identity_contract_id",
        "tenant_id",
        "cliente_id",
        "case_id",
        "owner_actor_id",
        "owner_actor_role",
        "source_system_ref",
        "source_context_ref",
        "workbook_ref",
        "provenance",
        *_SAFETY_FLAGS,
        "status",
    }
)


def service_1_tenant_identity_contract_from_mapping_v1(
    payload: Mapping[str, object],
) -> Service1TenantIdentityContractV1:
    if not isinstance(payload, Mapping):
        raise _blocked("BLOCKED_IDENTITY_CONTEXT_MISMATCH", "identity contract must be a mapping")
    missing = sorted(_SERIALIZED_FIELDS.difference(payload))
    if missing:
        raise _blocked(
            "BLOCKED_IDENTITY_CONTEXT_MISMATCH",
            f"identity contract payload is missing fields: {', '.join(missing)}",
        )
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise _blocked("BLOCKED_IDENTITY_CONTEXT_MISMATCH", "provenance must be a mapping")

    tenant_id = _validate_tenant_id(
        _required(payload.get("tenant_id"), field="tenant_id", code="BLOCKED_MISSING_TENANT_ID")
    )
    return Service1TenantIdentityContractV1(
        schema_version=str(payload.get("schema_version") or ""),
        identity_contract_id=str(payload.get("identity_contract_id") or ""),
        tenant_id=tenant_id,
        case_id=_required(
            payload.get("case_id"),
            field="case_id",
            code="BLOCKED_MISSING_CASE_ID",
        ),
        cliente_id=_optional(payload.get("cliente_id")),
        owner_actor_id=_required(
            payload.get("owner_actor_id"),
            field="owner_actor_id",
            code="BLOCKED_MISSING_OWNER_IDENTITY",
        ),
        owner_actor_role=_required(
            payload.get("owner_actor_role"),
            field="owner_actor_role",
            code="BLOCKED_MISSING_OWNER_IDENTITY",
        ),
        source_system_ref=_required(
            payload.get("source_system_ref"),
            field="source_system_ref",
            code="BLOCKED_MISSING_SOURCE_IDENTITY",
        ),
        source_context_ref=_required(
            payload.get("source_context_ref"),
            field="source_context_ref",
            code="BLOCKED_MISSING_SOURCE_IDENTITY",
        ),
        workbook_ref=_required(
            payload.get("workbook_ref"),
            field="workbook_ref",
            code="BLOCKED_MISSING_SOURCE_IDENTITY",
        ),
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


def build_service_1_tenant_identity_contract_v1(
    *,
    tenant_id: str,
    case_id: str,
    owner_actor_id: str,
    owner_actor_role: str,
    source_system_ref: str,
    source_context_ref: str,
    workbook_ref: str,
    cliente_id: str | None = None,
) -> Service1TenantIdentityContractV1:
    tenant = _validate_tenant_id(
        _required(tenant_id, field="tenant_id", code="BLOCKED_MISSING_TENANT_ID")
    )
    case_ref = _required(case_id, field="case_id", code="BLOCKED_MISSING_CASE_ID")
    actor_id = _required(owner_actor_id, field="owner_actor_id", code="BLOCKED_MISSING_OWNER_IDENTITY")
    actor_role = _required(owner_actor_role, field="owner_actor_role", code="BLOCKED_MISSING_OWNER_IDENTITY")
    system_ref = _required(
        source_system_ref,
        field="source_system_ref",
        code="BLOCKED_MISSING_SOURCE_IDENTITY",
    )
    context_ref = _required(
        source_context_ref,
        field="source_context_ref",
        code="BLOCKED_MISSING_SOURCE_IDENTITY",
    )
    workbook = _required(
        workbook_ref,
        field="workbook_ref",
        code="BLOCKED_MISSING_SOURCE_IDENTITY",
    )
    # The identity contract never derives tenant identity from case identity.
    if tenant == case_ref:
        raise _blocked(
            "BLOCKED_INVALID_TENANT_IDENTITY",
            "tenant_id must not be sourced from case identity",
        )
    # cliente_id is optional and is never inferred from tenant_id.
    client = _optional(cliente_id)

    payload = _identity_payload(
        tenant_id=tenant,
        case_id=case_ref,
        cliente_id=client,
        owner_actor_id=actor_id,
        owner_actor_role=actor_role,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
        workbook_ref=workbook,
    )
    return Service1TenantIdentityContractV1(
        schema_version=SCHEMA_VERSION,
        identity_contract_id=_identity_contract_id(payload),
        tenant_id=tenant,
        case_id=case_ref,
        cliente_id=client,
        owner_actor_id=actor_id,
        owner_actor_role=actor_role,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
        workbook_ref=workbook,
        provenance=MappingProxyType(dict(_PROVENANCE)),
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "Service1TenantIdentityContractErrorV1",
    "Service1TenantIdentityContractV1",
    "build_service_1_tenant_identity_contract_v1",
    "service_1_tenant_identity_contract_from_mapping_v1",
]
"""D6 tenant schema-family memory and delta-only revalidation for Servicio 1.

This module extends the existing tenant semantic memory conceptually; persistence
is owned by ``service_1_tenant_schema_family_memory_store_v1`` in the SAME
append-only tenant artifact shared with semantic contracts.  It grants no
semantic reuse, runtime, join or computability authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)
from pymia.smartpyme.service_1_workbook_schema_identity_v1 import (
    COMPATIBILITY_KNOWN,
    COMPATIBILITY_KNOWN_DELTA,
    COMPATIBILITY_MATERIAL,
    DRIFT_COMPATIBLE_DELTA,
    DRIFT_IDENTICAL,
    DRIFT_MATERIAL,
    DRIFT_UNRESOLVED,
    STATUS_READY as SCHEMA_READY,
    TABLE_MATCH_READY,
    UNKNOWN_FAMILY,
    WorkbookSchemaIdentityV1,
    build_service_1_workbook_schema_delta_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_TENANT_SCHEMA_FAMILY_MEMORY_V1"
RECORD_KIND: Final[str] = "TENANT_SCHEMA_FAMILY_MEMORY"
STATUS_READY: Final[str] = "TENANT_SCHEMA_FAMILY_MEMORY_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

REVALIDATION_KNOWN_IDENTICAL: Final[str] = "KNOWN_NO_MATERIAL_DELTA"
REVALIDATION_KNOWN_COMPATIBLE_DELTA: Final[str] = "KNOWN_COMPATIBLE_DELTA"
REVALIDATION_KNOWN_MATERIAL_DELTA: Final[str] = "KNOWN_MATERIAL_DELTA"
REVALIDATION_UNKNOWN_FAMILY: Final[str] = "UNKNOWN_FAMILY"
REVALIDATION_UNRESOLVED: Final[str] = "UNRESOLVED"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "automatic_reuse_authorized",
    "semantic_rebind_authorized",
    "runtime_authorized",
    "tool_execution_authorized",
    "join_execution_authorized",
    "computability_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)
_FORBIDDEN_PROVENANCE_KEYS: Final[frozenset[str]] = frozenset(
    {*_AUTHORITY_FLAGS, "raw_rows", "raw_values", "workbook_bytes", "credentials", "token", "tokens"}
)


class Service1TenantSchemaFamilyMemoryErrorV1(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _error(code: str, detail: str) -> Service1TenantSchemaFamilyMemoryErrorV1:
    return Service1TenantSchemaFamilyMemoryErrorV1(code, detail)


def _required(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", f"{field_name} is required")
    return text


def _identity_mapping(value: Mapping[str, Any] | WorkbookSchemaIdentityV1) -> dict[str, Any]:
    if isinstance(value, WorkbookSchemaIdentityV1):
        payload = value.to_dict()
        payload["status"] = SCHEMA_READY
        return payload
    if not isinstance(value, Mapping):
        raise _error("BLOCKED_SCHEMA_IDENTITY_INVALID", "schema identity must be a mapping or WorkbookSchemaIdentityV1")
    payload = dict(value)
    if payload.get("status") != SCHEMA_READY or not str(payload.get("schema_fingerprint") or "").strip():
        raise _error("BLOCKED_SCHEMA_IDENTITY_INVALID", "ready D3 schema identity is required")
    if any(bool(payload.get(flag)) for flag in _AUTHORITY_FLAGS):
        raise _error("BLOCKED_SCHEMA_MEMORY_AUTHORITY_FORBIDDEN", "schema identity carries authority")
    return payload


def _clean_mapping_refs(value: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    for raw in value:
        if not isinstance(raw, Mapping):
            raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "semantic mapping refs must be mappings")
        if any(bool(raw.get(flag)) for flag in _AUTHORITY_FLAGS):
            raise _error("BLOCKED_SCHEMA_MEMORY_AUTHORITY_FORBIDDEN", "semantic mapping ref carries authority")
        contract_id = _required(raw.get("contract_id"), "semantic_mapping_ref.contract_id")
        item = {
            "contract_id": contract_id,
            "mapping_series_id": str(raw.get("mapping_series_id") or "").strip() or None,
            "sheet_ref": str(raw.get("sheet_ref") or "").strip() or None,
            "source_column_name": str(raw.get("source_column_name") or "").strip() or None,
            "normalized_column_ref": str(raw.get("normalized_column_ref") or "").strip() or None,
            "logical_table_ref": str(raw.get("logical_table_ref") or "").strip() or None,
            "confirmed_role": str(raw.get("confirmed_role") or "").strip() or None,
            "confirmed_variable": str(raw.get("confirmed_variable") or "").strip() or None,
            "column_excluded": raw.get("column_excluded") is True,
            "historical_evidence_only": True,
            "automatic_reuse_authorized": False,
            "semantic_rebind_authorized": False,
        }
        result.append(item)
    result.sort(key=lambda item: (str(item.get("logical_table_ref") or ""), str(item.get("normalized_column_ref") or ""), item["contract_id"]))
    return tuple(result)


def _clean_relationship_refs(value: Sequence[Any]) -> tuple[str, ...]:
    result: list[str] = []
    for raw in value:
        if isinstance(raw, Mapping):
            ref = str(raw.get("relationship_ref") or "").strip()
        else:
            ref = str(raw or "").strip()
        if ref and ref not in result:
            result.append(ref)
    return tuple(sorted(result))


@dataclass(frozen=True)
class Service1TenantSchemaFamilyMemoryV1:
    record_kind: str
    schema_version: str
    record_id: str
    tenant_id: str
    source_system_ref: str
    source_context_ref: str
    schema_family_ref: str
    family_revision: int
    schema_version_logical: str
    schema_fingerprint: str
    schema_identity: Mapping[str, Any]
    logical_table_signatures: tuple[dict[str, Any], ...]
    semantic_mapping_refs: tuple[dict[str, Any], ...] = ()
    relationship_evidence_refs: tuple[str, ...] = ()
    prior_record_id: str | None = None
    prior_schema_fingerprint: str | None = None
    delta_affected_scope: tuple[str, ...] = ()
    delta_drift_state: str = DRIFT_IDENTICAL
    provenance: Mapping[str, Any] = field(default_factory=dict)
    automatic_reuse_authorized: bool = False
    semantic_rebind_authorized: bool = False
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    join_execution_authorized: bool = False
    computability_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    status: str = STATUS_READY

    def __post_init__(self) -> None:
        if self.record_kind != RECORD_KIND or self.schema_version != SCHEMA_VERSION or self.status != STATUS_READY:
            raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "invalid schema-family memory envelope")
        for name in ("record_id", "tenant_id", "source_system_ref", "source_context_ref", "schema_family_ref", "schema_version_logical", "schema_fingerprint"):
            if not str(getattr(self, name) or "").strip():
                raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", f"{name} is required")
        if self.schema_family_ref == UNKNOWN_FAMILY:
            raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "persisted family ref cannot be UNKNOWN")
        if self.family_revision < 1:
            raise _error("BLOCKED_SCHEMA_MEMORY_REVISION_INVALID", "family_revision must be >= 1")
        if self.family_revision == 1 and self.prior_record_id is not None:
            raise _error("BLOCKED_SCHEMA_MEMORY_REVISION_INVALID", "revision 1 cannot supersede a prior record")
        if self.family_revision > 1 and not self.prior_record_id:
            raise _error("BLOCKED_SCHEMA_MEMORY_REVISION_INVALID", "revision >1 requires prior_record_id")
        if any(getattr(self, flag) is not False for flag in _AUTHORITY_FLAGS):
            raise _error("BLOCKED_SCHEMA_MEMORY_AUTHORITY_FORBIDDEN", "all authority flags must remain false")
        provenance = dict(self.provenance or {})
        if _FORBIDDEN_PROVENANCE_KEYS.intersection(provenance):
            raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "provenance contains forbidden fields")
        identity = _identity_mapping(self.schema_identity)
        if str(identity.get("schema_fingerprint")) != self.schema_fingerprint:
            raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "schema identity fingerprint mismatch")
        object.__setattr__(self, "schema_identity", dict(identity))
        object.__setattr__(self, "logical_table_signatures", tuple(dict(item) for item in self.logical_table_signatures))
        object.__setattr__(self, "semantic_mapping_refs", _clean_mapping_refs(self.semantic_mapping_refs))
        object.__setattr__(self, "relationship_evidence_refs", _clean_relationship_refs(self.relationship_evidence_refs))
        object.__setattr__(self, "delta_affected_scope", tuple(dict.fromkeys(str(item) for item in self.delta_affected_scope if str(item).strip())))
        object.__setattr__(self, "provenance", provenance)

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def build_service_1_scoped_semantic_mapping_refs_v1(
    *,
    tenant_id: str,
    semantic_contracts: Sequence[Mapping[str, Any] | Any],
    semantic_scope_packet: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Project existing owner-confirmed tenant contracts into safe D6 references."""
    tenant = _required(tenant_id, "tenant_id")
    scopes = [dict(item) for item in (semantic_scope_packet or {}).get("column_scopes") or () if isinstance(item, Mapping)]
    by_identity: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for scope in scopes:
        key = (
            str(scope.get("sheet_ref") or "").strip(),
            _normalize_header(scope.get("normalized_header")),
        )
        if all(key):
            by_identity.setdefault(key, []).append(scope)

    refs: list[dict[str, Any]] = []
    for raw in semantic_contracts:
        payload = raw.to_dict() if hasattr(raw, "to_dict") else dict(raw) if isinstance(raw, Mapping) else None
        if not isinstance(payload, dict):
            raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "semantic contract must be serializable")
        if str(payload.get("tenant_id") or "").strip() != tenant:
            raise _error("BLOCKED_CROSS_TENANT_ACCESS", "semantic contract belongs to another tenant")
        if any(bool(payload.get(flag)) for flag in _AUTHORITY_FLAGS):
            raise _error("BLOCKED_SCHEMA_MEMORY_AUTHORITY_FORBIDDEN", "semantic contract carries authority")
        sheet = str(payload.get("sheet_ref") or "").strip()
        normalized = _normalize_header(payload.get("normalized_column_ref") or payload.get("source_column_name"))
        matches = by_identity.get((sheet, normalized), [])
        logical_table_ref = str(matches[0].get("logical_table_ref") or "").strip() if len(matches) == 1 else ""
        refs.append({
            "contract_id": payload.get("contract_id"),
            "mapping_series_id": payload.get("mapping_series_id"),
            "sheet_ref": sheet,
            "source_column_name": payload.get("source_column_name"),
            "normalized_column_ref": normalized,
            "logical_table_ref": logical_table_ref or None,
            "confirmed_role": payload.get("confirmed_role"),
            "confirmed_variable": payload.get("confirmed_variable"),
            "column_excluded": payload.get("column_excluded") is True,
        })
    return _clean_mapping_refs(refs)


def build_service_1_tenant_schema_family_memory_v1(
    *,
    tenant_id: str,
    source_system_ref: str,
    source_context_ref: str,
    schema_identity: Mapping[str, Any] | WorkbookSchemaIdentityV1,
    semantic_mapping_refs: Sequence[Mapping[str, Any]] = (),
    relationship_evidence_refs: Sequence[Any] = (),
    prior_record: Service1TenantSchemaFamilyMemoryV1 | Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> Service1TenantSchemaFamilyMemoryV1:
    tenant = _required(tenant_id, "tenant_id")
    system_ref = _required(source_system_ref, "source_system_ref")
    context_ref = _required(source_context_ref, "source_context_ref")
    identity = _identity_mapping(schema_identity)
    fingerprint = _required(identity.get("schema_fingerprint"), "schema_fingerprint")
    prior = None if prior_record is None else service_1_tenant_schema_family_memory_from_mapping_v1(
        prior_record.to_dict() if isinstance(prior_record, Service1TenantSchemaFamilyMemoryV1) else prior_record
    )

    if prior is not None:
        if (prior.tenant_id, prior.source_system_ref, prior.source_context_ref) != (tenant, system_ref, context_ref):
            raise _error("BLOCKED_CROSS_TENANT_ACCESS", "prior schema memory is outside the tenant/source context")
        explicit_family = str(identity.get("schema_family_ref") or UNKNOWN_FAMILY).strip() or UNKNOWN_FAMILY
        if explicit_family not in {UNKNOWN_FAMILY, prior.schema_family_ref}:
            raise _error("BLOCKED_SCHEMA_FAMILY_MISMATCH", "current schema identity names a different family")
        family_ref = prior.schema_family_ref
        family_revision = prior.family_revision + 1
        prior_record_id = prior.record_id
        prior_fingerprint = prior.schema_fingerprint
        prior_identity = dict(prior.schema_identity)
        prior_identity["schema_family_ref"] = family_ref
        current_identity = dict(identity)
        current_identity["schema_family_ref"] = family_ref
        delta = build_service_1_workbook_schema_delta_v1(
            prior_identity=prior_identity,
            current_identity=current_identity,
        )
        if delta.get("status") != SCHEMA_READY or delta.get("matching_status") != TABLE_MATCH_READY or delta.get("drift_state") == DRIFT_UNRESOLVED:
            raise _error("BLOCKED_SCHEMA_DELTA_UNRESOLVED", str(delta.get("blocked_reason") or delta.get("drift_state")))
        delta_scope = tuple(delta.get("affected_scope") or ())
        delta_state = str(delta.get("drift_state") or DRIFT_UNRESOLVED)
    else:
        explicit_family = str(identity.get("schema_family_ref") or UNKNOWN_FAMILY).strip() or UNKNOWN_FAMILY
        family_ref = explicit_family if explicit_family != UNKNOWN_FAMILY else build_service_1_structural_digest_v1(
            payload={
                "tenant_id": tenant,
                "source_system_ref": system_ref,
                "source_context_ref": context_ref,
                "initial_schema_fingerprint": fingerprint,
            },
            prefix="sfm_",
        )
        family_revision = 1
        prior_record_id = None
        prior_fingerprint = None
        delta_scope = ()
        delta_state = DRIFT_IDENTICAL

    identity = dict(identity)
    identity["schema_family_ref"] = family_ref
    semantic_refs = _clean_mapping_refs(semantic_mapping_refs)
    relationship_refs = _clean_relationship_refs(relationship_evidence_refs)
    record_payload = {
        "tenant_id": tenant,
        "source_system_ref": system_ref,
        "source_context_ref": context_ref,
        "schema_family_ref": family_ref,
        "family_revision": family_revision,
        "schema_fingerprint": fingerprint,
        "semantic_contract_ids": [item["contract_id"] for item in semantic_refs],
        "relationship_evidence_refs": list(relationship_refs),
        "prior_record_id": prior_record_id,
    }
    record_id = build_service_1_structural_digest_v1(payload=record_payload, prefix="tsfm_")
    return Service1TenantSchemaFamilyMemoryV1(
        record_kind=RECORD_KIND,
        schema_version=SCHEMA_VERSION,
        record_id=record_id,
        tenant_id=tenant,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
        schema_family_ref=family_ref,
        family_revision=family_revision,
        schema_version_logical=str(identity.get("schema_version") or identity.get("schema_version_logical") or "1"),
        schema_fingerprint=fingerprint,
        schema_identity=identity,
        logical_table_signatures=tuple(dict(item) for item in identity.get("logical_table_signatures") or ()),
        semantic_mapping_refs=semantic_refs,
        relationship_evidence_refs=relationship_refs,
        prior_record_id=prior_record_id,
        prior_schema_fingerprint=prior_fingerprint,
        delta_affected_scope=delta_scope,
        delta_drift_state=delta_state,
        provenance={
            "memory_scope": "TENANT_SCHEMA_FAMILY",
            "storage_contract": "EXISTING_TENANT_SEMANTIC_MEMORY_ARTIFACT",
            "delta_only_revalidation": True,
            **dict(provenance or {}),
        },
    )


def service_1_tenant_schema_family_memory_from_mapping_v1(
    payload: Mapping[str, Any],
) -> Service1TenantSchemaFamilyMemoryV1:
    if not isinstance(payload, Mapping):
        raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "schema-family memory must be a mapping")
    required = {
        "record_kind", "schema_version", "record_id", "tenant_id", "source_system_ref",
        "source_context_ref", "schema_family_ref", "family_revision", "schema_version_logical",
        "schema_fingerprint", "schema_identity", "logical_table_signatures", "semantic_mapping_refs",
        "relationship_evidence_refs", "prior_record_id", "prior_schema_fingerprint",
        "delta_affected_scope", "delta_drift_state", "provenance", "status", *_AUTHORITY_FLAGS,
    }
    missing = sorted(required.difference(payload))
    if missing:
        raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", f"missing fields: {', '.join(missing)}")
    try:
        revision = int(payload.get("family_revision"))
    except (TypeError, ValueError) as exc:
        raise _error("BLOCKED_SCHEMA_MEMORY_REVISION_INVALID", "family_revision must be integer") from exc
    identity = payload.get("schema_identity")
    provenance = payload.get("provenance")
    if not isinstance(identity, Mapping) or not isinstance(provenance, Mapping):
        raise _error("BLOCKED_SCHEMA_MEMORY_INVALID", "schema_identity and provenance must be mappings")
    return Service1TenantSchemaFamilyMemoryV1(
        record_kind=str(payload.get("record_kind") or ""),
        schema_version=str(payload.get("schema_version") or ""),
        record_id=str(payload.get("record_id") or ""),
        tenant_id=str(payload.get("tenant_id") or ""),
        source_system_ref=str(payload.get("source_system_ref") or ""),
        source_context_ref=str(payload.get("source_context_ref") or ""),
        schema_family_ref=str(payload.get("schema_family_ref") or ""),
        family_revision=revision,
        schema_version_logical=str(payload.get("schema_version_logical") or ""),
        schema_fingerprint=str(payload.get("schema_fingerprint") or ""),
        schema_identity=dict(identity),
        logical_table_signatures=tuple(dict(item) for item in payload.get("logical_table_signatures") or () if isinstance(item, Mapping)),
        semantic_mapping_refs=tuple(dict(item) for item in payload.get("semantic_mapping_refs") or () if isinstance(item, Mapping)),
        relationship_evidence_refs=tuple(str(item) for item in payload.get("relationship_evidence_refs") or ()),
        prior_record_id=str(payload.get("prior_record_id") or "").strip() or None,
        prior_schema_fingerprint=str(payload.get("prior_schema_fingerprint") or "").strip() or None,
        delta_affected_scope=tuple(str(item) for item in payload.get("delta_affected_scope") or ()),
        delta_drift_state=str(payload.get("delta_drift_state") or ""),
        provenance=dict(provenance),
        automatic_reuse_authorized=payload.get("automatic_reuse_authorized") is True,
        semantic_rebind_authorized=payload.get("semantic_rebind_authorized") is True,
        runtime_authorized=payload.get("runtime_authorized") is True,
        tool_execution_authorized=payload.get("tool_execution_authorized") is True,
        join_execution_authorized=payload.get("join_execution_authorized") is True,
        computability_authorized=payload.get("computability_authorized") is True,
        product_ready=payload.get("product_ready") is True,
        delivery_authorized=payload.get("delivery_authorized") is True,
        diagnosis_generated=payload.get("diagnosis_generated") is True,
        status=str(payload.get("status") or ""),
    )


def plan_service_1_schema_delta_revalidation_v1(
    *,
    tenant_id: str,
    source_system_ref: str,
    source_context_ref: str,
    current_schema_identity: Mapping[str, Any] | WorkbookSchemaIdentityV1,
    memory_records: Sequence[Service1TenantSchemaFamilyMemoryV1 | Mapping[str, Any]],
) -> dict[str, Any]:
    """Select compatible tenant family evidence and return ONLY the D3 affected scope.

    Memory remains historical evidence.  This function never auto-rebinds a
    semantic mapping and never authorizes computation/runtime.
    """
    tenant = _required(tenant_id, "tenant_id")
    system_ref = _required(source_system_ref, "source_system_ref")
    context_ref = _required(source_context_ref, "source_context_ref")
    current = _identity_mapping(current_schema_identity)
    records: list[Service1TenantSchemaFamilyMemoryV1] = []
    for raw in memory_records:
        record = raw if isinstance(raw, Service1TenantSchemaFamilyMemoryV1) else service_1_tenant_schema_family_memory_from_mapping_v1(raw)
        if (record.tenant_id, record.source_system_ref, record.source_context_ref) == (tenant, system_ref, context_ref):
            records.append(record)
    if not records:
        return _revalidation_result(
            state=REVALIDATION_UNKNOWN_FAMILY,
            family_ref=None,
            matched_record=None,
            delta=None,
            revalidation_scope=(),
            full_semantic_process_required=True,
        )

    latest_by_family: dict[str, Service1TenantSchemaFamilyMemoryV1] = {}
    for record in records:
        prior = latest_by_family.get(record.schema_family_ref)
        if prior is None or record.family_revision > prior.family_revision:
            latest_by_family[record.schema_family_ref] = record

    fingerprint = str(current.get("schema_fingerprint") or "")
    exact = [record for record in latest_by_family.values() if record.schema_fingerprint == fingerprint]
    if len(exact) == 1:
        return _revalidation_result(
            state=REVALIDATION_KNOWN_IDENTICAL,
            family_ref=exact[0].schema_family_ref,
            matched_record=exact[0],
            delta={
                "drift_state": DRIFT_IDENTICAL,
                "compatibility_state": COMPATIBILITY_KNOWN,
                "matching_status": TABLE_MATCH_READY,
                "affected_scope": [],
            },
            revalidation_scope=(),
            full_semantic_process_required=False,
        )
    if len(exact) > 1:
        return _revalidation_result(
            state=REVALIDATION_UNRESOLVED,
            family_ref=None,
            matched_record=None,
            delta=None,
            revalidation_scope=(),
            full_semantic_process_required=True,
            blocked_reason="AMBIGUOUS_EXACT_SCHEMA_FAMILY",
        )

    candidates: list[tuple[int, Service1TenantSchemaFamilyMemoryV1, dict[str, Any]]] = []
    for record in latest_by_family.values():
        prior_identity = dict(record.schema_identity)
        prior_identity["schema_family_ref"] = record.schema_family_ref
        candidate_current = dict(current)
        explicit_family = str(candidate_current.get("schema_family_ref") or UNKNOWN_FAMILY).strip() or UNKNOWN_FAMILY
        if explicit_family not in {UNKNOWN_FAMILY, record.schema_family_ref}:
            continue
        candidate_current["schema_family_ref"] = record.schema_family_ref
        delta = build_service_1_workbook_schema_delta_v1(
            prior_identity=prior_identity,
            current_identity=candidate_current,
        )
        if delta.get("status") != SCHEMA_READY or delta.get("matching_status") != TABLE_MATCH_READY:
            continue
        drift = str(delta.get("drift_state") or DRIFT_UNRESOLVED)
        matched_table_count = len(delta.get("changed_tables") or ()) + len(delta.get("unchanged_tables") or ())
        if drift == DRIFT_COMPATIBLE_DELTA:
            rank = 2
        elif drift == DRIFT_MATERIAL and matched_table_count > 0:
            # Material drift may still belong to a known family only when D3
            # found structural continuity. A pure remove+add replacement is
            # not enough evidence to assign family membership.
            rank = 1
        else:
            continue
        candidates.append((rank, record, delta))

    if not candidates:
        return _revalidation_result(
            state=REVALIDATION_UNKNOWN_FAMILY,
            family_ref=None,
            matched_record=None,
            delta=None,
            revalidation_scope=(),
            full_semantic_process_required=True,
        )
    best_rank = max(item[0] for item in candidates)
    best = [item for item in candidates if item[0] == best_rank]
    if len(best) != 1:
        return _revalidation_result(
            state=REVALIDATION_UNRESOLVED,
            family_ref=None,
            matched_record=None,
            delta=None,
            revalidation_scope=(),
            full_semantic_process_required=True,
            blocked_reason="AMBIGUOUS_SCHEMA_FAMILY_MATCH",
        )
    _, record, delta = best[0]
    drift = str(delta.get("drift_state") or DRIFT_UNRESOLVED)
    state = REVALIDATION_KNOWN_COMPATIBLE_DELTA if drift == DRIFT_COMPATIBLE_DELTA else REVALIDATION_KNOWN_MATERIAL_DELTA
    return _revalidation_result(
        state=state,
        family_ref=record.schema_family_ref,
        matched_record=record,
        delta=delta,
        revalidation_scope=tuple(delta.get("affected_scope") or ()),
        full_semantic_process_required=False,
    )


def _revalidation_result(
    *,
    state: str,
    family_ref: str | None,
    matched_record: Service1TenantSchemaFamilyMemoryV1 | None,
    delta: Mapping[str, Any] | None,
    revalidation_scope: Sequence[str],
    full_semantic_process_required: bool,
    blocked_reason: str | None = None,
) -> dict[str, Any]:
    semantic_refs = list(matched_record.semantic_mapping_refs) if matched_record is not None else []
    relationship_refs = list(matched_record.relationship_evidence_refs) if matched_record is not None else []
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY if state != REVALIDATION_UNRESOLVED else STATUS_BLOCKED,
        "blocked_reason": blocked_reason,
        "revalidation_state": state,
        "schema_family_ref": family_ref,
        "matched_memory_record_id": matched_record.record_id if matched_record is not None else None,
        "matched_schema_fingerprint": matched_record.schema_fingerprint if matched_record is not None else None,
        "schema_delta": dict(delta) if isinstance(delta, Mapping) else None,
        "affected_scope": list(revalidation_scope),
        "revalidation_scope": list(revalidation_scope),
        "historical_semantic_hints": semantic_refs,
        "historical_relationship_evidence_refs": relationship_refs,
        "historical_evidence_only": True,
        "full_semantic_process_required": bool(full_semantic_process_required),
        "automatic_reuse_authorized": False,
        "semantic_rebind_authorized": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "join_execution_authorized": False,
        "computability_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _normalize_header(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


__all__ = [
    "SCHEMA_VERSION",
    "RECORD_KIND",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "REVALIDATION_KNOWN_IDENTICAL",
    "REVALIDATION_KNOWN_COMPATIBLE_DELTA",
    "REVALIDATION_KNOWN_MATERIAL_DELTA",
    "REVALIDATION_UNKNOWN_FAMILY",
    "REVALIDATION_UNRESOLVED",
    "Service1TenantSchemaFamilyMemoryErrorV1",
    "Service1TenantSchemaFamilyMemoryV1",
    "build_service_1_scoped_semantic_mapping_refs_v1",
    "build_service_1_tenant_schema_family_memory_v1",
    "service_1_tenant_schema_family_memory_from_mapping_v1",
    "plan_service_1_schema_delta_revalidation_v1",
]

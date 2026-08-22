"""Servicio 1 — structural compatibility for tenant semantic memory V1.

ADR-029 / SEM-7. Builds stable structural signatures from SEM-1 workbook
profiles and classifies historical tenant semantic memory as a compatible hint,
an obsolete hint, or legacy-unverified evidence.

The signature intentionally excludes volatile row counts, exact cardinalities
and exact overlap percentages. It never authorizes semantic reuse, rebind,
runtime, product or delivery.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    SCHEMA_VERSION as WORKBOOK_PROFILE_SCHEMA_VERSION,
    STATUS_READY as WORKBOOK_PROFILE_READY,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_STRUCTURAL_COMPATIBILITY_SIGNATURE_V1"
STATUS_COMPATIBLE_HINT: Final[str] = "COMPATIBLE_HINT"
STATUS_OBSOLETE_HINT: Final[str] = "OBSOLETE_HINT"
STATUS_LEGACY_UNVERIFIED_HINT: Final[str] = "LEGACY_UNVERIFIED_HINT"
STATUS_NO_MATCH: Final[str] = "NO_MATCH"
STATUS_READY: Final[str] = "TENANT_MEMORY_COMPATIBILITY_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_PROFILE_INVALID: Final[str] = "BLOCK_STRUCTURAL_PROFILE_INVALID"
BLOCK_COLUMN_NOT_FOUND: Final[str] = "BLOCK_STRUCTURAL_COLUMN_NOT_FOUND"
BLOCK_SIGNATURE_INVALID: Final[str] = "BLOCK_STRUCTURAL_SIGNATURE_INVALID"
BLOCK_TENANT_REQUIRED: Final[str] = "BLOCK_STRUCTURAL_TENANT_REQUIRED"
BLOCK_SOURCE_CONTEXT_REQUIRED: Final[str] = "BLOCK_STRUCTURAL_SOURCE_CONTEXT_REQUIRED"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "automatic_reuse_authorized",
    "semantic_rebind_authorized",
)


@dataclass(frozen=True)
class Service1StructuralCompatibilitySignatureV1:
    signature_id: str
    column_ref: str
    normalized_header: str
    data_type_family: str
    nullability_class: str
    uniqueness_class: str
    key_role: str
    relationship_shape: tuple[str, ...]
    source_system_ref: str
    source_context_ref: str
    schema_version: str = SCHEMA_VERSION
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    automatic_reuse_authorized: bool = False
    semantic_rebind_authorized: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(BLOCK_SIGNATURE_INVALID)
        for name in (
            "signature_id",
            "column_ref",
            "normalized_header",
            "data_type_family",
            "nullability_class",
            "uniqueness_class",
            "key_role",
            "source_system_ref",
            "source_context_ref",
        ):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(BLOCK_SIGNATURE_INVALID)
        if any(getattr(self, flag) is not False for flag in _AUTHORITY_FLAGS):
            raise ValueError(BLOCK_SIGNATURE_INVALID)
        expected = _signature_id(
            column_ref=self.column_ref,
            normalized_header=self.normalized_header,
            data_type_family=self.data_type_family,
            nullability_class=self.nullability_class,
            uniqueness_class=self.uniqueness_class,
            key_role=self.key_role,
            relationship_shape=self.relationship_shape,
            source_system_ref=self.source_system_ref,
            source_context_ref=self.source_context_ref,
        )
        if self.signature_id != expected:
            raise ValueError(BLOCK_SIGNATURE_INVALID)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["relationship_shape"] = list(self.relationship_shape)
        return payload


def build_service_1_structural_signature_v1(
    *,
    workbook_profile: Mapping[str, Any],
    column_ref: str,
    source_system_ref: str,
    source_context_ref: str,
) -> Service1StructuralCompatibilitySignatureV1:
    if not _valid_profile(workbook_profile):
        raise ValueError(BLOCK_PROFILE_INVALID)
    requested = str(column_ref or "").strip()
    system_ref = str(source_system_ref or "").strip()
    context_ref = str(source_context_ref or "").strip()
    if not system_ref or not context_ref:
        raise ValueError(BLOCK_SOURCE_CONTEXT_REQUIRED)
    column = next(
        (
            item
            for item in workbook_profile.get("columns") or []
            if isinstance(item, Mapping)
            and str(item.get("column_ref") or "").strip() == requested
        ),
        None,
    )
    if column is None:
        raise ValueError(BLOCK_COLUMN_NOT_FOUND)

    relationships = [
        item
        for item in workbook_profile.get("relationships") or []
        if isinstance(item, Mapping)
        and requested
        in {
            str(item.get("left_column_ref") or "").strip(),
            str(item.get("right_column_ref") or "").strip(),
        }
    ]
    relationship_shape = tuple(sorted(_relationship_shape(requested, item) for item in relationships))
    data_type_family = _data_type_family(column.get("inferred_type"))
    nullability_class = _nullability_class(column.get("null_ratio"))
    uniqueness_class = str(column.get("uniqueness_class") or "UNKNOWN").strip().upper()
    key_role = _key_role(requested, column, relationships)
    normalized_header = str(column.get("normalized_header") or "").strip().casefold()
    signature_id = _signature_id(
        column_ref=requested,
        normalized_header=normalized_header,
        data_type_family=data_type_family,
        nullability_class=nullability_class,
        uniqueness_class=uniqueness_class,
        key_role=key_role,
        relationship_shape=relationship_shape,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
    )
    return Service1StructuralCompatibilitySignatureV1(
        signature_id=signature_id,
        column_ref=requested,
        normalized_header=normalized_header,
        data_type_family=data_type_family,
        nullability_class=nullability_class,
        uniqueness_class=uniqueness_class,
        key_role=key_role,
        relationship_shape=relationship_shape,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
    )


def service_1_structural_signature_from_mapping_v1(
    payload: Mapping[str, Any],
) -> Service1StructuralCompatibilitySignatureV1:
    if not isinstance(payload, Mapping):
        raise ValueError(BLOCK_SIGNATURE_INVALID)
    shape = payload.get("relationship_shape")
    if not isinstance(shape, (list, tuple)):
        raise ValueError(BLOCK_SIGNATURE_INVALID)
    return Service1StructuralCompatibilitySignatureV1(
        signature_id=str(payload.get("signature_id") or "").strip(),
        column_ref=str(payload.get("column_ref") or "").strip(),
        normalized_header=str(payload.get("normalized_header") or "").strip(),
        data_type_family=str(payload.get("data_type_family") or "").strip(),
        nullability_class=str(payload.get("nullability_class") or "").strip(),
        uniqueness_class=str(payload.get("uniqueness_class") or "").strip(),
        key_role=str(payload.get("key_role") or "").strip(),
        relationship_shape=tuple(str(item).strip() for item in shape if str(item).strip()),
        source_system_ref=str(payload.get("source_system_ref") or "").strip(),
        source_context_ref=str(payload.get("source_context_ref") or "").strip(),
        schema_version=str(payload.get("schema_version") or "").strip(),
        runtime_authorized=payload.get("runtime_authorized") is True,
        tool_execution_authorized=payload.get("tool_execution_authorized") is True,
        product_ready=payload.get("product_ready") is True,
        delivery_authorized=payload.get("delivery_authorized") is True,
        diagnosis_generated=payload.get("diagnosis_generated") is True,
        automatic_reuse_authorized=payload.get("automatic_reuse_authorized") is True,
        semantic_rebind_authorized=payload.get("semantic_rebind_authorized") is True,
    )


def classify_service_1_structural_compatibility_v1(
    *,
    historical_signature: Mapping[str, Any] | Service1StructuralCompatibilitySignatureV1 | None,
    current_signature: Mapping[str, Any] | Service1StructuralCompatibilitySignatureV1,
) -> dict[str, Any]:
    current = _coerce_signature(current_signature)
    if historical_signature is None:
        return _compatibility_result(
            STATUS_LEGACY_UNVERIFIED_HINT,
            current=current,
            historical=None,
            changed_fields=["structural_signature_missing"],
        )
    historical = _coerce_signature(historical_signature)
    if historical.column_ref != current.column_ref:
        return _compatibility_result(
            STATUS_NO_MATCH,
            current=current,
            historical=historical,
            changed_fields=["column_ref"],
        )
    compared = (
        "normalized_header",
        "data_type_family",
        "nullability_class",
        "uniqueness_class",
        "key_role",
        "relationship_shape",
        "source_system_ref",
        "source_context_ref",
    )
    changed = [name for name in compared if getattr(historical, name) != getattr(current, name)]
    return _compatibility_result(
        STATUS_COMPATIBLE_HINT if not changed else STATUS_OBSOLETE_HINT,
        current=current,
        historical=historical,
        changed_fields=changed,
    )


def select_service_1_compatible_tenant_memory_hints_v1(
    *,
    tenant_id: str,
    source_system_ref: str,
    source_context_ref: str,
    workbook_profile: Mapping[str, Any],
    memory_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    tenant = str(tenant_id or "").strip()
    if not tenant:
        return _selection_blocked(BLOCK_TENANT_REQUIRED)
    system_ref = str(source_system_ref or "").strip()
    context_ref = str(source_context_ref or "").strip()
    if not system_ref or not context_ref:
        return _selection_blocked(BLOCK_SOURCE_CONTEXT_REQUIRED)
    if not _valid_profile(workbook_profile):
        return _selection_blocked(BLOCK_PROFILE_INVALID)

    current_by_ref = {
        str(item.get("column_ref") or "").strip(): build_service_1_structural_signature_v1(
            workbook_profile=workbook_profile,
            column_ref=str(item.get("column_ref") or "").strip(),
            source_system_ref=system_ref,
            source_context_ref=context_ref,
        )
        for item in workbook_profile.get("columns") or []
        if isinstance(item, Mapping) and str(item.get("column_ref") or "").strip()
    }

    latest: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in memory_rows:
        if not isinstance(row, Mapping):
            continue
        if str(row.get("tenant_id") or "").strip() != tenant:
            continue
        if str(row.get("source_system_ref") or "").strip() != system_ref:
            continue
        if str(row.get("source_context_ref") or "").strip() != context_ref:
            continue
        sheet = str(row.get("sheet_ref") or "").strip()
        column = str(row.get("source_column_name") or row.get("column_ref") or "").strip()
        if not sheet or not column:
            continue
        key = (sheet, column)
        revision = _revision(row)
        prior = latest.get(key)
        if prior is None or revision >= _revision(prior):
            latest[key] = row

    compatible: list[dict[str, Any]] = []
    obsolete: list[dict[str, Any]] = []
    legacy: list[dict[str, Any]] = []
    for (sheet, column), row in latest.items():
        ref = f"{sheet}.{column}"
        current = current_by_ref.get(ref)
        if current is None:
            continue
        historical_payload = row.get("structural_signature")
        classification = classify_service_1_structural_compatibility_v1(
            historical_signature=(historical_payload if isinstance(historical_payload, Mapping) else None),
            current_signature=current,
        )
        item = {
            "contract_id": row.get("contract_id"),
            "mapping_series_id": row.get("mapping_series_id"),
            "column_ref": ref,
            "confirmed_role": row.get("confirmed_role"),
            "confirmed_variable": row.get("confirmed_variable"),
            "corrected_meaning": row.get("corrected_meaning"),
            "column_excluded": row.get("column_excluded") is True,
            "compatibility_status": classification["status"],
            "changed_fields": list(classification["changed_fields"]),
            "historical_evidence_only": True,
            "automatic_reuse_authorized": False,
            "semantic_rebind_authorized": False,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
        }
        if classification["status"] == STATUS_COMPATIBLE_HINT:
            compatible.append(item)
        elif classification["status"] == STATUS_OBSOLETE_HINT:
            obsolete.append(item)
        else:
            legacy.append(item)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "tenant_id": tenant,
        "compatible_hints": compatible,
        "obsolete_hints": obsolete,
        "legacy_unverified_hints": legacy,
        "compatible_hint_count": len(compatible),
        "obsolete_hint_count": len(obsolete),
        "legacy_unverified_hint_count": len(legacy),
        "automatic_reuse_authorized": False,
        "semantic_rebind_authorized": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _valid_profile(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("schema_version") == WORKBOOK_PROFILE_SCHEMA_VERSION
        and value.get("status") == WORKBOOK_PROFILE_READY
        and isinstance(value.get("columns"), list)
        and isinstance(value.get("relationships"), list)
        and not any(bool(value.get(flag)) for flag in _AUTHORITY_FLAGS[:5])
    )


def _data_type_family(value: Any) -> str:
    text = str(value or "").strip().casefold()
    if text in {"number", "numeric", "decimal", "float", "integer", "int", "currency", "money"}:
        return "NUMBER"
    if text in {"date", "datetime", "timestamp"}:
        return "DATE"
    if text in {"text", "string", "str"}:
        return "TEXT"
    if text == "empty":
        return "EMPTY"
    if text == "mixed":
        return "MIXED"
    return "UNKNOWN"


def _nullability_class(value: Any) -> str:
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        return "UNKNOWN"
    if ratio <= 0:
        return "NONE"
    if ratio <= 0.05:
        return "LOW"
    if ratio < 1:
        return "MATERIAL"
    return "ALL_NULL"


def _overlap_band(value: Any) -> str:
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        return "UNKNOWN"
    if ratio >= 0.95:
        return "VERY_HIGH"
    if ratio >= 0.80:
        return "HIGH"
    if ratio >= 0.50:
        return "MEDIUM"
    return "LOW"


def _relationship_shape(column_ref: str, relationship: Mapping[str, Any]) -> str:
    left = str(relationship.get("left_column_ref") or "").strip()
    right = str(relationship.get("right_column_ref") or "").strip()
    kind = str(relationship.get("relationship_kind") or "UNKNOWN").strip().upper()
    if column_ref == left:
        direction = "OUTBOUND"
        overlap = _overlap_band(relationship.get("left_value_coverage"))
    else:
        direction = "INBOUND"
        overlap = _overlap_band(relationship.get("right_value_coverage"))
    key_link = "FK" if relationship.get("candidate_foreign_key") and column_ref == left else (
        "PK" if relationship.get("candidate_primary_key_ref") == column_ref else "STRUCTURAL"
    )
    return f"{direction}|{kind}|{key_link}|{overlap}"


def _key_role(
    column_ref: str,
    column: Mapping[str, Any],
    relationships: Sequence[Mapping[str, Any]],
) -> str:
    is_pk = bool(column.get("candidate_primary_key")) or any(
        str(item.get("candidate_primary_key_ref") or "").strip() == column_ref
        for item in relationships
    )
    is_fk = any(
        item.get("candidate_foreign_key") is True
        and str(item.get("left_column_ref") or "").strip() == column_ref
        for item in relationships
    )
    if is_pk and is_fk:
        return "PRIMARY_AND_FOREIGN_KEY_CANDIDATE"
    if is_pk:
        return "PRIMARY_KEY_CANDIDATE"
    if is_fk:
        return "FOREIGN_KEY_CANDIDATE"
    return "NONE"


def _signature_id(
    *,
    column_ref: str,
    normalized_header: str,
    data_type_family: str,
    nullability_class: str,
    uniqueness_class: str,
    key_role: str,
    relationship_shape: tuple[str, ...],
    source_system_ref: str,
    source_context_ref: str,
) -> str:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "column_ref": column_ref,
        "normalized_header": normalized_header,
        "data_type_family": data_type_family,
        "nullability_class": nullability_class,
        "uniqueness_class": uniqueness_class,
        "key_role": key_role,
        "relationship_shape": list(relationship_shape),
        "source_system_ref": source_system_ref,
        "source_context_ref": source_context_ref,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "scs_" + hashlib.sha256(encoded).hexdigest()


def build_service_1_structural_digest_v1(
    *,
    payload: Mapping[str, Any],
    prefix: str = "stf_",
) -> str:
    """Build a deterministic SHA-256 digest for higher-level structure.

    This is the same canonical JSON/SHA-256 mechanism used by the existing
    column compatibility signature, exposed additively for table candidates.
    Callers must omit volatile values such as filenames and row counts.
    """
    if not isinstance(payload, Mapping):
        raise ValueError(BLOCK_SIGNATURE_INVALID)
    clean_prefix = str(prefix or "").strip()
    if not clean_prefix:
        raise ValueError(BLOCK_SIGNATURE_INVALID)
    encoded = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return clean_prefix + hashlib.sha256(encoded).hexdigest()


def _coerce_signature(
    value: Mapping[str, Any] | Service1StructuralCompatibilitySignatureV1,
) -> Service1StructuralCompatibilitySignatureV1:
    if isinstance(value, Service1StructuralCompatibilitySignatureV1):
        return value
    return service_1_structural_signature_from_mapping_v1(value)


def _compatibility_result(
    status: str,
    *,
    current: Service1StructuralCompatibilitySignatureV1,
    historical: Service1StructuralCompatibilitySignatureV1 | None,
    changed_fields: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "changed_fields": changed_fields,
        "current_signature_id": current.signature_id,
        "historical_signature_id": historical.signature_id if historical else None,
        "historical_evidence_only": True,
        "automatic_reuse_authorized": False,
        "semantic_rebind_authorized": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _selection_blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "compatible_hints": [],
        "obsolete_hints": [],
        "legacy_unverified_hints": [],
        "compatible_hint_count": 0,
        "obsolete_hint_count": 0,
        "legacy_unverified_hint_count": 0,
        "automatic_reuse_authorized": False,
        "semantic_rebind_authorized": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _revision(row: Mapping[str, Any]) -> int:
    try:
        return int(row.get("revision") or 0)
    except (TypeError, ValueError):
        return 0


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_COMPATIBLE_HINT",
    "STATUS_OBSOLETE_HINT",
    "STATUS_LEGACY_UNVERIFIED_HINT",
    "STATUS_NO_MATCH",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "Service1StructuralCompatibilitySignatureV1",
    "build_service_1_structural_digest_v1",
    "build_service_1_structural_signature_v1",
    "service_1_structural_signature_from_mapping_v1",
    "classify_service_1_structural_compatibility_v1",
    "select_service_1_compatible_tenant_memory_hints_v1",
]

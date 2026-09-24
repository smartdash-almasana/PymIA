"""D3 schema identity, family, version, and delta contracts.

This module is deliberately evidence-only.  It raises the D2 logical-table
candidate evidence to workbook/schema scope, reusing the canonical structural
SHA-256 helper instead of introducing another fingerprint implementation.
No tenant memory, semantic rebinding, joins, or downstream authority is
changed here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_WORKBOOK_SCHEMA_IDENTITY_V1"
DELTA_SCHEMA_VERSION: Final[str] = "SERVICE_1_WORKBOOK_SCHEMA_DELTA_V1"
STATUS_READY: Final[str] = "WORKBOOK_SCHEMA_READY"
STATUS_UNRESOLVED: Final[str] = "UNRESOLVED"
STATUS_BLOCKED: Final[str] = "BLOCKED"

UNKNOWN_FAMILY: Final[str] = "UNKNOWN"
GRAIN_RESOLVED: Final[str] = "RESOLVED"
GRAIN_UNRESOLVED: Final[str] = "UNRESOLVED"

DRIFT_IDENTICAL: Final[str] = "IDENTICAL"
DRIFT_COMPATIBLE_DELTA: Final[str] = "COMPATIBLE_DELTA"
DRIFT_MATERIAL: Final[str] = "MATERIAL_DRIFT"
DRIFT_NEW_FAMILY: Final[str] = "NEW_FAMILY"
DRIFT_UNRESOLVED: Final[str] = "UNRESOLVED"

COMPATIBILITY_KNOWN: Final[str] = "KNOWN_SCHEMA"
COMPATIBILITY_KNOWN_DELTA: Final[str] = "KNOWN_SCHEMA_WITH_COMPATIBLE_DELTA"
COMPATIBILITY_MATERIAL: Final[str] = "MATERIAL_SCHEMA_DRIFT"
COMPATIBILITY_NEW_FAMILY: Final[str] = "NEW_SCHEMA_FAMILY"

# Column order is presentation/physical evidence, not schema identity.  The
# canonical payload sorts columns by normalized header before hashing.
COLUMN_ORDER_POLICY: Final[str] = "CANONICALIZED_BY_NORMALIZED_HEADER"
SCHEMA_DRIFT_IS_DELTA: Final[str] = "SCHEMA_DRIFT_IS_DELTA"
TABLE_MATCH_READY: Final[str] = "TABLE_MATCH_READY"
TABLE_MATCH_UNRESOLVED: Final[str] = "TABLE_MATCH_UNRESOLVED"


@dataclass(frozen=True)
class WorkbookSchemaIdentityV1:
    schema_fingerprint: str
    schema_family_ref: str
    schema_version: str
    logical_table_signatures: tuple[dict[str, Any], ...]
    structural_relationship_signature: tuple[dict[str, Any], ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    semantic_rebind_authorized: bool = False
    family_auto_reuse_authorized: bool = False
    computability_authorized: bool = False

    def __post_init__(self) -> None:
        if not str(self.schema_fingerprint).strip():
            raise ValueError("schema_fingerprint must be non-empty")
        if not str(self.schema_family_ref or UNKNOWN_FAMILY).strip():
            raise ValueError("schema_family_ref must be non-empty")
        if not str(self.schema_version).strip():
            raise ValueError("schema_version must be non-empty")
        object.__setattr__(self, "schema_family_ref", str(self.schema_family_ref).strip())
        object.__setattr__(self, "schema_version", str(self.schema_version).strip())
        object.__setattr__(self, "logical_table_signatures", tuple(dict(item) for item in self.logical_table_signatures))
        object.__setattr__(self, "structural_relationship_signature", tuple(dict(item) for item in self.structural_relationship_signature))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in (
            "runtime_authorized",
            "semantic_rebind_authorized",
            "family_auto_reuse_authorized",
            "computability_authorized",
        ):
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        result = _as_jsonable(asdict(self))
        # ``relationship_signature`` is the shorter architectural name used
        # by the implementation plan; retain the explicit field as well.
        result["relationship_signature"] = result["structural_relationship_signature"]
        return result


@dataclass(frozen=True)
class WorkbookSchemaDeltaV1:
    prior_schema_fingerprint: str
    current_schema_fingerprint: str
    added_tables: tuple[dict[str, Any], ...] = ()
    removed_tables: tuple[dict[str, Any], ...] = ()
    changed_tables: tuple[dict[str, Any], ...] = ()
    unchanged_tables: tuple[dict[str, Any], ...] = ()
    added_columns: tuple[dict[str, Any], ...] = ()
    removed_columns: tuple[dict[str, Any], ...] = ()
    changed_columns: tuple[dict[str, Any], ...] = ()
    changed_grains: tuple[dict[str, Any], ...] = ()
    changed_keys: tuple[dict[str, Any], ...] = ()
    changed_relationships: tuple[dict[str, Any], ...] = ()
    affected_scope: tuple[str, ...] = ()
    drift_state: str = DRIFT_UNRESOLVED
    compatibility_state: str = DRIFT_UNRESOLVED
    matching_status: str = TABLE_MATCH_READY
    blocked_reason: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    semantic_rebind_authorized: bool = False
    family_auto_reuse_authorized: bool = False
    computability_authorized: bool = False

    def __post_init__(self) -> None:
        for name in ("prior_schema_fingerprint", "current_schema_fingerprint", "drift_state", "compatibility_state", "matching_status"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must be non-empty")
        for name in (
            "added_tables", "removed_tables", "changed_tables", "unchanged_tables",
            "added_columns", "removed_columns", "changed_columns", "changed_grains",
            "changed_keys", "changed_relationships",
        ):
            object.__setattr__(self, name, tuple(dict(item) for item in getattr(self, name)))
        object.__setattr__(self, "affected_scope", tuple(dict.fromkeys(str(item) for item in self.affected_scope)))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in (
            "runtime_authorized",
            "semantic_rebind_authorized",
            "family_auto_reuse_authorized",
            "computability_authorized",
        ):
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        result = _as_jsonable(asdict(self))
        result["prior_fingerprint"] = result["prior_schema_fingerprint"]
        result["current_fingerprint"] = result["current_schema_fingerprint"]
        return result


def build_service_1_workbook_schema_identity_v1(
    *,
    logical_table_candidates: Sequence[Mapping[str, Any]] | None = None,
    candidates: Sequence[Mapping[str, Any]] | None = None,
    relationship_evidence: Sequence[Mapping[str, Any]] = (),
    workbook_profile: Mapping[str, Any] | None = None,
    workbook_ref: str | None = None,
    schema_family_ref: str | None = None,
    schema_version: str | int = "1",
    provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic schema identity from D2 evidence.

    ``workbook_ref`` is retained only as provenance.  It is never included in
    any structural digest.  Callers may provide a family hint, but omitting it
    deliberately yields ``UNKNOWN`` rather than silently authorizing reuse.
    """
    raw_candidates = logical_table_candidates if logical_table_candidates is not None else candidates
    if raw_candidates is None:
        return _blocked("LOGICAL_TABLE_CANDIDATES_REQUIRED")
    if not relationship_evidence and isinstance(workbook_profile, Mapping):
        relationship_evidence = (
            workbook_profile.get("relationship_evidence")
            or workbook_profile.get("relationships")
            or ()
        )
    if isinstance(raw_candidates, Mapping):
        raw_candidates = raw_candidates.get("candidates")
    try:
        materialized_candidates = list(raw_candidates)
    except TypeError:
        return _blocked("LOGICAL_TABLE_CANDIDATES_NOT_SEQUENCE")
    candidate_list = [item for item in materialized_candidates if isinstance(item, Mapping)]
    if not candidate_list:
        return _unresolved("LOGICAL_TABLE_CANDIDATES_EMPTY")

    table_signatures = tuple(
        sorted(
            (_normalize_table_candidate(candidate) for candidate in candidate_list),
            key=lambda item: (str(item["table_signature"]), str(item["table_key"])),
        )
    )
    relationship_signature = tuple(
        sorted(
            (_normalize_relationship(item) for item in relationship_evidence if isinstance(item, Mapping)),
            key=lambda item: str(item["relationship_signature"]),
        )
    )
    fingerprint_payload = {
        "contract": SCHEMA_VERSION,
        "column_order_policy": COLUMN_ORDER_POLICY,
        "logical_tables": [
            _table_fingerprint_payload(item) for item in table_signatures
        ],
        "relationships": [
            _relationship_fingerprint_payload(item) for item in relationship_signature
        ],
    }
    fingerprint = build_service_1_structural_digest_v1(
        payload=fingerprint_payload,
        prefix="wsi_",
    )
    family = str(schema_family_ref or UNKNOWN_FAMILY).strip() or UNKNOWN_FAMILY
    identity = WorkbookSchemaIdentityV1(
        schema_fingerprint=fingerprint,
        schema_family_ref=family,
        schema_version=str(schema_version),
        logical_table_signatures=table_signatures,
        structural_relationship_signature=relationship_signature,
        provenance={
            **dict(provenance or {}),
            "contract": SCHEMA_VERSION,
            "workbook_ref": str(workbook_ref or ""),
            "column_order_policy": COLUMN_ORDER_POLICY,
            "schema_drift_rule": SCHEMA_DRIFT_IS_DELTA,
            "fingerprint_exclusions": [
                "filename", "workbook_ref", "local_path", "case_id", "timestamp",
                "processing_order", "tenant_id", "business_values",
            ],
        },
    )
    return {
        "contract_schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        **identity.to_dict(),
    }


def build_service_1_workbook_schema_delta_v1(
    *,
    prior_identity: Mapping[str, Any] | WorkbookSchemaIdentityV1,
    current_identity: Mapping[str, Any] | WorkbookSchemaIdentityV1,
) -> dict[str, Any]:
    """Compare two identities without executing a relationship graph."""
    prior = _identity_mapping(prior_identity)
    current = _identity_mapping(current_identity)
    prior_fp = str(prior.get("schema_fingerprint") or "")
    current_fp = str(current.get("schema_fingerprint") or "")
    if not prior_fp or not current_fp:
        return _blocked("SCHEMA_FINGERPRINT_REQUIRED")

    prior_tables = _table_records(prior)
    current_tables = _table_records(current)

    # Equal schema fingerprints are already a canonical multiset comparison.
    # Do not let instance refs (including D2's ``_rN`` suffix) manufacture a
    # table delta when only candidate processing order changed.
    if prior_fp == current_fp:
        unchanged_tables = tuple(
            {
                "table_key": _record_scope_key(record),
                "table_signature": record.get("table_signature"),
            }
            for record in sorted(
                current_tables,
                key=lambda item: (str(item.get("table_signature")), _record_scope_key(item)),
            )
        )
        relationship_changes = ()
        delta = WorkbookSchemaDeltaV1(
            prior_schema_fingerprint=prior_fp,
            current_schema_fingerprint=current_fp,
            unchanged_tables=unchanged_tables,
            affected_scope=(),
            drift_state=DRIFT_IDENTICAL,
            compatibility_state=COMPATIBILITY_KNOWN,
            matching_status=TABLE_MATCH_READY,
            provenance={"contract": DELTA_SCHEMA_VERSION, "schema_drift_rule": SCHEMA_DRIFT_IS_DELTA},
        )
        return {"contract_schema_version": DELTA_SCHEMA_VERSION, "status": STATUS_READY, **delta.to_dict()}

    matches, unmatched_prior, unmatched_current, matching_status, blocked_reason = _match_table_records(
        prior_tables,
        current_tables,
    )
    added_tables = tuple(
        {
            "table_key": _record_scope_key(current_tables[index]),
            "table_signature": current_tables[index].get("table_signature"),
        }
        for index in sorted(unmatched_current, key=lambda item: _record_scope_key(current_tables[item]))
    )
    removed_tables = tuple(
        {
            "table_key": _record_scope_key(prior_tables[index]),
            "table_signature": prior_tables[index].get("table_signature"),
        }
        for index in sorted(unmatched_prior, key=lambda item: _record_scope_key(prior_tables[item]))
    )
    unchanged_tables: list[dict[str, Any]] = []
    changed_tables: list[dict[str, Any]] = []

    added_columns: list[dict[str, Any]] = []
    removed_columns: list[dict[str, Any]] = []
    changed_columns: list[dict[str, Any]] = []
    changed_grains: list[dict[str, Any]] = []
    changed_keys: list[dict[str, Any]] = []
    scope: list[str] = []
    for prior_index, current_index, match_key in matches:
        before, after = prior_tables[prior_index], current_tables[current_index]
        before_columns = {str(item["normalized_header"]): item for item in before.get("column_signatures", ())}
        after_columns = {str(item["normalized_header"]): item for item in after.get("column_signatures", ())}
        if before.get("table_signature") == after.get("table_signature"):
            unchanged_tables.append({"table_key": match_key, "table_signature": after.get("table_signature")})
        else:
            changed_tables.append({
                "table_key": match_key,
                "prior_signature": before.get("table_signature"),
                "current_signature": after.get("table_signature"),
            })
        for column in sorted(set(after_columns) - set(before_columns)):
            added_columns.append({"table_key": match_key, "column": column, "current_signature": after_columns[column]})
            _scope_add(scope, f"table:{match_key}", f"column:{match_key}.{column}")
        for column in sorted(set(before_columns) - set(after_columns)):
            removed_columns.append({"table_key": match_key, "column": column, "prior_signature": before_columns[column]})
            _scope_add(scope, f"table:{match_key}", f"column:{match_key}.{column}")
        for column in sorted(set(before_columns) & set(after_columns)):
            if before_columns[column] != after_columns[column]:
                changed_columns.append({
                    "table_key": match_key,
                    "column": column,
                    "prior_signature": before_columns[column],
                    "current_signature": after_columns[column],
                })
                _scope_add(scope, f"table:{match_key}", f"column:{match_key}.{column}")
        if before.get("grain_signature") != after.get("grain_signature"):
            changed_grains.append({"table_key": match_key, "prior": before.get("grain_signature"), "current": after.get("grain_signature")})
            _scope_add(scope, f"table:{match_key}", f"grain:{match_key}")
        if before.get("key_signatures") != after.get("key_signatures"):
            changed_keys.append({"table_key": match_key, "prior": before.get("key_signatures", ()), "current": after.get("key_signatures", ())})
            _scope_add(scope, f"table:{match_key}", f"key:{match_key}")

    for record in added_tables + removed_tables:
        _scope_add(scope, f"table:{record['table_key']}")

    relationship_changes = _relationship_delta(prior, current, scope)
    drift_state, compatibility_state = _classify_delta(
        prior=prior,
        current=current,
        prior_fp=prior_fp,
        current_fp=current_fp,
        added_tables=added_tables,
        removed_tables=removed_tables,
        changed_tables=changed_tables,
        changed_columns=changed_columns,
        changed_grains=changed_grains,
        changed_keys=changed_keys,
        changed_relationships=relationship_changes,
        matching_status=matching_status,
    )
    delta = WorkbookSchemaDeltaV1(
        prior_schema_fingerprint=prior_fp,
        current_schema_fingerprint=current_fp,
        added_tables=added_tables,
        removed_tables=removed_tables,
        changed_tables=tuple(changed_tables),
        unchanged_tables=tuple(unchanged_tables),
        added_columns=tuple(added_columns),
        removed_columns=tuple(removed_columns),
        changed_columns=tuple(changed_columns),
        changed_grains=tuple(changed_grains),
        changed_keys=tuple(changed_keys),
        changed_relationships=tuple(relationship_changes),
        affected_scope=tuple(scope),
        drift_state=drift_state,
        compatibility_state=compatibility_state,
        matching_status=matching_status,
        blocked_reason=blocked_reason,
        provenance={"contract": DELTA_SCHEMA_VERSION, "schema_drift_rule": SCHEMA_DRIFT_IS_DELTA},
    )
    return {"contract_schema_version": DELTA_SCHEMA_VERSION, "status": STATUS_READY, **delta.to_dict()}


compare_service_1_workbook_schema_identities_v1 = build_service_1_workbook_schema_delta_v1
compare_service_1_workbook_schema_delta_v1 = build_service_1_workbook_schema_delta_v1
build_service_1_schema_delta_v1 = build_service_1_workbook_schema_delta_v1
Service1WorkbookSchemaIdentityV1 = WorkbookSchemaIdentityV1
Service1WorkbookSchemaDeltaV1 = WorkbookSchemaDeltaV1


def _normalize_table_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    table_key = str(candidate.get("table_key") or candidate.get("logical_table_id") or candidate.get("candidate_id") or "").strip()
    if not table_key:
        raise ValueError("logical table candidate requires a stable table key")
    provenance = candidate.get("provenance") if isinstance(candidate.get("provenance"), Mapping) else {}
    structural = provenance.get("structural_payload") if isinstance(provenance.get("structural_payload"), Mapping) else {}
    raw_columns = structural.get("columns") if isinstance(structural.get("columns"), Sequence) and not isinstance(structural.get("columns"), (str, bytes)) else candidate.get("columns", ())
    columns: list[dict[str, Any]] = []
    for raw in raw_columns or ():
        if not isinstance(raw, Mapping):
            continue
        header = _normalize_header(raw.get("normalized_header") or raw.get("header") or raw.get("column_name"))
        if not header:
            continue
        columns.append({
            "normalized_header": header,
            "inferred_type": _normalize_scalar(raw.get("inferred_type") or raw.get("data_type_family") or "unknown"),
            "nullability_class": _normalize_scalar(raw.get("nullability_class") or "UNKNOWN"),
            "uniqueness_class": _normalize_scalar(raw.get("uniqueness_class") or "UNKNOWN"),
            "candidate_primary_key": bool(raw.get("candidate_primary_key") is True),
        })
    columns.sort(key=lambda item: (item["normalized_header"], _canonical_key(item)))
    key_signatures = _key_signatures(candidate, table_key)
    grain_state = str(candidate.get("grain_state") or GRAIN_UNRESOLVED).strip().upper()
    if grain_state not in {GRAIN_RESOLVED, GRAIN_UNRESOLVED}:
        grain_state = GRAIN_UNRESOLVED
    grain_signature = {
        "state": grain_state,
        "candidate": _grain_shape(candidate.get("grain_candidate"), table_key) if grain_state == GRAIN_RESOLVED else None,
    }
    table_payload = {
        "columns": columns,
        "grain": grain_signature,
        "keys": key_signatures,
    }
    if not columns and candidate.get("structural_signature"):
        # D2 always emits structural payload columns, but retaining this
        # evidence as a closed fallback keeps the D3 contract useful for
        # serialized/minimal candidate fixtures without hashing volatile data.
        table_payload["d2_structural_signature"] = str(candidate.get("structural_signature"))
    table_signature = build_service_1_structural_digest_v1(payload=table_payload, prefix="lts_")
    matching_identity = _candidate_matching_identity(candidate, table_key)
    return {
        "table_key": table_key,
        "instance_ref": table_key,
        "matching_identity": matching_identity,
        "table_signature": table_signature,
        "structural_table_signature": table_signature,
        "column_signatures": tuple(columns),
        "grain_signature": grain_signature,
        "grain_state": grain_state,
        "key_signatures": tuple(key_signatures),
        "relationship_shape_signature": (),
        "matching_evidence": {
            "column_headers": tuple(item["normalized_header"] for item in columns),
            "key_signatures": tuple(key_signatures),
            "grain_signature": grain_signature,
        },
    }


def _key_signatures(candidate: Mapping[str, Any], table_key: str) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for field_name, default_kind in (("primary_key_candidates", "PRIMARY"), ("unique_key_candidates", "UNIQUE")):
        raw_values = candidate.get(field_name) or ()
        if not isinstance(raw_values, Sequence) or isinstance(raw_values, (str, bytes)):
            continue
        for raw in raw_values:
            if not isinstance(raw, Mapping):
                continue
            refs = [_normalize_column_ref(value, table_key) for value in raw.get("column_refs") or ()]
            refs = sorted(set(ref for ref in refs if ref))
            if not refs:
                continue
            records.append({
                "kind": _normalize_scalar(raw.get("key_kind") or default_kind),
                "columns": refs,
                "candidate_primary_key": bool(raw.get("candidate_primary_key") is True),
            })
    return tuple(sorted(records, key=_canonical_key))


def _grain_shape(value: Any, table_key: str) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    shape: dict[str, Any] = {}
    for key in ("kind", "grain_kind", "cardinality"):
        if value.get(key) is not None:
            shape[key] = _normalize_scalar(value.get(key))
    refs = value.get("key_refs") or value.get("candidate_key_refs")
    if isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)):
        shape["key_refs"] = sorted(set(_normalize_column_ref(item, table_key) for item in refs if _normalize_column_ref(item, table_key)))
    return shape or None


def _normalize_relationship(value: Mapping[str, Any]) -> dict[str, Any]:
    shape = {
        "left": _normalize_column_ref(value.get("left_column_ref") or value.get("left") or value.get("source_column"), ""),
        "right": _normalize_column_ref(value.get("right_column_ref") or value.get("right") or value.get("target_column"), ""),
        "kind": _normalize_scalar(value.get("relationship_kind") or value.get("kind") or "UNKNOWN"),
    }
    payload = {key: value for key, value in shape.items() if value}
    signature = build_service_1_structural_digest_v1(payload=payload, prefix="rel_")
    return {"relationship_signature": signature, **payload}


def _relationship_fingerprint_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in value.items() if key != "relationship_signature"}


def _table_fingerprint_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "columns": list(value.get("column_signatures") or ()),
        "grain": value.get("grain_signature"),
        "keys": list(value.get("key_signatures") or ()),
    }


def _relationship_delta(prior: Mapping[str, Any], current: Mapping[str, Any], scope: list[str]) -> tuple[dict[str, Any], ...]:
    before = {str(item.get("relationship_signature")): item for item in prior.get("structural_relationship_signature") or () if isinstance(item, Mapping)}
    after = {str(item.get("relationship_signature")): item for item in current.get("structural_relationship_signature") or () if isinstance(item, Mapping)}
    if before == after:
        return ()
    changes: list[dict[str, Any]] = []
    for key in sorted(set(after) - set(before)):
        changes.append({"change": "ADDED", "relationship_signature": key, "current": after[key]})
    for key in sorted(set(before) - set(after)):
        changes.append({"change": "REMOVED", "relationship_signature": key, "prior": before[key]})
    for item in changes:
        _scope_add(scope, f"relationship:{item['relationship_signature']}")
    return tuple(changes)


def _classify_delta(*, prior: Mapping[str, Any], current: Mapping[str, Any], prior_fp: str, current_fp: str, added_tables: Sequence[Mapping[str, Any]], removed_tables: Sequence[Mapping[str, Any]], changed_tables: Sequence[Mapping[str, Any]], changed_columns: Sequence[Mapping[str, Any]], changed_grains: Sequence[Mapping[str, Any]], changed_keys: Sequence[Mapping[str, Any]], changed_relationships: Sequence[Mapping[str, Any]], matching_status: str) -> tuple[str, str]:
    if prior_fp == current_fp:
        return DRIFT_IDENTICAL, COMPATIBILITY_KNOWN
    if matching_status != TABLE_MATCH_READY:
        return DRIFT_UNRESOLVED, DRIFT_UNRESOLVED
    prior_family = str(prior.get("schema_family_ref") or UNKNOWN_FAMILY).strip() or UNKNOWN_FAMILY
    current_family = str(current.get("schema_family_ref") or UNKNOWN_FAMILY).strip() or UNKNOWN_FAMILY
    if prior_family == UNKNOWN_FAMILY or current_family == UNKNOWN_FAMILY:
        return DRIFT_UNRESOLVED, DRIFT_UNRESOLVED
    if prior_family != current_family:
        return DRIFT_NEW_FAMILY, COMPATIBILITY_NEW_FAMILY
    # A table record changes whenever a column is added/removed, but that
    # compatible column delta is not itself material drift.  Type/key/grain/
    # relationship changes and whole-table additions/removals remain material.
    material = bool(added_tables or removed_tables or changed_grains or changed_keys or changed_relationships)
    material = material or any(
        str(item.get("prior_signature", {}).get("inferred_type")) != str(item.get("current_signature", {}).get("inferred_type"))
        for item in changed_columns
    )
    if material:
        return DRIFT_MATERIAL, COMPATIBILITY_MATERIAL
    return DRIFT_COMPATIBLE_DELTA, COMPATIBILITY_KNOWN_DELTA


_D2_INSTANCE_REF_RE = re.compile(r"^lt_[0-9a-f]{24}_r[0-9]+$")


def _candidate_matching_identity(candidate: Mapping[str, Any], table_key: str) -> str | None:
    """Return only an explicitly stable ref, never D2's processing-order ref."""
    for field_name in ("matching_identity", "stable_table_ref", "table_match_key"):
        value = str(candidate.get(field_name) or "").strip()
        if value:
            return value
    if table_key and not _D2_INSTANCE_REF_RE.fullmatch(table_key):
        return table_key
    return None


def _table_records(identity: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in identity.get("logical_table_signatures") or ():
        if not isinstance(raw, Mapping):
            continue
        record = dict(raw)
        table_key = str(record.get("table_key") or record.get("instance_ref") or "").strip()
        if not table_key:
            continue
        record["table_key"] = table_key
        record["instance_ref"] = str(record.get("instance_ref") or table_key)
        matching_identity = str(record.get("matching_identity") or "").strip() or None
        if matching_identity is None and not _D2_INSTANCE_REF_RE.fullmatch(table_key):
            matching_identity = table_key
        record["matching_identity"] = matching_identity
        record["column_signatures"] = tuple(
            dict(item) for item in record.get("column_signatures") or () if isinstance(item, Mapping)
        )
        record["key_signatures"] = tuple(
            dict(item) for item in record.get("key_signatures") or () if isinstance(item, Mapping)
        )
        records.append(record)
    return records


def _record_scope_key(record: Mapping[str, Any]) -> str:
    matching_identity = str(record.get("matching_identity") or "").strip()
    if matching_identity:
        return matching_identity
    signature = str(record.get("table_signature") or record.get("structural_table_signature") or "").strip()
    if signature:
        return f"structural:{signature}"
    return str(record.get("instance_ref") or record.get("table_key") or "").strip()


def _match_table_records(
    prior: Sequence[Mapping[str, Any]],
    current: Sequence[Mapping[str, Any]],
) -> tuple[list[tuple[int, int, str]], set[int], set[int], str, str | None]:
    """Match tables without treating D2 region indexes as identity.

    Stable refs and exact structural signatures are preferred.  A modified
    table may be paired only when common structural evidence gives one unique,
    reciprocal best match.  Ties remain unresolved rather than guessed.
    """
    matches: list[tuple[int, int, str]] = []
    available_prior = set(range(len(prior)))
    available_current = set(range(len(current)))
    blocked_prior: set[int] = set()
    blocked_current: set[int] = set()
    reasons: list[str] = []

    def consume(prior_index: int, current_index: int, match_key: str) -> None:
        matches.append((prior_index, current_index, match_key))
        available_prior.discard(prior_index)
        available_current.discard(current_index)

    # A caller-provided matching identity is authoritative for comparison,
    # while D2-generated logical_table_id values are intentionally absent.
    for identity in sorted(
        {
            str(item.get("matching_identity"))
            for item in list(prior) + list(current)
            if str(item.get("matching_identity") or "").strip()
        }
    ):
        prior_indices = [index for index in available_prior if prior[index].get("matching_identity") == identity]
        current_indices = [index for index in available_current if current[index].get("matching_identity") == identity]
        if len(prior_indices) == 1 and len(current_indices) == 1:
            consume(prior_indices[0], current_indices[0], identity)
        elif prior_indices and current_indices:
            blocked_prior.update(prior_indices)
            blocked_current.update(current_indices)
            reasons.append(f"AMBIGUOUS_STABLE_IDENTITY:{identity}")

    # Exact structural matches are safe even when the instance refs differ.
    for signature in sorted(
        {
            str(item.get("table_signature") or "")
            for item in list(prior) + list(current)
            if str(item.get("table_signature") or "")
        }
    ):
        prior_indices = [index for index in available_prior if index not in blocked_prior and prior[index].get("table_signature") == signature]
        current_indices = [index for index in available_current if index not in blocked_current and current[index].get("table_signature") == signature]
        if len(prior_indices) == 1 and len(current_indices) == 1:
            consume(prior_indices[0], current_indices[0], f"structural:{signature}")
        elif prior_indices and current_indices and (len(prior_indices) > 1 or len(current_indices) > 1):
            blocked_prior.update(prior_indices)
            blocked_current.update(current_indices)
            reasons.append(f"AMBIGUOUS_STRUCTURAL_SIGNATURE:{signature}")

    # Modified tables: score only common structural evidence and require a
    # unique reciprocal best match.  Region order and sheet names are absent.
    while True:
        scores: dict[tuple[int, int], tuple[int, int, int, float]] = {}
        for prior_index in sorted(available_prior - blocked_prior):
            for current_index in sorted(available_current - blocked_current):
                score = _table_match_score(prior[prior_index], current[current_index])
                if score is not None:
                    scores[(prior_index, current_index)] = score
        if not scores:
            break
        current_best: dict[int, list[int]] = {}
        for current_index in sorted({pair[1] for pair in scores}):
            candidates = [pair for pair in scores if pair[1] == current_index]
            best_score = max(scores[pair] for pair in candidates)
            current_best[current_index] = [pair[0] for pair in candidates if scores[pair] == best_score]
        prior_best: dict[int, list[int]] = {}
        for prior_index in sorted({pair[0] for pair in scores}):
            candidates = [pair for pair in scores if pair[0] == prior_index]
            best_score = max(scores[pair] for pair in candidates)
            prior_best[prior_index] = [pair[1] for pair in candidates if scores[pair] == best_score]
        mutual = [
            (prior_index, current_index)
            for current_index, prior_indices in current_best.items()
            if len(prior_indices) == 1
            for prior_index in prior_indices
            if len(prior_best.get(prior_index, ())) == 1
            and prior_best[prior_index][0] == current_index
        ]
        ambiguous_current = [index for index, candidates in current_best.items() if len(candidates) > 1]
        ambiguous_prior = [index for index, candidates in prior_best.items() if len(candidates) > 1]
        if ambiguous_current or ambiguous_prior:
            blocked_current.update(ambiguous_current)
            blocked_prior.update(ambiguous_prior)
            reasons.append("AMBIGUOUS_STRUCTURAL_OVERLAP")
        if not mutual:
            break
        for prior_index, current_index in sorted(mutual):
            if prior_index in available_prior and current_index in available_current:
                consume(prior_index, current_index, _pair_scope_key(prior[prior_index], current[current_index]))

    unmatched_prior = (available_prior - blocked_prior)
    unmatched_current = (available_current - blocked_current)
    status = TABLE_MATCH_UNRESOLVED if reasons else TABLE_MATCH_READY
    reason = ";".join(sorted(set(reasons))) or None
    return matches, unmatched_prior, unmatched_current, status, reason


def _table_match_score(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[int, int, int, float] | None:
    before_columns = {str(item.get("normalized_header")) for item in before.get("column_signatures") or () if isinstance(item, Mapping)}
    after_columns = {str(item.get("normalized_header")) for item in after.get("column_signatures") or () if isinstance(item, Mapping)}
    common = before_columns & after_columns
    if not common:
        return None
    before_keys = _key_column_names(before)
    after_keys = _key_column_names(after)
    key_overlap = len(before_keys & after_keys)
    if len(common) < 2 and key_overlap == 0:
        return None
    union = before_columns | after_columns
    jaccard = len(common) / len(union) if union else 0.0
    grain_same = int(before.get("grain_signature") == after.get("grain_signature"))
    return len(common), key_overlap, grain_same, round(jaccard, 12)


def _key_column_names(record: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in record.get("key_signatures") or ():
        if isinstance(key, Mapping):
            names.update(str(value) for value in key.get("columns") or ())
    return names


def _pair_scope_key(before: Mapping[str, Any], after: Mapping[str, Any]) -> str:
    before_identity = str(before.get("matching_identity") or "").strip()
    after_identity = str(after.get("matching_identity") or "").strip()
    if before_identity and before_identity == after_identity:
        return before_identity
    if before.get("table_signature") == after.get("table_signature"):
        return f"structural:{before.get('table_signature')}"
    before_columns = {str(item.get("normalized_header")) for item in before.get("column_signatures") or () if isinstance(item, Mapping)}
    after_columns = {str(item.get("normalized_header")) for item in after.get("column_signatures") or () if isinstance(item, Mapping)}
    payload = {
        "common_columns": sorted(before_columns & after_columns),
        "key_columns": sorted(_key_column_names(before) & _key_column_names(after)),
        "grain": before.get("grain_signature") if before.get("grain_signature") == after.get("grain_signature") else None,
    }
    return build_service_1_structural_digest_v1(payload=payload, prefix="match_")


def _identity_mapping(identity: Mapping[str, Any] | WorkbookSchemaIdentityV1) -> Mapping[str, Any]:
    return identity.to_dict() if isinstance(identity, WorkbookSchemaIdentityV1) else identity


def _normalize_header(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _normalize_scalar(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _normalize_column_ref(value: Any, table_key: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parts = [part.strip() for part in raw.replace("/", ".").split(".") if part.strip()]
    if table_key and table_key in parts:
        parts = parts[parts.index(table_key) + 1 :]
    return _normalize_header(parts[-1] if parts else raw)


def _canonical_key(value: Mapping[str, Any]) -> str:
    return repr(sorted((str(key), repr(value)) for key, value in value.items()))


def _scope_add(scope: list[str], *values: str) -> None:
    for value in values:
        if value and value not in scope:
            scope.append(value)


def _as_jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_as_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_as_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _as_jsonable(item) for key, item in value.items()}
    return value


def _unresolved(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_UNRESOLVED,
        "blocked_reason": reason,
        "schema_fingerprint": None,
        "schema_family_ref": UNKNOWN_FAMILY,
        "schema_version_logical": None,
        "logical_table_signatures": [],
        "structural_relationship_signature": [],
        "provenance": {},
        "runtime_authorized": False,
        "semantic_rebind_authorized": False,
        "family_auto_reuse_authorized": False,
        "computability_authorized": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    result = _unresolved(reason)
    result["status"] = STATUS_BLOCKED
    return result


__all__ = [
    "SCHEMA_VERSION",
    "DELTA_SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_UNRESOLVED",
    "STATUS_BLOCKED",
    "UNKNOWN_FAMILY",
    "DRIFT_IDENTICAL",
    "DRIFT_COMPATIBLE_DELTA",
    "DRIFT_MATERIAL",
    "DRIFT_NEW_FAMILY",
    "DRIFT_UNRESOLVED",
    "COMPATIBILITY_KNOWN",
    "COMPATIBILITY_KNOWN_DELTA",
    "COMPATIBILITY_MATERIAL",
    "COMPATIBILITY_NEW_FAMILY",
    "COLUMN_ORDER_POLICY",
    "SCHEMA_DRIFT_IS_DELTA",
    "TABLE_MATCH_READY",
    "TABLE_MATCH_UNRESOLVED",
    "WorkbookSchemaIdentityV1",
    "WorkbookSchemaDeltaV1",
    "Service1WorkbookSchemaIdentityV1",
    "Service1WorkbookSchemaDeltaV1",
    "build_service_1_workbook_schema_identity_v1",
    "build_service_1_workbook_schema_delta_v1",
    "compare_service_1_workbook_schema_identities_v1",
    "compare_service_1_workbook_schema_delta_v1",
    "build_service_1_schema_delta_v1",
]

"""Append-only tenant store for Servicio 1 schema-family memory records.

Schema-family memory shares the canonical tenant memory JSONL with owner-
confirmed semantic contracts.  This module owns only schema-family persistence;
it does not reinterpret semantic contracts or create a second memory artifact.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from pymia.smartpyme.service_1_tenant_memory_artifact_v1 import (
    service_1_tenant_memory_artifact_path_v1,
)
from pymia.smartpyme.service_1_tenant_schema_family_memory_v1 import (
    RECORD_KIND,
    Service1TenantSchemaFamilyMemoryErrorV1,
    Service1TenantSchemaFamilyMemoryV1,
    service_1_tenant_schema_family_memory_from_mapping_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
    service_1_tenant_semantic_contract_from_mapping_v1,
)


@dataclass(frozen=True)
class Service1TenantSchemaFamilyMemoryAppendResultV1:
    status: str
    record_id: str
    path: Path


def _read_records(
    path: Path,
    tenant_id: str,
) -> tuple[Service1TenantSchemaFamilyMemoryV1, ...]:
    if not path.exists():
        return ()
    records: list[Service1TenantSchemaFamilyMemoryV1] = []
    seen_by_id: dict[str, Service1TenantSchemaFamilyMemoryV1] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        try:
            raw = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise Service1TenantSchemaFamilyMemoryErrorV1(
                "BLOCKED_SCHEMA_MEMORY_INVALID",
                f"malformed tenant memory record at line {line_number}",
            ) from exc
        if not isinstance(raw, dict):
            raise Service1TenantSchemaFamilyMemoryErrorV1(
                "BLOCKED_SCHEMA_MEMORY_INVALID",
                f"tenant memory line {line_number} is not an object",
            )

        record_kind = str(raw.get("record_kind") or "").strip()
        if not record_kind:
            try:
                contract = service_1_tenant_semantic_contract_from_mapping_v1(raw)
            except Service1TenantSemanticContractErrorV1 as exc:
                raise Service1TenantSchemaFamilyMemoryErrorV1(
                    "BLOCKED_SCHEMA_MEMORY_INVALID",
                    f"invalid semantic memory record at line {line_number}",
                ) from exc
            if contract.tenant_id != tenant_id:
                raise Service1TenantSchemaFamilyMemoryErrorV1(
                    "BLOCKED_CROSS_TENANT_ACCESS",
                    "stored semantic contract does not belong to requested tenant",
                )
            continue
        if record_kind != RECORD_KIND:
            raise Service1TenantSchemaFamilyMemoryErrorV1(
                "BLOCKED_SCHEMA_MEMORY_INVALID",
                f"unknown tenant memory record kind at line {line_number}",
            )

        record = service_1_tenant_schema_family_memory_from_mapping_v1(raw)
        if record.tenant_id != tenant_id:
            raise Service1TenantSchemaFamilyMemoryErrorV1(
                "BLOCKED_CROSS_TENANT_ACCESS",
                "stored schema-family memory does not belong to requested tenant",
            )
        if record.record_id in seen_by_id:
            if seen_by_id[record.record_id].to_dict() != record.to_dict():
                raise Service1TenantSchemaFamilyMemoryErrorV1(
                    "BLOCKED_SCHEMA_MEMORY_ID_CONFLICT",
                    "stored schema memory id has conflicting payloads",
                )
            continue
        if record.family_revision > 1:
            prior = seen_by_id.get(record.prior_record_id or "")
            if (
                prior is None
                or prior.tenant_id != record.tenant_id
                or prior.schema_family_ref != record.schema_family_ref
                or prior.family_revision + 1 != record.family_revision
            ):
                raise Service1TenantSchemaFamilyMemoryErrorV1(
                    "BLOCKED_SCHEMA_MEMORY_REVISION_INVALID",
                    "stored schema memory revision does not follow prior family record",
                )
        seen_by_id[record.record_id] = record
        records.append(record)
    return tuple(records)


def append_service_1_tenant_schema_family_memory_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
    record: Service1TenantSchemaFamilyMemoryV1 | Mapping[str, object],
) -> Service1TenantSchemaFamilyMemoryAppendResultV1:
    path = service_1_tenant_memory_artifact_path_v1(
        base_dir=base_dir,
        tenant_id=tenant_id,
    )
    if isinstance(record, Service1TenantSchemaFamilyMemoryV1):
        raw_payload = record.to_dict()
    elif isinstance(record, Mapping):
        raw_payload = dict(record)
    else:
        raise Service1TenantSchemaFamilyMemoryErrorV1(
            "BLOCKED_SCHEMA_MEMORY_INVALID",
            "record must be a schema-family memory record or mapping",
        )

    existing = _read_records(path, tenant_id)
    requested_id = str(raw_payload.get("record_id") or "").strip()
    for stored in existing:
        if stored.record_id != requested_id:
            continue
        if stored.to_dict() == raw_payload:
            return Service1TenantSchemaFamilyMemoryAppendResultV1(
                status="TENANT_SCHEMA_FAMILY_MEMORY_ALREADY_RECORDED",
                record_id=stored.record_id,
                path=path,
            )
        raise Service1TenantSchemaFamilyMemoryErrorV1(
            "BLOCKED_SCHEMA_MEMORY_ID_CONFLICT",
            "schema memory id already exists with different content",
        )

    validated = service_1_tenant_schema_family_memory_from_mapping_v1(raw_payload)
    if validated.tenant_id != tenant_id:
        raise Service1TenantSchemaFamilyMemoryErrorV1(
            "BLOCKED_CROSS_TENANT_ACCESS",
            "argument tenant_id does not match schema memory tenant_id",
        )
    if validated.family_revision > 1:
        prior = next(
            (item for item in existing if item.record_id == validated.prior_record_id),
            None,
        )
        if (
            prior is None
            or prior.schema_family_ref != validated.schema_family_ref
            or prior.family_revision + 1 != validated.family_revision
        ):
            raise Service1TenantSchemaFamilyMemoryErrorV1(
                "BLOCKED_SCHEMA_MEMORY_REVISION_INVALID",
                "prior schema family record must already exist in the same lineage",
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        validated.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return Service1TenantSchemaFamilyMemoryAppendResultV1(
        status="TENANT_SCHEMA_FAMILY_MEMORY_RECORDED",
        record_id=validated.record_id,
        path=path,
    )


def list_service_1_tenant_schema_family_memory_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
) -> tuple[Service1TenantSchemaFamilyMemoryV1, ...]:
    path = service_1_tenant_memory_artifact_path_v1(
        base_dir=base_dir,
        tenant_id=tenant_id,
    )
    return _read_records(path, tenant_id)


def load_service_1_tenant_schema_family_memory_by_id_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
    record_id: str,
) -> Service1TenantSchemaFamilyMemoryV1 | None:
    requested_id = str(record_id or "").strip()
    if not requested_id:
        raise Service1TenantSchemaFamilyMemoryErrorV1(
            "BLOCKED_SCHEMA_MEMORY_INVALID",
            "record_id is required",
        )
    return next(
        (
            record
            for record in list_service_1_tenant_schema_family_memory_v1(
                base_dir=base_dir,
                tenant_id=tenant_id,
            )
            if record.record_id == requested_id
        ),
        None,
    )


__all__ = [
    "Service1TenantSchemaFamilyMemoryAppendResultV1",
    "append_service_1_tenant_schema_family_memory_v1",
    "list_service_1_tenant_schema_family_memory_v1",
    "load_service_1_tenant_schema_family_memory_by_id_v1",
]

"""Append-only tenant store for Servicio 1 semantic contracts."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
    Service1TenantSemanticContractV1,
    service_1_tenant_semantic_contract_from_mapping_v1,
)
from pymia.smartpyme.storage import resolve_tenant_storage_root

_ARTIFACT_NAME = "tenant_semantic_contracts.jsonl"


@dataclass(frozen=True)
class Service1TenantSemanticContractAppendResultV1:
    status: str
    contract_id: str
    path: Path


def _artifact_path(base_dir: str | Path, tenant_id: str) -> Path:
    return resolve_tenant_storage_root(base_dir, tenant_id) / _ARTIFACT_NAME


def _payload(contract: Service1TenantSemanticContractV1 | Mapping[str, object]) -> dict[str, object]:
    if isinstance(contract, Service1TenantSemanticContractV1):
        return contract.to_dict()
    if isinstance(contract, Mapping):
        return dict(contract)
    raise Service1TenantSemanticContractErrorV1(
        "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
        "contract must be a V1 contract or mapping",
    )


def _read_contracts(path: Path, tenant_id: str) -> tuple[Service1TenantSemanticContractV1, ...]:
    if not path.exists():
        return ()
    contracts: list[Service1TenantSemanticContractV1] = []
    seen_by_id: dict[str, Service1TenantSemanticContractV1] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            raw = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise Service1TenantSemanticContractErrorV1(
                "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
                f"malformed tenant semantic contract at line {line_number}",
            ) from exc
        if not isinstance(raw, dict):
            raise Service1TenantSemanticContractErrorV1(
                "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
                f"tenant semantic contract line {line_number} is not an object",
            )
        contract = service_1_tenant_semantic_contract_from_mapping_v1(raw)
        if contract.tenant_id != tenant_id:
            raise Service1TenantSemanticContractErrorV1(
                "BLOCKED_CROSS_TENANT_ACCESS",
                "stored contract does not belong to requested tenant",
            )
        if contract.contract_id in seen_by_id:
            prior_same_id = seen_by_id[contract.contract_id]
            if prior_same_id.to_dict() != contract.to_dict():
                raise Service1TenantSemanticContractErrorV1(
                    "BLOCKED_CONTRACT_ID_CONFLICT",
                    "stored contract id has conflicting payloads",
                )
            continue
        if contract.revision > 1:
            prior = seen_by_id.get(contract.supersedes_contract_id or "")
            if (
                prior is None
                or prior.tenant_id != contract.tenant_id
                or prior.mapping_series_id != contract.mapping_series_id
                or prior.revision + 1 != contract.revision
            ):
                raise Service1TenantSemanticContractErrorV1(
                    "BLOCKED_SUPERSESSION_MISMATCH",
                    "stored revision does not follow an earlier contract in the same series",
                )
        seen_by_id[contract.contract_id] = contract
        contracts.append(contract)
    return tuple(contracts)


def append_service_1_tenant_semantic_contract_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
    contract: Service1TenantSemanticContractV1 | Mapping[str, object],
) -> Service1TenantSemanticContractAppendResultV1:
    path = _artifact_path(base_dir, tenant_id)
    raw_payload = _payload(contract)
    requested_contract_id = str(raw_payload.get("contract_id") or "")
    existing = _read_contracts(path, tenant_id)

    for recorded in existing:
        if recorded.contract_id != requested_contract_id:
            continue
        if recorded.to_dict() == raw_payload:
            return Service1TenantSemanticContractAppendResultV1(
                status="TENANT_SEMANTIC_CONTRACT_ALREADY_RECORDED",
                contract_id=recorded.contract_id,
                path=path,
            )
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_CONTRACT_ID_CONFLICT",
            "contract id is already recorded with different content",
        )

    validated = service_1_tenant_semantic_contract_from_mapping_v1(raw_payload)
    if validated.tenant_id != tenant_id:
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_CROSS_TENANT_ACCESS",
            "argument tenant_id does not match contract tenant_id",
        )
    if validated.revision > 1:
        prior = next(
            (
                item
                for item in existing
                if item.contract_id == validated.supersedes_contract_id
            ),
            None,
        )
        if (
            prior is None
            or prior.mapping_series_id != validated.mapping_series_id
            or prior.revision + 1 != validated.revision
        ):
            raise Service1TenantSemanticContractErrorV1(
                "BLOCKED_SUPERSESSION_MISMATCH",
                "prior contract must already exist in this tenant and series",
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
    return Service1TenantSemanticContractAppendResultV1(
        status="TENANT_SEMANTIC_CONTRACT_RECORDED",
        contract_id=validated.contract_id,
        path=path,
    )


def list_service_1_tenant_semantic_contracts_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
) -> tuple[Service1TenantSemanticContractV1, ...]:
    path = _artifact_path(base_dir, tenant_id)
    return _read_contracts(path, tenant_id)


def load_service_1_tenant_semantic_contract_by_id_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
    contract_id: str,
) -> Service1TenantSemanticContractV1 | None:
    requested_id = str(contract_id or "").strip()
    if not requested_id:
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
            "contract_id is required",
        )
    return next(
        (
            contract
            for contract in list_service_1_tenant_semantic_contracts_v1(
                base_dir=base_dir,
                tenant_id=tenant_id,
            )
            if contract.contract_id == requested_id
        ),
        None,
    )


__all__ = [
    "Service1TenantSemanticContractAppendResultV1",
    "append_service_1_tenant_semantic_contract_v1",
    "list_service_1_tenant_semantic_contracts_v1",
    "load_service_1_tenant_semantic_contract_by_id_v1",
]

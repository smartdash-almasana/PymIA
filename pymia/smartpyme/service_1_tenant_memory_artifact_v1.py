"""Shared physical artifact location for Servicio 1 tenant memory.

This module owns no memory semantics.  It exists only so semantic-confirmation
records and schema-family records share one append-only tenant artifact without
duplicating or drifting the physical storage contract.
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

from pymia.smartpyme.storage import resolve_tenant_storage_root

TENANT_MEMORY_ARTIFACT_NAME: Final[str] = "tenant_semantic_contracts.jsonl"


def service_1_tenant_memory_artifact_path_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
) -> Path:
    return resolve_tenant_storage_root(base_dir, tenant_id) / TENANT_MEMORY_ARTIFACT_NAME


__all__ = [
    "TENANT_MEMORY_ARTIFACT_NAME",
    "service_1_tenant_memory_artifact_path_v1",
]

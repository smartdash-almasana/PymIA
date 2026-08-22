"""Legacy compatibility wrapper for the canonical Servicio 1 region evidence builder.

D7 productive code must import ``service_1_region_evidence_v1`` directly.
This wrapper remains only for pre-D7 callers/tests and has a delete condition:
remove once no compatibility caller imports this module.
"""
from __future__ import annotations

from typing import Any

from pymia.smartpyme.service_1_region_evidence_v1 import (
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_UNRESOLVED,
    build_service_1_region_evidence_from_canonical_ingestion_v1 as _build_canonical,
)

SCHEMA_VERSION = "SERVICE_1_CANONICAL_INGESTION_TO_REGION_EVIDENCE_ADAPTER_V1"


def build_service_1_region_evidence_from_canonical_ingestion_v1(**kwargs: Any) -> dict[str, Any]:
    result = dict(_build_canonical(**kwargs))
    result["schema_version"] = SCHEMA_VERSION
    result["temporary_adapter"] = True
    result["canonical_region_evidence"] = True
    return result


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_UNRESOLVED",
    "STATUS_BLOCKED",
    "build_service_1_region_evidence_from_canonical_ingestion_v1",
]

"""Minimal headless JSON contract for Service 1 around the canonical Product Root.

VTV (or any headless caller) sends a versioned JSON request, this module
validates it fail-closed, builds the canonical F12 command
(WorkbookAnalysisExecuteRequestV1), runs it through the UNCHANGED Product
Root (run_service_1_product_pipeline_v1), and projects the packet back to a
versioned JSON response preserving ResultSet identity and integrity fields.

Scope: F12 analysis execution only. No HTTP endpoint, no UI, no math or
semantic changes. Tenant identity is never defaulted or invented: absent
identity stays absent (the root decides persistence); a present JSON mapping
is coerced with service_1_tenant_identity_contract_from_mapping_v1 only, and
any coercion failure blocks fail-closed before reaching the root.
Cryptographic ResultSet verification stays inside Service1ResultMemoryRecordV1;
this boundary only asserts structural consistency (digest present and
artifact_ref coherent) and byte-identical passthrough.
"""
from __future__ import annotations

import json
from typing import Any, Mapping

from pymia.smartpyme.service_1_computability_v1 import (
    CONFIRMED_BINDINGS_STATUS,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    Service1ProductExecutionDependenciesV1,
    WorkbookAnalysisExecuteRequestV1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    Service1TenantIdentityContractV1,
    service_1_tenant_identity_contract_from_mapping_v1,
)

HEADLESS_REQUEST_SCHEMA_VERSION = "SERVICE_1_HEADLESS_REQUEST_V1"
HEADLESS_RESPONSE_SCHEMA_VERSION = "SERVICE_1_HEADLESS_RESPONSE_V1"
HEADLESS_SOURCE = "SERVICE_1_HEADLESS_CONTRACT_V1"

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "analysis_id",
        "ingestion_output",
        "confirmed_bindings",
        "tenant_identity_contract",
    }
)


def _blocked(reason: str, analysis_id: str = "") -> dict[str, Any]:
    return {
        "schema_version": HEADLESS_RESPONSE_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "status": "BLOCKED",
        "blocked_reason": reason,
        "title": None,
        "question": None,
        "result_set": None,
        "findings": [],
        "outcome": None,
        "result_memory": None,
        "integrity": None,
        "provenance": {"source": HEADLESS_SOURCE},
    }


def parse_service_1_headless_request_v1(
    payload: Any,
) -> tuple[WorkbookAnalysisExecuteRequestV1 | None, dict[str, Any] | None]:
    """Validate a headless JSON request fail-closed.

    Returns (request, None) on success or (None, blocked_response) on any
    invalid input. Never raises for malformed caller input.
    """
    if not isinstance(payload, Mapping):
        return None, _blocked("HEADLESS_REQUEST_MUST_BE_MAPPING")
    unknown = set(payload.keys()) - _REQUEST_FIELDS
    if unknown:
        return None, _blocked("HEADLESS_REQUEST_UNKNOWN_FIELDS")
    if payload.get("schema_version") != HEADLESS_REQUEST_SCHEMA_VERSION:
        return None, _blocked("HEADLESS_REQUEST_VERSION_INVALID")
    analysis_id = payload.get("analysis_id")
    if not isinstance(analysis_id, str) or not analysis_id.strip():
        return None, _blocked("HEADLESS_ANALYSIS_ID_REQUIRED")
    ingestion_output = payload.get("ingestion_output")
    if not isinstance(ingestion_output, Mapping):
        return None, _blocked("HEADLESS_INGESTION_REQUIRED", analysis_id.strip())
    confirmed_bindings = payload.get("confirmed_bindings")
    if not isinstance(confirmed_bindings, Mapping):
        return None, _blocked("HEADLESS_CONFIRMED_BINDINGS_REQUIRED", analysis_id.strip())
    if confirmed_bindings.get("status") != CONFIRMED_BINDINGS_STATUS:
        return None, _blocked("HEADLESS_CONFIRMED_BINDINGS_REQUIRED", analysis_id.strip())
    identity = payload.get("tenant_identity_contract")
    if identity is not None:
        if not isinstance(identity, Mapping):
            return None, _blocked("HEADLESS_IDENTITY_INVALID", analysis_id.strip())
        tenant_id = identity.get("tenant_id")
        if tenant_id is not None and (not isinstance(tenant_id, str) or not tenant_id.strip()):
            return None, _blocked("HEADLESS_IDENTITY_INVALID", analysis_id.strip())
    request = WorkbookAnalysisExecuteRequestV1(
        ingestion_output=dict(ingestion_output),
        confirmed_bindings=dict(confirmed_bindings),
        analysis_id=analysis_id.strip(),
        tenant_identity_contract=dict(identity) if isinstance(identity, Mapping) else None,
    )
    return request, None


def _integrity_check(packet: Mapping[str, Any]) -> dict[str, Any] | None:
    """Structural ResultSet integrity check (no crypto duplication).

    Returns None when the packet carries no digest to check (the root itself
    allows digest-less summaries, e.g. NOT_PERSISTED). Returns a BLOCKED
    reason string only on contradiction (present-but-incoherent fields).
    """
    memory = packet.get("result_memory")
    if not isinstance(memory, Mapping):
        return None
    digest = memory.get("result_set_integrity_digest")
    artifact_ref = memory.get("artifact_ref")
    if digest is None and artifact_ref is None:
        return None
    if not isinstance(digest, str) or not digest.strip():
        return "HEADLESS_RESULT_INTEGRITY_DRIFT"
    if artifact_ref != f"resultset:sha256:{digest}":
        return "HEADLESS_RESULT_INTEGRITY_DRIFT"
    return None


def build_service_1_headless_response_v1(
    *,
    request_analysis_id: str,
    packet: Any,
) -> dict[str, Any]:
    """Project a Product Root packet to a versioned JSON response fail-closed."""
    analysis_id = str(request_analysis_id or "").strip()
    if not isinstance(packet, Mapping):
        return _blocked("HEADLESS_PACKET_INVALID", analysis_id)
    status = packet.get("status")
    if status != "READY":
        return {
            **_blocked(str(packet.get("blocked_reason") or "HEADLESS_UPSTREAM_BLOCKED"), analysis_id),
            "title": packet.get("title"),
            "question": packet.get("question"),
        }
    drift = _integrity_check(packet)
    if drift is not None:
        return _blocked(drift, analysis_id)
    memory = packet.get("result_memory")
    digest_present = isinstance(memory, Mapping) and isinstance(
        memory.get("result_set_integrity_digest"), str
    )
    response = {
        "schema_version": HEADLESS_RESPONSE_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "status": "READY",
        "blocked_reason": None,
        "title": packet.get("title"),
        "question": packet.get("question"),
        "result_set": packet.get("result_set"),
        "findings": packet.get("findings") if isinstance(packet.get("findings"), list) else [],
        "outcome": packet.get("outcome"),
        "result_memory": dict(memory) if isinstance(memory, Mapping) else None,
        "integrity": {
            "digest_present": digest_present,
            "artifact_ref_coherent": digest_present,
        },
        "provenance": {
            "source": HEADLESS_SOURCE,
            "root_schema": str(packet.get("schema_version") or ""),
        },
    }
    try:
        json.dumps(response)
    except (TypeError, ValueError):
        return _blocked("HEADLESS_RESPONSE_NOT_SERIALIZABLE", analysis_id)
    return response


def execute_service_1_headless_json_v1(
    payload: Any,
    *,
    dependencies: Service1ProductExecutionDependenciesV1 | None = None,
) -> dict[str, Any]:
    """Parse, execute through the canonical Product Root, and respond.

    Invalid requests fail closed without reaching the root. Valid requests
    run the UNCHANGED root; its packet (READY or BLOCKED) is projected back.
    """
    request, blocked = parse_service_1_headless_request_v1(payload)
    if blocked is not None:
        try:
            json.dumps(blocked)
        except (TypeError, ValueError):
            return _blocked("HEADLESS_RESPONSE_NOT_SERIALIZABLE")
        return blocked
    assert request is not None
    identity = request.tenant_identity_contract
    if isinstance(identity, Mapping):
        try:
            coerced = service_1_tenant_identity_contract_from_mapping_v1(identity)
        except Exception:
            return _blocked("HEADLESS_IDENTITY_COERCION_FAILED", request.analysis_id)
        request = WorkbookAnalysisExecuteRequestV1(
            ingestion_output=request.ingestion_output,
            confirmed_bindings=request.confirmed_bindings,
            analysis_id=request.analysis_id,
            tenant_identity_contract=coerced,
        )
    elif identity is not None and not isinstance(identity, Service1TenantIdentityContractV1):
        return _blocked("HEADLESS_IDENTITY_COERCION_FAILED", request.analysis_id)
    packet = run_service_1_product_pipeline_v1(request, dependencies=dependencies)
    return build_service_1_headless_response_v1(
        request_analysis_id=request.analysis_id,
        packet=packet,
    )


__all__ = [
    "HEADLESS_REQUEST_SCHEMA_VERSION",
    "HEADLESS_RESPONSE_SCHEMA_VERSION",
    "HEADLESS_SOURCE",
    "build_service_1_headless_response_v1",
    "execute_service_1_headless_json_v1",
    "parse_service_1_headless_request_v1",
]

"""Focal contract tests for the Service 1 headless JSON boundary.

Hermetic by design: parse/reject/response paths need no fixtures and never
touch math, semantics, or persistence. The single executor test reaches the
real Product Root only through fail-closed paths (no math executes).
"""
from __future__ import annotations

import json
from typing import Any

from pymia.smartpyme.service_1_computability_v1 import CONFIRMED_BINDINGS_STATUS
from pymia.smartpyme.service_1_headless_contract_v1 import (
    HEADLESS_REQUEST_SCHEMA_VERSION,
    HEADLESS_RESPONSE_SCHEMA_VERSION,
    build_service_1_headless_response_v1,
    execute_service_1_headless_json_v1,
    parse_service_1_headless_request_v1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    WorkbookAnalysisExecuteRequestV1,
)


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": HEADLESS_REQUEST_SCHEMA_VERSION,
        "analysis_id": "sales_total",
        "ingestion_output": {"workbook_context": {"case_id": "case-headless-001"}},
        "confirmed_bindings": {"status": CONFIRMED_BINDINGS_STATUS},
        "tenant_identity_contract": {"tenant_id": "tenant-headless-001"},
    }
    payload.update(overrides)
    return payload


def test_parse_valid_request_builds_canonical_f12_command() -> None:
    request, blocked = parse_service_1_headless_request_v1(_valid_payload())
    assert blocked is None
    assert isinstance(request, WorkbookAnalysisExecuteRequestV1)
    assert request is not None
    assert request.analysis_id == "sales_total"
    assert request.ingestion_output["workbook_context"]["case_id"] == "case-headless-001"
    assert request.confirmed_bindings["status"] == CONFIRMED_BINDINGS_STATUS
    assert request.tenant_identity_contract == {"tenant_id": "tenant-headless-001"}


def test_parse_absent_identity_stays_absent() -> None:
    payload = _valid_payload()
    del payload["tenant_identity_contract"]
    request, blocked = parse_service_1_headless_request_v1(payload)
    assert blocked is None
    assert request is not None
    assert request.tenant_identity_contract is None


def test_parse_rejects_invalid_input_fail_closed() -> None:
    cases: list[tuple[Any, str]] = [
        (None, "HEADLESS_REQUEST_MUST_BE_MAPPING"),
        ([], "HEADLESS_REQUEST_MUST_BE_MAPPING"),
        (_valid_payload(schema_version="WRONG"), "HEADLESS_REQUEST_VERSION_INVALID"),
        (_valid_payload(analysis_id=""), "HEADLESS_ANALYSIS_ID_REQUIRED"),
        (_valid_payload(analysis_id="   "), "HEADLESS_ANALYSIS_ID_REQUIRED"),
        (_valid_payload(analysis_id=None), "HEADLESS_ANALYSIS_ID_REQUIRED"),
        (_valid_payload(ingestion_output="nope"), "HEADLESS_INGESTION_REQUIRED"),
        (_valid_payload(confirmed_bindings={}), "HEADLESS_CONFIRMED_BINDINGS_REQUIRED"),
        (
            _valid_payload(confirmed_bindings={"status": "DRAFT"}),
            "HEADLESS_CONFIRMED_BINDINGS_REQUIRED",
        ),
        (
            _valid_payload(tenant_identity_contract="tenant-x"),
            "HEADLESS_IDENTITY_INVALID",
        ),
        (
            _valid_payload(tenant_identity_contract={"tenant_id": "  "}),
            "HEADLESS_IDENTITY_INVALID",
        ),
        (_valid_payload(extra_field=1), "HEADLESS_REQUEST_UNKNOWN_FIELDS"),
    ]
    for payload, reason in cases:
        request, blocked = parse_service_1_headless_request_v1(payload)
        assert request is None, payload
        assert blocked is not None, payload
        assert blocked["status"] == "BLOCKED", payload
        assert blocked["blocked_reason"] == reason, payload
        assert blocked["schema_version"] == HEADLESS_RESPONSE_SCHEMA_VERSION
        json.dumps(blocked)


def test_execute_reaches_preserved_root_and_blocks_without_math() -> None:
    response = execute_service_1_headless_json_v1(_valid_payload())
    assert response["schema_version"] == HEADLESS_RESPONSE_SCHEMA_VERSION
    assert response["analysis_id"] == "sales_total"
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"]
    json.dumps(response)


def test_execute_garbage_never_reaches_root() -> None:
    response = execute_service_1_headless_json_v1({"schema_version": "NOPE"})
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"] == "HEADLESS_REQUEST_VERSION_INVALID"


def _complete_identity() -> dict[str, Any]:
    from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
        build_service_1_tenant_identity_contract_v1,
    )

    return build_service_1_tenant_identity_contract_v1(
        tenant_id="tenant-coercion-1",
        case_id="case-coercion-1",
        owner_actor_id="owner-1",
        owner_actor_role="OWNER",
        source_system_ref="E2E",
        source_context_ref="E2E_SMOKE",
        workbook_ref="cafeteria_abc.xlsx",
    ).to_dict()


def test_execute_coerces_complete_identity_before_root() -> None:
    response = execute_service_1_headless_json_v1(_valid_payload(tenant_identity_contract=_complete_identity()))
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"] not in (
        "HEADLESS_IDENTITY_COERCION_FAILED",
        "HEADLESS_IDENTITY_INVALID",
    )


def test_execute_incomplete_identity_fails_closed_before_root() -> None:
    response = execute_service_1_headless_json_v1(_valid_payload())
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"] == "HEADLESS_IDENTITY_COERCION_FAILED"
    assert response["analysis_id"] == "sales_total"
    json.dumps(response)


def _ready_packet() -> dict[str, Any]:
    digest = "0" * 64
    return {
        "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
        "status": "READY",
        "analysis_id": "sales_total",
        "title": "Resumen de ventas",
        "question": "¿Cuánto vendiste?",
        "result_set": {"case_id": "c1", "analysis_id": "sales_total", "total": 100},
        "findings": [{"finding_id": "f1"}],
        "outcome": {"decision": "none"},
        "result_memory": {
            "status": "PERSISTED",
            "persisted": True,
            "memory_record_id": "m1",
            "artifact_ref": f"resultset:sha256:{digest}",
            "result_set_integrity_digest": digest,
            "executed_at": "2026-09-22T00:00:00+00:00",
        },
    }


def test_response_ready_preserves_resultset_identity() -> None:
    packet = _ready_packet()
    response = build_service_1_headless_response_v1(
        request_analysis_id="sales_total",
        packet=packet,
    )
    assert response["status"] == "READY"
    assert response["analysis_id"] == "sales_total"
    assert response["result_set"] == packet["result_set"]
    assert response["findings"] == packet["findings"]
    assert (
        response["result_memory"]["result_set_integrity_digest"]
        == packet["result_memory"]["result_set_integrity_digest"]
    )
    assert response["integrity"] == {
        "digest_present": True,
        "artifact_ref_coherent": True,
    }
    assert json.loads(json.dumps(response)) == response


def test_response_tampered_digest_fails_closed() -> None:
    packet = _ready_packet()
    packet["result_memory"] = dict(packet["result_memory"])
    packet["result_memory"]["artifact_ref"] = "resultset:sha256:" + "f" * 64
    response = build_service_1_headless_response_v1(
        request_analysis_id="sales_total",
        packet=packet,
    )
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"] == "HEADLESS_RESULT_INTEGRITY_DRIFT"


def test_response_blocked_packet_passes_through() -> None:
    packet = {
        "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
        "status": "BLOCKED",
        "analysis_id": "sales_total",
        "title": "Resumen de ventas",
        "question": "¿Cuánto vendiste?",
        "blocked_reason": "F12_DISCOVERY_NOT_READY",
    }
    response = build_service_1_headless_response_v1(
        request_analysis_id="sales_total",
        packet=packet,
    )
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"] == "F12_DISCOVERY_NOT_READY"
    assert response["analysis_id"] == "sales_total"
    assert response["title"] == "Resumen de ventas"


def test_response_non_serializable_fails_closed() -> None:
    packet = _ready_packet()
    packet["result_set"] = {"bad": {1, 2, 3}}
    response = build_service_1_headless_response_v1(
        request_analysis_id="sales_total",
        packet=packet,
    )
    assert response["status"] == "BLOCKED"
    assert response["blocked_reason"] == "HEADLESS_RESPONSE_NOT_SERIALIZABLE"

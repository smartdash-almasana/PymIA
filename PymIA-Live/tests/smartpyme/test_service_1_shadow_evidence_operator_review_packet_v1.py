from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_shadow_evidence_operator_review_packet_v1 import (
    build_service_1_shadow_evidence_operator_review_packet_v1,
)


def _shadow_evidence() -> dict[str, object]:
    return {
        "schema_version": "S1_RUNNER_SHADOW_EVIDENCE_V1",
        "service_name": "SERVICE_1",
        "status": "SHADOW_EVIDENCE_READY",
        "blocked_reason": None,
        "evidence_ref": "shadow_evidence:case:s1:001:run:s1:001",
        "observed_at": "2026-07-05T12:00:00-03:00",
        "case_id": "case:s1:001",
        "run_id": "run:s1:001",
        "shadow_status": "SHADOW_RUNNER_READY",
        "shadow_run_authorized": True,
        "processed_tool_refs": ["precio_margen_basico"],
        "processed_request_count": 1,
        "runtime_authorized": False,
        "pipeline_called": False,
        "delivery_authorized": False,
        "owner_delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "evidence_packet": {
            "evidence_ref": "shadow_evidence:case:s1:001:run:s1:001",
            "observed_at": "2026-07-05T12:00:00-03:00",
            "case_id": "case:s1:001",
            "run_id": "run:s1:001",
            "shadow_status": "SHADOW_RUNNER_READY",
            "processed_tool_refs": ["precio_margen_basico"],
            "processed_request_count": 1,
            "runtime_authorized": False,
            "pipeline_called": False,
            "delivery_authorized": False,
        },
        "notes": [],
    }


def _payload() -> dict[str, object]:
    return {
        "shadow_evidence": _shadow_evidence(),
        "operator_ref": "operator:service_1:001",
        "review_packet_ref": "operator_review_packet:case:s1:001:run:s1:001",
        "notes": [],
        "owner_publication_requested": False,
    }


def test_operator_review_packet_wraps_shadow_evidence_without_owner_publication() -> None:
    result = build_service_1_shadow_evidence_operator_review_packet_v1(_payload())  # type: ignore[arg-type]

    assert result["status"] == "OPERATOR_REVIEW_PACKET_READY"
    assert result["review_packet_ref"] == "operator_review_packet:case:s1:001:run:s1:001"
    assert result["operator_ref"] == "operator:service_1:001"
    assert result["evidence_ref"] == "shadow_evidence:case:s1:001:run:s1:001"
    assert result["case_id"] == "case:s1:001"
    assert result["run_id"] == "run:s1:001"
    assert result["review_required"] is True
    assert result["owner_publication_authorized"] is False
    assert result["owner_delivery_authorized"] is False
    assert result["autonomous_delivery_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["pipeline_called"] is False
    assert result["processed_tool_refs"] == ["precio_margen_basico"]
    assert result["processed_request_count"] == 1
    assert result["review_items"] == [
        {
            "item_ref": "operator_review_item:1:precio_margen_basico",
            "tool_ref": "precio_margen_basico",
            "required_check": "OPERATOR_VALIDATE_SHADOW_EVIDENCE_BEFORE_ANY_OWNER_DELIVERY",
            "status": "PENDING_OPERATOR_REVIEW",
            "owner_visible": False,
        }
    ]
    assert result["operator_summary"] == {
        "review_packet_ref": "operator_review_packet:case:s1:001:run:s1:001",
        "operator_ref": "operator:service_1:001",
        "evidence_ref": "shadow_evidence:case:s1:001:run:s1:001",
        "case_id": "case:s1:001",
        "run_id": "run:s1:001",
        "processed_tool_refs": ["precio_margen_basico"],
        "processed_request_count": 1,
        "review_required": True,
        "owner_publication_authorized": False,
        "operator_decision_required": "APPROVE_FOR_INTERNAL_NEXT_STEP_OR_REJECT",
    }


def test_operator_review_packet_blocks_owner_publication_attempt() -> None:
    payload = _payload()
    payload["owner_publication_requested"] = True

    result = build_service_1_shadow_evidence_operator_review_packet_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_OWNER_PUBLICATION_ATTEMPT"
    assert result["blocked_reason"] == "owner_publication_requested_true"
    assert result["owner_publication_authorized"] is False
    assert result["operator_summary"] is None


def test_operator_review_packet_blocks_not_ready_shadow_evidence() -> None:
    payload = _payload()
    evidence = _shadow_evidence()
    evidence["status"] = "BLOCKED_INVALID_SHADOW_RESULT"
    payload["shadow_evidence"] = evidence

    result = build_service_1_shadow_evidence_operator_review_packet_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_SHADOW_EVIDENCE_NOT_READY"
    assert result["blocked_reason"] == "shadow_evidence_not_ready"
    assert result["operator_summary"] is None


def test_operator_review_packet_blocks_runtime_pipeline_or_delivery_authorized_evidence() -> None:
    runtime_payload = _payload()
    runtime_evidence = _shadow_evidence()
    runtime_evidence["runtime_authorized"] = True
    runtime_payload["shadow_evidence"] = runtime_evidence
    runtime_result = build_service_1_shadow_evidence_operator_review_packet_v1(runtime_payload)  # type: ignore[arg-type]
    assert runtime_result["status"] == "BLOCKED_INVALID_SHADOW_EVIDENCE"
    assert runtime_result["blocked_reason"] == "shadow_evidence_must_not_authorize_runtime_or_call_pipeline"

    delivery_payload = _payload()
    delivery_evidence = _shadow_evidence()
    delivery_evidence["owner_delivery_authorized"] = True
    delivery_payload["shadow_evidence"] = delivery_evidence
    delivery_result = build_service_1_shadow_evidence_operator_review_packet_v1(delivery_payload)  # type: ignore[arg-type]
    assert delivery_result["status"] == "BLOCKED_INVALID_SHADOW_EVIDENCE"
    assert delivery_result["blocked_reason"] == "shadow_evidence_must_not_authorize_delivery"


def test_operator_review_packet_blocks_processed_count_mismatch() -> None:
    payload = _payload()
    evidence = _shadow_evidence()
    evidence["processed_request_count"] = 2
    payload["shadow_evidence"] = evidence

    result = build_service_1_shadow_evidence_operator_review_packet_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_INVALID_SHADOW_EVIDENCE"
    assert result["blocked_reason"] == "processed_request_count_mismatch"


def test_operator_review_packet_blocks_missing_evidence_packet() -> None:
    payload = _payload()
    evidence = _shadow_evidence()
    evidence["evidence_packet"] = None
    payload["shadow_evidence"] = evidence

    result = build_service_1_shadow_evidence_operator_review_packet_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_INVALID_SHADOW_EVIDENCE"
    assert result["blocked_reason"] == "evidence_packet_required"


def test_operator_review_packet_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)

    build_service_1_shadow_evidence_operator_review_packet_v1(payload)  # type: ignore[arg-type]

    assert payload == original


def test_operator_review_packet_source_has_no_runtime_api_io_or_llm_imports() -> None:
    import pymia.smartpyme.service_1_shadow_evidence_operator_review_packet_v1 as review_module

    source = inspect.getsource(review_module).lower()
    forbidden_fragments = [
        "service_1_pipeline_v1",
        "service_1_autonomous_pipeline_runner_v1",
        "run_service_1_autonomous_pipeline_runner_v1",
        "service_1_operator_delivery_package_v1",
        "openai",
        "anthropic",
        "langchain",
        "langgraph",
        "pydantic_ai",
        "fastapi",
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import openpyxl",
        "from openpyxl",
        "import pandas",
        "from pandas",
        "import pathlib",
        "from pathlib",
        "import subprocess",
        "from subprocess",
        "import json",
        "from json",
        "import shutil",
        "from shutil",
        "import hashlib",
        "from hashlib",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source

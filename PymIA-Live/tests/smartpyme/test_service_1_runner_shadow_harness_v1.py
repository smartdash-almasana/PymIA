from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_runner_shadow_harness_v1 import build_service_1_runner_shadow_harness_v1


def _authorized_request() -> dict[str, object]:
    return {
        "tool_ref": "precio_margen_basico",
        "inputs": {
            "precio_venta": "sheet:Ventas.column:Precio",
            "costo_unitario": "sheet:Costos.column:CostoUnitario",
        },
        "source_pipeline_request_ref": "explicit_tool_request_candidate:tool_plan_candidate:precio_margen_basico",
        "request_kind": "AUTHORIZED_PIPELINE_TOOL_REQUEST",
        "executable": True,
    }


def _payload() -> dict[str, object]:
    return {
        "execution_gate_status": "EXECUTION_AUTHORIZED",
        "execution_authorized": True,
        "pipeline_authorized": True,
        "safe_to_call_pipeline": True,
        "authorized_pipeline_tool_requests": [_authorized_request()],
        "case_id": "case:s1:001",
        "run_id": "run:s1:001",
        "notes": [],
        "runtime_authorized": False,
        "owner_delivery_authorized": False,
        "autonomous_delivery_authorized": False,
    }


def test_shadow_harness_accepts_authorized_execution_gate_output_without_calling_pipeline() -> None:
    result = build_service_1_runner_shadow_harness_v1(_payload())  # type: ignore[arg-type]

    assert result["status"] == "SHADOW_RUNNER_READY"
    assert result["shadow_run_authorized"] is True
    assert result["runtime_authorized"] is False
    assert result["pipeline_called"] is False
    assert result["delivery_authorized"] is False
    assert result["owner_delivery_authorized"] is False
    assert result["autonomous_delivery_authorized"] is False
    assert result["executed_tool_refs"] == ["precio_margen_basico"]
    assert result["shadow_processed_requests"] == [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {
                "precio_venta": "sheet:Ventas.column:Precio",
                "costo_unitario": "sheet:Costos.column:CostoUnitario",
            },
            "source_pipeline_request_ref": "explicit_tool_request_candidate:tool_plan_candidate:precio_margen_basico",
            "request_kind": "SHADOW_PROCESSED_PIPELINE_TOOL_REQUEST",
            "executable": False,
            "pipeline_called": False,
        }
    ]


def test_shadow_harness_blocks_when_execution_gate_status_is_not_authorized() -> None:
    payload = _payload()
    payload["execution_gate_status"] = "BLOCKED_CANDIDATE_NOT_READY"

    result = build_service_1_runner_shadow_harness_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_EXECUTION_NOT_AUTHORIZED"
    assert result["blocked_reason"] == "execution_gate_status_not_authorized"
    assert result["shadow_run_authorized"] is False
    assert result["shadow_processed_requests"] == []


def test_shadow_harness_blocks_when_pipeline_is_not_authorized() -> None:
    payload = _payload()
    payload["pipeline_authorized"] = False

    result = build_service_1_runner_shadow_harness_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_PIPELINE_NOT_AUTHORIZED"
    assert result["blocked_reason"] == "pipeline_authorized_false"


def test_shadow_harness_blocks_when_pipeline_is_not_safe_to_call() -> None:
    payload = _payload()
    payload["safe_to_call_pipeline"] = False

    result = build_service_1_runner_shadow_harness_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_UNSAFE_TO_CALL_PIPELINE"
    assert result["blocked_reason"] == "safe_to_call_pipeline_false"


def test_shadow_harness_blocks_empty_requests() -> None:
    payload = _payload()
    payload["authorized_pipeline_tool_requests"] = []

    result = build_service_1_runner_shadow_harness_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_EMPTY_REQUESTS"
    assert result["blocked_reason"] == "authorized_pipeline_tool_requests_empty"


def test_shadow_harness_blocks_invalid_authorized_request_kind() -> None:
    payload = _payload()
    request = _authorized_request()
    request["request_kind"] = "PIPELINE_REQUEST_CANDIDATE"
    payload["authorized_pipeline_tool_requests"] = [request]

    result = build_service_1_runner_shadow_harness_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_INVALID_REQUEST"
    assert result["blocked_reason"] == "authorized_request_kind_required"


def test_shadow_harness_blocks_runtime_or_delivery_authorization() -> None:
    runtime_payload = _payload()
    runtime_payload["runtime_authorized"] = True
    runtime_result = build_service_1_runner_shadow_harness_v1(runtime_payload)  # type: ignore[arg-type]
    assert runtime_result["status"] == "BLOCKED_INVALID_REQUEST"
    assert runtime_result["blocked_reason"] == "runtime_authorized_must_remain_false_for_shadow"

    delivery_payload = _payload()
    delivery_payload["owner_delivery_authorized"] = True
    delivery_result = build_service_1_runner_shadow_harness_v1(delivery_payload)  # type: ignore[arg-type]
    assert delivery_result["status"] == "BLOCKED_INVALID_REQUEST"
    assert delivery_result["blocked_reason"] == "delivery_authorization_must_remain_false_for_shadow"


def test_shadow_harness_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)

    build_service_1_runner_shadow_harness_v1(payload)  # type: ignore[arg-type]

    assert payload == original


def test_shadow_harness_source_has_no_runner_pipeline_runtime_api_io_or_llm_imports() -> None:
    import pymia.smartpyme.service_1_runner_shadow_harness_v1 as harness_module

    source = inspect.getsource(harness_module).lower()
    forbidden_fragments = [
        "service_1_pipeline_v1",
        "service_1_autonomous_pipeline_runner_v1",
        "run_service_1_autonomous_pipeline_runner_v1",
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
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source

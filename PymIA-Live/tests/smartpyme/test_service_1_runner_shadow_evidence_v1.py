from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_runner_shadow_evidence_v1 import build_service_1_runner_shadow_evidence_v1


def _shadow_result() -> dict[str, object]:
    return {
        "schema_version": "S1_RUNNER_SHADOW_HARNESS_V1",
        "service_name": "SERVICE_1",
        "status": "SHADOW_RUNNER_READY",
        "blocked_reason": None,
        "case_id": "case:s1:001",
        "run_id": "run:s1:001",
        "shadow_run_authorized": True,
        "runtime_authorized": False,
        "pipeline_called": False,
        "delivery_authorized": False,
        "owner_delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "shadow_processed_requests": [
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
        ],
        "executed_tool_refs": ["precio_margen_basico"],
        "notes": [],
    }


def _payload() -> dict[str, object]:
    return {
        "shadow_result": _shadow_result(),
        "evidence_ref": "shadow_evidence:case:s1:001:run:s1:001",
        "observed_at": "2026-07-05T12:00:00-03:00",
        "notes": [],
    }


def test_shadow_evidence_wraps_ready_shadow_result_without_runtime_or_delivery() -> None:
    result = build_service_1_runner_shadow_evidence_v1(_payload())  # type: ignore[arg-type]

    assert result["status"] == "SHADOW_EVIDENCE_READY"
    assert result["evidence_ref"] == "shadow_evidence:case:s1:001:run:s1:001"
    assert result["case_id"] == "case:s1:001"
    assert result["run_id"] == "run:s1:001"
    assert result["shadow_status"] == "SHADOW_RUNNER_READY"
    assert result["processed_tool_refs"] == ["precio_margen_basico"]
    assert result["processed_request_count"] == 1
    assert result["runtime_authorized"] is False
    assert result["pipeline_called"] is False
    assert result["delivery_authorized"] is False
    assert result["owner_delivery_authorized"] is False
    assert result["autonomous_delivery_authorized"] is False
    assert result["evidence_packet"] == {
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
    }


def test_shadow_evidence_blocks_not_ready_shadow_result() -> None:
    payload = _payload()
    shadow = _shadow_result()
    shadow["status"] = "BLOCKED_EMPTY_REQUESTS"
    payload["shadow_result"] = shadow

    result = build_service_1_runner_shadow_evidence_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_SHADOW_NOT_READY"
    assert result["blocked_reason"] == "shadow_result_not_ready"
    assert result["evidence_packet"] is None


def test_shadow_evidence_blocks_runtime_or_pipeline_called_result() -> None:
    payload = _payload()
    shadow = _shadow_result()
    shadow["pipeline_called"] = True
    payload["shadow_result"] = shadow

    result = build_service_1_runner_shadow_evidence_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_INVALID_SHADOW_RESULT"
    assert result["blocked_reason"] == "shadow_result_must_not_authorize_runtime_or_call_pipeline"


def test_shadow_evidence_blocks_delivery_authorized_result() -> None:
    payload = _payload()
    shadow = _shadow_result()
    shadow["owner_delivery_authorized"] = True
    payload["shadow_result"] = shadow

    result = build_service_1_runner_shadow_evidence_v1(payload)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_INVALID_SHADOW_RESULT"
    assert result["blocked_reason"] == "shadow_result_must_not_authorize_delivery"


def test_shadow_evidence_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)

    build_service_1_runner_shadow_evidence_v1(payload)  # type: ignore[arg-type]

    assert payload == original


def test_shadow_evidence_source_has_no_runtime_api_io_or_llm_imports() -> None:
    import pymia.smartpyme.service_1_runner_shadow_evidence_v1 as evidence_module

    source = inspect.getsource(evidence_module).lower()
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

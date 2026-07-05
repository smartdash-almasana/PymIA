from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_explicit_request_to_pipeline_request_gate_v1 import (
    build_service_1_explicit_request_to_pipeline_request_gate_v1,
)
from pymia.smartpyme.service_1_saas_job_to_pipeline_request_adapter_v1 import (
    build_service_1_saas_job_to_pipeline_request_adapter_v1,
)

_ALLOWED_TOOLS = [
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
]


def _saas_job() -> dict[str, object]:
    return {
        "job_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
        "requested_job_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "source_file_intake_ref": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
        "autonomous_chain_candidate_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "autonomous_rerun_candidate_ref": "rerun_candidate:s1:001",
        },
        "planned_job_steps": [
            "validate_session_candidate_refs",
            "validate_file_intake_candidate_refs",
            "prepare_file_processing_job_candidate",
        ],
        "worker_authorized": False,
        "queue_authorized": False,
        "async_execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _explicit_candidate() -> dict[str, object]:
    return {
        "tool_ref": "precio_margen_basico",
        "input_refs": {
            "precio_venta": "sheet:Ventas.column:Precio",
            "costo_unitario": "sheet:Costos.column:CostoUnitario",
        },
        "source_plan_ref": "tool_plan_candidate:precio_margen_basico",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "request_kind": "CANDIDATE_ONLY",
        "executable": False,
    }


def _adapter_payload() -> dict[str, object]:
    return {
        "saas_job_orchestration_status": "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY",
        "saas_job_orchestration_candidate": _saas_job(),
        "explicit_request_status": "EXPLICIT_REQUEST_CANDIDATE_READY",
        "explicit_tool_request_candidate": [_explicit_candidate()],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "case_truth_status": "READY_FOR_TOOL_PLANNING",
        "missing_inputs": [],
        "unsafe_flags": [],
        "notes": [],
    }


def test_adapter_output_feeds_explicit_request_to_pipeline_request_gate() -> None:
    adapter_result = build_service_1_saas_job_to_pipeline_request_adapter_v1(_adapter_payload())  # type: ignore[arg-type]

    assert adapter_result["status"] == "ADAPTER_INPUTS_READY"
    explicit_gate_input = adapter_result["explicit_to_pipeline_gate_input"]
    assert explicit_gate_input is not None

    explicit_gate_result = build_service_1_explicit_request_to_pipeline_request_gate_v1(explicit_gate_input)  # type: ignore[arg-type]

    assert explicit_gate_result["status"] == "PIPELINE_REQUEST_CANDIDATE_READY"
    assert explicit_gate_result["pipeline_tool_request_candidate"] == [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {
                "precio_venta": "sheet:Ventas.column:Precio",
                "costo_unitario": "sheet:Costos.column:CostoUnitario",
            },
            "source_explicit_request_ref": "explicit_tool_request_candidate:tool_plan_candidate:precio_margen_basico",
            "request_kind": "PIPELINE_REQUEST_CANDIDATE",
            "executable": False,
        }
    ]
    assert explicit_gate_result["runtime_authorized"] is False
    assert explicit_gate_result["execution_authorized"] is False
    assert explicit_gate_result["pipeline_execution_authorized"] is False
    assert explicit_gate_result["delivery_authorized"] is False


def test_chain_blocks_before_explicit_gate_when_adapter_inputs_are_unsafe() -> None:
    payload = _adapter_payload()
    payload["unsafe_flags"] = ["forbidden_claim_requested"]

    adapter_result = build_service_1_saas_job_to_pipeline_request_adapter_v1(payload)  # type: ignore[arg-type]

    assert adapter_result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert adapter_result["explicit_to_pipeline_gate_input"] is None


def test_chain_does_not_mutate_adapter_payload() -> None:
    payload = _adapter_payload()
    original = copy.deepcopy(payload)

    adapter_result = build_service_1_saas_job_to_pipeline_request_adapter_v1(payload)  # type: ignore[arg-type]
    explicit_gate_input = adapter_result["explicit_to_pipeline_gate_input"]
    assert explicit_gate_input is not None
    build_service_1_explicit_request_to_pipeline_request_gate_v1(explicit_gate_input)  # type: ignore[arg-type]

    assert payload == original


def test_chain_source_does_not_import_runner_pipeline_execution_gate_api_io_or_llm() -> None:
    import pymia.smartpyme.service_1_saas_job_to_pipeline_request_adapter_v1 as adapter_module
    import pymia.smartpyme.service_1_explicit_request_to_pipeline_request_gate_v1 as explicit_gate_module

    source = (inspect.getsource(adapter_module) + inspect.getsource(explicit_gate_module)).lower()
    forbidden_source_fragments = [
        "service_1_pipeline_v1",
        "service_1_autonomous_pipeline_runner_v1",
        "build_service_1_pipeline_request_execution_gate_v1",
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
    for fragment in forbidden_source_fragments:
        assert fragment not in source

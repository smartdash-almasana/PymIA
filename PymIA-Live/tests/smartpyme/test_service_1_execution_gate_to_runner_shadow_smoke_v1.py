from __future__ import annotations

import inspect

from pymia.smartpyme.service_1_explicit_request_to_pipeline_request_gate_v1 import (
    build_service_1_explicit_request_to_pipeline_request_gate_v1,
)
from pymia.smartpyme.service_1_pipeline_request_execution_gate_v1 import (
    build_service_1_pipeline_request_execution_gate_v1,
)
from pymia.smartpyme.service_1_runner_shadow_evidence_v1 import build_service_1_runner_shadow_evidence_v1
from pymia.smartpyme.service_1_runner_shadow_harness_v1 import build_service_1_runner_shadow_harness_v1
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


def _execution_gate_input_from(
    *,
    explicit_gate_result: dict[str, object],
    missing_inputs: list[str] | None = None,
    case_truth_status: str | None = "READY_FOR_TOOL_PLANNING",
) -> dict[str, object]:
    return {
        "pipeline_candidate_status": explicit_gate_result["status"],
        "pipeline_tool_requests": explicit_gate_result["pipeline_tool_request_candidate"],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "missing_inputs": list(missing_inputs or []),
        "unsafe_flags": [],
        "case_truth_status": case_truth_status,
        "notes": [],
    }


def _execution_chain(payload: dict[str, object]) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    adapter_result = build_service_1_saas_job_to_pipeline_request_adapter_v1(payload)  # type: ignore[arg-type]
    explicit_gate_input = adapter_result["explicit_to_pipeline_gate_input"]
    assert explicit_gate_input is not None
    explicit_gate_result = build_service_1_explicit_request_to_pipeline_request_gate_v1(explicit_gate_input)  # type: ignore[arg-type]
    execution_gate_result = build_service_1_pipeline_request_execution_gate_v1(
        _execution_gate_input_from(explicit_gate_result=explicit_gate_result)  # type: ignore[arg-type]
    )
    return adapter_result, explicit_gate_result, execution_gate_result


def test_execution_gate_output_flows_to_runner_shadow_harness_and_evidence() -> None:
    adapter_result, explicit_gate_result, execution_gate_result = _execution_chain(_adapter_payload())

    shadow_result = build_service_1_runner_shadow_harness_v1(  # type: ignore[arg-type]
        {
            "execution_gate_status": execution_gate_result["status"],
            "execution_authorized": execution_gate_result["execution_authorized"],
            "pipeline_authorized": execution_gate_result["pipeline_authorized"],
            "safe_to_call_pipeline": execution_gate_result["safe_to_call_pipeline"],
            "authorized_pipeline_tool_requests": execution_gate_result["authorized_pipeline_tool_requests"],
            "case_id": "case:s1:001",
            "run_id": "run:s1:001",
            "notes": [],
            "runtime_authorized": execution_gate_result["runtime_authorized"],
            "owner_delivery_authorized": False,
            "autonomous_delivery_authorized": execution_gate_result["autonomous_delivery_authorized"],
        }
    )
    evidence_result = build_service_1_runner_shadow_evidence_v1(  # type: ignore[arg-type]
        {
            "shadow_result": shadow_result,
            "evidence_ref": "shadow_evidence:case:s1:001:run:s1:001",
            "observed_at": "2026-07-05T12:00:00-03:00",
            "notes": [],
        }
    )

    assert adapter_result["status"] == "ADAPTER_INPUTS_READY"
    assert explicit_gate_result["status"] == "PIPELINE_REQUEST_CANDIDATE_READY"
    assert execution_gate_result["status"] == "EXECUTION_AUTHORIZED"
    assert shadow_result["status"] == "SHADOW_RUNNER_READY"
    assert shadow_result["pipeline_called"] is False
    assert shadow_result["runtime_authorized"] is False
    assert shadow_result["delivery_authorized"] is False
    assert evidence_result["status"] == "SHADOW_EVIDENCE_READY"
    assert evidence_result["evidence_packet"] == {
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


def test_shadow_smoke_stops_when_execution_gate_blocks() -> None:
    adapter_result = build_service_1_saas_job_to_pipeline_request_adapter_v1(_adapter_payload())  # type: ignore[arg-type]
    explicit_gate_result = build_service_1_explicit_request_to_pipeline_request_gate_v1(
        adapter_result["explicit_to_pipeline_gate_input"]  # type: ignore[arg-type]
    )
    execution_gate_result = build_service_1_pipeline_request_execution_gate_v1(
        _execution_gate_input_from(
            explicit_gate_result=explicit_gate_result,
            case_truth_status="NEEDS_OWNER_CONFIRMATION",
        )  # type: ignore[arg-type]
    )

    shadow_result = build_service_1_runner_shadow_harness_v1(  # type: ignore[arg-type]
        {
            "execution_gate_status": execution_gate_result["status"],
            "execution_authorized": execution_gate_result["execution_authorized"],
            "pipeline_authorized": execution_gate_result["pipeline_authorized"],
            "safe_to_call_pipeline": execution_gate_result["safe_to_call_pipeline"],
            "authorized_pipeline_tool_requests": execution_gate_result["authorized_pipeline_tool_requests"],
            "case_id": "case:s1:001",
            "run_id": "run:s1:blocked",
            "notes": [],
        }
    )

    assert execution_gate_result["status"] == "BLOCKED_CANDIDATE_NOT_READY"
    assert shadow_result["status"] == "BLOCKED_EXECUTION_NOT_AUTHORIZED"
    assert shadow_result["pipeline_called"] is False
    assert shadow_result["runtime_authorized"] is False


def test_shadow_smoke_source_does_not_import_real_runner_pipeline_api_storage_worker_or_llm() -> None:
    import pymia.smartpyme.service_1_runner_shadow_evidence_v1 as evidence_module
    import pymia.smartpyme.service_1_runner_shadow_harness_v1 as harness_module

    source = (inspect.getsource(harness_module) + inspect.getsource(evidence_module)).lower()
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

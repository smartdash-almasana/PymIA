from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_saas_job_to_pipeline_request_adapter_v1 import (
    SCHEMA_VERSION,
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


def _payload() -> dict[str, object]:
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


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_saas_job_to_pipeline_request_adapter_v1(payload)  # type: ignore[arg-type]


def test_blocks_missing_saas_job_candidate() -> None:
    payload = _payload()
    payload["saas_job_orchestration_candidate"] = None

    result = _build(payload)

    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_MISSING_SAAS_JOB"
    assert result["blocked_reason"] == "saas_job_orchestration_candidate_required"
    assert result["explicit_to_pipeline_gate_input"] is None


def test_blocks_saas_job_status_not_ready() -> None:
    payload = _payload()
    payload["saas_job_orchestration_status"] = "BLOCKED_MISSING_SESSION"

    result = _build(payload)

    assert result["status"] == "BLOCKED_INVALID_SAAS_JOB"
    assert result["blocked_reason"] == "saas_job_orchestration_status_not_ready"


def test_blocks_unsupported_owner_delivery_packet_refresh_candidate() -> None:
    payload = _payload()
    job = copy.deepcopy(payload["saas_job_orchestration_candidate"])
    job["requested_job_kind"] = "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE"
    payload["saas_job_orchestration_candidate"] = job

    result = _build(payload)

    assert result["status"] == "BLOCKED_UNSUPPORTED_JOB_KIND"
    assert result["blocked_reason"] == "requested_job_kind_not_supported_by_adapter_v1"


def test_blocks_missing_explicit_requests() -> None:
    payload = _payload()
    payload["explicit_tool_request_candidate"] = []

    result = _build(payload)

    assert result["status"] == "BLOCKED_MISSING_EXPLICIT_REQUESTS"
    assert result["blocked_reason"] == "explicit_tool_request_candidate_required"


def test_blocks_executable_explicit_request_candidate() -> None:
    payload = _payload()
    candidate = copy.deepcopy(payload["explicit_tool_request_candidate"])[0]  # type: ignore[index]
    candidate["executable"] = True
    payload["explicit_tool_request_candidate"] = [candidate]

    result = _build(payload)

    assert result["status"] == "BLOCKED_INVALID_EXPLICIT_REQUEST"
    assert result["blocked_reason"] == "explicit_request_candidate_must_not_be_executable"


def test_blocks_non_candidate_only_request_kind() -> None:
    payload = _payload()
    candidate = copy.deepcopy(payload["explicit_tool_request_candidate"])[0]  # type: ignore[index]
    candidate["request_kind"] = "EXECUTABLE"
    payload["explicit_tool_request_candidate"] = [candidate]

    result = _build(payload)

    assert result["status"] == "BLOCKED_INVALID_EXPLICIT_REQUEST"
    assert result["blocked_reason"] == "request_kind_not_candidate_only"


def test_blocks_non_allowlisted_tool_ref() -> None:
    payload = _payload()
    payload["allowed_tool_refs"] = ["caja_diaria_triage"]

    result = _build(payload)

    assert result["status"] == "BLOCKED_INVALID_EXPLICIT_REQUEST"
    assert result["blocked_reason"] == "candidate_tool_ref_not_allowlisted"


def test_blocks_unsafe_flags() -> None:
    payload = _payload()
    payload["unsafe_flags"] = ["forbidden_claim_requested"]

    result = _build(payload)

    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "unsafe_flags_present"


def test_blocks_missing_inputs() -> None:
    payload = _payload()
    payload["missing_inputs"] = ["costo_unitario"]

    result = _build(payload)

    assert result["status"] == "BLOCKED_MISSING_INPUTS"
    assert result["blocked_reason"] == "missing_inputs_present"


def test_ready_returns_explicit_to_pipeline_gate_input_only() -> None:
    result = _build(_payload())

    assert result["status"] == "ADAPTER_INPUTS_READY"
    assert result["explicit_to_pipeline_gate_input"] == {
        "explicit_request_status": "EXPLICIT_REQUEST_CANDIDATE_READY",
        "explicit_tool_request_candidate": [_explicit_candidate()],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "final_execution_gate_status": "CLOSED_NOT_EXECUTABLE",
        "pipeline_request_policy": "SAAS_JOB_ADAPTER_V1",
    }
    assert result["pipeline_execution_gate_input_required_later"] is True
    assert "pipeline_execution_gate_input" not in result
    assert "pipeline_tool_requests" not in result


def test_never_authorizes_execution_runtime_or_delivery() -> None:
    for payload in [_payload(), {**_payload(), "saas_job_orchestration_candidate": None}]:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["execution_authorized"] is False
        assert result["pipeline_authorized"] is False
        assert result["runner_authorized"] is False
        assert result["delivery_authorized"] is False


def test_module_source_does_not_import_runtime_pipeline_io_api_or_llm() -> None:
    import pymia.smartpyme.service_1_saas_job_to_pipeline_request_adapter_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "service_1_pipeline_v1",
        "service_1_autonomous_pipeline_runner_v1",
        "build_service_1_explicit_request_to_pipeline_request_gate_v1",
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


def test_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)

    _build(payload)

    assert payload == original


def test_output_is_deterministic() -> None:
    payload = _payload()

    assert _build(copy.deepcopy(payload)) == _build(copy.deepcopy(payload))

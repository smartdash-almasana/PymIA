from __future__ import annotations

import copy
import inspect
from pathlib import Path
from typing import Any

import pymia.smartpyme.service_1_autonomous_pipeline_runner_v1 as runner_module
from pymia.smartpyme.service_1_autonomous_pipeline_runner_v1 import (
    SCHEMA_VERSION,
    run_service_1_autonomous_pipeline_runner_v1,
)


def _base_input(tmp_path: Path) -> dict[str, object]:
    return {
        "execution_gate_status": "EXECUTION_AUTHORIZED",
        "execution_authorized": True,
        "pipeline_authorized": True,
        "safe_to_call_pipeline": True,
        "authorized_pipeline_tool_requests": [
            {
                "tool_ref": "precio_margen_basico",
                "inputs": {
                    "precio_venta": 100,
                    "costo_unitario": 60,
                },
                "source_pipeline_request_ref": "pipeline_request_candidate:precio_margen_basico",
                "request_kind": "AUTHORIZED_PIPELINE_TOOL_REQUEST",
                "executable": True,
            }
        ],
        "case_id": "case_1",
        "run_id": "run_1",
        "notes": [],
        "output_dir": str(tmp_path),
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return run_service_1_autonomous_pipeline_runner_v1(payload)  # type: ignore[arg-type]


def _pipeline_result(tool_refs: list[str]) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "requested_tool_count": len(tool_refs),
        "executed_tool_refs": tool_refs,
        "tool_results": [],
        "delivery_flow": {"status": "MOCKED"},
        "runtime_authorized": False,
        "notes": ["mocked pipeline result"],
    }


def test_blocks_if_execution_gate_status_is_not_authorized(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    payload["execution_gate_status"] = "BLOCKED"

    result = _build(payload)

    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_EXECUTION_NOT_AUTHORIZED"
    assert result["pipeline_called"] is False
    assert result["runtime_authorized"] is False
    assert result["pipeline_run_result"] is None


def test_blocks_if_execution_authorized_false(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    payload["execution_authorized"] = False

    result = _build(payload)

    assert result["status"] == "BLOCKED_EXECUTION_NOT_AUTHORIZED"
    assert result["blocked_reason"] == "execution_authorized_false"


def test_blocks_if_pipeline_authorized_false(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    payload["pipeline_authorized"] = False

    result = _build(payload)

    assert result["status"] == "BLOCKED_PIPELINE_NOT_AUTHORIZED"
    assert result["blocked_reason"] == "pipeline_authorized_false"


def test_blocks_if_unsafe_to_call_pipeline(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    payload["safe_to_call_pipeline"] = False

    result = _build(payload)

    assert result["status"] == "BLOCKED_UNSAFE_TO_CALL_PIPELINE"
    assert result["blocked_reason"] == "safe_to_call_pipeline_false"


def test_blocks_if_authorized_requests_empty(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    payload["authorized_pipeline_tool_requests"] = []

    result = _build(payload)

    assert result["status"] == "BLOCKED_NO_REQUESTS"
    assert result["blocked_reason"] == "authorized_pipeline_tool_requests_empty"
    assert result["pipeline_called"] is False


def test_unknown_if_output_dir_missing(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    payload.pop("output_dir")

    result = _build(payload)

    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "output_dir_required"
    assert result["pipeline_called"] is False


def test_calls_pipeline_when_everything_is_authorized(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []

    def fake_pipeline(*, tool_requests, output_dir):  # type: ignore[no-untyped-def]
        calls.append({"tool_requests": tool_requests, "output_dir": output_dir})
        return _pipeline_result([request["tool_ref"] for request in tool_requests])

    monkeypatch.setattr(runner_module, "run_service_1_pipeline_v1", fake_pipeline)

    result = _build(_base_input(tmp_path))

    assert calls == [
        {
            "tool_requests": [
                {
                    "tool_ref": "precio_margen_basico",
                    "inputs": {"precio_venta": 100, "costo_unitario": 60},
                }
            ],
            "output_dir": tmp_path,
        }
    ]
    assert result["status"] == "PIPELINE_RUN_COMPLETED"
    assert result["pipeline_called"] is True
    assert result["runtime_authorized"] is False
    assert result["executed_tool_refs"] == ["precio_margen_basico"]
    assert result["pipeline_run_result"] == _pipeline_result(["precio_margen_basico"])


def test_pipeline_run_failed_if_pipeline_raises(monkeypatch, tmp_path: Path) -> None:
    def failing_pipeline(*, tool_requests, output_dir):  # type: ignore[no-untyped-def]
        raise RuntimeError("boom")

    monkeypatch.setattr(runner_module, "run_service_1_pipeline_v1", failing_pipeline)

    result = _build(_base_input(tmp_path))

    assert result["status"] == "PIPELINE_RUN_FAILED"
    assert result["pipeline_called"] is True
    assert result["runtime_authorized"] is False
    assert result["pipeline_run_result"] is None
    assert str(result["blocked_reason"]).startswith("pipeline_exception:RuntimeError:boom")


def test_pipeline_run_failed_if_authorized_request_is_not_executable(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    request = copy.deepcopy(payload["authorized_pipeline_tool_requests"])[0]  # type: ignore[index]
    request["executable"] = False
    payload["authorized_pipeline_tool_requests"] = [request]

    result = _build(payload)

    assert result["status"] == "PIPELINE_RUN_FAILED"
    assert result["blocked_reason"] == "authorized_request_must_be_executable"
    assert result["pipeline_called"] is False


def test_pipeline_run_failed_if_authorized_request_kind_is_wrong(tmp_path: Path) -> None:
    payload = _base_input(tmp_path)
    request = copy.deepcopy(payload["authorized_pipeline_tool_requests"])[0]  # type: ignore[index]
    request["request_kind"] = "PIPELINE_REQUEST_CANDIDATE"
    payload["authorized_pipeline_tool_requests"] = [request]

    result = _build(payload)

    assert result["status"] == "PIPELINE_RUN_FAILED"
    assert result["blocked_reason"] == "authorized_request_kind_required"
    assert result["pipeline_called"] is False


def test_does_not_authorize_delivery_or_autonomous_delivery(monkeypatch, tmp_path: Path) -> None:
    def fake_pipeline(*, tool_requests, output_dir):  # type: ignore[no-untyped-def]
        return _pipeline_result([request["tool_ref"] for request in tool_requests])

    monkeypatch.setattr(runner_module, "run_service_1_pipeline_v1", fake_pipeline)

    cases = []
    blocked = _base_input(tmp_path)
    blocked["execution_authorized"] = False
    cases.append(blocked)
    cases.append(_base_input(tmp_path))

    for payload in cases:
        result = _build(payload)
        assert result["delivery_authorized"] is False
        assert result["autonomous_delivery_authorized"] is False


def test_module_source_does_not_touch_cli_signoff_model_runtime_or_chatbot() -> None:
    source = inspect.getsource(runner_module).lower()
    forbidden_source_fragments = [
        "pymia.cli",
        "service_1_operator",
        "signoff",
        "llm",
        "chatbot",
        "owner_reentry",
        "case_delivery_folder",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source


def test_does_not_mutate_input(monkeypatch, tmp_path: Path) -> None:
    def fake_pipeline(*, tool_requests, output_dir):  # type: ignore[no-untyped-def]
        return _pipeline_result([request["tool_ref"] for request in tool_requests])

    monkeypatch.setattr(runner_module, "run_service_1_pipeline_v1", fake_pipeline)
    payload = _base_input(tmp_path)
    original = copy.deepcopy(payload)

    _build(payload)

    assert payload == original


def test_does_not_decide_or_add_tool_refs(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_pipeline(*, tool_requests, output_dir):  # type: ignore[no-untyped-def]
        calls.append([request["tool_ref"] for request in tool_requests])
        return _pipeline_result(calls[-1])

    monkeypatch.setattr(runner_module, "run_service_1_pipeline_v1", fake_pipeline)
    payload = _base_input(tmp_path)
    payload["authorized_pipeline_tool_requests"] = [
        {
            "tool_ref": "caja_diaria_triage",
            "inputs": {"saldo_inicial": 0, "ingresos": 10, "egresos": 4},
            "request_kind": "AUTHORIZED_PIPELINE_TOOL_REQUEST",
            "executable": True,
        }
    ]

    result = _build(payload)

    assert calls == [["caja_diaria_triage"]]
    assert result["executed_tool_refs"] == ["caja_diaria_triage"]

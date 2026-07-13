from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_explicit_request_to_pipeline_request_gate_v1 import (
    SCHEMA_VERSION,
    build_service_1_explicit_request_to_pipeline_request_gate_v1,
)

_ALLOWED_TOOLS = [
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
]


def _base_input() -> dict[str, object]:
    return {
        "explicit_request_status": "EXPLICIT_REQUEST_CANDIDATE_READY",
        "explicit_tool_request_candidate": [
            {
                "tool_ref": "precio_margen_basico",
                "input_refs": {
                    "precio_venta": "sheet:Ventas.column:Precio",
                    "costo_unitario": "sheet:Costos.column:CostoUnitario",
                },
                "source_plan_ref": "tool_plan_candidate:precio_margen_basico",
                "request_kind": "CANDIDATE_ONLY",
                "executable": False,
            }
        ],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "final_execution_gate_status": "CLOSED_NOT_EXECUTABLE",
        "pipeline_request_policy": "candidate_only",
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_explicit_request_to_pipeline_request_gate_v1(payload)  # type: ignore[arg-type]


def test_blocked_if_explicit_request_status_is_not_ready() -> None:
    payload = _base_input()
    payload["explicit_request_status"] = "NEEDS_MAPPING_CONFIRMATION"
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "explicit_request_status_not_ready"
    assert result["pipeline_tool_request_candidate"] == []


def test_needs_final_execution_authorization_if_gate_is_not_closed_not_executable() -> None:
    payload = _base_input()
    payload["final_execution_gate_status"] = "AUTHORIZED_TO_EXECUTE"
    result = _build(payload)
    assert result["status"] == "NEEDS_FINAL_EXECUTION_AUTHORIZATION"
    assert result["blocked_reason"] == "final_execution_gate_must_remain_closed_not_executable"


def test_blocked_if_request_kind_is_not_candidate_only() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["explicit_tool_request_candidate"])[0]  # type: ignore[index]
    candidate["request_kind"] = "EXECUTABLE"
    payload["explicit_tool_request_candidate"] = [candidate]
    result = _build(payload)
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "request_kind_not_candidate_only"


def test_blocked_if_explicit_candidate_is_executable() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["explicit_tool_request_candidate"])[0]  # type: ignore[index]
    candidate["executable"] = True
    payload["explicit_tool_request_candidate"] = [candidate]
    result = _build(payload)
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "explicit_request_candidate_must_not_be_executable"


def test_blocked_if_tool_ref_is_not_allowlisted() -> None:
    payload = _base_input()
    payload["allowed_tool_refs"] = ["caja_diaria_triage"]
    result = _build(payload)
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "candidate_tool_ref_not_allowlisted"


def test_unknown_if_input_refs_are_empty() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["explicit_tool_request_candidate"])[0]  # type: ignore[index]
    candidate["input_refs"] = {}
    payload["explicit_tool_request_candidate"] = [candidate]
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "missing_input_refs"


def test_ready_with_precio_margen_basico() -> None:
    result = _build(_base_input())
    assert result["status"] == "PIPELINE_REQUEST_CANDIDATE_READY"
    assert result["pipeline_tool_request_candidate"] == [
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


def test_ready_with_caja_diaria_triage() -> None:
    payload = _base_input()
    payload["explicit_tool_request_candidate"] = [
        {
            "tool_ref": "caja_diaria_triage",
            "input_refs": {
                "saldo_inicial": "sheet:Caja.column:SaldoInicial",
                "ingresos": "sheet:Caja.column:Ingresos",
                "egresos": "sheet:Caja.column:Egresos",
            },
            "source_plan_ref": "tool_plan_candidate:caja_diaria_triage",
            "request_kind": "CANDIDATE_ONLY",
            "executable": False,
        }
    ]
    result = _build(payload)
    assert result["status"] == "PIPELINE_REQUEST_CANDIDATE_READY"
    assert result["pipeline_tool_request_candidate"][0]["tool_ref"] == "caja_diaria_triage"
    assert result["pipeline_tool_request_candidate"][0]["executable"] is False


def test_never_authorizes_runtime_execution_pipeline_execution_or_delivery() -> None:
    cases = []
    blocked = _base_input()
    blocked["explicit_request_status"] = "BLOCKED"
    cases.append(blocked)
    needs_auth = _base_input()
    needs_auth["final_execution_gate_status"] = "OPEN"
    cases.append(needs_auth)
    unknown = _base_input()
    candidate = copy.deepcopy(unknown["explicit_tool_request_candidate"])[0]  # type: ignore[index]
    candidate["input_refs"] = {}
    unknown["explicit_tool_request_candidate"] = [candidate]
    cases.append(unknown)
    cases.append(_base_input())
    for payload in cases:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["execution_authorized"] is False
        assert result["pipeline_execution_authorized"] is False
        assert result["delivery_authorized"] is False


def test_result_does_not_return_tool_requests_key() -> None:
    result = _build(_base_input())
    assert "tool_requests" not in result


def test_pipeline_request_candidate_is_not_executable() -> None:
    result = _build(_base_input())
    candidate = result["pipeline_tool_request_candidate"][0]
    assert candidate["request_kind"] == "PIPELINE_REQUEST_CANDIDATE"
    assert candidate["executable"] is False


def test_module_source_does_not_import_pipeline_cli_delivery_model_runtime_or_chatbot() -> None:
    import pymia.smartpyme.service_1_explicit_request_to_pipeline_request_gate_v1 as module
    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import pymia.smartpyme.service_1_pipeline_v1",
        "from pymia.smartpyme.service_1_pipeline_v1",
        "run_service_1_pipeline_v1",
        "import pymia.cli.service_1_operator",
        "from pymia.cli.service_1_operator",
        "manual_first_aid_delivery",
        "delivery_flow",
        "llm",
        "chatbot",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source


def test_does_not_mutate_input() -> None:
    payload = _base_input()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original

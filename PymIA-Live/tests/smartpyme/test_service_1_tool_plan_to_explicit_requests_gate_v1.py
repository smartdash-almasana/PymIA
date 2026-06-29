from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_tool_plan_to_explicit_requests_gate_v1 import (
    SCHEMA_VERSION,
    build_service_1_tool_plan_to_explicit_requests_gate_v1,
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
        "tool_plan_status": "TOOL_PLAN_CANDIDATE_READY",
        "candidate_tool_refs": ["precio_margen_basico"],
        "tool_plan_candidate": [
            {
                "tool_ref": "precio_margen_basico",
                "reason": "Owner axis matched conservative V1 candidate precio_margen_basico.",
                "input_mapping_refs": {
                    "precio_venta": "sheet:Ventas.column:Precio",
                    "costo_unitario": "sheet:Costos.column:CostoUnitario",
                },
                "missing_inputs": [],
                "limitations": [],
            }
        ],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "authorization_status": "AUTHORIZED_FOR_EXPLICIT_REQUEST_CANDIDATE",
        "confirmed_input_mapping_refs": {
            "precio_margen_basico": {
                "precio_venta": "sheet:Ventas.column:Precio",
                "costo_unitario": "sheet:Costos.column:CostoUnitario",
            }
        },
        "execution_policy": "candidate_only",
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_tool_plan_to_explicit_requests_gate_v1(payload)  # type: ignore[arg-type]


def test_blocked_if_tool_plan_status_is_not_ready() -> None:
    payload = _base_input()
    payload["tool_plan_status"] = "NEEDS_EVIDENCE"
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "tool_plan_status_not_ready"
    assert result["explicit_tool_request_candidate"] == []


def test_needs_authorization_if_authorization_status_does_not_allow_candidate() -> None:
    payload = _base_input()
    payload["authorization_status"] = "NOT_AUTHORIZED"
    result = _build(payload)
    assert result["status"] == "NEEDS_AUTHORIZATION"
    assert result["blocked_reason"] == "authorization_required_for_explicit_request_candidate"


def test_blocked_if_candidate_tool_ref_is_not_allowlisted() -> None:
    payload = _base_input()
    payload["candidate_tool_refs"] = ["precio_margen_basico"]
    payload["allowed_tool_refs"] = ["caja_diaria_triage"]
    result = _build(payload)
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "candidate_tool_ref_not_allowlisted"


def test_needs_mapping_confirmation_if_confirmed_input_mapping_refs_are_missing() -> None:
    payload = _base_input()
    payload["confirmed_input_mapping_refs"] = {}
    result = _build(payload)
    assert result["status"] == "NEEDS_MAPPING_CONFIRMATION"
    assert result["blocked_reason"] == "input_mapping_confirmation_required"
    assert result["missing_confirmation_refs"] == ["precio_margen_basico:input_mapping_refs"]


def test_needs_mapping_confirmation_if_required_variable_mapping_is_missing() -> None:
    payload = _base_input()
    payload["confirmed_input_mapping_refs"] = {
        "precio_margen_basico": {
            "precio_venta": "sheet:Ventas.column:Precio",
        }
    }
    result = _build(payload)
    assert result["status"] == "NEEDS_MAPPING_CONFIRMATION"
    assert "precio_margen_basico:costo_unitario" in result["missing_confirmation_refs"]


def test_ready_with_precio_margen_basico_confirmed_mapping() -> None:
    result = _build(_base_input())
    assert result["status"] == "EXPLICIT_REQUEST_CANDIDATE_READY"
    assert result["explicit_tool_request_candidate"] == [
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
    ]


def test_ready_with_caja_diaria_triage_confirmed_mapping() -> None:
    payload = _base_input()
    payload["candidate_tool_refs"] = ["caja_diaria_triage"]
    payload["tool_plan_candidate"] = [
        {
            "tool_ref": "caja_diaria_triage",
            "input_mapping_refs": {
                "saldo_inicial": "sheet:Caja.column:SaldoInicial",
                "ingresos": "sheet:Caja.column:Ingresos",
                "egresos": "sheet:Caja.column:Egresos",
            },
        }
    ]
    payload["confirmed_input_mapping_refs"] = {
        "caja_diaria_triage": {
            "saldo_inicial": "sheet:Caja.column:SaldoInicial",
            "ingresos": "sheet:Caja.column:Ingresos",
            "egresos": "sheet:Caja.column:Egresos",
        }
    }
    result = _build(payload)
    assert result["status"] == "EXPLICIT_REQUEST_CANDIDATE_READY"
    assert result["explicit_tool_request_candidate"][0]["tool_ref"] == "caja_diaria_triage"
    assert result["explicit_tool_request_candidate"][0]["executable"] is False


def test_never_authorizes_runtime_execution_pipeline_or_delivery() -> None:
    cases = []
    blocked = _base_input()
    blocked["tool_plan_status"] = "UNKNOWN"
    cases.append(blocked)
    needs_auth = _base_input()
    needs_auth["authorization_status"] = "NOT_AUTHORIZED"
    cases.append(needs_auth)
    needs_mapping = _base_input()
    needs_mapping["confirmed_input_mapping_refs"] = {}
    cases.append(needs_mapping)
    cases.append(_base_input())
    for payload in cases:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["execution_authorized"] is False
        assert result["pipeline_authorized"] is False
        assert result["delivery_authorized"] is False


def test_result_does_not_return_tool_requests_key() -> None:
    result = _build(_base_input())
    assert "tool_requests" not in result


def test_explicit_tool_request_candidate_is_not_executable() -> None:
    result = _build(_base_input())
    candidate = result["explicit_tool_request_candidate"][0]
    assert candidate["request_kind"] == "CANDIDATE_ONLY"
    assert candidate["executable"] is False


def test_module_source_does_not_import_pipeline_cli_delivery_model_runtime_or_chatbot() -> None:
    import pymia.smartpyme.service_1_tool_plan_to_explicit_requests_gate_v1 as module
    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import pymia.smartpyme.service_1_pipeline_v1",
        "from pymia.smartpyme.service_1_pipeline_v1",
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

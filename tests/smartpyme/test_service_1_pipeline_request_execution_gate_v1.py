from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_pipeline_request_execution_gate_v1 import (
    SCHEMA_VERSION,
    build_service_1_pipeline_request_execution_gate_v1,
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
        "pipeline_candidate_status": "PIPELINE_REQUEST_CANDIDATE_READY",
        "pipeline_tool_requests": [
            {
                "tool_ref": "precio_margen_basico",
                "inputs": {
                    "precio_venta": "sheet:Ventas.column:Precio",
                    "costo_unitario": "sheet:Costos.column:CostoUnitario",
                },
                "source_explicit_request_ref": "explicit_tool_request_candidate:precio_margen_basico",
                "request_kind": "PIPELINE_REQUEST_CANDIDATE",
                "executable": False,
            }
        ],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "missing_inputs": [],
        "unsafe_flags": [],
        "case_truth_status": "READY_FOR_TOOL_PLANNING",
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_pipeline_request_execution_gate_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_pipeline_candidate_status_is_not_ready() -> None:
    payload = _base_input()
    payload["pipeline_candidate_status"] = "PIPELINE_REQUEST_CANDIDATE_BLOCKED"

    result = _build(payload)

    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_CANDIDATE_NOT_READY"
    assert result["execution_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["safe_to_call_pipeline"] is False
    assert result["authorized_pipeline_tool_requests"] == []


def test_blocks_if_case_truth_status_is_not_ready() -> None:
    payload = _base_input()
    payload["case_truth_status"] = "NEEDS_OWNER_CONFIRMATION"

    result = _build(payload)

    assert result["status"] == "BLOCKED_CANDIDATE_NOT_READY"
    assert result["blocked_reason"] == "case_truth_status_not_ready"


def test_blocks_unsafe_flags() -> None:
    payload = _base_input()
    payload["unsafe_flags"] = ["forbidden_claim_requested"]

    result = _build(payload)

    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "unsafe_flags_present"
    assert result["authorized_pipeline_tool_requests"] == []


def test_blocks_non_allowlisted_tool_ref() -> None:
    payload = _base_input()
    payload["allowed_tool_refs"] = ["caja_diaria_triage"]

    result = _build(payload)

    assert result["status"] == "BLOCKED_UNSUPPORTED_TOOL"
    assert result["blocked_reason"] == "candidate_tool_ref_not_allowlisted"


def test_blocks_missing_inputs_from_gate_input() -> None:
    payload = _base_input()
    payload["missing_inputs"] = ["costo_unitario"]

    result = _build(payload)

    assert result["status"] == "BLOCKED_MISSING_INPUTS"
    assert result["blocked_reason"] == "missing_inputs_present"
    assert result["missing_inputs"] == ["costo_unitario"]


def test_blocks_empty_candidate_inputs() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["pipeline_tool_requests"])[0]  # type: ignore[index]
    candidate["inputs"] = {}
    payload["pipeline_tool_requests"] = [candidate]

    result = _build(payload)

    assert result["status"] == "BLOCKED_MISSING_INPUTS"
    assert result["blocked_reason"] == "candidate_inputs_missing"
    assert result["missing_inputs"] == ["precio_margen_basico"]


def test_unknown_when_no_pipeline_tool_requests_are_provided() -> None:
    payload = _base_input()
    payload["pipeline_tool_requests"] = []

    result = _build(payload)

    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "missing_pipeline_tool_requests"


def test_authorizes_execution_when_everything_is_ready() -> None:
    result = _build(_base_input())

    assert result["status"] == "EXECUTION_AUTHORIZED"
    assert result["execution_authorized"] is True
    assert result["pipeline_authorized"] is True
    assert result["safe_to_call_pipeline"] is True
    assert result["runtime_authorized"] is False
    assert result["autonomous_delivery_authorized"] is False
    assert result["authorized_pipeline_tool_requests"] == [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {
                "precio_venta": "sheet:Ventas.column:Precio",
                "costo_unitario": "sheet:Costos.column:CostoUnitario",
            },
            "source_pipeline_request_ref": "explicit_tool_request_candidate:precio_margen_basico",
            "request_kind": "AUTHORIZED_PIPELINE_TOOL_REQUEST",
            "executable": True,
        }
    ]


def test_authorizes_multiple_allowlisted_requests_deterministically() -> None:
    payload = _base_input()
    payload["pipeline_tool_requests"] = [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {
                "precio_venta": "sheet:Ventas.column:Precio",
                "costo_unitario": "sheet:Costos.column:CostoUnitario",
            },
        },
        {
            "tool_ref": "caja_diaria_triage",
            "inputs": {
                "saldo_inicial": "sheet:Caja.column:SaldoInicial",
                "ingresos": "sheet:Caja.column:Ingresos",
                "egresos": "sheet:Caja.column:Egresos",
            },
        },
    ]

    result = _build(payload)

    assert result["status"] == "EXECUTION_AUTHORIZED"
    assert [request["tool_ref"] for request in result["authorized_pipeline_tool_requests"]] == [
        "precio_margen_basico",
        "caja_diaria_triage",
    ]
    assert [request["executable"] for request in result["authorized_pipeline_tool_requests"]] == [True, True]


def test_never_authorizes_autonomous_delivery() -> None:
    cases = []
    blocked = _base_input()
    blocked["pipeline_candidate_status"] = "BLOCKED"
    cases.append(blocked)
    unsafe = _base_input()
    unsafe["unsafe_flags"] = ["x"]
    cases.append(unsafe)
    missing = _base_input()
    missing["missing_inputs"] = ["x"]
    cases.append(missing)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["autonomous_delivery_authorized"] is False


def test_module_source_does_not_import_pipeline_cli_delivery_llm_or_chatbot() -> None:
    import pymia.smartpyme.service_1_pipeline_request_execution_gate_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import pymia.smartpyme.service_1_pipeline_v1",
        "from pymia.smartpyme.service_1_pipeline_v1",
        "run_service_1_pipeline_v1",
        "import pymia.cli",
        "from pymia.cli",
        "service_1_operator",
        "delivery_flow",
        "case_delivery",
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

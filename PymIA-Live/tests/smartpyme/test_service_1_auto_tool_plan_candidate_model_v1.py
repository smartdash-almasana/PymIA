from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_auto_tool_plan_candidate_model_v1 import (
    SCHEMA_VERSION,
    build_service_1_auto_tool_plan_candidate_v1,
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
        "case_truth_status": "READY_FOR_TOOL_PLANNING",
        "supported_family": "FIRST_AID",
        "owner_axis": "precio_margen",
        "owner_problem": "Quiero revisar margen y precios.",
        "evidence_refs": {
            "precio_venta": "sheet:Ventas.column:Precio",
            "costo_unitario": "sheet:Costos.column:CostoUnitario",
        },
        "confirmed_column_refs": [
            "sheet:Ventas.column:Precio",
            "sheet:Costos.column:CostoUnitario",
        ],
        "ambiguous_column_refs": [],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_auto_tool_plan_candidate_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_truth_integration_is_not_ready_for_tool_planning() -> None:
    payload = _base_input()
    payload["case_truth_status"] = "NEEDS_EVIDENCE"
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "case_truth_status_not_ready_for_tool_planning"
    assert result["candidate_tool_refs"] == []


def test_blocks_if_supported_family_is_not_first_aid() -> None:
    payload = _base_input()
    payload["supported_family"] = "DETERMINISTIC_DIAGNOSIS"
    result = _build(payload)
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "supported_family_not_first_aid"


def test_blocks_if_candidate_tool_is_not_in_allowed_tool_refs() -> None:
    payload = _base_input()
    payload["allowed_tool_refs"] = ["caja_diaria_triage"]
    result = _build(payload)
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "candidate_tool_ref_not_allowlisted"
    assert result["candidate_tool_refs"] == ["precio_margen_basico"]


def test_needs_evidence_if_required_evidence_is_missing() -> None:
    payload = _base_input()
    payload["evidence_refs"] = {"precio_venta": "sheet:Ventas.column:Precio"}
    payload["confirmed_column_refs"] = ["sheet:Ventas.column:Precio"]
    result = _build(payload)
    assert result["status"] == "NEEDS_EVIDENCE"
    assert result["candidate_tool_refs"] == ["precio_margen_basico"]
    assert result["missing_evidence_refs"] == ["costo_unitario"]
    assert result["tool_plan_candidate"][0]["missing_inputs"] == ["costo_unitario"]


def test_needs_owner_input_if_required_evidence_points_to_ambiguous_column() -> None:
    payload = _base_input()
    payload["ambiguous_column_refs"] = ["sheet:Costos.column:CostoUnitario"]
    result = _build(payload)
    assert result["status"] == "NEEDS_OWNER_INPUT"
    assert result["candidate_tool_refs"] == ["precio_margen_basico"]
    assert result["owner_questions"]


def test_ready_for_precio_margen_basico_with_confirmed_references() -> None:
    result = _build(_base_input())
    assert result["status"] == "TOOL_PLAN_CANDIDATE_READY"
    assert result["candidate_tool_refs"] == ["precio_margen_basico"]
    assert result["tool_plan_candidate"] == [
        {
            "tool_ref": "precio_margen_basico",
            "reason": "Owner axis matched conservative V1 candidate precio_margen_basico.",
            "input_mapping_refs": {
                "precio_venta": "sheet:Ventas.column:Precio",
                "costo_unitario": "sheet:Costos.column:CostoUnitario",
            },
            "missing_inputs": [],
            "limitations": [
                "Planifica cálculo básico por referencia; no confirma rentabilidad real ni precio definitivo."
            ],
        }
    ]


def test_ready_for_caja_diaria_triage_with_confirmed_references() -> None:
    payload = _base_input()
    payload["owner_axis"] = "caja"
    payload["owner_problem"] = "No me cierra la caja diaria."
    payload["evidence_refs"] = {
        "saldo_inicial": "sheet:Caja.column:SaldoInicial",
        "ingresos": "sheet:Caja.column:Ingresos",
        "egresos": "sheet:Caja.column:Egresos",
    }
    payload["confirmed_column_refs"] = [
        "sheet:Caja.column:SaldoInicial",
        "sheet:Caja.column:Ingresos",
        "sheet:Caja.column:Egresos",
    ]
    result = _build(payload)
    assert result["status"] == "TOOL_PLAN_CANDIDATE_READY"
    assert result["candidate_tool_refs"] == ["caja_diaria_triage"]
    assert result["tool_plan_candidate"][0]["input_mapping_refs"] == payload["evidence_refs"]


def test_unknown_if_owner_axis_does_not_match_known_family() -> None:
    payload = _base_input()
    payload["owner_axis"] = "rrhh"
    payload["owner_problem"] = "Quiero revisar turnos."
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["candidate_tool_refs"] == []
    assert result["tool_plan_candidate"] == []


def test_never_authorizes_runtime_execution_tool_requests_or_autonomous_delivery() -> None:
    cases = []
    blocked = _base_input()
    blocked["case_truth_status"] = "NEEDS_OWNER_CONFIRMATION"
    cases.append(blocked)
    missing = _base_input()
    missing["evidence_refs"] = {"precio_venta": "sheet:Ventas.column:Precio"}
    missing["confirmed_column_refs"] = ["sheet:Ventas.column:Precio"]
    cases.append(missing)
    ambiguous = _base_input()
    ambiguous["ambiguous_column_refs"] = ["sheet:Ventas.column:Precio"]
    cases.append(ambiguous)
    cases.append(_base_input())
    for payload in cases:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["execution_authorized"] is False
        assert result["tool_requests_authorized"] is False
        assert result["autonomous_delivery_authorized"] is False


def test_result_does_not_return_executable_tool_requests_key() -> None:
    result = _build(_base_input())
    assert "tool_requests" not in result


def test_module_source_does_not_import_pipeline_cli_delivery_model_runtime_or_chatbot() -> None:
    import pymia.smartpyme.service_1_auto_tool_plan_candidate_model_v1 as module
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

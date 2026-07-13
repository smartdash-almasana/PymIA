from __future__ import annotations

from pymia.smartpyme.first_aid_tool_activation_evaluator_v1 import evaluate_first_aid_tool_activation


def _base_input(**overrides):
    payload = {
        "tool_ref": "precio_margen_basico",
        "owner_problem": "Quiero revisar precio y margen.",
        "service_depth": "FIRST_AID",
        "available_evidence": {"precio_venta": 1200, "costo_unitario": 800},
        "column_confirmation_status": {"precio_venta": "confirmed", "costo_unitario": "confirmed"},
        "requested_formula_refs": ["margen_bruto"],
        "requested_claims": [],
        "pack_seed_status": "CANDIDATE_SEED",
        "runtime_authorized": False,
    }
    payload.update(overrides)
    return payload


def test_blocks_missing_evidence():
    result = evaluate_first_aid_tool_activation(
        _base_input(available_evidence={"precio_venta": 1200})
    )

    assert result["activation_status"] == "BLOCKED_MISSING_EVIDENCE"
    assert result["missing_inputs"] == ["costo_unitario"]
    assert result["owner_questions"]
    assert result["runtime_authorized"] is False


def test_blocks_unconfirmed_column():
    result = evaluate_first_aid_tool_activation(
        _base_input(column_confirmation_status={"costo_unitario": "unconfirmed"})
    )

    assert result["activation_status"] == "BLOCKED_COLUMN_CONFIRMATION"
    assert result["missing_inputs"] == ["costo_unitario"]
    assert result["runtime_authorized"] is False


def test_blocks_restricted_formula():
    result = evaluate_first_aid_tool_activation(
        _base_input(requested_formula_refs=["resultado_neto"])
    )

    assert result["activation_status"] == "BLOCKED_RESTRICTED_FORMULA"
    assert result["missing_inputs"] == ["resultado_neto"]
    assert result["escalation_hint"] == "DETERMINISTIC_DIAGNOSIS"


def test_blocks_forbidden_claim():
    result = evaluate_first_aid_tool_activation(
        _base_input(requested_claims=["rentabilidad real confirmada"])
    )

    assert result["activation_status"] == "BLOCKED_FORBIDDEN_CLAIM"
    assert result["missing_inputs"] == ["rentabilidad real confirmada"]
    assert result["escalation_hint"] == "reformulate_or_escalate"


def test_blocks_scope_mismatch():
    result = evaluate_first_aid_tool_activation(
        _base_input(service_depth="DETERMINISTIC_DIAGNOSIS")
    )

    assert result["activation_status"] == "BLOCKED_SCOPE_MISMATCH"
    assert result["escalation_hint"] == "DETERMINISTIC_DIAGNOSIS"


def test_blocks_component_not_aligned_for_unknown_tool():
    result = evaluate_first_aid_tool_activation(
        _base_input(tool_ref="unknown_tool")
    )

    assert result["activation_status"] == "BLOCKED_COMPONENT_NOT_ALIGNED"
    assert result["escalation_hint"] == "seed_audit_required"


def test_conceptually_eligible_still_blocks_when_runtime_not_authorized():
    result = evaluate_first_aid_tool_activation(_base_input(runtime_authorized=False))

    assert result["activation_status"] == "BLOCKED_RUNTIME_NOT_AUTHORIZED"
    assert result["blocking_reasons"] == [
        "tool is conceptually eligible but runtime execution is not authorized"
    ]
    assert result["runtime_authorized"] is False


def test_evaluator_never_authorizes_runtime_even_when_input_requests_it():
    result = evaluate_first_aid_tool_activation(_base_input(runtime_authorized=True))

    assert result["activation_status"] == "BLOCKED_RUNTIME_NOT_AUTHORIZED"
    assert result["blocking_reasons"] == [
        "tool is conceptually eligible but runtime execution is not authorized"
    ]
    assert result["missing_inputs"] == []
    assert result["owner_questions"] == []
    assert result["runtime_authorized"] is False


def test_blocks_formula_not_allowed_for_tool():
    result = evaluate_first_aid_tool_activation(
        _base_input(requested_formula_refs=["flujo_caja_neto"])
    )

    assert result["activation_status"] == "BLOCKED_RESTRICTED_FORMULA"
    assert result["missing_inputs"] == ["flujo_caja_neto"]
    assert result["escalation_hint"] == "tool_contract_audit_required"


def test_requested_claims_are_case_insensitive():
    result = evaluate_first_aid_tool_activation(
        _base_input(requested_claims=["RENTABILIDAD REAL CONFIRMADA"])
    )

    assert result["activation_status"] == "BLOCKED_FORBIDDEN_CLAIM"
    assert result["missing_inputs"] == ["rentabilidad real confirmada"]


def test_rejects_invalid_pack_seed_status_input():
    try:
        evaluate_first_aid_tool_activation(_base_input(pack_seed_status="READY"))
    except ValueError as exc:
        assert "pack_seed_status" in str(exc)
    else:
        raise AssertionError("expected ValueError for invalid pack_seed_status")


def test_rejects_invalid_contract_status():
    contract = {
        "status": "READY",
        "allowed_service_depth": ["FIRST_AID"],
        "tool_activation_matrix": [],
    }
    try:
        evaluate_first_aid_tool_activation(_base_input(), activation_contract=contract)
    except ValueError as exc:
        assert "activation_contract.status" in str(exc)
    else:
        raise AssertionError("expected ValueError for invalid contract status")


def test_rejects_invalid_seed_status():
    seed = {
        "status": "READY",
        "tool_refs": [],
        "tool_component_mapping": [],
    }
    try:
        evaluate_first_aid_tool_activation(_base_input(), pack_seed=seed)
    except ValueError as exc:
        assert "pack_seed.status" in str(exc)
    else:
        raise AssertionError("expected ValueError for invalid seed status")


def test_blocks_component_required_mismatch():
    contract = {
        "status": "CONTRACT_ONLY",
        "allowed_service_depth": ["FIRST_AID"],
        "tool_activation_matrix": [
            {
                "tool_ref": "precio_margen_basico",
                "component_required": "wrong_component",
                "minimum_evidence": ["precio_venta", "costo_unitario"],
                "allowed_formulas": ["margen_bruto"],
                "restricted_formulas": [],
                "forbidden_claims": [],
                "owner_questions_if_missing": [],
                "limitations": [],
            }
        ],
    }

    result = evaluate_first_aid_tool_activation(
        _base_input(), activation_contract=contract
    )

    assert result["activation_status"] == "BLOCKED_COMPONENT_NOT_ALIGNED"
    assert result["escalation_hint"] == "seed_audit_required"


def test_supports_all_five_first_aid_tools_with_minimum_evidence():
    cases = [
        (
            "caja_diaria_triage",
            {"saldo_inicial": 100, "ingresos": 500, "egresos": 200},
            {"saldo_inicial": "confirmed", "ingresos": "confirmed", "egresos": "confirmed"},
        ),
        (
            "precio_margen_basico",
            {"precio_venta": 1200, "costo_unitario": 800},
            {"precio_venta": "confirmed", "costo_unitario": "confirmed"},
        ),
        (
            "stock_alertas_basicas",
            {"producto": "A", "stock_actual": 3, "stock_minimo": 5},
            {"producto": "confirmed", "stock_actual": "confirmed", "stock_minimo": "confirmed"},
        ),
        (
            "gastos_triage",
            {"concepto": "luz", "importe": 1000},
            {"concepto": "confirmed", "importe": "confirmed"},
        ),
        (
            "proveedores_precio_variacion_triage",
            {"proveedor": "P", "producto_o_insumo": "harina", "precio_o_costo": 100},
            {"proveedor": "confirmed", "producto_o_insumo": "confirmed", "precio_o_costo": "confirmed"},
        ),
    ]

    for tool_ref, evidence, column_status in cases:
        result = evaluate_first_aid_tool_activation(
            _base_input(
                tool_ref=tool_ref,
                available_evidence=evidence,
                column_confirmation_status=column_status,
                requested_formula_refs=[],
                runtime_authorized=False,
            )
        )
        assert result["activation_status"] == "BLOCKED_RUNTIME_NOT_AUTHORIZED"

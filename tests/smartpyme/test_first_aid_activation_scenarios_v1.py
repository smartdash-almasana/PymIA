from __future__ import annotations

from pymia.smartpyme.first_aid_tool_activation_evaluator_v1 import evaluate_first_aid_tool_activation


def _activation_input(
    *,
    tool_ref: str,
    available_evidence: dict,
    column_confirmation_status: dict,
    requested_formula_refs: list[str] | None = None,
    requested_claims: list[str] | None = None,
    service_depth: str = "FIRST_AID",
    runtime_authorized: bool = False,
):
    return {
        "tool_ref": tool_ref,
        "owner_problem": "Escenario documental First Aid.",
        "service_depth": service_depth,
        "available_evidence": available_evidence,
        "column_confirmation_status": column_confirmation_status,
        "requested_formula_refs": requested_formula_refs or [],
        "requested_claims": requested_claims or [],
        "pack_seed_status": "CANDIDATE_SEED",
        "runtime_authorized": runtime_authorized,
    }


def test_scenario_a_precio_margen_conceptually_eligible_but_runtime_blocked():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="precio_margen_basico",
            available_evidence={"precio_venta": 1200, "costo_unitario": 800},
            column_confirmation_status={"precio_venta": "confirmed", "costo_unitario": "confirmed"},
            requested_formula_refs=["margen_bruto"],
        )
    )

    assert result["activation_status"] == "BLOCKED_RUNTIME_NOT_AUTHORIZED"
    assert result["runtime_authorized"] is False


def test_scenario_b_precio_margen_missing_cost():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="precio_margen_basico",
            available_evidence={"precio_venta": 1200},
            column_confirmation_status={"precio_venta": "confirmed"},
            requested_formula_refs=["margen_bruto"],
        )
    )

    assert result["activation_status"] == "BLOCKED_MISSING_EVIDENCE"
    assert result["missing_inputs"] == ["costo_unitario"]
    assert result["owner_questions"]


def test_scenario_c_caja_diaria_ambiguous_income_column():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="caja_diaria_triage",
            available_evidence={"saldo_inicial": 100, "ingresos": 500, "egresos": 200},
            column_confirmation_status={
                "saldo_inicial": "confirmed",
                "ingresos": "ambiguous",
                "egresos": "confirmed",
            },
            requested_formula_refs=["flujo_caja_neto"],
        )
    )

    assert result["activation_status"] == "BLOCKED_COLUMN_CONFIRMATION"
    assert result["missing_inputs"] == ["ingresos"]


def test_scenario_d_stock_restricted_rotation_formula():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="stock_alertas_basicas",
            available_evidence={"producto": "A", "stock_actual": 3, "stock_minimo": 5},
            column_confirmation_status={
                "producto": "confirmed",
                "stock_actual": "confirmed",
                "stock_minimo": "confirmed",
            },
            requested_formula_refs=["rotacion_inventario"],
        )
    )

    assert result["activation_status"] == "BLOCKED_RESTRICTED_FORMULA"
    assert result["missing_inputs"] == ["rotacion_inventario"]
    assert result["escalation_hint"] == "DETERMINISTIC_DIAGNOSIS"


def test_scenario_e_gastos_forbidden_accounting_claim():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="gastos_triage",
            available_evidence={"concepto": "luz", "importe": 1000},
            column_confirmation_status={"concepto": "confirmed", "importe": "confirmed"},
            requested_claims=["clasificación contable definitiva"],
        )
    )

    assert result["activation_status"] == "BLOCKED_FORBIDDEN_CLAIM"
    assert result["missing_inputs"] == ["clasificación contable definitiva"]


def test_scenario_f_proveedores_conceptually_eligible_but_runtime_blocked():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="proveedores_precio_variacion_triage",
            available_evidence={
                "proveedor": "Proveedor A",
                "producto_o_insumo": "harina",
                "precio_o_costo": 100,
            },
            column_confirmation_status={
                "proveedor": "confirmed",
                "producto_o_insumo": "confirmed",
                "precio_o_costo": "confirmed",
            },
            requested_formula_refs=[],
        )
    )

    assert result["activation_status"] == "BLOCKED_RUNTIME_NOT_AUTHORIZED"
    assert result["runtime_authorized"] is False


def test_scenario_g_scope_mismatch_goes_to_service_2():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="precio_margen_basico",
            available_evidence={"precio_venta": 1200, "costo_unitario": 800},
            column_confirmation_status={"precio_venta": "confirmed", "costo_unitario": "confirmed"},
            requested_formula_refs=["margen_bruto"],
            service_depth="DETERMINISTIC_DIAGNOSIS",
        )
    )

    assert result["activation_status"] == "BLOCKED_SCOPE_MISMATCH"
    assert result["escalation_hint"] == "DETERMINISTIC_DIAGNOSIS"


def test_scenario_h_unknown_tool_not_aligned():
    result = evaluate_first_aid_tool_activation(
        _activation_input(
            tool_ref="unknown_tool",
            available_evidence={},
            column_confirmation_status={},
        )
    )

    assert result["activation_status"] == "BLOCKED_COMPONENT_NOT_ALIGNED"
    assert result["escalation_hint"] == "seed_audit_required"

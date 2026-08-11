from __future__ import annotations

from types import SimpleNamespace

from pymia.smartpyme import service_1_assisted_web_v1 as web


def _app_with_case(tmp_path):
    app = web.AssistedWebApplicationV1(output_dir=tmp_path / "outputs")
    session_id = "workspace"
    state = app.session(session_id)
    state.tenant_identity_contract = SimpleNamespace(case_id="case-rivadavia-2026-08")
    state.ingestion_output = {
        "normalized_tables": [
            {
                "sheet_name": "Expensas",
                "rows": [
                    {"unidad": "UF-12", "saldo": "250", "expensa": "100"},
                    {"unidad": "UF-13", "saldo": "0", "expensa": "100"},
                ],
            },
            {
                "sheet_name": "Gastos",
                "rows": [
                    {"rubro_gasto": "Limpieza", "importe_gasto": "150"},
                ],
            },
            {
                "sheet_name": "Presupuesto",
                "rows": [
                    {
                        "rubro_presupuesto": "Limpieza",
                        "presupuesto": "100",
                        "historico": "100",
                    },
                ],
            },
        ]
    }
    app.bind_consorcio_case_context(
        session_id=session_id,
        case_id="case-rivadavia-2026-08",
        consorcio_id="rivadavia-1200",
        consorcio_name="Rivadavia 1200",
        period="2026-08",
        source_files=("agosto.xlsx",),
    )
    return app, session_id


def test_workspace_reuses_collection_aging_confirmation_only_inside_same_case(tmp_path):
    app, session_id = _app_with_case(tmp_path)

    status, first_page = app.consorcios_case_workspace(session_id=session_id)
    assert status == 200
    assert "Rivadavia 1200" in first_page
    assert "2026-08" in first_page
    assert 'name="unidad_funcional"' in first_page

    status, result = app.run_consorcios_collection_aging(
        session_id=session_id,
        fields={
            "sheet_name": "Expensas",
            "unidad_funcional": "unidad",
            "saldo_anterior": "saldo",
            "expensa_mes": "expensa",
        },
    )
    assert status == 200
    assert "UF-12" in result
    assert "2.5" in result

    status, workspace = app.consorcios_case_workspace(session_id=session_id)
    assert status == 200
    assert "Las columnas de este control ya fueron confirmadas para este caso." in workspace

    status, rerun = app.run_consorcios_collection_aging(session_id=session_id, fields={})
    assert status == 200
    assert "UF-12" in rerun
    assert "2.5" in rerun

    app.bind_consorcio_case_context(
        session_id=session_id,
        case_id="case-rivadavia-2026-09",
        consorcio_id="rivadavia-1200",
        consorcio_name="Rivadavia 1200",
        period="2026-09",
        source_files=("septiembre.xlsx",),
    )
    status, new_case_workspace = app.consorcios_case_workspace(session_id=session_id)
    assert status == 200
    assert 'name="unidad_funcional"' in new_case_workspace
    assert app.session(session_id).consorcio_case_context.collection_aging_bindings == {}


def test_workspace_reuses_expense_variance_confirmation_and_keeps_bank_and_radar_entries(tmp_path):
    app, session_id = _app_with_case(tmp_path)

    status, result = app.run_consorcios_expense_variance(
        session_id=session_id,
        fields={
            "expense_sheet": "Gastos",
            "expense_rubro": "rubro_gasto",
            "expense_importe": "importe_gasto",
            "budget_sheet": "Presupuesto",
            "budget_rubro": "rubro_presupuesto",
            "presupuesto_mensual": "presupuesto",
            "promedio_historico": "historico",
        },
    )
    assert status == 200
    assert "Limpieza" in result
    assert "50" in result

    status, workspace = app.consorcios_case_workspace(session_id=session_id)
    assert status == 200
    assert "Las columnas de gastos y presupuesto ya fueron confirmadas para este caso." in workspace
    assert "Conciliar banco" in workspace
    assert "Configurar RADAR" in workspace

    status, rerun = app.run_consorcios_expense_variance(session_id=session_id, fields={})
    assert status == 200
    assert "Limpieza" in rerun
    assert "50" in rerun

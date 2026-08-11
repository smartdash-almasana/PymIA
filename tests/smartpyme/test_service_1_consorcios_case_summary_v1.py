from __future__ import annotations

from pymia.smartpyme import service_1_assisted_web_v1 as web


def _bind_case(app: web.AssistedWebApplicationV1, session_id: str, *, period: str = "2026-08") -> None:
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id="tenant-summary",
        cliente_id="cliente-summary",
        owner_actor_id="owner-summary",
        owner_actor_role="OWNER",
    )
    state = app.session(session_id)
    state.tenant_identity_contract = type("Identity", (), {"case_id": f"case-{period}"})()
    state.ingestion_output = {"normalized_tables": [{"sheet_name": "Datos", "rows": [{"x": 1}]}]}
    app.bind_consorcio_case_context(
        session_id=session_id,
        case_id=f"case-{period}",
        consorcio_id="rivadavia-1200",
        consorcio_name="Rivadavia 1200",
        period=period,
        source_files=(f"{period}.xlsx",),
    )
    # bind_consorcio_case_context intentionally clears case-local derived state;
    # restore the verified identity contract exactly as receive_xlsx does in production.
    state.tenant_identity_contract = type("Identity", (), {"case_id": f"case-{period}"})()


def _bank_packet() -> dict[str, object]:
    return {
        "status": web.STATUS_RECONCILIATION_REVIEW_READY,
        "reconciliation_run": {
            "case_id": "bank-case",
            "reconciliation_type": web.BANK_RECONCILIATION,
            "assisted_review": {
                "review_result": {
                    "exact_matches_summary": {"items": [{"amount": "100"}]},
                    "bank_pending_summary": {"items": [{"amount": "50"}]},
                }
            },
        },
    }


def test_case_summary_composes_existing_results_radar_review_and_download(tmp_path) -> None:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path)
    _bind_case(app, "summary")
    state = app.session("summary")
    state.consorcios_results = {
        "collection_aging": {"rows": [{"unidad_funcional": "UF-12"}, {"unidad_funcional": "UF-13"}]},
        "expense_variance": {"rows": [{"rubro": "Limpieza"}]},
    }
    state.consorcios_radar_events = {
        "collection_aging": [
            {"communication_level": "ALERT", "observable_ref": "consorcios.debt_equivalent_periods"}
        ],
        "expense_variance": [
            {"communication_level": "NOTIFICATION", "observable_ref": "consorcios.expense_budget_deviation_pct"}
        ],
    }
    state.reconciliation_result = _bank_packet()
    state.reconciliation_decisions = [
        {"review_item_ref": "exact:1", "decision": "CONFIRM"}
    ]

    status, page = app.consorcios_case_summary(session_id="summary")

    assert status == 200
    assert "Resumen del período" in page
    assert "Rivadavia 1200" in page
    assert "2026-08" in page
    assert "Realizado · 2 unidad(es) revisada(s)" in page
    assert "Realizado · 1 rubro(s) revisado(s)" in page
    assert "Realizado · 2 caso(s) para revisión" in page
    assert "ALERT" in page
    assert "NOTIFICATION" in page
    assert "1 caso(s) bancario(s) todavía requieren una decisión humana" in page
    assert "/download-reconciliation-workpaper" in page
    assert "PymIA no asigna severidad" in page


def test_new_case_clears_summary_results_and_does_not_inherit_previous_period(tmp_path) -> None:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path)
    _bind_case(app, "summary")
    state = app.session("summary")
    state.consorcios_results["collection_aging"] = {"rows": [{"unidad_funcional": "UF-12"}]}
    state.consorcios_radar_events["collection_aging"] = [{"communication_level": "ALERT"}]
    state.reconciliation_result = _bank_packet()
    state.reconciliation_decisions = [{"review_item_ref": "exact:1", "decision": "CONFIRM"}]

    app.bind_consorcio_case_context(
        session_id="summary",
        case_id="case-2026-09",
        consorcio_id="rivadavia-1200",
        consorcio_name="Rivadavia 1200",
        period="2026-09",
        source_files=("2026-09.xlsx",),
    )
    state.tenant_identity_contract = type("Identity", (), {"case_id": "case-2026-09"})()

    status, page = app.consorcios_case_summary(session_id="summary")

    assert status == 200
    assert "2026-09" in page
    assert page.count("Pendiente") >= 3
    assert "Sin eventos RADAR" in page
    assert "0 caso(s) bancario(s)" in page
    assert "/download-reconciliation-workpaper" not in page

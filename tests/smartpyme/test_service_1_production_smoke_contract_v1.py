from pathlib import Path

import pytest

from tools import service_1_production_smoke_v1 as smoke


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_production_smoke_fails_closed_when_target_is_missing(monkeypatch) -> None:
    for name in (smoke.BASE_URL_ENV, smoke.SUPABASE_URL_ENV, smoke.SUPABASE_PUBLISHABLE_KEY_ENV, smoke.SMOKE_EMAIL_ENV, smoke.SMOKE_PASSWORD_ENV):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(smoke.SmokeFailure, match=smoke.BASE_URL_ENV):
        smoke.run()


def test_production_smoke_accepts_sem8_owner_actions() -> None:
    page = '<input type="radio" name="action_decision-1" value="ACCEPT">'
    assert smoke._answers(page) == {"action_decision-1": "ACCEPT"}


def test_production_smoke_still_accepts_canonical_answer_fields() -> None:
    page = '<input type="radio" name="answer_q-1" value="period_sales_total">'
    assert smoke._answers(page) == {"answer_q-1": "period_sales_total"}


def test_production_smoke_selects_durable_case_link_without_snapshot_suffix() -> None:
    page = (
        '<a href="/case?case_ref=case_new::sold_vs_collected_gap">resultado</a>'
        '<a href="/case?case_ref=case_persisted">evidencia</a>'
    )
    assert smoke._durable_case_link(page) == "/case?case_ref=case_persisted"


def test_production_smoke_builds_governed_ren_001_fixture() -> None:
    from io import BytesIO
    from openpyxl import load_workbook

    workbook = load_workbook(BytesIO(smoke._ren_001_xlsx_bytes(include_taxes=True)), data_only=True)
    assert workbook["Ventas"]["D2"].value == 1
    assert workbook["Ventas"]["E2"].value == 60
    assert workbook["Ventas"]["F3"].value == 0.1
    assert workbook["Productos"]["C2"].value == 28
    assert workbook["Resumen"]["A2"].value == 20


def test_production_smoke_maps_discount_fraction_owner_unit() -> None:
    page = '<input type="radio" name="unit_discount-q" value="DISCOUNT_FRACTION_0_1">'
    assert smoke._unit_answers(page) == {"unit_discount-q": "DISCOUNT_FRACTION_0_1"}


def test_production_smoke_unescapes_sem8_relationship_action_names() -> None:
    page = (
        '<input type="radio" '
        'name="action_dialogue:relationship:baseline:relationship:1:Productos.ProductoID-&gt;Ventas.ProductoID" '
        'value="ACCEPT">'
    )
    assert smoke._answers(page) == {
        "action_dialogue:relationship:baseline:relationship:1:Productos.ProductoID->Ventas.ProductoID": "ACCEPT"
    }

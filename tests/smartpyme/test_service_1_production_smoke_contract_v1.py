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

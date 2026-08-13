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

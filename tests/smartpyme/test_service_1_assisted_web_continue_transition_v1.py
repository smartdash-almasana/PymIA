from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_MODULE = ROOT / "pymia" / "smartpyme" / "service_1_assisted_web_v1.py"


def test_htmx_responses_are_fragments_not_nested_documents() -> None:
    module = WEB_MODULE.read_text(encoding="utf-8")

    assert 'self.headers.get("HX-Request")' in module
    assert "_send_fragment" in module


def test_file_received_continue_posts_to_column_confirmation() -> None:
    module = WEB_MODULE.read_text(encoding="utf-8")

    assert 'action="/confirm-columns"' in module
    assert 'hx-post="/confirm-columns"' in module
    assert 'hx-target="#app"' in module
    assert 'hx-swap="outerHTML"' in module

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_MODULE = ROOT / "pymia" / "smartpyme" / "service_1_assisted_web_v1.py"


def test_htmx_responses_are_fragments_not_nested_documents() -> None:
    module = WEB_MODULE.read_text(encoding="utf-8")

    assert 'self.headers.get("HX-Request")' in module
    assert "_send_fragment" in module


def test_upload_runs_canonical_unconfirmed_ingestion_without_first_dialog() -> None:
    module = WEB_MODULE.read_text(encoding="utf-8")

    assert "build_service_1_unconfirmed_canonical_ingestion_output_v1" in module
    assert "_run_product_root(" in module
    assert "_semantic_questions_page(state.semantic_questions)" in module
    assert "/confirm-columns" not in module
    assert "meaning_" not in module

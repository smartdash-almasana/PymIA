from __future__ import annotations

from pymia.smartpyme import service_1_assisted_web_v1 as web


def test_assisted_web_exposes_exactly_the_twelve_productive_reviews() -> None:
    visible_refs = tuple(item[0] for item in web._REVIEW_OPTIONS)
    visible_titles = tuple(item[1] for item in web._REVIEW_OPTIONS)

    assert len(visible_refs) == 12
    assert len(set(visible_refs)) == 12
    assert "net_margin_real" in visible_refs
    assert "Margen neto real" in visible_titles
    assert "dpo" not in visible_refs
    assert "Tiempo de pago" not in visible_titles

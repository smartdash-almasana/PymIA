from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_MODULE = ROOT / "pymia" / "smartpyme" / "service_1_assisted_web_v1.py"
UI_MODULE = ROOT / "pymia" / "smartpyme" / "service_1_ui_v1.py"
TEMPLATE = ROOT / "pymia" / "smartpyme" / "templates" / "service_1_assisted_web_v1.html"
STYLES = ROOT / "pymia" / "smartpyme" / "static" / "service_1_v1.css"


def _read(path: Path) -> str:
    assert path.exists(), f"Missing required assisted-web artifact: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _visible_surface() -> str:
    return _read(TEMPLATE) + "\n" + _read(UI_MODULE) + "\n" + _read(WEB_MODULE)


def test_assisted_web_artifacts_exist() -> None:
    assert WEB_MODULE.exists()
    assert UI_MODULE.exists()
    assert TEMPLATE.exists()
    assert STYLES.exists()


def test_visible_interface_uses_plain_spanish() -> None:
    surface = _visible_surface()

    required_text = (
        "PymIA · Servicio 1",
        "Subí tu Excel",
        "Leer mi Excel",
        "¿Qué querés que PymIA te devuelva?",
        "Podés analizar ahora",
        "No lo puedo confirmar ahora",
        "Datos utilizados",
        "Qué conviene tener en cuenta",
    )
    for text in required_text:
        assert text in surface

    forbidden_visible_terms = (
        "pipeline",
        "runtime",
        "binding",
        "kernel",
        "outcome",
        "delivery",
        "pathology",
        "patología",
        "capability",
    )
    template = _read(TEMPLATE).lower()
    for term in forbidden_visible_terms:
        assert term not in template


def test_htmx_is_used_without_frontend_framework() -> None:
    surface = _visible_surface().lower()

    assert "htmx" in surface
    assert "hx-post" in surface or "hx-get" in surface
    assert "hx-target" in surface
    assert "react.js" not in surface
    assert "vue.js" not in surface
    assert "angular.js" not in surface


def test_primary_excel_journey_does_not_depend_on_htmx() -> None:
    presentation = _read(UI_MODULE)

    assert '<form action="/upload" method="post" enctype="multipart/form-data"' in presentation
    assert 'action="/confirm-meanings" method="post"' in presentation
    assert '<form action="/upload" method="post" enctype="multipart/form-data" hx-post=' not in presentation


def test_accessibility_contract_is_present() -> None:
    surface = _visible_surface().lower()
    css = _read(STYLES)

    assert "<main" in surface
    assert "<h1" in surface
    assert "<label" in surface
    assert "aria-live" in surface
    assert "role=\"alert\"" in surface or "role='alert'" in surface
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
    assert "htmx:afterswap" in surface


def test_vertical_slice_delegates_to_product_root() -> None:
    module = _read(WEB_MODULE)

    assert "run_service_1_product_pipeline_v1" in module
    assert "service_1_product_pipeline_v1" in module
    assert "requested_capability" in module
    assert "owner_answers" in module
    assert "deliver_result" in module


def test_interface_does_not_reimplement_governed_formulas() -> None:
    module = _read(WEB_MODULE)

    forbidden_formula_fragments = (
        "interest_expense / ebitda",
        "closing_index / origin_index",
        "current_assets / current_liabilities",
        "net_income + depreciation",
    )
    for fragment in forbidden_formula_fragments:
        assert fragment not in module


def test_only_xlsx_upload_is_advertised() -> None:
    surface = _visible_surface().lower()

    assert ".xlsx" in surface
    assert "accept=\".xlsx" in surface or "accept='.xlsx" in surface
    assert ".pdf" not in surface
    assert "ocr" not in surface


def test_uncertainty_is_a_first_class_owner_answer() -> None:
    surface = _visible_surface()

    assert "No lo puedo confirmar ahora" in surface
    assert "value=\"not_sure\"" in surface or "value='not_sure'" in surface


def test_result_exposes_data_and_limits_without_causal_diagnosis() -> None:
    surface = _visible_surface()

    assert "Datos utilizados" in surface
    assert "datos confirmados" in surface.lower()
    assert "no atribuye automáticamente causas" in surface.lower()
    assert "diagnóstico causal" not in surface.lower()

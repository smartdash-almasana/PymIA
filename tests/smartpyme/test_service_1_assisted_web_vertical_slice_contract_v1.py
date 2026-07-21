from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_MODULE = ROOT / "pymia" / "smartpyme" / "service_1_assisted_web_v1.py"
TEMPLATE = ROOT / "pymia" / "smartpyme" / "templates" / "service_1_assisted_web_v1.html"
STYLES = ROOT / "pymia" / "smartpyme" / "static" / "service_1_assisted_web_v1.css"


def _read(path: Path) -> str:
    assert path.exists(), f"Missing required assisted-web artifact: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_assisted_web_artifacts_exist() -> None:
    assert WEB_MODULE.exists()
    assert TEMPLATE.exists()
    assert STYLES.exists()


def test_visible_interface_uses_plain_spanish() -> None:
    html = _read(TEMPLATE)

    required_text = (
        "Revisar información de mi negocio",
        "Elegir archivo",
        "Tu archivo no se modifica",
        "No estoy seguro",
        "¿Qué querés revisar?",
        "Ver cómo se calculó",
    )
    for text in required_text:
        assert text in html

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
    lowered = html.lower()
    for term in forbidden_visible_terms:
        assert term not in lowered


def test_htmx_is_used_without_frontend_framework() -> None:
    html = _read(TEMPLATE)
    lowered = html.lower()

    assert "htmx" in lowered
    assert "hx-post" in lowered or "hx-get" in lowered
    assert "hx-target" in lowered
    assert "react" not in lowered
    assert "vue" not in lowered
    assert "angular" not in lowered


def test_accessibility_contract_is_present() -> None:
    html = _read(TEMPLATE)
    css = _read(STYLES)
    lowered = html.lower()

    assert "<main" in lowered
    assert "<h1" in lowered
    assert "<label" in lowered
    assert "aria-live" in lowered
    assert "role=\"alert\"" in lowered or "role='alert'" in lowered
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css


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
    html = _read(TEMPLATE).lower()

    assert ".xlsx" in html
    assert "accept=\".xlsx" in html or "accept='.xlsx" in html
    assert ".pdf" not in html
    assert "ocr" not in html


def test_uncertainty_is_a_first_class_owner_answer() -> None:
    html = _read(TEMPLATE)

    assert "No estoy seguro" in html
    assert "value=\"not_sure\"" in html or "value='not_sure'" in html


def test_result_exposes_data_and_limits_without_causal_diagnosis() -> None:
    html = _read(TEMPLATE)

    assert "Datos utilizados" in html
    assert "Este cálculo describe una relación matemática" in html
    assert "No determina por sí solo" in html
    assert "diagnóstico causal" not in html.lower()

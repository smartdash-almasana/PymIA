from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme import service_1_assisted_web_v1 as web


def _ready_state(app: web.AssistedWebApplicationV1, session_id: str) -> None:
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id="tenant_admin",
        cliente_id="cliente_admin",
        owner_actor_id="owner-1",
        owner_actor_role="owner",
    )
    state = app.session(session_id)
    state.ingestion_output = {"sheet_name": "Datos", "filename": f"{session_id}.xlsx"}
    state.semantic_answers = {"q1": "sold_amount", "q2": "collected_amount"}


def _packet(output_path: Path) -> dict[str, object]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"PK-case")
    return {
        "status": web.STATUS_COMPUTATION_PLAN_READY,
        "semantic_run": {},
        "bounded_outcome": {"capability_ref": "sold_vs_collected_gap"},
        "delivery_result": {
            "status": "DELIVERED",
            "delivery": {"output_path": str(output_path)},
        },
        "delivery_generated": True,
    }


def test_consorcio_case_context_requires_identity_fields_and_month_period(tmp_path: Path) -> None:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path / "outputs")

    with pytest.raises(ValueError):
        app.bind_consorcio_case_context(
            session_id="s1",
            case_id="case-a",
            consorcio_id="",
            consorcio_name="Cabildo 100",
            period="2026-07",
            source_files=("cabildo.xlsx",),
        )

    with pytest.raises(ValueError):
        app.bind_consorcio_case_context(
            session_id="s1",
            case_id="case-a",
            consorcio_id="cabildo-100",
            consorcio_name="Cabildo 100",
            period="julio-2026",
            source_files=("cabildo.xlsx",),
        )


def test_home_exposes_optional_consorcio_and_period_context_fields() -> None:
    page = web._home_page()

    assert 'name="consorcio_id"' in page
    assert 'name="consorcio_name"' in page
    assert 'name="period"' in page
    assert 'type="month"' in page


def test_same_tenant_two_consorcios_get_distinct_review_output_directories(monkeypatch, tmp_path: Path) -> None:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path / "outputs")
    captured: dict[str, Path] = {}

    for session_id, consorcio_id, consorcio_name in (
        ("session-a", "cabildo-100", "Cabildo 100"),
        ("session-b", "rivadavia-200", "Rivadavia 200"),
    ):
        _ready_state(app, session_id)
        app.bind_consorcio_case_context(
            session_id=session_id,
            case_id=f"case-{consorcio_id}",
            consorcio_id=consorcio_id,
            consorcio_name=consorcio_name,
            period="2026-07",
            source_files=(f"{consorcio_id}.xlsx",),
        )

    def fake_root(**kwargs):
        output_dir = Path(kwargs["output_dir"])
        key = output_dir.parts[-3]
        captured[key] = output_dir
        return _packet(output_dir / "service_1_liq_001_result.xlsx")

    monkeypatch.setattr(web, "_run_product_root", fake_root)

    status_a, _ = app.run_review(session_id="session-a", requested_capability="sold_vs_collected_gap")
    status_b, _ = app.run_review(session_id="session-b", requested_capability="sold_vs_collected_gap")

    assert status_a == 200
    assert status_b == 200
    assert captured["cabildo-100"] != captured["rivadavia-200"]
    assert app.session("session-a").consorcio_case_context.case_status == "READY"
    assert app.session("session-b").consorcio_case_context.case_status == "READY"


def test_delivery_reader_fails_closed_on_cross_consorcio_path(tmp_path: Path) -> None:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path / "outputs")
    _ready_state(app, "session-a")
    _ready_state(app, "session-b")

    app.bind_consorcio_case_context(
        session_id="session-a",
        case_id="case-a",
        consorcio_id="cabildo-100",
        consorcio_name="Cabildo 100",
        period="2026-07",
        source_files=("cabildo.xlsx",),
    )
    app.bind_consorcio_case_context(
        session_id="session-b",
        case_id="case-b",
        consorcio_id="rivadavia-200",
        consorcio_name="Rivadavia 200",
        period="2026-07",
        source_files=("rivadavia.xlsx",),
    )

    output_a = app._review_output_dir(session_id="session-a") / "service_1_liq_001_result.xlsx"
    app.session("session-a").last_review_result = _packet(output_a)
    app.session("session-b").last_review_result = app.session("session-a").last_review_result

    filename, content = app.read_sales_collections_delivery(session_id="session-a")
    assert filename == "service_1_liq_001_result.xlsx"
    assert content == b"PK-case"

    with pytest.raises(ValueError, match="delivery path is invalid"):
        app.read_sales_collections_delivery(session_id="session-b")

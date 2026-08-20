from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme import service_1_assisted_web_v1 as web


def _ready_app(tmp_path: Path) -> web.AssistedWebApplicationV1:
    app = web.AssistedWebApplicationV1(output_dir=tmp_path / "outputs")
    state = app.session("session-ren")
    state.ingestion_output = {"sheet_name": "Margen", "filename": "margen.xlsx"}
    state.semantic_answers = {"q1": "sale_price", "q2": "costs", "q3": "taxes"}
    return app


def _ren_packet(*, delivery_generated: bool, output_path: Path | None = None) -> dict[str, object]:
    delivery_result = None
    if output_path is not None:
        delivery_result = {
            "status": "DELIVERED",
            "delivery": {"output_path": str(output_path)},
        }
    return {
        "status": web.STATUS_COMPUTATION_PLAN_READY,
        "semantic_run": {},
        "computation_result": {
            "status": "EVALUATED",
            "computed": {"net_margin_amount": 400.0, "net_margin_percentage": 26.67},
        },
        "bounded_outcome": {
            "capability_ref": "net_margin_real",
            "finding": "La evidencia confirmada muestra un margen neto real positivo.",
            "computed_results": {"net_margin_amount": 400.0},
            "limitations": ["Resultado acotado a la evidencia confirmada."],
        },
        "delivery_result": delivery_result,
        "delivery_generated": delivery_generated,
    }


def test_web_requests_existing_product_delivery_for_ren_001(monkeypatch, tmp_path: Path) -> None:
    app = _ready_app(tmp_path)
    captured: dict[str, object] = {}

    def fake_root(**kwargs):
        captured.update(kwargs)
        return _ren_packet(delivery_generated=True)

    monkeypatch.setattr(web, "_run_product_root", fake_root)

    status, page = app.run_review(
        session_id="session-ren",
        requested_capability="net_margin_real",
    )

    assert status == 200
    assert captured["requested_capability"] == "net_margin_real"
    assert captured["deliver_result"] is True
    assert 'href="/download-net-margin"' in page


def test_ren_001_page_does_not_offer_download_without_delivery(monkeypatch, tmp_path: Path) -> None:
    app = _ready_app(tmp_path)
    monkeypatch.setattr(
        web,
        "_run_product_root",
        lambda **_: _ren_packet(delivery_generated=False),
    )

    status, page = app.run_review(
        session_id="session-ren",
        requested_capability="net_margin_real",
    )

    assert status == 200
    assert 'href="/download-net-margin"' not in page
    assert "Resultado listo" in page


def test_read_net_margin_delivery_reads_only_current_session_delivery(tmp_path: Path) -> None:
    app = _ready_app(tmp_path)
    output = app.output_dir / "service_1_ren_001_result.xlsx"
    output.write_bytes(b"PK-ren-001")
    app.session("session-ren").last_review_result = _ren_packet(
        delivery_generated=True,
        output_path=output,
    )

    filename, content = app.read_net_margin_delivery(session_id="session-ren")

    assert filename == "service_1_ren_001_result.xlsx"
    assert content == b"PK-ren-001"


def test_read_net_margin_delivery_fails_closed_for_wrong_capability_or_path(tmp_path: Path) -> None:
    app = _ready_app(tmp_path)
    outside = tmp_path / "outside.xlsx"
    outside.write_bytes(b"PK-outside")
    packet = _ren_packet(delivery_generated=True, output_path=outside)
    app.session("session-ren").last_review_result = packet

    with pytest.raises(ValueError):
        app.read_net_margin_delivery(session_id="session-ren")

    packet["bounded_outcome"] = {"capability_ref": "sold_vs_collected_gap"}
    app.session("session-ren").last_review_result = packet
    with pytest.raises(ValueError):
        app.read_net_margin_delivery(session_id="session-ren")

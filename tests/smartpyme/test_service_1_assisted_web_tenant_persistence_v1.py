from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from http.client import HTTPConnection
from threading import Thread
from urllib.parse import urlencode

from openpyxl import Workbook

from pymia.smartpyme.service_1_assisted_web_v1 import (
    AssistedWebApplicationV1,
    create_assisted_web_server_v1,
)


def _xlsx_bytes() -> bytes:
    stream = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["fecha", "venta_total", "cobrado"])
    sheet.append(["2026-06-01", 1000, 800])
    sheet.append(["2026-06-02", 2000, 1500])
    workbook.save(stream)
    return stream.getvalue()


def _answers(page: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    for question_id, option_id in re.findall(
        r'name="answer_([^"]+)" value="([^"]+)"', page
    ):
        if option_id not in {"OTHER", "IGNORE", "not_sure"}:
            answers.setdefault(f"answer_{question_id}", option_id)
    assert answers
    return answers


def _bound_app(tmp_path: Path, persist):
    app = AssistedWebApplicationV1(
        output_dir=tmp_path / "outputs",
        persist_tenant_confirmation=persist,
        require_tenant_persistence=True,
    )
    app.bind_tenant_identity(
        session_id="session-1",
        tenant_id="tenant-acme",
        cliente_id="cliente-001",
        owner_actor_id="owner-001",
        owner_actor_role="OWNER",
    )
    return app


def test_assisted_web_persists_canonical_owner_events_after_successful_review(tmp_path: Path) -> None:
    recorded = []

    def persist(event, contract):
        recorded.append((event, contract))
        return True

    app = _bound_app(tmp_path, persist)
    status, page = app.receive_xlsx(
        session_id="session-1",
        filename="ventas.xlsx",
        content=_xlsx_bytes(),
    )
    assert status == 200
    assert "Confirmar qué significa cada dato" in page

    status, page = app.confirm_meanings(
        session_id="session-1",
        fields=_answers(page),
    )
    assert status == 200
    assert "¿Qué querés revisar?" in page

    status, page = app.run_review(
        session_id="session-1",
        requested_capability="sold_vs_collected_gap",
    )
    assert status == 200
    assert "Ventas y cobranzas" in page
    assert recorded
    for event, contract in recorded:
        assert event.case_id == contract.case_id
        assert event.file_ref == "ventas.xlsx"
        assert contract.tenant_id == "tenant-acme"
        assert contract.cliente_id == "cliente-001"
        assert contract.owner_actor_id == "owner-001"
        assert contract.owner_actor_role == "OWNER"
        assert contract.workbook_ref == "ventas.xlsx"
        assert contract.confirmation_event_ref


def test_required_tenant_persistence_blocks_upload_without_explicit_identity(tmp_path: Path) -> None:
    app = AssistedWebApplicationV1(
        output_dir=tmp_path / "outputs",
        persist_tenant_confirmation=lambda _event, _contract: True,
        require_tenant_persistence=True,
    )

    status, page = app.receive_xlsx(
        session_id="session-1",
        filename="ventas.xlsx",
        content=_xlsx_bytes(),
    )

    assert status == 400
    assert "Falta identificar el tenant" in page


def test_required_tenant_persistence_fails_closed_when_backend_rejects_write(tmp_path: Path) -> None:
    app = _bound_app(tmp_path, lambda _event, _contract: False)
    status, page = app.receive_xlsx(
        session_id="session-1",
        filename="ventas.xlsx",
        content=_xlsx_bytes(),
    )
    assert status == 200

    status, page = app.confirm_meanings(
        session_id="session-1",
        fields=_answers(page),
    )
    assert status == 200

    status, page = app.run_review(
        session_id="session-1",
        requested_capability="sold_vs_collected_gap",
    )

    assert status == 200
    assert "No se registró como memoria del tenant" in page
    assert "Ventas y cobranzas" not in page


def test_http_server_accepts_trusted_identity_resolver_and_persists(tmp_path: Path) -> None:
    recorded = []

    def persist(event, contract):
        recorded.append((event, contract))
        return True

    def resolver(_handler):
        return {
            "tenant_id": "tenant-acme",
            "cliente_id": "cliente-001",
            "owner_actor_id": "owner-001",
            "owner_actor_role": "OWNER",
        }

    server = create_assisted_web_server_v1(
        host="127.0.0.1",
        port=0,
        output_dir=tmp_path / "outputs-http",
        persist_tenant_confirmation=persist,
        require_tenant_persistence=True,
        tenant_identity_resolver=resolver,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        boundary = "TenantPersistenceBoundary"
        upload_body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="ventas.xlsx"\r\n'
            "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
        ).encode("utf-8") + _xlsx_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request(
            "POST",
            "/upload",
            body=upload_body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(upload_body)),
            },
        )
        response = connection.getresponse()
        upload_page = response.read().decode("utf-8")
        cookie = response.getheader("Set-Cookie").split(";", 1)[0]
        assert response.status == 200
        assert "Confirmar qué significa cada dato" in upload_page

        confirm_body = urlencode(_answers(upload_page)).encode("utf-8")
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request(
            "POST",
            "/confirm-meanings",
            body=confirm_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(confirm_body)),
                "Cookie": cookie,
            },
        )
        response = connection.getresponse()
        assert response.status == 200
        assert "¿Qué querés revisar?" in response.read().decode("utf-8")

        review_body = urlencode({"review": "sold_vs_collected_gap"}).encode("utf-8")
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request(
            "POST",
            "/run-review",
            body=review_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(review_body)),
                "Cookie": cookie,
            },
        )
        response = connection.getresponse()
        review_page = response.read().decode("utf-8")
        assert response.status == 200
        assert "Ventas y cobranzas" in review_page
        assert recorded
        assert all(contract.tenant_id == "tenant-acme" for _, contract in recorded)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

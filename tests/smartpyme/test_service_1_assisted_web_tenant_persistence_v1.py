from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from http.client import HTTPConnection
from threading import Thread
from urllib.parse import urlencode

from openpyxl import Workbook

from pymia.smartpyme import service_1_assisted_web_v1 as assisted_web
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


def test_owner_confirmation_is_persisted_even_when_requested_control_needs_more_evidence(tmp_path: Path) -> None:
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
    status, page = app.confirm_meanings(
        session_id="session-1",
        fields=_answers(page),
    )
    assert status == 200
    status, page = app.run_review(
        session_id="session-1",
        requested_capability="net_margin_real",
    )
    assert status == 200
    assert recorded
    assert "No se registró como memoria del tenant" not in page
    assert all(contract.tenant_id == "tenant-acme" for _, contract in recorded)


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


def test_tenant_memory_recall_is_visible_but_never_preselected(tmp_path: Path) -> None:
    def load_memory(tenant_id: str):
        assert tenant_id == "tenant-acme"
        return (
            {
                "tenant_id": "tenant-acme",
                "sheet_ref": "Ventas",
                "column_ref": "venta_total",
                "owner_answer": "sold_amount",
                "confirmed_at": "2026-08-09T20:00:00Z",
            },
        )

    app = AssistedWebApplicationV1(
        output_dir=tmp_path / "outputs-memory",
        load_tenant_memory=load_memory,
    )
    app.bind_tenant_identity(
        session_id="session-memory",
        tenant_id="tenant-acme",
        cliente_id="cliente-001",
        owner_actor_id="owner-001",
        owner_actor_role="OWNER",
    )
    state = app.session("session-memory")
    state.semantic_questions = [
        {
            "question_id": "q-1",
            "sheet_name": "Ventas",
            "column_name": "venta_total",
            "question": "¿Qué representa venta_total?",
            "context": "Confirmación explícita requerida.",
            "options": [
                {"option_id": "sold_amount", "label": "Ventas registradas"},
                {"option_id": "OTHER", "label": "Otra cosa"},
            ],
        }
    ]

    enriched = app._with_tenant_memory_hints(state)
    page = assisted_web._semantic_questions_page(enriched)

    assert enriched[0]["tenant_memory_hint"] == "Ventas registradas"
    assert "La vez anterior confirmaste" in page
    assert "Ventas registradas" in page
    assert "checked" not in page


def test_persisted_case_reentry_survives_fresh_application_without_ram_state(tmp_path: Path) -> None:
    persisted_case = {
        "case_ref": "case_abc",
        "case_id": "case_abc",
        "tenant_id": "tenant-acme",
        "workbook_ref": "ventas.xlsx",
        "owner_actor_id": "owner-001",
        "kind": "persisted_owner_evidence",
        "evidence": [
            {
                "sheet_ref": "Ventas",
                "column_ref": "VentaTotal",
                "owner_answer": "ACCEPT",
                "confirmed_at": "2026-08-14T20:00:00Z",
            }
        ],
    }
    provider_calls = []

    def provider(_payload):
        provider_calls.append(True)
        raise AssertionError("semantic provider must not run during persisted reentry")

    app = AssistedWebApplicationV1(
        output_dir=tmp_path / "fresh-instance",
        persist_tenant_confirmation=lambda _event, _contract: True,
        load_persisted_cases=lambda tenant: (
            ({
                **persisted_case,
                "service_name": "Servicio 1 · evidencia confirmada",
                "status": "EVIDENCIA PERSISTIDA",
                "updated_at": "2026-08-14T20:00:00Z",
            },)
            if tenant == "tenant-acme"
            else ()
        ),
        load_persisted_case=lambda tenant, case_id: (
            dict(persisted_case)
            if tenant == "tenant-acme" and case_id == "case_abc"
            else None
        ),
        require_tenant_persistence=True,
        semantic_provider=provider,
    )
    app.bind_tenant_identity(
        session_id="new-session",
        tenant_id="tenant-acme",
        cliente_id="cliente-001",
        owner_actor_id="owner-001",
        owner_actor_role="OWNER",
    )

    status, cases_page = app.recent_cases(session_id="new-session")
    assert status == 200
    assert "case_abc" in cases_page
    assert "EVIDENCIA PERSISTIDA" in cases_page

    status, case_page = app.open_case(session_id="new-session", case_ref="case_abc")
    assert status == 200
    assert "Reingreso durable del caso case_abc" in case_page
    assert "VentaTotal" in case_page
    assert "ACCEPT" in case_page
    assert provider_calls == []

    app.bind_tenant_identity(
        session_id="other-session",
        tenant_id="tenant-other",
        cliente_id="cliente-other",
        owner_actor_id="owner-other",
        owner_actor_role="OWNER",
    )
    status, other_cases = app.recent_cases(session_id="other-session")
    assert status == 200
    assert "case_abc" not in other_cases
    status, _ = app.open_case(session_id="other-session", case_ref="case_abc")
    assert status == 404
    assert provider_calls == []


def test_http_get_reentry_binds_verified_tenant_and_reads_persisted_case(tmp_path: Path) -> None:
    def resolver(handler):
        assert handler.headers.get("Authorization") == "Bearer verified-token"
        return {
            "tenant_id": "tenant-acme",
            "cliente_id": "cliente-001",
            "owner_actor_id": "owner-001",
            "owner_actor_role": "OWNER",
        }

    summary = {
        "case_ref": "case_abc",
        "case_id": "case_abc",
        "tenant_id": "tenant-acme",
        "service_name": "Servicio 1 · evidencia confirmada",
        "status": "EVIDENCIA PERSISTIDA",
        "updated_at": "2026-08-14T20:00:00Z",
        "kind": "persisted_owner_evidence",
    }
    detail = {
        **summary,
        "workbook_ref": "ventas.xlsx",
        "owner_actor_id": "owner-001",
        "evidence": [
            {
                "sheet_ref": "Ventas",
                "column_ref": "VentaTotal",
                "owner_answer": "ACCEPT",
                "confirmed_at": "2026-08-14T20:00:00Z",
            }
        ],
    }
    server = create_assisted_web_server_v1(
        host="127.0.0.1",
        port=0,
        output_dir=tmp_path / "reentry-http",
        persist_tenant_confirmation=lambda _event, _contract: True,
        load_persisted_cases=lambda tenant: (dict(summary),) if tenant == "tenant-acme" else (),
        load_persisted_case=lambda tenant, case_id: dict(detail) if (tenant, case_id) == ("tenant-acme", "case_abc") else None,
        require_tenant_persistence=True,
        tenant_identity_resolver=resolver,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request("GET", "/cases", headers={"Authorization": "Bearer verified-token"})
        response = connection.getresponse()
        cases_page = response.read().decode("utf-8")
        assert response.status == 200
        assert "case_abc" in cases_page

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request(
            "GET",
            "/case?case_ref=case_abc",
            headers={"Authorization": "Bearer verified-token"},
        )
        response = connection.getresponse()
        case_page = response.read().decode("utf-8")
        assert response.status == 200
        assert "Reingreso durable del caso case_abc" in case_page
        assert "VentaTotal" in case_page
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_required_persisted_case_read_model_fails_closed_on_backend_error(tmp_path: Path) -> None:
    def fail_list(_tenant):
        raise RuntimeError("backend unavailable")

    def fail_case(_tenant, _case_id):
        raise RuntimeError("backend unavailable")

    app = AssistedWebApplicationV1(
        output_dir=tmp_path / "failed-reentry",
        persist_tenant_confirmation=lambda _event, _contract: True,
        load_persisted_cases=fail_list,
        load_persisted_case=fail_case,
        require_tenant_persistence=True,
    )
    app.bind_tenant_identity(
        session_id="session-1",
        tenant_id="tenant-acme",
        cliente_id="cliente-001",
        owner_actor_id="owner-001",
        owner_actor_role="OWNER",
    )

    status, page = app.recent_cases(session_id="session-1")
    assert status == 400
    assert "No pudimos recuperar los casos persistidos" in page

    status, page = app.open_case(session_id="session-1", case_ref="case_abc")
    assert status == 400
    assert "No pudimos recuperar el caso persistido" in page

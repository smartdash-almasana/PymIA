from http.client import HTTPConnection
from pathlib import Path
from threading import Thread

from pymia.smartpyme.service_1_assisted_web_v1 import create_assisted_web_server_v1


def _session_cookie(set_cookie: str) -> str:
    return set_cookie.split(";", 1)[0]


def test_cases_and_case_revalidate_identity_on_every_sensitive_get(tmp_path: Path) -> None:
    resolver_calls: list[str] = []
    detail_calls: list[tuple[str, str]] = []

    def resolver(handler):
        auth = str(handler.headers.get("Authorization") or "")
        resolver_calls.append(auth)
        identities = {
            "Bearer token-a": {
                "tenant_id": "tenant-a",
                "cliente_id": "cliente-a",
                "owner_actor_id": "owner-a",
                "owner_actor_role": "OWNER",
            },
            "Bearer token-b": {
                "tenant_id": "tenant-b",
                "cliente_id": "cliente-b",
                "owner_actor_id": "owner-b",
                "owner_actor_role": "OWNER",
            },
        }
        return identities.get(auth)

    def list_cases(tenant: str):
        return ({
            "case_ref": f"case-{tenant}",
            "case_id": f"case-{tenant}",
            "tenant_id": tenant,
            "service_name": f"case for {tenant}",
            "status": "READY",
            "updated_at": "2026-08-19T10:00:00Z",
            "kind": "persisted_owner_evidence",
        },)

    def load_case(tenant: str, case_id: str):
        detail_calls.append((tenant, case_id))
        if case_id != f"case-{tenant}":
            return None
        return {
            "case_ref": case_id,
            "case_id": case_id,
            "tenant_id": tenant,
            "service_name": f"case for {tenant}",
            "status": "READY",
            "updated_at": "2026-08-19T10:00:00Z",
            "kind": "persisted_owner_evidence",
            "workbook_ref": "test.xlsx",
            "owner_actor_id": f"owner-{tenant[-1]}",
            "evidence": [],
        }

    server = create_assisted_web_server_v1(
        host="127.0.0.1",
        port=0,
        output_dir=tmp_path,
        persist_tenant_confirmation=lambda _event, _contract: True,
        load_persisted_cases=list_cases,
        load_persisted_case=load_case,
        require_tenant_persistence=True,
        tenant_identity_resolver=resolver,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request("GET", "/cases", headers={"Authorization": "Bearer token-a"})
        response = connection.getresponse()
        page_a = response.read().decode("utf-8")
        cookie = _session_cookie(response.getheader("Set-Cookie") or "")
        assert response.status == 200
        assert "case for tenant-a" in page_a

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request(
            "GET",
            "/cases",
            headers={"Authorization": "Bearer token-b", "Cookie": cookie},
        )
        response = connection.getresponse()
        page_b = response.read().decode("utf-8")
        assert response.status == 200
        assert "case for tenant-b" in page_b
        assert "case for tenant-a" not in page_b

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request(
            "GET",
            "/case?case_ref=case-tenant-b",
            headers={"Authorization": "Bearer token-b", "Cookie": cookie},
        )
        response = connection.getresponse()
        response.read()
        assert response.status == 200
        assert detail_calls == [("tenant-b", "case-tenant-b")]

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        connection.request("GET", "/cases", headers={"Cookie": cookie})
        response = connection.getresponse()
        unauthenticated = response.read().decode("utf-8")
        assert response.status == 400
        assert "verified tenant identity is required" in unauthenticated
        assert "case for tenant-b" not in unauthenticated

        assert resolver_calls == [
            "Bearer token-a",
            "Bearer token-b",
            "Bearer token-b",
            "",
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

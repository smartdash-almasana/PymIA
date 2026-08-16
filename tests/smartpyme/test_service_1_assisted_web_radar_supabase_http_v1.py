from __future__ import annotations

import os
import uuid
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

import pytest
from openpyxl import Workbook

from pymia.smartpyme.service_1_assisted_web_v1 import create_assisted_web_server_v1
from pymia.smartpyme.service_1_radar_supabase_persistence_v1 import (
    RADAR_POLICIES_TABLE,
    Service1RadarSupabasePersistenceAdapterV1,
)
from pymia.smartpyme.service_1_supabase_identity_resolver_v1 import (
    Service1SupabaseIdentityResolverV1,
    create_service_1_supabase_identity_client_v1,
    load_service_1_supabase_identity_config_v1,
)

_TEST_EMAIL = "neoalmasana@gmail.com"
_REQUIRED_ENV = (
    "PYMIA_SUPABASE_URL",
    "PYMIA_SUPABASE_SERVICE_ROLE_KEY",
    "PYMIA_SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_TEST_PASSWORD",
)


def _supabase_ready() -> bool:
    return all(str(os.environ.get(name) or "").strip() for name in _REQUIRED_ENV)


def _xlsx_bytes(tmp_path: Path) -> bytes:
    path = tmp_path / "consorcio.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Expensas"
    sheet.append(["unidad_funcional", "saldo_anterior", "expensa_mes"])
    sheet.append(["UF-12", 200, 100])
    workbook.save(path)
    return path.read_bytes()


def _multipart(filename: str, content: bytes, token: str) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1RadarSupabaseBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
        "Authorization": f"Bearer {token}",
    }


def _request(server, method: str, path: str, *, body: bytes = b"", headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=15)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    payload = response.read().decode("utf-8")
    return response.status, response.getheaders(), payload


def _cookie(headers: list[tuple[str, str]]) -> str:
    for name, value in headers:
        if name.lower() == "set-cookie":
            return value.split(";", 1)[0]
    raise AssertionError("missing session cookie")


@pytest.mark.skipif(not _supabase_ready(), reason="Supabase RADAR environment is not configured")
def test_assisted_web_owner_radar_policy_physical_supabase_http_roundtrip(tmp_path: Path) -> None:
    store = Service1RadarSupabasePersistenceAdapterV1.from_environment()
    identity_config = load_service_1_supabase_identity_config_v1()
    identity_client = create_service_1_supabase_identity_client_v1(identity_config)

    password = str(os.environ["SUPABASE_TEST_PASSWORD"]).strip()
    login = identity_client.auth.sign_in_with_password(
        {"email": _TEST_EMAIL, "password": password}
    )
    token = login.session.access_token
    assert token

    resolver = Service1SupabaseIdentityResolverV1(identity_client)
    identity = resolver.__call__(
        type("Handler", (), {"headers": {"Authorization": f"Bearer {token}"}})()
    )
    tenant_id = identity["tenant_id"]
    policy_ref = f"owner-radar-http-{uuid.uuid4().hex[:12]}"

    server = create_assisted_web_server_v1(
        host="127.0.0.1",
        port=0,
        output_dir=tmp_path / "outputs",
        tenant_identity_resolver=resolver,
        radar_policy_store=store,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        upload_body, upload_headers = _multipart(
            "consorcio.xlsx", _xlsx_bytes(tmp_path), token
        )
        status, headers, page = _request(
            server,
            "POST",
            "/upload",
            body=upload_body,
            headers=upload_headers,
        )
        assert status == 200
        assert "Esto encontré en tu Excel" in page or "¿Qué querés revisar?" in page
        cookie = _cookie(headers)

        status, _, radar_page = _request(
            server,
            "GET",
            "/radar",
            headers={"Cookie": cookie, "Authorization": f"Bearer {token}"},
        )
        assert status == 200
        assert "Configurar RADAR del consorcio" in radar_page
        assert "RADAR no decide por vos" in radar_page
        assert 'name="communication_level"' in radar_page

        form = urlencode(
            {
                "policy_ref": policy_ref,
                "observable_ref": "consorcios.debt_equivalent_periods",
                "enabled": "true",
                "operator": "GTE",
                "comparison_value": "2",
                "communication_level": "ALERT",
                "confirmed_by_owner": "true",
            }
        ).encode("utf-8")
        status, _, saved_page = _request(
            server,
            "POST",
            "/save-radar-policy",
            body=form,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(form)),
                "Cookie": cookie,
                "Authorization": f"Bearer {token}",
            },
        )
        assert status == 200
        assert "Regla RADAR guardada" in saved_page
        assert "GTE 2" in saved_page
        assert "ALERT" in saved_page

        loaded = store.load_policy(tenant_id=tenant_id, policy_ref=policy_ref)
        assert loaded is not None
        assert loaded.tenant_id == tenant_id
        assert loaded.observable_ref == "consorcios.debt_equivalent_periods"
        assert loaded.operator == "GTE"
        assert loaded.comparison_value == "2"
        assert loaded.communication_level == "ALERT"
        assert loaded.confirmed_by_owner is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    store._client.table(RADAR_POLICIES_TABLE).delete().eq("tenant_id", tenant_id).eq(
        "policy_ref", policy_ref
    ).execute()
    residual = (
        store._client.table(RADAR_POLICIES_TABLE)
        .select("policy_ref")
        .eq("tenant_id", tenant_id)
        .eq("policy_ref", policy_ref)
        .execute()
    )
    assert residual.data == []

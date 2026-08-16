from __future__ import annotations

import os
import uuid
from datetime import datetime
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


def _table_xlsx(tmp_path: Path, name: str, headers: list[str], row: list[object]) -> bytes:
    path = tmp_path / name
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Datos"
    sheet.append(headers)
    sheet.append(row)
    workbook.save(path)
    return path.read_bytes()


def _multipart(filename: str, content: bytes, token: str) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1RadarEventSupabaseBoundary"
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


def _multipart_files(
    files: dict[str, tuple[str, bytes]], token: str, cookie: str
) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1RadarEventReconciliationBoundary"
    chunks: list[bytes] = []
    for field_name, (filename, content) in files.items():
        chunks.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
                "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
            ).encode("utf-8")
            + content
            + b"\r\n"
        )
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(chunks)
    return body, {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
        "Cookie": cookie,
        "Authorization": f"Bearer {token}",
    }


def _post_form(
    server, path: str, values: dict[str, str], cookie: str, token: str
):
    body = urlencode(values).encode("utf-8")
    return _request(
        server,
        "POST",
        path,
        body=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
            "Cookie": cookie,
            "Authorization": f"Bearer {token}",
        },
    )


def _request(server, method: str, path: str, *, body: bytes = b"", headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=20)
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
def test_assisted_web_bank_reconciliation_presents_persisted_radar_event_physical_supabase_http(
    tmp_path: Path,
) -> None:
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
    policy_ref = f"owner-radar-event-{uuid.uuid4().hex[:12]}"

    server = create_assisted_web_server_v1(
        host="127.0.0.1",
        port=0,
        output_dir=tmp_path / "outputs-event",
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

        status, _, saved_page = _post_form(
            server,
            "/save-radar-policy",
            {
                "policy_ref": policy_ref,
                "observable_ref": "consorcios.bank_unmatched_amount",
                "enabled": "true",
                "operator": "GTE",
                "comparison_value": "1000",
                "communication_level": "ALERT",
                "confirmed_by_owner": "true",
            },
            cookie,
            token,
        )
        assert status == 200
        assert "Regla RADAR guardada" in saved_page

        status, _, _ = _post_form(
            server,
            "/start-reconciliation",
            {"reconciliation_type": "BANK_RECONCILIATION"},
            cookie,
            token,
        )
        assert status == 200

        bank = _table_xlsx(
            tmp_path,
            "bank_event.xlsx",
            ["Número de operación", "Fecha movimiento", "Importe acreditado", "Referencia bancaria"],
            ["BANK-1", datetime(2026, 8, 1), 1250, "BANK-REF-1"],
        )
        internal = _table_xlsx(
            tmp_path,
            "internal_event.xlsx",
            ["Número de factura", "Fecha prevista", "Importe esperado", "Referencia comercial"],
            ["INT-1", datetime(2026, 8, 8), 300, "INTERNAL-REF-9"],
        )
        body, headers = _multipart_files(
            {
                "source_bank": ("bank_event.xlsx", bank),
                "source_internal": ("internal_event.xlsx", internal),
            },
            token,
            cookie,
        )
        status, _, page = _request(
            server,
            "POST",
            "/upload-reconciliation",
            body=body,
            headers=headers,
        )
        assert status == 200
        assert "Confirmar columnas para conciliación bancaria" in page

        status, _, result_page = _post_form(
            server,
            "/confirm-reconciliation-columns",
            {
                "bind_bank_id": "Número de operación",
                "bind_bank_fecha": "Fecha movimiento",
                "bind_bank_importe": "Importe acreditado",
                "bind_bank_referencia": "Referencia bancaria",
                "bind_internal_id": "Número de factura",
                "bind_internal_fecha": "Fecha prevista",
                "bind_internal_importe": "Importe esperado",
                "bind_internal_referencia": "Referencia comercial",
            },
            cookie,
            token,
        )
        assert status == 200
        assert "RADAR" in result_page
        assert "consorcios.bank_unmatched_amount" in result_page
        assert "ALERT" in result_page
        assert "1250.0" in result_page
        assert "GTE 1000" in result_page
        assert "no es una severidad asignada por PymIA" in result_page
        assert "HIGH" not in result_page
        assert "MODERATE" not in result_page
        assert "severity" not in result_page
        assert "risk" not in result_page
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    loaded = store.load_policy(tenant_id=tenant_id, policy_ref=policy_ref)
    assert loaded is not None
    assert loaded.tenant_id == tenant_id
    assert loaded.policy_ref == policy_ref
    assert loaded.observable_ref == "consorcios.bank_unmatched_amount"
    assert loaded.operator == "GTE"
    assert loaded.comparison_value == "1000"
    assert loaded.communication_level == "ALERT"
    assert loaded.confirmed_by_owner is True

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

from __future__ import annotations

from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

from openpyxl import Workbook

from pymia.smartpyme.service_1_assisted_web_v1 import create_assisted_web_server_v1
from pymia.smartpyme.service_1_radar_observation_policy_v1 import RadarObservationPolicyV1


class _RadarStore:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], RadarObservationPolicyV1] = {}

    def save_policy(self, policy: RadarObservationPolicyV1) -> bool:
        key = (policy.tenant_id, policy.policy_ref)
        existing = self.rows.get(key)
        if existing is not None and existing.to_dict() != policy.to_dict():
            raise ValueError("conflicting policy")
        self.rows[key] = policy
        return True

    def list_policies(
        self, *, tenant_id: str, enabled_only: bool = False
    ) -> tuple[RadarObservationPolicyV1, ...]:
        rows = [
            policy
            for (row_tenant, _), policy in self.rows.items()
            if row_tenant == tenant_id and (not enabled_only or policy.enabled)
        ]
        return tuple(sorted(rows, key=lambda item: item.policy_ref))


def _xlsx_bytes(tmp_path: Path) -> bytes:
    path = tmp_path / "consorcio.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Expensas"
    sheet.append(["unidad_funcional", "saldo_anterior", "expensa_mes"])
    sheet.append(["UF-12", 200, 100])
    workbook.save(path)
    return path.read_bytes()


def _multipart(filename: str, content: bytes) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1RadarWebBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
        "Authorization": "Bearer test-token",
    }


def _request(server, method: str, path: str, *, body: bytes = b"", headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    payload = response.read().decode("utf-8")
    return response.status, response.getheaders(), payload


def _cookie(headers: list[tuple[str, str]]) -> str:
    for name, value in headers:
        if name.lower() == "set-cookie":
            return value.split(";", 1)[0]
    raise AssertionError("missing session cookie")


def test_authenticated_assisted_web_owner_can_open_radar_menu_and_persist_policy(
    tmp_path: Path,
) -> None:
    store = _RadarStore()

    def resolver(_handler):
        return {
            "tenant_id": "tenant-consorcio-web",
            "cliente_id": "cliente-consorcio-web",
            "owner_actor_id": "owner-consorcio-web",
            "owner_actor_role": "OWNER",
        }

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
            "consorcio.xlsx", _xlsx_bytes(tmp_path)
        )
        status, headers, page = _request(
            server,
            "POST",
            "/upload",
            body=upload_body,
            headers=upload_headers,
        )
        assert status == 200
        assert "Confirmar qué significa cada dato" in page or "¿Qué querés revisar?" in page
        cookie = _cookie(headers)

        status, _, radar_page = _request(
            server,
            "GET",
            "/radar",
            headers={"Cookie": cookie},
        )
        assert status == 200
        assert "Configurar RADAR del consorcio" in radar_page
        assert "Períodos equivalentes de deuda" in radar_page
        assert "Importe absoluto de movimientos bancarios sin imputar" in radar_page
        assert "RADAR no decide por vos" in radar_page
        assert 'name="communication_level"' in radar_page
        assert "Reporte a demanda" in radar_page
        assert "Notificación" in radar_page
        assert "Alerta" in radar_page
        assert "Urgencia" in radar_page

        form = urlencode(
            {
                "policy_ref": "owner-debt-two-periods-web",
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
                "Authorization": "Bearer test-token",
            },
        )
        assert status == 200
        assert "Regla RADAR guardada" in saved_page
        assert "GTE 2" in saved_page
        assert "ALERT" in saved_page

        stored = store.rows[("tenant-consorcio-web", "owner-debt-two-periods-web")]
        assert stored.observable_ref == "consorcios.debt_equivalent_periods"
        assert stored.comparison_value == "2"
        assert stored.communication_level == "ALERT"
        assert stored.confirmed_by_owner is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

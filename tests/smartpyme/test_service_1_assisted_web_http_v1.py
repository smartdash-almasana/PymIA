from __future__ import annotations

import html
import re
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

import pytest
from openpyxl import Workbook

from pymia.smartpyme.service_1_assisted_web_v1 import create_assisted_web_server_v1


@pytest.fixture()
def assisted_server(tmp_path: Path):
    server = create_assisted_web_server_v1(host="127.0.0.1", port=0, output_dir=tmp_path / "outputs")
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _request_raw(server, method: str, path: str, body: bytes = b"", headers: dict[str, str] | None = None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    return response.status, response.getheaders(), response.read()


def _request(server, method: str, path: str, body: bytes = b"", headers: dict[str, str] | None = None):
    status, response_headers, response_body = _request_raw(server, method, path, body, headers)
    return status, response_headers, response_body.decode("utf-8")


def _multipart(filename: str, content: bytes, *, launch_review: str | None = None) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1AssistedWebBoundary"
    prefix = b""
    if launch_review is not None:
        prefix = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="launch_review"\r\n\r\n'
            f"{launch_review}\r\n"
        ).encode("utf-8")
    body = prefix + (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, {"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))}


def _sales_xlsx(tmp_path: Path) -> bytes:
    path = tmp_path / "ventas.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["fecha", "venta_total", "cobrado"])
    sheet.append(["2026-06-01", 1000, 800])
    sheet.append(["2026-06-02", 2000, 1500])
    workbook.save(path)
    return path.read_bytes()


def _margin_xlsx(tmp_path: Path) -> bytes:
    path = tmp_path / "margen.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Resumen"
    sheet.append(["ventas_periodo", "cmv_total", "impuestos_periodo"])
    sheet.append([100000, 60000, 10000])
    workbook.save(path)
    return path.read_bytes()


def _cookie(headers: list[tuple[str, str]]) -> str:
    for key, value in headers:
        if key.lower() == "set-cookie":
            return value.split(";", 1)[0]
    raise AssertionError("missing session cookie")


def _form(server, path: str, values: dict[str, str], cookie: str):
    body = urlencode(values).encode("utf-8")
    return _request(
        server,
        "POST",
        path,
        body,
        {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body)), "Cookie": cookie},
    )


class _BrowserAuthResolver:
    def sign_in_with_password(self, email: str, password: str) -> str:
        if email != "owner@example.test" or password != "secret":
            raise ValueError("invalid credentials")
        return "browser.jwt"

    def __call__(self, handler) -> dict[str, str]:
        cookie = str(handler.headers.get("Cookie") or "")
        if "service1_access_token=browser.jwt" not in cookie:
            raise ValueError("verified session required")
        return {
            "tenant_id": "tenant-browser",
            "cliente_id": "cliente-browser",
            "owner_actor_id": "owner-browser",
            "owner_actor_role": "OWNER",
        }


def _semantic_confirmation_answers(page: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    for question_id, option_id in re.findall(
        r'name="answer_([^"]+)" value="([^"]+)"',
        page,
    ):
        if option_id not in {"OTHER", "IGNORE", "not_sure"}:
            answers.setdefault(f"answer_{question_id}", option_id)
    if answers:
        return answers
    for decision_id in re.findall(
        r'name="action_([^"]+)" value="ACCEPT"',
        page,
    ):
        clean = html.unescape(decision_id)
        answers[f"action_{clean}"] = "ACCEPT"
    assert answers
    return answers


def test_browser_login_cookie_allows_real_upload_without_manual_authorization(tmp_path: Path) -> None:
    resolver = _BrowserAuthResolver()
    server = create_assisted_web_server_v1(
        host="127.0.0.1",
        port=0,
        output_dir=tmp_path / "browser-auth",
        tenant_identity_resolver=resolver,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, response_headers, page = _request(server, "GET", "/")
        assert status == 200
        assert "Ingresar a PymIA" in page
        session_cookie = _cookie(response_headers)

        login_body = urlencode(
            {"email": "owner@example.test", "password": "secret"}
        ).encode("utf-8")
        status, login_headers, page = _request(
            server,
            "POST",
            "/login",
            login_body,
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(login_body)),
                "Cookie": session_cookie,
            },
        )
        assert status == 200
        assert "¿Qué querés entender de tu Excel?" in page
        cookies = "; ".join(
            value.split(";", 1)[0]
            for key, value in login_headers
            if key.lower() == "set-cookie"
        )
        assert "service1_access_token=browser.jwt" in cookies
        assert "service1_session=" in cookies

        body, headers = _multipart(
            "ventas.xlsx",
            _sales_xlsx(tmp_path),
            launch_review="sold_vs_collected_gap",
        )
        headers["Cookie"] = cookies
        status, _, page = _request(server, "POST", "/upload", body, headers)
        assert status == 200
        assert "Esto encontré en tu Excel" in page
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_assisted_flow_uploads_xlsx_confirms_and_evaluates(assisted_server, tmp_path: Path) -> None:
    status, _, page = _request(assisted_server, "GET", "/")
    assert status == 200
    assert "Revisar información de mi negocio" in page

    invalid_body, invalid_headers = _multipart("ventas.csv", b"not an xlsx")
    status, _, page = _request(assisted_server, "POST", "/upload", invalid_body, invalid_headers)
    assert status == 400
    assert "Solo se pueden subir archivos .xlsx." in page

    body, headers = _multipart("ventas.xlsx", _sales_xlsx(tmp_path))
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    assert "Esto encontré en tu Excel" in page
    assert "No estoy seguro" in page
    cookie = _cookie(response_headers)

    semantic_questions_page = page
    status, _, page = _form(
        assisted_server,
        "/confirm-meanings",
        {"answer_cobrado": "A"},
        cookie,
    )
    assert status == 400
    assert "Elegí una respuesta para cada columna." in page

    status, _, page = _form(
        assisted_server,
        "/confirm-meanings",
        _semantic_confirmation_answers(semantic_questions_page),
        cookie,
    )
    assert status == 200
    assert "¿Qué querés revisar?" in page

    status, _, page = _form(assisted_server, "/run-review", {"review": "sold_vs_collected_gap"}, cookie)
    assert status == 200
    assert "Ventas y cobranzas" in page
    assert "Total vendido" in page
    assert "3.000,00" in page
    assert "Total cobrado" in page
    assert "2.300,00" in page
    assert "Diferencia" in page
    assert "700,00" in page
    assert "Porcentaje cobrado" in page
    assert "76.67%" in page
    assert "Diferencia todavía no compensada por cobranzas" in page
    assert "Archivo: <strong>ventas.xlsx</strong>" in page
    assert "hoja <strong>Ventas</strong>" in page
    assert "columna <strong>venta_total</strong>" in page
    assert "columna <strong>cobrado</strong>" in page
    assert "Período: no identificado explícitamente en los archivos recibidos." in page
    assert "deuda confirmada" not in page.lower()
    assert "dinero perdido" not in page.lower()
    assert "no identifica por sí sola clientes morosos" in page.lower()
    assert 'href="/download-sales-collections"' in page

    status, download_headers, content = _request_raw(
        assisted_server,
        "GET",
        "/download-sales-collections",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert content.startswith(b"PK")
    assert any(
        key.lower() == "content-disposition" and "service_1_liq_001_result.xlsx" in value
        for key, value in download_headers
    )
    assert [path.name for path in (tmp_path / "outputs").iterdir()] == [
        "service_1_liq_001_result.xlsx"
    ]


def test_launch_service_first_flow_runs_selected_control_after_confirmation(assisted_server, tmp_path: Path) -> None:
    status, _, home = _request(assisted_server, "GET", "/")
    assert status == 200
    assert "¿Qué querés entender de tu Excel?" in home
    assert "Ventas y cobranzas" in home
    assert "Margen real" in home
    assert "Flujo de caja" in home
    assert "Qué debería traer tu Excel" in home
    assert "Saldo de caja proyectado" not in home

    body, headers = _multipart(
        "ventas.xlsx",
        _sales_xlsx(tmp_path),
        launch_review="sold_vs_collected_gap",
    )
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    assert "Esto encontré en tu Excel" in page
    assert "¿Es correcto?" in page
    cookie = _cookie(response_headers)

    status, _, page = _form(
        assisted_server,
        "/confirm-meanings",
        _semantic_confirmation_answers(page),
        cookie,
    )
    assert status == 200
    assert "Ventas y cobranzas" in page
    assert "Total vendido" in page
    assert "Diferencia" in page
    assert 'href="/download-sales-collections"' in page


def test_launch_margin_real_flow_reaches_real_delivery(assisted_server, tmp_path: Path) -> None:
    body, headers = _multipart(
        "margen.xlsx",
        _margin_xlsx(tmp_path),
        launch_review="net_margin_real",
    )
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    assert "Esto encontré en tu Excel" in page
    assert "¿Es correcto?" in page
    cookie = _cookie(response_headers)

    status, _, page = _form(
        assisted_server,
        "/confirm-meanings",
        _semantic_confirmation_answers(page),
        cookie,
    )
    assert status == 200
    assert "Margen real" in page
    assert 'href="/download-net-margin"' in page

    status, download_headers, content = _request_raw(
        assisted_server,
        "GET",
        "/download-net-margin",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert content.startswith(b"PK")
    assert any(
        key.lower() == "content-disposition" and "service_1_ren_001_result.xlsx" in value
        for key, value in download_headers
    )


def test_completed_launch_control_appears_in_recent_cases_and_can_reopen(assisted_server, tmp_path: Path) -> None:
    body, headers = _multipart(
        "ventas.xlsx",
        _sales_xlsx(tmp_path),
        launch_review="sold_vs_collected_gap",
    )
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    cookie = _cookie(response_headers)
    status, _, page = _form(
        assisted_server,
        "/confirm-meanings",
        _semantic_confirmation_answers(page),
        cookie,
    )
    assert status == 200
    assert "Ventas y cobranzas" in page

    status, _, cases = _request(
        assisted_server,
        "GET",
        "/cases",
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert "Casos recientes" in cases
    assert "Ventas y cobranzas" in cases
    match = re.search(r'href="(/case\?case_ref=[^"]+)"', cases)
    assert match is not None

    status, _, reopened = _request(
        assisted_server,
        "GET",
        match.group(1),
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert "Ventas y cobranzas" in reopened
    assert "Total vendido" in reopened
    assert "3.000,00" in reopened

    status, _, other_session_cases = _request(assisted_server, "GET", "/cases")
    assert status == 200
    assert "Todavía no hay controles terminados en esta sesión." in other_session_cases
    assert "Ventas y cobranzas" not in other_session_cases


def _working_capital_xlsx(tmp_path: Path) -> bytes:
    path = tmp_path / "capital_trabajo.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "CapitalTrabajo"
    sheet.append([
        "saldo_inicial",
        "cobros_esperados",
        "pagos_esperados",
        "cuentas_por_cobrar",
        "ventas_periodo",
        "dias_periodo",
        "activo_corriente",
        "pasivo_corriente",
    ])
    sheet.append([1000, 2500, 1800, 3000, 9000, 30, 15000, 10000])
    workbook.save(path)
    return path.read_bytes()


def test_launch_working_capital_composes_three_governed_controls(assisted_server, tmp_path: Path) -> None:
    body, headers = _multipart(
        "capital_trabajo.xlsx",
        _working_capital_xlsx(tmp_path),
        launch_review="working_capital",
    )
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    cookie = _cookie(response_headers)
    if "Esto encontré en tu Excel" in page:
        assert "Esto encontré en tu Excel" in page
        status, _, page = _form(
            assisted_server,
            "/confirm-meanings",
            _semantic_confirmation_answers(page),
            cookie,
        )
        assert status == 200
    assert "Flujo de caja" in page
    assert "Flujo de caja proyectado" in page
    assert "Tiempo promedio de cobro" in page
    assert "Capacidad para cubrir obligaciones de corto plazo" in page
    assert "1.700" in page or "1700" in page
    assert "10.0 días" in page or "10 días" in page
    assert "1.5" in page
    assert "no explican por sí solos la causa de un problema" in page.lower()


def test_working_capital_cash_only_is_presented_as_partial_valid_result(assisted_server, tmp_path: Path) -> None:
    path = tmp_path / "flujo_caja.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Proyeccion_Caja"
    sheet.append(["saldo_inicial", "cobros_esperados", "pagos_esperados"])
    sheet.append([1000, 2500, 1800])
    workbook.save(path)

    body, headers = _multipart(
        "flujo_caja.xlsx",
        path.read_bytes(),
        launch_review="working_capital",
    )
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    cookie = _cookie(response_headers)
    if "Esto encontré en tu Excel" in page:
        status, _, page = _form(
            assisted_server,
            "/confirm-meanings",
            _semantic_confirmation_answers(page),
            cookie,
        )
        assert status == 200

    assert "Flujo de caja" in page
    assert "RESULTADO PARCIAL" in page
    assert "Flujo de caja proyectado" in page
    assert "1700" in page or "1.700" in page
    assert "Lo que sí pude calcular es válido" in page
    assert "FALTA INFORMACIÓN" not in page


def test_not_sure_keeps_case_open_and_preserves_confirmed_choices(assisted_server, tmp_path: Path) -> None:
    body, headers = _multipart("ventas.xlsx", _sales_xlsx(tmp_path))
    status, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    assert status == 200
    cookie = _cookie(response_headers)
    answers = _semantic_confirmation_answers(page)
    unresolved_key = next(iter(answers))
    partial = dict(answers)
    partial[unresolved_key] = "not_sure"

    status, _, page = _form(assisted_server, "/confirm-meanings", partial, cookie)

    assert status == 200
    assert "Esto encontré en tu Excel" in page
    assert "Todavía hay columnas sin confirmar" in page
    assert 'value="not_sure" selected' in page
    for key, value in answers.items():
        if key == unresolved_key:
            continue
        assert f'value="{value}" selected' in page

    status, _, page = _form(assisted_server, "/confirm-meanings", answers, cookie)
    assert status == 200
    assert "¿Qué querés revisar?" in page


def test_htmx_upload_returns_only_needed_semantic_questions_fragment(
    assisted_server,
    tmp_path: Path,
) -> None:
    body, headers = _multipart("ventas.xlsx", _sales_xlsx(tmp_path))
    headers["HX-Request"] = "true"
    status, _, fragment = _request(
        assisted_server,
        "POST",
        "/upload",
        body,
        headers,
    )

    assert status == 200
    assert fragment.lstrip().startswith("<main")
    assert "<!doctype" not in fragment.lower()
    assert "Esto encontré en tu Excel" in fragment
    assert "cobrado" in fragment
    assert "¿Qué representa la columna fecha?" not in fragment


def test_http_assisted_flow_rejects_missing_file_and_surfaces_blocked_result(assisted_server, tmp_path: Path) -> None:
    status, response_headers, page = _request(
        assisted_server,
        "POST",
        "/upload",
        b"",
        {"Content-Type": "multipart/form-data; boundary=empty", "Content-Length": "0"},
    )
    assert status == 400
    assert "Elegí un archivo" in page or "No se pudo leer el envío" in page

    corrupt_body, corrupt_headers = _multipart("incompleto.xlsx", b"not a workbook")
    status, _, page = _request(assisted_server, "POST", "/upload", corrupt_body, corrupt_headers)
    assert status == 400
    assert "No se pudo usar el archivo" in page

    body, headers = _multipart("ventas.xlsx", _sales_xlsx(tmp_path))
    _, response_headers, page = _request(assisted_server, "POST", "/upload", body, headers)
    cookie = _cookie(response_headers)
    status, _, _ = _form(
        assisted_server,
        "/confirm-meanings",
        _semantic_confirmation_answers(page),
        cookie,
    )
    assert status == 200

    status, _, page = _form(assisted_server, "/run-review", {"review": "payment_collection_gap"}, cookie)
    assert status == 200
    assert "FALTA INFORMACIÓN" in page
    assert "Caso guardado" in page
    assert "La descarga no está habilitada" in page

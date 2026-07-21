from __future__ import annotations

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


def _request(server, method: str, path: str, body: bytes = b"", headers: dict[str, str] | None = None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    return response.status, response.getheaders(), response.read().decode("utf-8")


def _multipart(filename: str, content: bytes) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1AssistedWebBoundary"
    body = (
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
    assert "Archivo recibido" in page
    assert "Ventas" in page
    assert "venta_total" in page
    cookie = _cookie(response_headers)

    status, _, page = _form(
        assisted_server,
        "/confirm-columns",
        {
            "meaning_col_confirm_001": "fecha de la operación",
            "meaning_col_confirm_002": "importe total vendido",
            "meaning_col_confirm_003": "importe efectivamente cobrado",
        },
        cookie,
    )
    assert status == 200
    assert "Confirmar qué significa cada dato" in page
    assert "No estoy seguro" in page

    status, _, page = _form(assisted_server, "/confirm-meanings", {"answer_cobrado": "A"}, cookie)
    assert status == 200
    assert "¿Qué querés revisar?" in page

    status, _, page = _form(assisted_server, "/run-review", {"review": "sold_vs_collected_gap"}, cookie)
    assert status == 200
    assert "Ventas y cobros" in page
    assert "Datos utilizados" in page
    assert "Este cálculo describe una relación matemática" in page
    assert "La descarga no está habilitada" in page
    assert list((tmp_path / "outputs").iterdir()) == []


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
    _, response_headers, _ = _request(assisted_server, "POST", "/upload", body, headers)
    cookie = _cookie(response_headers)
    _form(
        assisted_server,
        "/confirm-columns",
        {
            "meaning_col_confirm_001": "fecha de la operación",
            "meaning_col_confirm_002": "importe total vendido",
            "meaning_col_confirm_003": "importe efectivamente cobrado",
        },
        cookie,
    )
    _form(assisted_server, "/confirm-meanings", {"answer_cobrado": "A"}, cookie)

    status, _, page = _form(assisted_server, "/run-review", {"review": "payment_collection_gap"}, cookie)
    assert status == 200
    assert "No se puede continuar" in page
    assert "La descarga no está habilitada" in page

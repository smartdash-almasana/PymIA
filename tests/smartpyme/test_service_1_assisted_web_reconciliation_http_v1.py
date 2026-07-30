from __future__ import annotations

from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

import pytest
from openpyxl import Workbook

from pymia.smartpyme.service_1_assisted_web_v1 import create_assisted_web_server_v1
from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
)


@pytest.fixture()
def assisted_server(tmp_path: Path):
    server = create_assisted_web_server_v1(
        host="127.0.0.1", port=0, output_dir=tmp_path / "outputs"
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _request(server, method: str, path: str, body: bytes = b"", headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    return response.status, response.getheaders(), response.read().decode("utf-8")


def _cookie(headers: list[tuple[str, str]]) -> str:
    for key, value in headers:
        if key.lower() == "set-cookie":
            return value.split(";", 1)[0]
    raise AssertionError("missing session cookie")


def _form(server, path: str, values: dict[str, str], cookie: str | None = None):
    body = urlencode(values).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(body)),
    }
    if cookie:
        headers["Cookie"] = cookie
    return _request(server, "POST", path, body, headers)


def _xlsx(tmp_path: Path, name: str, headers: list[str], row: list[object]) -> bytes:
    path = tmp_path / name
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Datos"
    sheet.append(headers)
    sheet.append(row)
    workbook.save(path)
    return path.read_bytes()


def _multipart_files(files: dict[str, tuple[str, bytes]]) -> tuple[bytes, dict[str, str]]:
    boundary = "Service1ReconciliationBoundary"
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
    }


def test_bank_reconciliation_web_flow_reaches_human_review(
    assisted_server, tmp_path: Path
) -> None:
    status, _, home = _request(assisted_server, "GET", "/")
    assert status == 200
    assert "Conciliar movimientos" in home
    assert "Conciliación bancaria" in home

    status, response_headers, page = _form(
        assisted_server,
        "/start-reconciliation",
        {"reconciliation_type": BANK_RECONCILIATION},
    )
    assert status == 200
    assert "Extracto bancario" in page
    assert "Cobros o movimientos internos" in page
    cookie = _cookie(response_headers)

    bank = _xlsx(
        tmp_path,
        "banco.xlsx",
        ["mov_id", "fecha", "importe", "referencia"],
        ["B-1", "2026-07-01", 1000, "REF-1"],
    )
    internal = _xlsx(
        tmp_path,
        "cobros.xlsx",
        ["cobro_id", "fecha", "importe", "referencia"],
        ["C-1", "2026-07-01", 1000, "REF-1"],
    )
    body, headers = _multipart_files(
        {
            "source_bank": ("banco.xlsx", bank),
            "source_internal": ("cobros.xlsx", internal),
        }
    )
    headers["Cookie"] = cookie
    status, _, page = _request(
        assisted_server, "POST", "/upload-reconciliation", body, headers
    )
    assert status == 200
    assert "Confirmar columnas para conciliación bancaria" in page
    assert "PymIA no lo va a adivinar" in page

    status, _, page = _form(
        assisted_server,
        "/confirm-reconciliation-columns",
        {
            "bind_bank_id": "mov_id",
            "bind_bank_fecha": "fecha",
            "bind_bank_importe": "importe",
            "bind_bank_referencia": "referencia",
            "bind_internal_id": "cobro_id",
            "bind_internal_fecha": "fecha",
            "bind_internal_importe": "importe",
            "bind_internal_referencia": "referencia",
        },
        cookie,
    )
    assert status == 200
    assert "Revisión humana requerida" in page
    assert "Coincidencias claras" in page
    assert "Banco: B-1" in page
    assert "Interno: C-1" in page
    assert "no marcó ningún movimiento como conciliado" in page
    assert list((tmp_path / "outputs").iterdir()) == []


def test_mercado_pago_reconciliation_web_flow_reaches_human_review(
    assisted_server, tmp_path: Path
) -> None:
    status, response_headers, page = _form(
        assisted_server,
        "/start-reconciliation",
        {"reconciliation_type": MERCADO_PAGO_BANK_RECONCILIATION},
    )
    assert status == 200
    assert "Liquidaciones de Mercado Pago" in page
    cookie = _cookie(response_headers)

    mercado_pago = _xlsx(
        tmp_path,
        "mercado_pago.xlsx",
        ["op_id", "fecha", "bruto", "comision", "retencion", "neto", "lote", "referencia"],
        ["MP-1", "2026-07-01", 1000, 50, 20, 930, "L-1", "MPREF-1"],
    )
    bank = _xlsx(
        tmp_path,
        "banco_mp.xlsx",
        ["mov_id", "fecha", "importe", "lote", "referencia"],
        ["B-MP-1", "2026-07-02", 930, "L-1", "MPREF-1"],
    )
    body, headers = _multipart_files(
        {
            "source_mercado_pago": ("mercado_pago.xlsx", mercado_pago),
            "source_bank": ("banco_mp.xlsx", bank),
        }
    )
    headers["Cookie"] = cookie
    status, _, page = _request(
        assisted_server, "POST", "/upload-reconciliation", body, headers
    )
    assert status == 200
    assert "Importe bruto" in page
    assert "Importe acreditado" in page

    status, _, page = _form(
        assisted_server,
        "/confirm-reconciliation-columns",
        {
            "bind_mercado_pago_operacion_mp_id": "op_id",
            "bind_mercado_pago_fecha_operacion": "fecha",
            "bind_mercado_pago_importe_bruto": "bruto",
            "bind_mercado_pago_comision": "comision",
            "bind_mercado_pago_retencion": "retencion",
            "bind_mercado_pago_importe_neto": "neto",
            "bind_mercado_pago_lote_id": "lote",
            "bind_mercado_pago_referencia": "referencia",
            "bind_bank_movimiento_banco_id": "mov_id",
            "bind_bank_fecha": "fecha",
            "bind_bank_importe": "importe",
            "bind_bank_lote_id": "lote",
            "bind_bank_referencia": "referencia",
        },
        cookie,
    )
    assert status == 200
    assert "Mercado Pago ↔ Banco" in page
    assert "Revisión humana requerida" in page
    assert "Coincidencias claras" in page
    assert "Inconsistencias de cálculo" in page
    assert "no marcó ningún movimiento como conciliado" in page


def test_reconciliation_web_rejects_reusing_one_column_for_two_meanings(
    assisted_server, tmp_path: Path
) -> None:
    status, response_headers, _ = _form(
        assisted_server,
        "/start-reconciliation",
        {"reconciliation_type": BANK_RECONCILIATION},
    )
    assert status == 200
    cookie = _cookie(response_headers)
    bank = _xlsx(
        tmp_path,
        "banco.xlsx",
        ["mov_id", "fecha", "importe", "referencia"],
        ["B-1", "2026-07-01", 1000, "REF-1"],
    )
    internal = _xlsx(
        tmp_path,
        "cobros.xlsx",
        ["cobro_id", "fecha", "importe", "referencia"],
        ["C-1", "2026-07-01", 1000, "REF-1"],
    )
    body, headers = _multipart_files(
        {
            "source_bank": ("banco.xlsx", bank),
            "source_internal": ("cobros.xlsx", internal),
        }
    )
    headers["Cookie"] = cookie
    status, _, _ = _request(
        assisted_server, "POST", "/upload-reconciliation", body, headers
    )
    assert status == 200

    status, _, page = _form(
        assisted_server,
        "/confirm-reconciliation-columns",
        {
            "bind_bank_id": "mov_id",
            "bind_bank_fecha": "fecha",
            "bind_bank_importe": "importe",
            "bind_bank_referencia": "importe",
            "bind_internal_id": "cobro_id",
            "bind_internal_fecha": "fecha",
            "bind_internal_importe": "importe",
            "bind_internal_referencia": "referencia",
        },
        cookie,
    )
    assert status == 400
    assert "No uses la misma columna" in page

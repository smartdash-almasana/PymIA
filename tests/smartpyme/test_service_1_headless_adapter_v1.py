"""Focal tests for the headless HTTP/JSON adapter (transport only).

The adapter owns no analytical logic: every test below exercises HTTP
mapping, JSON discipline, and delegation to the closed contract + preserved
Product Root. No fixtures, no math, no persistence.
"""
from __future__ import annotations

import ast
import json
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from typing import Any

from pymia.smartpyme.service_1_computability_v1 import CONFIRMED_BINDINGS_STATUS
from pymia.smartpyme.service_1_headless_adapter_v1 import (
    HEADLESS_ROUTE_V1,
    create_service_1_headless_server_v1,
)
from pymia.smartpyme.service_1_headless_contract_v1 import (
    HEADLESS_REQUEST_SCHEMA_VERSION,
)


def _serve():
    server = create_service_1_headless_server_v1(host="127.0.0.1", port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _post(server, path: str, body: bytes, content_type: str = "application/json"):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=30)
    conn.request("POST", path, body=body, headers={"Content-Type": content_type})
    resp = conn.getresponse()
    data = resp.read()
    ctype = resp.getheader("Content-Type") or ""
    return resp.status, ctype, json.loads(data.decode("utf-8"))


def _valid_payload() -> dict[str, Any]:
    return {
        "schema_version": HEADLESS_REQUEST_SCHEMA_VERSION,
        "analysis_id": "sales_total",
        "ingestion_output": {},
        "confirmed_bindings": {"status": CONFIRMED_BINDINGS_STATUS},
    }


def test_post_valid_shape_uses_contract_and_root_blocks_without_math() -> None:
    server, thread = _serve()
    try:
        status, ctype, body = _post(server, HEADLESS_ROUTE_V1, json.dumps(_valid_payload()).encode())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert status == 200
    assert ctype == "application/json"
    assert body["status"] == "BLOCKED"
    assert body["analysis_id"] == "sales_total"
    assert body["blocked_reason"]


def test_post_invalid_request_returns_400_blocked() -> None:
    payload = _valid_payload()
    payload["schema_version"] = "WRONG"
    server, thread = _serve()
    try:
        status, ctype, body = _post(server, HEADLESS_ROUTE_V1, json.dumps(payload).encode())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert status == 400
    assert ctype == "application/json"
    assert body["status"] == "BLOCKED"
    assert body["blocked_reason"] == "HEADLESS_REQUEST_VERSION_INVALID"


def test_post_non_json_body_returns_400_blocked() -> None:
    server, thread = _serve()
    try:
        status, ctype, body = _post(server, HEADLESS_ROUTE_V1, b"not-json{{{")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert status == 400
    assert ctype == "application/json"
    assert body["status"] == "BLOCKED"
    assert body["blocked_reason"] == "HEADLESS_BODY_NOT_JSON"


def test_unknown_route_and_method_stay_json_fail_closed() -> None:
    server, thread = _serve()
    try:
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=30)
        conn.request("GET", HEADLESS_ROUTE_V1)
        resp = conn.getresponse()
        get_status, get_ctype, get_body = (
            resp.status,
            resp.getheader("Content-Type") or "",
            json.loads(resp.read().decode("utf-8")),
        )
        status, ctype, body = _post(server, "/nope", b"{}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert get_status == 404
    assert get_ctype == "application/json"
    assert get_body["status"] == "BLOCKED"
    assert status == 404
    assert ctype == "application/json"
    assert body["status"] == "BLOCKED"


def test_adapter_contains_no_analytical_logic() -> None:
    source = Path(__file__).resolve().parents[2] / "pymia" / "smartpyme" / "service_1_headless_adapter_v1.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            roots.add(node.module if top == "pymia" else top)
    allowed = {"__future__", "json", "http", "typing", "pymia.smartpyme.service_1_headless_contract_v1"}
    assert roots <= allowed, roots
    text = source.read_text(encoding="utf-8")
    assert "run_service_1_product_pipeline_v1" not in text

"""Minimal headless HTTP/JSON adapter for Service 1 (F12-only).

Thin transport over the closed contract SERVICE_1_HEADLESS_REQUEST_V1 /
SERVICE_1_HEADLESS_RESPONSE_V1. This adapter contains NO analytical logic:
it parses the body, delegates to execute_service_1_headless_json_v1 (which
owns validation and Product Root dispatch), and serializes the response.

Single route: POST /headless/v1/execute with a JSON body.
Every response (success or failure) has Content-Type: application/json.
HTTP mapping: 200 when the request executed through the root (READY or
root-BLOCKED inside the body); 400 for transport/shape failures;
404/405 for unknown route/method. No auth layer: for local/controlled use.
Tenant identity travels only inside the request JSON and is passed through
untouched; the adapter never invents or defaults identity.
"""
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from pymia.smartpyme.service_1_headless_contract_v1 import (
    execute_service_1_headless_json_v1,
)

HEADLESS_ROUTE_V1 = "/headless/v1/execute"
CONTENT_TYPE_JSON = "application/json"
MAX_JSON_BODY_BYTES_V1 = 1 * 1024 * 1024

_PARSE_BLOCK_REASONS = frozenset(
    {
        "HEADLESS_BODY_NOT_JSON",
        "HEADLESS_REQUEST_MUST_BE_MAPPING",
        "HEADLESS_REQUEST_UNKNOWN_FIELDS",
        "HEADLESS_REQUEST_VERSION_INVALID",
        "HEADLESS_ANALYSIS_ID_REQUIRED",
        "HEADLESS_INGESTION_REQUIRED",
        "HEADLESS_CONFIRMED_BINDINGS_REQUIRED",
        "HEADLESS_IDENTITY_INVALID",
        "HEADLESS_IDENTITY_COERCION_FAILED",
    }
)


def _error_body(reason: str) -> dict[str, Any]:
    return {
        "schema_version": "SERVICE_1_HEADLESS_RESPONSE_V1",
        "analysis_id": "",
        "status": "BLOCKED",
        "blocked_reason": reason,
        "title": None,
        "question": None,
        "result_set": None,
        "findings": [],
        "outcome": None,
        "result_memory": None,
        "integrity": None,
        "provenance": {"source": "SERVICE_1_HEADLESS_ADAPTER_V1"},
    }


class Service1HeadlessHandlerV1(BaseHTTPRequestHandler):
    server_version = "Service1HeadlessV1"

    def log_message(self, *args: Any) -> None:
        return None

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", CONTENT_TYPE_JSON)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _method_not_allowed(self) -> None:
        self._send_json(HTTPStatus.METHOD_NOT_ALLOWED, _error_body("HEADLESS_METHOD_NOT_ALLOWED"))

    def do_GET(self) -> None:
        self._send_json(HTTPStatus.NOT_FOUND, _error_body("HEADLESS_ROUTE_NOT_FOUND"))

    def do_PUT(self) -> None:
        self._method_not_allowed()

    def do_PATCH(self) -> None:
        self._method_not_allowed()

    def do_DELETE(self) -> None:
        self._method_not_allowed()

    def do_POST(self) -> None:
        if self.path != HEADLESS_ROUTE_V1:
            self._send_json(HTTPStatus.NOT_FOUND, _error_body("HEADLESS_ROUTE_NOT_FOUND"))
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            length = 0
        if length > MAX_JSON_BODY_BYTES_V1:
            self.close_connection = True
            self._send_json(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                _error_body("HEADLESS_BODY_TOO_LARGE"),
            )
            return
        try:
            raw = self.rfile.read(length) if length > 0 else b""
            payload = json.loads(raw.decode("utf-8")) if raw.strip() else None
        except (UnicodeDecodeError, ValueError):
            payload = None
            parse_error = True
        else:
            parse_error = payload is None
        if parse_error:
            self._send_json(HTTPStatus.BAD_REQUEST, _error_body("HEADLESS_BODY_NOT_JSON"))
            return
        dependencies = getattr(self.server, "headless_dependencies", None)
        response = execute_service_1_headless_json_v1(payload, dependencies=dependencies)
        if response.get("blocked_reason") in _PARSE_BLOCK_REASONS:
            self._send_json(HTTPStatus.BAD_REQUEST, response)
            return
        self._send_json(HTTPStatus.OK, response)


def create_service_1_headless_server_v1(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    dependencies: Any = None,
) -> ThreadingHTTPServer:
    """Build the headless server. Dependencies pass through to the contract."""
    server = ThreadingHTTPServer((host, port), Service1HeadlessHandlerV1)
    server.headless_dependencies = dependencies  # type: ignore[attr-defined]
    return server


__all__ = [
    "CONTENT_TYPE_JSON",
    "HEADLESS_ROUTE_V1",
    "Service1HeadlessHandlerV1",
    "create_service_1_headless_server_v1",
]

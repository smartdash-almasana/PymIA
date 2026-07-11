"""Dev-only HTTP endpoint for the Service 1 web experiment backend boundary."""

from __future__ import annotations

import argparse
import json
from email.parser import BytesParser
from email.policy import default as default_email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from pymia.smartpyme.service_1_web_experiment_backend_boundary_v1 import (
    BLOCK_INVALID_EXTENSION,
    build_service_1_web_experiment_backend_boundary_v1 as run_backend,
)

SCHEMA_VERSION = "SERVICE_1_WEB_EXPERIMENT_HTTP_ENDPOINT_V1"
ROUTE_RUN_EXPERIMENT = "/service-1/experiment/run"

STATUS_BLOCKED = "BLOCKED"

BLOCK_MISSING_FILE = "MISSING_FILE"
BLOCK_MISSING_PAYLOAD_JSON = "MISSING_PAYLOAD_JSON"
BLOCK_INVALID_PAYLOAD_JSON = "INVALID_PAYLOAD_JSON"
BLOCK_INVALID_CONTENT_TYPE = "INVALID_CONTENT_TYPE"
BLOCK_INVALID_MULTIPART = "INVALID_MULTIPART_FORM_DATA"
BLOCK_METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
BLOCK_ROUTE_NOT_FOUND = "ROUTE_NOT_FOUND"
BLOCK_INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

_REQUIRED_PAYLOAD_FIELDS = (
    "owner_column_answers",
    "semantic_owner_answers",
    "owner_authorization",
    "owner_validation",
    "delivery_authorized",
    "output_dir",
)


class Service1WebExperimentDevHTTPServer(ThreadingHTTPServer):
    """Threaded dev server carrying the injected backend runner."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class: type[BaseHTTPRequestHandler],
        *,
        backend_runner: Callable[..., dict[str, Any]],
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.backend_runner = backend_runner


def create_service_1_web_experiment_dev_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    backend_runner: Callable[..., dict[str, Any]] = run_backend,
) -> Service1WebExperimentDevHTTPServer:
    """Create the dev-only HTTP server."""
    return Service1WebExperimentDevHTTPServer(
        (host, int(port)),
        _Service1WebExperimentHandler,
        backend_runner=backend_runner,
    )


def serve_service_1_web_experiment_dev_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    backend_runner: Callable[..., dict[str, Any]] = run_backend,
) -> None:
    """Serve the dev-only HTTP endpoint until interrupted."""
    server = create_service_1_web_experiment_dev_server(
        host=host,
        port=port,
        backend_runner=backend_runner,
    )
    try:
        print(f"[dev-only] Service 1 web experiment server listening on http://{host}:{server.server_port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


class _Service1WebExperimentHandler(BaseHTTPRequestHandler):
    server_version = "PymIAService1WebExperimentHTTP/1.0"
    sys_version = ""

    # Dev-only CORS: allows the static frontend (e.g. served from :8080) to call
    # this endpoint (on :8000) during local experiments. NOT for production.
    _CORS_HEADERS = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    def _write_cors_headers(self) -> None:
        for key, value in self._CORS_HEADERS.items():
            self.send_header(key, value)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._write_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        route = urlsplit(self.path).path
        if route != ROUTE_RUN_EXPERIMENT:
            self._write_json(
                404,
                _build_http_packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=BLOCK_ROUTE_NOT_FOUND,
                ),
            )
            return

        try:
            http_status, payload = self._handle_run_request()
        except Exception:
            http_status, payload = 500, _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=BLOCK_INTERNAL_SERVER_ERROR,
            )
        self._write_json(http_status, payload)

    def do_GET(self) -> None:  # noqa: N802
        self._write_json(
            405,
            _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=BLOCK_METHOD_NOT_ALLOWED,
            ),
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _handle_run_request(self) -> tuple[int, dict[str, Any]]:
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            return 400, _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=BLOCK_INVALID_CONTENT_TYPE,
            )

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        raw_body = self.rfile.read(max(content_length, 0))

        try:
            parts = _parse_multipart_form_data(content_type=content_type, raw_body=raw_body)
        except ValueError as exc:
            return 400, _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=str(exc) or BLOCK_INVALID_MULTIPART,
            )

        file_part = parts.get("file")
        if file_part is None or not str(file_part.get("filename") or "").strip():
            return 400, _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=BLOCK_MISSING_FILE,
            )

        payload_part = parts.get("payload_json")
        if payload_part is None:
            return 400, _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=BLOCK_MISSING_PAYLOAD_JSON,
            )

        try:
            payload_json = _load_payload_json(payload_part["data"])
        except ValueError:
            return 400, _build_http_packet(
                status=STATUS_BLOCKED,
                blocked_reason=BLOCK_INVALID_PAYLOAD_JSON,
            )

        backend_packet = self.server.backend_runner(
            uploaded_xlsx_bytes=file_part["data"],
            uploaded_filename=str(file_part["filename"]),
            owner_column_answers=payload_json["owner_column_answers"],
            semantic_owner_answers=payload_json["semantic_owner_answers"],
            owner_authorization=payload_json["owner_authorization"],
            owner_validation=payload_json["owner_validation"],
            delivery_authorized=payload_json["delivery_authorized"],
            output_dir=payload_json["output_dir"],
        )

        http_status = 200
        if (
            backend_packet.get("status") == STATUS_BLOCKED
            and backend_packet.get("blocked_reason") == BLOCK_INVALID_EXTENSION
        ):
            http_status = 400

        return http_status, _build_http_packet(
            status=str(backend_packet.get("status") or STATUS_BLOCKED),
            blocked_reason=backend_packet.get("blocked_reason"),
            trace=backend_packet.get("trace"),
            delivery_packet=backend_packet.get("delivery_packet"),
        )

    def _write_json(self, http_status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(http_status)
        self._write_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _parse_multipart_form_data(*, content_type: str, raw_body: bytes) -> dict[str, dict[str, Any]]:
    if not raw_body:
        raise ValueError(BLOCK_INVALID_MULTIPART)

    header_block = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
    message = BytesParser(policy=default_email_policy).parsebytes(header_block + raw_body)
    if not message.is_multipart():
        raise ValueError(BLOCK_INVALID_MULTIPART)

    parts: dict[str, dict[str, Any]] = {}
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        field_name = part.get_param("name", header="content-disposition")
        if not field_name:
            continue
        parts[str(field_name)] = {
            "filename": part.get_filename(),
            "content_type": part.get_content_type(),
            "data": part.get_payload(decode=True) or b"",
        }
    return parts


def _load_payload_json(raw_payload: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON) from exc

    if not isinstance(payload, dict):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)

    for field_name in _REQUIRED_PAYLOAD_FIELDS:
        if field_name not in payload:
            raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)

    if not isinstance(payload["owner_column_answers"], dict):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)
    if not isinstance(payload["semantic_owner_answers"], dict):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)
    if not isinstance(payload["owner_authorization"], str):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)
    if not isinstance(payload["owner_validation"], str):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)
    if not isinstance(payload["delivery_authorized"], bool):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)
    if payload["output_dir"] is not None and not isinstance(payload["output_dir"], str):
        raise ValueError(BLOCK_INVALID_PAYLOAD_JSON)

    return payload


def _build_http_packet(
    *,
    status: str,
    blocked_reason: Optional[str],
    trace: Optional[dict[str, Any]] = None,
    delivery_packet: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "blocked_reason": blocked_reason,
        "trace": trace or {},
        "delivery_packet": _summarize_delivery_packet(delivery_packet),
    }


def _summarize_delivery_packet(delivery_packet: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(delivery_packet, dict):
        return {"summary": None, "refs": []}

    refs = []
    for item in delivery_packet.get("deliverables", []):
        if not isinstance(item, dict):
            continue
        refs.append(
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "bytes": item.get("bytes"),
            }
        )

    return {
        "summary": {
            "status": delivery_packet.get("status"),
            "blocked_reason": delivery_packet.get("blocked_reason"),
            "output_dir": delivery_packet.get("output_dir"),
            "delivery_created": bool(delivery_packet.get("delivery_created")),
            "delivery_authorized": bool(delivery_packet.get("delivery_authorized")),
            "product_ready": bool(delivery_packet.get("product_ready")),
            "deliverable_count": len(refs),
        },
        "refs": refs,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Dev-only Service 1 web experiment HTTP endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    serve_service_1_web_experiment_dev_server(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SCHEMA_VERSION",
    "ROUTE_RUN_EXPERIMENT",
    "STATUS_BLOCKED",
    "BLOCK_INVALID_EXTENSION",
    "BLOCK_MISSING_FILE",
    "BLOCK_MISSING_PAYLOAD_JSON",
    "BLOCK_INVALID_PAYLOAD_JSON",
    "BLOCK_INVALID_CONTENT_TYPE",
    "BLOCK_INVALID_MULTIPART",
    "BLOCK_METHOD_NOT_ALLOWED",
    "BLOCK_ROUTE_NOT_FOUND",
    "BLOCK_INTERNAL_SERVER_ERROR",
    "Service1WebExperimentDevHTTPServer",
    "create_service_1_web_experiment_dev_server",
    "serve_service_1_web_experiment_dev_server",
    "main",
]

"""Small JSON HTTP server for the canonical Service 1 semantic boundary."""
from __future__ import annotations

import json
from http import HTTPStatus
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from pymia.smartpyme.service_1_semantic_boundary_v1 import (
    INITIAL_REQUEST_SCHEMA,
    REENTRY_REQUEST_SCHEMA,
    Service1SemanticStateStoreV1,
    execute_service_1_semantic_initial_json_v1,
    execute_service_1_semantic_reentry_json_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    build_service_1_workbook_profile_v1,
)

SEMANTIC_INITIAL_ROUTE_V1 = "/semantic/v1/initial"
SEMANTIC_REENTRY_ROUTE_V1 = "/semantic/v1/reentry"
XLSX_INGESTION_ROUTE_V1 = "/ingestion/v1/xlsx"
XLSX_INGESTION_RESPONSE_SCHEMA_V1 = "SERVICE_1_XLSX_INGESTION_RESPONSE_V1"
MAX_XLSX_UPLOAD_BYTES_V1 = 25 * 1024 * 1024
MAX_JSON_BODY_BYTES_V1 = 1 * 1024 * 1024


class Service1SemanticBoundaryHandlerV1(BaseHTTPRequestHandler):
    server_version = "Service1SemanticBoundaryV1"

    def log_message(self, *_args: Any) -> None:
        return None

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=_json_default).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._send_json(HTTPStatus.NOT_FOUND, {"status": "BLOCKED", "blocked_reason": "C2_SEMANTIC_ROUTE_NOT_FOUND"})

    def do_POST(self) -> None:
        if self.path == XLSX_INGESTION_ROUTE_V1:
            self._do_xlsx_ingestion()
            return
        if self.path not in {SEMANTIC_INITIAL_ROUTE_V1, SEMANTIC_REENTRY_ROUTE_V1}:
            self._send_json(HTTPStatus.NOT_FOUND, {"status": "BLOCKED", "blocked_reason": "C2_SEMANTIC_ROUTE_NOT_FOUND"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length < 0:
                self.close_connection = True
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"status": "BLOCKED", "blocked_reason": "C2_SEMANTIC_BODY_LENGTH_INVALID"},
                )
                return
            if length > MAX_JSON_BODY_BYTES_V1:
                self.close_connection = True
                self._send_json(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {"status": "BLOCKED", "blocked_reason": "C2_SEMANTIC_BODY_TOO_LARGE"},
                )
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else None
        except (TypeError, ValueError, UnicodeDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"status": "BLOCKED", "blocked_reason": "C2_SEMANTIC_BODY_NOT_JSON"})
            return
        dependencies = getattr(self.server, "semantic_dependencies", None)
        provider = getattr(dependencies, "provider", None) if dependencies is not None else None
        store = getattr(self.server, "semantic_state_store", None)
        if not isinstance(store, Service1SemanticStateStoreV1):
            store = Service1SemanticStateStoreV1()
            self.server.semantic_state_store = store  # type: ignore[attr-defined]
        if self.path == SEMANTIC_INITIAL_ROUTE_V1:
            response = execute_service_1_semantic_initial_json_v1(payload, provider=provider, state_store=store)
        else:
            response = execute_service_1_semantic_reentry_json_v1(payload, state_store=store)
        self._send_json(HTTPStatus.OK if response.get("status") != "BLOCKED" else HTTPStatus.UNPROCESSABLE_ENTITY, response)

    def _do_xlsx_ingestion(self) -> None:
        try:
            filename, content = _multipart_file(self)
            intake = build_service_1_web_column_confirmation_intake_boundary_v1(
                uploaded_xlsx_bytes=content,
                uploaded_filename=filename,
                include_all_sheets=True,
            )
            if intake.get("status") == "BLOCKED":
                self._send_json(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    {
                        "schema_version": XLSX_INGESTION_RESPONSE_SCHEMA_V1,
                        "status": "BLOCKED",
                        "blocked_reason": intake.get("blocked_reason"),
                        "detail": intake.get("reader_blocking_errors", []),
                        "source": "SERVICE_1_CANONICAL_XLSX_INGESTION_V1",
                    },
                )
                return
            canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
                owner_question_packet=intake,
            )
            if canonical.get("status") != "UNCONFIRMED_INGESTION_OUTPUT_READY":
                self._send_json(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    {
                        "schema_version": XLSX_INGESTION_RESPONSE_SCHEMA_V1,
                        "status": "BLOCKED",
                        "blocked_reason": canonical.get("blocked_reason") or "CANONICAL_INGESTION_BLOCKED",
                        "source": "SERVICE_1_CANONICAL_XLSX_INGESTION_V1",
                    },
                )
                return
            ingestion_output = canonical.get("ingestion_output")
            profile = build_service_1_workbook_profile_v1(ingestion_output=ingestion_output)
            status = str(profile.get("status") or "BLOCKED")
            self._send_json(
                HTTPStatus.OK if status == "WORKBOOK_PROFILE_READY" else HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    "schema_version": XLSX_INGESTION_RESPONSE_SCHEMA_V1,
                    "status": status,
                    "blocked_reason": profile.get("blocked_reason"),
                    "detail": profile.get("detail"),
                    "file": {
                        "file_id": intake.get("source_artifact_ref"),
                        "filename": intake.get("filename"),
                        "size_bytes": len(content),
                        "content_hash": intake.get("source_artifact_ref"),
                    },
                    "workbook": {
                        "sheet_count": len(intake.get("sheet_names") or []),
                        "sheet_names": list(intake.get("sheet_names") or []),
                        "date_system": "1900",
                    },
                    "ingestion_output": ingestion_output,
                    "workbook_profile": profile,
                    "source": "SERVICE_1_CANONICAL_XLSX_INGESTION_V1",
                },
            )
        except (TypeError, ValueError, UnicodeDecodeError) as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "schema_version": XLSX_INGESTION_RESPONSE_SCHEMA_V1,
                    "status": "BLOCKED",
                    "blocked_reason": "SERVICE_1_XLSX_MULTIPART_INVALID",
                    "detail": str(exc),
                    "source": "SERVICE_1_CANONICAL_XLSX_INGESTION_V1",
                },
            )
        except Exception as exc:  # fail closed at the HTTP boundary
            self._send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    "schema_version": XLSX_INGESTION_RESPONSE_SCHEMA_V1,
                    "status": "BLOCKED",
                    "blocked_reason": "SERVICE_1_XLSX_INGESTION_FAILED",
                    "detail": str(exc),
                    "source": "SERVICE_1_CANONICAL_XLSX_INGESTION_V1",
                },
            )


def _multipart_file(handler: BaseHTTPRequestHandler) -> tuple[str, bytes]:
    content_type = str(handler.headers.get("Content-Type") or "")
    if "multipart/form-data" not in content_type:
        raise ValueError("multipart form data required")
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0 or length > MAX_XLSX_UPLOAD_BYTES_V1:
        raise ValueError("invalid upload size")
    body = handler.rfile.read(length)
    envelope = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
    )
    for part in envelope.iter_parts():
        if part.get_param("name", header="content-disposition") != "file":
            continue
        filename = str(part.get_filename() or "").strip()
        payload = part.get_payload(decode=True) or b""
        if not filename or not payload:
            raise ValueError("file field required")
        return filename, payload
    raise ValueError("file field required")


def _json_default(value: Any) -> str:
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return str(isoformat())
    return str(value)


def create_service_1_semantic_boundary_server_v1(*, host: str = "127.0.0.1", port: int = 0, provider: Any = None) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), Service1SemanticBoundaryHandlerV1)
    server.semantic_dependencies = type("SemanticDependencies", (), {"provider": provider})()  # type: ignore[attr-defined]
    server.semantic_state_store = Service1SemanticStateStoreV1()  # type: ignore[attr-defined]
    return server


__all__ = [
    "SEMANTIC_INITIAL_ROUTE_V1", "SEMANTIC_REENTRY_ROUTE_V1", "XLSX_INGESTION_ROUTE_V1",
    "Service1SemanticBoundaryHandlerV1", "create_service_1_semantic_boundary_server_v1",
    "INITIAL_REQUEST_SCHEMA", "REENTRY_REQUEST_SCHEMA",
]

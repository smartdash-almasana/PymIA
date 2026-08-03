"""Local, assisted HTML flow for the single Servicio 1 product root."""
from __future__ import annotations

import argparse
import html
import json
import math
import secrets
import tempfile
from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    STATUS_UNCONFIRMED_READY as CANONICAL_UNCONFIRMED_READY,
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_NEEDS_OWNER,
    STATUS_RECONCILIATION_NEEDS_EVIDENCE,
    STATUS_RECONCILIATION_NEEDS_OWNER,
    STATUS_RECONCILIATION_REVIEW_READY,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_reconciliation_human_review_decision_v1 import (
    ALLOWED_DECISIONS as ALLOWED_RECONCILIATION_DECISIONS,
    build_reconciliation_human_review_decision_v1,
)
from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
)
from pymia.smartpyme.service_1_reconciliation_workpaper_xlsx_v1 import (
    build_service_1_reconciliation_workpaper_xlsx_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)

_MODULE_DIR = Path(__file__).resolve().parent
_TEMPLATE_PATH = _MODULE_DIR / "templates" / "service_1_assisted_web_v1.html"
_STYLES_PATH = _MODULE_DIR / "static" / "service_1_assisted_web_v1.css"

_REVIEW_OPTIONS: tuple[tuple[str, str, str], ...] = (
    ("sold_vs_collected_gap", "Ventas y cobros", "Compará lo vendido con lo cobrado en el período."),
    ("net_margin_real", "Margen neto real", "Compará el margen real estimado a partir del precio, los costos y los impuestos."),
    ("projected_closing_cash_balance", "Saldo de caja proyectado", "Calculá un saldo de cierre a partir de movimientos confirmados."),
    ("dso", "Tiempo de cobro", "Conocé la relación entre cuentas por cobrar, ventas y días del período."),
    ("payment_collection_gap", "Cobros y pagos", "Compará los tiempos ya calculados de cobro y de pago."),
    ("reorder_point", "Punto de reposición", "Calculá cuándo conviene revisar la reposición según datos confirmados."),
    ("inventory_turnover", "Rotación de inventario", "Mostrá la relación entre inventario y costo registrado."),
    ("current_ratio", "Relación de corto plazo", "Compará activos y pasivos corrientes confirmados."),
    ("sales_concentration", "Concentración de ventas", "Mostrá qué parte de las ventas registradas corresponde al producto principal."),
    ("interest_burden_ratio", "Carga de intereses", "Compará intereses registrados con el resultado operativo informado."),
    ("adjusted_operating_cash_flow", "Flujo operativo ajustado", "Calculá una relación a partir de resultados y movimientos confirmados."),
    ("index_update_ratio", "Actualización entre índices", "Compará un índice de cierre con un índice de origen."),
)
_REVIEW_BY_REF = {item[0]: item for item in _REVIEW_OPTIONS}

_RECONCILIATION_OPTIONS: tuple[tuple[str, str, str], ...] = (
    (
        BANK_RECONCILIATION,
        "Conciliación bancaria",
        "Compará el extracto bancario con tus cobros o movimientos internos.",
    ),
    (
        MERCADO_PAGO_BANK_RECONCILIATION,
        "Mercado Pago ↔ Banco",
        "Compará las liquidaciones de Mercado Pago con las acreditaciones bancarias.",
    ),
)
_RECONCILIATION_BY_TYPE = {item[0]: item for item in _RECONCILIATION_OPTIONS}

_RECONCILIATION_NUMERIC_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {
    BANK_RECONCILIATION: {
        "bank": ("importe",),
        "internal": ("importe",),
    },
    MERCADO_PAGO_BANK_RECONCILIATION: {
        "mercado_pago": (
            "importe_bruto",
            "comision",
            "retencion",
            "importe_neto",
        ),
        "bank": ("importe",),
    },
}

_RECONCILIATION_SOURCES: dict[str, tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]] = {
    BANK_RECONCILIATION: (
        (
            "bank",
            "Extracto bancario",
            (
                ("id", "ID del movimiento"),
                ("fecha", "Fecha"),
                ("importe", "Importe"),
                ("referencia", "Referencia"),
            ),
        ),
        (
            "internal",
            "Cobros o movimientos internos",
            (
                ("id", "ID del movimiento"),
                ("fecha", "Fecha"),
                ("importe", "Importe"),
                ("referencia", "Referencia"),
            ),
        ),
    ),
    MERCADO_PAGO_BANK_RECONCILIATION: (
        (
            "mercado_pago",
            "Liquidaciones de Mercado Pago",
            (
                ("operacion_mp_id", "ID de operación"),
                ("fecha_operacion", "Fecha de operación"),
                ("importe_bruto", "Importe bruto"),
                ("comision", "Comisión"),
                ("retencion", "Retención"),
                ("importe_neto", "Importe neto"),
                ("lote_id", "Lote"),
                ("referencia", "Referencia"),
            ),
        ),
        (
            "bank",
            "Extracto bancario",
            (
                ("movimiento_banco_id", "ID del movimiento bancario"),
                ("fecha", "Fecha"),
                ("importe", "Importe acreditado"),
                ("lote_id", "Lote"),
                ("referencia", "Referencia"),
            ),
        ),
    ),
}


@dataclass
class AssistedWebSessionV1:
    ingestion_output: dict[str, Any] | None = None
    semantic_questions: list[dict[str, Any]] = field(default_factory=list)
    semantic_answers: dict[str, Any] = field(default_factory=dict)
    reconciliation_type: str | None = None
    reconciliation_intakes: dict[str, dict[str, Any]] = field(default_factory=dict)
    reconciliation_result: dict[str, Any] | None = None
    reconciliation_decisions: list[dict[str, Any]] = field(default_factory=list)


class AssistedWebApplicationV1:
    """Small in-memory coordinator. It never stores uploaded workbook bytes."""

    def __init__(self, *, output_dir: str | Path | None = None) -> None:
        self._sessions: dict[str, AssistedWebSessionV1] = {}
        self.output_dir = Path(output_dir) if output_dir is not None else Path(tempfile.mkdtemp(prefix="pymia-service-1-web-"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def session(self, session_id: str) -> AssistedWebSessionV1:
        return self._sessions.setdefault(session_id, AssistedWebSessionV1())

    def start_reconciliation(self, *, session_id: str, reconciliation_type: str) -> tuple[int, str]:
        if reconciliation_type not in _RECONCILIATION_BY_TYPE:
            return HTTPStatus.BAD_REQUEST, _home_page("Elegí un tipo de conciliación disponible.")
        state = self.session(session_id)
        state.reconciliation_type = reconciliation_type
        state.reconciliation_intakes = {}
        state.reconciliation_result = None
        state.reconciliation_decisions = []
        return HTTPStatus.OK, _reconciliation_upload_page(reconciliation_type)

    def receive_reconciliation_sources(
        self,
        *,
        session_id: str,
        files: dict[str, tuple[str, bytes]],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        reconciliation_type = state.reconciliation_type
        if reconciliation_type not in _RECONCILIATION_SOURCES:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero elegí qué conciliación querés hacer.")

        intakes: dict[str, dict[str, Any]] = {}
        for source_kind, source_label, _ in _RECONCILIATION_SOURCES[reconciliation_type]:
            filename, content = files.get(f"source_{source_kind}", ("", b""))
            if not filename:
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"Falta el archivo: {source_label}.",
                )
            if not filename.lower().endswith(".xlsx"):
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"{source_label}: solo se aceptan archivos .xlsx.",
                )
            intake = build_service_1_web_column_confirmation_intake_boundary_v1(
                uploaded_xlsx_bytes=content,
                uploaded_filename=filename,
            )
            if intake.get("status") == "BLOCKED":
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"No se pudo leer {source_label}. Revisá el archivo.",
                )
            intakes[source_kind] = intake

        state.reconciliation_intakes = intakes
        state.reconciliation_result = None
        state.reconciliation_decisions = []
        return HTTPStatus.OK, _reconciliation_column_confirmation_page(
            reconciliation_type,
            intakes,
        )

    def confirm_reconciliation_columns(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        reconciliation_type = state.reconciliation_type
        intakes = state.reconciliation_intakes
        if reconciliation_type not in _RECONCILIATION_SOURCES or not intakes:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero subí los dos archivos de conciliación.")

        source_packets: list[dict[str, Any]] = []
        case_parts: list[str] = []
        for source_kind, source_label, field_specs in _RECONCILIATION_SOURCES[reconciliation_type]:
            intake = intakes.get(source_kind)
            if not isinstance(intake, dict):
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"Falta el archivo: {source_label}.",
                )
            available_columns = {str(item) for item in intake.get("columns") or []}
            bindings = {
                canonical_field: fields.get(
                    f"bind_{source_kind}_{canonical_field}", ""
                ).strip()
                for canonical_field, _ in field_specs
            }
            if any(not column for column in bindings.values()):
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "Confirmá todas las columnas necesarias para continuar.",
                )
            if any(column not in available_columns for column in bindings.values()):
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "Una de las columnas elegidas ya no coincide con el archivo recibido.",
                )
            if len(set(bindings.values())) != len(bindings):
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "No uses la misma columna para representar dos datos distintos.",
                )

            normalized = intake.get("normalized_table")
            if not isinstance(normalized, dict):
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"No se pudo preparar {source_label} para conciliación.",
                )
            rows = normalized.get("rows")
            if not isinstance(rows, list) or not rows:
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"{source_label} no contiene movimientos para revisar.",
                )

            approved_columns = list(dict.fromkeys(bindings.values()))
            source_packets.append(
                {
                    "source_kind": source_kind,
                    "source_ref": str(intake.get("filename") or source_label),
                    "rows": _prepare_reconciliation_rows(
                        rows=rows,
                        bindings=bindings,
                        reconciliation_type=reconciliation_type,
                        source_kind=source_kind,
                    ),
                    "field_bindings": bindings,
                    "governance": {
                        "p5_status": "CONFIRMED",
                        "p6_decisions": [
                            {"column_ref": column, "status": "APPROVED"}
                            for column in approved_columns
                        ],
                        "p7_status": "REQUIREMENT_MATCHED",
                        "p8_status": "COMPUTABLE",
                        "runtime_authorized": False,
                        "tool_execution_authorized": False,
                        "product_ready": False,
                        "delivery_authorized": False,
                        "diagnosis_generated": False,
                    },
                }
            )
            case_parts.append(str(intake.get("case_id") or source_kind)[-10:])

        packet = run_service_1_product_pipeline_v1(
            ingestion_output=None,
            tool_requests=[],
            output_dir=self.output_dir,
            reconciliation_request={
                "case_id": "web_reconciliation_" + "_".join(case_parts),
                "owner_requested": True,
                "reconciliation_type": reconciliation_type,
                "source_packets": source_packets,
            },
        )
        state.reconciliation_result = packet
        state.reconciliation_decisions = []
        if packet.get("status") == STATUS_RECONCILIATION_NEEDS_OWNER:
            return HTTPStatus.OK, _reconciliation_column_confirmation_page(
                reconciliation_type,
                intakes,
                "Hace falta volver a confirmar el significado de las columnas.",
            )
        if packet.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_message_page(
                "No se pudo preparar la conciliación con estos datos. Revisá los archivos y las columnas elegidas."
            )
        if packet.get("status") in {
            STATUS_RECONCILIATION_REVIEW_READY,
            STATUS_RECONCILIATION_NEEDS_EVIDENCE,
        }:
            return HTTPStatus.OK, _reconciliation_result_page(packet)
        return HTTPStatus.OK, _blocked_message_page(
            "La conciliación quedó en un estado que necesita revisión antes de continuar."
        )

    def decide_reconciliation_item(
        self,
        *,
        session_id: str,
        review_item_ref: str,
        decision: str,
        reviewed_by: str,
        observation: str,
    ) -> tuple[int, str]:
        state = self.session(session_id)
        packet = state.reconciliation_result
        if not isinstance(packet, dict):
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero ejecutá una conciliación para revisar sus casos."
            )
        chosen = str(decision or "").strip().upper()
        reviewer = str(reviewed_by or "").strip()
        if chosen not in ALLOWED_RECONCILIATION_DECISIONS:
            return HTTPStatus.BAD_REQUEST, _reconciliation_result_page(
                packet,
                decisions=state.reconciliation_decisions,
                error="Elegí Confirmar, Rechazar o Dejar pendiente.",
            )
        if not reviewer:
            return HTTPStatus.BAD_REQUEST, _reconciliation_result_page(
                packet,
                decisions=state.reconciliation_decisions,
                error="Indicá quién realizó la revisión.",
            )
        item_index = _reconciliation_review_item_index(packet)
        selected = item_index.get(str(review_item_ref or "").strip())
        if selected is None:
            return HTTPStatus.BAD_REQUEST, _reconciliation_result_page(
                packet,
                decisions=state.reconciliation_decisions,
                error="Ese caso ya no pertenece a la conciliación actual.",
            )
        reconciliation_run = packet.get("reconciliation_run")
        run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
        record = build_reconciliation_human_review_decision_v1(
            case_id=str(run.get("case_id") or ""),
            reconciliation_type=str(run.get("reconciliation_type") or ""),
            review_item_ref=str(review_item_ref),
            review_category=str(selected["category"]),
            review_item=selected["item"],
            decision=chosen,
            reviewed_by=reviewer,
            observation=observation,
        )
        state.reconciliation_decisions.append(record)
        _append_reconciliation_decision_jsonl(self.output_dir, record)
        return HTTPStatus.OK, _reconciliation_result_page(
            packet,
            decisions=state.reconciliation_decisions,
            notice="Decisión humana registrada. Los movimientos originales no fueron modificados.",
        )

    def build_reconciliation_workpaper(
        self,
        *,
        session_id: str,
    ) -> dict[str, Any]:
        state = self.session(session_id)
        packet = state.reconciliation_result
        if not isinstance(packet, dict):
            raise ValueError("reconciliation result is required")
        return build_service_1_reconciliation_workpaper_xlsx_v1(
            reconciliation_packet=packet,
            human_decisions=state.reconciliation_decisions,
        )

    def receive_xlsx(self, *, session_id: str, filename: str, content: bytes) -> tuple[int, str]:
        if not filename:
            return HTTPStatus.BAD_REQUEST, _error_page("Elegí un archivo de Excel para continuar.")
        if not filename.lower().endswith(".xlsx"):
            return HTTPStatus.BAD_REQUEST, _error_page("Solo se pueden subir archivos .xlsx.")
        intake = build_service_1_web_column_confirmation_intake_boundary_v1(
            uploaded_xlsx_bytes=content,
            uploaded_filename=filename,
        )
        if intake.get("status") == "BLOCKED":
            return HTTPStatus.BAD_REQUEST, _error_page("No se pudo usar el archivo. Revisá que sea un Excel .xlsx válido.")
        canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
            owner_question_packet=intake,
        )
        if canonical.get("status") != CANONICAL_UNCONFIRMED_READY:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "No se pudo preparar la lectura del archivo."
            )

        state = self.session(session_id)
        state.ingestion_output = canonical["ingestion_output"]
        state.semantic_questions = []
        state.semantic_answers = {}

        try:
            first_run = _run_product_root(
                ingestion_output=state.ingestion_output,
                output_dir=self.output_dir,
            )
        except ValueError as error:
            if "requires at least one tool request" in str(error):
                return HTTPStatus.OK, _review_selection_page()
            raise
        if first_run.get("status") == STATUS_NEEDS_OWNER:
            state.semantic_questions = list(first_run.get("owner_questions") or [])
            return HTTPStatus.OK, _semantic_questions_page(state.semantic_questions)
        if first_run.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_result_page(first_run)
        return HTTPStatus.OK, _review_selection_page()

    def confirm_meanings(self, *, session_id: str, fields: dict[str, str]) -> tuple[int, str]:
        state = self.session(session_id)
        if not state.ingestion_output or not state.semantic_questions:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero confirmá las columnas del archivo.")
        answers: dict[str, Any] = {}
        for question in state.semantic_questions:
            question_id = str(question.get("question_id") or "")
            selected = fields.get(f"answer_{question_id}", "").strip()
            if not selected:
                return HTTPStatus.BAD_REQUEST, _semantic_questions_page(state.semantic_questions, "Elegí una respuesta para cada columna.")
            if selected == "not_sure":
                return HTTPStatus.OK, _blocked_message_page("No se puede continuar hasta confirmar el significado de esas columnas. Podés volver a elegir el archivo cuando tengas esa información.")
            if selected == "OTHER":
                free_text = fields.get(f"other_{question_id}", "").strip()
                if not free_text:
                    return HTTPStatus.BAD_REQUEST, _semantic_questions_page(state.semantic_questions, "Explicá qué significa la columna cuando elegís Otra cosa.")
                answers[question_id] = {"option_id": "OTHER", "free_text": free_text}
            else:
                answers[question_id] = selected
        state.semantic_answers = answers
        state.semantic_questions = []
        return HTTPStatus.OK, _review_selection_page()

    def run_review(self, *, session_id: str, requested_capability: str) -> tuple[int, str]:
        state = self.session(session_id)
        if requested_capability not in _REVIEW_BY_REF:
            return HTTPStatus.BAD_REQUEST, _review_selection_page("Elegí una revisión disponible.")
        if not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero subí y confirmá un archivo de Excel.")
        packet = _run_product_root(
            ingestion_output=state.ingestion_output,
            owner_answers=state.semantic_answers,
            requested_capability=requested_capability,
            output_dir=self.output_dir,
        )
        if packet.get("status") == STATUS_NEEDS_OWNER:
            state.semantic_questions = list(packet.get("owner_questions") or [])
            if any(not str(question.get("question_id") or "").strip() for question in state.semantic_questions):
                return HTTPStatus.OK, _blocked_message_page("No se puede continuar con esa descripción. Elegí una opción clara o volvé a confirmar las columnas.")
            return HTTPStatus.OK, _semantic_questions_page(state.semantic_questions, "Hace falta una precisión más para continuar.")
        if packet.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_result_page(packet, requested_capability)
        return HTTPStatus.OK, _evaluated_result_page(packet, requested_capability)


def _run_product_root(
    *,
    ingestion_output: dict[str, Any],
    owner_answers: Any = None,
    requested_capability: str | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    return run_service_1_product_pipeline_v1(
        ingestion_output=ingestion_output,
        tool_requests=[],
        output_dir=output_dir or tempfile.gettempdir(),
        sheet_name=str(ingestion_output.get("sheet_name") or "sheet1"),
        owner_answers=owner_answers,
        requested_capability=requested_capability,
        deliver_result=False,
    )


def create_assisted_web_server_v1(*, host: str = "127.0.0.1", port: int = 8765, output_dir: str | Path | None = None) -> ThreadingHTTPServer:
    application = AssistedWebApplicationV1(output_dir=output_dir)
    return ThreadingHTTPServer((host, port), _handler_for(application))


def _handler_for(application: AssistedWebApplicationV1) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/":
                self._send_html(HTTPStatus.OK, _home_page())
            elif self.path == "/static/service_1_assisted_web_v1.css":
                self._send(HTTPStatus.OK, _STYLES_PATH.read_bytes(), "text/css; charset=utf-8")
            elif self.path == "/healthz":
                self._send(HTTPStatus.OK, b'{"status":"ok"}', "application/json; charset=utf-8")
            elif self.path == "/download-reconciliation-workpaper":
                session_id = self._session_id()
                try:
                    workpaper = application.build_reconciliation_workpaper(
                        session_id=session_id
                    )
                except ValueError:
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _error_page("Primero prepará una conciliación para generar el papel de trabajo."),
                        session_id=session_id,
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    workpaper["content"],
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    session_id=session_id,
                    extra_headers={
                        "Content-Disposition": f'attachment; filename="{workpaper["filename"]}"'
                    },
                )
            else:
                self._send_html(HTTPStatus.NOT_FOUND, _error_page("No encontramos esa página."))

        def do_POST(self) -> None:  # noqa: N802
            session_id = self._session_id()
            try:
                if self.path == "/upload":
                    filename, content = _multipart_file(self)
                    status, content_html = application.receive_xlsx(session_id=session_id, filename=filename, content=content)
                elif self.path == "/upload-reconciliation":
                    _, files = _multipart_form(self)
                    status, content_html = application.receive_reconciliation_sources(
                        session_id=session_id,
                        files=files,
                    )
                else:
                    fields = _form_fields(self)
                    if self.path == "/start-reconciliation":
                        status, content_html = application.start_reconciliation(
                            session_id=session_id,
                            reconciliation_type=fields.get("reconciliation_type", ""),
                        )
                    elif self.path == "/confirm-reconciliation-columns":
                        status, content_html = application.confirm_reconciliation_columns(
                            session_id=session_id,
                            fields=fields,
                        )
                    elif self.path == "/decide-reconciliation-item":
                        status, content_html = application.decide_reconciliation_item(
                            session_id=session_id,
                            review_item_ref=fields.get("review_item_ref", ""),
                            decision=fields.get("decision", ""),
                            reviewed_by=fields.get("reviewed_by", ""),
                            observation=fields.get("observation", ""),
                        )
                    elif self.path == "/confirm-meanings":
                        status, content_html = application.confirm_meanings(session_id=session_id, fields=fields)
                    elif self.path == "/run-review":
                        status, content_html = application.run_review(session_id=session_id, requested_capability=fields.get("review", ""))
                    else:
                        status, content_html = HTTPStatus.NOT_FOUND, _error_page("No encontramos esa acción.")
            except ValueError:
                status, content_html = HTTPStatus.BAD_REQUEST, _error_page("No se pudo leer el envío. Probá de nuevo.")
            if self.headers.get("HX-Request") == "true":
                self._send_fragment(status, content_html, session_id=session_id)
            else:
                self._send_html(status, content_html, session_id=session_id)

        def _session_id(self) -> str:
            cookie = self.headers.get("Cookie", "")
            for part in cookie.split(";"):
                name, _, value = part.strip().partition("=")
                if name == "service1_session" and value:
                    return value
            return secrets.token_urlsafe(18)

        def _send_fragment(self, status: int, content: str, *, session_id: str | None = None) -> None:
            self._send(status, content.encode("utf-8"), "text/html; charset=utf-8", session_id=session_id)

        def _send_html(self, status: int, content: str, *, session_id: str | None = None) -> None:
            self._send(status, _document(content).encode("utf-8"), "text/html; charset=utf-8", session_id=session_id)

        def _send(
            self,
            status: int,
            body: bytes,
            content_type: str,
            *,
            session_id: str | None = None,
            extra_headers: dict[str, str] | None = None,
        ) -> None:
            self.send_response(int(status))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for name, value in (extra_headers or {}).items():
                self.send_header(name, value)
            if session_id is not None:
                self.send_header("Set-Cookie", f"service1_session={session_id}; Path=/; SameSite=Lax; HttpOnly")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def _multipart_file(handler: BaseHTTPRequestHandler) -> tuple[str, bytes]:
    _, files = _multipart_form(handler)
    if "file" not in files:
        raise ValueError("file field required")
    return files["file"]


def _multipart_form(
    handler: BaseHTTPRequestHandler,
) -> tuple[dict[str, str], dict[str, tuple[str, bytes]]]:
    content_type = handler.headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type:
        raise ValueError("multipart form data required")
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0 or length > 40 * 1024 * 1024:
        raise ValueError("invalid upload size")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
        + handler.rfile.read(length)
    )
    fields: dict[str, str] = {}
    files: dict[str, tuple[str, bytes]] = {}
    for part in message.iter_parts():
        name = str(part.get_param("name", header="content-disposition") or "").strip()
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True)
        raw = payload if isinstance(payload, bytes) else b""
        if filename is not None:
            files[name] = (filename, raw)
        else:
            fields[name] = raw.decode("utf-8", errors="replace")
    return fields, files


def _form_fields(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length).decode("utf-8", errors="replace")
    parsed = parse_qs(raw, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _document(content: str) -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("{{content}}", content)


def _home_page(error: str | None = None) -> str:
    reconciliation_options = "".join(
        f'<label class="choice"><input type="radio" name="reconciliation_type" value="{_esc(ref)}" required><strong>{_esc(name)}</strong><span>{_esc(description)}</span></label>'
        for ref, name, description in _RECONCILIATION_OPTIONS
    )
    return f"""
    <main id="app" tabindex="-1">
      <h1>Revisar información de mi negocio</h1>
      {_error(error)}
      <p>Subí un archivo de Excel y te ayudaremos a entenderlo paso a paso.</p>
      <form action="/upload" method="post" enctype="multipart/form-data" hx-post="/upload" hx-target="#app" hx-swap="outerHTML">
        <label for="file">Elegir archivo</label>
        <input id="file" name="file" type="file" accept=".xlsx" required>
        <p>Tu archivo no se modifica.</p>
        <p>Antes de hacer cálculos, te pediremos que confirmes qué significa cada dato.</p>
        <button type="submit">Continuar</button>
      </form>
      <hr>
      <h2>Conciliar movimientos</h2>
      <p>Si querés comparar dos fuentes, elegí qué tipo de conciliación necesitás.</p>
      <form action="/start-reconciliation" method="post" hx-post="/start-reconciliation" hx-target="#app" hx-swap="outerHTML">
        {reconciliation_options}
        <button type="submit">Empezar conciliación</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _reconciliation_upload_page(
    reconciliation_type: str,
    error: str | None = None,
) -> str:
    _, title, description = _RECONCILIATION_BY_TYPE[reconciliation_type]
    file_fields = "".join(
        f'''<fieldset><legend>{_esc(source_label)}</legend>
          <label for="source_{_esc(source_kind)}">Elegir Excel</label>
          <input id="source_{_esc(source_kind)}" name="source_{_esc(source_kind)}" type="file" accept=".xlsx" required>
        </fieldset>'''
        for source_kind, source_label, _ in _RECONCILIATION_SOURCES[reconciliation_type]
    )
    return f"""
    <main id="app" tabindex="-1">
      <h1>{_esc(title)}</h1>
      {_error(error)}
      <p>{_esc(description)}</p>
      <p>Necesitamos las dos fuentes. No modificamos ninguno de los archivos.</p>
      <form action="/upload-reconciliation" method="post" enctype="multipart/form-data" hx-post="/upload-reconciliation" hx-target="#app" hx-swap="outerHTML">
        {file_fields}
        <button type="submit">Revisar archivos</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _reconciliation_column_confirmation_page(
    reconciliation_type: str,
    intakes: dict[str, dict[str, Any]],
    error: str | None = None,
) -> str:
    _, title, _ = _RECONCILIATION_BY_TYPE[reconciliation_type]
    source_blocks: list[str] = []
    for source_kind, source_label, field_specs in _RECONCILIATION_SOURCES[reconciliation_type]:
        intake = intakes[source_kind]
        columns = [str(item) for item in intake.get("columns") or []]
        selectors: list[str] = []
        for canonical_field, field_label in field_specs:
            options = '<option value="">Elegí una columna</option>' + "".join(
                f'<option value="{_esc(column)}">{_esc(column)}</option>'
                for column in columns
            )
            selectors.append(
                f'''<label for="bind_{_esc(source_kind)}_{_esc(canonical_field)}">{_esc(field_label)}</label>
                <select id="bind_{_esc(source_kind)}_{_esc(canonical_field)}" name="bind_{_esc(source_kind)}_{_esc(canonical_field)}" required>{options}</select>'''
            )
        source_blocks.append(
            f'''<fieldset><legend>{_esc(source_label)}</legend>
              <p>Archivo: <strong>{_esc(intake.get("filename"))}</strong></p>
              <p>Decinos qué columna representa cada dato. PymIA no lo va a adivinar.</p>
              {''.join(selectors)}
            </fieldset>'''
        )
    return f"""
    <main id="app" tabindex="-1">
      <h1>Confirmar columnas para { _esc(title.lower()) }</h1>
      {_error(error)}
      <form action="/confirm-reconciliation-columns" method="post" hx-post="/confirm-reconciliation-columns" hx-target="#app" hx-swap="outerHTML">
        {''.join(source_blocks)}
        <button type="submit">Cruzar movimientos</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _prepare_reconciliation_rows(
    *,
    rows: list[Any],
    bindings: dict[str, str],
    reconciliation_type: str,
    source_kind: str,
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    numeric_fields = _RECONCILIATION_NUMERIC_FIELDS.get(
        reconciliation_type, {}
    ).get(source_kind, ())
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        for canonical_field in numeric_fields:
            source_column = bindings.get(canonical_field, "")
            if not source_column:
                continue
            numeric = _confirmed_numeric_value(row.get(source_column))
            if numeric is not None:
                row[source_column] = numeric
        prepared.append(row)
    return prepared


def _confirmed_numeric_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    candidates = [text]
    if text.count(",") == 1 and "." not in text:
        whole, fractional = text.split(",", 1)
        if whole.lstrip("+-").isdigit() and fractional.isdigit() and len(fractional) <= 2:
            candidates.append(whole + "." + fractional)
    for candidate in candidates:
        try:
            number = float(candidate)
        except ValueError:
            continue
        if math.isfinite(number):
            return number
    return None


def _reconciliation_result_page(
    packet: dict[str, Any],
    *,
    decisions: list[dict[str, Any]] | None = None,
    notice: str | None = None,
    error: str | None = None,
) -> str:
    reconciliation_run = packet.get("reconciliation_run")
    run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
    review_raw = run.get("assisted_review")
    review = review_raw if isinstance(review_raw, dict) else {}
    summary_raw = review.get("review_summary")
    summary = summary_raw if isinstance(summary_raw, dict) else {}
    reconciliation_type = str(run.get("reconciliation_type") or "")
    title = _RECONCILIATION_BY_TYPE.get(
        reconciliation_type,
        ("", "Conciliación", ""),
    )[1]
    pending_label = (
        "Operaciones de Mercado Pago sin acreditación"
        if reconciliation_type == MERCADO_PAGO_BANK_RECONCILIATION
        else "Movimientos internos sin banco"
    )
    metrics = (
        ("Coincidencias claras", summary.get("confirmed_candidates", 0)),
        ("Coincidencias probables", summary.get("probable_candidates", 0)),
        ("Casos dudosos", summary.get("ambiguous_groups", 0)),
        ("Diferencias de importe", summary.get("amount_differences", 0)),
        ("Diferencias de fecha", summary.get("date_differences", 0)),
        ("Movimientos bancarios sin pareja", summary.get("bank_pending", 0)),
        (pending_label, summary.get("internal_pending", 0)),
        ("Faltantes de evidencia", summary.get("missing_evidence", 0)),
        ("Inconsistencias de cálculo", summary.get("calculation_inconsistencies", 0)),
    )
    rows = "".join(
        f"<tr><th>{_esc(label)}</th><td>{_esc(value)}</td></tr>"
        for label, value in metrics
    )
    status_note = (
        "Falta evidencia en uno o más movimientos. Revisá los casos señalados antes de tomar una decisión."
        if packet.get("status") == STATUS_RECONCILIATION_NEEDS_EVIDENCE
        else "El cruce está preparado para revisión humana."
    )
    decision_history = list(decisions or [])
    details = _reconciliation_detail_sections(
        packet=packet,
        decisions=decision_history,
    )
    decision_count = len(decision_history)
    return f"""
    <main id="app" tabindex="-1">
      <h1>{_esc(title)}</h1>
      {_error(error)}
      {f'<p class="notice">{_esc(notice)}</p>' if notice else ''}
      <p><strong>Revisión humana requerida.</strong> {_esc(status_note)}</p>
      <p>Decisiones registradas en esta revisión: <strong>{decision_count}</strong>.</p>
      <table><tbody>{rows}</tbody></table>
      {details}
      <p><a href="/download-reconciliation-workpaper">Descargar papel de trabajo (.xlsx)</a></p>
      <p>El archivo incluye resultados, decisiones humanas y casos todavía pendientes.</p>
      <p class="notice">PymIA no marcó ningún movimiento como conciliado, no modificó los archivos y no realizó ningún cierre contable.</p>
      <div aria-live="polite">Resultado de conciliación listo para revisar.</div>
    </main>"""


def _reconciliation_review_sections(
    packet: dict[str, Any],
) -> list[tuple[str, str, list[Any]]]:
    reconciliation_run = packet.get("reconciliation_run")
    run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
    review_raw = run.get("assisted_review")
    review = review_raw if isinstance(review_raw, dict) else {}
    review_result_raw = review.get("review_result")
    review_result = review_result_raw if isinstance(review_result_raw, dict) else {}
    reconciliation_type = str(run.get("reconciliation_type") or "")
    if reconciliation_type == BANK_RECONCILIATION:
        return [
            ("exact", "Coincidencias claras", _summary_items(review_result, "exact_matches_summary")),
            ("probable", "Coincidencias probables", _summary_items(review_result, "probable_matches_summary")),
            ("ambiguous", "Casos dudosos", _summary_items(review_result, "ambiguous_matches_summary")),
            ("amount_difference", "Diferencias de importe", _summary_items(review_result, "amount_differences_summary")),
            ("date_difference", "Diferencias de fecha", _summary_items(review_result, "date_differences_summary")),
            ("bank_pending", "Banco sin pareja", _summary_items(review_result, "bank_pending_summary")),
            ("internal_pending", "Movimientos internos sin banco", _summary_items(review_result, "internal_pending_summary")),
            ("missing_evidence", "Faltantes de evidencia", _summary_items(review_result, "missing_evidence_summary")),
        ]
    if reconciliation_type == MERCADO_PAGO_BANK_RECONCILIATION:
        return [
            ("exact", "Coincidencias claras", _list_value(review_result, "conciliaciones")),
            ("ambiguous", "Casos dudosos", _list_value(review_result, "ambiguos")),
            ("amount_difference", "Diferencias de importe", _list_value(review_result, "diferencias_importe")),
            ("bank_pending", "Banco sin operación de Mercado Pago", _list_value(review_result, "movimientos_banco_sin_operacion_mp")),
            ("internal_pending", "Mercado Pago sin acreditación", _list_value(review_result, "operaciones_mp_sin_acreditacion")),
            ("calculation_inconsistency", "Inconsistencias de cálculo", _list_value(review_result, "inconsistencias_calculo")),
            ("missing_evidence", "Faltantes de evidencia", _list_value(review_result, "faltantes_evidencia")),
        ]
    return []


def _reconciliation_review_item_index(
    packet: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for category, _, items in _reconciliation_review_sections(packet):
        for position, raw_item in enumerate(items, start=1):
            item = raw_item if isinstance(raw_item, dict) else {"value": raw_item}
            item_ref = f"{category}:{position}"
            index[item_ref] = {
                "category": category,
                "item": item,
            }
    return index


def _reconciliation_detail_sections(
    *,
    packet: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> str:
    latest = {
        str(record.get("review_item_ref") or ""): record
        for record in decisions
        if isinstance(record, dict)
    }
    rendered_sections: list[str] = []
    for category, label, items in _reconciliation_review_sections(packet):
        if not items:
            continue
        rendered_items: list[str] = []
        for position, raw_item in enumerate(items, start=1):
            item = raw_item if isinstance(raw_item, dict) else {"value": raw_item}
            item_ref = f"{category}:{position}"
            current = latest.get(item_ref)
            current_text = ""
            if current:
                observation = str(current.get("observation") or "").strip()
                reviewer = str(current.get("reviewed_by") or "").strip()
                current_text = (
                    f'<p><strong>Última decisión:</strong> {_esc(current.get("decision"))}'
                    f' · Revisó: {_esc(reviewer)}'
                    f' · {_esc(current.get("decided_at"))}'
                    f'{" · " + _esc(observation) if observation else ""}</p>'
                )
            rendered_items.append(
                f'''<li>
                  <p>{_reconciliation_item_text(item)}</p>
                  {current_text}
                  <form action="/decide-reconciliation-item" method="post" hx-post="/decide-reconciliation-item" hx-target="#app" hx-swap="outerHTML">
                    <input type="hidden" name="review_item_ref" value="{_esc(item_ref)}">
                    <label for="reviewed_by_{_esc(category)}_{position}">Revisado por</label>
                    <input id="reviewed_by_{_esc(category)}_{position}" name="reviewed_by" type="text" required>
                    <label for="observation_{_esc(category)}_{position}">Observación</label>
                    <input id="observation_{_esc(category)}_{position}" name="observation" type="text" placeholder="Opcional">
                    <div>
                      <button type="submit" name="decision" value="CONFIRM">Confirmar</button>
                      <button type="submit" name="decision" value="REJECT">Rechazar</button>
                      <button type="submit" name="decision" value="PENDING">Dejar pendiente</button>
                    </div>
                  </form>
                </li>'''
            )
        rendered_sections.append(
            f"<details open><summary>{_esc(label)} ({len(items)})</summary><ol>{''.join(rendered_items)}</ol></details>"
        )
    return "".join(rendered_sections)


def _append_reconciliation_decision_jsonl(
    output_dir: Path,
    record: dict[str, Any],
) -> Path:
    target = output_dir / "reconciliation_human_decisions.jsonl"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return target


def _list_value(container: dict[str, Any], key: str) -> list[Any]:
    value = container.get(key)
    return value if isinstance(value, list) else []


def _summary_items(container: dict[str, Any], key: str) -> list[Any]:
    summary = container.get(key)
    if not isinstance(summary, dict):
        return []
    items = summary.get("items")
    return items if isinstance(items, list) else []


def _reconciliation_item_text(item: Any) -> str:
    if not isinstance(item, dict):
        return _esc(item)
    labels = {
        "banco_id": "Banco",
        "interno_id": "Interno",
        "movimiento_banco_id": "Banco",
        "operacion_mp_id": "Mercado Pago",
        "lote_id": "Lote",
        "referencia": "Referencia",
        "criterio": "Criterio",
        "importe": "Importe",
        "importe_banco": "Importe banco",
        "importe_interno": "Importe interno",
        "diferencia_absoluta": "Diferencia",
        "dias": "Días",
    }
    parts: list[str] = []
    for key, value in item.items():
        if key in {"evidencia", "requires_human_review", "tipo_match"}:
            continue
        if isinstance(value, dict):
            nested = ", ".join(
                f"{labels.get(str(nested_key), str(nested_key).replace('_', ' ').capitalize())}: {nested_value}"
                for nested_key, nested_value in value.items()
                if not isinstance(nested_value, (dict, list))
            )
            if nested:
                parts.append(nested)
        elif not isinstance(value, list):
            parts.append(
                f"{labels.get(str(key), str(key).replace('_', ' ').capitalize())}: {value}"
            )
    return _esc(" · ".join(parts) or "Caso para revisar")


def _semantic_questions_page(questions: list[dict[str, Any]], error: str | None = None) -> str:
    items = []
    for question in questions:
        question_id = _esc(question.get("question_id"))
        options = "".join(
            f'<label><input type="radio" name="answer_{question_id}" value="{_esc(option.get("option_id"))}" required> {_esc(option.get("label"))}</label>'
            for option in question.get("options") or []
        )
        items.append(f"""
        <fieldset><legend>{_esc(question.get('question') or '¿Qué representa esta columna?')}</legend>
          <p>{_esc(question.get('context'))}</p>{options}
          <label><input type="radio" name="answer_{question_id}" value="not_sure"> No estoy seguro</label>
          <label for="other_{question_id}">Si elegís Otra cosa, explicala</label><input id="other_{question_id}" name="other_{question_id}" type="text">
        </fieldset>""")
    return f"""
    <main id="app" tabindex="-1"><h1>Confirmar qué significa cada dato</h1>{_error(error)}
      <form action="/confirm-meanings" method="post" hx-post="/confirm-meanings" hx-target="#app" hx-swap="outerHTML">{''.join(items)}<button type="submit">Continuar</button></form>
      <div class="notice" aria-live="polite"></div></main>"""


def _review_selection_page(error: str | None = None) -> str:
    options = "".join(
        f'<label class="choice"><input type="radio" name="review" value="{_esc(ref)}" required><strong>{_esc(name)}</strong><span>{_esc(description)}</span></label>'
        for ref, name, description in _REVIEW_OPTIONS
    )
    return f"""
    <main id="app" tabindex="-1"><h1>¿Qué querés revisar?</h1>{_error(error)}
      <form action="/run-review" method="post" hx-post="/run-review" hx-target="#app" hx-swap="outerHTML">{options}<button type="submit">Ver resultado</button></form>
      <div class="notice" aria-live="polite"></div></main>"""


def _evaluated_result_page(packet: dict[str, Any], requested_capability: str) -> str:
    _, title, _ = _REVIEW_BY_REF[requested_capability]
    computation = packet.get("computation_result") if isinstance(packet.get("computation_result"), dict) else {}
    typed = computation.get("typed_result") if isinstance(computation.get("typed_result"), dict) else {}
    outcome = packet.get("bounded_outcome") if isinstance(packet.get("bounded_outcome"), dict) else {}
    value = _result_value(computation=computation, typed=typed, outcome=outcome)
    unit = typed.get("unit", "")
    data = _data_used(computation, outcome)
    limitations = outcome.get("limitations") if isinstance(outcome.get("limitations"), (list, tuple)) else []
    finding = outcome.get("finding") or "El cálculo se completó con los datos confirmados."
    return f"""
    <main id="app" tabindex="-1"><h1>{_esc(title)}</h1>
      <p class="result"><strong>{_esc(value)} {_esc(unit)}</strong></p><p>{_esc(finding)}</p>
      <h2>Datos utilizados</h2>{data}
      <p>Este cálculo describe una relación matemática a partir de los datos confirmados.</p>
      <p>No determina por sí solo causas, problemas del negocio ni acciones a tomar.</p>
      <details><summary>Ver cómo se calculó</summary><p>Se aplicó el cálculo definido para esta revisión sobre los datos confirmados.</p></details>
      <h2>Límites de interpretación</h2><ul>{''.join(f'<li>{_esc(item)}</li>' for item in limitations)}</ul>
      <p class="notice">La descarga no está habilitada para esta revisión.</p>
      <div aria-live="polite">Resultado listo para revisar.</div></main>"""


def _result_value(*, computation: dict[str, Any], typed: dict[str, Any], outcome: dict[str, Any]) -> Any:
    if "value" in typed:
        return typed["value"]
    if "value" in computation:
        return computation["value"]
    computed = outcome.get("computed_results")
    if isinstance(computed, dict) and computed:
        return next(iter(computed.values()))
    return "No disponible"


def _data_used(computation: dict[str, Any], outcome: dict[str, Any]) -> str:
    provenance = computation.get("provenance") if isinstance(computation.get("provenance"), dict) else {}
    variables = provenance.get("variables") if isinstance(provenance.get("variables"), dict) else {}
    values = list(variables.values()) if variables else list((outcome.get("inputs_used") or {}).values())
    if not values:
        return "<p>Se usaron las columnas confirmadas del archivo.</p>"
    return "<ul>" + "".join(f"<li>Dato confirmado {index}: {_esc(value)}</li>" for index, value in enumerate(values, start=1)) + "</ul>"


def _blocked_result_page(packet: dict[str, Any], requested_capability: str | None = None) -> str:
    title = _REVIEW_BY_REF.get(requested_capability or "", ("", "Resultado", ""))[1]
    return _blocked_message_page(f"No se puede completar {title.lower()} con los datos confirmados. Revisá las columnas elegidas o seleccioná otra revisión.")


def _blocked_message_page(message: str) -> str:
    return f'<main id="app" tabindex="-1"><h1>No se puede continuar</h1><p role="alert">{_esc(message)}</p><p>La descarga no está habilitada.</p><div aria-live="polite">Necesita revisión.</div></main>'


def _error_page(message: str) -> str:
    return f'<main id="app" tabindex="-1"><h1>Revisar información de mi negocio</h1><p role="alert">{_esc(message)}</p><a href="/">Volver al inicio</a><div aria-live="polite">Necesita revisión.</div></main>'


def _error(message: str | None) -> str:
    return f'<p role="alert">{_esc(message)}</p>' if message else ""


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Servicio 1 assisted web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = create_assisted_web_server_v1(host=args.host, port=args.port)
    print(f"Servicio 1 disponible en http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()


__all__ = ["AssistedWebApplicationV1", "AssistedWebSessionV1", "create_assisted_web_server_v1", "main"]

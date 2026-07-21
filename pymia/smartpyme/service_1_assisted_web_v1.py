"""Local, assisted HTML flow for the single Servicio 1 product root."""
from __future__ import annotations

import argparse
import html
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
    STATUS_READY as CANONICAL_INGESTION_READY,
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_NEEDS_OWNER,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)

_MODULE_DIR = Path(__file__).resolve().parent
_TEMPLATE_PATH = _MODULE_DIR / "templates" / "service_1_assisted_web_v1.html"
_STYLES_PATH = _MODULE_DIR / "static" / "service_1_assisted_web_v1.css"

_REVIEW_OPTIONS: tuple[tuple[str, str, str], ...] = (
    ("sold_vs_collected_gap", "Ventas y cobros", "Compará lo vendido con lo cobrado en el período."),
    ("projected_closing_cash_balance", "Saldo de caja proyectado", "Calculá un saldo de cierre a partir de movimientos confirmados."),
    ("dso", "Tiempo de cobro", "Conocé la relación entre cuentas por cobrar, ventas y días del período."),
    ("dpo", "Tiempo de pago", "Conocé la relación entre cuentas por pagar, compras y días del período."),
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


@dataclass
class AssistedWebSessionV1:
    intake_packet: dict[str, Any] | None = None
    ingestion_output: dict[str, Any] | None = None
    semantic_questions: list[dict[str, Any]] = field(default_factory=list)
    semantic_answers: dict[str, Any] = field(default_factory=dict)


class AssistedWebApplicationV1:
    """Small in-memory coordinator. It never stores uploaded workbook bytes."""

    def __init__(self, *, output_dir: str | Path | None = None) -> None:
        self._sessions: dict[str, AssistedWebSessionV1] = {}
        self.output_dir = Path(output_dir) if output_dir is not None else Path(tempfile.mkdtemp(prefix="pymia-service-1-web-"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def session(self, session_id: str) -> AssistedWebSessionV1:
        return self._sessions.setdefault(session_id, AssistedWebSessionV1())

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
        state = self.session(session_id)
        state.intake_packet = intake
        state.ingestion_output = None
        state.semantic_questions = []
        state.semantic_answers = {}
        return HTTPStatus.OK, _file_received_page(intake)

    def confirm_columns(self, *, session_id: str, fields: dict[str, str]) -> tuple[int, str]:
        state = self.session(session_id)
        packet = state.intake_packet
        if not isinstance(packet, dict):
            return HTTPStatus.BAD_REQUEST, _error_page("Primero elegí un archivo de Excel.")
        answers = {question["question_id"]: fields.get(f"meaning_{question['question_id']}", "").strip() for question in packet.get("owner_questions", [])}
        if any(not answer for answer in answers.values()):
            return HTTPStatus.BAD_REQUEST, _column_confirmation_page(packet, "Respondé cada pregunta o elegí No estoy seguro.")
        canonical = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
            owner_question_packet=packet,
            owner_answers=answers,
        )
        if canonical.get("status") != CANONICAL_INGESTION_READY:
            return HTTPStatus.BAD_REQUEST, _error_page("No se pudieron confirmar las columnas. Volvé a revisar las respuestas.")
        ingestion = dict(canonical["ingestion_output"])
        ingestion["normalized_tables"] = list(packet.get("normalized_tables") or [])
        state.ingestion_output = ingestion
        try:
            first_run = _run_product_root(ingestion_output=ingestion, output_dir=self.output_dir)
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
            else:
                self._send_html(HTTPStatus.NOT_FOUND, _error_page("No encontramos esa página."))

        def do_POST(self) -> None:  # noqa: N802
            session_id = self._session_id()
            try:
                if self.path == "/upload":
                    filename, content = _multipart_file(self)
                    status, content_html = application.receive_xlsx(session_id=session_id, filename=filename, content=content)
                else:
                    fields = _form_fields(self)
                    if self.path == "/confirm-columns":
                        status, content_html = application.confirm_columns(session_id=session_id, fields=fields)
                    elif self.path == "/confirm-meanings":
                        status, content_html = application.confirm_meanings(session_id=session_id, fields=fields)
                    elif self.path == "/run-review":
                        status, content_html = application.run_review(session_id=session_id, requested_capability=fields.get("review", ""))
                    else:
                        status, content_html = HTTPStatus.NOT_FOUND, _error_page("No encontramos esa acción.")
            except ValueError:
                status, content_html = HTTPStatus.BAD_REQUEST, _error_page("No se pudo leer el envío. Probá de nuevo.")
            self._send_html(status, content_html, session_id=session_id)

        def _session_id(self) -> str:
            cookie = self.headers.get("Cookie", "")
            for part in cookie.split(";"):
                name, _, value = part.strip().partition("=")
                if name == "service1_session" and value:
                    return value
            return secrets.token_urlsafe(18)

        def _send_html(self, status: int, content: str, *, session_id: str | None = None) -> None:
            self._send(status, _document(content).encode("utf-8"), "text/html; charset=utf-8", session_id=session_id)

        def _send(self, status: int, body: bytes, content_type: str, *, session_id: str | None = None) -> None:
            self.send_response(int(status))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if session_id is not None:
                self.send_header("Set-Cookie", f"service1_session={session_id}; Path=/; SameSite=Lax; HttpOnly")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def _multipart_file(handler: BaseHTTPRequestHandler) -> tuple[str, bytes]:
    content_type = handler.headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type:
        raise ValueError("multipart form data required")
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0 or length > 20 * 1024 * 1024:
        raise ValueError("invalid upload size")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + handler.rfile.read(length)
    )
    for part in message.iter_attachments():
        if part.get_param("name", header="content-disposition") == "file":
            filename = part.get_filename() or ""
            payload = part.get_payload(decode=True)
            return filename, payload if isinstance(payload, bytes) else b""
    raise ValueError("file field required")


def _form_fields(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length).decode("utf-8", errors="replace")
    parsed = parse_qs(raw, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _document(content: str) -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("{{content}}", content)


def _home_page() -> str:
    return """
    <main id="app" tabindex="-1">
      <h1>Revisar información de mi negocio</h1>
      <p>Subí un archivo de Excel y te ayudaremos a entenderlo paso a paso.</p>
      <form action="/upload" method="post" enctype="multipart/form-data" hx-post="/upload" hx-target="#app" hx-swap="outerHTML">
        <label for="file">Elegir archivo</label>
        <input id="file" name="file" type="file" accept=".xlsx" required>
        <p>Tu archivo no se modifica.</p>
        <p>Antes de hacer cálculos, te pediremos que confirmes qué significa cada dato.</p>
        <button type="submit">Continuar</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _file_received_page(packet: dict[str, Any]) -> str:
    sheets = ", ".join(_esc(item) for item in packet.get("sheet_names") or []) or "Sin hojas legibles"
    columns = "".join(f"<li>{_esc(column)}</li>" for column in packet.get("columns") or [])
    rows = sum(len(table.get("rows") or []) for table in packet.get("normalized_tables") or [] if isinstance(table, dict))
    return f"""
    <main id="app" tabindex="-1">
      <h1>Archivo recibido</h1>
      <p><strong>{_esc(packet.get('filename'))}</strong></p>
      <p>Hojas encontradas: {sheets}.</p>
      <p>Encontramos {rows} filas y {len(packet.get('columns') or [])} columnas.</p>
      <h2>Columnas encontradas</h2><ul>{columns}</ul>
      <form action="/confirm-columns" method="post" hx-post="/confirm-columns" hx-target="#app" hx-swap="outerHTML">
        <button type="submit">Continuar</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _column_confirmation_page(packet: dict[str, Any], error: str | None = None) -> str:
    questions = []
    for question in packet.get("owner_questions") or []:
        question_id = _esc(question.get("question_id"))
        column = _esc(question.get("column_name"))
        questions.append(f"""
        <fieldset><legend>¿Qué representa la columna {column}?</legend>
          <label><input type="radio" name="meaning_{question_id}" value="importe de ventas" required> Importe de ventas</label>
          <label><input type="radio" name="meaning_{question_id}" value="costo o gasto"> Costo o gasto</label>
          <label><input type="radio" name="meaning_{question_id}" value="fecha o período"> Fecha o período</label>
          <label><input type="radio" name="meaning_{question_id}" value="otra cosa"> Otra cosa</label>
          <label><input type="radio" name="meaning_{question_id}" value="not_sure"> No estoy seguro</label>
        </fieldset>""")
    return f"""
    <main id="app" tabindex="-1"><h1>Confirmar columnas</h1>
      {_error(error)}<form action="/confirm-columns" method="post" hx-post="/confirm-columns" hx-target="#app" hx-swap="outerHTML">{''.join(questions)}<button type="submit">Continuar</button></form>
      <div class="notice" aria-live="polite"></div></main>"""


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

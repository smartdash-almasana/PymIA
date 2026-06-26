from __future__ import annotations

from typing import Any, Final, Literal, NotRequired, TypedDict

OwnerPureViewStatus = Literal["DELIVERED_CANDIDATE", "BLOCKED"]

SCHEMA_VERSION: Final[str] = "OWNER_PURE_VIEW_V1"
SAFE_LIMIT_WARNING: Final[str] = "No diagnostica sin evidencia suficiente ni confirmación del dueño."

_FORBIDDEN_TECHNICAL_TERMS: Final[tuple[str, ...]] = (
    "structured_evidence",
    "formula_ids",
    "diagnostic_result",
    "kernel_state",
    "task_spec",
    "taskspec",
    "runtime_authorized",
    "output_hash",
    "run_id",
    "evidence_id",
    "jsonl",
    "traceback",
    "python",
    "pytest",
    "vertical_pipeline",
    "document_ingestion",
)


class OwnerPureView(TypedDict):
    schema_version: str
    status: OwnerPureViewStatus
    title: str
    owner_summary: str
    what_we_could_read: list[str]
    what_is_missing: list[str]
    next_question: str
    next_step: str
    limits: list[str]


class OwnerPureViewInput(TypedDict, total=False):
    status: str
    file_name: NotRequired[str]
    rows: NotRequired[int]
    columns: NotRequired[int]
    headers: NotRequired[list[str]]
    table_sheets: NotRequired[list[dict[str, Any]]]
    missing_evidence: NotRequired[list[str]]
    next_questions: NotRequired[list[str]]
    limit_warnings: NotRequired[list[str]]
    owner_summary: NotRequired[str]


def build_owner_pure_view(*, report: dict[str, Any]) -> OwnerPureView:
    """Build a non-technical owner-facing view from an existing report dict.

    This function is deliberately pure: no IO, no pipeline calls, no LLM calls and
    no runtime authorization. It only filters and phrases already available data.
    """

    status = _normalize_status(report.get("status"))
    file_name = _normalize_optional_text(report.get("file_name") or report.get("file"))
    rows = _normalize_int(report.get("rows"))
    columns = _normalize_int(report.get("columns"))
    headers = _normalize_text_list(report.get("headers", []))
    table_sheets = _normalize_table_sheets(report.get("table_sheets", []))
    missing = _normalize_text_list(report.get("missing_evidence", []))
    questions = _normalize_text_list(report.get("next_questions", []))
    limits = _merge_limits(_normalize_text_list(report.get("limit_warnings", [])))

    view: OwnerPureView = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "title": _build_title(status=status),
        "owner_summary": _build_owner_summary(status=status, owner_summary=report.get("owner_summary")),
        "what_we_could_read": _build_readable_facts(
            file_name=file_name,
            rows=rows,
            columns=columns,
            headers=headers,
            table_sheets=table_sheets,
        ),
        "what_is_missing": _build_missing_items(status=status, missing=missing),
        "next_question": _build_next_question(status=status, questions=questions, missing=missing),
        "next_step": _build_next_step(status=status, missing=missing),
        "limits": limits,
    }
    _assert_owner_safe(view)
    return view


def _normalize_status(value: object) -> OwnerPureViewStatus:
    status = _normalize_optional_text(value)
    if status == "DELIVERED":
        return "DELIVERED_CANDIDATE"
    if status in {"DELIVERED_CANDIDATE", "BLOCKED"}:
        return status  # type: ignore[return-value]
    if status == "candidate":
        return "DELIVERED_CANDIDATE"
    if status == "blocked":
        return "BLOCKED"
    raise ValueError("owner pure view only accepts DELIVERED_CANDIDATE or BLOCKED status")


def _build_title(*, status: OwnerPureViewStatus) -> str:
    if status == "BLOCKED":
        return "Necesito un dato más para avanzar con seguridad."
    return "Primera lectura lista para revisar."


def _build_owner_summary(*, status: OwnerPureViewStatus, owner_summary: object) -> str:
    explicit = _normalize_optional_text(owner_summary)
    if explicit:
        return explicit
    if status == "BLOCKED":
        return "Pude leer parte del material, pero todavía falta evidencia mínima para entregar una lectura confiable."
    return "Pude leer la planilla y preparar una primera lectura. Debe revisarse como resultado candidato, no como diagnóstico final."


def _build_readable_facts(
    *,
    file_name: str | None,
    rows: int | None,
    columns: int | None,
    headers: list[str],
    table_sheets: list[dict[str, Any]],
) -> list[str]:
    facts: list[str] = []
    if file_name:
        facts.append(f"Archivo recibido: {file_name}.")
    if rows is not None and columns is not None:
        facts.append(f"La planilla tiene {rows} filas y {columns} columnas visibles.")
    elif rows is not None:
        facts.append(f"La planilla tiene {rows} filas visibles.")
    elif columns is not None:
        facts.append(f"La planilla tiene {columns} columnas visibles.")
    if headers:
        facts.append("Columnas detectadas: " + ", ".join(headers[:8]) + _ellipsis_if_needed(headers) + ".")
    if table_sheets:
        sheet_names = [_normalize_optional_text(sheet.get("name")) for sheet in table_sheets]
        visible_names = [name for name in sheet_names if name]
        if visible_names:
            facts.append("Hojas con tablas detectadas: " + ", ".join(visible_names[:6]) + _ellipsis_if_needed(visible_names) + ".")
    return facts or ["Pude recibir el material, pero todavía no hay estructura suficiente para describirlo con seguridad."]


def _build_missing_items(*, status: OwnerPureViewStatus, missing: list[str]) -> list[str]:
    if missing:
        return [_owner_label_for_missing(item) for item in missing]
    if status == "BLOCKED":
        return ["Falta evidencia mínima para avanzar sin inventar una conclusión."]
    return []


def _build_next_question(*, status: OwnerPureViewStatus, questions: list[str], missing: list[str]) -> str:
    if questions:
        return questions[0]
    if missing:
        return "¿Podés completar o confirmar la evidencia faltante para seguir?"
    if status == "BLOCKED":
        return "¿Podés enviar una planilla con datos operativos y al menos una fila de información?"
    return "¿Confirmás que estos datos representan el período que querés revisar?"


def _build_next_step(*, status: OwnerPureViewStatus, missing: list[str]) -> str:
    if status == "BLOCKED":
        if missing:
            return "Completar la evidencia faltante antes de calcular o diagnosticar."
        return "Enviar una versión con datos suficientes para poder avanzar."
    return "Revisar esta primera lectura con el dueño antes de tomarla como diagnóstico."


def _owner_label_for_missing(item: str) -> str:
    labels: dict[str, str] = {
        "filas_de_datos": "Faltan filas de datos además de los encabezados.",
        "columnas_operativas": "Faltan columnas operativas como fecha, producto, ventas, precio, costo, cantidad o SKU.",
    }
    return labels.get(item, item)


def _merge_limits(values: list[str]) -> list[str]:
    merged = list(values)
    if SAFE_LIMIT_WARNING not in merged:
        merged.append(SAFE_LIMIT_WARNING)
    return merged


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = _normalize_optional_text(item)
        if text:
            normalized.append(text)
    return normalized


def _normalize_table_sheets(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _normalize_int(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return None
    return normalized if normalized >= 0 else None


def _ellipsis_if_needed(values: list[str]) -> str:
    return "..." if len(values) > 8 else ""


def _assert_owner_safe(view: OwnerPureView) -> None:
    payload = _flatten_strings(view).casefold()
    for term in _FORBIDDEN_TECHNICAL_TERMS:
        if term.casefold() in payload:
            raise ValueError(f"owner pure view leaked technical term: {term}")


def _flatten_strings(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_flatten_strings(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_strings(item) for item in value)
    return ""


__all__ = [
    "OwnerPureView",
    "OwnerPureViewInput",
    "OwnerPureViewStatus",
    "SCHEMA_VERSION",
    "SAFE_LIMIT_WARNING",
    "build_owner_pure_view",
]

"""
Docling Document Metadata Adapter — Optional parser for PDF/DOCX/PPTX.

Produce ``ParsedDocumentMetadata`` a partir de archivos PDF/DOCX/PPTX usando
``docling`` como backend, con import **lazy** para que ``docling`` siga siendo
una dependencia opcional (no requerida por el paquete base).

Este módulo:
    - SOLO importa ``docling`` dentro de la función de parsing.
    - Si ``docling`` no está instalado → retorna ``parse_status=FAILED`` con
      warning ``optional_dependency_missing:docling`` (no rompe el flujo).
    - Si ``docling`` falla durante el parseo → retorna ``parse_status=FAILED``
      con warning ``docling_parse_error:<mensaje corto>``.
    - Si parsea con éxito → retorna ``ParsedDocumentMetadata`` con
      ``parse_status=OK`` o ``PARTIAL``, ``sections`` / ``tables`` /
      ``fields`` poblados y ``confidence`` conservadora.

Este módulo:
    - NO ejecuta fórmulas.
    - NO diagnostica.
    - NO genera reportes.
    - NO crea ``EvidenceRecord``.
    - NO toca ``evidence_gate`` / ``post_ficha_evidence_gate`` / ``intake``.
    - NO instala dependencias.
    - NO modifica ``pyproject.toml`` ni ``requirements*.txt``.
    - NO toca tests.
    - NO hace push.

Ver: pymia/smartpyme/parsed_document_metadata.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Tuple

from pymia.smartpyme.parsed_document_metadata import (
    DEFAULT_DOCUMENT_CONTEXT,
    DEFAULT_INGESTION_ROUTE,
    PARSE_STATUS_FAILED,
    PARSE_STATUS_OK,
    PARSE_STATUS_PARTIAL,
    ParsedDocumentMetadata,
    SectionSummary,
    TableSummary,
)


PARSER_NAME = "docling_v1"
PARSER_VERSION_FALLBACK = "unknown"

# Extensiones soportadas por este adaptador.
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx"}

# Confidence máxima conservadora incluso cuando Docling reporta éxito total.
_MAX_CONFIDENCE = 0.9
# Confidence base cuando Docling está instalado pero el documento es pobre.
_MIN_CONFIDENCE_ON_PARSE = 0.3


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_docling_to_document_metadata(
    source_ref: str | Path,
) -> ParsedDocumentMetadata:
    """
    Parse a local PDF/DOCX/PPTX file into ``ParsedDocumentMetadata`` using
    ``docling`` (optional dependency, lazy-imported).

    Fail-closed guarantees:
        - ``source_ref`` no válido o inexistente → ``FAILED`` + warning
          ``file_not_found``.
        - Extensión no soportada → ``FAILED`` + warning
          ``unsupported_extension:<ext>``.
        - ``docling`` no instalado → ``FAILED`` + warning
          ``optional_dependency_missing:docling``.
        - ``docling`` lanza excepción → ``FAILED`` + warning
          ``docling_parse_error:<mensaje corto>``.
        - Éxito → ``OK`` (con tablas o secciones) o ``PARTIAL`` (sin ninguno
          de los dos, pero sin error).
    """
    warnings: List[str] = []

    # 1) Validar path --------------------------------------------------------
    try:
        path = Path(source_ref)
    except TypeError as exc:
        return _build_failed(
            file_type=_safe_ext(source_ref),
            warnings=[f"invalid_path_type: {exc}"],
        )

    if not path.exists() or not path.is_file():
        return _build_failed(
            file_type=_safe_ext(path),
            warnings=[f"file_not_found: {path}"],
        )

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return _build_failed(
            file_type=_safe_ext(path) or "unknown",
            warnings=[f"unsupported_extension:{ext or '(none)'}"],
        )

    # 2) Lazy import de Docling ---------------------------------------------
    docling_mod, docling_err = _ensure_docling()
    if docling_mod is None:
        return _build_failed(
            file_type=ext.lstrip("."),
            warnings=[f"optional_dependency_missing:docling",
                      f"docling_import_error: {docling_err}"],
        )

    parser_version = _extract_docling_version(docling_mod)

    # 3) Ejecutar parser (aislado en try/except) ----------------------------
    try:
        document = _run_docling(docling_mod, path)
    except Exception as exc:  # noqa: BLE001 - aislamiento fail-closed
        short_msg = _short_message(exc)
        return _build_failed(
            file_type=ext.lstrip("."),
            parser_version=parser_version,
            warnings=[f"docling_parse_error:{short_msg}"],
        )

    if document is None:
        return _build_failed(
            file_type=ext.lstrip("."),
            parser_version=parser_version,
            warnings=["docling_parse_error: returned_none"],
        )

    # 4) Extraer secciones / tablas / fields --------------------------------
    sections = _extract_sections(document)
    tables, table_fields = _extract_tables(document)

    all_fields = _dedupe(table_fields)
    has_content = bool(sections or tables)

    parse_status = PARSE_STATUS_OK if has_content else PARSE_STATUS_PARTIAL
    confidence = _compute_confidence(
        n_sections=len(sections),
        n_tables=len(tables),
        n_fields=len(all_fields),
    )

    if not has_content:
        warnings.append("docling_empty_document: no_sections_or_tables")

    return ParsedDocumentMetadata(
        file_type=ext.lstrip("."),
        parser_name=PARSER_NAME,
        parser_version=parser_version,
        parse_status=parse_status,
        sheets=[],                     # no aplica a PDF/DOCX/PPTX
        tables=tables,
        sections=sections,
        fields=all_fields,
        ambiguous_fields=[],
        unknown_fields=[],
        declared_fields=[],
        warnings=warnings,
        confidence=confidence,
        ingestion_route=DEFAULT_INGESTION_ROUTE,
        document_context=DEFAULT_DOCUMENT_CONTEXT,
        raw_artifact_refs={"docling_source": str(path.resolve())},
    )


# ---------------------------------------------------------------------------
# Lazy Docling import
# ---------------------------------------------------------------------------
def _ensure_docling() -> Tuple[Optional[Any], Optional[str]]:
    """
    Try to ``import docling`` lazily.

    Returns:
        (module, None) on success.
        (None, error_message) on failure.
    """
    try:
        import docling  # type: ignore[import-not-found]  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        return None, _short_message(exc)
    return docling, None


def _extract_docling_version(docling_mod: Any) -> str:
    """Best-effort extraction of ``docling.__version__``; ``unknown`` otherwise."""
    version = getattr(docling_mod, "__version__", None)
    if isinstance(version, str) and version.strip():
        return version.strip()
    return PARSER_VERSION_FALLBACK


# ---------------------------------------------------------------------------
# Docling execution
# ---------------------------------------------------------------------------
def _run_docling(docling_mod: Any, path: Path) -> Optional[Any]:
    """
    Invoke ``docling.document_converter.DocumentConverter`` on ``path`` and
    return the parsed ``DoclingDocument`` (or ``None`` on empty result).

    Isolates all Docling API calls so that any API change in Docling only
    affects this helper, not the public adapter surface.
    """
    converter_cls = getattr(
        getattr(docling_mod, "document_converter", None),
        "DocumentConverter",
        None,
    )
    if converter_cls is None:
        raise RuntimeError("docling.document_converter.DocumentConverter not found")

    converter = converter_cls()
    result = converter.convert(str(path))

    # ``ConversionResult`` expone ``.document`` con el ``DoclingDocument``.
    document = getattr(result, "document", None)
    if document is None:
        # Some Docling versions return the document directly from convert().
        return result
    return document


# ---------------------------------------------------------------------------
# Extraction helpers (Docling → ParsedDocumentMetadata)
# ---------------------------------------------------------------------------
def _extract_sections(document: Any) -> List[SectionSummary]:
    """
    Walk the Docling document and emit one ``SectionSummary`` per heading
    (or per top-level text block if no headings are present).
    """
    sections: List[SectionSummary] = []

    # Docling exposes ``document.headings`` (iterable of SectionHeaderItem)
    # and ``document.texts`` (iterable of TextItem). Prefer headings when
    # available; fallback to texts when not.
    headings = getattr(document, "headings", None) or []
    try:
        heading_iter = list(headings)
    except TypeError:
        heading_iter = []

    if heading_iter:
        for h in heading_iter:
            heading_text = _safe_text(getattr(h, "text", ""))
            level = _safe_int(getattr(h, "level", 0))
            char_count = len(heading_text)
            if heading_text:
                sections.append(
                    SectionSummary(
                        heading=heading_text[:256],
                        level=level,
                        char_count=char_count,
                        keyword_hits=[],
                    )
                )
        return sections

    # Fallback: treat each text block as a pseudo-section.
    texts = getattr(document, "texts", None) or []
    try:
        text_iter = list(texts)
    except TypeError:
        text_iter = []

    for idx, t in enumerate(text_iter):
        text = _safe_text(getattr(t, "text", ""))
        if not text:
            continue
        sections.append(
            SectionSummary(
                heading=text[:128] or f"section_{idx}",
                level=0,
                char_count=len(text),
                keyword_hits=[],
            )
        )

    return sections


def _extract_tables(document: Any) -> Tuple[List[TableSummary], List[str]]:
    """
    Walk ``document.tables`` and emit one ``TableSummary`` per table, plus a
    flat list of header names (used as ``fields``).
    """
    summaries: List[TableSummary] = []
    fields: List[str] = []

    tables = getattr(document, "tables", None) or []
    try:
        table_iter = list(tables)
    except TypeError:
        table_iter = []

    for idx, t in enumerate(table_iter):
        table_id = _safe_text(getattr(t, "self_ref", "")) or f"table_{idx}"
        origin = f"docling_table:{idx}"

        # Header extraction: Docling's ``TableItem`` exposes ``.data`` with
        # ``grid`` (rows of cells) or ``.column_headers``. Try both.
        headers = _extract_table_headers(t)
        col_count = len(headers) or _safe_int(getattr(t, "num_cols", 0))
        row_count = _safe_int(getattr(t, "num_rows", 0))

        summaries.append(
            TableSummary(
                table_id=table_id or f"table_{idx}",
                origin=origin,
                column_count=col_count,
                row_count=row_count,
                header_sample=headers[:8],
                semantic_hint=None,
            )
        )
        fields.extend(headers)

    return summaries, fields


def _extract_table_headers(table_item: Any) -> List[str]:
    """Best-effort extraction of header names from a Docling ``TableItem``."""
    # 1) Try explicit ``column_headers`` attribute.
    headers_attr = getattr(table_item, "column_headers", None)
    if isinstance(headers_attr, (list, tuple)):
        out = [_safe_text(h) for h in headers_attr if _safe_text(h)]
        if out:
            return out

    # 2) Try ``data.grid`` / ``data`` with ``.text`` cells (first row).
    data = getattr(table_item, "data", None)
    grid = getattr(data, "grid", None) if data is not None else None
    if isinstance(grid, list) and grid:
        first_row = grid[0]
        if isinstance(first_row, list):
            headers: List[str] = []
            for cell in first_row:
                text = _safe_text(getattr(cell, "text", cell))
                if text:
                    headers.append(text)
            if headers:
                return headers

    return []


# ---------------------------------------------------------------------------
# Confidence (conservative)
# ---------------------------------------------------------------------------
def _compute_confidence(
    *, n_sections: int, n_tables: int, n_fields: int
) -> float:
    """
    Conservative confidence in ``[MIN, MAX]`` based on how much structure
    Docling was able to extract. Never reaches ``1.0`` to signal that
    manual review may still be required.
    """
    score = 0.0
    score += min(n_sections, 10) * 0.03      # up to 0.30
    score += min(n_tables, 5) * 0.08         # up to 0.40
    score += min(n_fields, 20) * 0.01        # up to 0.20
    score = max(_MIN_CONFIDENCE_ON_PARSE, min(_MAX_CONFIDENCE, score))
    return round(float(score), 3)


# ---------------------------------------------------------------------------
# Failed-metadata builders
# ---------------------------------------------------------------------------
def _build_failed(
    *,
    file_type: str,
    warnings: List[str],
    parser_version: str = PARSER_VERSION_FALLBACK,
) -> ParsedDocumentMetadata:
    return ParsedDocumentMetadata(
        file_type=file_type or "unknown",
        parser_name=PARSER_NAME,
        parser_version=parser_version,
        parse_status=PARSE_STATUS_FAILED,
        sheets=[],
        tables=[],
        sections=[],
        fields=[],
        ambiguous_fields=[],
        unknown_fields=[],
        declared_fields=[],
        warnings=warnings,
        confidence=0.0,
        ingestion_route=DEFAULT_INGESTION_ROUTE,
        document_context=DEFAULT_DOCUMENT_CONTEXT,
    )


# ---------------------------------------------------------------------------
# Sanitization helpers
# ---------------------------------------------------------------------------
def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    return s


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _safe_ext(value: Any) -> str:
    try:
        ext = Path(str(value)).suffix.lower().lstrip(".")
        return ext or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def _dedupe(values: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for v in values:
        s = _safe_text(v)
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _short_message(exc: BaseException) -> str:
    """Compact exception message, truncated to 160 chars, safe for warnings."""
    msg = str(exc) or exc.__class__.__name__
    msg = msg.replace("\n", " ").strip()
    if len(msg) > 160:
        return msg[:157] + "..."
    return msg


__all__ = [
    "parse_docling_to_document_metadata",
    "PARSER_NAME",
    "PARSER_VERSION_FALLBACK",
    "SUPPORTED_EXTENSIONS",
]

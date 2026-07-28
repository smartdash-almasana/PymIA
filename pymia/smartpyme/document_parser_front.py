"""
Document Parser Front — Router general para fuentes documentales locales.

Recibe un ``source_ref`` local y produce ``ParsedDocumentMetadata`` usando
el adaptador disponible según tipo de archivo.

Este módulo:
    - NO asume XLSX como único formato.
    - Delegates a ``parse_xlsx_to_document_metadata`` para ``.xlsx`` / ``.xlsm``.
    - Delegates a ``parse_docling_to_document_metadata`` para ``.pdf`` /
      ``.docx`` / ``.pptx`` (Docling es dependencia opcional; el adaptador
      hace el import lazy y es fail-closed si no está instalado).
    - Para ``.txt``, ``.md``, ``.csv``, ``.tsv`` (todavía no implementados),
      retorna ``ParsedDocumentMetadata`` con ``parse_status=FAILED`` y
      warnings explícitos.
    - Para extensiones desconocidas, retorna ``parse_status=FAILED`` con
      ``file_type="unknown"`` y warning ``unknown_extension:<ext>``.
    - NO instala Docling.
    - NO importa Docling directamente (el adaptador lo importa lazy).
    - NO ejecuta fórmulas.
    - NO diagnostica.
    - NO crea ``EvidenceRecord``.
    - NO toca gates.

Ver: pymia/smartpyme/parsed_document_metadata.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pymia.smartpyme.parsed_document_metadata import (
    DEFAULT_DOCUMENT_CONTEXT,
    DEFAULT_INGESTION_ROUTE,
    PARSE_STATUS_FAILED,
    ParsedDocumentMetadata,
)
from pymia.smartpyme.xlsx_document_metadata_adapter import (
    parse_xlsx_to_document_metadata,
)
from pymia.smartpyme.docling_document_metadata_adapter import (
    parse_docling_to_document_metadata,
)


ROUTER_NAME = "document_parser_front"
ROUTER_VERSION = "1.1.0"

# Extensiones soportadas por adaptadores existentes
_XLSX_EXTENSIONS = {".xlsx", ".xlsm"}
_DOCLING_EXTENSIONS = {".pdf", ".docx", ".pptx"}

# Extensiones reconocidas pero sin parser implementado todavía
_UNIMPLEMENTED_PARSERS = {
    ".txt": "plaintext_v1",
    ".md": "plaintext_v1",
    ".csv": "csv_parser_v1",
    ".tsv": "csv_parser_v1",
}


def parse_document_to_metadata(source_ref: str | Path) -> ParsedDocumentMetadata:
    """
    Router documental general que recibe un ``source_ref`` local y devuelve
    ``ParsedDocumentMetadata`` usando el adaptador disponible según tipo de archivo.

    Fail-closed:
        - Si el path es inválido → ``parse_status=FAILED`` con warning.
        - Si la extensión no es reconocida → ``parse_status=FAILED`` con
          ``file_type="unknown"`` y warning ``"unknown_extension:<ext>"``.
        - Si la extensión es reconocida pero el parser no está implementado
          todavía (``.txt`` / ``.md`` / ``.csv`` / ``.tsv``) →
          ``parse_status=FAILED`` con warning ``"parser_not_configured:<ext>"``.
        - Si la extensión es ``.xlsx`` o ``.xlsm`` → delega a
          ``parse_xlsx_to_document_metadata`` (que ya es fail-closed).
        - Si la extensión es ``.pdf``, ``.docx`` o ``.pptx`` → delega a
          ``parse_docling_to_document_metadata`` (que hace import lazy de
          Docling y es fail-closed si la dependencia no está instalada).
    """
    warnings: list[str] = []

    # 1) Validar path --------------------------------------------------------
    try:
        path = Path(source_ref)
    except TypeError as exc:
        return _build_unsupported_metadata(
            file_type="unknown",
            warnings=[f"invalid_path_type: {exc}"],
        )

    if not path.exists():
        return _build_unsupported_metadata(
            file_type="unknown",
            warnings=[f"file_not_found: {path}"],
        )

    ext = path.suffix.lower()

    # 2) Dispatch por extensión ----------------------------------------------
    if ext in _XLSX_EXTENSIONS:
        return parse_xlsx_to_document_metadata(path)

    if ext in _DOCLING_EXTENSIONS:
        # El adaptador Docling hace el import lazy y retorna FAILED si
        # docling no está instalado; no necesitamos verificarlo aquí.
        return parse_docling_to_document_metadata(path)

    if ext in _UNIMPLEMENTED_PARSERS:
        parser_name = _UNIMPLEMENTED_PARSERS[ext]
        file_type = ext.lstrip(".")
        return _build_unsupported_metadata(
            file_type=file_type,
            warnings=[f"parser_not_configured:{ext}"],
            parser_name=parser_name,
        )

    # 3) Extensión desconocida -----------------------------------------------
    return _build_unsupported_metadata(
        file_type="unknown",
        warnings=[f"unknown_extension:{ext or '(none)'}"],
    )


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _build_unsupported_metadata(
    file_type: str,
    warnings: list[str],
    parser_name: str = ROUTER_NAME,
) -> ParsedDocumentMetadata:
    """
    Construye metadata fail-closed para formatos no soportados o desconocidos.

    Retorna ``parse_status=FAILED`` con ``confidence=0.0`` y warnings explícitos.
    """
    return ParsedDocumentMetadata(
        file_type=file_type,
        parser_name=parser_name,
        parser_version=ROUTER_VERSION,
        parse_status=PARSE_STATUS_FAILED,
        warnings=warnings,
        confidence=0.0,
        ingestion_route=DEFAULT_INGESTION_ROUTE,
        document_context=DEFAULT_DOCUMENT_CONTEXT,
    )


__all__ = [
    "parse_document_to_metadata",
    "ROUTER_NAME",
    "ROUTER_VERSION",
]

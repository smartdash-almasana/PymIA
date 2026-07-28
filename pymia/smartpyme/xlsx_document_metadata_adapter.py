"""
XLSX Document Metadata Adapter.

Adaptador delgado que reutiliza ``ExcelProfileBuilder``
(``tools/bem_schema_builder/excel_profile_builder.py``) para producir un
``ParsedDocumentMetadata`` compatible con ``EvidenceRecord.metadata`` y
``EvidenceSufficiencyGate``.

Este módulo:
    - Reutiliza el lector estructural existente (no crea uno nuevo).
    - NO lee semántica de negocio más allá de la estructura/mapeo existente.
    - NO genera ``EvidenceRecord``.
    - NO toca ``evidence_gate`` ni ``post_ficha_evidence_gate``.
    - NO toca ``intake``.
    - NO ejecuta fórmulas.
    - NO diagnostica.
    - NO calcula variables derivadas (``ventas_total``, ``margen_bruto``, etc.).
    - NO importa ``docling``.

Ver: pymia/smartpyme/parsed_document_metadata.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pymia.smartpyme.parsed_document_metadata import (
    DEFAULT_DOCUMENT_CONTEXT,
    DEFAULT_INGESTION_ROUTE,
    PARSE_STATUS_FAILED,
    PARSE_STATUS_OK,
    PARSE_STATUS_PARTIAL,
    ParsedDocumentMetadata,
    SheetSummary,
)
from tools.bem_schema_builder.excel_profile_builder import ExcelProfileBuilder


PARSER_NAME = "excel_profile_v1"
PARSER_VERSION = "1.0.0"
FILE_TYPE = "xlsx"
_ALLOWED_EXTENSIONS = {".xlsx", ".xlsm"}


def parse_xlsx_to_document_metadata(
    excel_path: str | Path,
) -> ParsedDocumentMetadata:
    """
    Consume un XLSX local y produce ``ParsedDocumentMetadata`` reutilizando
    ``ExcelProfileBuilder``.

    Fail-closed:
        - Path inexistente → ``parse_status=FAILED`` con warning explícito.
        - Extensión no permitida → ``parse_status=FAILED``.
        - Error en ``ExcelProfileBuilder`` → ``parse_status=FAILED``.
        - Sin campos detectados → ``parse_status=FAILED``.
        - Solo campos desconocidos/ambiguos → ``parse_status=PARTIAL``.
    """
    warnings: list[str] = []

    # 1) Validar path y extensión --------------------------------------------
    path_validation = _validate_path(excel_path, warnings)
    if path_validation is not None:
        return path_validation
    path: Path = Path(excel_path)

    # 2) Reutilizar ExcelProfileBuilder -------------------------------------
    try:
        profile = ExcelProfileBuilder().build_profile(path)
    except Exception as exc:  # noqa: BLE001 — aislamiento del lector externo
        warnings.append(f"profile_builder_error: {exc}")
        return _build_failed_metadata(warnings)

    # 3) Construir SheetSummary por cada hoja del workbook ------------------
    sheets: list[SheetSummary] = []
    all_fields: set[str] = set()
    all_ambiguous: set[str] = set()
    all_unknown: set[str] = set()

    for sheet in profile.sheets:
        detected, ambiguous, unknown = _classify_sheet_columns(sheet)

        if detected or ambiguous:
            sheet_status = "OK"
        elif unknown:
            sheet_status = "PARTIAL"
        else:
            sheet_status = "BLOCKED"

        sheets.append(
            SheetSummary(
                name=sheet.sheet_name,
                kind=sheet.sheet_kind or "auxiliary",
                header_row=sheet.probable_header_row,
                column_count=int(sheet.max_column or 0),
                row_count=int(sheet.max_row or 0),
                fields_detected=detected,
                fields_ambiguous=ambiguous,
                fields_unknown=unknown,
                status=sheet_status,
            )
        )

        all_fields.update(detected)
        all_ambiguous.update(ambiguous)
        all_unknown.update(unknown)

    # 4) Calcular status global ---------------------------------------------
    fields_list = sorted(all_fields)
    ambiguous_list = sorted(all_ambiguous)
    unknown_list = sorted(all_unknown)

    if fields_list or ambiguous_list:
        parse_status = PARSE_STATUS_OK
    elif sheets and unknown_list:
        parse_status = PARSE_STATUS_PARTIAL
    else:
        parse_status = PARSE_STATUS_FAILED
        warnings.append("no_fields_detected")

    # 5) Confidence: promedio de tabular_likelihood en sheets tabulares -----
    confidence = _compute_confidence(profile.sheets, warnings)

    # 6) Advertencias estructurales por hoja --------------------------------
    for sheet in profile.sheets:
        if getattr(sheet, "formula_cells_count", 0) > 0:
            warnings.append(
                f"sheet:{sheet.sheet_name}:formula_cells_present"
            )
        if getattr(sheet, "merged_ranges", None):
            warnings.append(
                f"sheet:{sheet.sheet_name}:merged_ranges_present"
            )

    # 7) Construir metadata común -------------------------------------------
    return ParsedDocumentMetadata(
        file_type=FILE_TYPE,
        parser_name=PARSER_NAME,
        parser_version=PARSER_VERSION,
        parse_status=parse_status,
        sheets=sheets,
        fields=fields_list,
        ambiguous_fields=ambiguous_list,
        unknown_fields=unknown_list,
        warnings=warnings,
        confidence=confidence,
        ingestion_route=DEFAULT_INGESTION_ROUTE,
        document_context=DEFAULT_DOCUMENT_CONTEXT,
        raw_artifact_refs={"profile_source": str(path.resolve())},
    )


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _validate_path(
    excel_path: Any, warnings: list[str]
) -> ParsedDocumentMetadata | None:
    """Retorna metadata FAILED si el path es inválido; ``None`` si es válido."""
    try:
        path = Path(excel_path)
    except TypeError as exc:
        return _build_failed_metadata(
            [f"invalid_path_type: {exc}"]
        )

    if not path.exists():
        return _build_failed_metadata(
            [f"file_not_found: {path}"]
        )

    if path.suffix.lower() not in _ALLOWED_EXTENSIONS:
        return _build_failed_metadata(
            [f"unsupported_extension: {path.suffix!r}"]
        )

    return None


def _classify_sheet_columns(sheet: Any) -> tuple[list[str], list[str], list[str]]:
    """
    Dada una ``SheetProfile`` (con ``columns: list[ColumnProfile]``),
    clasifica cada columna en detectada / ambigua / desconocida.
    """
    detected: list[str] = []
    ambiguous: list[str] = []
    unknown: list[str] = []

    columns = getattr(sheet, "columns", None) or []
    for col in columns:
        label = getattr(col, "semantic_label", None)
        is_ambiguous = bool(getattr(col, "is_ambiguous", False))
        col_name = str(getattr(col, "name", "") or "")

        if not label:
            if col_name:
                unknown.append(col_name)
            continue

        if label == "unknown":
            if col_name:
                unknown.append(col_name)
        elif is_ambiguous:
            ambiguous.append(label)
        else:
            detected.append(label)

    return sorted(set(detected)), sorted(set(ambiguous)), sorted(set(unknown))


def _compute_confidence(
    sheets: list[Any], warnings: list[str]
) -> float:
    """
    Promedio de ``tabular_likelihood`` sobre hojas tabulares. Si no hay
    hojas tabulares, retorna 0.0 y agrega un warning.
    """
    tabular_sheets = [
        s for s in sheets if getattr(s, "sheet_kind", None) == "tabular"
    ]
    if not tabular_sheets:
        if sheets:
            warnings.append("no_tabular_sheets_detected")
        return 0.0

    likelihoods: list[float] = []
    for s in tabular_sheets:
        value = getattr(s, "tabular_likelihood", 0.0)
        try:
            likelihoods.append(float(value or 0.0))
        except (TypeError, ValueError):
            likelihoods.append(0.0)

    if not likelihoods:
        return 0.0
    return round(sum(likelihoods) / len(likelihoods), 3)


def _build_failed_metadata(warnings: list[str]) -> ParsedDocumentMetadata:
    """Construye metadata fail-closed para casos de input inválido o error."""
    return ParsedDocumentMetadata(
        file_type=FILE_TYPE,
        parser_name=PARSER_NAME,
        parser_version=PARSER_VERSION,
        parse_status=PARSE_STATUS_FAILED,
        warnings=warnings,
        confidence=0.0,
        ingestion_route=DEFAULT_INGESTION_ROUTE,
        document_context=DEFAULT_DOCUMENT_CONTEXT,
    )


__all__ = [
    "parse_xlsx_to_document_metadata",
    "PARSER_NAME",
    "PARSER_VERSION",
    "FILE_TYPE",
]

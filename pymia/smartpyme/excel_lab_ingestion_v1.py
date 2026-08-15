"""Productized Excel Lab Ingestion for PymIA/SmartPyme.

This module provides the logic to:
1. Ingest Excel structures (Structural Intake/Reader)
2. Profile and normalize columns and map semantic fields (Profiling/Extraction)
3. Generate structured evidence (Structured Evidence Exporter)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, ClassVar
import unicodedata

import pandas as pd
from pydantic import BaseModel, ConfigDict, ValidationError

from pymia.contracts.evidence_v1 import EvidenceTable, StructuredEvidence
from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    infer_calculation_relevance,
)
from pymia.smartpyme.evidence_value_normalizer import normalize_evidence_value
from tools.bem_schema_builder.excel_profile_builder import ColumnSemanticClassifier, ExcelProfileBuilder


# ==============================================================================
# 0. COMMON DEFINITIONS & HELPERS
# ==============================================================================

JsonObject = dict[str, Any]

NUMERIC_FIELDS = {
    "cantidad",
    "precio_venta",
    "costo_unitario",
    "venta_total",
    "costo_total",
    "margen",
    "stock",
    "stock_final",
    "saldo",
    "pago",
    "cobro",
    "ingreso",
    "egreso",
}

# Governed structural marker for exact duplicate business rows in curated tables.
# Not a column name: signals that duplicate rows require owner review before any
# affected calculation. Never used for automatic deduplication or row selection.
DUPLICATE_ROWS_AMBIGUITY_MARKER: str = "__duplicate_rows__"
TOTAL_ROWS_AMBIGUITY_MARKER: str = "__embedded_total_rows__"
MIXED_CURRENCY_AMBIGUITY_MARKER: str = "__mixed_currency__"


class _BaseTypedRow(BaseModel):
    model_config = ConfigDict(extra="ignore")


class ProductoRow(_BaseTypedRow):
    sku: str | None = None
    producto: str | None = None
    stock: int | None = None
    stock_final: int | None = None
    costo_unitario: float | None = None
    precio_venta: float | None = None


class VentaRow(_BaseTypedRow):
    fecha: date | None = None
    factura: str | None = None
    cliente: str | None = None
    canal: str | None = None
    producto: str | None = None
    cantidad: float | None = None
    precio_venta: float | None = None
    venta_total: float | None = None
    margen: float | None = None


class StockRow(_BaseTypedRow):
    fecha: date | None = None
    sku: str | None = None
    producto: str | None = None
    stock: int | None = None
    stock_final: int | None = None
    cantidad: float | None = None


class CajaBancoRow(_BaseTypedRow):
    fecha: date | None = None
    pago: float | None = None
    cobro: float | None = None
    saldo: float | None = None
    factura: str | None = None
    cliente: str | None = None
    proveedor: str | None = None


class SignalRow(_BaseTypedRow):
    signal_id: str | None = None
    mes: str | None = None
    signal_type: str | None = None
    description: str | None = None
    evidencia_relacionada: str | None = None
    severity: str | None = None
    suggested_action: str | None = None


def json_dumps(payload: Any) -> str:
    import json
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _safe_column_name(value: Any, index: int) -> str:
    if value is None:
        return f"unnamed_{index}"
    text = str(value).strip()
    return text or f"unnamed_{index}"


def _clean_record(record: JsonObject) -> JsonObject:
    clean: JsonObject = {}
    for key, value in record.items():
        if pd.isna(value):
            clean[str(key)] = None
        elif hasattr(value, "isoformat"):
            clean[str(key)] = value.isoformat()
        else:
            clean[str(key)] = value
    return clean


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            text = value.strip().replace("$", "").replace("%", "")
            text = text.replace("\u00a0", "").replace(" ", "")
            if not text or text.lower() in {"nan", "none", "null", "-"}:
                return None
            if "," in text and "." in text:
                if text.rfind(",") > text.rfind("."):
                    text = text.replace(".", "").replace(",", ".")
                else:
                    text = text.replace(",", "")
            elif "," in text:
                text = text.replace(".", "").replace(",", ".")
            return float(text)
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_text(text: Any) -> str:
    return str(text or "").strip().lower().replace("_", " ").replace("-", " ")


def _normalize_lookup_key(text: str) -> str:
    t = str(text or "").strip().lower().replace("", "ñ")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return t


def _to_int(value: Any) -> int | None:
    num = _to_float(value)
    if num is None:
        return None
    return int(round(num))


def _to_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "-"}:
        return None

    if not (("-" in text or "/" in text) and any(c.isdigit() for c in text)):
        return None

    import re
    is_iso = bool(re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}", text))
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=not is_iso)
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _coerce_semantic_value(field_name: str, value: Any, *, context: str) -> Any:
    if value is None:
        return None
    numeric_fields = NUMERIC_FIELDS | {"precio_unitario", "descuento_pct"}
    int_fields = {"stock", "stock_final", "stock_minimo"}
    date_fields = {"fecha", "vencimiento", "fecha_pago"}
    text_fields = {"producto", "cliente", "canal", "proveedor", "factura", "sku"}

    if field_name in int_fields or (context == "stock" and field_name == "cantidad"):
        return _to_int(value)
    if field_name in numeric_fields:
        parsed = _to_float(value)
        if parsed is None and isinstance(value, str):
            text = value.strip().lower()
            if text and text not in {"nan", "none", "null", "-"}:
                return value
        return parsed
    if field_name in date_fields:
        return _to_date(value)
    if field_name in text_fields:
        text = str(value).strip()
        return text if text else None
    return value


def _get_required_labels(variable_name: str) -> set[str]:
    """Return the set of semantic labels required to compute a given variable."""
    from pymia.contracts.column_confirmation_v1 import _VARIABLE_REQUIRED_LABELS
    return _VARIABLE_REQUIRED_LABELS.get(variable_name, set())


# ==============================================================================
# 1. INGESTIÓN / LECTURA ESTRUCTURAL
# ==============================================================================

@dataclass(frozen=True, slots=True)
class RawTable:
    sheet_name: str
    header_row: int
    columns: list[str]
    records: list[JsonObject]
    context: str = "generic"

    def to_dict(self) -> JsonObject:
        return asdict(self)


class ContextClassifier:
    _CONTEXT_KEYWORDS: ClassVar[dict[str, tuple[str, ...]]] = {
        "productos": ("producto", "productos", "sku", "lista", "precios"),
        "ventas": ("venta", "ventas", "facturacion", "cliente"),
        "stock": ("stock", "inventario", "deposito"),
        "caja_banco": ("caja", "banco", "mercado pago", "saldo", "conciliacion"),
        "compras": ("compra", "compras", "proveedor", "factura"),
        "senales_operativas": ("señal", "senal", "resumen", "kpi", "dashboard"),
    }

    def classify(self, sheet_name: str, columns: list[str]) -> str:
        haystack = _normalize_text(" ".join([sheet_name, *columns]))
        scores = {
            context: sum(1 for keyword in keywords if keyword in haystack)
            for context, keywords in self._CONTEXT_KEYWORDS.items()
        }
        best_context, best_score = max(scores.items(), key=lambda item: item[1])
        return best_context if best_score > 0 else "generic"


class XlsxDocumentIngestor:
    """Extract raw tabular tables from XLSX using PymIA's existing profiler."""

    def __init__(self) -> None:
        self._profiler = ExcelProfileBuilder()
        self._context_classifier = ContextClassifier()

    def ingest(self, excel_path: str | Path) -> list[RawTable]:
        path = Path(excel_path)
        profile = self._profiler.build_profile(path)
        tables: list[RawTable] = []
        for sheet in profile.sheets:
            if not sheet.columns or sheet.probable_header_row is None:
                continue
            if sheet.sheet_kind not in {"tabular", "summary"}:
                continue

            raw = pd.read_excel(path, sheet_name=sheet.sheet_name, header=None, dtype=object)
            header_idx = sheet.probable_header_row - 1
            columns = [_safe_column_name(value, idx + 1) for idx, value in enumerate(raw.iloc[header_idx].tolist())]
            body = raw.iloc[header_idx + 1 :].copy()
            body.columns = columns
            body = body.dropna(how="all")
            records = [_clean_record(row) for row in body.to_dict(orient="records")]
            records = [record for record in records if any(value is not None for value in record.values())]
            context = self._context_classifier.classify(sheet.sheet_name, [str(column) for column in columns])
            tables.append(
                RawTable(
                    sheet_name=sheet.sheet_name,
                    header_row=sheet.probable_header_row,
                    columns=[str(column) for column in columns],
                    records=records,
                    context=context,
                )
            )
        return tables


# ==============================================================================
# 2. PROFILING / EXTRACCIÓN
# ==============================================================================

@dataclass(frozen=True, slots=True)
class FieldMapping:
    source_column: str
    target_field: str
    confidence: str
    reason: str | None = None

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class NormalizedTable:
    sheet_name: str
    context: str
    header_row: int
    columns: list[str]
    mappings: list[FieldMapping]
    records: list[JsonObject]

    def to_dict(self) -> JsonObject:
        payload = asdict(self)
        payload["mappings"] = [m.to_dict() for m in self.mappings]
        return payload


@dataclass(frozen=True, slots=True)
class CellValidationIssue:
    sheet_name: str
    row_number: int
    column: str
    code: str
    message: str
    value: Any = None

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DocumentCurationReport:
    file_name: str
    status: str
    tables_count: int
    rows_count: int
    mapped_fields: dict[str, str]
    unknown_fields: list[str] = field(default_factory=list)
    ambiguous_fields: list[str] = field(default_factory=list)
    sheet_reports: dict[str, str] = field(default_factory=dict)
    validation_issues: list[CellValidationIssue] = field(default_factory=list)
    column_confirmation_matrix: ColumnConfirmationMatrix | None = None

    def to_dict(self) -> JsonObject:
        payload = asdict(self)
        payload["validation_issues"] = [issue.to_dict() for issue in self.validation_issues]
        if self.column_confirmation_matrix is not None:
            payload["column_confirmation_matrix"] = self.column_confirmation_matrix.model_dump(mode="json")
        return payload


@dataclass(frozen=True, slots=True)
class CuratedDocument:
    file_name: str
    document_type: str
    raw_tables: list[RawTable]
    normalized_tables: list[NormalizedTable]
    report: DocumentCurationReport

    def to_dict(self) -> JsonObject:
        return {
            "file_name": self.file_name,
            "document_type": self.document_type,
            "raw_tables": [table.to_dict() for table in self.raw_tables],
            "normalized_tables": [table.to_dict() for table in self.normalized_tables],
            "report": self.report.to_dict(),
        }


class SemanticFieldMapper:
    """Map document columns to canonical evidence fields with explicit uncertainty."""

    _EXACT_FALLBACKS: dict[str, str] = {
        "venta": "venta_total",
        "ventas": "venta_total",
        "total venta": "venta_total",
        "importe venta": "venta_total",
        "margen": "margen",
        "margen bruto": "margen",
        "resultado": "margen",
        "factura": "factura",
        "comprobante": "factura",
        "nro factura": "factura",
        "canal": "canal",
        "canal venta": "canal",
        "señal_id": "signal_id",
        "senal_id": "signal_id",
        "tipo_señal": "signal_type",
        "tipo_senal": "signal_type",
        "descripción": "description",
        "descripcion": "description",
        "severidad": "severity",
        "acción_sugerida": "suggested_action",
        "accion_sugerida": "suggested_action",
    }

    def __init__(self) -> None:
        self._classifier = ColumnSemanticClassifier()
        self._typed_by_context: dict[str, type[_BaseTypedRow]] = {
            "productos": ProductoRow,
            "ventas": VentaRow,
            "stock": StockRow,
            "caja_banco": CajaBancoRow,
            "senales_operativas": SignalRow,
        }

    def map_columns(self, columns: list[str]) -> list[FieldMapping]:
        mappings: list[FieldMapping] = []
        for column in columns:
            label, is_ambiguous, reason = self._classifier.classify(column)
            normalized = column.lower().strip()
            normalized_key = _normalize_lookup_key(normalized)
            if label == "unknown":
                if normalized in self._EXACT_FALLBACKS:
                    label = self._EXACT_FALLBACKS[normalized]
                    reason = "exact_fallback"
                elif normalized_key in self._EXACT_FALLBACKS:
                    label = self._EXACT_FALLBACKS[normalized_key]
                    reason = "normalized_fallback"

            if label == "unknown":
                confidence = "unknown"
            elif is_ambiguous:
                confidence = "ambiguous"
            else:
                confidence = "mapped"

            mappings.append(
                FieldMapping(
                    source_column=column,
                    target_field=label,
                    confidence=confidence,
                    reason=reason,
                )
            )
        return mappings

    def normalize_record(self, record: JsonObject, mappings: list[FieldMapping], *, context: str) -> JsonObject:
        by_source = {mapping.source_column: mapping for mapping in mappings}
        normalized: JsonObject = {}
        for column, value in record.items():
            mapping = by_source.get(str(column))
            if mapping is None or mapping.target_field == "unknown" or value is None:
                continue
            if mapping.target_field in normalized and normalized[mapping.target_field] is not None:
                continue
            normalized[mapping.target_field] = _coerce_semantic_value(mapping.target_field, value, context=context)
        return normalized

    def normalize_tables(self, raw_tables: list[RawTable]) -> list[NormalizedTable]:
        normalized_tables: list[NormalizedTable] = []
        for table in raw_tables:
            mappings = self.map_columns(table.columns)
            records = [self.normalize_record(record, mappings, context=table.context) for record in table.records]
            records = [record for record in records if record]
            normalized_tables.append(
                NormalizedTable(
                    sheet_name=table.sheet_name,
                    context=table.context,
                    header_row=table.header_row,
                    columns=table.columns,
                    mappings=mappings,
                    records=records,
                )
            )
        return normalized_tables


class DocumentCurator:
    """Build a deterministic curation report from raw and normalized tables."""

    def __init__(self) -> None:
        self._confirmation_builder = ColumnConfirmationBuilder()

    def build_report(self, *, file_name: str, raw_tables: list[RawTable], normalized_tables: list[NormalizedTable]) -> DocumentCurationReport:
        mapped_fields: dict[str, str] = {}
        unknown_fields: set[str] = set()
        ambiguous_fields: set[str] = set()
        sheet_reports: dict[str, str] = {}
        issues: list[CellValidationIssue] = []

        for table in normalized_tables:
            for mapping in table.mappings:
                if mapping.confidence == "unknown":
                    unknown_fields.add(mapping.source_column)
                else:
                    mapped_fields[mapping.source_column] = mapping.target_field
                if mapping.confidence == "ambiguous":
                    ambiguous_fields.add(mapping.source_column)

            table_issue_count = 0
            table_valid_count = 0
            for idx, record in enumerate(table.records, start=table.header_row + 1):
                row_issues = self._validate_normalized_record(
                    table.sheet_name,
                    idx,
                    record,
                    context=table.context,
                )
                table_issue_count += len(row_issues)
                if not row_issues:
                    table_valid_count += 1
                issues.extend(row_issues)

            if table_valid_count > 0 and table_issue_count == 0:
                sheet_reports[table.sheet_name] = "OK"
            elif table_valid_count > 0:
                sheet_reports[table.sheet_name] = "PARTIAL"
            else:
                sheet_reports[table.sheet_name] = "BLOCKED"

        if self._has_exact_duplicate_rows(raw_tables):
            # Exact duplicate business rows are a governed structural signal.
            # Do not deduplicate, do not choose which row to keep, do not assume
            # they are an error: they may be real repeated operations. Surface
            # the ambiguity so any affected calculation requires owner review.
            ambiguous_fields.add(DUPLICATE_ROWS_AMBIGUITY_MARKER)

        if self._has_embedded_total_rows(raw_tables):
            # Exact SUBTOTAL/TOTAL labels mixed with detail rows are a governed
            # granularity ambiguity. Preserve every row and require owner review
            # instead of silently treating aggregate rows as operations.
            ambiguous_fields.add(TOTAL_ROWS_AMBIGUITY_MARKER)

        if self._has_mixed_currency(raw_tables):
            # Multiple explicit currency codes within the same table make monetary
            # aggregation unsafe without a governed conversion contract. Preserve
            # original values and require owner review; never invent an FX rate.
            ambiguous_fields.add(MIXED_CURRENCY_AMBIGUITY_MARKER)

        rows_count = sum(len(table.records) for table in raw_tables)
        status = "CURATED"
        if issues or ambiguous_fields or unknown_fields:
            status = "PARTIAL"
        if not normalized_tables or not any(table.records for table in normalized_tables):
            status = "BLOCKED"

        matrix = self._confirmation_builder.build(
            file_name=file_name,
            normalized_tables=normalized_tables,
            raw_tables=raw_tables,
        )

        return DocumentCurationReport(
            file_name=file_name,
            status=status,
            tables_count=len(raw_tables),
            rows_count=rows_count,
            mapped_fields=mapped_fields,
            unknown_fields=sorted(unknown_fields),
            ambiguous_fields=sorted(ambiguous_fields),
            sheet_reports=sheet_reports,
            validation_issues=issues,
            column_confirmation_matrix=matrix,
        )

    @staticmethod
    def _has_exact_duplicate_rows(raw_tables: list[RawTable]) -> bool:
        for table in raw_tables:
            seen: set[str] = set()
            for record in table.records:
                key = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
                if key in seen:
                    return True
                seen.add(key)
        return False

    @staticmethod
    def _has_embedded_total_rows(raw_tables: list[RawTable]) -> bool:
        aggregate_labels = {"SUBTOTAL", "TOTAL"}
        for table in raw_tables:
            labels = [str(record.get("comprobante") or "").strip().upper() for record in table.records]
            has_aggregate = any(label in aggregate_labels for label in labels)
            has_detail = any(label and label not in aggregate_labels for label in labels)
            if has_aggregate and has_detail:
                return True
        return False

    @staticmethod
    def _has_mixed_currency(raw_tables: list[RawTable]) -> bool:
        for table in raw_tables:
            currencies = {
                str(record.get("moneda") or "").strip().upper()
                for record in table.records
                if record.get("moneda") is not None and str(record.get("moneda")).strip()
            }
            if len(currencies) > 1:
                return True
        return False

    def _validate_normalized_record(self, sheet_name: str, row_number: int, record: JsonObject, *, context: str) -> list[CellValidationIssue]:
        issues: list[CellValidationIssue] = []
        for field_name in ("cantidad", "precio_venta", "costo_unitario", "venta_total", "costo_total", "margen", "stock", "pago", "saldo"):
            if field_name in record and record[field_name] is not None and _to_float(record[field_name]) is None:
                issues.append(
                    CellValidationIssue(
                        sheet_name=sheet_name,
                        row_number=row_number,
                        column=field_name,
                        code="invalid_number",
                        message=f'El campo "{field_name}" no puede convertirse a numero.',
                        value=record[field_name],
                    )
                )

        typed_model = {
            "productos": ProductoRow,
            "ventas": VentaRow,
            "stock": StockRow,
            "caja_banco": CajaBancoRow,
            "senales_operativas": SignalRow,
        }.get(context)
        if typed_model is not None:
            try:
                typed_model.model_validate(record)
            except ValidationError as exc:
                for err in exc.errors():
                    loc = ".".join(str(p) for p in err.get("loc", [])) or "record"
                    issues.append(
                        CellValidationIssue(
                            sheet_name=sheet_name,
                            row_number=row_number,
                            column=loc,
                            code="typed_validation_error",
                            message=str(err.get("msg", "invalid value")),
                            value=record.get(loc),
                        )
                    )
        return issues


class ColumnConfirmationBuilder:
    """Build a column confirmation matrix from curated tables."""

    _NEGATIVE_TOKEN_PATTERNS: dict[str, set[str]] = {
        "pago": {"metodo", "forma", "tipo", "modalidad", "medio"},
        "precio": {"lista", "referencia", "sugerido", "mayorista"},
        "costo": {"lista", "referencia"},
        "venta": {"canal", "tipo", "forma", "metodo"},
    }

    _SPECIFIC_PROMPTS: dict[str, str] = {
        "preciounitario": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es el precio cobrado al cliente? ¿Antes o después de descuento?",
        "precio": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es precio de lista, precio de venta real, costo o referencia?",
        "metodopago": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica forma de pago (efectivo/tarjeta/transferencia) o contiene un importe?",
        "formadepago": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica forma de pago (efectivo/tarjeta/transferencia) o contiene un importe?",
        "modalidaddepago": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica forma de pago o contiene un importe?",
        "mediodepago": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica forma de pago o contiene un importe?",
        "tipodepago": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica forma de pago o contiene un importe?",
        "canalventa": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica el canal comercial de la venta?",
        "canal": "En la hoja \"{sheet}\", ¿la columna \"{col}\" indica el canal comercial o contiene datos adicionales?",
        "sucursalid": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es identificador de sucursal o contiene datos numéricos?",
        "ventaID": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es identificador de venta o contiene un importe?",
        "hora": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es hora de la venta, de entrega, de pago o de registro?",
        "empleado": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es nombre/ID del vendedor o contiene comisiones?",
        "categoria": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es categoría de producto, de cliente o de venta?",
        "ciudad": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es ciudad del cliente, de la sucursal o de entrega?",
        "sucursal": "En la hoja \"{sheet}\", ¿la columna \"{col}\" es nombre de sucursal o contiene datos adicionales?",
    }

    def build(
        self,
        *,
        file_name: str,
        normalized_tables: list[NormalizedTable],
        raw_tables: list[RawTable],
    ) -> ColumnConfirmationMatrix:
        entries: list[ColumnConfirmationEntry] = []
        raw_by_sheet = {t.sheet_name: t for t in raw_tables}

        for table in normalized_tables:
            raw = raw_by_sheet.get(table.sheet_name)
            sample_by_column: dict[str, list[Any]] = {}
            if raw is not None and raw.records:
                for column in table.columns:
                    values: list[Any] = []
                    for record in raw.records[:5]:
                        v = record.get(column)
                        if v is not None:
                            values.append(v)
                    sample_by_column[column] = values

            for mapping in table.mappings:
                column = mapping.source_column
                suggested_role = mapping.target_field
                confidence = mapping.confidence
                relevance = infer_calculation_relevance(suggested_role)
                inferred_type = self._infer_type_from_samples(sample_by_column.get(column, []))
                suggested_data_type = self._suggest_data_type(suggested_role, inferred_type)

                is_ambiguous = confidence == "ambiguous"
                is_unknown = confidence == "unknown"
                has_negative_pattern = self._matches_negative_pattern(column, suggested_role)

                if has_negative_pattern:
                    suggested_role = "unknown"
                    relevance = CalculationRelevance.INFORMATIONAL
                    is_unknown = True
                    confidence = "unknown"

                if is_ambiguous and relevance != CalculationRelevance.INFORMATIONAL:
                    status = ConfirmationStatus.BLOCKED_AMBIGUOUS
                elif is_unknown and relevance != CalculationRelevance.INFORMATIONAL:
                    status = ConfirmationStatus.PENDING_OWNER_CONFIRMATION
                elif is_unknown or is_ambiguous:
                    status = ConfirmationStatus.PENDING_OWNER_CONFIRMATION
                else:
                    status = ConfirmationStatus.PENDING_OWNER_CONFIRMATION

                owner_question = self._build_question(
                    sheet_name=table.sheet_name,
                    column=column,
                    suggested_role=suggested_role,
                    relevance=relevance,
                    status=status,
                )

                entries.append(
                    ColumnConfirmationEntry(
                        original_column_name=column,
                        sheet_name=table.sheet_name,
                        sample_values=sample_by_column.get(column, [])[:5],
                        inferred_type=inferred_type,
                        suggested_semantic_role=suggested_role,
                        suggested_data_type=suggested_data_type,
                        calculation_relevance=relevance,
                        confidence=confidence,
                        owner_question=owner_question,
                        owner_confirmed_role=None,
                        confirmation_status=status,
                    )
                )

        return ColumnConfirmationMatrix(file_name=file_name, entries=entries)

    def _matches_negative_pattern(self, column_name: str, suggested_role: str) -> bool:
        normalized = column_name.lower().replace(" ", "").replace("_", "").replace("-", "")
        negative_tokens = self._NEGATIVE_TOKEN_PATTERNS.get(suggested_role, set())
        if not negative_tokens:
            return False
        return any(token in normalized for token in negative_tokens)

    def _infer_type_from_samples(self, samples: list[Any]) -> str:
        if not samples:
            return "empty"
        numeric_count = 0
        date_count = 0
        text_count = 0
        for v in samples:
            if v is None:
                continue
            if isinstance(v, bool):
                text_count += 1
            elif isinstance(v, (int, float)):
                numeric_count += 1
            elif isinstance(v, str):
                if _to_float(v) is not None:
                    numeric_count += 1
                elif _to_date(v) is not None:
                    date_count += 1
                else:
                    text_count += 1
            else:
                text_count += 1
        total = numeric_count + date_count + text_count
        if total == 0:
            return "empty"
        if numeric_count / total >= 0.6:
            return "number"
        if date_count / total >= 0.6:
            return "date"
        if text_count / total >= 0.6:
            return "text"
        return "mixed"

    def _suggest_data_type(self, semantic_role: str, inferred_type: str) -> str:
        if inferred_type in {"number", "date", "text"}:
            return inferred_type
        if semantic_role in {"cantidad", "stock", "stock_final"}:
            return "int"
        if semantic_role in {
            "precio_venta",
            "costo_unitario",
            "venta_total",
            "costo_total",
            "margen",
            "pago",
            "cobro",
            "saldo",
            "gasto",
        }:
            return "float"
        if semantic_role == "fecha":
            return "date"
        return "text"

    def _build_question(
        self,
        *,
        sheet_name: str,
        column: str,
        suggested_role: str,
        relevance: CalculationRelevance,
        status: ConfirmationStatus,
    ) -> str:
        normalized = column.lower().replace(" ", "").replace("_", "").replace("-", "")
        for key, prompt in self._SPECIFIC_PROMPTS.items():
            if key in normalized:
                return prompt.format(sheet=sheet_name, col=column)

        if relevance == CalculationRelevance.VENTAS:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" representa un monto de venta o una cantidad?"
        if relevance == CalculationRelevance.COSTOS:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" representa un costo unitario o un costo total?"
        if relevance == CalculationRelevance.MARGEN:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" es margen bruto en pesos o porcentaje?"
        if relevance == CalculationRelevance.STOCK:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" es cantidad de unidades en stock?"
        if relevance == CalculationRelevance.PAGOS:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" es un pago/cobro en dinero o un método de pago?"
        if relevance == CalculationRelevance.CANTIDADES:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" representa unidades vendidas, compradas o producidas?"
        if relevance == CalculationRelevance.SEGMENTATION:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" se usa para agrupar/segmentar datos (ej: canal, sucursal) o contiene valores calculables?"
        if relevance == CalculationRelevance.INFORMATIONAL:
            return f"En la hoja \"{sheet_name}\", ¿la columna \"{column}\" sólo describe información (ej: nombre, ID, categoría) o se usa para algún cálculo?"

        return f"En la hoja \"{sheet_name}\", ¿qué significa la columna \"{column}\"? ¿Se usa para calcular ventas, costos, margen, stock, pagos o sólo describe información?"


# ==============================================================================
# 3. OUTPUT ESTRUCTURADO
# ==============================================================================

class StructuredEvidenceExporter:
    """Convert curated local tables into PymIA StructuredEvidence."""

    def export(self, *, curated: CuratedDocument, tenant_id: str, source: str = "xlsx_upload") -> StructuredEvidence:
        evidence_tables = [
            EvidenceTable(
                sheet_name=table.sheet_name,
                columns=table.columns,
                rows=[[record.get(column) for column in table.columns] for record in table.records],
            )
            for table in curated.raw_tables
        ]
        semantic_rows = []
        for table in curated.normalized_tables:
            if table.context == "senales_operativas":
                continue
            for idx, record in enumerate(table.records, start=table.header_row + 1):
                enriched = dict(record)
                enriched["document_ref"] = f"{table.sheet_name}:row:{idx}"
                semantic_rows.append(enriched)

        matrix = curated.report.column_confirmation_matrix
        confirmed_roles: set[str] = set()
        if matrix is not None:
            confirmed_roles = {
                entry.suggested_semantic_role
                for entry in matrix.confirmed_entries()
            }

        computed_variables, evidence_warnings = self._compute_variables(
            semantic_rows,
            column_confirmation_matrix=matrix,
        )
        signals = [
            dict(record)
            for table in curated.normalized_tables
            if table.context == "senales_operativas"
            for record in table.records
        ]

        owner_questions: list[dict[str, str]] = []
        calculation_blocked = False
        if matrix is not None:
            owner_questions = matrix.owner_questions()
            calculation_blocked = bool(matrix.actionable_for_calculation())

        metadata: dict[str, Any] = {
            "curation_status": curated.report.status,
            "extraction_engine": "local_excel_evidence_v1",
            "tables_count": curated.report.tables_count,
            "rows_count": curated.report.rows_count,
            "semantic_rows_count": sum(len(table.records) for table in curated.normalized_tables),
            "field_map": curated.report.mapped_fields,
            "fields_unknown": curated.report.unknown_fields,
            "fields_ambiguous": curated.report.ambiguous_fields,
            "sheet_reports": curated.report.sheet_reports,
            "validation_issues_count": len(curated.report.validation_issues),
            "owner_questions_required": bool(curated.report.unknown_fields or curated.report.ambiguous_fields),
            "evidence_warnings": evidence_warnings,
            "signals": signals,
            "column_confirmation_matrix": matrix.model_dump(mode="json") if matrix is not None else None,
            "owner_questions": owner_questions,
            "calculation_blocked": calculation_blocked,
            "confirmed_roles": sorted(confirmed_roles),
        }

        return StructuredEvidence(
            tenant_id=tenant_id,
            document_type=curated.document_type,
            source=source,
            file_name=curated.file_name,
            tables=evidence_tables,
            computed_variables=computed_variables,
            metadata=metadata,
        )

    def _compute_variables(
        self,
        rows: list[JsonObject],
        *,
        column_confirmation_matrix: ColumnConfirmationMatrix | None = None,
    ) -> tuple[dict[str, float], list[JsonObject]]:
        ventas_total = 0.0
        costos_total = 0.0
        margen_total = 0.0
        cantidad_total = 0.0
        has_quantity = False
        has_sales = False
        has_costs = False
        has_margin = False
        evidence_warnings: list[JsonObject] = []

        can_compute = {
            "ventas_total": True,
            "costos_total": True,
            "cantidad_total": True,
            "margen_bruto": True,
            "margen_bruto_pct": True,
        }
        if column_confirmation_matrix is not None:
            for var_name in can_compute:
                can_compute[var_name] = column_confirmation_matrix.can_compute_variable(var_name)

            for var_name, allowed in can_compute.items():
                if not allowed:
                    pending_cols = [
                        e.original_column_name
                        for e in column_confirmation_matrix.actionable_for_calculation()
                        if e.suggested_semantic_role in _get_required_labels(var_name)
                    ]
                    evidence_warnings.append({
                        "warning_id": f"{var_name}:COLUMN_CONFIRMATION_PENDING",
                        "severity": "BLOCKING",
                        "source_field": var_name,
                        "reason_code": "COLUMN_CONFIRMATION_PENDING",
                        "owner_message": f"No puedo calcular {var_name} hasta que confirmes las columnas: {', '.join(pending_cols[:3])}",
                        "operator_detail": f"variable={var_name}; pending_columns={pending_cols}",
                        "blocks_calculation": True,
                        "suggested_next_evidence": "Confirmar el significado de las columnas pendientes.",
                    })

        for row in rows:
            normalized_row = self._normalize_compute_row(row)
            evidence_warnings.extend(normalized_row["evidence_warnings"])
            values = normalized_row["values"]

            cantidad = values.get("cantidad")
            venta_total = values.get("venta_total")
            precio_venta = values.get("precio_venta")
            costo_unitario = values.get("costo_unitario")
            margen = values.get("margen")

            if cantidad is not None and can_compute["cantidad_total"]:
                cantidad_total += cantidad
                has_quantity = True
            if venta_total is None and precio_venta is not None and cantidad is not None:
                venta_total = precio_venta * cantidad
            if venta_total is not None and can_compute["ventas_total"]:
                ventas_total += venta_total
                has_sales = True
            if costo_unitario is not None and cantidad is not None and can_compute["costos_total"]:
                costos_total += costo_unitario * cantidad
                has_costs = True
            if margen is not None and can_compute["margen_bruto"]:
                margen_total += margen
                has_margin = True

        computed: dict[str, float] = {}
        if has_sales and can_compute["ventas_total"]:
            computed["ventas_total"] = round(ventas_total, 2)
        if has_costs and can_compute["costos_total"]:
            computed["costos_total"] = round(costos_total, 2)
        if has_quantity and can_compute["cantidad_total"]:
            computed["cantidad_total"] = round(cantidad_total, 2)
        if has_margin and can_compute["margen_bruto"]:
            computed["margen_bruto"] = round(margen_total, 2)
        elif has_sales and has_costs and can_compute["margen_bruto"]:
            computed["margen_bruto"] = round(ventas_total - costos_total, 2)
        if "margen_bruto" in computed and has_sales and ventas_total and can_compute["margen_bruto_pct"]:
            computed["margen_bruto_pct"] = round(computed["margen_bruto"] / ventas_total, 4)
        return computed, evidence_warnings

    def _normalize_compute_row(self, row: JsonObject) -> JsonObject:
        values: dict[str, float] = {}
        evidence_warnings: list[JsonObject] = []

        for field_name in ("cantidad", "venta_total", "precio_venta", "costo_unitario", "margen"):
            if field_name not in row:
                continue

            normalized = normalize_evidence_value(
                raw_value=self._value_for_compute_normalizer(row.get(field_name)),
                field_name=field_name,
                expected_type="number",
                required=False,
            )
            evidence_warnings.extend(self._dump_evidence_warning(warning) for warning in normalized.warnings)
            if normalized.allows_calculation and normalized.normalized_value is not None:
                values[field_name] = float(normalized.normalized_value)

        return {
            "values": values,
            "evidence_warnings": evidence_warnings,
        }

    def _value_for_compute_normalizer(self, raw_value: Any) -> Any:
        if isinstance(raw_value, str):
            text = raw_value.strip().lower()
            if text in {"nan", "none", "null", "-"}:
                return None
            parsed = _to_float(raw_value)
            return parsed if parsed is not None else raw_value
        if isinstance(raw_value, bool):
            return raw_value
        if isinstance(raw_value, int | float) and pd.isna(raw_value):
            return None
        return raw_value

    def _dump_evidence_warning(self, warning: Any) -> JsonObject:
        return {
            "warning_id": warning.warning_id,
            "severity": warning.severity,
            "source_field": warning.source_field,
            "reason_code": warning.reason_code,
            "owner_message": warning.owner_message,
            "operator_detail": warning.operator_detail,
            "blocks_calculation": warning.blocks_calculation,
            "suggested_next_evidence": warning.suggested_next_evidence,
        }


class XlsxCurationPipeline:
    def __init__(self) -> None:
        self._ingestor = XlsxDocumentIngestor()
        self._mapper = SemanticFieldMapper()
        self._curator = DocumentCurator()

    def curate(self, excel_path: str | Path, document_type: str = "xlsx_operational_evidence") -> CuratedDocument:
        path = Path(excel_path)
        raw_tables = self._ingestor.ingest(path)
        normalized_tables = self._mapper.normalize_tables(raw_tables)
        report = self._curator.build_report(file_name=path.name, raw_tables=raw_tables, normalized_tables=normalized_tables)
        return CuratedDocument(
            file_name=path.name,
            document_type=document_type,
            raw_tables=raw_tables,
            normalized_tables=normalized_tables,
            report=report,
        )


def curate_xlsx_document(excel_path: str | Path, document_type: str = "xlsx_operational_evidence") -> CuratedDocument:
    return XlsxCurationPipeline().curate(excel_path, document_type=document_type)


def build_structured_evidence_from_xlsx(
    *,
    excel_path: str | Path,
    tenant_id: str,
    document_type: str = "xlsx_operational_evidence",
) -> StructuredEvidence:
    curated = curate_xlsx_document(excel_path, document_type=document_type)
    return StructuredEvidenceExporter().export(curated=curated, tenant_id=tenant_id)


def persist_curation_artifacts(
    *,
    curated: CuratedDocument,
    evidence: StructuredEvidence,
    output_dir: str | Path,
    stem: str,
) -> dict[str, str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    raw_path = root / f"{stem}.raw_tables.json"
    normalized_path = root / f"{stem}.normalized_tables.json"
    sheet_report_path = root / f"{stem}.sheet_reports.json"
    evidence_path = root / f"{stem}.structured_evidence.json"

    raw_path.write_text(
        json_dumps([table.to_dict() for table in curated.raw_tables]),
        encoding="utf-8",
    )
    normalized_path.write_text(
        json_dumps([table.to_dict() for table in curated.normalized_tables]),
        encoding="utf-8",
    )
    sheet_report_path.write_text(
        json_dumps(curated.report.sheet_reports),
        encoding="utf-8",
    )
    evidence_path.write_text(
        json_dumps(evidence.model_dump(mode="json")),
        encoding="utf-8",
    )
    return {
        "raw_tables": str(raw_path),
        "normalized_tables": str(normalized_path),
        "sheet_reports": str(sheet_report_path),
        "structured_evidence": str(evidence_path),
    }

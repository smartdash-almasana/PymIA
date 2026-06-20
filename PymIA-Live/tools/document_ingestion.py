"""Glass-box local document ingestion and curation for PymIA.

This module prepares auditable artifacts from raw documents. It separates:
- raw table extraction
- semantic field mapping
- curation reporting
- StructuredEvidence export

It intentionally lives in tools/ and does not diagnose operationally by itself.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, ClassVar
import unicodedata

import pandas as pd
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from pymia.contracts.evidence_v1 import EvidenceTable, StructuredEvidence
from pymia.smartpyme.evidence_value_normalizer import normalize_evidence_value
from tools.bem_schema_builder.excel_profile_builder import ColumnSemanticClassifier, ExcelProfileBuilder


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


@dataclass(frozen=True, slots=True)
class RawTable:
    sheet_name: str
    header_row: int
    columns: list[str]
    records: list[JsonObject]
    context: str = "generic"

    def to_dict(self) -> JsonObject:
        return asdict(self)


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

    def to_dict(self) -> JsonObject:
        payload = asdict(self)
        payload["validation_issues"] = [issue.to_dict() for issue in self.validation_issues]
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

        rows_count = sum(len(table.records) for table in raw_tables)
        status = "CURATED"
        if issues or ambiguous_fields or unknown_fields:
            status = "PARTIAL"
        if not normalized_tables or not any(table.records for table in normalized_tables):
            status = "BLOCKED"

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
        )

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
        computed_variables, evidence_warnings = self._compute_variables(semantic_rows)
        signals = [
            dict(record)
            for table in curated.normalized_tables
            if table.context == "senales_operativas"
            for record in table.records
        ]
        return StructuredEvidence(
            tenant_id=tenant_id,
            document_type=curated.document_type,
            source=source,
            file_name=curated.file_name,
            tables=evidence_tables,
            computed_variables=computed_variables,
            metadata={
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
            },
        )

    def _compute_variables(self, rows: list[JsonObject]) -> tuple[dict[str, float], list[JsonObject]]:
        ventas_total = 0.0
        costos_total = 0.0
        margen_total = 0.0
        cantidad_total = 0.0
        has_quantity = False
        has_sales = False
        has_costs = False
        has_margin = False
        evidence_warnings: list[JsonObject] = []

        for row in rows:
            normalized_row = self._normalize_compute_row(row)
            evidence_warnings.extend(normalized_row["evidence_warnings"])
            values = normalized_row["values"]

            cantidad = values.get("cantidad")
            venta_total = values.get("venta_total")
            precio_venta = values.get("precio_venta")
            costo_unitario = values.get("costo_unitario")
            margen = values.get("margen")

            if cantidad is not None:
                cantidad_total += cantidad
                has_quantity = True
            if venta_total is None and precio_venta is not None and cantidad is not None:
                venta_total = precio_venta * cantidad
            if venta_total is not None:
                ventas_total += venta_total
                has_sales = True
            if costo_unitario is not None and cantidad is not None:
                costos_total += costo_unitario * cantidad
                has_costs = True
            if margen is not None:
                margen_total += margen
                has_margin = True

        computed: dict[str, float] = {}
        if has_sales:
            computed["ventas_total"] = round(ventas_total, 2)
        if has_costs:
            computed["costos_total"] = round(costos_total, 2)
        if has_quantity:
            computed["cantidad_total"] = round(cantidad_total, 2)
        if has_margin:
            computed["margen_bruto"] = round(margen_total, 2)
        elif has_sales and has_costs:
            computed["margen_bruto"] = round(ventas_total - costos_total, 2)
        if "margen_bruto" in computed and has_sales and ventas_total:
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
    t = str(text or "").strip().lower().replace("�", "ñ")
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
        return _to_float(value)
    if field_name in date_fields:
        return _to_date(value)
    if field_name in text_fields:
        text = str(value).strip()
        return text if text else None
    return value


def json_dumps(payload: Any) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)

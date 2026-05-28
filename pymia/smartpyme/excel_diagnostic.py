from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from tools.document_ingestion import RawTable, XlsxDocumentIngestor


@dataclass(frozen=True)
class EvidenceRecord:
    tenant_id: str
    source_file: str
    total_rows: int
    sheets_processed: int


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    count: int
    sheet_name: str | None = None


@dataclass(frozen=True)
class ExcelDiagnosticResult:
    evidence: EvidenceRecord
    findings: list[Finding]
    markdown: str


CONTEXT_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "productos": {
        "product": ("producto", "product", "sku"),
        "cost": ("costo_unitario", "costo_unitario_actual", "costo", "cost"),
    },
    "ventas": {
        "product": ("producto", "product", "sku"),
        "sales": (
            "precio_unitario_vendido",
            "importe_total",
            "ventas",
            "venta",
            "sales",
            "cantidad",
        ),
        "cost": ("costo_unitario", "costo_unitario_actual", "costo_variable", "costo", "cost"),
    },
    "compras": {
        "product": ("producto", "product", "sku"),
        "cost": ("costo_unitario", "cantidad_comprada", "costo", "cost"),
    },
    "resumen_mensual": {
        "sales": ("ventas_brutas", "ventas", "venta"),
        "cost": ("costo_variable", "costos_fijos", "costo", "cost"),
        "margin": ("margen_bruto", "margen"),
    },
}

DEFAULT_ALIASES = {
    "product": ("producto", "product", "sku"),
    "sales": ("ventas", "venta", "sales"),
    "cost": ("costo", "cost", "costo_unitario"),
}


def _resolve_column(columns: Iterable[str], aliases: tuple[str, ...]) -> str | None:
    lowered = {str(c).strip().lower(): str(c) for c in columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _count_empties(table: RawTable, column: str) -> int:
    return sum(1 for record in table.records if _is_empty(record.get(column)))


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _diagnose_sheet(table: RawTable) -> list[Finding]:
    aliases = CONTEXT_ALIASES.get(table.context, DEFAULT_ALIASES)
    product_col = _resolve_column(table.columns, aliases.get("product", ()))
    sales_col = _resolve_column(table.columns, aliases.get("sales", ()))
    cost_col = _resolve_column(table.columns, aliases.get("cost", ()))

    findings: list[Finding] = []
    sheet = table.sheet_name

    if table.context == "productos" and product_col is None:
        findings.append(Finding(code="EMPTY_PRODUCT", severity="high", message="Columna relevante ausente.", count=1, sheet_name=sheet))

    for col_name, code in (
        (product_col, "EMPTY_PRODUCT"),
        (sales_col, "EMPTY_SALES"),
        (cost_col, "EMPTY_COST"),
    ):
        if col_name is None:
            continue
        empties = _count_empties(table, col_name)
        if empties > 0:
            findings.append(
                Finding(
                    code=code,
                    severity="medium",
                    message=f"Celdas vacias detectadas en columna {col_name}.",
                    count=empties,
                    sheet_name=sheet,
                )
            )

    duplicate_rows = len(table.records) - len({tuple(sorted(record.items())) for record in table.records})
    if duplicate_rows > 0:
        findings.append(Finding(code="DUPLICATE_ROWS", severity="medium", message="Filas duplicadas detectadas.", count=duplicate_rows, sheet_name=sheet))

    if product_col is not None and cost_col is not None:
        without_cost = 0
        for record in table.records:
            product = record.get(product_col)
            cost = _as_float(record.get(cost_col))
            if not _is_empty(product) and (cost is None or cost <= 0):
                without_cost += 1
        if without_cost > 0:
            findings.append(
                Finding(
                    code="PRODUCT_WITHOUT_COST",
                    severity="high",
                    message="Productos con costo faltante o no positivo.",
                    count=without_cost,
                    sheet_name=sheet,
                )
            )

    if sales_col is not None and cost_col is not None:
        not_calculable = 0
        low_margin = 0
        for record in table.records:
            sales = _as_float(record.get(sales_col))
            cost = _as_float(record.get(cost_col))
            if sales is None or sales <= 0 or cost is None:
                not_calculable += 1
                continue
            margin = (sales - cost) / sales
            if margin < 0.10:
                low_margin += 1
        if not_calculable > 0:
            findings.append(
                Finding(
                    code="MARGIN_NOT_CALCULABLE",
                    severity="high",
                    message="Margen no calculable por ventas/costos invalidos.",
                    count=not_calculable,
                    sheet_name=sheet,
                )
            )
        if low_margin > 0:
            findings.append(
                Finding(
                    code="LOW_MARGIN",
                    severity="medium",
                    message="Margen bajo (<10%).",
                    count=low_margin,
                    sheet_name=sheet,
                )
            )
    return findings


def _build_markdown(result: ExcelDiagnosticResult) -> str:
    lines = [
        "# SmartPyme Excel Diagnostic Slice",
        "",
        f"- tenant_id: `{result.evidence.tenant_id}`",
        f"- source_file: `{result.evidence.source_file}`",
        f"- total_rows: `{result.evidence.total_rows}`",
        f"- sheets_processed: `{result.evidence.sheets_processed}`",
        "",
        "## Findings",
    ]
    if not result.findings:
        lines.append("- Sin hallazgos.")
    else:
        for finding in result.findings:
            sheet_info = f" [hoja={finding.sheet_name}]" if finding.sheet_name else ""
            lines.append(
                f"- [{finding.severity}] `{finding.code}`{sheet_info} x{finding.count}: {finding.message}"
            )
    return "\n".join(lines) + "\n"


def diagnose_excel(
    *,
    excel_path: str | Path,
    tenant_id: str,
    markdown_output_path: str | Path | None = None,
) -> ExcelDiagnosticResult:
    path = Path(excel_path)
    ingestor = XlsxDocumentIngestor()
    tables = ingestor.ingest(path)
    findings: list[Finding] = []
    total_rows = 0
    for table in tables:
        total_rows += len(table.records)
        findings.extend(_diagnose_sheet(table))

    base = ExcelDiagnosticResult(
        evidence=EvidenceRecord(
            tenant_id=tenant_id,
            source_file=str(path),
            total_rows=total_rows,
            sheets_processed=len(tables),
        ),
        findings=findings,
        markdown="",
    )
    markdown = _build_markdown(base)
    result = ExcelDiagnosticResult(evidence=base.evidence, findings=base.findings, markdown=markdown)

    if markdown_output_path is not None:
        Path(markdown_output_path).write_text(markdown, encoding="utf-8")

    return result

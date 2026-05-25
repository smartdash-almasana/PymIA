from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class EvidenceRecord:
    tenant_id: str
    source_file: str
    total_rows: int


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    count: int


@dataclass(frozen=True)
class ExcelDiagnosticResult:
    evidence: EvidenceRecord
    findings: list[Finding]
    markdown: str


def _resolve_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    lowered = {str(c).strip().lower(): str(c) for c in df.columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def _build_markdown(result: ExcelDiagnosticResult) -> str:
    lines = [
        "# SmartPyme Excel Diagnostic Slice",
        "",
        f"- tenant_id: `{result.evidence.tenant_id}`",
        f"- source_file: `{result.evidence.source_file}`",
        f"- total_rows: `{result.evidence.total_rows}`",
        "",
        "## Findings",
    ]
    if not result.findings:
        lines.append("- Sin hallazgos.")
    else:
        for finding in result.findings:
            lines.append(
                f"- [{finding.severity}] `{finding.code}` x{finding.count}: {finding.message}"
            )
    return "\n".join(lines) + "\n"


def diagnose_excel(
    *,
    excel_path: str | Path,
    tenant_id: str,
    markdown_output_path: str | Path | None = None,
) -> ExcelDiagnosticResult:
    path = Path(excel_path)
    df = pd.read_excel(path)

    product_col = _resolve_column(df, ("producto", "product", "sku"))
    sales_col = _resolve_column(df, ("ventas", "venta", "sales"))
    cost_col = _resolve_column(df, ("costo", "cost", "costo_unitario"))

    findings: list[Finding] = []

    for col_name, code in (
        (product_col, "EMPTY_PRODUCT"),
        (sales_col, "EMPTY_SALES"),
        (cost_col, "EMPTY_COST"),
    ):
        if col_name is None:
            findings.append(Finding(code=code, severity="high", message="Columna relevante ausente.", count=1))
            continue
        empties = int(df[col_name].isna().sum())
        if empties > 0:
            findings.append(
                Finding(
                    code=code,
                    severity="medium",
                    message=f"Celdas vacías detectadas en columna {col_name}.",
                    count=empties,
                )
            )

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows > 0:
        findings.append(Finding(code="DUPLICATE_ROWS", severity="medium", message="Filas duplicadas detectadas.", count=duplicate_rows))

    if product_col is not None and cost_col is not None:
        cost = pd.to_numeric(df[cost_col], errors="coerce")
        without_cost = int((df[product_col].notna() & (cost.isna() | (cost <= 0))).sum())
        if without_cost > 0:
            findings.append(
                Finding(
                    code="PRODUCT_WITHOUT_COST",
                    severity="high",
                    message="Productos con costo faltante o no positivo.",
                    count=without_cost,
                )
            )

    if sales_col is not None and cost_col is not None:
        sales = pd.to_numeric(df[sales_col], errors="coerce")
        cost = pd.to_numeric(df[cost_col], errors="coerce")
        not_calculable = int((sales.isna() | (sales <= 0) | cost.isna()).sum())
        if not_calculable > 0:
            findings.append(
                Finding(
                    code="MARGIN_NOT_CALCULABLE",
                    severity="high",
                    message="Margen no calculable por ventas/costos inválidos.",
                    count=not_calculable,
                )
            )
        valid = sales.notna() & (sales > 0) & cost.notna()
        low_margin = int((((sales - cost) / sales) < 0.10)[valid].sum())
        if low_margin > 0:
            findings.append(
                Finding(
                    code="LOW_MARGIN",
                    severity="medium",
                    message="Margen bajo (<10%).",
                    count=low_margin,
                )
            )

    base = ExcelDiagnosticResult(
        evidence=EvidenceRecord(tenant_id=tenant_id, source_file=str(path), total_rows=int(len(df))),
        findings=findings,
        markdown="",
    )
    markdown = _build_markdown(base)
    result = ExcelDiagnosticResult(evidence=base.evidence, findings=base.findings, markdown=markdown)

    if markdown_output_path is not None:
        Path(markdown_output_path).write_text(markdown, encoding="utf-8")

    return result

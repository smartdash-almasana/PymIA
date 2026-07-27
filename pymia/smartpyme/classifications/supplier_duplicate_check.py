from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from pymia.smartpyme.excel_diagnostic import EvidenceRecord, ExcelDiagnosticResult, Finding


LEGAL_SUFFIX_RE = re.compile(r"\b(s\.?r\.?l\.?|s\.?a\.?|s\.?a\.?s\.?)\b", re.IGNORECASE)


def _resolve_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    lowered = {str(c).strip().lower(): str(c) for c in df.columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def _normalize_name(value: str) -> str:
    collapsed = " ".join(value.strip().split())
    collapsed = LEGAL_SUFFIX_RE.sub(lambda m: m.group(0).replace(".", "").upper(), collapsed)
    collapsed = collapsed.replace(".", "")
    return collapsed.upper()


def _build_markdown(result: ExcelDiagnosticResult, diagnostic_status: str) -> str:
    lines = [
        "# SmartPyme Supplier Duplicate Check",
        "",
        f"- tenant_id: `{result.evidence.tenant_id}`",
        f"- source_file: `{result.evidence.source_file}`",
        f"- total_rows: `{result.evidence.total_rows}`",
        f"- diagnostic_status: `{diagnostic_status}`",
        "",
        "## Findings",
    ]
    if not result.findings:
        lines.append("- Sin hallazgos.")
    else:
        for finding in result.findings:
            lines.append(f"- [{finding.severity}] `{finding.code}` x{finding.count}: {finding.message}")
    return "\n".join(lines) + "\n"


def diagnose_supplier_duplicates(
    *,
    excel_path: str | Path,
    tenant_id: str,
    markdown_output_path: str | Path | None = None,
) -> tuple[ExcelDiagnosticResult, str]:
    path = Path(excel_path)
    df = pd.read_excel(path)

    proveedor_col = _resolve_column(df, ("proveedor", "supplier"))
    cuit_col = _resolve_column(df, ("cuit", "tax_id"))
    razon_col = _resolve_column(df, ("razon_social", "razon social", "social_name"))

    findings: list[Finding] = []

    if proveedor_col is None:
        findings.append(
            Finding(
                code="MISSING_PROVEEDOR_COLUMN",
                severity="high",
                message="Falta columna obligatoria de proveedor.",
                count=1,
            )
        )
        status = "BLOCKED"
    else:
        if cuit_col is not None:
            normalized_cuit = df[cuit_col].astype(str).str.strip()
            normalized_cuit = normalized_cuit.where(df[cuit_col].notna(), "")
            non_empty = normalized_cuit[normalized_cuit != ""]
            duplicate_count = int(non_empty.duplicated(keep=False).sum())
            if duplicate_count > 0:
                findings.append(
                    Finding(
                        code="DUPLICATE_CUIT",
                        severity="high",
                        message="CUIT repetido detectado.",
                        count=duplicate_count,
                    )
                )
            missing_cuit = int((normalized_cuit == "").sum())
            if missing_cuit > 0:
                findings.append(
                    Finding(
                        code="MISSING_CUIT",
                        severity="medium",
                        message="Filas sin CUIT.",
                        count=missing_cuit,
                    )
                )
        else:
            findings.append(
                Finding(
                    code="MISSING_CUIT",
                    severity="medium",
                    message="Columna CUIT ausente; análisis limitado.",
                    count=1,
                )
            )

        if razon_col is not None:
            razon_series = df[razon_col].astype(str).str.strip()
            razon_series = razon_series.where(df[razon_col].notna(), "")
            missing_razon = int((razon_series == "").sum())
            if missing_razon > 0:
                findings.append(
                    Finding(
                        code="MISSING_RAZON_SOCIAL",
                        severity="medium",
                        message="Filas sin razón social.",
                        count=missing_razon,
                    )
                )

            normalization_needed = int(
                df[razon_col]
                .astype(str)
                .fillna("")
                .map(lambda x: ("  " in x) or (x != " ".join(x.strip().split())))
                .sum()
            )
            if normalization_needed > 0:
                findings.append(
                    Finding(
                        code="NORMALIZATION_NEEDED",
                        severity="low",
                        message="Se detectaron espacios/puntuación que requieren normalización.",
                        count=normalization_needed,
                    )
                )

            normalized = {}
            for raw in razon_series:
                if raw:
                    key = _normalize_name(raw)
                    normalized.setdefault(key, set()).add(raw.upper())
            legal_suffix_variation = sum(1 for values in normalized.values() if len(values) > 1)
            if legal_suffix_variation > 0:
                findings.append(
                    Finding(
                        code="LEGAL_SUFFIX_VARIATION",
                        severity="low",
                        message="Variaciones simples de sufijo legal detectadas.",
                        count=legal_suffix_variation,
                    )
                )
        else:
            findings.append(
                Finding(
                    code="MISSING_RAZON_SOCIAL",
                    severity="medium",
                    message="Columna razón social ausente; análisis limitado.",
                    count=1,
                )
            )

        has_minimum = proveedor_col is not None and (cuit_col is not None or razon_col is not None)
        status = "PASS" if has_minimum else "PARTIAL"

    base = ExcelDiagnosticResult(
        evidence=EvidenceRecord(
            tenant_id=tenant_id,
            source_file=str(path),
            total_rows=int(len(df)),
            sheets_processed=1,
        ),
        findings=findings,
        markdown="",
    )
    markdown = _build_markdown(base, status)
    result = ExcelDiagnosticResult(evidence=base.evidence, findings=base.findings, markdown=markdown)

    if markdown_output_path is not None:
        Path(markdown_output_path).write_text(markdown, encoding="utf-8")

    return result, status


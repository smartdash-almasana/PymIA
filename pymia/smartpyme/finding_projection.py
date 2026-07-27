"""Projection from MicroserviceExecutionResult to actionable findings.

Pure deterministic transformation. No LLM, no writes, no network.
This module consumes execution results as dicts (or objects with to_dict())
and produces a list of ActionableFinding without importing excel_diagnostic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


EXECUTION_EXECUTED = "EXECUTED"

GENERIC_METRIC = "desconocido"
GENERIC_RECOMMENDATION = "Revisar manualmente el hallazgo detectado."

_METRIC_MAP: dict[str, str] = {
    "EMPTY_PRODUCT": "producto",
    "EMPTY_SALES": "ventas",
    "EMPTY_COST": "costo",
    "DUPLICATE_ROWS": "filas",
    "PRODUCT_WITHOUT_COST": "costo",
    "MARGIN_NOT_CALCULABLE": "margen",
    "LOW_MARGIN": "margen",
}

_DIFFERENCE_TEMPLATES: dict[str, str] = {
    "EMPTY_PRODUCT": "{count} filas sin producto en {sheet_name}",
    "EMPTY_SALES": "{count} celdas vacias en columna ventas en {sheet_name}",
    "EMPTY_COST": "{count} celdas vacias en columna costo en {sheet_name}",
    "DUPLICATE_ROWS": "{count} filas duplicadas en {sheet_name}",
    "PRODUCT_WITHOUT_COST": "{count} productos sin costo valido en {sheet_name}",
    "MARGIN_NOT_CALCULABLE": "{count} productos con margen no calculable en {sheet_name}",
    "LOW_MARGIN": "{count} productos con margen bajo (<10%) en {sheet_name}",
}

_RECOMMENDATION_TEMPLATES: dict[str, str] = {
    "EMPTY_PRODUCT": "Completar nombres de producto en hoja {sheet_name}.",
    "EMPTY_SALES": "Revisar registros de ventas incompletos en hoja {sheet_name}.",
    "EMPTY_COST": "Completar costos faltantes en hoja {sheet_name}.",
    "DUPLICATE_ROWS": "Eliminar filas duplicadas para evitar doble conteo en hoja {sheet_name}.",
    "PRODUCT_WITHOUT_COST": "Asignar costo unitario positivo a productos afectados en hoja {sheet_name}.",
    "MARGIN_NOT_CALCULABLE": "Corregir ventas/costos invalidos para calcular margen en hoja {sheet_name}.",
    "LOW_MARGIN": "Revisar estructura de precios y costos de productos afectados en hoja {sheet_name}.",
}

_ENTITY_TEMPLATES: dict[str, str] = {
    "EMPTY_PRODUCT": "Hoja {sheet_name}",
    "EMPTY_SALES": "Columna ventas en {sheet_name}",
    "EMPTY_COST": "Columna costo en {sheet_name}",
    "DUPLICATE_ROWS": "Filas de {sheet_name}",
    "PRODUCT_WITHOUT_COST": "Productos en {sheet_name}",
    "MARGIN_NOT_CALCULABLE": "Productos en {sheet_name}",
    "LOW_MARGIN": "Productos en {sheet_name}",
}


@dataclass(frozen=True)
class ActionableFinding:
    """Minimal actionable finding produced from a microservice execution result.

    Deterministic. JSON-safe. No LLM, no network, no writes.
    """

    entity: str
    metric: str
    difference: str
    source_comparison: str
    severity: str
    evidence_refs: list[str] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "entity": str(self.entity),
            "metric": str(self.metric),
            "difference": str(self.difference),
            "source_comparison": str(self.source_comparison),
            "severity": str(self.severity),
            "evidence_refs": [str(r) for r in self.evidence_refs],
            "recommendation": str(self.recommendation),
        }


def _execution_to_dict(execution_result: Any) -> dict:
    if isinstance(execution_result, dict):
        return dict(execution_result)
    if hasattr(execution_result, "to_dict") and callable(execution_result.to_dict):
        data = execution_result.to_dict()
        if not isinstance(data, dict):
            raise ValueError("execution_result.to_dict() must return dict")
        return dict(data)
    raise ValueError(
        "execution_result must be a dict or expose to_dict()"
    )


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _safe_count(value: Any) -> int:
    try:
        n = int(value)
    except Exception:
        return 0
    return max(0, n)


def _build_source_comparison(raw_result: dict) -> str:
    evidence = raw_result.get("evidence") if isinstance(raw_result, dict) else None
    if isinstance(evidence, dict):
        source = _as_str(evidence.get("source_file")).strip()
        if source:
            return source
    return ""


def _project_one_finding(
    finding_dict: dict,
    evidence_refs: list[str],
    source_comparison: str,
) -> ActionableFinding:
    code = _as_str(finding_dict.get("code")).strip()
    severity = _as_str(finding_dict.get("severity")).strip() or "medium"
    count = _safe_count(finding_dict.get("count"))
    sheet_name = _as_str(finding_dict.get("sheet_name")).strip() or "hoja desconocida"

    if not code:
        code = "UNKNOWN"

    ctx = {"count": count, "sheet_name": sheet_name}

    metric = _METRIC_MAP.get(code, GENERIC_METRIC)
    difference_template = _DIFFERENCE_TEMPLATES.get(code)
    recommendation_template = _RECOMMENDATION_TEMPLATES.get(code)
    entity_template = _ENTITY_TEMPLATES.get(code)

    if difference_template is None:
        difference = _as_str(finding_dict.get("message")).strip() or (
            f"Hallazgo detectado ({code}) con count={count} en {sheet_name}"
        )
    else:
        try:
            difference = difference_template.format(**ctx)
        except Exception:
            difference = f"{count} ocurrencias de {code} en {sheet_name}"

    if recommendation_template is None:
        recommendation = GENERIC_RECOMMENDATION
    else:
        try:
            recommendation = recommendation_template.format(**ctx)
        except Exception:
            recommendation = GENERIC_RECOMMENDATION

    if entity_template is None:
        entity = sheet_name
    else:
        try:
            entity = entity_template.format(**ctx)
        except Exception:
            entity = sheet_name

    return ActionableFinding(
        entity=entity,
        metric=metric,
        difference=difference,
        source_comparison=source_comparison,
        severity=severity,
        evidence_refs=list(evidence_refs),
        recommendation=recommendation,
    )


def project_actionable_findings(execution_result: Any) -> list[ActionableFinding]:
    """Project a microservice execution result to a list of actionable findings.

    Fail-closed contract:
    - Returns [] if status is not EXECUTED.
    - Returns [] if findings_count is zero or negative.
    - Returns [] if raw_result is missing or has no valid findings list.
    - Propagates output_refs to evidence_refs of every finding.
    - Returns a generic finding if an unknown code is encountered.

    No LLM, no writes, no network.
    """
    try:
        data = _execution_to_dict(execution_result)
    except ValueError:
        return []

    status = _as_str(data.get("status")).strip()
    if status != EXECUTION_EXECUTED:
        return []

    findings_count = _safe_count(data.get("findings_count"))
    if findings_count <= 0:
        return []

    raw_result = data.get("raw_result")
    if not isinstance(raw_result, dict):
        return []

    raw_findings = raw_result.get("findings")
    if not isinstance(raw_findings, list) or len(raw_findings) == 0:
        return []

    output_refs = data.get("output_refs")
    evidence_refs: list[str] = []
    if isinstance(output_refs, list):
        evidence_refs = [str(r) for r in output_refs if str(r).strip()]

    source_comparison = _build_source_comparison(raw_result)

    projected: list[ActionableFinding] = []
    for raw_finding in raw_findings:
        if not isinstance(raw_finding, dict):
            continue
        projected.append(
            _project_one_finding(raw_finding, evidence_refs, source_comparison)
        )

    return projected


__all__ = [
    "ActionableFinding",
    "project_actionable_findings",
    "EXECUTION_EXECUTED",
    "GENERIC_METRIC",
    "GENERIC_RECOMMENDATION",
]

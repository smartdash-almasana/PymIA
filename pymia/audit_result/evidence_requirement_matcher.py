from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pymia.contracts.evidence_v1 import StructuredEvidence


@dataclass
class EvidenceRequirementMatch:
    pathology_code: str
    pathology_name: str
    formula_id: str
    status: str
    available_evidence: list[str]
    missing_evidence: list[str]
    matched_sources: list[str]
    required_evidence: list[str]
    required_variables: list[str]
    next_audit_questions: list[dict[str, Any]]


_SIGNAL_TO_PATHOLOGY = {
    "margen_bajo": "REN_001",
    "margen_negativo": "REN_001",
    "precio_desactualizado": "REN_001",
    "caja_tensionada": "LIQ_001",
    "sobrestock": "INV_002",
    "stock_bajo": "INV_001",
}


def _docs_root() -> Path:
    return Path(__file__).resolve().parents[2] / "docs"


def _load_catalog_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sheet_status(evidence: StructuredEvidence) -> dict[str, str]:
    md = evidence.metadata if isinstance(evidence.metadata, dict) else {}
    sr = md.get("sheet_reports", {})
    return sr if isinstance(sr, dict) else {}


def _signals(evidence: StructuredEvidence) -> list[dict[str, Any]]:
    md = evidence.metadata if isinstance(evidence.metadata, dict) else {}
    raw = md.get("signals", [])
    return [s for s in raw if isinstance(s, dict)] if isinstance(raw, list) else []


def _compute_key_aliases(evidence: StructuredEvidence) -> tuple[set[str], dict[str, list[str]]]:
    available: set[str] = set()
    sources: dict[str, list[str]] = {}

    def add(key: str, source: str) -> None:
        if key not in sources:
            sources[key] = []
        if source not in sources[key]:
            sources[key].append(source)
        available.add(key)

    sheets = _sheet_status(evidence)
    computed = evidence.computed_variables or {}

    for name, status in sheets.items():
        sheet_key = f"sheet:{name}"
        add(sheet_key, sheet_key)
        if str(status).upper() == "OK":
            add(name.lower(), sheet_key)

    for key in computed:
        csrc = f"computed:{key}"
        add(key, csrc)

    # Evidence aliases for formula catalog required_evidence
    if "ventas_total" in computed or "ventas" in sheets:
        add("ventas_del_periodo", "sheet:ventas")
        add("sales", "sheet:ventas")
        add("ventas_totales", "sheet:ventas")
        add("ventas_por_sku", "sheet:ventas")

    if "costos_total" in computed or "compras" in sheets:
        add("costos_directos", "sheet:compras")
        add("costs", "sheet:compras")
        add("cmv_periodo", "sheet:compras")

    if "stock" in sheets:
        add("inventario_inicial", "sheet:stock")
        add("inventario_final", "sheet:stock")
        add("average_stock", "sheet:stock")

    if "caja_banco" in sheets:
        add("cobranzas_del_periodo", "sheet:caja_banco")
        add("cuentas_corrientes_clientes", "sheet:caja_banco")
        add("collected_amount", "sheet:caja_banco")

    if "costos_fijos" in sheets:
        add("impuestos_y_comisiones", "sheet:costos_fijos")
        add("taxes", "sheet:costos_fijos")

    # Variable aliases from computed variables
    if "ventas_total" in computed:
        add("sold_amount", "computed:ventas_total")
        add("sale_price", "computed:ventas_total")
    if "costos_total" in computed:
        add("costs", "computed:costos_total")
        add("cost_of_goods_sold", "computed:costos_total")

    for sig in _signals(evidence):
        sid = str(sig.get("signal_id") or "unknown")
        stype = str(sig.get("signal_type") or "").strip().lower()
        if stype:
            add(f"signal_type:{stype}", f"signal:{sid}")

    return available, sources


def _status_for_formula(
    *,
    pathology_code: str,
    required_evidence: list[str],
    required_variables: list[str],
    available_keys: set[str],
    sheet_reports: dict[str, str],
    signal_pathology_codes: set[str],
) -> str:
    ev_present = [e for e in required_evidence if e in available_keys]
    var_present = [v for v in required_variables if v in available_keys]

    blocked_sheet = any(str(v).upper() == "BLOCKED" for v in sheet_reports.values())
    if blocked_sheet and (ev_present or var_present):
        return "blocked"

    full_evidence = len(ev_present) == len(required_evidence)
    full_vars = len(var_present) == len(required_variables)

    if full_evidence and full_vars:
        return "calculable"

    if ev_present or var_present:
        return "pending_data"

    if pathology_code in signal_pathology_codes:
        return "candidate"

    return "not_applicable"


def match_evidence_requirements(
    evidence: StructuredEvidence,
    *,
    formula_catalog_path: Path | None = None,
    pathology_catalog_path: Path | None = None,
) -> list[EvidenceRequirementMatch]:
    docs = _docs_root()
    formula_data = _load_catalog_json(formula_catalog_path or (docs / "formula_catalog.v1.json"))
    pathology_data = _load_catalog_json(pathology_catalog_path or (docs / "pathology_catalog.v1.json"))

    pathology_by_code = {
        p["pathology_code"]: p for p in pathology_data.get("pathologies", []) if isinstance(p, dict) and p.get("pathology_code")
    }

    available_keys, source_map = _compute_key_aliases(evidence)
    sheet_reports = _sheet_status(evidence)

    sig_pathologies: set[str] = set()
    for sig in _signals(evidence):
        stype = str(sig.get("signal_type") or "").strip().lower()
        code = _SIGNAL_TO_PATHOLOGY.get(stype)
        if code:
            sig_pathologies.add(code)

    matches: list[EvidenceRequirementMatch] = []
    for formula in formula_data.get("formulas", []):
        if not isinstance(formula, dict):
            continue
        pathology_code = str(formula.get("pathology_code") or "")
        if pathology_code not in pathology_by_code:
            continue

        required_evidence = [str(x) for x in formula.get("required_evidence", []) if isinstance(x, str)]
        required_variables = [str(x) for x in formula.get("required_variables", []) if isinstance(x, str)]

        available_evidence = [e for e in required_evidence if e in available_keys]
        missing_evidence = [e for e in required_evidence if e not in available_keys]
        matched_sources: list[str] = []
        for key in available_evidence + [v for v in required_variables if v in available_keys]:
            matched_sources.extend(source_map.get(key, []))
        matched_sources = sorted(set(matched_sources))

        status = _status_for_formula(
            pathology_code=pathology_code,
            required_evidence=required_evidence,
            required_variables=required_variables,
            available_keys=available_keys,
            sheet_reports=sheet_reports,
            signal_pathology_codes=sig_pathologies,
        )

        next_q = []
        if status in {"candidate", "pending_data", "blocked"}:
            next_q.append(
                {
                    "question": f"Falta evidencia para evaluar {pathology_code}. ¿Podés compartir {', '.join(missing_evidence[:2])}?",
                    "requires_data": missing_evidence,
                    "priority": "high" if status in {"blocked", "pending_data"} else "medium",
                }
            )

        matches.append(
            EvidenceRequirementMatch(
                pathology_code=pathology_code,
                pathology_name=str(pathology_by_code[pathology_code].get("name") or pathology_code),
                formula_id=str(formula.get("formula_id") or "unknown_formula"),
                status=status,
                available_evidence=available_evidence,
                missing_evidence=missing_evidence,
                matched_sources=matched_sources,
                required_evidence=required_evidence,
                required_variables=required_variables,
                next_audit_questions=next_q,
            )
        )

    return matches

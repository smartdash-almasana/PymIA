from __future__ import annotations

from pymia.contracts.evidence_v1 import StructuredEvidence

from .models import DiagnosticCoreInput

_FORMULA_VARIABLE_ALIASES: dict[str, dict[str, list[str]]] = {
    "REN_001_margen_neto_real": {
        "sale_price": ["sale_price", "ventas_total"],
        "costs": ["costs", "costos_total"],
        "taxes": ["taxes", "impuestos_total"],
    },
    "LIQ_001_vendido_cobrado": {
        "sold_amount": ["sold_amount", "ventas_total"],
        "collected_amount": ["collected_amount", "cobranzas_total"],
    },
    "INV_002_rotacion_stock": {
        "cost_of_goods_sold": ["cost_of_goods_sold", "costos_total"],
        "average_stock": ["average_stock", "stock_promedio"],
    },
    "PYME_044_margen_cliente": {
        "client_revenue": ["client_revenue", "ingresos_cliente"],
        "client_direct_costs": ["client_direct_costs", "costos_directos_cliente"],
        "client_service_costs": ["client_service_costs", "costos_servicio_cliente"],
    },
    "PYME_033_concentracion_sku": {
        "main_sku_sales": ["main_sku_sales", "ventas_sku_principal"],
        "total_sales": ["total_sales", "ventas_total"],
    },
    "REN_002_coeficiente_reposicion": {
        "closing_index": ["closing_index", "indice_cierre"],
        "origin_index": ["origin_index", "indice_origen"],
    },
}


def build_diagnostic_core_input_from_structured_evidence(
    evidence: StructuredEvidence,
    *,
    case_id: str,
    tenant_id: str,
    formula_ids: list[str],
    hypothesis_codes: list[str] | None = None,
) -> DiagnosticCoreInput:
    computed = evidence.computed_variables or {}
    variables: dict[str, float | int | None] = {}
    evidence_refs: dict[str, list[str]] = {}

    for formula_id in formula_ids:
        for target_name, aliases in _FORMULA_VARIABLE_ALIASES.get(formula_id, {}).items():
            value, matched_alias = _pick_first_available(computed, aliases)
            if value is None:
                continue
            variables[target_name] = value
            refs = _source_refs_for(evidence, target_name, matched_alias)
            if refs:
                evidence_refs[target_name] = refs

    return DiagnosticCoreInput(
        case_id=case_id,
        tenant_id=tenant_id,
        hypothesis_codes=hypothesis_codes or [],
        formula_ids=formula_ids,
        variables=variables,
        evidence_refs=evidence_refs,
        evidence_status="STRUCTURED_EVIDENCE_BOUND",
        metadata={
            "binding_source": "StructuredEvidence.computed_variables",
            "document_type": evidence.document_type,
            "file_name": evidence.file_name,
        },
    )


def _pick_first_available(
    computed: dict[str, float],
    aliases: list[str],
) -> tuple[float | int | None, str | None]:
    for alias in aliases:
        if alias in computed and computed[alias] is not None:
            return computed[alias], alias
    return None, None


def _source_refs_for(
    evidence: StructuredEvidence,
    canonical_name: str,
    matched_alias: str | None,
) -> list[str]:
    if not matched_alias:
        return []

    metadata = evidence.metadata or {}
    variable_refs = metadata.get("variable_source_refs")
    if isinstance(variable_refs, dict):
        for key in (canonical_name, matched_alias):
            refs = variable_refs.get(key)
            if isinstance(refs, list):
                return [str(ref) for ref in refs if str(ref).strip()]

    if evidence.file_name:
        return [f"{evidence.file_name}:{matched_alias}"]
    return []

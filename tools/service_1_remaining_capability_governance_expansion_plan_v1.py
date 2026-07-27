from __future__ import annotations

from typing import Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_REMAINING_CAPABILITY_GOVERNANCE_EXPANSION_PLAN_V1"
VERDICT: Final[str] = "AUTHORIZED_BOUNDED_EXPANSION"

PROMOTE_NOW: Final[dict[str, dict[str, object]]] = {
    "reorder_point": {
        "pathology_code": "INV_001",
        "canonical_formula_id": "INV_001_punto_reposicion",
        "required_variables": ["average_sales", "lead_time", "safety_stock"],
        "calculation_state": "CALCULABLE",
    },
    "inventory_turnover": {
        "pathology_code": "INV_002",
        "canonical_formula_id": "INV_002_rotacion_stock",
        "required_variables": ["cost_of_goods_sold", "average_stock"],
        "calculation_state": "CALCULABLE",
    },
    "current_ratio": {
        "pathology_code": "PYME_024",
        "canonical_formula_id": "PYME_024_liquidez_corriente",
        "required_variables": ["current_assets", "current_liabilities"],
        "calculation_state": "CALCULABLE",
    },
    "sales_concentration": {
        "pathology_code": "PYME_033",
        "canonical_formula_id": "PYME_033_concentracion_sku",
        "required_variables": ["main_sku_sales", "total_sales"],
        "calculation_state": "CALCULABLE",
    },
    "interest_burden_ratio": {
        "pathology_code": "PYME_027",
        "canonical_formula_id": "PYME_027_intereses_ebitda",
        "required_variables": ["interest_expense", "ebitda"],
        "calculation_state": "CALCULABLE",
    },
    "index_update_ratio": {
        "pathology_code": "REN_002",
        "canonical_formula_id": "REN_002_coeficiente_reposicion",
        "required_variables": ["closing_index", "origin_index"],
        "calculation_state": "CALCULABLE",
    },
}

DEFERRED: Final[dict[str, dict[str, str]]] = {
    "adjusted_operating_cash_flow": {
        "reason": "FORMULA_CALCULABLE_CON_SUPUESTOS",
        "required_action": "GOVERN_WORKING_CAPITAL_CHANGE_ASSUMPTIONS_BEFORE_COMPUTABLE",
    },
    "dpo": {
        "reason": "NO_CANONICAL_FORMULA_ENTRY_FOR_PREREQUISITE_PATHOLOGY",
        "required_action": "DEFINE_DPO_FORMULA_AND_PATHOLOGY_GOVERNANCE",
    },
    "payment_collection_gap": {
        "reason": "COMPOSITE_DEPENDS_ON_UNGOVERNED_DPO",
        "required_action": "GOVERN_DPO_THEN_CERTIFY_COMPOSITE",
    },
}


def build_service_1_remaining_capability_governance_expansion_plan_v1() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT,
        "promote_now_count": len(PROMOTE_NOW),
        "deferred_count": len(DEFERRED),
        "promote_now": PROMOTE_NOW,
        "deferred": DEFERRED,
        "migration_policy": "ADDITIVE_CREATE_MIGRATE_VERIFY_DELETE",
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "VERDICT",
    "PROMOTE_NOW",
    "DEFERRED",
    "build_service_1_remaining_capability_governance_expansion_plan_v1",
]

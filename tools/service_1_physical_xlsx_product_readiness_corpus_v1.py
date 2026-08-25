from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PHYSICAL_XLSX_PRODUCT_READINESS_CORPUS_V1"
VERDICT_READY: Final[str] = "READY_FOR_PRODUCT_READINESS_NEXT_GATE"
VERDICT_NOT_READY: Final[str] = "NOT_READY"

EXACT_MATCH = "EXACT_MATCH"
SAFE_QUESTION = "SAFE_QUESTION"
SAFE_UNKNOWN = "SAFE_UNKNOWN"
FALSE_CONFIDENT = "FALSE_CONFIDENT"


@dataclass(frozen=True)
class PhysicalCaseSpec:
    case_id: str
    sector: str
    filename: str
    sheet_name: str
    expected_roles: dict[str, str]
    dangerous_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class PhysicalRow:
    case_id: str
    sector: str
    filename: str
    sheet_name: str
    column_name: str
    expected_role: str
    predicted_role: str
    confidence: float
    owner_question_needed: bool
    outcome: str
    dangerous_if_wrong: bool


CASES: Final[tuple[PhysicalCaseSpec, ...]] = (
    PhysicalCaseSpec(
        case_id="S1-PHY-001",
        sector="ventas_margen",
        filename="CASE_001_ventas_junio_2026_margin_leak.xlsx",
        sheet_name="Ventas_Junio_2026",
        expected_roles={
            "fecha": "operation_date",
            "comprobante": "document_reference",
            "producto_codigo": "product_identifier",
            "producto": "product_name",
            "categoria": "commercial_category",
            "cantidad": "quantity",
            "precio_unitario": "unit_sale_price",
            "costo_unitario": "unit_cost_candidate",
            "canal": "sales_channel",
            "venta_total": "sales_amount",
        },
        dangerous_columns=("producto_codigo", "precio_unitario", "costo_unitario", "venta_total"),
    ),
    PhysicalCaseSpec(
        case_id="S1-PHY-002",
        sector="textil_ventas",
        filename="la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        sheet_name="ventas",
        expected_roles={
            "fecha": "operation_date",
            "comprobante": "document_reference",
            "canal": "sales_channel",
            "cliente": "customer_name",
            "sku": "product_identifier",
            "producto": "product_name",
            "cantidad": "quantity",
            "precio_unitario_vendido": "unit_sale_price",
            "descuento_pct": "discount_candidate",
            "medio_cobro": "payment_method",
            "plazo_cobro_dias": "unknown",
            "importe_total": "sales_amount",
        },
        dangerous_columns=("sku", "precio_unitario_vendido", "descuento_pct", "importe_total"),
    ),
    PhysicalCaseSpec(
        case_id="S1-PHY-003",
        sector="textil_compras",
        filename="la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        sheet_name="compras",
        expected_roles={
            "fecha": "operation_date",
            "orden_compra": "document_reference",
            "proveedor": "supplier_name",
            "sku": "product_identifier",
            "producto": "product_name",
            "cantidad_comprada": "quantity",
            "costo_unitario": "unit_cost_candidate",
            "importe_total": "purchase_amount",
            "fecha_pago": "unknown",
            "estado_pago": "unknown",
        },
        dangerous_columns=("orden_compra", "sku", "costo_unitario", "importe_total"),
    ),
    PhysicalCaseSpec(
        case_id="S1-PHY-004",
        sector="textil_stock",
        filename="la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        sheet_name="stock",
        expected_roles={
            "sku": "product_identifier",
            "producto": "product_name",
            "stock_inicial_marzo": "opening_stock",
            "compras_marzo": "stock_inflow",
            "ventas_marzo": "stock_outflow",
            "stock_final_marzo": "closing_stock",
            "compras_abril": "stock_inflow",
            "ventas_abril": "stock_outflow",
            "stock_final_abril": "closing_stock",
            "compras_mayo": "stock_inflow",
            "ventas_mayo": "stock_outflow",
            "stock_final_mayo": "closing_stock",
            "stock_minimo": "stock_minimum",
            "valor_stock_actual": "unknown",
            "estado_stock": "unknown",
        },
        dangerous_columns=(
            "stock_inicial_marzo", "compras_marzo", "ventas_marzo", "stock_final_marzo",
            "compras_abril", "ventas_abril", "stock_final_abril",
            "compras_mayo", "ventas_mayo", "stock_final_mayo", "stock_minimo",
        ),
    ),
    PhysicalCaseSpec(
        case_id="S1-PHY-005",
        sector="cobranzas",
        filename="cobros_marzo_2026.xlsx",
        sheet_name="Cobros_Marzo_2026",
        expected_roles={
            "fecha": "operation_date",
            "cobro_id": "document_reference",
            "medio_de_cobro": "payment_method",
            "referencia": "document_reference",
            "importe_cobrado": "collected_amount",
            "ticket_relacionado": "document_reference",
            "estado_match_declarado": "unknown",
            "observaciones": "unknown",
        },
        dangerous_columns=("cobro_id", "importe_cobrado", "ticket_relacionado"),
    ),
    PhysicalCaseSpec(
        case_id="S1-PHY-006",
        sector="taller_stock",
        filename="taller_mecanico_lubricar_srl.xlsx",
        sheet_name="PRODUCTOS_STOCK",
        expected_roles={
            "codigo": "product_identifier",
            "producto": "product_name",
            "categoria": "commercial_category",
            "unidad": "unknown",
            "costo_unitario": "unit_cost_candidate",
            "precio_venta": "unit_sale_price",
            "stock_actual": "stock_current",
            "stock_minimo": "stock_minimum",
        },
        dangerous_columns=("codigo", "costo_unitario", "precio_venta", "stock_actual", "stock_minimo"),
    ),
    PhysicalCaseSpec(
        case_id="S1-PHY-007",
        sector="caja_banco_control",
        filename="first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx",
        sheet_name="Caja_Banco",
        expected_roles={
            "ID movimiento": "document_reference",
            "Fecha": "operation_date",
            "Fuente": "unknown",
            "Tipo movimiento": "unknown",
            "Descripción": "unknown",
            "Importe declarado": "unknown",
            "Importe banco": "unknown",
            "Importe caja/POS": "unknown",
            "Medio de pago": "payment_method",
            "Referencia externa": "document_reference",
            "Estado esperado": "unknown",
            "Observación dueño": "unknown",
            "Diferencia banco vs caja": "unknown",
            "Señal First Aid": "unknown",
            "Límite owner-safe": "unknown",
        },
        dangerous_columns=("ID movimiento", "Importe declarado", "Importe banco", "Importe caja/POS", "Diferencia banco vs caja"),
    ),
)


def _owner_answers(boundary: dict) -> dict[str, str]:
    return {
        str(question["field_id"]): f"La columna {question['column_name']} representa {question['column_name']}"
        for question in boundary["owner_questions"]
    }


def _outcome(expected: str, predicted: str, owner_question_needed: bool) -> str:
    if expected != "unknown" and predicted == expected:
        return EXACT_MATCH
    if owner_question_needed:
        return SAFE_UNKNOWN if expected == "unknown" else SAFE_QUESTION
    return FALSE_CONFIDENT


def evaluate_physical_xlsx_product_readiness_corpus_v1(root: Path | None = None) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    rows: list[PhysicalRow] = []
    case_results: list[dict] = []

    for case in CASES:
        source = repo / "prueba_excels" / case.filename
        boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
            local_xlsx_path=source,
            sheet_name=case.sheet_name,
        )
        if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
            raise AssertionError(f"{case.case_id}: intake blocked: {boundary.get('blocked_reason')}")
        connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
            owner_question_packet=boundary,
            owner_answers=_owner_answers(boundary),
        )
        if connector.get("status") != "INGESTION_OUTPUT_READY":
            raise AssertionError(f"{case.case_id}: connector blocked: {connector.get('blocked_reason')}")
        bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
            ingestion_output=connector["ingestion_output"]
        )
        if bridge.get("status") != "SEMANTIC_CANDIDATES_READY":
            raise AssertionError(f"{case.case_id}: semantic bridge blocked: {bridge.get('blocked_reason')}")

        by_column = {item.column_name: item for item in bridge["column_understandings"]}
        observed_columns = set(by_column)
        expected_columns = set(case.expected_roles)
        if observed_columns != expected_columns:
            raise AssertionError(
                f"{case.case_id}: physical columns drifted; expected={sorted(expected_columns)} observed={sorted(observed_columns)}"
            )

        case_rows: list[PhysicalRow] = []
        for column_name, expected in case.expected_roles.items():
            understanding = by_column[column_name]
            primary = understanding.primary_hypothesis
            predicted = primary.semantic_role if primary is not None else "unknown"
            row = PhysicalRow(
                case_id=case.case_id,
                sector=case.sector,
                filename=case.filename,
                sheet_name=case.sheet_name,
                column_name=column_name,
                expected_role=expected,
                predicted_role=predicted,
                confidence=float(understanding.confidence),
                owner_question_needed=bool(understanding.owner_question_needed),
                outcome=_outcome(expected, predicted, bool(understanding.owner_question_needed)),
                dangerous_if_wrong=column_name in case.dangerous_columns,
            )
            rows.append(row)
            case_rows.append(row)
        case_results.append({
            "case_id": case.case_id,
            "sector": case.sector,
            "filename": case.filename,
            "sheet_name": case.sheet_name,
            "columns": len(case_rows),
            "exact_matches": sum(r.outcome == EXACT_MATCH for r in case_rows),
            "safe_questions": sum(r.outcome == SAFE_QUESTION for r in case_rows),
            "safe_unknowns": sum(r.outcome == SAFE_UNKNOWN for r in case_rows),
            "false_confident": sum(r.outcome == FALSE_CONFIDENT for r in case_rows),
        })

    known_rows = [row for row in rows if row.expected_role != "unknown"]
    exact_matches = sum(row.outcome == EXACT_MATCH for row in rows)
    safe_questions = sum(row.outcome == SAFE_QUESTION for row in rows)
    safe_unknowns = sum(row.outcome == SAFE_UNKNOWN for row in rows)
    false_confident = sum(row.outcome == FALSE_CONFIDENT for row in rows)
    dangerous_errors = sum(
        row.outcome == FALSE_CONFIDENT and row.dangerous_if_wrong for row in rows
    )
    semantic_precision = (
        sum(row.outcome == EXACT_MATCH for row in known_rows) / len(known_rows)
        if known_rows else 0.0
    )
    safe_resolution_rate = (
        (exact_matches + safe_questions + safe_unknowns) / len(rows) if rows else 0.0
    )
    direct_resolution_coverage = exact_matches / len(rows) if rows else 0.0
    verdict = (
        VERDICT_READY
        if semantic_precision >= 0.90
        and safe_resolution_rate == 1.0
        and false_confident == 0
        and dangerous_errors == 0
        else VERDICT_NOT_READY
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "cases_count": len(CASES),
        "sectors_count": len({case.sector for case in CASES}),
        "columns_count": len(rows),
        "known_semantic_columns": len(known_rows),
        "exact_matches": exact_matches,
        "safe_questions": safe_questions,
        "safe_unknowns": safe_unknowns,
        "false_confident": false_confident,
        "dangerous_errors": dangerous_errors,
        "semantic_precision_supported_scope": round(semantic_precision, 4),
        "direct_resolution_coverage": round(direct_resolution_coverage, 4),
        "safe_resolution_rate": round(safe_resolution_rate, 4),
        "case_results": case_results,
        "rows": [asdict(row) for row in rows],
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_physical_xlsx_product_readiness_corpus_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == VERDICT_READY else 2


if __name__ == "__main__":
    raise SystemExit(main())

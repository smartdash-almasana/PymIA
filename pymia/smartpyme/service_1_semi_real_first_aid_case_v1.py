from __future__ import annotations

from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.first_aid_caja_diaria_triage_v1 import run_caja_diaria_triage_v1
from pymia.smartpyme.first_aid_precio_margen_basico_v1 import run_precio_margen_basico_v1
from pymia.smartpyme.first_aid_stock_alertas_basicas_v1 import run_stock_alertas_basicas_v1
from pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 import (
    Service1ManualFirstAidDeliveryFlowV1,
    build_service_1_manual_first_aid_delivery_flow_v1,
)

SEMI_REAL_CASE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
SEMI_REAL_CASE_ID: Final[str] = "service_1_semi_real_first_aid_case_v1"


class Service1SemiRealFirstAidCaseV1(TypedDict):
    case_id: str
    schema_version: str
    service_name: str
    business_profile: dict[str, object]
    declared_inputs: dict[str, object]
    flow: Service1ManualFirstAidDeliveryFlowV1
    generated_files: list[str]
    owner_context: str
    operator_review_notes: list[str]
    runtime_authorized: bool


def run_service_1_semi_real_first_aid_case_v1(
    output_dir: str | Path,
) -> Service1SemiRealFirstAidCaseV1:
    """Run a semi-real Service 1 First Aid case with plausible declared data."""
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    business_profile: dict[str, object] = {
        "business_type": "comercio_minorista_alimentos",
        "business_size": "micro_pyme",
        "operator_scenario": "Dueño pide una revisión rápida de margen, caja diaria y stock crítico.",
        "data_source": "datos declarados manualmente por el dueño",
    }
    declared_inputs: dict[str, object] = {
        "precio_margen_basico": {
            "precio_venta": 2500,
            "costo_unitario": 1625,
        },
        "caja_diaria_triage": {
            "saldo_inicial": 180000,
            "ingresos": 324500,
            "egresos": 286750,
        },
        "stock_alertas_basicas": {
            "producto": "Pack yerba 1kg",
            "stock_actual": 8,
            "stock_minimo": 15,
            "ventas_diarias_promedio": 3,
        },
    }

    tool_results = [
        run_precio_margen_basico_v1(**declared_inputs["precio_margen_basico"]),
        run_caja_diaria_triage_v1(**declared_inputs["caja_diaria_triage"]),
        run_stock_alertas_basicas_v1(**declared_inputs["stock_alertas_basicas"]),
    ]

    flow = build_service_1_manual_first_aid_delivery_flow_v1(
        tool_results=tool_results,
        output_dir=output_path,
    )

    return {
        "case_id": SEMI_REAL_CASE_ID,
        "schema_version": SEMI_REAL_CASE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "business_profile": business_profile,
        "declared_inputs": declared_inputs,
        "flow": flow,
        "generated_files": [delivery["output_path"] for delivery in flow["deliveries"]],
        "owner_context": (
            "Caso semi-real de comercio minorista: revisión preliminar de margen, "
            "caja diaria y stock crítico con datos declarados."
        ),
        "operator_review_notes": [
            "Revisar que los importes declarados coincidan con lo informado por el dueño.",
            "Entregar XLSX y summary_text como orientación preliminar, no como certificación.",
            "Solicitar evidencia adicional antes de prometer saldos, stock o rentabilidad real.",
        ],
        "runtime_authorized": False,
    }

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

SMOKE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
SMOKE_CASE_ID: Final[str] = "service_1_manual_first_aid_smoke_case_v1"


class Service1ManualFirstAidSmokeCaseV1(TypedDict):
    smoke_case_id: str
    schema_version: str
    service_name: str
    scenario_name: str
    flow: Service1ManualFirstAidDeliveryFlowV1
    generated_files: list[str]
    operator_runbook: list[str]
    runtime_authorized: bool
    notes: list[str]


def run_service_1_manual_first_aid_smoke_case_v1(
    output_dir: str | Path,
) -> Service1ManualFirstAidSmokeCaseV1:
    """Run a reproducible manual Service 1 First Aid smoke case.

    This smoke case intentionally executes the three existing deterministic First Aid
    tools with fixed declared inputs, then passes their already-built results into
    the manual delivery flow. It does not open any forbidden product layer.
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    tool_results = [
        run_precio_margen_basico_v1(precio_venta=1000, costo_unitario=650),
        run_caja_diaria_triage_v1(saldo_inicial=5000, ingresos=2400, egresos=1800),
        run_stock_alertas_basicas_v1(
            producto="SKU-SMOKE-001",
            stock_actual=7,
            stock_minimo=10,
            ventas_diarias_promedio=2,
        ),
    ]

    flow = build_service_1_manual_first_aid_delivery_flow_v1(
        tool_results=tool_results,
        output_dir=output_path,
    )

    generated_files = [delivery["output_path"] for delivery in flow["deliveries"]]

    return {
        "smoke_case_id": SMOKE_CASE_ID,
        "schema_version": SMOKE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "scenario_name": "Manual First Aid delivery with margin, cash, and stock declared inputs.",
        "flow": flow,
        "generated_files": generated_files,
        "operator_runbook": [
            "Prepare declared inputs for margin, cash, and stock First Aid checks.",
            "Run the deterministic First Aid tools manually or from an approved operator harness.",
            "Pass the resulting FirstAidToolResultV1 payloads to the manual delivery flow.",
            "Review the generated XLSX files and owner-facing summary before delivery.",
            "Do not present the output as full diagnosis, closed reconciliation, real stock, or real bank balance.",
        ],
        "runtime_authorized": False,
        "notes": [
            "Smoke case uses fixed declared inputs and deterministic local tools.",
            "No forbidden product layer is used.",
        ],
    }

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, Sequence, TypedDict

from pymia.smartpyme.first_aid_caja_diaria_triage_v1 import run_caja_diaria_triage_v1
from pymia.smartpyme.first_aid_precio_margen_basico_v1 import run_precio_margen_basico_v1
from pymia.smartpyme.first_aid_stock_alertas_basicas_v1 import run_stock_alertas_basicas_v1
from pymia.smartpyme.first_aid_tool_result_v1 import FirstAidToolResultV1
from pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 import (
    Service1ManualFirstAidDeliveryFlowV1,
    build_service_1_manual_first_aid_delivery_flow_v1,
)

PIPELINE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"

Service1PipelineToolRefV1 = Literal[
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
]

_ALLOWED_TOOL_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
)


class Service1PipelineToolRequestV1(TypedDict):
    tool_ref: Service1PipelineToolRefV1
    inputs: dict[str, object]


class Service1PipelineV1(TypedDict):
    schema_version: str
    service_name: str
    requested_tool_count: int
    executed_tool_refs: list[str]
    tool_results: list[FirstAidToolResultV1]
    delivery_flow: Service1ManualFirstAidDeliveryFlowV1
    runtime_authorized: bool
    notes: list[str]


def run_service_1_pipeline_v1(
    *,
    tool_requests: Sequence[Service1PipelineToolRequestV1],
    output_dir: str | Path,
) -> Service1PipelineV1:
    """Run the minimal explicit Service 1 First Aid pipeline.

    The pipeline executes only explicitly requested and allowlisted deterministic
    First Aid tools, then delegates delivery to the already validated manual
    delivery flow. It does not decide which tools to run.
    """
    normalized_requests = list(tool_requests)
    if not normalized_requests:
        raise ValueError("SERVICE_1_PIPELINE_V1 requires at least one tool request.")

    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    tool_results: list[FirstAidToolResultV1] = []
    for request in normalized_requests:
        tool_ref = str(request["tool_ref"])
        inputs = dict(request["inputs"])
        if tool_ref not in _ALLOWED_TOOL_REFS:
            raise ValueError(f"Unsupported SERVICE_1_PIPELINE_V1 tool_ref: {tool_ref}")
        tool_results.append(_execute_allowed_tool(tool_ref=tool_ref, inputs=inputs))

    delivery_flow = build_service_1_manual_first_aid_delivery_flow_v1(
        tool_results=tool_results,
        output_dir=output_path,
    )

    return {
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "requested_tool_count": len(normalized_requests),
        "executed_tool_refs": [result["tool_ref"] for result in tool_results],
        "tool_results": tool_results,
        "delivery_flow": delivery_flow,
        "runtime_authorized": False,
        "notes": [
            "SERVICE_1_PIPELINE_V1 executed explicit allowlisted First Aid tools only.",
            "No forbidden product layer occurred.",
        ],
    }


def _execute_allowed_tool(*, tool_ref: str, inputs: dict[str, object]) -> FirstAidToolResultV1:
    if tool_ref == "precio_margen_basico":
        return run_precio_margen_basico_v1(
            precio_venta=inputs.get("precio_venta"),
            costo_unitario=inputs.get("costo_unitario"),
        )
    if tool_ref == "caja_diaria_triage":
        return run_caja_diaria_triage_v1(
            saldo_inicial=inputs.get("saldo_inicial"),
            ingresos=inputs.get("ingresos"),
            egresos=inputs.get("egresos"),
        )
    if tool_ref == "stock_alertas_basicas":
        return run_stock_alertas_basicas_v1(
            producto=inputs.get("producto"),
            stock_actual=inputs.get("stock_actual"),
            stock_minimo=inputs.get("stock_minimo"),
            ventas_diarias_promedio=inputs.get("ventas_diarias_promedio"),
        )
    raise ValueError(f"Unsupported SERVICE_1_PIPELINE_V1 tool_ref: {tool_ref}")

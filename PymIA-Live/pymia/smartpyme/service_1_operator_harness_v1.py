from __future__ import annotations

from pathlib import Path
from typing import Final, Sequence, TypedDict

from pymia.smartpyme.service_1_pipeline_v1 import (
    Service1PipelineToolRequestV1,
    Service1PipelineV1,
    run_service_1_pipeline_v1,
)

HARNESS_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
SAMPLE_CASE_ID: Final[str] = "service_1_first_aid_comercio_minorista_demo"


class Service1OperatorHarnessCaseV1(TypedDict):
    case_id: str
    case_name: str
    tool_requests: list[Service1PipelineToolRequestV1]
    operator_notes: list[str]


class Service1OperatorHarnessRunV1(TypedDict):
    schema_version: str
    service_name: str
    case_id: str
    case_name: str
    delivery_dir: str
    pipeline_result: Service1PipelineV1
    generated_files: list[str]
    summary_path: str
    operator_report_path: str
    summary_text: str
    runtime_authorized: bool
    notes: list[str]


def build_service_1_operator_harness_sample_case_v1() -> Service1OperatorHarnessCaseV1:
    return {
        "case_id": SAMPLE_CASE_ID,
        "case_name": "Comercio minorista alimentos - First Aid demo",
        "tool_requests": [
            {
                "tool_ref": "precio_margen_basico",
                "inputs": {"precio_venta": 2500, "costo_unitario": 1625},
            },
            {
                "tool_ref": "caja_diaria_triage",
                "inputs": {"saldo_inicial": 180000, "ingresos": 324500, "egresos": 286750},
            },
            {
                "tool_ref": "stock_alertas_basicas",
                "inputs": {
                    "producto": "Pack yerba 1kg",
                    "stock_actual": 8,
                    "stock_minimo": 15,
                    "ventas_diarias_promedio": 3,
                },
            },
            {
                "tool_ref": "gastos_triage",
                "inputs": {
                    "concepto": ["alquiler", "energia", "insumos"],
                    "importe": [120000, 38500, 74200],
                    "categoria": ["fijo", "fijo", "variable"],
                },
            },
            {
                "tool_ref": "proveedores_precio_variacion_triage",
                "inputs": {
                    "proveedor": ["Mayorista Norte", "Mayorista Sur", "Mayorista Norte"],
                    "producto_o_insumo": ["Yerba 1kg", "Yerba 1kg", "Azucar 1kg"],
                    "precio_o_costo": [1625, 1710, 940],
                },
            },
        ],
        "operator_notes": [
            "Caso demo con datos declarados por el dueño.",
            "Entregar XLSX y resumen como orientación preliminar.",
            "Pedir evidencia adicional antes de afirmar resultados reales.",
        ],
    }


def run_service_1_operator_harness_v1(
    *,
    case: Service1OperatorHarnessCaseV1,
    output_root: str | Path,
) -> Service1OperatorHarnessRunV1:
    output_root_path = Path(output_root)
    if not output_root_path.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root_path}")

    case_id = _safe_case_id(case["case_id"])
    if not case_id:
        raise ValueError("SERVICE_1_OPERATOR_HARNESS_V1 requires a non-empty case_id.")
    if not case["tool_requests"]:
        raise ValueError("SERVICE_1_OPERATOR_HARNESS_V1 requires at least one tool request.")

    delivery_dir = output_root_path / case_id
    delivery_dir.mkdir(exist_ok=True)

    pipeline_result = run_service_1_pipeline_v1(
        tool_requests=case["tool_requests"],
        output_dir=delivery_dir,
    )

    generated_files = [
        delivery["output_path"] for delivery in pipeline_result["delivery_flow"]["deliveries"]
    ]
    summary_text = pipeline_result["delivery_flow"]["summary_text"]
    summary_path = delivery_dir / "summary.txt"
    operator_report_path = delivery_dir / "operator_report.txt"

    summary_path.write_text(summary_text, encoding="utf-8")
    operator_report_path.write_text(
        _build_operator_report(case=case, pipeline_result=pipeline_result),
        encoding="utf-8",
    )

    return {
        "schema_version": HARNESS_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": case_id,
        "case_name": case["case_name"],
        "delivery_dir": str(delivery_dir.resolve()),
        "pipeline_result": pipeline_result,
        "generated_files": generated_files,
        "summary_path": str(summary_path.resolve()),
        "operator_report_path": str(operator_report_path.resolve()),
        "summary_text": summary_text,
        "runtime_authorized": False,
        "notes": [
            "Operator harness run completed from explicit case payload.",
            "Delivery folder contains XLSX files, summary, and operator report.",
        ],
    }


def _safe_case_id(value: str) -> str:
    safe_chars = [char if char.isalnum() or char in ("-", "_") else "_" for char in value]
    return "".join(safe_chars).strip("._")


def _build_operator_report(
    *,
    case: Service1OperatorHarnessCaseV1,
    pipeline_result: Service1PipelineV1,
) -> str:
    lines: list[str] = [
        f"Caso: {case['case_name']}",
        f"Case ID: {case['case_id']}",
        f"Tools ejecutadas: {pipeline_result['requested_tool_count']}",
        "",
        "Resultados:",
    ]
    for tool_ref, status in zip(
        pipeline_result["executed_tool_refs"],
        pipeline_result["delivery_flow"]["statuses"],
        strict=True,
    ):
        lines.append(f"- {tool_ref}: {status}")

    if case["operator_notes"]:
        lines.append("")
        lines.append("Notas operador:")
        for note in case["operator_notes"]:
            lines.append(f"- {note}")

    lines.append("")
    lines.append("Entrega preliminar basada en datos declarados.")
    return "\n".join(lines)

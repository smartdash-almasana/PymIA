from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.exceland_bridge_v1 import ExcelandBridgeV1Result, build_exceland_bridge_v1
from pymia.smartpyme.excel_treatment_lab_v1 import ExcelTreatmentLabV1Result, build_excel_treatment_lab_v1
from pymia.smartpyme.service_1_xlsx_delivery_v1 import Service1XlsxDeliveryV1, build_service_1_xlsx_delivery_v1

COMPLETION_SLICE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
CAPABILITY_REF: Final[str] = "service_1_excel_treatment_lab_completion_slice_v1"
REVIEW_PACKET_CAPABILITY_REF: Final[str] = "service_1_excel_treatment_lab_review_packet_v1"
SYNTHETIC_CASE_ID: Final[str] = "service_1_excel_treatment_lab_synthetic_completion_v1"


class ExcelTreatmentLabCompletionSliceV1(TypedDict):
    schema_version: str
    service_name: str
    capability_ref: str
    case_id: str
    synthetic_data: bool
    real_client_data: bool
    runtime_authorized: bool
    production_allowed: bool
    lab_result: ExcelTreatmentLabV1Result
    exceland_bridge: ExcelandBridgeV1Result
    treatment_actions: list[str]
    review_findings: list[str]
    xlsx_delivery: Service1XlsxDeliveryV1
    owner_summary_path: str
    operator_notes_path: str
    output_files: list[str]
    output_hashes: dict[str, str]
    final_status: str
    owner_visible_summary: str
    operator_notes: list[str]


def run_excel_treatment_lab_completion_slice_v1(output_dir: str | Path) -> ExcelTreatmentLabCompletionSliceV1:
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    lab_result = build_excel_treatment_lab_v1(
        lab_input={
            "source_file": "ventas_sinteticas_junio.xlsx",
            "detected_columns": [
                {
                    "original_column_name": "Fecha Venta",
                    "suggested_semantic_role": "fecha",
                    "confidence": "mapped",
                },
                {
                    "original_column_name": "Producto",
                    "suggested_semantic_role": "producto",
                    "confidence": "mapped",
                },
                {
                    "original_column_name": "Cantidad Vendida",
                    "suggested_semantic_role": "cantidad",
                    "confidence": "mapped",
                },
                {
                    "original_column_name": "Precio Unitario",
                    "suggested_semantic_role": "precio_venta",
                    "confidence": "mapped",
                },
                {
                    "original_column_name": "Costo Unitario",
                    "suggested_semantic_role": "costo_unitario",
                    "confidence": "mapped",
                },
            ],
            "confirmed_columns": [
                {"original_column_name": "Fecha Venta", "confirmed_semantic_role": "fecha"},
                {"original_column_name": "Producto", "confirmed_semantic_role": "producto"},
                {"original_column_name": "Cantidad Vendida", "confirmed_semantic_role": "cantidad"},
                {"original_column_name": "Precio Unitario", "confirmed_semantic_role": "precio_venta"},
                {"original_column_name": "Costo Unitario", "confirmed_semantic_role": "costo_unitario"},
            ],
            "rows_processed": 25,
            "warnings": [
                "Fixture sintético con encabezados ya confirmados para rehearsal.",
                "No se ejecutó lectura ni normalización real de workbook.",
            ],
            "limitations": [
                "Paquete sintético de revisión; no procesa archivos reales.",
                "No confirma normalización final del archivo del cliente.",
                "No ejecuta limpieza irreversible sobre datos fuente.",
            ],
            "forbidden_claims": [
                "No confirma archivo cliente normalizado.",
                "No confirma cálculo validado sobre datos reales.",
                "No reemplaza revisión humana de columnas.",
            ],
            "owner_summary": "Laboratorio Excel sintético listo para paquete de revisión; columnas detectadas y confirmadas sin procesar archivo real.",
            "technical_notes": [
                "Completion slice uses declared fixture metadata only.",
                "No workbook was read as source input.",
            ],
        }
    )
    exceland_bridge = build_exceland_bridge_v1(
        bridge_input={
            "requested_template_ref": "precio_margen_basico_template",
            "requested_formula_refs": ["margen_bruto", "margen_bruto_pesos", "markup"],
            "input_fields_required": ["cantidad", "precio_venta", "costo_unitario"],
            "input_fields_received": {
                "cantidad": "Cantidad Vendida",
                "precio_venta": "Precio Unitario",
                "costo_unitario": "Costo Unitario",
            },
            "warnings": ["Bridge lógico preparado desde columnas confirmadas del fixture."],
            "limitations": ["No ejecuta factoría ni genera plantilla Excel final."],
            "owner_summary": "Bridge lógico Exceland listo para revisión; no ejecuta fórmulas ni factoría real.",
            "technical_notes": ["Completion slice calls bridge contract only."],
        }
    )

    treatment_actions = _build_treatment_actions(lab_result=lab_result, exceland_bridge=exceland_bridge)
    review_findings = _build_review_findings(lab_result=lab_result, exceland_bridge=exceland_bridge)
    final_status = _final_status(lab_result=lab_result, exceland_bridge=exceland_bridge)

    xlsx_path = output_path / "excel_treatment_lab_review_packet.xlsx"
    xlsx_delivery = build_service_1_xlsx_delivery_v1(
        delivery_input=_build_delivery_input(
            final_status=final_status,
            lab_result=lab_result,
            exceland_bridge=exceland_bridge,
            treatment_actions=treatment_actions,
            review_findings=review_findings,
        ),
        output_path=xlsx_path,
    )

    owner_summary = _build_owner_visible_summary(
        lab_result=lab_result,
        exceland_bridge=exceland_bridge,
        treatment_actions=treatment_actions,
    )
    operator_notes = _build_operator_notes(
        lab_result=lab_result,
        exceland_bridge=exceland_bridge,
        treatment_actions=treatment_actions,
        review_findings=review_findings,
    )

    owner_summary_path = output_path / "owner_summary_excel_treatment_lab.txt"
    operator_notes_path = output_path / "operator_notes_excel_treatment_lab.txt"
    owner_summary_path.write_text(owner_summary, encoding="utf-8")
    operator_notes_path.write_text("\n".join(operator_notes), encoding="utf-8")

    output_files = [str(xlsx_path.resolve()), str(owner_summary_path.resolve()), str(operator_notes_path.resolve())]

    return {
        "schema_version": COMPLETION_SLICE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "capability_ref": CAPABILITY_REF,
        "case_id": SYNTHETIC_CASE_ID,
        "synthetic_data": True,
        "real_client_data": False,
        "runtime_authorized": False,
        "production_allowed": False,
        "lab_result": lab_result,
        "exceland_bridge": exceland_bridge,
        "treatment_actions": treatment_actions,
        "review_findings": review_findings,
        "xlsx_delivery": xlsx_delivery,
        "owner_summary_path": str(owner_summary_path.resolve()),
        "operator_notes_path": str(operator_notes_path.resolve()),
        "output_files": output_files,
        "output_hashes": {path: _sha256(Path(path)) for path in output_files},
        "final_status": final_status,
        "owner_visible_summary": owner_summary,
        "operator_notes": operator_notes,
    }


def _build_treatment_actions(
    *,
    lab_result: ExcelTreatmentLabV1Result,
    exceland_bridge: ExcelandBridgeV1Result,
) -> list[str]:
    actions = [
        f"Confirmar {len(lab_result['confirmed_columns'])} columnas semánticas declaradas.",
        f"Registrar {lab_result['rows_processed']} filas sintéticas como volumen de rehearsal.",
        "Preparar paquete XLSX de revisión con límites y claims prohibidos.",
    ]
    if exceland_bridge["status"] == "OK":
        actions.append("Adjuntar bridge lógico Exceland como referencia de plantilla permitida.")
    return actions


def _build_review_findings(
    *,
    lab_result: ExcelTreatmentLabV1Result,
    exceland_bridge: ExcelandBridgeV1Result,
) -> list[str]:
    return [
        f"lab_status={lab_result['status']}",
        f"detected_columns_count={lab_result['computed_results']['detected_columns_count']}",
        f"confirmed_columns_count={lab_result['computed_results']['confirmed_columns_count']}",
        f"pending_confirmation_columns={len(lab_result['computed_results']['pending_confirmation_columns'])}",
        f"exceland_bridge_status={exceland_bridge['status']}",
        f"exceland_supported_template={exceland_bridge['delivery_input']['computed_results']['supported_template']}",
    ]


def _final_status(
    *,
    lab_result: ExcelTreatmentLabV1Result,
    exceland_bridge: ExcelandBridgeV1Result,
) -> str:
    if lab_result["status"] != "OK":
        return "BLOCKED_BY_EXCEL_TREATMENT_LAB"
    if exceland_bridge["status"] != "OK":
        return "BLOCKED_BY_EXCELAND_BRIDGE"
    return "READY"


def _build_delivery_input(
    *,
    final_status: str,
    lab_result: ExcelTreatmentLabV1Result,
    exceland_bridge: ExcelandBridgeV1Result,
    treatment_actions: list[str],
    review_findings: list[str],
) -> dict[str, object]:
    return {
        "service_name": SERVICE_NAME,
        "capability_ref": REVIEW_PACKET_CAPABILITY_REF,
        "status": final_status,
        "owner_summary": "Paquete de revisión Laboratorio Excel listo; usa fixture sintético y no procesa archivo real.",
        "inputs_used": {
            "source_file_ref": lab_result["source_file"],
            "detected_columns": lab_result["detected_columns"],
            "confirmed_columns": lab_result["confirmed_columns"],
            "rows_processed": lab_result["rows_processed"],
            "exceland_template_ref": exceland_bridge["requested_template_ref"],
            "exceland_formula_refs": exceland_bridge["requested_formula_refs"],
            "synthetic_data": True,
            "real_client_data": False,
        },
        "computed_results": {
            "lab_status": lab_result["status"],
            "exceland_bridge_status": exceland_bridge["status"],
            "detected_columns_count": lab_result["computed_results"]["detected_columns_count"],
            "confirmed_columns_count": lab_result["computed_results"]["confirmed_columns_count"],
            "pending_confirmation_columns": lab_result["computed_results"]["pending_confirmation_columns"],
            "treatment_actions": treatment_actions,
            "review_findings": review_findings,
        },
        "missing_inputs": [],
        "limitations": [
            "Fixture sintético; no lee ni modifica archivos reales.",
            "No confirma normalización final del archivo del cliente.",
            "No ejecuta factoría Exceland real.",
            "No ejecuta fórmulas ni cálculos de negocio sobre datos reales.",
            "Revisión humana obligatoria antes de cualquier uso con cliente.",
        ],
        "forbidden_claims": [
            "No confirma archivo cliente normalizado.",
            "No confirma fórmula ejecutada.",
            "No confirma cálculo de negocio validado.",
            "No reemplaza revisión humana de columnas.",
            "No procesa archivos reales.",
        ],
        "technical_notes": [
            "Completion slice uses Excel Treatment Lab V1 contract.",
            "Completion slice uses Exceland Bridge V1 contract.",
            "No source workbook is read or written as input.",
            "Only the review packet XLSX output is generated.",
        ],
        "runtime_authorized": False,
    }


def _build_owner_visible_summary(
    *,
    lab_result: ExcelTreatmentLabV1Result,
    exceland_bridge: ExcelandBridgeV1Result,
    treatment_actions: list[str],
) -> str:
    return "\n".join(
        [
            "Servicio 1 — Paquete de revisión Laboratorio Excel",
            "",
            "Se generó un paquete sintético para revisar estructura, columnas confirmadas y posible bridge lógico Exceland.",
            "",
            "Resumen:",
            f"- Estado Laboratorio Excel: {lab_result['status']}",
            f"- Columnas detectadas: {lab_result['computed_results']['detected_columns_count']}",
            f"- Columnas confirmadas: {lab_result['computed_results']['confirmed_columns_count']}",
            f"- Filas declaradas en fixture: {lab_result['rows_processed']}",
            f"- Estado bridge Exceland: {exceland_bridge['status']}",
            f"- Acciones de tratamiento propuestas: {len(treatment_actions)}",
            "",
            "Límites:",
            "- No procesa archivos reales.",
            "- No confirma normalización final del archivo del cliente.",
            "- No ejecuta factoría Exceland real.",
            "- No ejecuta fórmulas ni cálculos de negocio sobre datos reales.",
            "- Requiere revisión humana antes de cualquier entrega con cliente.",
        ]
    )


def _build_operator_notes(
    *,
    lab_result: ExcelTreatmentLabV1Result,
    exceland_bridge: ExcelandBridgeV1Result,
    treatment_actions: list[str],
    review_findings: list[str],
) -> list[str]:
    return [
        "EXCEL_TREATMENT_LAB_COMPLETION_SLICE_V1",
        f"lab_status={lab_result['status']}",
        f"exceland_bridge_status={exceland_bridge['status']}",
        f"detected_columns_count={lab_result['computed_results']['detected_columns_count']}",
        f"confirmed_columns_count={lab_result['computed_results']['confirmed_columns_count']}",
        f"rows_processed={lab_result['rows_processed']}",
        f"treatment_actions_count={len(treatment_actions)}",
        "Use as synthetic review packet only; do not treat as normalized client workbook.",
        "No source workbook was read or modified.",
        "No external factory or formula execution was run.",
        "Human review remains mandatory before any client-facing interpretation.",
        *review_findings,
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

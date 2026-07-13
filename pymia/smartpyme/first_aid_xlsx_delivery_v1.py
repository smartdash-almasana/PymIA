from __future__ import annotations

from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.first_aid_tool_result_v1 import FirstAidToolResultV1
from pymia.smartpyme.service_1_xlsx_delivery_v1 import (
    DELIVERY_SCHEMA_VERSION,
    SERVICE_NAME,
    SHEET_NAMES,
    Service1XlsxDeliveryInputV1,
    build_service_1_xlsx_delivery_v1,
)


class FirstAidXlsxDeliveryV1(TypedDict):
    delivery_id: str
    schema_version: str
    service_name: str
    tool_ref: str
    output_path: str
    sheet_names: list[str]
    runtime_authorized: bool
    notes: list[str]


def build_first_aid_xlsx_delivery_v1(
    *,
    tool_result: FirstAidToolResultV1,
    output_path: str | Path,
) -> FirstAidXlsxDeliveryV1:
    delivery = build_service_1_xlsx_delivery_v1(
        delivery_input=_delivery_input_from_first_aid_tool_result(tool_result),
        output_path=output_path,
    )

    return {
        "delivery_id": delivery["delivery_id"].replace(
            "service_1_xlsx_delivery_v1:",
            "first_aid_xlsx_delivery_v1:",
            1,
        ),
        "schema_version": delivery["schema_version"],
        "service_name": delivery["service_name"],
        "tool_ref": str(tool_result["tool_ref"]),
        "output_path": delivery["output_path"],
        "sheet_names": delivery["sheet_names"],
        "runtime_authorized": delivery["runtime_authorized"],
        "notes": [
            "Deterministic XLSX delivery generated from FirstAidToolResultV1 via Service1XlsxDeliveryInputV1.",
            "No formulas, macros, or runtime execution were used.",
        ],
    }


def _delivery_input_from_first_aid_tool_result(
    tool_result: FirstAidToolResultV1,
) -> Service1XlsxDeliveryInputV1:
    return {
        "service_name": tool_result["service_name"],
        "capability_ref": str(tool_result["tool_ref"]),
        "status": tool_result["status"],
        "owner_summary": tool_result["owner_summary"],
        "inputs_used": dict(tool_result["inputs_used"]),
        "computed_results": dict(tool_result["computed_results"]),
        "missing_inputs": list(tool_result["missing_inputs"]),
        "limitations": list(tool_result["limitations"]),
        "forbidden_claims": list(tool_result["forbidden_claims"]),
        "technical_notes": list(tool_result["technical_notes"]),
        "runtime_authorized": tool_result["runtime_authorized"],
        "summary_ref_label": "tool_ref",
    }

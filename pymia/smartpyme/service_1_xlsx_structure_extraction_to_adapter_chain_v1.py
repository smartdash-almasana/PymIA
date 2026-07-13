from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.service_1_xlsx_structure_to_column_confirmation_v1 import (
    Service1XlsxStructureToColumnConfirmationResultV1,
    build_service_1_xlsx_structure_to_column_confirmation_v1,
)

SCHEMA_VERSION = "SERVICE_1_XLSX_STRUCTURE_EXTRACTION_TO_ADAPTER_CHAIN_V1"
SERVICE_NAME = "SERVICE_1"


@dataclass(frozen=True)
class Service1XlsxStructureExtractionToAdapterChainResultV1:
    schema_version: str
    service_name: str
    status: str
    extracted_file_name: str
    adapter_input: dict[str, Any]
    column_confirmation_result: Service1XlsxStructureToColumnConfirmationResultV1
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "status": self.status,
            "extracted_file_name": self.extracted_file_name,
            "adapter_input": self.adapter_input,
            "column_confirmation_result": self.column_confirmation_result.to_dict(),
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "metadata": dict(self.metadata),
        }


def build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
    *,
    extracted_structure: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> Service1XlsxStructureExtractionToAdapterChainResultV1:
    if not isinstance(extracted_structure, dict):
        raise ValueError("extracted_structure must be a dict")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    adapter_input = _normalize_extracted_structure_to_adapter_input(extracted_structure)
    chain_metadata = dict(metadata or {})
    column_confirmation_result = build_service_1_xlsx_structure_to_column_confirmation_v1(
        xlsx_structure=adapter_input,
        metadata=chain_metadata,
    )

    return Service1XlsxStructureExtractionToAdapterChainResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=column_confirmation_result.status,
        extracted_file_name=adapter_input["file_name"],
        adapter_input=adapter_input,
        column_confirmation_result=column_confirmation_result,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=chain_metadata,
    )


def _normalize_extracted_structure_to_adapter_input(extracted_structure: dict[str, Any]) -> dict[str, Any]:
    file_name = _required_text(
        extracted_structure.get("source_path_basename"),
        field_name="source_path_basename",
    )
    workbook = extracted_structure.get("workbook")
    if not isinstance(workbook, dict):
        raise ValueError("extracted_structure.workbook must be a dict")
    sheets = workbook.get("sheets")
    if not isinstance(sheets, list):
        raise ValueError("extracted_structure.workbook.sheets must be a list")

    normalized_sheets: list[dict[str, Any]] = []
    for index, sheet in enumerate(sheets):
        if not isinstance(sheet, dict):
            raise ValueError(f"workbook.sheets[{index}] must be a dict")

        sheet_name = _required_text(sheet.get("name"), field_name=f"workbook.sheets[{index}].name")
        headers = sheet.get("headers")
        if not isinstance(headers, list):
            raise ValueError(f"workbook.sheets[{index}].headers must be a list")

        sample_rows = sheet.get("sample_rows", [])
        if not isinstance(sample_rows, list):
            raise ValueError(f"workbook.sheets[{index}].sample_rows must be a list")

        normalized_sheets.append(
            {
                "sheet_name": sheet_name,
                "headers": list(headers),
                "sample_rows": sample_rows,
            }
        )

    return {
        "file_name": file_name,
        "sheets": normalized_sheets,
    }


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "Service1XlsxStructureExtractionToAdapterChainResultV1",
    "build_service_1_xlsx_structure_extraction_to_adapter_chain_v1",
]

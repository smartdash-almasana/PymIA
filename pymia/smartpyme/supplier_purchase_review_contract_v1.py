from __future__ import annotations

from typing import Final, Literal, TypedDict

from pymia.smartpyme.service_1_accounting_contracts_v1 import (
    Service1AccountingContractResultV1,
    build_service_1_accounting_contract_v1,
)

SUPPLIER_PURCHASE_REVIEW_CONTRACT_REF: Final[str] = "supplier_purchase_review_basic"
SUPPLIER_PURCHASE_REVIEW_CAPABILITY_REF: Final[str] = "service_1_supplier_purchase_review_contract_v1"

SupplierPurchaseReviewContractStatus = Literal[
    "READY_FOR_REVIEW",
    "MISSING_SUPPLIER_REGISTER",
    "MISSING_PURCHASE_REGISTER",
    "MISSING_FIELDS",
    "INVALID_INPUT",
]

_REQUIRED_SOURCES: Final[tuple[str, str]] = ("registro_proveedores", "registro_compras")
_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "fecha",
    "proveedor",
    "numero_comprobante",
    "importe",
)


class SupplierPurchaseReviewContractInputV1(TypedDict):
    owner_requested_output: str
    source_files_received: list[str]
    received_fields: list[str]


class SupplierPurchaseReviewContractResultV1(TypedDict):
    status: SupplierPurchaseReviewContractStatus
    contract_ref: str
    required_sources: list[str]
    received_sources: list[str]
    missing_sources: list[str]
    required_fields: list[str]
    received_fields: list[str]
    missing_fields: list[str]
    runtime_authorized: Literal[False]
    next_allowed_action: str
    accounting_contract: Service1AccountingContractResultV1
    delivery_input: dict[str, object]


def build_supplier_purchase_review_contract_v1(
    *,
    contract_input: SupplierPurchaseReviewContractInputV1,
) -> SupplierPurchaseReviewContractResultV1:
    source_files_received_raw = contract_input.get("source_files_received")
    received_fields_raw = contract_input.get("received_fields")

    if not _is_string_list(source_files_received_raw) or not _is_string_list(received_fields_raw):
        return _build_invalid_input_result(contract_input=contract_input)

    source_files_received = _normalize_text_list(source_files_received_raw)
    received_fields = _normalize_text_list(received_fields_raw)
    owner_requested_output = _normalize_optional_text(contract_input.get("owner_requested_output")) or "supplier_purchase_review_scope_report"

    accounting_contract = build_service_1_accounting_contract_v1(
        contract_input={
            "contract_ref": SUPPLIER_PURCHASE_REVIEW_CONTRACT_REF,
            "owner_requested_output": owner_requested_output,
            "source_files_required": list(_REQUIRED_SOURCES),
            "source_files_received": source_files_received,
            "required_fields": list(_REQUIRED_FIELDS),
            "received_fields": received_fields,
        }
    )

    status = _map_accounting_status_to_supplier_purchase_status(accounting_contract)
    next_allowed_action = _next_allowed_action(status)
    delivery_input = dict(accounting_contract["delivery_input"])
    delivery_input["capability_ref"] = SUPPLIER_PURCHASE_REVIEW_CAPABILITY_REF
    delivery_input["status"] = status
    delivery_input["owner_summary"] = _owner_summary(
        status=status,
        missing_fields=accounting_contract["missing_fields"],
    )
    delivery_input["computed_results"] = {
        **dict(delivery_input["computed_results"]),
        "supplier_purchase_review_status": status,
        "supplier_purchase_review_next_allowed_action": next_allowed_action,
    }

    return {
        "status": status,
        "contract_ref": SUPPLIER_PURCHASE_REVIEW_CONTRACT_REF,
        "required_sources": list(_REQUIRED_SOURCES),
        "received_sources": source_files_received,
        "missing_sources": list(accounting_contract["missing_sources"]),
        "required_fields": list(_REQUIRED_FIELDS),
        "received_fields": received_fields,
        "missing_fields": list(accounting_contract["missing_fields"]),
        "runtime_authorized": False,
        "next_allowed_action": next_allowed_action,
        "accounting_contract": accounting_contract,
        "delivery_input": delivery_input,
    }


def _build_invalid_input_result(
    *,
    contract_input: SupplierPurchaseReviewContractInputV1,
) -> SupplierPurchaseReviewContractResultV1:
    accounting_contract = build_service_1_accounting_contract_v1(
        contract_input={
            "contract_ref": SUPPLIER_PURCHASE_REVIEW_CONTRACT_REF,
            "owner_requested_output": _normalize_optional_text(contract_input.get("owner_requested_output")) or "supplier_purchase_review_scope_report",
            "source_files_required": list(_REQUIRED_SOURCES),
            "source_files_received": [],
            "required_fields": list(_REQUIRED_FIELDS),
            "received_fields": [],
        }
    )
    delivery_input = dict(accounting_contract["delivery_input"])
    delivery_input["capability_ref"] = SUPPLIER_PURCHASE_REVIEW_CAPABILITY_REF
    delivery_input["status"] = "INVALID_INPUT"
    delivery_input["owner_summary"] = "El contrato compras-proveedores es inválido; revisá listas de fuentes y campos."

    return {
        "status": "INVALID_INPUT",
        "contract_ref": SUPPLIER_PURCHASE_REVIEW_CONTRACT_REF,
        "required_sources": list(_REQUIRED_SOURCES),
        "received_sources": [],
        "missing_sources": list(_REQUIRED_SOURCES),
        "required_fields": list(_REQUIRED_FIELDS),
        "received_fields": [],
        "missing_fields": list(_REQUIRED_FIELDS),
        "runtime_authorized": False,
        "next_allowed_action": "fix_invalid_supplier_purchase_review_contract_input",
        "accounting_contract": accounting_contract,
        "delivery_input": delivery_input,
    }


def _map_accounting_status_to_supplier_purchase_status(
    accounting_contract: Service1AccountingContractResultV1,
) -> SupplierPurchaseReviewContractStatus:
    if accounting_contract["status"] == "MISSING_SOURCES":
        missing_sources = set(accounting_contract["missing_sources"])
        if "registro_proveedores" in missing_sources:
            return "MISSING_SUPPLIER_REGISTER"
        if "registro_compras" in missing_sources:
            return "MISSING_PURCHASE_REGISTER"
    if accounting_contract["status"] == "MISSING_FIELDS":
        return "MISSING_FIELDS"
    if accounting_contract["status"] == "READY_FOR_REVIEW":
        return "READY_FOR_REVIEW"
    return "INVALID_INPUT"


def _next_allowed_action(status: SupplierPurchaseReviewContractStatus) -> str:
    if status == "READY_FOR_REVIEW":
        return "manual_supplier_purchase_review"
    if status == "MISSING_SUPPLIER_REGISTER":
        return "request_supplier_register"
    if status == "MISSING_PURCHASE_REGISTER":
        return "request_purchase_register"
    if status == "MISSING_FIELDS":
        return "request_missing_supplier_purchase_review_fields"
    return "fix_invalid_supplier_purchase_review_contract_input"


def _owner_summary(
    *,
    status: SupplierPurchaseReviewContractStatus,
    missing_fields: list[str],
) -> str:
    if status == "READY_FOR_REVIEW":
        return "El contrato compras-proveedores está listo para revisión manual; no valida precios, impuestos ni comprobantes."
    if status == "MISSING_SUPPLIER_REGISTER":
        return "Falta el registro de proveedores para preparar la revisión compras-proveedores."
    if status == "MISSING_PURCHASE_REGISTER":
        return "Falta el registro de compras para preparar la revisión compras-proveedores."
    if status == "MISSING_FIELDS":
        return "Faltan campos obligatorios para preparar la revisión compras-proveedores: " + ", ".join(missing_fields) + "."
    return "El contrato compras-proveedores es inválido; revisá listas de fuentes y campos."


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _normalize_text_list(values: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        text = _normalize_optional_text(value)
        if text:
            normalized.append(text)
    return normalized


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

from __future__ import annotations

from typing import Final, Literal, TypedDict

from pymia.smartpyme.service_1_accounting_contracts_v1 import (
    Service1AccountingContractResultV1,
    build_service_1_accounting_contract_v1,
)

BANK_RECONCILIATION_CONTRACT_REF: Final[str] = "bank_reconciliation_basic"
BANK_RECONCILIATION_CAPABILITY_REF: Final[str] = "service_1_bank_reconciliation_contract_v1"

BankReconciliationContractStatus = Literal[
    "READY_FOR_REVIEW",
    "MISSING_BANK_STATEMENT",
    "MISSING_INTERNAL_LEDGER",
    "MISSING_FIELDS",
    "INVALID_INPUT",
]

_REQUIRED_SOURCES: Final[tuple[str, str]] = ("extracto_banco", "archivo_contable")
_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "fecha",
    "importe",
    "referencia",
)


class BankReconciliationContractInputV1(TypedDict):
    owner_requested_output: str
    source_files_received: list[str]
    received_fields: list[str]


class BankReconciliationContractResultV1(TypedDict):
    status: BankReconciliationContractStatus
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


def build_bank_reconciliation_contract_v1(
    *,
    contract_input: BankReconciliationContractInputV1,
) -> BankReconciliationContractResultV1:
    source_files_received_raw = contract_input.get("source_files_received")
    received_fields_raw = contract_input.get("received_fields")

    if not _is_string_list(source_files_received_raw) or not _is_string_list(received_fields_raw):
        return _build_invalid_input_result(contract_input=contract_input)

    source_files_received = _normalize_text_list(source_files_received_raw)
    received_fields = _normalize_text_list(received_fields_raw)
    owner_requested_output = _normalize_optional_text(contract_input.get("owner_requested_output")) or "bank_reconciliation_scope_report"

    accounting_contract = build_service_1_accounting_contract_v1(
        contract_input={
            "contract_ref": BANK_RECONCILIATION_CONTRACT_REF,
            "owner_requested_output": owner_requested_output,
            "source_files_required": list(_REQUIRED_SOURCES),
            "source_files_received": source_files_received,
            "required_fields": list(_REQUIRED_FIELDS),
            "received_fields": received_fields,
        }
    )

    status = _map_accounting_status_to_bank_status(accounting_contract)
    next_allowed_action = _next_allowed_action(status)
    delivery_input = dict(accounting_contract["delivery_input"])
    delivery_input["capability_ref"] = BANK_RECONCILIATION_CAPABILITY_REF
    delivery_input["status"] = status
    delivery_input["owner_summary"] = _owner_summary(
        status=status,
        missing_sources=accounting_contract["missing_sources"],
        missing_fields=accounting_contract["missing_fields"],
    )
    delivery_input["computed_results"] = {
        **dict(delivery_input["computed_results"]),
        "bank_reconciliation_status": status,
        "bank_reconciliation_next_allowed_action": next_allowed_action,
    }

    return {
        "status": status,
        "contract_ref": BANK_RECONCILIATION_CONTRACT_REF,
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
    contract_input: BankReconciliationContractInputV1,
) -> BankReconciliationContractResultV1:
    accounting_contract = build_service_1_accounting_contract_v1(
        contract_input={
            "contract_ref": BANK_RECONCILIATION_CONTRACT_REF,
            "owner_requested_output": _normalize_optional_text(contract_input.get("owner_requested_output")) or "bank_reconciliation_scope_report",
            "source_files_required": list(_REQUIRED_SOURCES),
            "source_files_received": [],
            "required_fields": list(_REQUIRED_FIELDS),
            "received_fields": [],
        }
    )
    delivery_input = dict(accounting_contract["delivery_input"])
    delivery_input["capability_ref"] = BANK_RECONCILIATION_CAPABILITY_REF
    delivery_input["status"] = "INVALID_INPUT"
    delivery_input["owner_summary"] = "El contrato de conciliación bancaria es inválido; revisá listas de fuentes y campos."

    return {
        "status": "INVALID_INPUT",
        "contract_ref": BANK_RECONCILIATION_CONTRACT_REF,
        "required_sources": list(_REQUIRED_SOURCES),
        "received_sources": [],
        "missing_sources": list(_REQUIRED_SOURCES),
        "required_fields": list(_REQUIRED_FIELDS),
        "received_fields": [],
        "missing_fields": list(_REQUIRED_FIELDS),
        "runtime_authorized": False,
        "next_allowed_action": "fix_invalid_bank_reconciliation_contract_input",
        "accounting_contract": accounting_contract,
        "delivery_input": delivery_input,
    }


def _map_accounting_status_to_bank_status(
    accounting_contract: Service1AccountingContractResultV1,
) -> BankReconciliationContractStatus:
    if accounting_contract["status"] == "MISSING_SOURCES":
        missing_sources = set(accounting_contract["missing_sources"])
        if "extracto_banco" in missing_sources:
            return "MISSING_BANK_STATEMENT"
        if "archivo_contable" in missing_sources:
            return "MISSING_INTERNAL_LEDGER"
    if accounting_contract["status"] == "MISSING_FIELDS":
        return "MISSING_FIELDS"
    if accounting_contract["status"] == "READY_FOR_REVIEW":
        return "READY_FOR_REVIEW"
    return "INVALID_INPUT"


def _next_allowed_action(status: BankReconciliationContractStatus) -> str:
    if status == "READY_FOR_REVIEW":
        return "manual_bank_reconciliation_review"
    if status == "MISSING_BANK_STATEMENT":
        return "request_bank_statement"
    if status == "MISSING_INTERNAL_LEDGER":
        return "request_internal_ledger"
    if status == "MISSING_FIELDS":
        return "request_missing_bank_reconciliation_fields"
    return "fix_invalid_bank_reconciliation_contract_input"


def _owner_summary(
    *,
    status: BankReconciliationContractStatus,
    missing_sources: list[str],
    missing_fields: list[str],
) -> str:
    if status == "READY_FOR_REVIEW":
        return "El contrato de conciliación bancaria está listo para revisión manual; no ejecuta matching ni confirma saldo conciliado."
    if status == "MISSING_BANK_STATEMENT":
        return "Falta el extracto bancario para preparar la revisión de conciliación."
    if status == "MISSING_INTERNAL_LEDGER":
        return "Falta el archivo contable interno para preparar la revisión de conciliación."
    if status == "MISSING_FIELDS":
        return "Faltan campos obligatorios para preparar la revisión de conciliación: " + ", ".join(missing_fields) + "."
    return "El contrato de conciliación bancaria es inválido; revisá listas de fuentes y campos."


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

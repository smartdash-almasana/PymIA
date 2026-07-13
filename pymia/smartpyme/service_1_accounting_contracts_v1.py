from __future__ import annotations

import hashlib
import json
from typing import Final, Literal, TypedDict

from pymia.smartpyme.service_1_xlsx_delivery_v1 import Service1XlsxDeliveryInputV1

SERVICE_NAME: Final[str] = "SERVICE_1"
CAPABILITY_REF: Final[str] = "service_1_accounting_contracts_v1"

AccountingContractStatus = Literal[
    "READY_FOR_REVIEW",
    "MISSING_SOURCES",
    "MISSING_FIELDS",
    "UNSUPPORTED_CONTRACT",
    "INVALID_INPUT",
]

AccountingContractFamily = Literal[
    "bank_reconciliation",
    "mercado_pago_reconciliation",
    "invoice_collection_matching",
    "supplier_purchase_review",
    "accounting_workpaper",
]

SUPPORTED_CONTRACTS: Final[dict[str, dict[str, object]]] = {
    "bank_reconciliation_basic": {
        "family": "bank_reconciliation",
        "allowed_outputs": ["contract_review_report", "reconciliation_scope_summary"],
    },
    "mercado_pago_reconciliation_basic": {
        "family": "mercado_pago_reconciliation",
        "allowed_outputs": ["contract_review_report", "collection_scope_summary"],
    },
    "invoice_collection_matching_basic": {
        "family": "invoice_collection_matching",
        "allowed_outputs": ["contract_review_report", "matching_scope_summary"],
    },
    "supplier_purchase_review_basic": {
        "family": "supplier_purchase_review",
        "allowed_outputs": ["contract_review_report", "supplier_scope_summary"],
    },
    "accounting_workpaper_basic": {
        "family": "accounting_workpaper",
        "allowed_outputs": ["contract_review_report", "workpaper_scope_summary"],
    },
}

DEFAULT_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No confirma conciliación bancaria cerrada.",
    "No confirma auditoría contable certificada.",
    "No confirma exactitud fiscal.",
    "No confirma liquidación impositiva.",
    "No genera asientos contables automáticos.",
)

DEFAULT_LIMITATIONS: Final[tuple[str, ...]] = (
    "No ejecuta matching real ni conciliación efectiva.",
    "No calcula diferencias reales todavía.",
    "No produce movimientos contables ni workpapers finales.",
)

DEFAULT_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Pure deterministic accounting contract layer for Service 1.",
    "No IO, external integrations, OCR, PDF parsing, or accounting runtime execution were performed.",
)


class Service1AccountingContractInputV1(TypedDict):
    contract_ref: str | None
    owner_requested_output: str
    source_files_required: list[str]
    source_files_received: list[str]
    required_fields: list[str]
    received_fields: list[str]


class Service1AccountingContractResultV1(TypedDict):
    contract_id: str
    contract_ref: str | None
    family: AccountingContractFamily | str
    owner_requested_output: str
    source_files_required: list[str]
    source_files_received: list[str]
    missing_sources: list[str]
    required_fields: list[str]
    received_fields: list[str]
    missing_fields: list[str]
    allowed_outputs: list[str]
    forbidden_claims: list[str]
    limitations: list[str]
    runtime_authorized: Literal[False]
    next_allowed_action: str
    status: AccountingContractStatus
    delivery_input: Service1XlsxDeliveryInputV1


def build_service_1_accounting_contract_v1(
    *,
    contract_input: Service1AccountingContractInputV1,
) -> Service1AccountingContractResultV1:
    contract_ref = _normalize_optional_text(contract_input.get("contract_ref"))
    owner_requested_output = _normalize_optional_text(contract_input.get("owner_requested_output")) or "contract_review_report"

    source_files_required_raw = contract_input.get("source_files_required")
    source_files_received_raw = contract_input.get("source_files_received")
    required_fields_raw = contract_input.get("required_fields")
    received_fields_raw = contract_input.get("received_fields")

    invalid_lists = not all(
        _is_string_list(value)
        for value in (
            source_files_required_raw,
            source_files_received_raw,
            required_fields_raw,
            received_fields_raw,
        )
    )

    if invalid_lists:
        source_files_required: list[str] = []
        source_files_received: list[str] = []
        required_fields: list[str] = []
        received_fields: list[str] = []
        status: AccountingContractStatus = "INVALID_INPUT"
    else:
        source_files_required = _normalize_text_list(source_files_required_raw)
        source_files_received = _normalize_text_list(source_files_received_raw)
        required_fields = _normalize_text_list(required_fields_raw)
        received_fields = _normalize_text_list(received_fields_raw)
        status = "READY_FOR_REVIEW"

    metadata = SUPPORTED_CONTRACTS.get(contract_ref or "")
    family = str(metadata["family"]) if metadata else "unsupported_contract"
    allowed_outputs = list(metadata["allowed_outputs"]) if metadata else ["contract_review_report"]

    missing_sources = _difference(source_files_required, source_files_received)
    missing_fields = _difference(required_fields, received_fields)

    if status != "INVALID_INPUT":
        if not contract_ref or metadata is None:
            status = "UNSUPPORTED_CONTRACT"
        elif missing_sources:
            status = "MISSING_SOURCES"
        elif missing_fields:
            status = "MISSING_FIELDS"

    contract_id = _build_contract_id(
        contract_ref=contract_ref,
        source_files_required=source_files_required,
        source_files_received=source_files_received,
        required_fields=required_fields,
        received_fields=received_fields,
        owner_requested_output=owner_requested_output,
    )
    next_allowed_action = _next_allowed_action(status)
    owner_summary = _build_owner_summary(
        status=status,
        contract_ref=contract_ref,
        family=family,
        missing_sources=missing_sources,
        missing_fields=missing_fields,
    )

    delivery_input: Service1XlsxDeliveryInputV1 = {
        "service_name": SERVICE_NAME,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "owner_summary": owner_summary,
        "inputs_used": {
            "contract_ref": contract_ref,
            "family": family,
            "owner_requested_output": owner_requested_output,
            "source_files_required": source_files_required,
            "source_files_received": source_files_received,
            "required_fields": required_fields,
            "received_fields": received_fields,
        },
        "computed_results": {
            "contract_id": contract_id,
            "next_allowed_action": next_allowed_action,
            "allowed_outputs": allowed_outputs,
            "missing_sources": missing_sources,
            "missing_fields": missing_fields,
        },
        "missing_inputs": [*missing_sources, *missing_fields],
        "limitations": list(DEFAULT_LIMITATIONS),
        "forbidden_claims": list(DEFAULT_FORBIDDEN_CLAIMS),
        "technical_notes": list(DEFAULT_TECHNICAL_NOTES),
        "runtime_authorized": False,
    }

    return {
        "contract_id": contract_id,
        "contract_ref": contract_ref,
        "family": family,
        "owner_requested_output": owner_requested_output,
        "source_files_required": source_files_required,
        "source_files_received": source_files_received,
        "missing_sources": missing_sources,
        "required_fields": required_fields,
        "received_fields": received_fields,
        "missing_fields": missing_fields,
        "allowed_outputs": allowed_outputs,
        "forbidden_claims": list(DEFAULT_FORBIDDEN_CLAIMS),
        "limitations": list(DEFAULT_LIMITATIONS),
        "runtime_authorized": False,
        "next_allowed_action": next_allowed_action,
        "status": status,
        "delivery_input": delivery_input,
    }


def _difference(required_items: list[str], received_items: list[str]) -> list[str]:
    received = set(received_items)
    return [item for item in required_items if item not in received]


def _next_allowed_action(status: AccountingContractStatus) -> str:
    if status == "READY_FOR_REVIEW":
        return "manual_accounting_review"
    if status == "MISSING_SOURCES":
        return "request_missing_source_files"
    if status == "MISSING_FIELDS":
        return "request_missing_fields"
    if status == "UNSUPPORTED_CONTRACT":
        return "request_supported_contract_ref"
    return "fix_invalid_contract_input"


def _build_owner_summary(
    *,
    status: AccountingContractStatus,
    contract_ref: str | None,
    family: str,
    missing_sources: list[str],
    missing_fields: list[str],
) -> str:
    if status == "READY_FOR_REVIEW":
        return (
            "El contrato contable quedó listo para revisión manual prudente, "
            "sin prometer conciliación cerrada ni automatización contable."
        )
    if status == "MISSING_SOURCES":
        return "Faltan archivos fuente obligatorios para revisar este contrato: " + ", ".join(missing_sources) + "."
    if status == "MISSING_FIELDS":
        return "Faltan campos obligatorios para revisar este contrato: " + ", ".join(missing_fields) + "."
    if status == "UNSUPPORTED_CONTRACT":
        return (
            "El contrato solicitado no está soportado por la allowlist mínima actual: "
            f"{contract_ref or 'sin_contract_ref'}."
        )
    return (
        "El contrato lógico contable es inválido; "
        f"revisá el shape de listas requerido para {family}."
    )


def _build_contract_id(
    *,
    contract_ref: str | None,
    source_files_required: list[str],
    source_files_received: list[str],
    required_fields: list[str],
    received_fields: list[str],
    owner_requested_output: str,
) -> str:
    canonical_payload = json.dumps(
        {
            "contract_ref": contract_ref,
            "source_files_required": source_files_required,
            "source_files_received": source_files_received,
            "required_fields": required_fields,
            "received_fields": received_fields,
            "owner_requested_output": owner_requested_output,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    payload_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()[:16]
    return f"service_1_accounting_contracts_v1:{payload_hash}"


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

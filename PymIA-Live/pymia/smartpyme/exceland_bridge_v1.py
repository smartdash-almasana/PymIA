from __future__ import annotations

import hashlib
import json
from typing import Final, Literal, NotRequired, TypedDict

from pymia.smartpyme.service_1_xlsx_delivery_v1 import Service1XlsxDeliveryInputV1

SERVICE_NAME: Final[str] = "SERVICE_1"
SOURCE_SYSTEM: Final[str] = "EXCELAND"
CAPABILITY_REF: Final[str] = "exceland_bridge_v1"

SUPPORTED_TEMPLATE_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico_template",
    "caja_diaria_template",
    "stock_alertas_basicas_template",
    "gastos_triage_template",
    "proveedores_precio_variacion_template",
)

SUPPORTED_FORMULA_REFS: Final[tuple[str, ...]] = (
    "margen_bruto",
    "margen_bruto_pesos",
    "markup",
    "flujo_caja_neto",
    "saldo_acumulado",
    "alerta_stock_minimo",
    "dias_stock_restante",
)

DEFAULT_LIMITATIONS: Final[tuple[str, ...]] = (
    "No ejecuta Exceland real.",
    "No genera archivos Excel reales desde el bridge.",
    "No calcula resultados de negocio ni evalúa fórmulas.",
)

DEFAULT_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No confirma que la plantilla Excel final haya sido generada.",
    "No confirma que las fórmulas ya fueron ejecutadas.",
    "No confirma resultados de negocio ni validación contable.",
)

DEFAULT_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Pure deterministic bridge between Service 1 and the logical Exceland contract.",
    "No IO, YAML loading, formula execution, or workbook generation was performed.",
)

ExcelandBridgeStatus = Literal[
    "OK",
    "MISSING_INPUTS",
    "UNKNOWN_TEMPLATE",
    "UNSUPPORTED_FORMULA",
    "INVALID_INPUT",
]


class ExcelandBridgeInputV1(TypedDict):
    requested_template_ref: str | None
    requested_formula_refs: list[str]
    input_fields_required: list[str]
    input_fields_received: dict[str, object]
    warnings: NotRequired[list[str]]
    limitations: NotRequired[list[str]]
    forbidden_claims: NotRequired[list[str]]
    owner_summary: NotRequired[str]
    technical_notes: NotRequired[list[str]]


class ExcelandBridgeV1Result(TypedDict):
    bridge_id: str
    service_name: Literal["SERVICE_1"]
    source_system: Literal["EXCELAND"]
    capability_ref: Literal["exceland_bridge_v1"]
    status: ExcelandBridgeStatus
    requested_template_ref: str | None
    requested_formula_refs: list[str]
    input_fields_required: list[str]
    input_fields_received: dict[str, object]
    missing_inputs: list[str]
    warnings: list[str]
    limitations: list[str]
    forbidden_claims: list[str]
    owner_summary: str
    technical_notes: list[str]
    runtime_authorized: Literal[False]
    delivery_input: Service1XlsxDeliveryInputV1


def build_exceland_bridge_v1(
    *,
    bridge_input: ExcelandBridgeInputV1,
) -> ExcelandBridgeV1Result:
    requested_template_ref = _normalize_optional_text(bridge_input.get("requested_template_ref"))
    requested_formula_refs_raw = bridge_input.get("requested_formula_refs", [])
    input_fields_required_raw = bridge_input.get("input_fields_required")
    input_fields_received_raw = bridge_input.get("input_fields_received")

    warnings = _normalize_text_list(bridge_input.get("warnings", []))
    limitations = _merge_unique(DEFAULT_LIMITATIONS, bridge_input.get("limitations"))
    forbidden_claims = _merge_unique(DEFAULT_FORBIDDEN_CLAIMS, bridge_input.get("forbidden_claims"))
    technical_notes = _merge_unique(DEFAULT_TECHNICAL_NOTES, bridge_input.get("technical_notes"))

    if not _is_string_list(input_fields_required_raw):
        status: ExcelandBridgeStatus = "INVALID_INPUT"
        input_fields_required: list[str] = []
    else:
        input_fields_required = _normalize_text_list(input_fields_required_raw)
        status = "OK"

    if status != "INVALID_INPUT" and not isinstance(input_fields_received_raw, dict):
        status = "INVALID_INPUT"
        input_fields_received: dict[str, object] = {}
    else:
        input_fields_received = dict(input_fields_received_raw or {})

    if status != "INVALID_INPUT" and not _is_string_list(requested_formula_refs_raw):
        status = "INVALID_INPUT"
        requested_formula_refs: list[str] = []
    else:
        requested_formula_refs = _normalize_text_list(requested_formula_refs_raw if isinstance(requested_formula_refs_raw, list) else [])

    if status != "INVALID_INPUT":
        missing_inputs = _missing_inputs(
            requested_template_ref=requested_template_ref,
            input_fields_required=input_fields_required,
            input_fields_received=input_fields_received,
        )
        unsupported_formula_refs = [
            formula_ref
            for formula_ref in requested_formula_refs
            if formula_ref not in SUPPORTED_FORMULA_REFS
        ]

        if not requested_template_ref:
            status = "MISSING_INPUTS"
        elif requested_template_ref not in SUPPORTED_TEMPLATE_REFS:
            status = "UNKNOWN_TEMPLATE"
        elif unsupported_formula_refs:
            status = "UNSUPPORTED_FORMULA"
        elif missing_inputs:
            status = "MISSING_INPUTS"
    else:
        missing_inputs = []
        unsupported_formula_refs = []

    bridge_id = _build_bridge_id(
        requested_template_ref=requested_template_ref,
        requested_formula_refs=requested_formula_refs,
        input_fields_required=input_fields_required,
        input_fields_received=input_fields_received,
    )

    owner_summary = _build_owner_summary(
        status=status,
        requested_template_ref=requested_template_ref,
        missing_inputs=missing_inputs,
        unsupported_formula_refs=unsupported_formula_refs,
        owner_summary=bridge_input.get("owner_summary"),
    )

    delivery_input: Service1XlsxDeliveryInputV1 = {
        "service_name": SERVICE_NAME,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "owner_summary": owner_summary,
        "inputs_used": {
            "source_system": SOURCE_SYSTEM,
            "requested_template_ref": requested_template_ref,
            "requested_formula_refs": requested_formula_refs,
            "input_fields_required": input_fields_required,
            "input_fields_received": input_fields_received,
        },
        "computed_results": {
            "bridge_id": bridge_id,
            "source_system": SOURCE_SYSTEM,
            "supported_template": requested_template_ref if requested_template_ref in SUPPORTED_TEMPLATE_REFS else None,
            "supported_formula_refs": [
                formula_ref
                for formula_ref in requested_formula_refs
                if formula_ref in SUPPORTED_FORMULA_REFS
            ],
            "unsupported_formula_refs": unsupported_formula_refs,
            "received_input_field_count": len(input_fields_received),
        },
        "missing_inputs": missing_inputs,
        "limitations": limitations,
        "forbidden_claims": forbidden_claims,
        "technical_notes": technical_notes,
        "runtime_authorized": False,
    }

    return {
        "bridge_id": bridge_id,
        "service_name": SERVICE_NAME,
        "source_system": SOURCE_SYSTEM,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "requested_template_ref": requested_template_ref,
        "requested_formula_refs": requested_formula_refs,
        "input_fields_required": input_fields_required,
        "input_fields_received": input_fields_received,
        "missing_inputs": missing_inputs,
        "warnings": warnings,
        "limitations": limitations,
        "forbidden_claims": forbidden_claims,
        "owner_summary": owner_summary,
        "technical_notes": technical_notes,
        "runtime_authorized": False,
        "delivery_input": delivery_input,
    }


def _missing_inputs(
    *,
    requested_template_ref: str | None,
    input_fields_required: list[str],
    input_fields_received: dict[str, object],
) -> list[str]:
    missing: list[str] = []
    if not requested_template_ref:
        missing.append("requested_template_ref")

    for field_name in input_fields_required:
        if field_name not in input_fields_received:
            missing.append(field_name)
            continue
        value = input_fields_received[field_name]
        if value is None:
            missing.append(field_name)
            continue
        if isinstance(value, str) and not value.strip():
            missing.append(field_name)
    return missing


def _build_owner_summary(
    *,
    status: ExcelandBridgeStatus,
    requested_template_ref: str | None,
    missing_inputs: list[str],
    unsupported_formula_refs: list[str],
    owner_summary: str | None,
) -> str:
    normalized_summary = _normalize_optional_text(owner_summary)
    if normalized_summary:
        return normalized_summary

    if status == "OK":
        return (
            "La solicitud lógica para Exceland quedó lista y puede pasar al delivery XLSX genérico "
            "sin ejecutar la factoría todavía."
        )
    if status == "MISSING_INPUTS":
        return "Faltan datos mínimos para preparar el bridge lógico de Exceland: " + ", ".join(missing_inputs) + "."
    if status == "UNKNOWN_TEMPLATE":
        return (
            "La plantilla pedida no está soportada por la allowlist mínima actual del bridge: "
            f"{requested_template_ref or 'sin_template'}."
        )
    if status == "UNSUPPORTED_FORMULA":
        return (
            "La solicitud incluye fórmulas fuera de la allowlist mínima del bridge: "
            + ", ".join(unsupported_formula_refs)
            + "."
        )
    return "El contrato lógico del bridge Exceland es inválido y debe corregirse antes de continuar."


def _build_bridge_id(
    *,
    requested_template_ref: str | None,
    requested_formula_refs: list[str],
    input_fields_required: list[str],
    input_fields_received: dict[str, object],
) -> str:
    canonical = json.dumps(
        {
            "requested_template_ref": requested_template_ref,
            "requested_formula_refs": requested_formula_refs,
            "input_fields_required": input_fields_required,
            "input_fields_received": input_fields_received,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"exceland_bridge_v1:{payload_hash}"


def _merge_unique(defaults: tuple[str, ...], extra_values: list[str] | None) -> list[str]:
    merged = list(defaults)
    for value in _normalize_text_list(extra_values or []):
        if value not in merged:
            merged.append(value)
    return merged


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

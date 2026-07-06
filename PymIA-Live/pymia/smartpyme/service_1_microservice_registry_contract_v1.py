from __future__ import annotations

from typing import Any, Literal, TypedDict

RegistryStatus = Literal[
    "VALID",
    "INVALID_INPUT",
    "UNKNOWN_MICROSERVICE",
    "BLOCKED_MICROSERVICE",
    "BLOCKED_BY_DEPENDENCIES",
]

MicroserviceState = Literal[
    "IMPLEMENTED_VALIDATED",
    "IMPLEMENTED_PARTIAL",
    "CONTRACT_ONLY",
    "EXPERIMENTAL_FROZEN",
    "OUT_OF_SCOPE",
]

REQUIRED_REGISTRY_OUTPUT_FIELDS: tuple[str, ...] = (
    "status",
    "microservice_id",
    "state",
    "allowed_inputs",
    "allowed_outputs",
    "runtime_authorized",
    "human_review_required",
    "blocked_capabilities",
    "dependencies",
    "missing_dependencies",
    "next_allowed_action",
)

SUPPORTED_MICROSERVICES: dict[str, dict[str, object]] = {
    "file_intake": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["xlsx_or_tabular_file_metadata"],
        "allowed_outputs": ["file_intake_result"],
        "runtime_authorized": False,
        "human_review_required": False,
        "blocked_capabilities": ["ocr", "parser_automatico", "api_ingestion"],
        "dependencies": [],
        "next_allowed_action": "use_as_intake_boundary",
    },
    "first_aid_triage": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["explicit_tool_request", "simple_declared_values"],
        "allowed_outputs": ["first_aid_tool_result", "missing_inputs", "limitations"],
        "runtime_authorized": False,
        "human_review_required": False,
        "blocked_capabilities": ["diagnostico_integral", "autonomous_tool_selection"],
        "dependencies": [],
        "next_allowed_action": "run_allowlisted_first_aid_tool",
    },
    "excel_treatment_lab": {
        "state": "IMPLEMENTED_PARTIAL",
        "allowed_inputs": ["tabular_evidence", "declared_column_roles"],
        "allowed_outputs": ["normalized_evidence_notes", "treatment_limitations"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["final_clean_file_claim", "certified_transformation"],
        "dependencies": ["file_intake"],
        "next_allowed_action": "use_as_assisted_lab_component",
    },
    "exceland_bridge": {
        "state": "IMPLEMENTED_PARTIAL",
        "allowed_inputs": ["validated_tool_result", "delivery_spec"],
        "allowed_outputs": ["xlsx_delivery_spec"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["productive_accounting_runtime", "final_workbook_claim"],
        "dependencies": ["xlsx_delivery"],
        "next_allowed_action": "use_as_xlsx_bridge_under_review",
    },
    "owner_output": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["file_intake_result", "taskspec_patch", "tool_result"],
        "allowed_outputs": ["owner_response", "owner_message"],
        "runtime_authorized": False,
        "human_review_required": False,
        "blocked_capabilities": ["final_accounting_claim", "audit_claim"],
        "dependencies": [],
        "next_allowed_action": "render_safe_owner_output",
    },
    "xlsx_delivery": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["validated_delivery_input"],
        "allowed_outputs": ["operational_xlsx_draft"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["final_accounting_workbook", "tax_filing_ready_output"],
        "dependencies": [],
        "next_allowed_action": "prepare_operational_xlsx_draft",
    },
    "accounting_contracts": {
        "state": "CONTRACT_ONLY",
        "allowed_inputs": ["contract_ref", "source_files_required", "received_fields"],
        "allowed_outputs": ["contract_review_report", "scope_summary"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["matching_real", "conciliacion_definitiva", "asientos_automaticos"],
        "dependencies": ["xlsx_delivery"],
        "next_allowed_action": "prepare_contract_review",
    },
    "bank_reconciliation_basic": {
        "state": "CONTRACT_ONLY",
        "allowed_inputs": ["bank_statement_reference", "declared_internal_records"],
        "allowed_outputs": ["reconciliation_scope_summary", "missing_sources"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["conciliacion_bancaria_cerrada", "api_bancaria"],
        "dependencies": ["accounting_contracts", "xlsx_delivery"],
        "next_allowed_action": "prepare_bank_reconciliation_review_contract",
    },
    "mercado_pago_reconciliation_basic": {
        "state": "CONTRACT_ONLY",
        "allowed_inputs": ["mercado_pago_export_reference", "bank_statement_reference"],
        "allowed_outputs": ["collection_scope_summary", "missing_sources"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["mercado_pago_api", "liquidacion_final_comisiones"],
        "dependencies": ["accounting_contracts", "xlsx_delivery"],
        "next_allowed_action": "prepare_mercado_pago_review_contract",
    },
    "invoice_collection_matching_basic": {
        "state": "CONTRACT_ONLY",
        "allowed_inputs": ["invoice_list_reference", "collections_reference"],
        "allowed_outputs": ["matching_scope_summary", "missing_fields"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["matching_fino_definitivo", "saldo_cliente_final"],
        "dependencies": ["accounting_contracts", "xlsx_delivery"],
        "next_allowed_action": "prepare_invoice_collection_review_contract",
    },
    "supplier_purchase_review_basic": {
        "state": "CONTRACT_ONLY",
        "allowed_inputs": ["supplier_statement_reference", "purchase_records_reference"],
        "allowed_outputs": ["supplier_scope_summary", "missing_sources"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["cuenta_corriente_cerrada", "validacion_fiscal_proveedor"],
        "dependencies": ["accounting_contracts", "xlsx_delivery"],
        "next_allowed_action": "prepare_supplier_purchase_review_contract",
    },
    "accounting_workpaper": {
        "state": "IMPLEMENTED_PARTIAL",
        "allowed_inputs": ["accounting_contract_result", "manifest", "human_review_gate"],
        "allowed_outputs": ["workpaper_draft_packet", "operator_notes"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["papel_de_trabajo_final", "dictamen", "certificacion"],
        "dependencies": ["accounting_contracts", "xlsx_delivery"],
        "next_allowed_action": "prepare_workpaper_draft_packet",
    },
    "case_folder_manifest": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["case_metadata", "scope", "review_status"],
        "allowed_outputs": ["case_folder_manifest_contract_result"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["delivery_without_manifest"],
        "dependencies": [],
        "next_allowed_action": "validate_case_folder_manifest",
    },
    "delivery_manifest_audit": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["delivery_manifest_fields", "qa_status", "human_review_status"],
        "allowed_outputs": ["delivery_manifest_audit_result"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["delivery_without_qa", "forbidden_claims"],
        "dependencies": ["case_folder_manifest"],
        "next_allowed_action": "audit_delivery_manifest",
    },
    "owner_release_action_gate": {
        "state": "IMPLEMENTED_VALIDATED",
        "allowed_inputs": ["case_manifest_status", "delivery_audit_status", "requested_release_action"],
        "allowed_outputs": ["release_action_decision"],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["chatbot_autonomo", "llm_runtime", "ocr", "parser", "api", "final_accounting_claim"],
        "dependencies": ["case_folder_manifest", "delivery_manifest_audit"],
        "next_allowed_action": "gate_owner_release_action",
    },
    "chatbot": {
        "state": "OUT_OF_SCOPE",
        "allowed_inputs": [],
        "allowed_outputs": [],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["free_chat", "autonomous_decision"],
        "dependencies": [],
        "next_allowed_action": "do_not_open_in_service_1_registry_v1",
    },
    "servicio_2_diagnostic": {
        "state": "OUT_OF_SCOPE",
        "allowed_inputs": [],
        "allowed_outputs": [],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": ["diagnostico_integral_pyme"],
        "dependencies": [],
        "next_allowed_action": "keep_out_of_scope",
    },
}

BLOCKED_STATES = ("EXPERIMENTAL_FROZEN", "OUT_OF_SCOPE")


class Service1MicroserviceRegistryContractV1(TypedDict):
    status: RegistryStatus
    microservice_id: str | None
    state: str
    allowed_inputs: list[str]
    allowed_outputs: list[str]
    runtime_authorized: bool
    human_review_required: bool
    blocked_capabilities: list[str]
    dependencies: list[str]
    missing_dependencies: list[str]
    next_allowed_action: str


def build_service_1_microservice_registry_contract_v1(registry_input: dict[str, Any]) -> Service1MicroserviceRegistryContractV1:
    if not isinstance(registry_input, dict):
        return _empty_result(
            status="INVALID_INPUT",
            microservice_id=None,
            next_allowed_action="provide_registry_input_dict",
        )

    microservice_id_raw = registry_input.get("microservice_id")
    if microservice_id_raw is None or str(microservice_id_raw).strip() == "":
        return _empty_result(
            status="INVALID_INPUT",
            microservice_id=None,
            next_allowed_action="provide_microservice_id",
        )

    microservice_id = str(microservice_id_raw).strip()
    spec = SUPPORTED_MICROSERVICES.get(microservice_id)
    if spec is None:
        return _empty_result(
            status="UNKNOWN_MICROSERVICE",
            microservice_id=microservice_id,
            next_allowed_action="select_supported_service_1_microservice",
        )

    dependencies = list(spec["dependencies"])
    available_microservices = _normalize_available_microservices(registry_input.get("available_microservices"))
    missing_dependencies = [dependency for dependency in dependencies if dependency not in available_microservices]
    state = str(spec["state"])

    status: RegistryStatus = "VALID"
    next_allowed_action = str(spec["next_allowed_action"])
    if state in BLOCKED_STATES:
        status = "BLOCKED_MICROSERVICE"
        next_allowed_action = "keep_microservice_blocked"
    elif missing_dependencies:
        status = "BLOCKED_BY_DEPENDENCIES"
        next_allowed_action = "complete_microservice_dependencies"

    return {
        "status": status,
        "microservice_id": microservice_id,
        "state": state,
        "allowed_inputs": list(spec["allowed_inputs"]),
        "allowed_outputs": list(spec["allowed_outputs"]),
        "runtime_authorized": bool(spec["runtime_authorized"]),
        "human_review_required": bool(spec["human_review_required"]),
        "blocked_capabilities": list(spec["blocked_capabilities"]),
        "dependencies": dependencies,
        "missing_dependencies": missing_dependencies,
        "next_allowed_action": next_allowed_action,
    }


def _normalize_available_microservices(value: object) -> set[str]:
    if value is None:
        return set(SUPPORTED_MICROSERVICES)
    if not isinstance(value, list):
        return set()
    return {str(item).strip() for item in value if str(item).strip()}


def _empty_result(*, status: RegistryStatus, microservice_id: str | None, next_allowed_action: str) -> Service1MicroserviceRegistryContractV1:
    return {
        "status": status,
        "microservice_id": microservice_id,
        "state": "",
        "allowed_inputs": [],
        "allowed_outputs": [],
        "runtime_authorized": False,
        "human_review_required": True,
        "blocked_capabilities": [],
        "dependencies": [],
        "missing_dependencies": [],
        "next_allowed_action": next_allowed_action,
    }

from __future__ import annotations

from typing import Literal, TypedDict

RouteStatus = Literal["READY_FOR_SANDBOX_REHEARSAL"]
DataMode = Literal[
    "SYNTHETIC_FIXTURE",
    "MANUAL_METADATA",
    "ANONYMIZED_REHEARSAL_CANDIDATE",
]

REQUIRED_WEB_TEST_ROUTE_FIELDS: tuple[str, ...] = (
    "route_id",
    "label",
    "status",
    "maturity_hint",
    "allowed_data_modes",
    "blocked_data_modes",
    "runner_ref",
    "expected_artifacts",
    "forbidden_claims",
    "human_review_required",
    "runtime_authorized",
    "production_allowed",
)

ALLOWED_WEB_TEST_ROUTE_IDS: tuple[str, ...] = (
    "excel_treatment_lab_sandbox",
    "invoice_collection_matching_sandbox",
    "bank_reconciliation_sandbox",
    "accounting_workpaper_draft_sandbox",
    "first_aid_synthetic_delivery_rehearsal",
)

BLOCKED_WEB_TEST_ROUTE_IDS: tuple[str, ...] = (
    "mercado_pago_reconciliation",
    "mercado_pago_reconciliation_sandbox",
    "servicio_2_diagnostic",
    "servicio_2_diagnostic_sandbox",
    "ocr_ingestion",
    "api_ingestion",
    "chatbot_autonomo",
    "real_client_delivery",
    "final_accounting_review",
)

DEFAULT_ALLOWED_DATA_MODES: tuple[DataMode, ...] = (
    "SYNTHETIC_FIXTURE",
    "MANUAL_METADATA",
    "ANONYMIZED_REHEARSAL_CANDIDATE",
)

DEFAULT_BLOCKED_DATA_MODES: tuple[str, ...] = (
    "REAL_CLIENT_DATA",
    "SENSITIVE_ACCOUNTING_RECORDS",
    "BANK_CREDENTIALS",
    "MERCADO_PAGO_CREDENTIALS",
    "PRODUCTION_API_TOKENS",
)


class Service1WebTestRouteV1(TypedDict):
    route_id: str
    label: str
    status: RouteStatus
    maturity_hint: str
    allowed_data_modes: list[str]
    blocked_data_modes: list[str]
    runner_ref: str
    expected_artifacts: list[str]
    forbidden_claims: list[str]
    human_review_required: bool
    runtime_authorized: bool
    production_allowed: bool


_ALLOWED_WEB_TEST_ROUTES: dict[str, Service1WebTestRouteV1] = {
    "excel_treatment_lab_sandbox": {
        "route_id": "excel_treatment_lab_sandbox",
        "label": "Excel Treatment Lab Sandbox",
        "status": "READY_FOR_SANDBOX_REHEARSAL",
        "maturity_hint": "~82%",
        "allowed_data_modes": list(DEFAULT_ALLOWED_DATA_MODES),
        "blocked_data_modes": list(DEFAULT_BLOCKED_DATA_MODES),
        "runner_ref": "run_excel_treatment_lab_completion_slice_v1",
        "expected_artifacts": [
            "excel_treatment_lab_review_packet.xlsx",
            "owner_summary_excel_treatment_lab.txt",
            "operator_notes_excel_treatment_lab.txt",
        ],
        "forbidden_claims": [
            "real_workbook_normalized",
            "formulas_executed",
            "client_file_processed",
            "human_review_replaced",
            "final_clean_file_claim",
        ],
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
    },
    "invoice_collection_matching_sandbox": {
        "route_id": "invoice_collection_matching_sandbox",
        "label": "Invoice / Collection Matching Sandbox",
        "status": "READY_FOR_SANDBOX_REHEARSAL",
        "maturity_hint": "~70%",
        "allowed_data_modes": list(DEFAULT_ALLOWED_DATA_MODES),
        "blocked_data_modes": list(DEFAULT_BLOCKED_DATA_MODES),
        "runner_ref": "run_invoice_collection_matching_sandbox_completion_slice_v1",
        "expected_artifacts": [
            "invoice_collection_matching_sandbox_review_packet.xlsx",
            "owner_summary_invoice_collection_matching_sandbox.txt",
            "operator_notes_invoice_collection_matching_sandbox.txt",
        ],
        "forbidden_claims": [
            "final_debt_confirmed",
            "collection_applied_definitively",
            "customer_balance_certified",
            "accounting_entries_generated",
            "final_accounting_claim",
        ],
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
    },
    "bank_reconciliation_sandbox": {
        "route_id": "bank_reconciliation_sandbox",
        "label": "Bank Reconciliation Sandbox",
        "status": "READY_FOR_SANDBOX_REHEARSAL",
        "maturity_hint": "~76%",
        "allowed_data_modes": list(DEFAULT_ALLOWED_DATA_MODES),
        "blocked_data_modes": list(DEFAULT_BLOCKED_DATA_MODES),
        "runner_ref": "run_bank_reconciliation_sandbox_completion_slice_v1",
        "expected_artifacts": [
            "bank_reconciliation_sandbox_review_packet.xlsx",
            "owner_summary_bank_reconciliation_sandbox.txt",
            "operator_notes_bank_reconciliation_sandbox.txt",
        ],
        "forbidden_claims": [
            "reconciled_balance_confirmed",
            "final_difference_confirmed",
            "bank_api_used",
            "real_bank_statement_read",
            "conciliacion_bancaria_cerrada",
        ],
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
    },
    "accounting_workpaper_draft_sandbox": {
        "route_id": "accounting_workpaper_draft_sandbox",
        "label": "Accounting Workpaper Draft Sandbox",
        "status": "READY_FOR_SANDBOX_REHEARSAL",
        "maturity_hint": "~78%",
        "allowed_data_modes": list(DEFAULT_ALLOWED_DATA_MODES),
        "blocked_data_modes": list(DEFAULT_BLOCKED_DATA_MODES),
        "runner_ref": "run_accounting_workpaper_completion_slice_v1",
        "expected_artifacts": [
            "accounting_workpaper_draft_packet.xlsx",
            "owner_summary_accounting_workpaper.txt",
            "operator_notes_accounting_workpaper.txt",
        ],
        "forbidden_claims": [
            "final_workpaper_confirmed",
            "accounting_evidence_certified",
            "journal_entry_generated",
            "accountant_replaced",
            "tax_filing_ready_output",
        ],
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
    },
    "first_aid_synthetic_delivery_rehearsal": {
        "route_id": "first_aid_synthetic_delivery_rehearsal",
        "label": "First Aid Synthetic Delivery Rehearsal",
        "status": "READY_FOR_SANDBOX_REHEARSAL",
        "maturity_hint": "~90%",
        "allowed_data_modes": ["SYNTHETIC_FIXTURE", "MANUAL_METADATA"],
        "blocked_data_modes": list(DEFAULT_BLOCKED_DATA_MODES) + ["ANONYMIZED_REHEARSAL_CANDIDATE"],
        "runner_ref": "run_service_1_synthetic_real_case_pilot_v1",
        "expected_artifacts": [
            "first_aid_xlsx_outputs",
            "summary.txt",
            "delivery_report.txt",
            "README_ENTREGA.md",
            "manifest.json",
        ],
        "forbidden_claims": [
            "real_client_case_confirmed",
            "final_diagnosis_confirmed",
            "human_review_replaced",
            "autonomous_delivery_claim",
            "servicio_2_diagnostic_claim",
        ],
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
    },
}


def list_service_1_web_test_routes_v1() -> list[Service1WebTestRouteV1]:
    return [_copy_route(_ALLOWED_WEB_TEST_ROUTES[route_id]) for route_id in ALLOWED_WEB_TEST_ROUTE_IDS]


def get_service_1_web_test_route_v1(route_id: str) -> Service1WebTestRouteV1 | None:
    normalized_route_id = _normalize_route_id(route_id)
    route = _ALLOWED_WEB_TEST_ROUTES.get(normalized_route_id)
    if route is None:
        return None
    return _copy_route(route)


def is_service_1_web_test_route_allowed_v1(route_id: str) -> bool:
    normalized_route_id = _normalize_route_id(route_id)
    return normalized_route_id in _ALLOWED_WEB_TEST_ROUTES


def assert_service_1_web_test_route_allowed_v1(route_id: str) -> Service1WebTestRouteV1:
    route = get_service_1_web_test_route_v1(route_id)
    if route is None:
        raise ValueError(f"Blocked or unknown Servicio 1 web-test route: {route_id}")
    return route


def _normalize_route_id(route_id: str) -> str:
    return str(route_id).strip()


def _copy_route(route: Service1WebTestRouteV1) -> Service1WebTestRouteV1:
    return {
        "route_id": route["route_id"],
        "label": route["label"],
        "status": route["status"],
        "maturity_hint": route["maturity_hint"],
        "allowed_data_modes": list(route["allowed_data_modes"]),
        "blocked_data_modes": list(route["blocked_data_modes"]),
        "runner_ref": route["runner_ref"],
        "expected_artifacts": list(route["expected_artifacts"]),
        "forbidden_claims": list(route["forbidden_claims"]),
        "human_review_required": bool(route["human_review_required"]),
        "runtime_authorized": bool(route["runtime_authorized"]),
        "production_allowed": bool(route["production_allowed"]),
    }

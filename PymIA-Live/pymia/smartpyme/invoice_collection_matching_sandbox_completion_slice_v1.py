from __future__ import annotations

import hashlib
from decimal import Decimal
from pathlib import Path
from typing import Final, Literal, TypedDict

from pymia.smartpyme.accounting_sandbox_release_gate_v1 import (
    GateResult,
    evaluate_accounting_sandbox_release_gate_v1,
)
from pymia.smartpyme.invoice_collection_matching_contract_v1 import (
    InvoiceCollectionMatchingContractResultV1,
    build_invoice_collection_matching_contract_v1,
)
from pymia.smartpyme.service_1_xlsx_delivery_v1 import (
    Service1XlsxDeliveryV1,
    build_service_1_xlsx_delivery_v1,
)

COMPLETION_SLICE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
CAPABILITY_REF: Final[str] = "service_1_invoice_collection_matching_sandbox_completion_slice_v1"
REVIEW_PACKET_CAPABILITY_REF: Final[str] = "service_1_invoice_collection_matching_sandbox_review_packet_v1"
SYNTHETIC_CASE_ID: Final[str] = "service_1_invoice_collection_matching_sandbox_synthetic_completion_v1"

MatchStatus = Literal[
    "MATCHED_BY_INVOICE_NUMBER",
    "PENDING_COLLECTION",
    "UNMATCHED_COLLECTION",
    "AMOUNT_DIFFERENCE_REVIEW",
]


class InvoiceFixtureRowV1(TypedDict):
    fecha: str
    cliente: str
    numero_factura: str
    importe: str


class CollectionFixtureRowV1(TypedDict):
    fecha: str
    cliente: str
    numero_factura: str
    importe: str


class MatchingRowV1(TypedDict):
    numero_factura: str
    cliente: str
    invoice_amount: str
    collection_amount: str
    difference: str
    status: MatchStatus
    review_note: str


class InvoiceCollectionSandboxFixtureV1(TypedDict):
    fixture_id: str
    period_ref: str
    currency: str
    invoices: list[InvoiceFixtureRowV1]
    collections: list[CollectionFixtureRowV1]
    synthetic_data: bool
    real_client_data: bool


class InvoiceCollectionMatchingSandboxCompletionSliceV1(TypedDict):
    schema_version: str
    service_name: str
    capability_ref: str
    case_id: str
    synthetic_data: bool
    real_client_data: bool
    runtime_authorized: bool
    production_allowed: bool
    base_contract: InvoiceCollectionMatchingContractResultV1
    human_review_gate: GateResult
    fixture: InvoiceCollectionSandboxFixtureV1
    matching_rows: list[MatchingRowV1]
    status_counts: dict[str, int]
    xlsx_delivery: Service1XlsxDeliveryV1
    owner_summary_path: str
    operator_notes_path: str
    output_files: list[str]
    output_hashes: dict[str, str]
    final_status: str
    owner_visible_summary: str
    operator_notes: list[str]


def run_invoice_collection_matching_sandbox_completion_slice_v1(
    output_dir: str | Path,
) -> InvoiceCollectionMatchingSandboxCompletionSliceV1:
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    base_contract = build_invoice_collection_matching_contract_v1(
        contract_input={
            "owner_requested_output": "invoice_collection_matching_sandbox_review_packet",
            "source_files_received": ["registro_facturas", "registro_cobros"],
            "received_fields": ["fecha", "cliente", "numero_factura", "importe"],
        }
    )
    human_review_gate = evaluate_accounting_sandbox_release_gate_v1(
        gate_input={
            "capability_ref": "invoice_collection_matching_basic",
            "reviewer_role": "operator",
            "decision": "APPROVED",
            "scope_ok": True,
            "evidence_ok": True,
            "forbidden_claims": [],
            "live_use": False,
        }
    )
    fixture = _build_synthetic_fixture()
    matching_rows = _match_invoice_collection_rows(fixture=fixture)
    status_counts = _count_statuses(matching_rows)
    final_status = _final_status(base_contract=base_contract, human_review_gate=human_review_gate)

    delivery_input = _build_delivery_input(
        final_status=final_status,
        fixture=fixture,
        matching_rows=matching_rows,
        status_counts=status_counts,
    )
    xlsx_path = output_path / "invoice_collection_matching_sandbox_review_packet.xlsx"
    xlsx_delivery = build_service_1_xlsx_delivery_v1(
        delivery_input=delivery_input,
        output_path=xlsx_path,
    )

    owner_summary = _build_owner_visible_summary(status_counts=status_counts)
    operator_notes = _build_operator_notes(
        base_contract=base_contract,
        human_review_gate=human_review_gate,
        matching_rows=matching_rows,
        status_counts=status_counts,
    )

    owner_summary_path = output_path / "owner_summary_invoice_collection_matching_sandbox.txt"
    operator_notes_path = output_path / "operator_notes_invoice_collection_matching_sandbox.txt"
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
        "base_contract": base_contract,
        "human_review_gate": human_review_gate,
        "fixture": fixture,
        "matching_rows": matching_rows,
        "status_counts": status_counts,
        "xlsx_delivery": xlsx_delivery,
        "owner_summary_path": str(owner_summary_path.resolve()),
        "operator_notes_path": str(operator_notes_path.resolve()),
        "output_files": output_files,
        "output_hashes": {path: _sha256(Path(path)) for path in output_files},
        "final_status": final_status,
        "owner_visible_summary": owner_summary,
        "operator_notes": operator_notes,
    }


def _build_synthetic_fixture() -> InvoiceCollectionSandboxFixtureV1:
    return {
        "fixture_id": "synthetic-invoice-collection-fixture-001",
        "period_ref": "2026-06",
        "currency": "ARS",
        "invoices": [
            {"fecha": "2026-06-01", "cliente": "Cliente A", "numero_factura": "F-001", "importe": "100000.00"},
            {"fecha": "2026-06-02", "cliente": "Cliente B", "numero_factura": "F-002", "importe": "75000.00"},
            {"fecha": "2026-06-03", "cliente": "Cliente C", "numero_factura": "F-003", "importe": "50000.00"},
            {"fecha": "2026-06-04", "cliente": "Cliente D", "numero_factura": "F-004", "importe": "42000.00"},
        ],
        "collections": [
            {"fecha": "2026-06-05", "cliente": "Cliente A", "numero_factura": "F-001", "importe": "100000.00"},
            {"fecha": "2026-06-07", "cliente": "Cliente C", "numero_factura": "F-003", "importe": "47000.00"},
            {"fecha": "2026-06-08", "cliente": "Cliente X", "numero_factura": "F-999", "importe": "15000.00"},
        ],
        "synthetic_data": True,
        "real_client_data": False,
    }


def _match_invoice_collection_rows(*, fixture: InvoiceCollectionSandboxFixtureV1) -> list[MatchingRowV1]:
    invoices_by_number = {invoice["numero_factura"]: invoice for invoice in fixture["invoices"]}
    collections_by_number = {collection["numero_factura"]: collection for collection in fixture["collections"]}
    rows: list[MatchingRowV1] = []

    for invoice_number, invoice in invoices_by_number.items():
        collection = collections_by_number.get(invoice_number)
        if collection is None:
            rows.append(
                _build_matching_row(
                    invoice=invoice,
                    collection=None,
                    status="PENDING_COLLECTION",
                    review_note="Factura sin cobro sintético asociado; requiere revisión manual.",
                )
            )
            continue

        invoice_amount = Decimal(invoice["importe"])
        collection_amount = Decimal(collection["importe"])
        if invoice_amount == collection_amount:
            rows.append(
                _build_matching_row(
                    invoice=invoice,
                    collection=collection,
                    status="MATCHED_BY_INVOICE_NUMBER",
                    review_note="Factura y cobro coinciden por número e importe en fixture sintético.",
                )
            )
        else:
            rows.append(
                _build_matching_row(
                    invoice=invoice,
                    collection=collection,
                    status="AMOUNT_DIFFERENCE_REVIEW",
                    review_note="Factura y cobro comparten número, pero el importe difiere; requiere revisión manual.",
                )
            )

    for collection_number, collection in collections_by_number.items():
        if collection_number not in invoices_by_number:
            rows.append(
                _build_matching_row(
                    invoice=None,
                    collection=collection,
                    status="UNMATCHED_COLLECTION",
                    review_note="Cobro sintético sin factura asociada; requiere revisión manual.",
                )
            )

    return rows


def _build_matching_row(
    *,
    invoice: InvoiceFixtureRowV1 | None,
    collection: CollectionFixtureRowV1 | None,
    status: MatchStatus,
    review_note: str,
) -> MatchingRowV1:
    invoice_amount = Decimal(invoice["importe"]) if invoice is not None else Decimal("0.00")
    collection_amount = Decimal(collection["importe"]) if collection is not None else Decimal("0.00")
    invoice_number = invoice["numero_factura"] if invoice is not None else collection["numero_factura"] if collection else ""
    cliente = invoice["cliente"] if invoice is not None else collection["cliente"] if collection else ""
    return {
        "numero_factura": invoice_number,
        "cliente": cliente,
        "invoice_amount": _money(invoice_amount),
        "collection_amount": _money(collection_amount),
        "difference": _money(invoice_amount - collection_amount),
        "status": status,
        "review_note": review_note,
    }


def _count_statuses(rows: list[MatchingRowV1]) -> dict[str, int]:
    counts: dict[str, int] = {
        "MATCHED_BY_INVOICE_NUMBER": 0,
        "PENDING_COLLECTION": 0,
        "UNMATCHED_COLLECTION": 0,
        "AMOUNT_DIFFERENCE_REVIEW": 0,
    }
    for row in rows:
        counts[row["status"]] += 1
    return counts


def _final_status(
    *,
    base_contract: InvoiceCollectionMatchingContractResultV1,
    human_review_gate: GateResult,
) -> str:
    if base_contract["status"] != "READY_FOR_REVIEW":
        return "BLOCKED_BY_CONTRACT"
    if human_review_gate["status"] != "PASS":
        return "BLOCKED_BY_HUMAN_REVIEW_GATE"
    return "READY"


def _build_delivery_input(
    *,
    final_status: str,
    fixture: InvoiceCollectionSandboxFixtureV1,
    matching_rows: list[MatchingRowV1],
    status_counts: dict[str, int],
) -> dict[str, object]:
    return {
        "service_name": SERVICE_NAME,
        "capability_ref": REVIEW_PACKET_CAPABILITY_REF,
        "status": final_status,
        "owner_summary": "Paquete sandbox facturas-cobros listo para revisión manual; no confirma cobranzas aplicadas ni deuda final.",
        "inputs_used": {
            "fixture_id": fixture["fixture_id"],
            "period_ref": fixture["period_ref"],
            "currency": fixture["currency"],
            "invoice_rows": len(fixture["invoices"]),
            "collection_rows": len(fixture["collections"]),
            "synthetic_data": fixture["synthetic_data"],
            "real_client_data": fixture["real_client_data"],
        },
        "computed_results": {
            "matching_rows_count": len(matching_rows),
            "matched_by_invoice_number": status_counts["MATCHED_BY_INVOICE_NUMBER"],
            "pending_collection": status_counts["PENDING_COLLECTION"],
            "unmatched_collection": status_counts["UNMATCHED_COLLECTION"],
            "amount_difference_review": status_counts["AMOUNT_DIFFERENCE_REVIEW"],
            "matching_rows": matching_rows,
        },
        "missing_inputs": [],
        "limitations": [
            "Sandbox sintético; no usa registros reales de facturas o cobros.",
            "Matching determinístico mínimo por número de factura e importe.",
            "No confirma deuda final ni cobranza aplicada definitiva.",
            "No genera asientos contables ni imputaciones finales.",
            "Revisión humana contable obligatoria antes de cualquier uso con cliente.",
        ],
        "forbidden_claims": [
            "No confirma deuda final.",
            "No confirma cobranza aplicada definitiva.",
            "No certifica saldo de cliente.",
            "No genera asientos contables automáticos.",
            "No reemplaza revisión contable humana.",
            "No usa API ni archivos reales.",
        ],
        "technical_notes": [
            "Fixture embedded in completion slice.",
            "No source files are read or parsed.",
            "No external API is called.",
            "No autonomous conversational, image extraction, or parser runtime is used.",
        ],
        "runtime_authorized": False,
    }


def _build_owner_visible_summary(*, status_counts: dict[str, int]) -> str:
    return "\n".join(
        [
            "Servicio 1 — Paquete sandbox de revisión facturas-cobros",
            "",
            "Se generó un borrador sintético para revisar cruces básicos entre facturas y cobros.",
            "",
            "Resumen sandbox:",
            f"- Coincidencias por número de factura: {status_counts['MATCHED_BY_INVOICE_NUMBER']}",
            f"- Facturas pendientes de cobro: {status_counts['PENDING_COLLECTION']}",
            f"- Cobros sin factura asociada: {status_counts['UNMATCHED_COLLECTION']}",
            f"- Diferencias de importe para revisar: {status_counts['AMOUNT_DIFFERENCE_REVIEW']}",
            "",
            "Límites:",
            "- No confirma deuda final.",
            "- No confirma cobranza aplicada definitiva.",
            "- No certifica saldo de cliente.",
            "- No genera asientos contables.",
            "- No usa API ni archivos reales.",
            "- Requiere revisión humana contable antes de cualquier interpretación con cliente.",
        ]
    )


def _build_operator_notes(
    *,
    base_contract: InvoiceCollectionMatchingContractResultV1,
    human_review_gate: GateResult,
    matching_rows: list[MatchingRowV1],
    status_counts: dict[str, int],
) -> list[str]:
    return [
        "INVOICE_COLLECTION_MATCHING_SANDBOX_COMPLETION_SLICE_V1",
        f"base_contract_status={base_contract['status']}",
        f"human_review_gate_status={human_review_gate['status']}",
        f"matching_rows_count={len(matching_rows)}",
        f"matched_by_invoice_number={status_counts['MATCHED_BY_INVOICE_NUMBER']}",
        f"pending_collection={status_counts['PENDING_COLLECTION']}",
        f"unmatched_collection={status_counts['UNMATCHED_COLLECTION']}",
        f"amount_difference_review={status_counts['AMOUNT_DIFFERENCE_REVIEW']}",
        "Use as sandbox review packet only; do not treat as final invoice/collection matching.",
        "No API was called.",
        "No source files were read or parsed in this completion slice.",
        "No Mercado Pago logic is included.",
        "Human accounting review remains mandatory before any client-facing accounting interpretation.",
    ]


def _money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

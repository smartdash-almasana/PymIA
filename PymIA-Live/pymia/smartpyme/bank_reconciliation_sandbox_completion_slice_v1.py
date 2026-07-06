from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.accounting_sandbox_release_gate_v1 import (
    GateResult,
    evaluate_accounting_sandbox_release_gate_v1,
)
from pymia.smartpyme.bank_reconciliation_contract_v1 import (
    BankReconciliationContractResultV1,
    build_bank_reconciliation_contract_v1,
)
from pymia.smartpyme.bank_reconciliation_sandbox_contract_v1 import (
    SandboxResult,
    build_bank_reconciliation_sandbox_contract_v1,
)
from pymia.smartpyme.bank_reconciliation_sandbox_fixture_handoff_v1 import (
    HandoffResult,
    build_bank_reconciliation_sandbox_fixture_handoff_v1,
)
from pymia.smartpyme.bank_reconciliation_sandbox_fixture_model_v1 import (
    FixtureBundleResultV1,
    build_bank_reconciliation_sandbox_fixture_model_v1,
)
from pymia.smartpyme.bank_reconciliation_sandbox_review_packet_v1 import (
    ReviewPacketResult,
    build_bank_reconciliation_sandbox_review_packet_v1,
)
from pymia.smartpyme.service_1_xlsx_delivery_v1 import (
    Service1XlsxDeliveryV1,
    build_service_1_xlsx_delivery_v1,
)

COMPLETION_SLICE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
CAPABILITY_REF: Final[str] = "service_1_bank_reconciliation_sandbox_completion_slice_v1"
SYNTHETIC_CASE_ID: Final[str] = "service_1_bank_reconciliation_sandbox_synthetic_completion_v1"


class BankReconciliationSandboxCompletionSliceV1(TypedDict):
    schema_version: str
    service_name: str
    capability_ref: str
    case_id: str
    synthetic_data: bool
    real_client_data: bool
    runtime_authorized: bool
    production_allowed: bool
    base_contract: BankReconciliationContractResultV1
    sandbox_release_gate: GateResult
    fixture_model: FixtureBundleResultV1
    fixture_handoff: HandoffResult
    sandbox_contract: SandboxResult
    review_packet: ReviewPacketResult
    xlsx_delivery: Service1XlsxDeliveryV1
    owner_summary_path: str
    operator_notes_path: str
    output_files: list[str]
    output_hashes: dict[str, str]
    final_status: str
    owner_visible_summary: str
    operator_notes: list[str]


def run_bank_reconciliation_sandbox_completion_slice_v1(output_dir: str | Path) -> BankReconciliationSandboxCompletionSliceV1:
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    base_contract = build_bank_reconciliation_contract_v1(
        contract_input={
            "owner_requested_output": "bank_reconciliation_sandbox_review_packet",
            "source_files_received": ["extracto_banco", "archivo_contable"],
            "received_fields": ["fecha", "importe", "referencia"],
        }
    )
    sandbox_release_gate = evaluate_accounting_sandbox_release_gate_v1(
        gate_input={
            "capability_ref": "bank_reconciliation_basic",
            "responsible_role": "owner_or_accountant",
            "decision": "APPROVED",
            "scope_ok": True,
            "evidence_ok": True,
            "forbidden_claims": [],
            "live_use": False,
        }
    )
    fixture_model = build_bank_reconciliation_sandbox_fixture_model_v1(
        bundle_input={
            "bank_statement_fixture": {
                "fixture_id": "synthetic-bank-statement-fixture-001",
                "source_ref": "synthetic-bank-export-june-2026",
                "period_ref": "2026-06",
                "currency": "ARS",
                "movements": [
                    {
                        "movement_ref": "bank-001",
                        "date": "2026-06-03",
                        "amount": "125000.00",
                        "description": "Transferencia cliente A",
                    },
                    {
                        "movement_ref": "bank-002",
                        "date": "2026-06-05",
                        "amount": "-38500.00",
                        "description": "Pago proveedor limpieza",
                    },
                    {
                        "movement_ref": "bank-003",
                        "date": "2026-06-10",
                        "amount": "76000.00",
                        "description": "Depósito ventas mostrador",
                    },
                ],
                "live_source": False,
            },
            "internal_ledger_fixture": {
                "fixture_id": "synthetic-internal-ledger-fixture-001",
                "source_ref": "synthetic-ledger-june-2026",
                "period_ref": "2026-06",
                "currency": "ARS",
                "movements": [
                    {
                        "movement_ref": "ledger-001",
                        "date": "2026-06-03",
                        "amount": "125000.00",
                        "description": "Cobro cliente A declarado",
                    },
                    {
                        "movement_ref": "ledger-002",
                        "date": "2026-06-05",
                        "amount": "-38500.00",
                        "description": "Factura proveedor limpieza declarada",
                    },
                    {
                        "movement_ref": "ledger-003",
                        "date": "2026-06-11",
                        "amount": "76000.00",
                        "description": "Ventas mostrador declaradas",
                    },
                ],
                "live_source": False,
            },
        }
    )
    fixture_handoff = build_bank_reconciliation_sandbox_fixture_handoff_v1(
        handoff_input={
            "fixture_model_result": fixture_model,
            "base_contract": base_contract,
            "sandbox_release_gate": sandbox_release_gate,
            "live_use_requested": False,
        }
    )
    if fixture_handoff["sandbox_input"] is None:
        sandbox_contract = build_bank_reconciliation_sandbox_contract_v1(
            sandbox_input={
                "bank_contract": base_contract,
                "sandbox_release_gate": sandbox_release_gate,
                "fixture_refs": [],
                "live_use_requested": False,
            }
        )
    else:
        sandbox_contract = build_bank_reconciliation_sandbox_contract_v1(
            sandbox_input=fixture_handoff["sandbox_input"]  # type: ignore[arg-type]
        )
    review_packet = build_bank_reconciliation_sandbox_review_packet_v1(
        packet_input={
            "fixture_model_result": fixture_model,
            "fixture_handoff_result": fixture_handoff,
            "sandbox_contract_result": sandbox_contract,
        }
    )

    xlsx_path = output_path / "bank_reconciliation_sandbox_review_packet.xlsx"
    xlsx_delivery = build_service_1_xlsx_delivery_v1(
        delivery_input=review_packet["delivery_input"],
        output_path=xlsx_path,
    )

    owner_summary = _build_owner_visible_summary(review_packet=review_packet)
    operator_notes = _build_operator_notes(
        base_contract=base_contract,
        sandbox_release_gate=sandbox_release_gate,
        fixture_model=fixture_model,
        fixture_handoff=fixture_handoff,
        sandbox_contract=sandbox_contract,
        review_packet=review_packet,
    )

    owner_summary_path = output_path / "owner_summary_bank_reconciliation_sandbox.txt"
    operator_notes_path = output_path / "operator_notes_bank_reconciliation_sandbox.txt"
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
        "sandbox_release_gate": sandbox_release_gate,
        "fixture_model": fixture_model,
        "fixture_handoff": fixture_handoff,
        "sandbox_contract": sandbox_contract,
        "review_packet": review_packet,
        "xlsx_delivery": xlsx_delivery,
        "owner_summary_path": str(owner_summary_path.resolve()),
        "operator_notes_path": str(operator_notes_path.resolve()),
        "output_files": output_files,
        "output_hashes": {path: _sha256(Path(path)) for path in output_files},
        "final_status": review_packet["status"],
        "owner_visible_summary": owner_summary,
        "operator_notes": operator_notes,
    }


def _build_owner_visible_summary(*, review_packet: ReviewPacketResult) -> str:
    return "\n".join(
        [
            "Servicio 1 — Paquete sandbox de revisión bancaria",
            "",
            review_packet["owner_summary"],
            "",
            "Alcance:",
            "- Borrador operativo para revisión owner/operator.",
            "- Basado en fixtures sintéticos declarados.",
            "- Sirve para preparar una revisión, no para cerrar una conciliación.",
            "",
            "Límites:",
            "- No confirma saldo conciliado.",
            "- No confirma diferencia final.",
            "- No genera asientos contables.",
            "- No certifica exactitud contable o fiscal.",
            "- No lee extractos bancarios reales.",
            "- No usa API bancaria.",
        ]
    )


def _build_operator_notes(
    *,
    base_contract: BankReconciliationContractResultV1,
    sandbox_release_gate: GateResult,
    fixture_model: FixtureBundleResultV1,
    fixture_handoff: HandoffResult,
    sandbox_contract: SandboxResult,
    review_packet: ReviewPacketResult,
) -> list[str]:
    return [
        "BANK_RECONCILIATION_SANDBOX_COMPLETION_SLICE_V1",
        f"base_contract_status={base_contract['status']}",
        f"sandbox_release_gate_status={sandbox_release_gate['status']}",
        f"fixture_model_status={fixture_model['status']}",
        f"fixture_handoff_status={fixture_handoff['status']}",
        f"sandbox_contract_status={sandbox_contract['status']}",
        f"review_packet_status={review_packet['status']}",
        "Use as sandbox review packet only; do not treat as final bank reconciliation.",
        "No bank API was called.",
        "No source files were read or parsed in this completion slice.",
        "Accounting sandbox release remains mandatory before any client-facing accounting interpretation.",
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

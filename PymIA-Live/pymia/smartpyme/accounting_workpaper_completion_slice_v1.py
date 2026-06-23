from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.accounting_human_review_gate_v1 import (
    GateResult,
    evaluate_accounting_human_review_gate_v1,
)
from pymia.smartpyme.accounting_workpaper_contract_v1 import (
    AccountingWorkpaperContractResultV1,
    build_accounting_workpaper_contract_v1,
)
from pymia.smartpyme.accounting_workpaper_draft_packet_v1 import (
    WorkpaperDraftPacketResultV1,
    build_accounting_workpaper_draft_packet_v1,
)
from pymia.smartpyme.accounting_workpaper_manifest_model_v1 import (
    WorkpaperManifestBundleResultV1,
    build_accounting_workpaper_manifest_model_v1,
)
from pymia.smartpyme.service_1_xlsx_delivery_v1 import (
    Service1XlsxDeliveryV1,
    build_service_1_xlsx_delivery_v1,
)

COMPLETION_SLICE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
CAPABILITY_REF: Final[str] = "service_1_accounting_workpaper_completion_slice_v1"
SYNTHETIC_CASE_ID: Final[str] = "service_1_accounting_workpaper_synthetic_completion_v1"


class AccountingWorkpaperCompletionSliceV1(TypedDict):
    schema_version: str
    service_name: str
    capability_ref: str
    case_id: str
    synthetic_data: bool
    real_client_data: bool
    runtime_authorized: bool
    production_allowed: bool
    contract: AccountingWorkpaperContractResultV1
    manifest_model: WorkpaperManifestBundleResultV1
    human_review_gate: GateResult
    draft_packet: WorkpaperDraftPacketResultV1
    xlsx_delivery: Service1XlsxDeliveryV1
    owner_summary_path: str
    operator_notes_path: str
    output_files: list[str]
    output_hashes: dict[str, str]
    final_status: str
    owner_visible_summary: str
    operator_notes: list[str]


def run_accounting_workpaper_completion_slice_v1(output_dir: str | Path) -> AccountingWorkpaperCompletionSliceV1:
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    contract = build_accounting_workpaper_contract_v1(
        contract_input={
            "owner_requested_output": "accounting_workpaper_draft_review_packet",
            "source_files_received": ["evidencia_soporte", "plantilla_papel_trabajo"],
            "received_fields": ["periodo", "cliente", "area_revision", "responsable"],
        }
    )
    manifest_model = build_accounting_workpaper_manifest_model_v1(
        bundle_input={
            "evidence_manifest": {
                "manifest_id": "synthetic-evidence-manifest-workpaper-001",
                "period_ref": "2026-06",
                "evidence_items": [
                    {
                        "evidence_ref": "synthetic-balance-support-001",
                        "source_name": "Balance soporte sintético junio",
                        "source_kind": "xlsx_declared_synthetic",
                        "period_ref": "2026-06",
                        "owner_supplied": True,
                        "operator_notes": "Dato sintético declarado; no parseado desde archivo real.",
                        "sensitive_data_present": False,
                    },
                    {
                        "evidence_ref": "synthetic-ledger-extract-001",
                        "source_name": "Mayor contable sintético caja",
                        "source_kind": "xlsx_declared_synthetic",
                        "period_ref": "2026-06",
                        "owner_supplied": True,
                        "operator_notes": "Usado sólo para paquete borrador; no auditado.",
                        "sensitive_data_present": False,
                    },
                ],
                "live_source": False,
            },
            "template_manifest": {
                "template_ref": "synthetic-workpaper-template-001",
                "template_name": "Borrador revisión mensual caja",
                "area_revision": "caja",
                "required_sections": ["alcance", "evidencia", "faltantes", "revision_humana"],
                "optional_sections": ["notas_operador", "siguientes_pasos"],
                "review_owner": "operator",
                "template_runtime_requested": False,
            },
        }
    )
    human_review_gate = evaluate_accounting_human_review_gate_v1(
        gate_input={
            "capability_ref": "accounting_workpaper_basic",
            "reviewer_role": "operator",
            "decision": "APPROVED",
            "scope_ok": True,
            "evidence_ok": True,
            "forbidden_claims": [],
            "live_use": False,
        }
    )
    draft_packet = build_accounting_workpaper_draft_packet_v1(
        packet_input={
            "workpaper_contract_result": contract,
            "manifest_model_result": manifest_model,
            "human_review_gate_result": human_review_gate,
        }
    )

    xlsx_path = output_path / "accounting_workpaper_draft_packet.xlsx"
    xlsx_delivery = build_service_1_xlsx_delivery_v1(
        delivery_input=draft_packet["delivery_input"],
        output_path=xlsx_path,
    )

    owner_summary = _build_owner_visible_summary(draft_packet=draft_packet)
    operator_notes = _build_operator_notes(
        contract=contract,
        manifest_model=manifest_model,
        human_review_gate=human_review_gate,
        draft_packet=draft_packet,
    )

    owner_summary_path = output_path / "owner_summary_accounting_workpaper.txt"
    operator_notes_path = output_path / "operator_notes_accounting_workpaper.txt"
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
        "contract": contract,
        "manifest_model": manifest_model,
        "human_review_gate": human_review_gate,
        "draft_packet": draft_packet,
        "xlsx_delivery": xlsx_delivery,
        "owner_summary_path": str(owner_summary_path.resolve()),
        "operator_notes_path": str(operator_notes_path.resolve()),
        "output_files": output_files,
        "output_hashes": {path: _sha256(Path(path)) for path in output_files},
        "final_status": draft_packet["status"],
        "owner_visible_summary": owner_summary,
        "operator_notes": operator_notes,
    }


def _build_owner_visible_summary(*, draft_packet: WorkpaperDraftPacketResultV1) -> str:
    return "\n".join(
        [
            "Servicio 1 — Paquete borrador de papel de trabajo contable",
            "",
            draft_packet["owner_summary"],
            "",
            "Alcance:",
            "- Borrador operativo para revisión owner/operator.",
            "- Basado en manifiestos sintéticos declarados.",
            "- Requiere revisión humana antes de cualquier interpretación contable.",
            "",
            "Límites:",
            "- No genera papel de trabajo final.",
            "- No certifica evidencia suficiente.",
            "- No certifica conclusión contable o fiscal.",
            "- No genera asientos contables.",
            "- No lee archivos soporte reales.",
        ]
    )


def _build_operator_notes(
    *,
    contract: AccountingWorkpaperContractResultV1,
    manifest_model: WorkpaperManifestBundleResultV1,
    human_review_gate: GateResult,
    draft_packet: WorkpaperDraftPacketResultV1,
) -> list[str]:
    return [
        "SERVICE_1_ACCOUNTING_WORKPAPER_COMPLETION_SLICE_V1",
        f"contract_status={contract['status']}",
        f"manifest_status={manifest_model['status']}",
        f"human_review_gate_status={human_review_gate['status']}",
        f"draft_packet_status={draft_packet['status']}",
        "Use as draft packet only; do not treat as final workpaper.",
        "No source files were read or parsed in this completion slice.",
        "No template runtime was executed.",
        "Human accounting review remains mandatory before any client-facing accounting interpretation.",
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

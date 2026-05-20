from __future__ import annotations

import json
import sys
from pathlib import Path

# Add conversa-engine to sys.path
CONVERSA_DIR = Path(__file__).resolve().parents[1] / "conversa-engine"
if str(CONVERSA_DIR) not in sys.path:
    sys.path.insert(0, str(CONVERSA_DIR))

from operational_audit_runner import run_excel_operational_audit
from operational_audit_router import route_operational_audit_message
from pymia.audit_result.models import OperationalAuditResult


REPO_ROOT = Path(__file__).resolve().parents[1]
TEXTIL_XLSX = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def test_conversa_operational_audit_runner_e2e_integration(tmp_path: Path) -> None:
    tenant_id = "tenant-conversa-runner"
    session_id = "tenant-conversa-runner/user_42"

    result = run_excel_operational_audit(
        excel_path=TEXTIL_XLSX,
        tenant_id=tenant_id,
        session_id=session_id,
        output_dir=tmp_path,
    )

    assert result.ok is True
    assert result.evidence_path.exists()
    assert result.kernel_path.exists()
    assert result.audit_path.exists()

    # Load and validate the generated audit result
    with open(result.audit_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reconcile date fields for model validation
    pa = data["business_context"]["period_analyzed"]
    if "from_date" in pa:
        pa["from"] = pa.pop("from_date")
    if "to_date" in pa:
        pa["to"] = pa.pop("to_date")

    audit = OperationalAuditResult.model_validate(data)

    assert audit.audit_id == "audit_tenant-conversa-runner_la_textil_cosida_srl_mar_abr_may_2026"
    assert audit.pathology_routing_summary

    # Find PYME_033 and assert correct status & missing evidence
    pyme033_entry = None
    for r in audit.pathology_routing_summary:
        if r.pathology_code == "PYME_033":
            pyme033_entry = r
            break

    assert pyme033_entry is not None
    assert pyme033_entry.status == "pending_data"
    assert "ventas_por_sku" in pyme033_entry.missing_evidence

    # Invoke router
    decision = route_operational_audit_message("quiero ver PYME_033", audit)
    assert decision.pathology_code == "PYME_033"
    assert "ventas_por_sku" in decision.missing_evidence
    assert decision.next_question
    assert "PYME_033" in decision.reply_text

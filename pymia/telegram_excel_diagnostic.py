from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pymia.smartpyme.microservice_dispatcher import dispatch_candidate
from pymia.smartpyme.runtime_bridge import EXECUTION_READY_TO_EXECUTE, RuntimeExecutionCandidate
from pymia.telegram_excel_summary import resolve_latest_excel
from pymia.telegram_runtime import SENTINEL

DIAGNOSTIC_TRIGGERS = (
    "diagnosticalo",
    "diagnostica el excel",
    "diagnosticar el excel",
    "hace diagnostico",
    "hacer diagnostico",
    "ejecuta diagnostico",
    "ejecutar diagnostico",
)


@dataclass(frozen=True)
class TelegramExcelDiagnosticResult:
    text: str
    source: str = "pymia"
    mode: str = "diagnostic_dispatch"


def is_diagnostic_request(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return any(trigger in lowered for trigger in DIAGNOSTIC_TRIGGERS)


def _candidate_for_excel(path: Path) -> RuntimeExecutionCandidate:
    stem = path.stem.replace(" ", "_")[:80] or "telegram_excel"
    return RuntimeExecutionCandidate(
        tenant_id="telegram_direct",
        intake_id=f"telegram_{stem}",
        runtime_classification="excel_diagnostic",
        microservice_name="excel_diagnostic_worker",
        evidence_ids=[str(path)],
        status=EXECUTION_READY_TO_EXECUTE,
        can_dispatch=True,
    )


def render_dispatch_result(result) -> str:
    status = str(getattr(result, "status", "UNKNOWN"))
    microservice_name = str(getattr(result, "microservice_name", "excel_diagnostic_worker"))
    findings_count = int(getattr(result, "findings_count", 0) or 0)
    warnings = list(getattr(result, "warnings", []) or [])
    output_refs = list(getattr(result, "output_refs", []) or [])

    lines = [
        f"{SENTINEL} Diagnostico Excel via dispatcher",
        f"status: {status}",
        f"microservice: {microservice_name}",
        f"findings_count: {findings_count}",
    ]
    if output_refs:
        lines.append("output_refs:")
        lines.extend(f"- {ref}" for ref in output_refs[:3])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings[:3])
    if status != "EXECUTED":
        lines.append("No invento diagnostico: el dispatcher no ejecuto exitosamente.")
    return "\n".join(lines)


def run_latest_excel_diagnostic(output_dir: str | Path | None = None) -> TelegramExcelDiagnosticResult:
    latest = resolve_latest_excel()
    if latest is None:
        return TelegramExcelDiagnosticResult(
            text=f"{SENTINEL} No encontre un Excel recibido para diagnosticar. Primero subi un .xlsx, .xls o .csv.",
            mode="blocked",
        )
    if output_dir is None:
        output_dir = latest.parent / "diagnostics"
    result = dispatch_candidate(_candidate_for_excel(latest), evidence_path=latest, output_dir=output_dir)
    return TelegramExcelDiagnosticResult(text=render_dispatch_result(result))

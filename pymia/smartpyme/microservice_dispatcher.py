"""One-microservice dispatcher smoke for SmartPyme.

Executes only excel_diagnostic from a RuntimeExecutionCandidate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymia.smartpyme.classifications.supplier_duplicate_check import (
    diagnose_supplier_duplicates,
)
from pymia.smartpyme.excel_diagnostic import diagnose_excel
from .runtime_bridge import RuntimeExecutionCandidate, EXECUTION_READY_TO_EXECUTE

EXECUTION_EXECUTED = "EXECUTED"
EXECUTION_BLOCKED = "BLOCKED"
EXECUTION_UNSUPPORTED = "UNSUPPORTED"
EXECUTION_FAILED = "FAILED"


@dataclass
class MicroserviceExecutionResult:
    tenant_id: str
    intake_id: str
    runtime_classification: str
    microservice_name: str
    status: str
    output_refs: list[str] = field(default_factory=list)
    findings_count: int = 0
    raw_result: dict = field(default_factory=dict)
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "intake_id": self.intake_id,
            "runtime_classification": self.runtime_classification,
            "microservice_name": self.microservice_name,
            "status": self.status,
            "output_refs": list(self.output_refs),
            "findings_count": int(self.findings_count),
            "raw_result": dict(self.raw_result),
            "executed_at": self.executed_at,
            "warnings": list(self.warnings),
        }


def _candidate_to_dict(candidate: Any) -> dict:
    if isinstance(candidate, dict):
        return dict(candidate)
    if isinstance(candidate, RuntimeExecutionCandidate):
        return candidate.to_dict()
    if hasattr(candidate, "to_dict") and callable(candidate.to_dict):
        obj = candidate.to_dict()
        if not isinstance(obj, dict):
            raise ValueError("candidate.to_dict() must return dict")
        return dict(obj)
    raise ValueError("candidate must be dict or RuntimeExecutionCandidate")


def dispatch_candidate(candidate: Any, *, evidence_path: str | Path, output_dir: str | Path | None = None) -> MicroserviceExecutionResult:
    c = _candidate_to_dict(candidate)

    tenant_id = str(c.get("tenant_id", ""))
    intake_id = str(c.get("intake_id", ""))
    runtime_classification = str(c.get("runtime_classification", ""))
    microservice_name = str(c.get("microservice_name", ""))

    if c.get("status") != EXECUTION_READY_TO_EXECUTE:
        return MicroserviceExecutionResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name=microservice_name,
            status=EXECUTION_BLOCKED,
            warnings=["Candidate status is not READY_TO_EXECUTE."],
        )

    if bool(c.get("can_dispatch")) is False:
        return MicroserviceExecutionResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name=microservice_name,
            status=EXECUTION_BLOCKED,
            warnings=["Candidate can_dispatch is False."],
        )

    if runtime_classification not in {"excel_diagnostic", "supplier_duplicate_check"}:
        return MicroserviceExecutionResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name=microservice_name,
            status=EXECUTION_UNSUPPORTED,
            warnings=[f"Unsupported runtime_classification: {runtime_classification!r}."],
        )

    try:
        out_refs: list[str] = []
        markdown_output_path: Path | None = None
        if output_dir is not None:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            markdown_output_path = out_dir / "diagnostic_report.md"

        if runtime_classification == "excel_diagnostic":
            result = diagnose_excel(
                excel_path=evidence_path,
                tenant_id=tenant_id,
                markdown_output_path=markdown_output_path,
            )
        else:
            result, _ = diagnose_supplier_duplicates(
                excel_path=evidence_path,
                tenant_id=tenant_id,
                markdown_output_path=markdown_output_path,
            )

        if markdown_output_path is not None and markdown_output_path.exists():
            out_refs.append(str(markdown_output_path))

        return MicroserviceExecutionResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name=microservice_name,
            status=EXECUTION_EXECUTED,
            output_refs=out_refs,
            findings_count=len(result.findings),
            raw_result=asdict(result),
        )
    except Exception as exc:  # explicit fail-safe contract for smoke dispatcher
        return MicroserviceExecutionResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name=microservice_name,
            status=EXECUTION_FAILED,
            warnings=[f"Dispatcher execution failed: {exc}"],
            raw_result={"error": str(exc), "error_type": type(exc).__name__},
        )


__all__ = [
    "MicroserviceExecutionResult",
    "dispatch_candidate",
    "EXECUTION_EXECUTED",
    "EXECUTION_BLOCKED",
    "EXECUTION_UNSUPPORTED",
    "EXECUTION_FAILED",
]

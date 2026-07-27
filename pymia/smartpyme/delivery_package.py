"""Minimal delivery package builder for SmartPyme.

Pure conversion layer from execution result + gate verdict to tenant-deliverable
package metadata. No IO, no validation re-run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

STATUS_READY_TO_DELIVER = "READY_TO_DELIVER"
STATUS_BLOCKED = "BLOCKED"
STATUS_FAILED = "FAILED"


@dataclass
class DeliveryPackage:
    tenant_id: str
    intake_id: str
    runtime_classification: str
    output_refs: list[str]
    summary: str
    warnings: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    gate_verdict: str = ""
    status: str = STATUS_FAILED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "intake_id": self.intake_id,
            "runtime_classification": self.runtime_classification,
            "output_refs": list(self.output_refs),
            "summary": self.summary,
            "warnings": list(self.warnings),
            "reasons": list(self.reasons),
            "gate_verdict": self.gate_verdict,
            "status": self.status,
            "created_at": self.created_at,
        }


def _to_dict(obj: Any, *, label: str) -> dict:
    if isinstance(obj, dict):
        return dict(obj)
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        data = obj.to_dict()
        if not isinstance(data, dict):
            raise ValueError(f"{label}.to_dict() must return dict")
        return dict(data)
    raise ValueError(f"{label} must be dict or expose to_dict()")


def _required_non_empty(data: dict, key: str, *, label: str) -> str:
    val = data.get(key)
    text = "" if val is None else str(val).strip()
    if not text:
        raise ValueError(f"{label} missing required field: {key}")
    return text


def build_delivery_package(result: Any, verdict: Any) -> DeliveryPackage:
    result_data = _to_dict(result, label="result")
    verdict_data = _to_dict(verdict, label="verdict")

    tenant_id = _required_non_empty(result_data, "tenant_id", label="result")
    intake_id = _required_non_empty(result_data, "intake_id", label="result")
    runtime_classification = _required_non_empty(
        result_data, "runtime_classification", label="result"
    )

    raw_output_refs = result_data.get("output_refs")
    if raw_output_refs is None:
        raise ValueError("result missing required field: output_refs")
    if not isinstance(raw_output_refs, list):
        raise ValueError("result.output_refs must be a list")

    gate_verdict = _required_non_empty(verdict_data, "verdict", label="verdict")

    warnings = [str(w) for w in (result_data.get("warnings") or [])]
    warnings.extend(str(w) for w in (verdict_data.get("warnings") or []))
    reasons = [str(r) for r in (verdict_data.get("reasons") or [])]
    output_refs = [str(x) for x in raw_output_refs]

    if gate_verdict == "PASS":
        status = STATUS_READY_TO_DELIVER
        summary = "Execution validated and ready to deliver."
    elif gate_verdict == "BLOCKED":
        status = STATUS_BLOCKED
        summary = "Execution blocked by gate verdict."
    elif gate_verdict in {"FAILED", "UNDELIVERABLE"}:
        status = STATUS_FAILED
        summary = "Execution failed delivery criteria."
    else:
        raise ValueError(f"Unsupported gate verdict: {gate_verdict!r}")

    return DeliveryPackage(
        tenant_id=tenant_id,
        intake_id=intake_id,
        runtime_classification=runtime_classification,
        output_refs=output_refs,
        summary=summary,
        warnings=warnings,
        reasons=reasons,
        gate_verdict=gate_verdict,
        status=status,
    )


__all__ = [
    "DeliveryPackage",
    "build_delivery_package",
    "STATUS_READY_TO_DELIVER",
    "STATUS_BLOCKED",
    "STATUS_FAILED",
]

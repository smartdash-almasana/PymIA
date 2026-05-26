"""Execution result validation gate for SmartPyme.

Pure deterministic validation for a microservice execution result.
No writes, no network, no DB.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

VERDICT_PASS = "PASS"
VERDICT_BLOCKED = "BLOCKED"
VERDICT_FAILED = "FAILED"
VERDICT_UNDELIVERABLE = "UNDELIVERABLE"

_ALLOWED_VERDICTS: tuple[str, ...] = (
    VERDICT_PASS,
    VERDICT_BLOCKED,
    VERDICT_FAILED,
    VERDICT_UNDELIVERABLE,
)


@dataclass
class ExecutionResultGateVerdict:
    verdict: str
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
        }


def _to_dict(result: Any) -> dict:
    if isinstance(result, dict):
        return dict(result)
    if hasattr(result, "to_dict") and callable(result.to_dict):
        data = result.to_dict()
        if not isinstance(data, dict):
            raise ValueError("result.to_dict() must return dict")
        return dict(data)
    raise ValueError("result must be a dict or expose to_dict()")


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def validate_execution_result(result: Any) -> ExecutionResultGateVerdict:
    data = _to_dict(result)

    status = _as_str(data.get("status"))
    warnings = [str(w) for w in (data.get("warnings") or [])]

    if status == "BLOCKED":
        return ExecutionResultGateVerdict(
            verdict=VERDICT_BLOCKED,
            reasons=["Execution result status is BLOCKED."],
            warnings=warnings,
        )

    if status == "FAILED":
        return ExecutionResultGateVerdict(
            verdict=VERDICT_FAILED,
            reasons=["Execution result status is FAILED."],
            warnings=warnings,
        )

    if status == "UNSUPPORTED":
        return ExecutionResultGateVerdict(
            verdict=VERDICT_BLOCKED,
            reasons=["Execution result status is UNSUPPORTED."],
            warnings=warnings,
        )

    if status != "EXECUTED":
        return ExecutionResultGateVerdict(
            verdict=VERDICT_UNDELIVERABLE,
            reasons=[f"Unknown execution result status: {status!r}."],
            warnings=warnings,
        )

    reasons: list[str] = []

    tenant_id = _as_str(data.get("tenant_id")).strip()
    if not tenant_id:
        reasons.append("tenant_id is empty.")

    intake_id = _as_str(data.get("intake_id")).strip()
    if not intake_id:
        reasons.append("intake_id is empty.")

    runtime_classification = _as_str(data.get("runtime_classification")).strip()
    if not runtime_classification:
        reasons.append("runtime_classification is empty.")

    output_refs = data.get("output_refs") or []
    if not isinstance(output_refs, list) or len(output_refs) == 0:
        reasons.append("output_refs is empty.")
    else:
        for idx, ref in enumerate(output_refs):
            ref_text = _as_str(ref).strip()
            if not ref_text:
                reasons.append(f"output_refs[{idx}] is empty.")
                continue
            local_path = Path(ref_text)
            if not local_path.exists():
                reasons.append(f"output_ref does not exist: {ref_text}")

    findings_count = data.get("findings_count")
    try:
        findings_count_int = int(findings_count)
    except Exception:
        reasons.append("findings_count is not an integer.")
    else:
        if findings_count_int < 0:
            reasons.append("findings_count is negative.")

    raw_result = data.get("raw_result")
    if not raw_result:
        reasons.append("raw_result is empty.")
    else:
        try:
            json.dumps(raw_result)
        except Exception as exc:
            reasons.append(f"raw_result is not serializable: {exc}")

    if reasons:
        return ExecutionResultGateVerdict(
            verdict=VERDICT_UNDELIVERABLE,
            reasons=reasons,
            warnings=warnings,
        )

    return ExecutionResultGateVerdict(
        verdict=VERDICT_PASS,
        reasons=["Execution result is valid and deliverable."],
        warnings=warnings,
    )


__all__ = [
    "ExecutionResultGateVerdict",
    "validate_execution_result",
    "VERDICT_PASS",
    "VERDICT_BLOCKED",
    "VERDICT_FAILED",
    "VERDICT_UNDELIVERABLE",
]

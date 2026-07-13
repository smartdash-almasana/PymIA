"""Owner-facing report builder constrained by ADR-018.

This module does not compute diagnostics, alter findings, call runtime, or
expand evidence. It only translates existing operational artifacts into a
minimal owner-readable report.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from pymia.contracts.owner_facing_report_copy_v1 import warning_for_operational_status


STATUS_DELIVERED = "DELIVERED"
STATUS_DELIVERED_CANDIDATE = "DELIVERED_CANDIDATE"
STATUS_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class OwnerFacingReport:
    tenant_id: str
    intake_id: str
    status: str
    delivery_status: str
    operational_status: str
    summary: str
    blocked_message: str
    evidence_used: list[str]
    missing_evidence: list[str]
    next_questions: list[str]
    next_steps: list[str]
    references: list[str]
    output_refs: list[str]
    limit_warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_dict(obj: Any, *, label: str) -> dict[str, Any]:
    if isinstance(obj, Mapping):
        return dict(obj)
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump") and callable(obj.model_dump):
        data = obj.model_dump(mode="json")
        if not isinstance(data, dict):
            raise ValueError(f"{label}.model_dump() must return dict")
        return dict(data)
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        data = obj.to_dict()
        if not isinstance(data, dict):
            raise ValueError(f"{label}.to_dict() must return dict")
        return dict(data)
    raise ValueError(f"{label} must be mapping, dataclass, or expose model_dump()/to_dict()")


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _required_text(data: dict[str, Any], key: str, *, label: str) -> str:
    text = str(data.get(key) or "").strip()
    if not text:
        raise ValueError(f"{label} missing required field: {key}")
    return text


def _resolve_status(*, operational_status: str, delivery_status: str) -> str:
    if operational_status in {"blocked", "pending_data"} or delivery_status == "BLOCKED":
        return STATUS_BLOCKED
    if operational_status == "candidate":
        return STATUS_DELIVERED_CANDIDATE
    return STATUS_DELIVERED


def _resolve_summary(
    *,
    render_summary: str,
    blocked_message: str,
    delivery_summary: str,
) -> str:
    if blocked_message:
        return blocked_message
    if render_summary:
        return render_summary
    if delivery_summary:
        return delivery_summary
    raise ValueError("owner-facing report cannot be built without a traceable summary")


def _resolve_limit_warnings(
    *,
    render_contract: dict[str, Any],
    delivery_package: dict[str, Any],
    operational_status: str,
) -> list[str]:
    warnings = _as_string_list(render_contract.get("forbidden_inferences"))
    warnings.extend(_as_string_list(delivery_package.get("warnings")))
    operational_warning = warning_for_operational_status(operational_status)
    if operational_warning:
        warnings.append(operational_warning)
    return _dedupe_preserve_order(warnings)


def build_owner_facing_report(
    *,
    operational_audit_result: Any,
    render_contract: Any,
    delivery_package: Any,
) -> OwnerFacingReport:
    audit_data = _as_dict(operational_audit_result, label="operational_audit_result")
    render_data = _as_dict(render_contract, label="render_contract")
    delivery_data = _as_dict(delivery_package, label="delivery_package")

    tenant_id = _required_text(delivery_data, "tenant_id", label="delivery_package")
    intake_id = _required_text(delivery_data, "intake_id", label="delivery_package")
    delivery_status = _required_text(delivery_data, "status", label="delivery_package")
    operational_status = _required_text(audit_data, "status", label="operational_audit_result")

    audit_tenant_id = _required_text(audit_data, "tenant_id", label="operational_audit_result")
    render_tenant_id = _required_text(render_data, "tenant_id", label="render_contract")
    if tenant_id != audit_tenant_id or tenant_id != render_tenant_id:
        raise ValueError("tenant_id mismatch across owner-facing report sources")

    evidence_used = _dedupe_preserve_order(_as_string_list(audit_data.get("evidence_used")))
    missing_evidence = _dedupe_preserve_order(_as_string_list(audit_data.get("missing_evidence")))
    next_questions = _dedupe_preserve_order(
        _as_string_list(render_data.get("next_questions")) or list(missing_evidence)
    )
    next_steps = _dedupe_preserve_order(_as_string_list(render_data.get("next_steps")))
    references = _dedupe_preserve_order(_as_string_list(render_data.get("references")))
    output_refs = _dedupe_preserve_order(_as_string_list(delivery_data.get("output_refs")))
    blocked_message = str(render_data.get("blocked_message") or "").strip()
    render_summary = str(render_data.get("summary") or "").strip()
    delivery_summary = str(delivery_data.get("summary") or "").strip()

    status = _resolve_status(
        operational_status=operational_status,
        delivery_status=delivery_status,
    )
    summary = _resolve_summary(
        render_summary=render_summary,
        blocked_message=blocked_message,
        delivery_summary=delivery_summary,
    )
    limit_warnings = _resolve_limit_warnings(
        render_contract=render_data,
        delivery_package=delivery_data,
        operational_status=operational_status,
    )

    return OwnerFacingReport(
        tenant_id=tenant_id,
        intake_id=intake_id,
        status=status,
        delivery_status=delivery_status,
        operational_status=operational_status,
        summary=summary,
        blocked_message=blocked_message,
        evidence_used=evidence_used,
        missing_evidence=missing_evidence,
        next_questions=next_questions,
        next_steps=next_steps,
        references=references,
        output_refs=output_refs,
        limit_warnings=limit_warnings,
    )


__all__ = [
    "OwnerFacingReport",
    "STATUS_DELIVERED",
    "STATUS_DELIVERED_CANDIDATE",
    "STATUS_BLOCKED",
    "build_owner_facing_report",
]

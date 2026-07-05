from __future__ import annotations

from typing import Any, Final, Literal, NotRequired, TypedDict

SCHEMA_VERSION: Final[str] = "S1_RUNNER_SHADOW_EVIDENCE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_SHADOW_STATUS: Final[str] = "SHADOW_RUNNER_READY"

RunnerShadowEvidenceStatusV1 = Literal[
    "SHADOW_EVIDENCE_READY",
    "BLOCKED_INVALID_SHADOW_RESULT",
    "BLOCKED_SHADOW_NOT_READY",
    "UNKNOWN",
]


class Service1RunnerShadowEvidenceInputV1(TypedDict):
    shadow_result: dict[str, Any]
    evidence_ref: str
    observed_at: NotRequired[str]
    notes: list[str]


class Service1RunnerShadowEvidenceResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: RunnerShadowEvidenceStatusV1
    blocked_reason: str | None
    evidence_ref: str | None
    observed_at: str | None
    case_id: str | None
    run_id: str | None
    shadow_status: str | None
    shadow_run_authorized: bool
    processed_tool_refs: list[str]
    processed_request_count: int
    runtime_authorized: Literal[False]
    pipeline_called: Literal[False]
    delivery_authorized: Literal[False]
    owner_delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    evidence_packet: dict[str, Any] | None
    notes: list[str]


def build_service_1_runner_shadow_evidence_v1(
    evidence_input: Service1RunnerShadowEvidenceInputV1,
) -> Service1RunnerShadowEvidenceResultV1:
    """Wrap a shadow harness result as structured audit evidence.

    The wrapper is pure and deterministic. It does not read clocks, write files,
    publish delivery, call pipeline, or reach any runtime/LLM/API/storage layer.
    """
    shadow_result = evidence_input.get("shadow_result")
    if not isinstance(shadow_result, dict):
        return _result(
            status="BLOCKED_INVALID_SHADOW_RESULT",
            blocked_reason="shadow_result_must_be_dict",
            notes=["Shadow evidence requires a dict shadow_result."],
        )

    evidence_ref = evidence_input.get("evidence_ref")
    if not isinstance(evidence_ref, str) or not evidence_ref.strip():
        return _result(
            status="BLOCKED_INVALID_SHADOW_RESULT",
            blocked_reason="evidence_ref_required",
            notes=["Shadow evidence requires evidence_ref."],
        )

    if shadow_result.get("status") != READY_SHADOW_STATUS:
        return _result(
            status="BLOCKED_SHADOW_NOT_READY",
            blocked_reason="shadow_result_not_ready",
            evidence_ref=evidence_ref,
            observed_at=evidence_input.get("observed_at"),
            shadow_result=shadow_result,
            notes=["Shadow result must be SHADOW_RUNNER_READY before evidence wrapping."],
        )

    if shadow_result.get("shadow_run_authorized") is not True:
        return _result(
            status="BLOCKED_INVALID_SHADOW_RESULT",
            blocked_reason="shadow_run_authorized_required",
            evidence_ref=evidence_ref,
            observed_at=evidence_input.get("observed_at"),
            shadow_result=shadow_result,
            notes=["Shadow result must have shadow_run_authorized=true."],
        )

    if shadow_result.get("runtime_authorized") is True or shadow_result.get("pipeline_called") is True:
        return _result(
            status="BLOCKED_INVALID_SHADOW_RESULT",
            blocked_reason="shadow_result_must_not_authorize_runtime_or_call_pipeline",
            evidence_ref=evidence_ref,
            observed_at=evidence_input.get("observed_at"),
            shadow_result=shadow_result,
            notes=["Shadow evidence rejects runtime-authorized or pipeline-called results."],
        )

    if shadow_result.get("delivery_authorized") is True or shadow_result.get("owner_delivery_authorized") is True or shadow_result.get("autonomous_delivery_authorized") is True:
        return _result(
            status="BLOCKED_INVALID_SHADOW_RESULT",
            blocked_reason="shadow_result_must_not_authorize_delivery",
            evidence_ref=evidence_ref,
            observed_at=evidence_input.get("observed_at"),
            shadow_result=shadow_result,
            notes=["Shadow evidence rejects delivery-authorized results."],
        )

    processed_requests = shadow_result.get("shadow_processed_requests")
    if not isinstance(processed_requests, list) or not processed_requests:
        return _result(
            status="BLOCKED_INVALID_SHADOW_RESULT",
            blocked_reason="shadow_processed_requests_required",
            evidence_ref=evidence_ref,
            observed_at=evidence_input.get("observed_at"),
            shadow_result=shadow_result,
            notes=["Shadow evidence requires non-empty shadow_processed_requests."],
        )

    processed_tool_refs: list[str] = []
    for request in processed_requests:
        if not isinstance(request, dict):
            return _result(
                status="BLOCKED_INVALID_SHADOW_RESULT",
                blocked_reason="shadow_processed_request_must_be_dict",
                evidence_ref=evidence_ref,
                observed_at=evidence_input.get("observed_at"),
                shadow_result=shadow_result,
                notes=["Each shadow processed request must be a dict."],
            )
        tool_ref = request.get("tool_ref")
        if not isinstance(tool_ref, str) or not tool_ref.strip():
            return _result(
                status="BLOCKED_INVALID_SHADOW_RESULT",
                blocked_reason="shadow_processed_request_tool_ref_required",
                evidence_ref=evidence_ref,
                observed_at=evidence_input.get("observed_at"),
                shadow_result=shadow_result,
                notes=["Each shadow processed request requires tool_ref."],
            )
        processed_tool_refs.append(tool_ref)

    evidence_packet = {
        "evidence_ref": evidence_ref,
        "observed_at": evidence_input.get("observed_at"),
        "case_id": shadow_result.get("case_id"),
        "run_id": shadow_result.get("run_id"),
        "shadow_status": shadow_result.get("status"),
        "processed_tool_refs": list(processed_tool_refs),
        "processed_request_count": len(processed_tool_refs),
        "runtime_authorized": False,
        "pipeline_called": False,
        "delivery_authorized": False,
    }

    return _result(
        status="SHADOW_EVIDENCE_READY",
        blocked_reason=None,
        evidence_ref=evidence_ref,
        observed_at=evidence_input.get("observed_at"),
        shadow_result=shadow_result,
        processed_tool_refs=processed_tool_refs,
        evidence_packet=evidence_packet,
        notes=list(evidence_input.get("notes", [])) + ["Shadow evidence packet created without runtime or delivery authorization."],
    )


def _result(
    *,
    status: RunnerShadowEvidenceStatusV1,
    blocked_reason: str | None,
    evidence_ref: str | None = None,
    observed_at: str | None = None,
    shadow_result: dict[str, Any] | None = None,
    processed_tool_refs: list[str] | None = None,
    evidence_packet: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> Service1RunnerShadowEvidenceResultV1:
    processed_tool_refs = list(processed_tool_refs or [])
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "blocked_reason": blocked_reason,
        "evidence_ref": evidence_ref,
        "observed_at": observed_at,
        "case_id": shadow_result.get("case_id") if isinstance(shadow_result, dict) else None,
        "run_id": shadow_result.get("run_id") if isinstance(shadow_result, dict) else None,
        "shadow_status": shadow_result.get("status") if isinstance(shadow_result, dict) else None,
        "shadow_run_authorized": bool(shadow_result.get("shadow_run_authorized")) if isinstance(shadow_result, dict) else False,
        "processed_tool_refs": processed_tool_refs,
        "processed_request_count": len(processed_tool_refs),
        "runtime_authorized": False,
        "pipeline_called": False,
        "delivery_authorized": False,
        "owner_delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "evidence_packet": evidence_packet,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "READY_SHADOW_STATUS",
    "Service1RunnerShadowEvidenceInputV1",
    "Service1RunnerShadowEvidenceResultV1",
    "build_service_1_runner_shadow_evidence_v1",
]

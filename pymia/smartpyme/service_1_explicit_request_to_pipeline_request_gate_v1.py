from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_EXPLICIT_REQUEST_TO_PIPELINE_REQUEST_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_EXPLICIT_REQUEST_STATUS: Final[str] = "EXPLICIT_REQUEST_CANDIDATE_READY"
FINAL_GATE_CLOSED_STATUS: Final[str] = "CLOSED_NOT_EXECUTABLE"
SOURCE_REQUEST_KIND: Final[str] = "CANDIDATE_ONLY"
PIPELINE_REQUEST_KIND: Final[str] = "PIPELINE_REQUEST_CANDIDATE"

PipelineRequestGateStatusV1 = Literal[
    "PIPELINE_REQUEST_CANDIDATE_READY",
    "NEEDS_FINAL_EXECUTION_AUTHORIZATION",
    "BLOCKED",
    "UNKNOWN",
]

_ALLOWED_TOOL_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
)


class Service1ExplicitRequestToPipelineRequestGateInputV1(TypedDict):
    explicit_request_status: str
    explicit_tool_request_candidate: list[dict[str, Any]]
    allowed_tool_refs: list[str]
    final_execution_gate_status: str
    pipeline_request_policy: str | None


class Service1PipelineToolRequestCandidateV1(TypedDict):
    tool_ref: str
    inputs: dict[str, str]
    source_explicit_request_ref: str
    request_kind: Literal["PIPELINE_REQUEST_CANDIDATE"]
    executable: Literal[False]


class Service1ExplicitRequestToPipelineRequestGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: PipelineRequestGateStatusV1
    pipeline_tool_request_candidate: list[Service1PipelineToolRequestCandidateV1]
    blocked_reason: str | None
    runtime_authorized: Literal[False]
    execution_authorized: Literal[False]
    pipeline_execution_authorized: Literal[False]
    delivery_authorized: Literal[False]
    notes: list[str]


def build_service_1_explicit_request_to_pipeline_request_gate_v1(
    gate_input: Service1ExplicitRequestToPipelineRequestGateInputV1,
) -> Service1ExplicitRequestToPipelineRequestGateResultV1:
    """Translate explicit request candidates into non-executable pipeline request candidates.

    This pure gate does not execute tools, import pipeline runtime, call a runner,
    perform I/O, or authorize delivery. It only reshapes confirmed refs.
    """
    if gate_input.get("explicit_request_status") != READY_EXPLICIT_REQUEST_STATUS:
        return _result(
            status="BLOCKED",
            blocked_reason="explicit_request_status_not_ready",
            notes=["Pipeline request candidates require EXPLICIT_REQUEST_CANDIDATE_READY."],
        )

    if gate_input.get("final_execution_gate_status") != FINAL_GATE_CLOSED_STATUS:
        return _result(
            status="NEEDS_FINAL_EXECUTION_AUTHORIZATION",
            blocked_reason="final_execution_gate_must_remain_closed_not_executable",
            notes=["Final execution gate is not closed in non-executable mode."],
        )

    explicit_candidates = list(gate_input.get("explicit_tool_request_candidate", []))
    if not explicit_candidates:
        return _result(
            status="UNKNOWN",
            blocked_reason="missing_explicit_tool_request_candidate",
            notes=["No explicit_tool_request_candidate entries were provided."],
        )

    allowed_tool_refs = set(str(ref) for ref in gate_input.get("allowed_tool_refs", []))
    pipeline_candidates: list[Service1PipelineToolRequestCandidateV1] = []

    for candidate in explicit_candidates:
        tool_ref = candidate.get("tool_ref")
        if not isinstance(tool_ref, str) or not tool_ref.strip():
            return _result(
                status="UNKNOWN",
                blocked_reason="missing_candidate_tool_ref",
                notes=["Every explicit request candidate requires a tool_ref."],
            )

        if tool_ref not in _ALLOWED_TOOL_REFS or tool_ref not in allowed_tool_refs:
            return _result(
                status="BLOCKED",
                blocked_reason="candidate_tool_ref_not_allowlisted",
                notes=[f"Candidate tool ref is not allowlisted: {tool_ref}"],
            )

        if candidate.get("request_kind") != SOURCE_REQUEST_KIND:
            return _result(
                status="BLOCKED",
                blocked_reason="request_kind_not_candidate_only",
                notes=["Only CANDIDATE_ONLY explicit requests can be translated."],
            )

        if candidate.get("executable") is not False:
            return _result(
                status="BLOCKED",
                blocked_reason="explicit_request_candidate_must_not_be_executable",
                notes=["Executable explicit requests are outside this gate."],
            )

        input_refs = _input_refs(candidate)
        if not input_refs:
            return _result(
                status="UNKNOWN",
                blocked_reason="missing_input_refs",
                notes=["Pipeline request candidates require non-empty input refs."],
            )

        pipeline_candidates.append(
            {
                "tool_ref": tool_ref,
                "inputs": input_refs,
                "source_explicit_request_ref": _source_explicit_request_ref(tool_ref=tool_ref, candidate=candidate),
                "request_kind": PIPELINE_REQUEST_KIND,
                "executable": False,
            }
        )

    return _result(
        status="PIPELINE_REQUEST_CANDIDATE_READY",
        pipeline_tool_request_candidate=pipeline_candidates,
        notes=["Pipeline request candidates created as non-executable refs only."],
    )


def _input_refs(candidate: dict[str, Any]) -> dict[str, str]:
    raw_refs = candidate.get("input_refs", {})
    if not isinstance(raw_refs, dict):
        return {}
    return {str(key): str(value) for key, value in raw_refs.items() if _has_ref(str(value))}


def _source_explicit_request_ref(*, tool_ref: str, candidate: dict[str, Any]) -> str:
    explicit_ref = candidate.get("explicit_request_ref") or candidate.get("source_explicit_request_ref")
    if isinstance(explicit_ref, str) and explicit_ref.strip():
        return explicit_ref
    source_plan_ref = candidate.get("source_plan_ref")
    if isinstance(source_plan_ref, str) and source_plan_ref.strip():
        return f"explicit_tool_request_candidate:{source_plan_ref}"
    return f"explicit_tool_request_candidate:{tool_ref}"


def _result(
    *,
    status: PipelineRequestGateStatusV1,
    pipeline_tool_request_candidate: list[Service1PipelineToolRequestCandidateV1] | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1ExplicitRequestToPipelineRequestGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "pipeline_tool_request_candidate": list(pipeline_tool_request_candidate or []),
        "blocked_reason": blocked_reason,
        "runtime_authorized": False,
        "execution_authorized": False,
        "pipeline_execution_authorized": False,
        "delivery_authorized": False,
        "notes": list(notes or []),
    }


def _has_ref(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "SCHEMA_VERSION",
    "Service1ExplicitRequestToPipelineRequestGateInputV1",
    "Service1PipelineToolRequestCandidateV1",
    "Service1ExplicitRequestToPipelineRequestGateResultV1",
    "build_service_1_explicit_request_to_pipeline_request_gate_v1",
]

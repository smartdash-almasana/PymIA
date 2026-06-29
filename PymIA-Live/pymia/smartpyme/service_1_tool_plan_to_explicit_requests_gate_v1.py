from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_TOOL_PLAN_TO_EXPLICIT_REQUESTS_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_TOOL_PLAN_STATUS: Final[str] = "TOOL_PLAN_CANDIDATE_READY"
AUTHORIZED_STATUS: Final[str] = "AUTHORIZED_FOR_EXPLICIT_REQUEST_CANDIDATE"
REQUEST_KIND: Final[str] = "CANDIDATE_ONLY"

GateStatusV1 = Literal[
    "EXPLICIT_REQUEST_CANDIDATE_READY",
    "NEEDS_AUTHORIZATION",
    "NEEDS_MAPPING_CONFIRMATION",
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


class Service1ToolPlanToExplicitRequestsGateInputV1(TypedDict):
    tool_plan_status: str
    candidate_tool_refs: list[str]
    tool_plan_candidate: list[dict[str, Any]]
    allowed_tool_refs: list[str]
    authorization_status: str
    confirmed_input_mapping_refs: dict[str, dict[str, str]]
    execution_policy: str | None


class Service1ExplicitToolRequestCandidateV1(TypedDict):
    tool_ref: str
    input_refs: dict[str, str]
    source_plan_ref: str
    request_kind: Literal["CANDIDATE_ONLY"]
    executable: Literal[False]


class Service1ToolPlanToExplicitRequestsGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: GateStatusV1
    explicit_tool_request_candidate: list[Service1ExplicitToolRequestCandidateV1]
    blocked_reason: str | None
    missing_confirmation_refs: list[str]
    runtime_authorized: Literal[False]
    execution_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    delivery_authorized: Literal[False]
    notes: list[str]


def build_service_1_tool_plan_to_explicit_requests_gate_v1(
    gate_input: Service1ToolPlanToExplicitRequestsGateInputV1,
) -> Service1ToolPlanToExplicitRequestsGateResultV1:
    """Translate a ready tool plan into explicit request candidates.

    The output remains non-executable. This pure gate does not execute tools,
    call pipelines, perform I/O, build final requests, or authorize delivery.
    """
    if gate_input.get("tool_plan_status") != READY_TOOL_PLAN_STATUS:
        return _result(
            status="BLOCKED",
            blocked_reason="tool_plan_status_not_ready",
            notes=["Explicit request candidates require TOOL_PLAN_CANDIDATE_READY."],
        )

    if gate_input.get("authorization_status") != AUTHORIZED_STATUS:
        return _result(
            status="NEEDS_AUTHORIZATION",
            blocked_reason="authorization_required_for_explicit_request_candidate",
            notes=["Authorization gate did not allow explicit request candidate creation."],
        )

    candidate_tool_refs = [str(ref) for ref in gate_input.get("candidate_tool_refs", [])]
    if not candidate_tool_refs:
        return _result(
            status="UNKNOWN",
            blocked_reason="missing_candidate_tool_refs",
            notes=["No candidate_tool_refs were provided."],
        )

    allowed_input_refs = set(str(ref) for ref in gate_input.get("allowed_tool_refs", []))
    for tool_ref in candidate_tool_refs:
        if tool_ref not in _ALLOWED_TOOL_REFS or tool_ref not in allowed_input_refs:
            return _result(
                status="BLOCKED",
                blocked_reason="candidate_tool_ref_not_allowlisted",
                notes=[f"Candidate tool ref is not allowlisted: {tool_ref}"],
            )

    plans_by_tool_ref = _plans_by_tool_ref(gate_input.get("tool_plan_candidate", []))
    confirmed_mapping_refs = {
        str(tool_ref): dict(input_refs)
        for tool_ref, input_refs in gate_input.get("confirmed_input_mapping_refs", {}).items()
    }

    missing_confirmation_refs: list[str] = []
    candidates: list[Service1ExplicitToolRequestCandidateV1] = []
    for tool_ref in candidate_tool_refs:
        plan = plans_by_tool_ref.get(tool_ref)
        if plan is None:
            missing_confirmation_refs.append(f"{tool_ref}:source_plan")
            continue

        plan_input_refs = _input_refs_from_plan(plan)
        confirmed_input_refs = confirmed_mapping_refs.get(tool_ref, {})
        if not confirmed_input_refs:
            missing_confirmation_refs.append(f"{tool_ref}:input_mapping_refs")
            continue

        missing_keys = [key for key in plan_input_refs if key not in confirmed_input_refs or not _has_ref(confirmed_input_refs.get(key))]
        mismatched_keys = [
            key
            for key, ref in plan_input_refs.items()
            if key in confirmed_input_refs and _has_ref(confirmed_input_refs.get(key)) and confirmed_input_refs[key] != ref
        ]
        for key in missing_keys:
            missing_confirmation_refs.append(f"{tool_ref}:{key}")
        for key in mismatched_keys:
            missing_confirmation_refs.append(f"{tool_ref}:{key}:mismatch")
        if missing_keys or mismatched_keys:
            continue

        candidates.append(
            {
                "tool_ref": tool_ref,
                "input_refs": dict(confirmed_input_refs),
                "source_plan_ref": _source_plan_ref(tool_ref=tool_ref, plan=plan),
                "request_kind": REQUEST_KIND,
                "executable": False,
            }
        )

    if missing_confirmation_refs:
        return _result(
            status="NEEDS_MAPPING_CONFIRMATION",
            missing_confirmation_refs=missing_confirmation_refs,
            explicit_tool_request_candidate=candidates,
            blocked_reason="input_mapping_confirmation_required",
            notes=["All plan input refs must be confirmed before creating explicit request candidates."],
        )

    return _result(
        status="EXPLICIT_REQUEST_CANDIDATE_READY",
        explicit_tool_request_candidate=candidates,
        notes=["Explicit request candidates created as CANDIDATE_ONLY and executable=false."],
    )


def _plans_by_tool_ref(tool_plan_candidate: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    plans: dict[str, dict[str, Any]] = {}
    for plan in tool_plan_candidate:
        tool_ref = plan.get("tool_ref")
        if isinstance(tool_ref, str) and tool_ref.strip():
            plans[tool_ref] = dict(plan)
    return plans


def _input_refs_from_plan(plan: dict[str, Any]) -> dict[str, str]:
    raw_refs = plan.get("input_mapping_refs", {})
    if not isinstance(raw_refs, dict):
        return {}
    return {str(key): str(value) for key, value in raw_refs.items() if _has_ref(str(value))}


def _source_plan_ref(*, tool_ref: str, plan: dict[str, Any]) -> str:
    explicit_ref = plan.get("plan_ref") or plan.get("source_plan_ref")
    if isinstance(explicit_ref, str) and explicit_ref.strip():
        return explicit_ref
    return f"tool_plan_candidate:{tool_ref}"


def _result(
    *,
    status: GateStatusV1,
    explicit_tool_request_candidate: list[Service1ExplicitToolRequestCandidateV1] | None = None,
    blocked_reason: str | None = None,
    missing_confirmation_refs: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1ToolPlanToExplicitRequestsGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "explicit_tool_request_candidate": list(explicit_tool_request_candidate or []),
        "blocked_reason": blocked_reason,
        "missing_confirmation_refs": list(missing_confirmation_refs or []),
        "runtime_authorized": False,
        "execution_authorized": False,
        "pipeline_authorized": False,
        "delivery_authorized": False,
        "notes": list(notes or []),
    }


def _has_ref(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "SCHEMA_VERSION",
    "Service1ToolPlanToExplicitRequestsGateInputV1",
    "Service1ExplicitToolRequestCandidateV1",
    "Service1ToolPlanToExplicitRequestsGateResultV1",
    "build_service_1_tool_plan_to_explicit_requests_gate_v1",
]

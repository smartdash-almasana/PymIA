from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_AUTONOMOUS_DELIVERY_RELEASE_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
PIPELINE_COMPLETED_STATUS: Final[str] = "PIPELINE_RUN_COMPLETED"
DELIVERY_POLICY_ALLOWED_STATUS: Final[str] = "DELIVERY_POLICY_CANDIDATE_ALLOWED"
RELEASE_KIND: Final[str] = "DELIVERY_RELEASE_CANDIDATE"

AutonomousDeliveryReleaseGateStatusV1 = Literal[
    "DELIVERY_RELEASE_CANDIDATE_READY",
    "BLOCKED_PIPELINE_NOT_COMPLETED",
    "BLOCKED_MISSING_ARTIFACTS",
    "BLOCKED_PIPELINE_ERRORS",
    "BLOCKED_DELIVERY_POLICY",
    "UNKNOWN",
]


class Service1AutonomousDeliveryReleaseGateInputV1(TypedDict):
    pipeline_run_status: str
    pipeline_run_result: dict[str, Any]
    expected_artifacts: list[str]
    produced_artifacts: list[str]
    pipeline_errors: list[str]
    pipeline_warnings: list[str]
    delivery_policy_status: str
    notes: list[str]


class Service1DeliveryReleaseCandidateV1(TypedDict):
    source_pipeline_run_ref: str
    artifact_refs: list[str]
    warning_refs: list[str]
    release_kind: Literal["DELIVERY_RELEASE_CANDIDATE"]
    publishable: Literal[False]
    signoff_required: Literal[True]


class Service1AutonomousDeliveryReleaseGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: AutonomousDeliveryReleaseGateStatusV1
    delivery_release_candidate: Service1DeliveryReleaseCandidateV1 | None
    blocked_reason: str | None
    missing_artifacts: list[str]
    delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    release_authorized: Literal[False]
    signoff_authorized: Literal[False]
    notes: list[str]


def build_service_1_autonomous_delivery_release_gate_v1(
    gate_input: Service1AutonomousDeliveryReleaseGateInputV1,
) -> Service1AutonomousDeliveryReleaseGateResultV1:
    """Build a non-publishable delivery release candidate from a completed run.

    This pure gate only inspects declared status, policy, warnings, errors, and
    artifact references. It does not execute runners, create files, copy files,
    publish outputs, close cases, or produce final approval.
    """
    if gate_input.get("pipeline_run_status") != PIPELINE_COMPLETED_STATUS:
        return _result(
            status="BLOCKED_PIPELINE_NOT_COMPLETED",
            blocked_reason="pipeline_run_status_not_completed",
            notes=["Delivery release candidate requires PIPELINE_RUN_COMPLETED."],
        )

    pipeline_errors = _clean_refs(gate_input.get("pipeline_errors", []))
    if pipeline_errors:
        return _result(
            status="BLOCKED_PIPELINE_ERRORS",
            blocked_reason="pipeline_errors_present",
            notes=["Pipeline errors block delivery release candidate creation."],
        )

    if gate_input.get("delivery_policy_status") != DELIVERY_POLICY_ALLOWED_STATUS:
        return _result(
            status="BLOCKED_DELIVERY_POLICY",
            blocked_reason="delivery_policy_not_allowed",
            notes=["Delivery policy did not allow candidate creation."],
        )

    expected_artifacts = _clean_refs(gate_input.get("expected_artifacts", []))
    if not expected_artifacts:
        return _result(
            status="UNKNOWN",
            blocked_reason="expected_artifacts_required",
            notes=["Expected artifacts are required before release candidate creation."],
        )

    produced_artifacts = _clean_refs(gate_input.get("produced_artifacts", []))
    missing_artifacts = [artifact for artifact in expected_artifacts if artifact not in set(produced_artifacts)]
    if missing_artifacts:
        return _result(
            status="BLOCKED_MISSING_ARTIFACTS",
            blocked_reason="missing_expected_artifacts",
            missing_artifacts=missing_artifacts,
            notes=["One or more expected artifacts were not produced."],
        )

    pipeline_run_result = dict(gate_input.get("pipeline_run_result", {}))
    candidate: Service1DeliveryReleaseCandidateV1 = {
        "source_pipeline_run_ref": _source_pipeline_run_ref(pipeline_run_result),
        "artifact_refs": list(expected_artifacts),
        "warning_refs": _clean_refs(gate_input.get("pipeline_warnings", [])),
        "release_kind": RELEASE_KIND,
        "publishable": False,
        "signoff_required": True,
    }

    return _result(
        status="DELIVERY_RELEASE_CANDIDATE_READY",
        delivery_release_candidate=candidate,
        notes=["Delivery release candidate created as non-publishable and signoff-required."],
    )


def _source_pipeline_run_ref(pipeline_run_result: dict[str, Any]) -> str:
    for key in ("pipeline_run_ref", "run_id", "case_id"):
        value = pipeline_run_result.get(key)
        if isinstance(value, str) and value.strip():
            return value
    schema_version = pipeline_run_result.get("schema_version")
    if isinstance(schema_version, str) and schema_version.strip():
        return f"pipeline_run:{schema_version}"
    return "pipeline_run:unknown"


def _clean_refs(values: list[str] | object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if isinstance(value, str) and value.strip()]


def _result(
    *,
    status: AutonomousDeliveryReleaseGateStatusV1,
    delivery_release_candidate: Service1DeliveryReleaseCandidateV1 | None = None,
    blocked_reason: str | None = None,
    missing_artifacts: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1AutonomousDeliveryReleaseGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "delivery_release_candidate": delivery_release_candidate,
        "blocked_reason": blocked_reason,
        "missing_artifacts": list(missing_artifacts or []),
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "release_authorized": False,
        "signoff_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "PIPELINE_COMPLETED_STATUS",
    "DELIVERY_POLICY_ALLOWED_STATUS",
    "RELEASE_KIND",
    "Service1AutonomousDeliveryReleaseGateInputV1",
    "Service1DeliveryReleaseCandidateV1",
    "Service1AutonomousDeliveryReleaseGateResultV1",
    "build_service_1_autonomous_delivery_release_gate_v1",
]

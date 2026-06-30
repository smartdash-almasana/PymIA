from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_FINAL_OWNER_RELEASE_DECISION_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
DECISION_GATE_KIND: Final[str] = "FINAL_OWNER_RELEASE_CANDIDATE"
HUMAN_REVIEW_INTEGRATION_KIND: Final[str] = "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE"
DELIVERY_RELEASE_KIND: Final[str] = "DELIVERY_RELEASE_CANDIDATE"
OWNER_PACKET_KIND: Final[str] = "OWNER_DELIVERY_PACKET_CANDIDATE"
SIGNED_OFF_STATUS: Final[str] = "SIGNED_OFF_FOR_DELIVERY"
REJECTED_STATUS: Final[str] = "REJECTED"
QA_GATE_TYPE: Final[str] = "QA_DELIVERY_GATE"

FinalOwnerReleaseDecisionStatusV1 = Literal[
    "FINAL_OWNER_RELEASE_CANDIDATE_READY",
    "BLOCKED_INVALID_HUMAN_REVIEW_INTEGRATION",
    "BLOCKED_MISSING_SIGNOFF",
    "BLOCKED_REJECTED_SIGNOFF",
    "BLOCKED_INVALID_QA",
    "BLOCKED_INVALID_DELIVERY_RELEASE",
    "BLOCKED_INVALID_OWNER_PACKET",
    "BLOCKED_UNSAFE_RELEASE_FLAGS",
    "NEEDS_SIGNOFF",
    "NEEDS_QA",
    "UNKNOWN",
]


class Service1FinalOwnerReleaseDecisionGateInputV1(TypedDict):
    human_review_release_integration_candidate: dict[str, object] | None
    human_review_signoff_result: dict[str, object] | None
    qa_delivery_gate_result: dict[str, object] | None
    delivery_release_candidate: dict[str, object] | None
    owner_delivery_packet_candidate: dict[str, object] | None
    notes: list[str]


class Service1FinalOwnerReleaseAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["FINAL_OWNER_RELEASE_CANDIDATE"]
    source_slice_ref: str
    audit_log_ref_candidate: str
    audit_event_ref_candidate: str
    append_operation: Literal["APPEND_EVENT"]
    event_summary: str
    source_context_refs: dict[str, str]
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1FinalOwnerReleaseCandidateV1(TypedDict):
    candidate_kind: Literal["FINAL_OWNER_RELEASE_CANDIDATE"]
    service_name: Literal["SERVICE_1"]
    source_pipeline_run_ref: str
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    artifact_refs: list[str]
    warning_refs: list[str]
    owner_facing_summary: str
    signoff_status: str
    signoff_decision: str
    qa_gate_status: str
    qa_checks_passed: int
    qa_checks_total: int
    delivery_status_before_signoff: str | None
    delivery_status_after_signoff: str
    publishable: Literal[False]
    final_release_authorized: Literal[True]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    audit_event_candidate: Service1FinalOwnerReleaseAuditEventCandidateV1
    warnings: list[str]
    errors: list[str]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    runtime_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


class Service1FinalOwnerReleaseDecisionGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: FinalOwnerReleaseDecisionStatusV1
    final_owner_release_candidate: Service1FinalOwnerReleaseCandidateV1 | None
    blocked_reason: str | None
    audit_event_candidate: Service1FinalOwnerReleaseAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    runtime_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]
    notes: list[str]


def build_service_1_final_owner_release_decision_gate_v1(
    gate_input: Service1FinalOwnerReleaseDecisionGateInputV1,
) -> Service1FinalOwnerReleaseDecisionGateResultV1:
    """Decide if a delivery may become a pure final owner release candidate."""
    integration_candidate = gate_input.get("human_review_release_integration_candidate")
    if not isinstance(integration_candidate, dict) or not integration_candidate:
        return _result(
            status="BLOCKED_INVALID_HUMAN_REVIEW_INTEGRATION",
            blocked_reason="human_review_release_integration_candidate_required",
            errors=["human_review_release_integration_candidate_required"],
            notes=_notes(gate_input.get("notes"), "Final owner release decision requires human_review_release_integration_candidate."),
        )

    unsafe_integration_reason = _unsafe_release_reason(integration_candidate)
    if unsafe_integration_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_RELEASE_FLAGS",
            blocked_reason=unsafe_integration_reason,
            errors=[unsafe_integration_reason],
            notes=_notes(gate_input.get("notes"), "Unsafe release flags are blocked."),
        )

    integration_validation_reason = _validate_human_review_integration_candidate(integration_candidate)
    if integration_validation_reason is not None:
        return _result(
            status="BLOCKED_INVALID_HUMAN_REVIEW_INTEGRATION",
            blocked_reason=integration_validation_reason,
            errors=[integration_validation_reason],
            notes=_notes(gate_input.get("notes"), "Human review integration candidate is invalid."),
        )

    delivery_release_candidate = gate_input.get("delivery_release_candidate")
    if not isinstance(delivery_release_candidate, dict) or not delivery_release_candidate:
        return _result(
            status="BLOCKED_INVALID_DELIVERY_RELEASE",
            blocked_reason="delivery_release_candidate_required",
            errors=["delivery_release_candidate_required"],
            notes=_notes(gate_input.get("notes"), "Final owner release decision requires delivery_release_candidate."),
        )
    unsafe_delivery_reason = _unsafe_release_reason(delivery_release_candidate)
    if unsafe_delivery_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_RELEASE_FLAGS",
            blocked_reason=unsafe_delivery_reason,
            errors=[unsafe_delivery_reason],
            notes=_notes(gate_input.get("notes"), "Unsafe release flags are blocked."),
        )
    delivery_release_validation = _validate_delivery_release_candidate(
        delivery_release_candidate=delivery_release_candidate,
        integration_candidate=integration_candidate,
    )
    if delivery_release_validation is not None:
        return _result(
            status="BLOCKED_INVALID_DELIVERY_RELEASE",
            blocked_reason=delivery_release_validation,
            errors=[delivery_release_validation],
            notes=_notes(gate_input.get("notes"), "Delivery release candidate is invalid."),
        )

    owner_delivery_packet_candidate = gate_input.get("owner_delivery_packet_candidate")
    if not isinstance(owner_delivery_packet_candidate, dict) or not owner_delivery_packet_candidate:
        return _result(
            status="BLOCKED_INVALID_OWNER_PACKET",
            blocked_reason="owner_delivery_packet_candidate_required",
            errors=["owner_delivery_packet_candidate_required"],
            notes=_notes(gate_input.get("notes"), "Final owner release decision requires owner_delivery_packet_candidate."),
        )
    unsafe_packet_reason = _unsafe_release_reason(owner_delivery_packet_candidate)
    if unsafe_packet_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_RELEASE_FLAGS",
            blocked_reason=unsafe_packet_reason,
            errors=[unsafe_packet_reason],
            notes=_notes(gate_input.get("notes"), "Unsafe release flags are blocked."),
        )
    owner_packet_validation = _validate_owner_packet_candidate(
        owner_delivery_packet_candidate=owner_delivery_packet_candidate,
        integration_candidate=integration_candidate,
    )
    if owner_packet_validation is not None:
        return _result(
            status="BLOCKED_INVALID_OWNER_PACKET",
            blocked_reason=owner_packet_validation,
            errors=[owner_packet_validation],
            notes=_notes(gate_input.get("notes"), "Owner delivery packet candidate is invalid."),
        )

    source_pipeline_run_ref = str(integration_candidate["source_pipeline_run_ref"]).strip()
    if source_pipeline_run_ref == "pipeline_run:unknown":
        return _result(
            status="UNKNOWN",
            blocked_reason="source_pipeline_run_ref_unknown",
            errors=["source_pipeline_run_ref_unknown"],
            notes=_notes(gate_input.get("notes"), "The source pipeline run cannot be classified safely."),
        )

    signoff_result = gate_input.get("human_review_signoff_result")
    if signoff_result is None:
        return _result(
            status="BLOCKED_MISSING_SIGNOFF",
            blocked_reason="human_review_signoff_result_required",
            errors=["human_review_signoff_result_required"],
            notes=_notes(gate_input.get("notes"), "A human review signoff result is required."),
        )
    if not isinstance(signoff_result, dict) or not signoff_result:
        return _result(
            status="BLOCKED_MISSING_SIGNOFF",
            blocked_reason="human_review_signoff_result_invalid",
            errors=["human_review_signoff_result_invalid"],
            notes=_notes(gate_input.get("notes"), "The human review signoff result is invalid."),
        )
    signoff_validation = _validate_signoff_result(signoff_result)
    if signoff_validation is not None:
        status, reason = signoff_validation
        return _result(
            status=status,
            blocked_reason=reason,
            errors=[reason],
            notes=_notes(gate_input.get("notes"), "The human review signoff result is not ready for final owner release."),
        )

    qa_delivery_gate_result = gate_input.get("qa_delivery_gate_result")
    if qa_delivery_gate_result is None:
        return _result(
            status="NEEDS_QA",
            blocked_reason="qa_delivery_gate_result_required",
            errors=["qa_delivery_gate_result_required"],
            notes=_notes(gate_input.get("notes"), "A QA delivery gate result is required."),
        )
    if not isinstance(qa_delivery_gate_result, dict) or not qa_delivery_gate_result:
        return _result(
            status="BLOCKED_INVALID_QA",
            blocked_reason="qa_delivery_gate_result_invalid",
            errors=["qa_delivery_gate_result_invalid"],
            notes=_notes(gate_input.get("notes"), "The QA delivery gate result is invalid."),
        )
    qa_validation = _validate_qa_delivery_gate_result(qa_delivery_gate_result)
    if qa_validation is not None:
        status, reason = qa_validation
        return _result(
            status=status,
            blocked_reason=reason,
            errors=[reason],
            notes=_notes(gate_input.get("notes"), "The QA delivery gate result is not ready for final owner release."),
        )

    audit_event_candidate = _audit_event_candidate(
        owner_ref=str(integration_candidate["owner_ref"]).strip(),
        case_ref=str(integration_candidate["case_ref"]).strip(),
        session_ref=str(integration_candidate["session_ref"]).strip(),
        source_pipeline_run_ref=source_pipeline_run_ref,
        tenant_ref=str(integration_candidate["tenant_ref"]).strip(),
    )
    candidate: Service1FinalOwnerReleaseCandidateV1 = {
        "candidate_kind": DECISION_GATE_KIND,
        "service_name": SERVICE_NAME,
        "source_pipeline_run_ref": source_pipeline_run_ref,
        "tenant_ref": str(integration_candidate["tenant_ref"]).strip(),
        "owner_ref": str(integration_candidate["owner_ref"]).strip(),
        "case_ref": str(integration_candidate["case_ref"]).strip(),
        "session_ref": str(integration_candidate["session_ref"]).strip(),
        "artifact_refs": _clean_refs(integration_candidate.get("artifact_refs")),
        "warning_refs": _clean_refs(integration_candidate.get("warning_refs")),
        "owner_facing_summary": str(integration_candidate["owner_facing_summary"]).strip(),
        "signoff_status": str(signoff_result["status"]).strip(),
        "signoff_decision": str(signoff_result["decision"]).strip(),
        "qa_gate_status": str(qa_delivery_gate_result["status"]).strip(),
        "qa_checks_passed": int(qa_delivery_gate_result["checks_passed"]),
        "qa_checks_total": int(qa_delivery_gate_result["checks_total"]),
        "delivery_status_before_signoff": _clean_optional_ref(signoff_result.get("delivery_status_before")),
        "delivery_status_after_signoff": str(signoff_result["delivery_status_after"]).strip(),
        "publishable": False,
        "final_release_authorized": True,
        "publish_executed": False,
        "notification_sent": False,
        "audit_event_candidate": audit_event_candidate,
        "warnings": [],
        "errors": [],
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }
    return _result(
        status="FINAL_OWNER_RELEASE_CANDIDATE_READY",
        final_owner_release_candidate=candidate,
        audit_event_candidate=audit_event_candidate,
        notes=_notes(
            gate_input.get("notes"),
            "Final owner release candidate created as pure data only; no publish, send, notification, or runtime action was executed.",
        ),
    )


def _validate_human_review_integration_candidate(candidate: dict[str, object]) -> str | None:
    if candidate.get("gate_kind") != HUMAN_REVIEW_INTEGRATION_KIND:
        return "gate_kind_must_be_human_review_release_integration_candidate"
    if candidate.get("candidate_status") != "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_READY":
        return "candidate_status_must_be_ready"
    if candidate.get("status") != "PENDING_HUMAN_REVIEW":
        return "status_must_be_pending_human_review"
    if candidate.get("service_name") != SERVICE_NAME:
        return "service_name_must_be_service_1"
    if _clean_required_ref(candidate.get("source_pipeline_run_ref")) is None:
        return "source_pipeline_run_ref_required"
    if _clean_required_ref(candidate.get("tenant_ref")) is None:
        return "tenant_ref_required"
    if _clean_required_ref(candidate.get("owner_ref")) is None:
        return "owner_ref_required"
    if _clean_required_ref(candidate.get("case_ref")) is None:
        return "case_ref_required"
    if _clean_required_ref(candidate.get("session_ref")) is None:
        return "session_ref_required"
    if not _clean_refs(candidate.get("artifact_refs")):
        return "artifact_refs_required"
    if _clean_required_ref(candidate.get("owner_facing_summary")) is None:
        return "owner_facing_summary_required"
    if candidate.get("human_review_required") is not True:
        return "human_review_required_must_be_true"
    if candidate.get("decision_required_before_client_use") is not True:
        return "decision_required_before_client_use_must_be_true"
    if candidate.get("publishable") is not False:
        return "publishable_must_be_false"
    if candidate.get("signoff_required") is not True:
        return "signoff_required_must_be_true"
    if candidate.get("final_release_authorized") is not False:
        return "final_release_authorized_must_be_false_before_signoff"
    return None


def _validate_delivery_release_candidate(
    *,
    delivery_release_candidate: dict[str, object],
    integration_candidate: dict[str, object],
) -> str | None:
    if delivery_release_candidate.get("release_kind") != DELIVERY_RELEASE_KIND:
        return "release_kind_must_be_delivery_release_candidate"
    if _clean_required_ref(delivery_release_candidate.get("source_pipeline_run_ref")) != _clean_required_ref(
        integration_candidate.get("source_pipeline_run_ref")
    ):
        return "source_pipeline_run_ref_must_match_human_review_integration"
    if _clean_refs(delivery_release_candidate.get("artifact_refs")) != _clean_refs(integration_candidate.get("artifact_refs")):
        return "artifact_refs_must_match_human_review_integration"
    if delivery_release_candidate.get("signoff_required") is not True:
        return "signoff_required_must_be_true"
    if delivery_release_candidate.get("publishable") is not False:
        return "publishable_must_be_false"
    return None


def _validate_owner_packet_candidate(
    *,
    owner_delivery_packet_candidate: dict[str, object],
    integration_candidate: dict[str, object],
) -> str | None:
    if owner_delivery_packet_candidate.get("packet_kind") != OWNER_PACKET_KIND:
        return "packet_kind_must_be_owner_delivery_packet_candidate"
    if _clean_required_ref(owner_delivery_packet_candidate.get("source_pipeline_run_ref")) != _clean_required_ref(
        integration_candidate.get("source_pipeline_run_ref")
    ):
        return "source_pipeline_run_ref_must_match_human_review_integration"
    if _clean_refs(owner_delivery_packet_candidate.get("artifact_refs")) != _clean_refs(integration_candidate.get("artifact_refs")):
        return "artifact_refs_must_match_human_review_integration"
    if _clean_required_ref(owner_delivery_packet_candidate.get("owner_facing_summary")) != _clean_required_ref(
        integration_candidate.get("owner_facing_summary")
    ):
        return "owner_facing_summary_must_match_human_review_integration"
    if owner_delivery_packet_candidate.get("publishable") is not False:
        return "publishable_must_be_false"
    if owner_delivery_packet_candidate.get("signoff_required") is not True:
        return "signoff_required_must_be_true"
    return None


def _validate_signoff_result(
    signoff_result: dict[str, object],
) -> tuple[FinalOwnerReleaseDecisionStatusV1, str] | None:
    if signoff_result.get("service_name") != SERVICE_NAME:
        return ("BLOCKED_MISSING_SIGNOFF", "signoff_service_name_must_be_service_1")
    if _clean_required_ref(signoff_result.get("signoff_type")) is None:
        return ("BLOCKED_MISSING_SIGNOFF", "signoff_type_required")
    if signoff_result.get("runtime_authorized") is not False:
        return ("BLOCKED_UNSAFE_RELEASE_FLAGS", "runtime_authorized_must_be_false")
    if signoff_result.get("human_review_required") is not True:
        return ("BLOCKED_MISSING_SIGNOFF", "human_review_required_must_be_true")
    status = _clean_required_ref(signoff_result.get("status"))
    if status is None:
        return ("BLOCKED_MISSING_SIGNOFF", "signoff_status_required")
    if status == REJECTED_STATUS:
        return ("BLOCKED_REJECTED_SIGNOFF", "signoff_result_rejected")
    if status in {"NEEDS_CORRECTION", "BLOCKED"}:
        return ("NEEDS_SIGNOFF", "signoff_not_approved_for_delivery")
    if status != SIGNED_OFF_STATUS:
        return ("BLOCKED_MISSING_SIGNOFF", "signoff_status_not_supported")
    if signoff_result.get("delivery_allowed_after_signoff") is not True:
        return ("NEEDS_SIGNOFF", "delivery_allowed_after_signoff_must_be_true")
    if _clean_required_ref(signoff_result.get("delivery_status_after")) != "APPROVED_FOR_HUMAN_SUPERVISED_DELIVERY":
        return ("NEEDS_SIGNOFF", "delivery_status_after_must_be_human_supervised_delivery")
    return None


def _validate_qa_delivery_gate_result(
    qa_delivery_gate_result: dict[str, object],
) -> tuple[FinalOwnerReleaseDecisionStatusV1, str] | None:
    if qa_delivery_gate_result.get("service_name") != SERVICE_NAME:
        return ("BLOCKED_INVALID_QA", "qa_service_name_must_be_service_1")
    if qa_delivery_gate_result.get("gate_type") != QA_GATE_TYPE:
        return ("BLOCKED_INVALID_QA", "qa_gate_type_must_be_qa_delivery_gate")
    if qa_delivery_gate_result.get("runtime_authorized") is not False:
        return ("BLOCKED_UNSAFE_RELEASE_FLAGS", "runtime_authorized_must_be_false")
    status = _clean_required_ref(qa_delivery_gate_result.get("status"))
    if status is None:
        return ("BLOCKED_INVALID_QA", "qa_status_required")
    checks_passed = qa_delivery_gate_result.get("checks_passed")
    checks_total = qa_delivery_gate_result.get("checks_total")
    if not isinstance(checks_passed, int) or not isinstance(checks_total, int):
        return ("BLOCKED_INVALID_QA", "qa_checks_summary_invalid")
    if status == "BLOCKED":
        return ("NEEDS_QA", "qa_delivery_gate_blocked")
    if status != "PASS":
        return ("BLOCKED_INVALID_QA", "qa_status_not_supported")
    if checks_total <= 0 or checks_passed < 0 or checks_passed > checks_total:
        return ("BLOCKED_INVALID_QA", "qa_checks_summary_invalid")
    return None


def _unsafe_release_reason(candidate: dict[str, object]) -> str | None:
    for flag_name in (
        "publish_executed",
        "notification_sent",
        "api_exposed",
        "storage_write_authorized",
        "db_authorized",
        "worker_authorized",
        "queue_authorized",
        "runtime_authorized",
        "mutation_authorized",
        "llm_authorized",
        "publish_authorized",
    ):
        if flag_name in candidate and candidate.get(flag_name) is not False:
            return f"{flag_name}_must_be_false"
    return None


def _audit_event_candidate(
    *,
    owner_ref: str,
    case_ref: str,
    session_ref: str,
    source_pipeline_run_ref: str,
    tenant_ref: str,
) -> Service1FinalOwnerReleaseAuditEventCandidateV1:
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "FINAL_OWNER_RELEASE_CANDIDATE_RECORDED",
        "event_status": "FINAL_OWNER_RELEASE_CANDIDATE_READY",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": session_ref,
        "source_slice_kind": DECISION_GATE_KIND,
        "source_slice_ref": source_pipeline_run_ref,
        "audit_log_ref_candidate": f"audit_log:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}",
        "audit_event_ref_candidate": f"audit_event:{_safe_ref(source_pipeline_run_ref)}:{_safe_ref(session_ref)}",
        "append_operation": "APPEND_EVENT",
        "event_summary": "Final owner release candidate recorded.",
        "source_context_refs": {
            "tenant_ref": tenant_ref,
            "source_pipeline_run_ref": source_pipeline_run_ref,
            "session_ref": session_ref,
        },
        "owner_visible": False,
        "mutation_requested": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if isinstance(value, str) and value.strip()]


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _clean_optional_ref(value: object) -> str | None:
    if value is None:
        return None
    return _clean_required_ref(value)


def _notes(notes: object, fallback_note: str) -> list[str]:
    if not isinstance(notes, list):
        return [fallback_note]
    cleaned_notes = [str(item) for item in notes]
    cleaned_notes.append(fallback_note)
    return cleaned_notes


def _result(
    *,
    status: FinalOwnerReleaseDecisionStatusV1,
    final_owner_release_candidate: Service1FinalOwnerReleaseCandidateV1 | None = None,
    blocked_reason: str | None = None,
    audit_event_candidate: Service1FinalOwnerReleaseAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1FinalOwnerReleaseDecisionGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "final_owner_release_candidate": final_owner_release_candidate,
        "blocked_reason": blocked_reason,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "publish_executed": False,
        "notification_sent": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "DECISION_GATE_KIND",
    "HUMAN_REVIEW_INTEGRATION_KIND",
    "DELIVERY_RELEASE_KIND",
    "OWNER_PACKET_KIND",
    "SIGNED_OFF_STATUS",
    "REJECTED_STATUS",
    "QA_GATE_TYPE",
    "Service1FinalOwnerReleaseDecisionGateInputV1",
    "Service1FinalOwnerReleaseAuditEventCandidateV1",
    "Service1FinalOwnerReleaseCandidateV1",
    "Service1FinalOwnerReleaseDecisionGateResultV1",
    "build_service_1_final_owner_release_decision_gate_v1",
]

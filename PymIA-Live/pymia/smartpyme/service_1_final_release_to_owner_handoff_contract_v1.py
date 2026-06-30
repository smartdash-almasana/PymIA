from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_FINAL_RELEASE_TO_OWNER_HANDOFF_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
HANDOFF_KIND: Final[str] = "OWNER_HANDOFF_CANDIDATE"
FINAL_RELEASE_KIND: Final[str] = "FINAL_OWNER_RELEASE_CANDIDATE"
OWNER_PACKET_KIND: Final[str] = "OWNER_DELIVERY_PACKET_CANDIDATE"
DELIVERY_RELEASE_KIND: Final[str] = "DELIVERY_RELEASE_CANDIDATE"
HANDOFF_CHANNEL_KIND: Final[str] = "OWNER_HANDOFF_CHANNEL_CANDIDATE"
ALLOWED_HANDOFF_CHANNEL_KINDS: Final[tuple[str, ...]] = (
    "OWNER_PORTAL_LINK",
    "SECURE_DOWNLOAD",
    "OPERATOR_MEDIATED_HANDOFF",
)

FinalReleaseToOwnerHandoffStatusV1 = Literal[
    "OWNER_HANDOFF_CANDIDATE_READY",
    "BLOCKED_INVALID_FINAL_RELEASE",
    "BLOCKED_INVALID_OWNER_PACKET",
    "BLOCKED_INVALID_DELIVERY_RELEASE",
    "BLOCKED_MISSING_OWNER",
    "BLOCKED_MISSING_TENANT",
    "BLOCKED_MISSING_CASE",
    "BLOCKED_INVALID_HANDOFF_CHANNEL",
    "BLOCKED_UNSAFE_HANDOFF_FLAGS",
    "UNKNOWN",
]


class Service1FinalReleaseToOwnerHandoffContractInputV1(TypedDict):
    final_owner_release_candidate: dict[str, object] | None
    owner_delivery_packet_candidate: dict[str, object] | None
    delivery_release_candidate: dict[str, object] | None
    handoff_channel_candidate: dict[str, object] | None
    owner_ref: str
    tenant_ref: str
    case_ref: str
    notes: list[str]


class Service1OwnerHandoffAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["OWNER_HANDOFF_CANDIDATE"]
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


class Service1OwnerHandoffCandidateV1(TypedDict):
    candidate_kind: Literal["OWNER_HANDOFF_CANDIDATE"]
    service_name: Literal["SERVICE_1"]
    source_pipeline_run_ref: str
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    artifact_refs: list[str]
    warning_refs: list[str]
    owner_facing_summary: str
    handoff_channel_kind: str | None
    handoff_channel_ref: str | None
    final_release_status: str
    handoff_authorized: Literal[True]
    handoff_executed: Literal[False]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    audit_event_candidate: Service1OwnerHandoffAuditEventCandidateV1
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


class Service1FinalReleaseToOwnerHandoffContractResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: FinalReleaseToOwnerHandoffStatusV1
    owner_handoff_candidate: Service1OwnerHandoffCandidateV1 | None
    blocked_reason: str | None
    audit_event_candidate: Service1OwnerHandoffAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    handoff_executed: Literal[False]
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


def build_service_1_final_release_to_owner_handoff_contract_v1(
    handoff_input: Service1FinalReleaseToOwnerHandoffContractInputV1,
) -> Service1FinalReleaseToOwnerHandoffContractResultV1:
    """Convert a valid final owner release candidate into a pure owner handoff candidate."""
    final_owner_release_candidate = handoff_input.get("final_owner_release_candidate")
    if not isinstance(final_owner_release_candidate, dict) or not final_owner_release_candidate:
        return _result(
            status="BLOCKED_INVALID_FINAL_RELEASE",
            blocked_reason="final_owner_release_candidate_required",
            errors=["final_owner_release_candidate_required"],
            notes=_notes(handoff_input.get("notes"), "Owner handoff requires final_owner_release_candidate."),
        )

    unsafe_final_release_reason = _unsafe_handoff_reason(final_owner_release_candidate)
    if unsafe_final_release_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_HANDOFF_FLAGS",
            blocked_reason=unsafe_final_release_reason,
            errors=[unsafe_final_release_reason],
            notes=_notes(handoff_input.get("notes"), "Unsafe handoff flags are blocked."),
        )

    tenant_ref = _clean_required_ref(handoff_input.get("tenant_ref"))
    if tenant_ref is None:
        return _result(
            status="BLOCKED_MISSING_TENANT",
            blocked_reason="tenant_ref_required",
            errors=["tenant_ref_required"],
            notes=_notes(handoff_input.get("notes"), "Owner handoff requires tenant_ref."),
        )

    owner_ref = _clean_required_ref(handoff_input.get("owner_ref"))
    if owner_ref is None:
        return _result(
            status="BLOCKED_MISSING_OWNER",
            blocked_reason="owner_ref_required",
            errors=["owner_ref_required"],
            notes=_notes(handoff_input.get("notes"), "Owner handoff requires owner_ref."),
        )

    case_ref = _clean_required_ref(handoff_input.get("case_ref"))
    if case_ref is None:
        return _result(
            status="BLOCKED_MISSING_CASE",
            blocked_reason="case_ref_required",
            errors=["case_ref_required"],
            notes=_notes(handoff_input.get("notes"), "Owner handoff requires case_ref."),
        )

    final_release_validation = _validate_final_owner_release_candidate(
        final_owner_release_candidate=final_owner_release_candidate,
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
    )
    if final_release_validation is not None:
        return _result(
            status="BLOCKED_INVALID_FINAL_RELEASE",
            blocked_reason=final_release_validation,
            errors=[final_release_validation],
            notes=_notes(handoff_input.get("notes"), "Final owner release candidate is invalid for owner handoff."),
        )

    owner_delivery_packet_candidate = handoff_input.get("owner_delivery_packet_candidate")
    if not isinstance(owner_delivery_packet_candidate, dict) or not owner_delivery_packet_candidate:
        return _result(
            status="BLOCKED_INVALID_OWNER_PACKET",
            blocked_reason="owner_delivery_packet_candidate_required",
            errors=["owner_delivery_packet_candidate_required"],
            notes=_notes(handoff_input.get("notes"), "Owner handoff requires owner_delivery_packet_candidate."),
        )
    unsafe_owner_packet_reason = _unsafe_handoff_reason(owner_delivery_packet_candidate)
    if unsafe_owner_packet_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_HANDOFF_FLAGS",
            blocked_reason=unsafe_owner_packet_reason,
            errors=[unsafe_owner_packet_reason],
            notes=_notes(handoff_input.get("notes"), "Unsafe handoff flags are blocked."),
        )
    owner_packet_validation = _validate_owner_packet_candidate(
        owner_delivery_packet_candidate=owner_delivery_packet_candidate,
        final_owner_release_candidate=final_owner_release_candidate,
    )
    if owner_packet_validation is not None:
        return _result(
            status="BLOCKED_INVALID_OWNER_PACKET",
            blocked_reason=owner_packet_validation,
            errors=[owner_packet_validation],
            notes=_notes(handoff_input.get("notes"), "Owner delivery packet candidate is invalid for owner handoff."),
        )

    delivery_release_candidate = handoff_input.get("delivery_release_candidate")
    if not isinstance(delivery_release_candidate, dict) or not delivery_release_candidate:
        return _result(
            status="BLOCKED_INVALID_DELIVERY_RELEASE",
            blocked_reason="delivery_release_candidate_required",
            errors=["delivery_release_candidate_required"],
            notes=_notes(handoff_input.get("notes"), "Owner handoff requires delivery_release_candidate."),
        )
    unsafe_delivery_release_reason = _unsafe_handoff_reason(delivery_release_candidate)
    if unsafe_delivery_release_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_HANDOFF_FLAGS",
            blocked_reason=unsafe_delivery_release_reason,
            errors=[unsafe_delivery_release_reason],
            notes=_notes(handoff_input.get("notes"), "Unsafe handoff flags are blocked."),
        )
    delivery_release_validation = _validate_delivery_release_candidate(
        delivery_release_candidate=delivery_release_candidate,
        final_owner_release_candidate=final_owner_release_candidate,
    )
    if delivery_release_validation is not None:
        return _result(
            status="BLOCKED_INVALID_DELIVERY_RELEASE",
            blocked_reason=delivery_release_validation,
            errors=[delivery_release_validation],
            notes=_notes(handoff_input.get("notes"), "Delivery release candidate is invalid for owner handoff."),
        )

    source_pipeline_run_ref = str(final_owner_release_candidate["source_pipeline_run_ref"]).strip()
    if source_pipeline_run_ref == "pipeline_run:unknown":
        return _result(
            status="UNKNOWN",
            blocked_reason="source_pipeline_run_ref_unknown",
            errors=["source_pipeline_run_ref_unknown"],
            notes=_notes(handoff_input.get("notes"), "The source pipeline run cannot be classified safely."),
        )

    handoff_channel_candidate = handoff_input.get("handoff_channel_candidate")
    handoff_channel_validation = _validate_handoff_channel_candidate(
        handoff_channel_candidate=handoff_channel_candidate,
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
    )
    if handoff_channel_validation is not None:
        status, reason = handoff_channel_validation
        return _result(
            status=status,
            blocked_reason=reason,
            errors=[reason],
            notes=_notes(handoff_input.get("notes"), "Handoff channel candidate is invalid for owner handoff."),
        )

    session_ref = str(final_owner_release_candidate["session_ref"]).strip()
    audit_event_candidate = _audit_event_candidate(
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_ref=session_ref,
        source_pipeline_run_ref=source_pipeline_run_ref,
        tenant_ref=tenant_ref,
    )
    candidate: Service1OwnerHandoffCandidateV1 = {
        "candidate_kind": HANDOFF_KIND,
        "service_name": SERVICE_NAME,
        "source_pipeline_run_ref": source_pipeline_run_ref,
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "session_ref": session_ref,
        "artifact_refs": _clean_refs(final_owner_release_candidate.get("artifact_refs")),
        "warning_refs": _clean_refs(final_owner_release_candidate.get("warning_refs")),
        "owner_facing_summary": str(final_owner_release_candidate["owner_facing_summary"]).strip(),
        "handoff_channel_kind": _handoff_channel_value(handoff_channel_candidate, "channel_kind"),
        "handoff_channel_ref": _handoff_channel_value(handoff_channel_candidate, "channel_ref"),
        "final_release_status": "FINAL_OWNER_RELEASE_CANDIDATE_READY",
        "handoff_authorized": True,
        "handoff_executed": False,
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
        status="OWNER_HANDOFF_CANDIDATE_READY",
        owner_handoff_candidate=candidate,
        audit_event_candidate=audit_event_candidate,
        notes=_notes(
            handoff_input.get("notes"),
            "Owner handoff candidate created as pure data only; no publish, send, notification, storage write, or runtime action was executed.",
        ),
    )


def _validate_final_owner_release_candidate(
    *,
    final_owner_release_candidate: dict[str, object],
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
) -> str | None:
    if final_owner_release_candidate.get("candidate_kind") != FINAL_RELEASE_KIND:
        return "candidate_kind_must_be_final_owner_release_candidate"
    if final_owner_release_candidate.get("service_name") != SERVICE_NAME:
        return "service_name_must_be_service_1"
    if _clean_required_ref(final_owner_release_candidate.get("source_pipeline_run_ref")) is None:
        return "source_pipeline_run_ref_required"
    if _clean_required_ref(final_owner_release_candidate.get("session_ref")) is None:
        return "session_ref_required"
    if _clean_required_ref(final_owner_release_candidate.get("tenant_ref")) != tenant_ref:
        return "tenant_ref_must_match_explicit_tenant_ref"
    if _clean_required_ref(final_owner_release_candidate.get("owner_ref")) != owner_ref:
        return "owner_ref_must_match_explicit_owner_ref"
    if _clean_required_ref(final_owner_release_candidate.get("case_ref")) != case_ref:
        return "case_ref_must_match_explicit_case_ref"
    if not _clean_refs(final_owner_release_candidate.get("artifact_refs")):
        return "artifact_refs_required"
    if _clean_required_ref(final_owner_release_candidate.get("owner_facing_summary")) is None:
        return "owner_facing_summary_required"
    if final_owner_release_candidate.get("final_release_authorized") is not True:
        return "final_release_authorized_must_be_true"
    if final_owner_release_candidate.get("publish_executed") is not False:
        return "publish_executed_must_be_false"
    if final_owner_release_candidate.get("notification_sent") is not False:
        return "notification_sent_must_be_false"
    return None


def _validate_owner_packet_candidate(
    *,
    owner_delivery_packet_candidate: dict[str, object],
    final_owner_release_candidate: dict[str, object],
) -> str | None:
    if owner_delivery_packet_candidate.get("packet_kind") != OWNER_PACKET_KIND:
        return "packet_kind_must_be_owner_delivery_packet_candidate"
    if _clean_required_ref(owner_delivery_packet_candidate.get("source_pipeline_run_ref")) != _clean_required_ref(
        final_owner_release_candidate.get("source_pipeline_run_ref")
    ):
        return "source_pipeline_run_ref_must_match_final_owner_release_candidate"
    if _clean_refs(owner_delivery_packet_candidate.get("artifact_refs")) != _clean_refs(final_owner_release_candidate.get("artifact_refs")):
        return "artifact_refs_must_match_final_owner_release_candidate"
    if _clean_required_ref(owner_delivery_packet_candidate.get("owner_facing_summary")) != _clean_required_ref(
        final_owner_release_candidate.get("owner_facing_summary")
    ):
        return "owner_facing_summary_must_match_final_owner_release_candidate"
    if owner_delivery_packet_candidate.get("publishable") is not False:
        return "publishable_must_be_false"
    if owner_delivery_packet_candidate.get("signoff_required") is not True:
        return "signoff_required_must_be_true"
    return None


def _validate_delivery_release_candidate(
    *,
    delivery_release_candidate: dict[str, object],
    final_owner_release_candidate: dict[str, object],
) -> str | None:
    if delivery_release_candidate.get("release_kind") != DELIVERY_RELEASE_KIND:
        return "release_kind_must_be_delivery_release_candidate"
    if _clean_required_ref(delivery_release_candidate.get("source_pipeline_run_ref")) != _clean_required_ref(
        final_owner_release_candidate.get("source_pipeline_run_ref")
    ):
        return "source_pipeline_run_ref_must_match_final_owner_release_candidate"
    if _clean_refs(delivery_release_candidate.get("artifact_refs")) != _clean_refs(final_owner_release_candidate.get("artifact_refs")):
        return "artifact_refs_must_match_final_owner_release_candidate"
    if delivery_release_candidate.get("publishable") is not False:
        return "publishable_must_be_false"
    if delivery_release_candidate.get("signoff_required") is not True:
        return "signoff_required_must_be_true"
    return None


def _validate_handoff_channel_candidate(
    *,
    handoff_channel_candidate: object,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
) -> tuple[FinalReleaseToOwnerHandoffStatusV1, str] | None:
    if handoff_channel_candidate is None:
        return None
    if not isinstance(handoff_channel_candidate, dict) or not handoff_channel_candidate:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "handoff_channel_candidate_invalid")
    unsafe_reason = _unsafe_handoff_reason(handoff_channel_candidate)
    if unsafe_reason is not None:
        return ("BLOCKED_UNSAFE_HANDOFF_FLAGS", unsafe_reason)
    if handoff_channel_candidate.get("channel_candidate_kind") != HANDOFF_CHANNEL_KIND:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "channel_candidate_kind_must_be_owner_handoff_channel_candidate")
    channel_kind = _clean_required_ref(handoff_channel_candidate.get("channel_kind"))
    if channel_kind is None:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "channel_kind_required")
    if channel_kind not in ALLOWED_HANDOFF_CHANNEL_KINDS:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "channel_kind_not_allowed")
    if _clean_required_ref(handoff_channel_candidate.get("channel_ref")) is None:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "channel_ref_required")
    if handoff_channel_candidate.get("channel_ready") is not True:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "channel_ready_must_be_true")
    channel_tenant_ref = handoff_channel_candidate.get("tenant_ref")
    if channel_tenant_ref is not None and _clean_required_ref(channel_tenant_ref) != tenant_ref:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "tenant_ref_must_match_explicit_tenant_ref")
    channel_owner_ref = handoff_channel_candidate.get("owner_ref")
    if channel_owner_ref is not None and _clean_required_ref(channel_owner_ref) != owner_ref:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "owner_ref_must_match_explicit_owner_ref")
    channel_case_ref = handoff_channel_candidate.get("case_ref")
    if channel_case_ref is not None and _clean_required_ref(channel_case_ref) != case_ref:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "case_ref_must_match_explicit_case_ref")
    if handoff_channel_candidate.get("handoff_authorized") is not False:
        return ("BLOCKED_INVALID_HANDOFF_CHANNEL", "handoff_authorized_must_be_false")
    return None


def _handoff_channel_value(handoff_channel_candidate: object, key: str) -> str | None:
    if not isinstance(handoff_channel_candidate, dict):
        return None
    return _clean_required_ref(handoff_channel_candidate.get(key))


def _unsafe_handoff_reason(candidate: dict[str, object]) -> str | None:
    for flag_name in (
        "handoff_executed",
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
        "delivery_authorized",
        "autonomous_delivery_authorized",
        "signoff_authorized",
        "release_authorized",
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
) -> Service1OwnerHandoffAuditEventCandidateV1:
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "OWNER_HANDOFF_CANDIDATE_RECORDED",
        "event_status": "OWNER_HANDOFF_CANDIDATE_READY",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": session_ref,
        "source_slice_kind": HANDOFF_KIND,
        "source_slice_ref": source_pipeline_run_ref,
        "audit_log_ref_candidate": f"audit_log:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}",
        "audit_event_ref_candidate": f"audit_event:{_safe_ref(source_pipeline_run_ref)}:{_safe_ref(session_ref)}:owner_handoff",
        "append_operation": "APPEND_EVENT",
        "event_summary": "Owner handoff candidate recorded.",
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


def _notes(notes: object, fallback_note: str) -> list[str]:
    if not isinstance(notes, list):
        return [fallback_note]
    cleaned_notes = [str(item) for item in notes]
    cleaned_notes.append(fallback_note)
    return cleaned_notes


def _result(
    *,
    status: FinalReleaseToOwnerHandoffStatusV1,
    owner_handoff_candidate: Service1OwnerHandoffCandidateV1 | None = None,
    blocked_reason: str | None = None,
    audit_event_candidate: Service1OwnerHandoffAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1FinalReleaseToOwnerHandoffContractResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "owner_handoff_candidate": owner_handoff_candidate,
        "blocked_reason": blocked_reason,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "handoff_executed": False,
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
    "HANDOFF_KIND",
    "FINAL_RELEASE_KIND",
    "OWNER_PACKET_KIND",
    "DELIVERY_RELEASE_KIND",
    "HANDOFF_CHANNEL_KIND",
    "ALLOWED_HANDOFF_CHANNEL_KINDS",
    "Service1FinalReleaseToOwnerHandoffContractInputV1",
    "Service1OwnerHandoffAuditEventCandidateV1",
    "Service1OwnerHandoffCandidateV1",
    "Service1FinalReleaseToOwnerHandoffContractResultV1",
    "build_service_1_final_release_to_owner_handoff_contract_v1",
]

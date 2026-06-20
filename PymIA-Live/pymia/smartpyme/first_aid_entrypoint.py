from __future__ import annotations

from typing import Any, Literal, TypedDict

from pymia.smartpyme.service_depth import ServiceDepthVerdict, derive_service_depth

FirstAidEntrypointStatus = Literal["FIRST_AID_READY", "FIRST_AID_NEEDS_EVIDENCE", "NOT_FIRST_AID"]


class FirstAidEntrypointVerdict(TypedDict):
    status: FirstAidEntrypointStatus
    service_depth: ServiceDepthVerdict
    tenant_id: str
    intake_id: str
    raw_owner_message: str
    has_file: bool
    allowed_to_run_first_aid: bool
    next_allowed_action: str
    required_evidence: list[str]
    warnings: list[str]


def evaluate_first_aid_entrypoint(
    *,
    tenant_id: str,
    intake_id: str,
    raw_owner_message: str,
    has_file: bool,
    taxonomic_intake: dict[str, Any] | None = None,
) -> FirstAidEntrypointVerdict:
    """Evaluate whether a minimal owner intake can enter FIRST_AID.

    This helper is pure and deterministic. It does not persist, read files,
    execute the vertical pipeline, calculate formulas, diagnose, or touch OCF/replay.
    It delegates service-depth classification to derive_service_depth(...).
    """
    normalized_tenant_id = _required_text(tenant_id, field_name="tenant_id")
    normalized_intake_id = _required_text(intake_id, field_name="intake_id")
    normalized_message = _required_text(raw_owner_message, field_name="raw_owner_message")
    if not isinstance(has_file, bool):
        raise ValueError("has_file must be a bool")
    if taxonomic_intake is not None and not isinstance(taxonomic_intake, dict):
        raise ValueError("taxonomic_intake must be a dict or None")

    evidence_records = [_first_aid_file_evidence()] if has_file else []
    service_depth = derive_service_depth(
        taxonomic_intake=taxonomic_intake,
        raw_owner_message=normalized_message,
        evidence_records=evidence_records,
    )

    status = _status_from_service_depth(service_depth=service_depth, has_file=has_file)
    allowed_to_run_first_aid = status == "FIRST_AID_READY"

    return {
        "status": status,
        "service_depth": service_depth,
        "tenant_id": normalized_tenant_id,
        "intake_id": normalized_intake_id,
        "raw_owner_message": normalized_message,
        "has_file": has_file,
        "allowed_to_run_first_aid": allowed_to_run_first_aid,
        "next_allowed_action": service_depth["next_allowed_action"],
        "required_evidence": [] if has_file else ["minimal_file_or_source"],
        "warnings": _warnings_from_status(status=status, service_depth=service_depth, has_file=has_file),
    }


def _status_from_service_depth(*, service_depth: ServiceDepthVerdict, has_file: bool) -> FirstAidEntrypointStatus:
    if service_depth["level"] != "FIRST_AID":
        return "NOT_FIRST_AID"
    if has_file and service_depth["next_allowed_action"] == "run_first_aid_microservice":
        return "FIRST_AID_READY"
    return "FIRST_AID_NEEDS_EVIDENCE"


def _first_aid_file_evidence() -> dict[str, str]:
    return {
        "evidence_id": "first_aid_pending_file",
        "evidence_type": "single_file_upload",
        "source_kind": "owner_uploaded_file",
        "status": "REGISTERED",
    }


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _warnings_from_status(
    *,
    status: FirstAidEntrypointStatus,
    service_depth: ServiceDepthVerdict,
    has_file: bool,
) -> list[str]:
    if status == "FIRST_AID_READY":
        return []
    if status == "FIRST_AID_NEEDS_EVIDENCE" and not has_file:
        return ["FIRST_AID requires a minimal file or source before execution."]
    if status == "NOT_FIRST_AID":
        return [
            "Intake requires a different service depth; FIRST_AID must not run or diagnose from this signal alone.",
            f"service_depth_level={service_depth['level']}",
        ]
    return []


__all__ = [
    "FirstAidEntrypointStatus",
    "FirstAidEntrypointVerdict",
    "evaluate_first_aid_entrypoint",
]

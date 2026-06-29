from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_OWNER_DELIVERY_PACKET_FOR_SAAS_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
RELEASE_READY_STATUS: Final[str] = "DELIVERY_RELEASE_CANDIDATE_READY"
RELEASE_KIND: Final[str] = "DELIVERY_RELEASE_CANDIDATE"
PACKET_KIND: Final[str] = "OWNER_DELIVERY_PACKET_CANDIDATE"

OwnerDeliveryPacketStatusV1 = Literal[
    "OWNER_DELIVERY_PACKET_CANDIDATE_READY",
    "BLOCKED_RELEASE_CANDIDATE_NOT_READY",
    "BLOCKED_MISSING_RELEASE_CANDIDATE",
    "BLOCKED_MISSING_PIPELINE_RESULT",
    "BLOCKED_MISSING_ARTIFACT_REFS",
    "UNKNOWN",
]


class Service1OwnerDeliveryPacketForSaasInputV1(TypedDict):
    release_candidate_status: str
    delivery_release_candidate: dict[str, Any] | None
    pipeline_run_result: dict[str, Any] | None
    notes: list[str]


class Service1OwnerDeliveryPacketCandidateV1(TypedDict):
    source_pipeline_run_ref: str
    artifact_refs: list[str]
    warning_refs: list[str]
    owner_facing_summary: str
    packet_kind: Literal["OWNER_DELIVERY_PACKET_CANDIDATE"]
    publishable: Literal[False]
    signoff_required: Literal[True]
    delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    signoff_authorized: Literal[False]


class Service1OwnerDeliveryPacketForSaasResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: OwnerDeliveryPacketStatusV1
    owner_delivery_packet_candidate: Service1OwnerDeliveryPacketCandidateV1 | None
    blocked_reason: str | None
    missing_artifact_refs: list[str]
    publishable: Literal[False]
    delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    signoff_required: Literal[True]
    signoff_authorized: Literal[False]
    notes: list[str]


def build_service_1_owner_delivery_packet_for_saas_v1(
    packet_input: Service1OwnerDeliveryPacketForSaasInputV1,
) -> Service1OwnerDeliveryPacketForSaasResultV1:
    """Build a SaaS owner-facing delivery packet candidate.

    This pure transformer does not read files, write files, publish artifacts,
    create archives, close cases, call pipelines, or produce final approval. It
    only reshapes verified references into an owner-readable candidate packet.
    """
    if packet_input.get("release_candidate_status") != RELEASE_READY_STATUS:
        return _result(
            status="BLOCKED_RELEASE_CANDIDATE_NOT_READY",
            blocked_reason="release_candidate_status_not_ready",
            notes=["Owner packet candidate requires DELIVERY_RELEASE_CANDIDATE_READY."],
        )

    release_candidate = packet_input.get("delivery_release_candidate")
    if not isinstance(release_candidate, dict) or not release_candidate:
        return _result(
            status="BLOCKED_MISSING_RELEASE_CANDIDATE",
            blocked_reason="delivery_release_candidate_required",
            notes=["Missing delivery release candidate."],
        )

    pipeline_run_result = packet_input.get("pipeline_run_result")
    if not isinstance(pipeline_run_result, dict) or not pipeline_run_result:
        return _result(
            status="BLOCKED_MISSING_PIPELINE_RESULT",
            blocked_reason="pipeline_run_result_required",
            notes=["Missing pipeline run result."],
        )

    if release_candidate.get("release_kind") != RELEASE_KIND:
        return _result(
            status="BLOCKED_RELEASE_CANDIDATE_NOT_READY",
            blocked_reason="release_kind_not_delivery_release_candidate",
            notes=["Only DELIVERY_RELEASE_CANDIDATE can be transformed into owner packet candidate."],
        )

    if release_candidate.get("publishable") is not False:
        return _result(
            status="BLOCKED_RELEASE_CANDIDATE_NOT_READY",
            blocked_reason="release_candidate_must_not_be_publishable",
            notes=["Publishable release candidates are outside this transformer."],
        )

    if release_candidate.get("signoff_required") is not True:
        return _result(
            status="BLOCKED_RELEASE_CANDIDATE_NOT_READY",
            blocked_reason="release_candidate_must_require_signoff",
            notes=["Owner packet candidate requires signoff_required=true."],
        )

    artifact_refs = _clean_refs(release_candidate.get("artifact_refs", []))
    if not artifact_refs:
        return _result(
            status="BLOCKED_MISSING_ARTIFACT_REFS",
            blocked_reason="artifact_refs_required",
            missing_artifact_refs=["artifact_refs"],
            notes=["Owner packet candidate requires artifact references."],
        )

    source_pipeline_run_ref = _source_pipeline_run_ref(release_candidate, pipeline_run_result)
    warning_refs = _clean_refs(release_candidate.get("warning_refs", []))
    executed_tool_refs = _clean_refs(pipeline_run_result.get("executed_tool_refs", []))

    candidate: Service1OwnerDeliveryPacketCandidateV1 = {
        "source_pipeline_run_ref": source_pipeline_run_ref,
        "artifact_refs": list(artifact_refs),
        "warning_refs": list(warning_refs),
        "owner_facing_summary": _owner_facing_summary(
            artifact_count=len(artifact_refs),
            warning_count=len(warning_refs),
            executed_tool_refs=executed_tool_refs,
        ),
        "packet_kind": PACKET_KIND,
        "publishable": False,
        "signoff_required": True,
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "signoff_authorized": False,
    }

    return _result(
        status="OWNER_DELIVERY_PACKET_CANDIDATE_READY",
        owner_delivery_packet_candidate=candidate,
        notes=["Owner delivery packet candidate created without publishing or final approval."],
    )


def _source_pipeline_run_ref(
    release_candidate: dict[str, Any],
    pipeline_run_result: dict[str, Any],
) -> str:
    candidate_ref = release_candidate.get("source_pipeline_run_ref")
    if isinstance(candidate_ref, str) and candidate_ref.strip():
        return candidate_ref
    for key in ("pipeline_run_ref", "run_id", "case_id"):
        value = pipeline_run_result.get(key)
        if isinstance(value, str) and value.strip():
            return value
    schema_version = pipeline_run_result.get("schema_version")
    if isinstance(schema_version, str) and schema_version.strip():
        return f"pipeline_run:{schema_version}"
    return "pipeline_run:unknown"


def _owner_facing_summary(
    *,
    artifact_count: int,
    warning_count: int,
    executed_tool_refs: list[str],
) -> str:
    tool_count = len(executed_tool_refs)
    return (
        "PymIA preparó un paquete candidato para el dueño PyME con "
        f"{artifact_count} artefacto(s) referenciado(s), "
        f"{warning_count} advertencia(s) y "
        f"{tool_count} herramienta(s) ejecutada(s). "
        "El paquete todavía requiere revisión/signoff antes de publicarse."
    )


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if isinstance(value, str) and value.strip()]


def _result(
    *,
    status: OwnerDeliveryPacketStatusV1,
    owner_delivery_packet_candidate: Service1OwnerDeliveryPacketCandidateV1 | None = None,
    blocked_reason: str | None = None,
    missing_artifact_refs: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1OwnerDeliveryPacketForSaasResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "owner_delivery_packet_candidate": owner_delivery_packet_candidate,
        "blocked_reason": blocked_reason,
        "missing_artifact_refs": list(missing_artifact_refs or []),
        "publishable": False,
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "signoff_required": True,
        "signoff_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "RELEASE_READY_STATUS",
    "RELEASE_KIND",
    "PACKET_KIND",
    "Service1OwnerDeliveryPacketForSaasInputV1",
    "Service1OwnerDeliveryPacketCandidateV1",
    "Service1OwnerDeliveryPacketForSaasResultV1",
    "build_service_1_owner_delivery_packet_for_saas_v1",
]

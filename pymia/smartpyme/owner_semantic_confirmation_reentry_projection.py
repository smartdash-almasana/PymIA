from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from pymia.contracts.owner_semantic_confirmation import OwnerSemanticConfirmationGate
from pymia.smartpyme.owner_confirmed_semantic_request_flow import (
    build_owner_confirmed_semantic_request_flow,
)
from pymia.smartpyme.owner_confirmed_semantic_request_projection import (
    project_confirmed_semantic_requests_to_owner_facing,
)

SEMANTIC_CONFIRMATION_STATUS_CONFIRMED = "CONFIRMED_BY_OWNER"
SEMANTIC_CONFIRMATION_STATUS_CORRECTED = "CORRECTED_BY_OWNER"
SEMANTIC_CONFIRMATION_STATUS_REJECTED = "REJECTED_BY_OWNER"
SUPPORTED_CONFIRMATION_STATUSES = {
    SEMANTIC_CONFIRMATION_STATUS_CONFIRMED,
    SEMANTIC_CONFIRMATION_STATUS_CORRECTED,
    SEMANTIC_CONFIRMATION_STATUS_REJECTED,
}


def _as_dict(value: Any, *, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "model_dump") and callable(value.model_dump):
        data = value.model_dump(mode="json")
        if not isinstance(data, dict):
            raise ValueError(f"{label}.model_dump() must return dict")
        return dict(data)
    if hasattr(value, "to_dict") and callable(value.to_dict):
        data = value.to_dict()
        if not isinstance(data, dict):
            raise ValueError(f"{label}.to_dict() must return dict")
        return dict(data)
    raise ValueError(f"{label} must be mapping, dataclass, or expose model_dump()/to_dict()")


def _metadata_from_answer(answer_data: dict[str, Any]) -> dict[str, Any]:
    metadata = answer_data.get("metadata") or {}
    if not isinstance(metadata, Mapping):
        return {}
    return dict(metadata)


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list | tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def project_semantic_confirmation_reentry_to_owner_facing(
    *,
    owner_answer: Mapping[str, Any] | Any,
    owner_facing_report: Mapping[str, Any] | Any,
    missing_keys: list[str] | tuple[str, ...],
    source_ref: str,
) -> dict[str, Any]:
    """Project explicit semantic-confirmation reentry into owner-facing report.

    This function is intentionally conservative: it only acts when the owner
    answer metadata carries an explicit semantic_confirmation_status. It does
    not infer confirmation from free text.
    """

    answer_data = _as_dict(owner_answer, label="owner_answer")
    metadata = _metadata_from_answer(answer_data)
    confirmation_status = str(metadata.get("semantic_confirmation_status") or "").strip()
    if confirmation_status not in SUPPORTED_CONFIRMATION_STATUSES:
        report = _as_dict(owner_facing_report, label="owner_facing_report")
        report["semantic_confirmation_reentry_projection"] = {
            "applied": False,
            "reason": "missing_explicit_semantic_confirmation_status",
        }
        return report

    source_ref_text = str(source_ref or "").strip()
    if not source_ref_text:
        raise ValueError("source_ref must be non-empty")

    proposed_interpretation = str(
        metadata.get("proposed_interpretation")
        or metadata.get("semantic_interpretation")
        or ""
    ).strip()
    if not proposed_interpretation:
        raise ValueError("semantic confirmation reentry requires proposed_interpretation metadata")

    confirmation_question = str(
        metadata.get("confirmation_question")
        or "¿Confirmás este eje semántico para pedir evidencia concreta?"
    ).strip()
    owner_response_text = str(answer_data.get("answer_text") or metadata.get("owner_response_text") or "").strip()
    if confirmation_status in {
        SEMANTIC_CONFIRMATION_STATUS_CONFIRMED,
        SEMANTIC_CONFIRMATION_STATUS_REJECTED,
    } and not owner_response_text:
        raise ValueError("confirmed/rejected semantic confirmation requires owner response text")

    corrected_interpretation = str(metadata.get("corrected_interpretation") or "").strip()
    if confirmation_status == SEMANTIC_CONFIRMATION_STATUS_CORRECTED and not corrected_interpretation:
        raise ValueError("corrected semantic confirmation requires corrected_interpretation metadata")

    related_missing_keys = _dedupe(
        _string_list(metadata.get("related_missing_keys")) or list(missing_keys)
    )
    gate = OwnerSemanticConfirmationGate(
        gate_id=str(metadata.get("gate_id") or f"semantic_confirmation_reentry:{source_ref_text}"),
        target_type=str(metadata.get("target_type") or "SEMANTIC_INTERPRETATION"),
        proposed_interpretation=proposed_interpretation,
        confirmation_question=confirmation_question,
        status=confirmation_status,
        owner_response_text=owner_response_text or None,
        corrected_interpretation=corrected_interpretation or None,
        related_missing_keys=related_missing_keys,
        source_ref=source_ref_text,
        metadata={"projection_source": "owner_answer_reentry"},
    )

    flow_result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=gate,
        missing_keys=_dedupe(list(missing_keys)),
        source_ref=source_ref_text,
        metadata={"projection_source": "owner_answer_reentry"},
    )
    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=owner_facing_report,
        flow_result=flow_result,
    )
    projected["semantic_confirmation_reentry_projection"] = {
        "applied": True,
        "confirmation_status": confirmation_status,
        "flow_status": flow_result.flow_status,
        "requests_count": len(flow_result.semantic_evidence_requests),
        "unsupported_missing_keys": list(flow_result.unsupported_missing_keys),
        "does_resolve_structural_input": False,
        "produces_findings": False,
    }
    return projected


__all__ = [
    "SEMANTIC_CONFIRMATION_STATUS_CONFIRMED",
    "SEMANTIC_CONFIRMATION_STATUS_CORRECTED",
    "SEMANTIC_CONFIRMATION_STATUS_REJECTED",
    "project_semantic_confirmation_reentry_to_owner_facing",
]

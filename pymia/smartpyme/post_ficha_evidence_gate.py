"""Post-ficha evidence reception and readiness gate.

Pure helpers for handling structured evidence messages after post_ficha_routing exists.
"""

from __future__ import annotations

from typing import Any

from pymia.smartpyme.evidence import create_evidence_record
from pymia.smartpyme.intake import (
    EVIDENCE_STATUS_RECEIVED,
    EVIDENCE_STATUS_REQUESTED,
    EVIDENCE_STATUS_SATISFIED,
)


def parse_post_ficha_evidence_input(text: str) -> tuple[str, str, str]:
    """Parse `EVIDENCE::<source_kind>::<evidence_type>::<source_ref>`."""
    parts = text.split("::")
    if len(parts) != 4:
        raise ValueError(
            "Formato inválido. Usá: EVIDENCE::<source_kind>::<evidence_type>::<source_ref>"
        )
    prefix, source_kind, evidence_type, source_ref = [p.strip() for p in parts]
    if prefix != "EVIDENCE" or not source_kind or not evidence_type or not source_ref:
        raise ValueError(
            "Formato inválido. Usá: EVIDENCE::<source_kind>::<evidence_type>::<source_ref>"
        )
    return source_kind, evidence_type, source_ref


def is_post_ficha_evidence_input(text: str) -> bool:
    return isinstance(text, str) and text.strip().upper().startswith("EVIDENCE::")


def merge_previous_post_ficha_evidence_context(
    *,
    previous_context: dict[str, Any] | None,
    updated_context: dict[str, Any],
) -> dict[str, Any]:
    """Carry forward post-ficha evidence/readiness lightweight context."""
    if not isinstance(previous_context, dict):
        return updated_context

    merged = dict(updated_context)
    prev_records = previous_context.get("evidence_records")
    if isinstance(prev_records, list):
        merged["evidence_records"] = [
            dict(item) for item in prev_records if isinstance(item, dict)
        ]
    prev_readiness = previous_context.get("post_ficha_readiness")
    if isinstance(prev_readiness, dict):
        merged["post_ficha_readiness"] = dict(prev_readiness)
    return merged


def _request_is_satisfied(status: str) -> bool:
    return status in {EVIDENCE_STATUS_RECEIVED, EVIDENCE_STATUS_SATISFIED}


def _find_matching_request_id(evidence_requests: list[dict[str, Any]], evidence_type: str) -> str | None:
    for req in evidence_requests:
        if not isinstance(req, dict):
            continue
        if str(req.get("evidence_type") or "").strip() == evidence_type:
            request_id = req.get("request_id")
            if isinstance(request_id, str) and request_id.strip():
                return request_id
    return None


def apply_post_ficha_evidence_turn(
    *,
    tenant_id: str,
    message_text: str,
    previous_context: dict[str, Any] | None,
    updated_context: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Apply evidence reception, request update, and readiness projection."""
    source_kind, evidence_type, source_ref = parse_post_ficha_evidence_input(message_text.strip())

    post_ficha_routing = updated_context.get("post_ficha_routing")
    if not isinstance(post_ficha_routing, dict):
        raise ValueError("No hay post_ficha_routing disponible. Completá primero la ficha inicial.")

    intake_id = str(post_ficha_routing.get("intake_id") or "").strip()
    if not intake_id:
        raise ValueError("post_ficha_routing no contiene intake_id válido.")

    evidence_requests_raw = post_ficha_routing.get("evidence_requests")
    evidence_requests = [
        dict(req) for req in evidence_requests_raw if isinstance(req, dict)
    ] if isinstance(evidence_requests_raw, list) else []

    request_id = _find_matching_request_id(evidence_requests, evidence_type)
    evidence_key = (intake_id, evidence_type, source_kind, source_ref)

    evidence_records_raw = updated_context.get("evidence_records")
    evidence_records: list[dict[str, Any]] = []
    if isinstance(evidence_records_raw, list):
        for row in evidence_records_raw:
            if isinstance(row, dict):
                evidence_records.append(dict(row))

    already_exists = False
    for row in evidence_records:
        row_key = (
            str(row.get("intake_id") or "").strip(),
            str(row.get("evidence_type") or "").strip(),
            str(row.get("source_kind") or "").strip(),
            str(row.get("source_ref") or "").strip(),
        )
        if row_key == evidence_key:
            already_exists = True
            break

    if not already_exists:
        evidence_record = create_evidence_record(
            tenant_id=tenant_id,
            intake_id=intake_id,
            request_id=request_id,
            evidence_type=evidence_type,
            source_kind=source_kind,
            source_ref=source_ref,
        )
        evidence_records.append(evidence_record.to_dict())

    updated_requests: list[dict[str, Any]] = []
    for req in evidence_requests:
        item = dict(req)
        if str(item.get("evidence_type") or "").strip() == evidence_type:
            item["status"] = EVIDENCE_STATUS_RECEIVED
        elif not str(item.get("status") or "").strip():
            item["status"] = EVIDENCE_STATUS_REQUESTED
        updated_requests.append(item)

    out_context = dict(updated_context)
    updated_post_ficha_routing = dict(post_ficha_routing)
    updated_post_ficha_routing["evidence_requests"] = updated_requests
    out_context["post_ficha_routing"] = updated_post_ficha_routing
    out_context["evidence_records"] = evidence_records

    blocking_requests = [
        req for req in updated_requests if bool(req.get("blocks_analysis", True))
    ]
    requested_count = len(blocking_requests)
    missing_types: list[str] = []
    received_count = 0
    for req in blocking_requests:
        status = str(req.get("status") or EVIDENCE_STATUS_REQUESTED).strip()
        if _request_is_satisfied(status):
            received_count += 1
        else:
            missing_types.append(str(req.get("evidence_type") or "").strip())

    ready_for_analysis = requested_count == 0 or len(missing_types) == 0
    readiness_state = "READY_FOR_ANALYSIS" if ready_for_analysis else "NEEDS_EVIDENCE"
    out_context["post_ficha_readiness"] = {
        "intake_id": intake_id,
        "readiness_state": readiness_state,
        "received_count": received_count,
        "requested_count": requested_count,
        "missing_evidence_types": [x for x in missing_types if x],
        "ready_for_analysis": ready_for_analysis,
    }

    if ready_for_analysis:
        reply = (
            "Evidencia recibida. Ya quedó reunida la evidencia mínima para revisión y análisis posterior."
        )
    else:
        missing_list = [x for x in missing_types if x]
        if missing_list:
            missing_lines = "\n".join(f"- {item}" for item in missing_list)
            reply = (
                "Evidencia recibida. Para avanzar todavía falta esta evidencia mínima:\n"
                f"{missing_lines}"
            )
        else:
            reply = "Evidencia recibida. Todavía faltan evidencias para avanzar."

    return out_context, reply

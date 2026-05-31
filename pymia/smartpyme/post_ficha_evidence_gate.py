"""Post-ficha evidence reception and readiness gate.

Pure helpers for handling structured evidence messages after post_ficha_routing exists.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pymia.smartpyme.evidence import create_evidence_record
from pymia.smartpyme.xlsx_document_metadata_adapter import (
    parse_xlsx_to_document_metadata,
)
from pymia.smartpyme.evidence_gate import (
    ASSESSMENT_SATISFIED,
    SUGGESTED_READY_FOR_ANALYSIS,
    evaluate_evidence_sufficiency,
)
from pymia.smartpyme.intake import (
    EVIDENCE_STATUS_RECEIVED,
    EVIDENCE_STATUS_REQUESTED,
    EVIDENCE_STATUS_SATISFIED,
)


def _parse_post_ficha_evidence_input_with_metadata(
    text: str,
) -> tuple[str, str, str, dict[str, Any]]:
    """Parse evidence input and optional declared structural fields."""
    parts = text.split("::")
    if len(parts) not in {4, 5}:
        raise ValueError(
            "Formato inválido. Usá: EVIDENCE::<source_kind>::<evidence_type>::<source_ref>"
            "[::FIELDS=<campo1,campo2>]"
        )
    prefix, source_kind, evidence_type, source_ref = [p.strip() for p in parts[:4]]
    if prefix != "EVIDENCE" or not source_kind or not evidence_type or not source_ref:
        raise ValueError(
            "Formato inválido. Usá: EVIDENCE::<source_kind>::<evidence_type>::<source_ref>"
            "[::FIELDS=<campo1,campo2>]"
        )
    metadata: dict[str, Any] = {}
    if len(parts) == 5:
        fields_part = parts[4].strip()
        if not fields_part.upper().startswith("FIELDS="):
            raise ValueError("Metadata inválida. Usá: FIELDS=<campo1,campo2>")
        raw_fields = fields_part.split("=", 1)[1]
        fields = list(dict.fromkeys(
            field.strip() for field in raw_fields.split(",") if field.strip()
        ))
        metadata["fields"] = fields
    return source_kind, evidence_type, source_ref, metadata


def parse_post_ficha_evidence_input(text: str) -> tuple[str, str, str]:
    """Parse evidence input while preserving the original public return shape."""
    source_kind, evidence_type, source_ref, _ = _parse_post_ficha_evidence_input_with_metadata(text)
    return source_kind, evidence_type, source_ref


def is_post_ficha_evidence_input(text: str) -> bool:
    return isinstance(text, str) and text.strip().upper().startswith("EVIDENCE::")


def _enrich_metadata_from_source(
    source_ref: str,
    record_metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Si ``source_ref`` apunta a un archivo XLSX local existente y no hay
    ``FIELDS=`` declarados en ``record_metadata``, invoca el adaptador XLSX
    para poblar metadata estructural automáticamente.

    Si el parseo falla, no rompe el flujo: retorna metadata con
    ``parse_status=FAILED`` y warnings, pero sin exceptions.
    """
    # 1) Solo enriquecer si no hay fields declarados manualmente
    if "fields" in record_metadata:
        return record_metadata

    # 2) Solo procesar si source_ref parece un path local a XLSX
    try:
        path = Path(source_ref)
    except (TypeError, ValueError):
        return record_metadata

    if not path.exists():
        return record_metadata

    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        return record_metadata

    # 3) Invocar adaptador XLSX (fail-closed: nunca lanza)
    try:
        parsed = parse_xlsx_to_document_metadata(path)
        enriched = dict(record_metadata)
        enriched.update(parsed.to_dict())
        return enriched
    except Exception as exc:  # noqa: BLE001 — aislamiento del adaptador
        # Fallar abierto: metadata mínima con warning
        from pymia.smartpyme.parsed_document_metadata import (
            PARSE_STATUS_FAILED,
        )
        return {
            **record_metadata,
            "parse_status": PARSE_STATUS_FAILED,
            "warnings": [f"xlsx_adapter_error: {exc}"],
            "confidence": 0.0,
        }


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
    evidence_metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    """Apply evidence reception and delegate declared-content sufficiency evaluation."""
    source_kind, evidence_type, source_ref, declared_metadata = (
        _parse_post_ficha_evidence_input_with_metadata(message_text.strip())
    )
    record_metadata = dict(evidence_metadata or {})
    if "fields" in declared_metadata:
        record_metadata["fields"] = list(declared_metadata["fields"])

    # Enriquecer metadata automáticamente desde source_ref si aplica
    record_metadata = _enrich_metadata_from_source(source_ref, record_metadata)

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

    existing_record: dict[str, Any] | None = None
    for row in evidence_records:
        row_key = (
            str(row.get("intake_id") or "").strip(),
            str(row.get("evidence_type") or "").strip(),
            str(row.get("source_kind") or "").strip(),
            str(row.get("source_ref") or "").strip(),
        )
        if row_key == evidence_key:
            existing_record = row
            break

    if existing_record is None:
        evidence_record = create_evidence_record(
            tenant_id=tenant_id,
            intake_id=intake_id,
            request_id=request_id,
            evidence_type=evidence_type,
            source_kind=source_kind,
            source_ref=source_ref,
            metadata=record_metadata,
        )
        evidence_records.append(evidence_record.to_dict())
    elif record_metadata:
        merged_metadata = dict(existing_record.get("metadata") or {})
        existing_fields = merged_metadata.get("fields")
        new_fields = record_metadata.get("fields")
        if isinstance(existing_fields, list) and isinstance(new_fields, list):
            record_metadata["fields"] = list(dict.fromkeys([*existing_fields, *new_fields]))
        merged_metadata.update(record_metadata)
        existing_record["metadata"] = merged_metadata

    updated_requests: list[dict[str, Any]] = []
    for req in evidence_requests:
        item = dict(req)
        if str(item.get("evidence_type") or "").strip() == evidence_type:
            item["status"] = EVIDENCE_STATUS_RECEIVED
        elif not str(item.get("status") or "").strip():
            item["status"] = EVIDENCE_STATUS_REQUESTED
        updated_requests.append(item)

    sufficiency = evaluate_evidence_sufficiency(
        {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "evidence_requests": updated_requests,
        },
        evidence_records,
    )
    assessment_by_id = {
        assessment.request_id: assessment for assessment in sufficiency.assessments
    }
    for item in updated_requests:
        assessment = assessment_by_id.get(str(item.get("request_id") or ""))
        if assessment is None:
            continue
        if assessment.status == ASSESSMENT_SATISFIED:
            item["status"] = EVIDENCE_STATUS_SATISFIED
        elif assessment.matched_evidence_ids:
            item["status"] = EVIDENCE_STATUS_RECEIVED

    out_context = dict(updated_context)
    updated_post_ficha_routing = dict(post_ficha_routing)
    updated_post_ficha_routing["evidence_requests"] = updated_requests
    out_context["post_ficha_routing"] = updated_post_ficha_routing
    out_context["evidence_records"] = evidence_records

    blocking_assessments = [
        assessment for assessment in sufficiency.assessments if assessment.blocking
    ]
    requested_count = len(blocking_assessments)
    received_count = sum(bool(assessment.matched_evidence_ids) for assessment in blocking_assessments)
    satisfied_count = sum(
        assessment.status == ASSESSMENT_SATISFIED for assessment in blocking_assessments
    )
    missing_types = [
        assessment.evidence_type
        for assessment in blocking_assessments
        if assessment.status != ASSESSMENT_SATISFIED
    ]
    ready_for_analysis = sufficiency.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS
    readiness_state = "READY_FOR_ANALYSIS" if ready_for_analysis else "NEEDS_EVIDENCE"
    out_context["post_ficha_readiness"] = {
        "intake_id": intake_id,
        "readiness_state": readiness_state,
        "received_count": received_count,
        "satisfied_count": satisfied_count,
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

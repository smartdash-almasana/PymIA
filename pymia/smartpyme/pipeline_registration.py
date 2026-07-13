from __future__ import annotations

import hashlib
import json
from pathlib import Path


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _trace_metadata() -> dict:
    return {"registered_by": "vertical_pipeline", "channel": "cli"}


def _write_jsonl_line(target: Path, payload: dict) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
    return target


def register_anamnesis_record(
    message: str,
    tenant_id: str,
    intake_id: str,
    storage_dir: Path,
    *,
    business_taxonomy: dict | None = None,
) -> dict:
    from pymia.smartpyme.anamnesis import create_anamnesis_record
    from pymia.smartpyme.storage import save_anamnesis_record

    record = create_anamnesis_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        raw_owner_message=message,
        business_taxonomy=business_taxonomy,
        metadata=_trace_metadata(),
    )
    save_anamnesis_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_investigation_record(message: str, tenant_id: str, intake_id: str, anamnesis_id: str, storage_dir: Path) -> dict:
    from pymia.smartpyme.investigation import create_investigation_record
    from pymia.smartpyme.storage import save_investigation_record

    record = create_investigation_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        anamnesis_id=anamnesis_id,
        owner_prompt=message,
        metadata=_trace_metadata(),
    )
    save_investigation_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_owner_answer_record(
    *,
    tenant_id: str,
    intake_id: str,
    anamnesis_id: str,
    investigation_id: str,
    question_ref: str,
    raw_owner_answer: str,
    storage_dir: Path,
) -> dict:
    from pymia.smartpyme.owner_answer import create_owner_answer_record
    from pymia.smartpyme.storage import save_owner_answer_record

    record = create_owner_answer_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        anamnesis_id=anamnesis_id,
        investigation_id=investigation_id,
        question_ref=question_ref,
        raw_owner_answer=raw_owner_answer,
        metadata=_trace_metadata(),
    )
    save_owner_answer_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_evidence_request_record(
    *,
    tenant_id: str,
    intake_id: str,
    anamnesis_id: str,
    investigation_id: str,
    owner_answer_id: str | None,
    requested_evidence: list[str],
    request_reason: str,
    storage_dir: Path,
) -> dict:
    from pymia.smartpyme.evidence_request import (
        EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD,
        create_evidence_request_record,
    )
    from pymia.smartpyme.storage import save_evidence_request_record

    record = create_evidence_request_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        anamnesis_id=anamnesis_id,
        investigation_id=investigation_id,
        owner_answer_id=owner_answer_id,
        requested_evidence=requested_evidence,
        request_reason=request_reason,
        status=EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD,
        metadata=_trace_metadata(),
    )
    save_evidence_request_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_evidence_record(path: Path, tenant_id: str, intake_id: str, storage_dir: Path, request_id: str | None = None) -> dict:
    from pymia.smartpyme.evidence import (
        EVIDENCE_STATUS_REGISTERED,
        SOURCE_KIND_UPLOADED_FILE,
        create_evidence_record,
    )
    from pymia.smartpyme.storage import save_evidence_record

    record = create_evidence_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        request_id=request_id,
        evidence_type="xlsx_upload",
        source_kind=SOURCE_KIND_UPLOADED_FILE,
        source_ref=str(path),
        original_filename=path.name,
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        size_bytes=path.stat().st_size,
        content_hash=calculate_sha256(path),
        status=EVIDENCE_STATUS_REGISTERED,
        metadata=_trace_metadata(),
    )
    save_evidence_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_pipeline_run_record(
    *,
    tenant_id: str,
    intake_id: str,
    message: str,
    anamnesis_record: dict,
    investigation_record: dict,
    owner_answer_record: dict | None,
    evidence_request_record: dict | None,
    evidence_record: dict,
    structured_summary: dict,
    blocked: bool,
    storage_dir: Path,
) -> dict:
    from pymia.contracts.pipeline_run_v1 import build_pipeline_run_record

    output_payload = {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "anamnesis_id": anamnesis_record["anamnesis_id"],
        "investigation_id": investigation_record["investigation_id"],
        "evidence_id": evidence_record["evidence_id"],
        "structured_evidence_status": structured_summary["status"],
        "blocked": blocked,
    }
    if owner_answer_record:
        output_payload["owner_answer_id"] = owner_answer_record["answer_id"]
    if evidence_request_record:
        output_payload["evidence_request_id"] = evidence_request_record["request_id"]
    record = build_pipeline_run_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        message=message,
        evidence_ids=[evidence_record["evidence_id"]],
        status="BLOCKED" if blocked else "COMPLETED",
        output_payload=output_payload,
        steps_executed=[
            "evidence_record_registered",
            "structured_evidence_built",
            "evidence_sufficiency_checked",
            "owner_facing_report_built",
        ],
    )
    payload = record.model_dump(mode="json")
    payload["metadata"]["anamnesis_id"] = anamnesis_record["anamnesis_id"]
    payload["metadata"]["investigation_id"] = investigation_record["investigation_id"]
    if owner_answer_record:
        payload["metadata"]["owner_answer_id"] = owner_answer_record["answer_id"]
    if evidence_request_record:
        payload["metadata"]["evidence_request_id"] = evidence_request_record["request_id"]
    _write_jsonl_line(storage_dir / tenant_id / "pipeline_runs.jsonl", payload)
    return payload

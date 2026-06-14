from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _safe_join(base_dir: Path, tenant_id: str) -> Path:
    if not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if ".." in tenant_id or "/" in tenant_id or "\\" in tenant_id:
        raise ValueError("tenant_id contains invalid path traversal markers")
    target = (base_dir / tenant_id).resolve()
    base = base_dir.resolve()
    if base not in target.parents and target != base:
        raise ValueError("resolved path escapes base_dir")
    return target


def ensure_tenant_storage(base_dir: str | Path, tenant_id: str) -> dict[str, Path]:
    base = Path(base_dir).resolve()
    tenant_root = _safe_join(base, tenant_id)
    evidence_dir = tenant_root / "evidence"
    reports_dir = tenant_root / "reports"
    results_dir = tenant_root / "results"
    receptions_jsonl = tenant_root / "receptions.jsonl"
    intakes_jsonl = tenant_root / "intakes.jsonl"
    anamnesis_jsonl = tenant_root / "anamnesis.jsonl"
    investigations_jsonl = tenant_root / "investigations.jsonl"
    owner_answers_jsonl = tenant_root / "owner_answers.jsonl"
    evidences_jsonl = tenant_root / "evidences.jsonl"
    for d in (tenant_root, evidence_dir, reports_dir, results_dir):
        d.mkdir(parents=True, exist_ok=True)
    for jsonl in (
        receptions_jsonl,
        intakes_jsonl,
        anamnesis_jsonl,
        investigations_jsonl,
        owner_answers_jsonl,
        evidences_jsonl,
    ):
        if not jsonl.exists():
            jsonl.write_text("", encoding="utf-8")
    return {
        "tenant_root": tenant_root,
        "evidence_dir": evidence_dir,
        "reports_dir": reports_dir,
        "results_dir": results_dir,
        "receptions_jsonl": receptions_jsonl,
        "intakes_jsonl": intakes_jsonl,
        "anamnesis_jsonl": anamnesis_jsonl,
        "investigations_jsonl": investigations_jsonl,
        "owner_answers_jsonl": owner_answers_jsonl,
        "evidences_jsonl": evidences_jsonl,
    }


def _write_jsonl_line(target: Path, payload: dict[str, Any]) -> Path:
    line = json.dumps(payload, ensure_ascii=False)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return target


def _record_to_dict(record: Any, *, record_name: str) -> dict[str, Any]:
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return record.to_dict()
    if isinstance(record, dict):
        return record.copy()
    raise ValueError(f"{record_name} must be a supported record or dict")


def save_anamnesis_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    """Persiste un AnamnesisRecord o dict en <base_dir>/<tenant_id>/anamnesis.jsonl."""
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if base_dir is None:
        raise ValueError("base_dir is required")

    record_dict = _record_to_dict(record, record_name="record")

    if "tenant_id" not in record_dict:
        raise ValueError("record missing tenant_id field")
    if record_dict["tenant_id"] != tenant_id:
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match "
            f"argument tenant_id ({tenant_id})"
        )

    required_fields = [
        "anamnesis_id",
        "tenant_id",
        "intake_id",
        "raw_owner_message",
        "business_taxonomy",
        "declared_pains",
        "owner_hypotheses",
        "declared_documents",
        "requested_documents",
        "status",
        "created_at",
        "metadata",
    ]
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")

    if not isinstance(record_dict["business_taxonomy"], dict):
        raise ValueError("field business_taxonomy must be dict")
    if not isinstance(record_dict["metadata"], dict):
        raise ValueError("field metadata must be dict")
    for field in (
        "declared_pains",
        "owner_hypotheses",
        "declared_documents",
        "requested_documents",
    ):
        if not isinstance(record_dict[field], list):
            raise ValueError(f"field {field} must be list")

    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths["anamnesis_jsonl"], record_dict)


def save_investigation_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    """Persiste un InvestigationRecord o dict en <base_dir>/<tenant_id>/investigations.jsonl."""
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if base_dir is None:
        raise ValueError("base_dir is required")

    record_dict = _record_to_dict(record, record_name="record")

    if "tenant_id" not in record_dict:
        raise ValueError("record missing tenant_id field")
    if record_dict["tenant_id"] != tenant_id:
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match "
            f"argument tenant_id ({tenant_id})"
        )

    required_fields = [
        "investigation_id",
        "tenant_id",
        "intake_id",
        "anamnesis_id",
        "owner_prompt",
        "investigation_axis",
        "declared_question",
        "status",
        "evidence_required",
        "pathology_candidates",
        "formula_candidates",
        "created_at",
        "metadata",
    ]
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")

    if not isinstance(record_dict["metadata"], dict):
        raise ValueError("field metadata must be dict")
    for field in (
        "evidence_required",
        "pathology_candidates",
        "formula_candidates",
    ):
        if not isinstance(record_dict[field], list):
            raise ValueError(f"field {field} must be list")

    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths["investigations_jsonl"], record_dict)


def save_owner_answer_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    """Persiste un OwnerAnswerRecord o dict en <base_dir>/<tenant_id>/owner_answers.jsonl."""
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if base_dir is None:
        raise ValueError("base_dir is required")

    record_dict = _record_to_dict(record, record_name="record")

    if "tenant_id" not in record_dict:
        raise ValueError("record missing tenant_id field")
    if record_dict["tenant_id"] != tenant_id:
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match "
            f"argument tenant_id ({tenant_id})"
        )

    required_fields = [
        "answer_id",
        "tenant_id",
        "intake_id",
        "anamnesis_id",
        "investigation_id",
        "question_ref",
        "raw_owner_answer",
        "answer_kind",
        "created_at",
        "metadata",
    ]
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")

    if not isinstance(record_dict["metadata"], dict):
        raise ValueError("field metadata must be dict")

    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths["owner_answers_jsonl"], record_dict)


def save_evidence_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    """Persiste un EvidenceRecord o dict en <base_dir>/<tenant_id>/evidences.jsonl.

    Contrato aprobado:
        save_evidence_record(tenant_id, record, *, base_dir=None) -> Path
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if base_dir is None:
        raise ValueError("base_dir is required")

    record_dict = _record_to_dict(record, record_name="record")

    if "tenant_id" not in record_dict:
        raise ValueError("record missing tenant_id field")
    if record_dict["tenant_id"] != tenant_id:
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match "
            f"argument tenant_id ({tenant_id})"
        )

    required_fields = [
        "evidence_id",
        "tenant_id",
        "intake_id",
        "request_id",
        "evidence_type",
        "source_kind",
        "source_ref",
        "original_filename",
        "mime_type",
        "size_bytes",
        "content_hash",
        "status",
        "received_at",
        "notes",
        "metadata",
    ]
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")

    if not isinstance(record_dict["notes"], list):
        raise ValueError("field notes must be list")
    if not isinstance(record_dict["metadata"], dict):
        raise ValueError("field metadata must be dict")

    if record_dict["size_bytes"] is not None:
        if not isinstance(record_dict["size_bytes"], int) or isinstance(
            record_dict["size_bytes"], bool
        ):
            raise ValueError("field size_bytes must be int or None")

    nullable_str_fields = [
        "request_id",
        "original_filename",
        "mime_type",
        "content_hash",
    ]
    for field in nullable_str_fields:
        if record_dict[field] is not None and not isinstance(record_dict[field], str):
            raise ValueError(f"field {field} must be str or None")

    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths["evidences_jsonl"], record_dict)

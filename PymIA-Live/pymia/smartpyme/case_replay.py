from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pymia.smartpyme.anamnesis import normalize_business_taxonomy
from pymia.smartpyme.storage import _safe_join


_JSONL_SPECS = {
    "anamnesis": ("anamnesis.jsonl", "created_at", "anamnesis_id"),
    "investigations": ("investigations.jsonl", "created_at", "investigation_id"),
    "owner_answers": ("owner_answers.jsonl", "created_at", "answer_id"),
    "evidence_requests": ("evidence_requests.jsonl", "created_at", "request_id"),
    "evidences": ("evidences.jsonl", "received_at", "evidence_id"),
    "pipeline_runs": ("pipeline_runs.jsonl", "started_at", "run_id"),
}


def _minimal_taxonomic_signal_present(taxonomic_intake: dict[str, Any]) -> bool:
    has_declared_pains = bool(taxonomic_intake.get("dolores_declarados"))
    has_business_anchor = any(
        [
            taxonomic_intake.get("empresa_tipo") != "desconocido",
            taxonomic_intake.get("industria") != "desconocido",
            taxonomic_intake.get("modelo_comercial") != "desconocido",
            bool(taxonomic_intake.get("areas_criticas")),
        ]
    )
    return has_declared_pains and has_business_anchor


def _has_any_taxonomic_content(taxonomic_intake: dict[str, Any]) -> bool:
    return any(
        [
            taxonomic_intake.get("empresa_tipo") != "desconocido",
            taxonomic_intake.get("industria") != "desconocido",
            taxonomic_intake.get("modelo_comercial") != "desconocido",
            bool(taxonomic_intake.get("canales_venta")),
            bool(taxonomic_intake.get("areas_criticas")),
            taxonomic_intake.get("maneja_stock") is not None,
            taxonomic_intake.get("produce") is not None,
            taxonomic_intake.get("presta_servicios") is not None,
            bool(taxonomic_intake.get("dolores_declarados")),
            bool(taxonomic_intake.get("documentos_disponibles")),
        ]
    )


def _extract_taxonomic_intake(
    anamnesis_record: dict[str, Any] | None,
    warnings: list[str],
) -> dict[str, Any] | None:
    if not anamnesis_record:
        return None
    raw_taxonomy = anamnesis_record.get("business_taxonomy")
    if not raw_taxonomy:
        warnings.append("taxonomic_intake missing in anamnesis_record")
        return None

    normalized = normalize_business_taxonomy(
        raw_taxonomy,
        declared_pains=anamnesis_record.get("declared_pains"),
        declared_documents=anamnesis_record.get("declared_documents"),
    ).to_dict()
    if not _has_any_taxonomic_content(normalized):
        warnings.append("taxonomic_intake missing or empty in anamnesis_record")
        return None
    if not _minimal_taxonomic_signal_present(normalized):
        warnings.append("taxonomic_intake present but poor: missing declared pains or business anchor")
    return normalized


def _sort_records(records: list[dict[str, Any]], *, timestamp_key: str, id_key: str) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda record: (
            str(record.get(timestamp_key) or ""),
            str(record.get(id_key) or ""),
        ),
    )


def _load_jsonl_records(
    *,
    target: Path,
    tenant_id: str,
    intake_id: str,
    warnings: list[str],
) -> list[dict[str, Any]]:
    if not target.exists():
        return []

    records: list[dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f"Malformed JSONL line ignored in {target.name}:{line_number}")
                continue
            if not isinstance(payload, dict):
                warnings.append(f"Non-object JSONL line ignored in {target.name}:{line_number}")
                continue
            if payload.get("tenant_id") != tenant_id or payload.get("intake_id") != intake_id:
                continue
            records.append(payload)
    return records


def _collect_missing_links(
    *,
    anamnesis_record: dict[str, Any] | None,
    investigation_record: dict[str, Any] | None,
    owner_answer_records: list[dict[str, Any]],
    evidence_request_records: list[dict[str, Any]],
    evidence_records: list[dict[str, Any]],
    pipeline_run_records: list[dict[str, Any]],
) -> list[str]:
    missing: set[str] = set()

    if anamnesis_record is None:
        missing.add("anamnesis_record")
    if investigation_record is None:
        missing.add("investigation_record")
    if not evidence_records:
        missing.add("evidence_records")
    if not pipeline_run_records:
        missing.add("pipeline_run_records")

    answer_ids = {record.get("answer_id") for record in owner_answer_records}
    request_ids = {record.get("request_id") for record in evidence_request_records}
    evidence_ids = {record.get("evidence_id") for record in evidence_records}

    if anamnesis_record and investigation_record:
        if investigation_record.get("anamnesis_id") != anamnesis_record.get("anamnesis_id"):
            missing.add("investigation_record.anamnesis_id")

    for record in owner_answer_records:
        if anamnesis_record and record.get("anamnesis_id") != anamnesis_record.get("anamnesis_id"):
            missing.add(f"owner_answer:{record.get('answer_id')}:anamnesis_id")
        if investigation_record and record.get("investigation_id") != investigation_record.get("investigation_id"):
            missing.add(f"owner_answer:{record.get('answer_id')}:investigation_id")

    for record in evidence_request_records:
        if anamnesis_record and record.get("anamnesis_id") != anamnesis_record.get("anamnesis_id"):
            missing.add(f"evidence_request:{record.get('request_id')}:anamnesis_id")
        if investigation_record and record.get("investigation_id") != investigation_record.get("investigation_id"):
            missing.add(f"evidence_request:{record.get('request_id')}:investigation_id")
        owner_answer_id = record.get("owner_answer_id")
        if owner_answer_id and owner_answer_id not in answer_ids:
            missing.add(f"evidence_request:{record.get('request_id')}:owner_answer_id")

    for record in evidence_records:
        request_id = record.get("request_id")
        if request_id and request_id not in request_ids:
            missing.add(f"evidence:{record.get('evidence_id')}:request_id")

    for record in pipeline_run_records:
        record_evidence_ids = record.get("evidence_ids") or []
        if any(evidence_id not in evidence_ids for evidence_id in record_evidence_ids):
            missing.add(f"pipeline_run:{record.get('run_id')}:evidence_ids")
        metadata = record.get("metadata") or {}
        if anamnesis_record and metadata.get("anamnesis_id") != anamnesis_record.get("anamnesis_id"):
            missing.add(f"pipeline_run:{record.get('run_id')}:anamnesis_id")
        if investigation_record and metadata.get("investigation_id") != investigation_record.get("investigation_id"):
            missing.add(f"pipeline_run:{record.get('run_id')}:investigation_id")
        owner_answer_id = metadata.get("owner_answer_id")
        if owner_answer_id and owner_answer_id not in answer_ids:
            missing.add(f"pipeline_run:{record.get('run_id')}:owner_answer_id")
        evidence_request_id = metadata.get("evidence_request_id")
        if evidence_request_id and evidence_request_id not in request_ids:
            missing.add(f"pipeline_run:{record.get('run_id')}:evidence_request_id")

    return sorted(missing)


def replay_case_from_jsonl(
    *,
    storage_dir: Path,
    tenant_id: str,
    intake_id: str,
) -> dict:
    tenant_root = _safe_join(Path(storage_dir).resolve(), tenant_id)
    warnings: list[str] = []

    if not tenant_root.exists():
        return {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "status": "NOT_FOUND",
            "anamnesis_record": None,
            "investigation_record": None,
            "taxonomic_intake": None,
            "owner_answer_records": [],
            "evidence_request_records": [],
            "evidence_records": [],
            "pipeline_run_records": [],
            "latest_pipeline_run_record": None,
            "missing_links": [],
            "warnings": warnings,
        }

    anamnesis_records = _sort_records(
        _load_jsonl_records(
            target=tenant_root / _JSONL_SPECS["anamnesis"][0],
            tenant_id=tenant_id,
            intake_id=intake_id,
            warnings=warnings,
        ),
        timestamp_key=_JSONL_SPECS["anamnesis"][1],
        id_key=_JSONL_SPECS["anamnesis"][2],
    )
    investigation_records = _sort_records(
        _load_jsonl_records(
            target=tenant_root / _JSONL_SPECS["investigations"][0],
            tenant_id=tenant_id,
            intake_id=intake_id,
            warnings=warnings,
        ),
        timestamp_key=_JSONL_SPECS["investigations"][1],
        id_key=_JSONL_SPECS["investigations"][2],
    )
    owner_answer_records = _sort_records(
        _load_jsonl_records(
            target=tenant_root / _JSONL_SPECS["owner_answers"][0],
            tenant_id=tenant_id,
            intake_id=intake_id,
            warnings=warnings,
        ),
        timestamp_key=_JSONL_SPECS["owner_answers"][1],
        id_key=_JSONL_SPECS["owner_answers"][2],
    )
    evidence_request_records = _sort_records(
        _load_jsonl_records(
            target=tenant_root / _JSONL_SPECS["evidence_requests"][0],
            tenant_id=tenant_id,
            intake_id=intake_id,
            warnings=warnings,
        ),
        timestamp_key=_JSONL_SPECS["evidence_requests"][1],
        id_key=_JSONL_SPECS["evidence_requests"][2],
    )
    evidence_records = _sort_records(
        _load_jsonl_records(
            target=tenant_root / _JSONL_SPECS["evidences"][0],
            tenant_id=tenant_id,
            intake_id=intake_id,
            warnings=warnings,
        ),
        timestamp_key=_JSONL_SPECS["evidences"][1],
        id_key=_JSONL_SPECS["evidences"][2],
    )
    pipeline_run_records = _sort_records(
        _load_jsonl_records(
            target=tenant_root / _JSONL_SPECS["pipeline_runs"][0],
            tenant_id=tenant_id,
            intake_id=intake_id,
            warnings=warnings,
        ),
        timestamp_key=_JSONL_SPECS["pipeline_runs"][1],
        id_key=_JSONL_SPECS["pipeline_runs"][2],
    )

    all_records = (
        anamnesis_records
        + investigation_records
        + owner_answer_records
        + evidence_request_records
        + evidence_records
        + pipeline_run_records
    )
    if not all_records:
        return {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "status": "NOT_FOUND",
            "anamnesis_record": None,
            "investigation_record": None,
            "taxonomic_intake": None,
            "owner_answer_records": [],
            "evidence_request_records": [],
            "evidence_records": [],
            "pipeline_run_records": [],
            "latest_pipeline_run_record": None,
            "missing_links": [],
            "warnings": warnings,
        }

    anamnesis_record = anamnesis_records[-1] if anamnesis_records else None
    investigation_record = investigation_records[-1] if investigation_records else None
    latest_pipeline_run_record = pipeline_run_records[-1] if pipeline_run_records else None
    missing_links = _collect_missing_links(
        anamnesis_record=anamnesis_record,
        investigation_record=investigation_record,
        owner_answer_records=owner_answer_records,
        evidence_request_records=evidence_request_records,
        evidence_records=evidence_records,
        pipeline_run_records=pipeline_run_records,
    )
    taxonomic_intake = _extract_taxonomic_intake(anamnesis_record, warnings)
    required_ready = (
        anamnesis_record is not None
        and investigation_record is not None
        and bool(evidence_records)
        and latest_pipeline_run_record is not None
    )
    status = "REPLAY_READY" if required_ready and not missing_links else "PARTIAL_REPLAY"
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "status": status,
        "anamnesis_record": anamnesis_record,
        "investigation_record": investigation_record,
        "taxonomic_intake": taxonomic_intake,
        "owner_answer_records": owner_answer_records,
        "evidence_request_records": evidence_request_records,
        "evidence_records": evidence_records,
        "pipeline_run_records": pipeline_run_records,
        "latest_pipeline_run_record": latest_pipeline_run_record,
        "missing_links": missing_links,
        "warnings": warnings,
    }


__all__ = ["replay_case_from_jsonl"]

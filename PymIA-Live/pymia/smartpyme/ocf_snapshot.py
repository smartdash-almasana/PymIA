from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from pymia.smartpyme.case_replay import replay_case_from_jsonl


SnapshotStatus = Literal["SNAPSHOT_READY", "PARTIAL_SNAPSHOT", "NOT_FOUND"]


@dataclass(frozen=True)
class SnapshotBuildError(Exception):
    tenant_id: str
    intake_id: str
    missing_field: str
    reason: str


@dataclass(frozen=True)
class OrganizationalCaseFileSnapshot:
    case_id: str
    tenant_id: str
    intake_id: str
    case_status: SnapshotStatus
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    run_refs: list[dict[str, Any]] = field(default_factory=list)
    owner_answer_refs: list[dict[str, Any]] = field(default_factory=list)
    evidence_request_refs: list[dict[str, Any]] = field(default_factory=list)
    available_variables: list[dict[str, Any]] = field(default_factory=list)
    missing_variables: list[dict[str, Any]] = field(default_factory=list)
    open_unknowns: list[dict[str, Any]] = field(default_factory=list)
    next_questions: list[str] = field(default_factory=list)
    trace_refs: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)


_COVERAGE_FIELDS = [
    "case_id", "tenant_id", "intake_id", "case_status",
    "evidence_refs", "run_refs", "owner_answer_refs", "evidence_request_refs",
    "available_variables", "missing_variables", "open_unknowns",
    "next_questions", "trace_refs", "warnings",
]


def _compute_coverage(snapshot: OrganizationalCaseFileSnapshot) -> dict[str, Any]:
    total = len(_COVERAGE_FIELDS)
    populated = 0
    empty_with_warning = 0

    for field_name in _COVERAGE_FIELDS:
        value = getattr(snapshot, field_name)
        if field_name in ("warnings",):
            if value:
                populated += 1
            else:
                empty_with_warning += 1
            continue
        if field_name == "trace_refs":
            if any(v is not None for v in value.values()):
                populated += 1
            else:
                empty_with_warning += 1
            continue
        if isinstance(value, list):
            if value:
                populated += 1
            else:
                empty_with_warning += 1
        elif value is not None and value != "":
            populated += 1
        else:
            empty_with_warning += 1

    return {
        "total_fields": total,
        "populated_from_replay": populated,
        "empty_with_warning": empty_with_warning,
        "inferred_or_heuristic": 0,
        "coverage_from_replay": round(populated / total, 4) if total > 0 else 0.0,
        "heuristic_ratio": 0.0,
    }


def _derive_status(replay_status: str) -> SnapshotStatus:
    if replay_status == "NOT_FOUND":
        return "NOT_FOUND"
    if replay_status == "REPLAY_READY":
        return "SNAPSHOT_READY"
    return "PARTIAL_SNAPSHOT"


def _build_evidence_refs(evidence_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for record in evidence_records:
        refs.append({
            "evidence_id": record.get("evidence_id", ""),
            "evidence_type": record.get("evidence_type", ""),
            "source_kind": record.get("source_kind", ""),
            "status": record.get("status", ""),
            "trace_ref": f"evidences.jsonl:{record.get('evidence_id', 'unknown')}",
        })
    return refs


def _build_run_refs(pipeline_run_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for record in pipeline_run_records:
        refs.append({
            "run_id": record.get("run_id", ""),
            "pipeline_name": record.get("pipeline_name", ""),
            "status": record.get("status", ""),
            "trace_ref": f"pipeline_runs.jsonl:{record.get('run_id', 'unknown')}",
        })
    return refs


def _build_owner_answer_refs(owner_answer_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for record in owner_answer_records:
        refs.append({
            "answer_id": record.get("answer_id", ""),
            "question_ref": record.get("question_ref", ""),
            "answer_kind": record.get("answer_kind", ""),
            "trace_ref": f"owner_answers.jsonl:{record.get('answer_id', 'unknown')}",
        })
    return refs


def _build_evidence_request_refs(evidence_request_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for record in evidence_request_records:
        refs.append({
            "request_id": record.get("request_id", ""),
            "requested_evidence": record.get("requested_evidence", []),
            "status": record.get("status", ""),
            "trace_ref": f"evidence_requests.jsonl:{record.get('request_id', 'unknown')}",
        })
    return refs


def _extract_available_variables(
    replay: dict[str, Any],
    warnings: list[str],
) -> list[dict[str, Any]]:
    variables: list[dict[str, Any]] = []
    latest_run = replay.get("latest_pipeline_run_record")
    if latest_run:
        metadata = latest_run.get("metadata") or {}
        for key in ("computed_variables", "structured_summary"):
            raw = metadata.get(key)
            if isinstance(raw, dict):
                for var_name, var_value in raw.items():
                    if isinstance(var_name, str):
                        variables.append({
                            "variable": var_name,
                            "source": "pipeline_output",
                            "value": var_value,
                            "trace_ref": f"pipeline_runs.jsonl:{latest_run.get('run_id', 'unknown')}",
                        })

    owner_answers = replay.get("owner_answer_records") or []
    for answer in owner_answers:
        question_ref = answer.get("question_ref") or ""
        raw = answer.get("raw_owner_answer") or ""
        if question_ref and "owner_question:" in question_ref:
            var_name = question_ref.replace("owner_question:", "").strip()
            if var_name and not _has_variable(variables, var_name):
                variables.append({
                    "variable": var_name,
                    "source": "owner_declared",
                    "value": raw,
                    "trace_ref": f"owner_answers.jsonl:{answer.get('answer_id', 'unknown')}",
                })

    evidence_records = replay.get("evidence_records") or []
    for record in evidence_records:
        meta = record.get("metadata") or {}
        detected = meta.get("detected_variables")
        if isinstance(detected, dict):
            for var_name, var_value in detected.items():
                if isinstance(var_name, str) and not _has_variable(variables, var_name):
                    variables.append({
                        "variable": var_name,
                        "source": "structured_evidence",
                        "value": var_value,
                        "trace_ref": f"evidences.jsonl:{record.get('evidence_id', 'unknown')}",
                    })

    if not variables:
        warnings.append("available_variables empty: no variables found in replay outputs")
    return variables


def _has_variable(variables: list[dict[str, Any]], name: str) -> bool:
    return any(v.get("variable") == name for v in variables)


def _extract_missing_variables(
    replay: dict[str, Any],
    warnings: list[str],
) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    evidence_requests = replay.get("evidence_request_records") or []
    evidence_records = replay.get("evidence_records") or []

    existing_evidence_types: set[str] = set()
    for record in evidence_records:
        etype = record.get("evidence_type") or ""
        if etype:
            existing_evidence_types.add(etype)

    for request in evidence_requests:
        requested = request.get("requested_evidence") or []
        request_id = request.get("request_id", "unknown")
        for item in requested:
            if str(item) not in existing_evidence_types:
                missing.append({
                    "variable": str(item),
                    "reason": "requested in evidence request but no matching evidence received",
                    "requested_in": request_id,
                })

    if not missing and evidence_requests:
        warnings.append("missing_variables empty: no unmatched evidence found against requests")
    return missing


def _extract_open_unknowns(
    replay: dict[str, Any],
    warnings: list[str],
) -> list[dict[str, Any]]:
    unknowns: list[dict[str, Any]] = []

    investigation = replay.get("investigation_record")
    if investigation:
        goal = investigation.get("investigation_goal") or ""
        if goal:
            unknowns.append({
                "unknown": goal,
                "type": "unanswered_question",
                "source_ref": f"investigations.jsonl:{investigation.get('investigation_id', 'unknown')}",
            })

    evidence_requests = replay.get("evidence_request_records") or []
    for request in evidence_requests:
        reason = request.get("request_reason") or ""
        if reason:
            unknowns.append({
                "unknown": reason,
                "type": "missing_evidence",
                "source_ref": f"evidence_requests.jsonl:{request.get('request_id', 'unknown')}",
            })

    owner_answers = replay.get("owner_answer_records") or []
    UNCERTAINTY_MARKERS = ("no sé", "no se", "no estoy seguro", "no estoy segura", "no sabemos", "no tengo idea")
    for answer in owner_answers:
        raw = (answer.get("raw_owner_answer") or "").lower()
        if any(marker in raw for marker in UNCERTAINTY_MARKERS):
            unknowns.append({
                "unknown": answer.get("raw_owner_answer", ""),
                "type": "unanswered_question",
                "source_ref": f"owner_answers.jsonl:{answer.get('answer_id', 'unknown')}",
            })

    anamnesis = replay.get("anamnesis_record")
    if anamnesis and not unknowns:
        msg = anamnesis.get("raw_owner_message") or anamnesis.get("message") or ""
        if msg:
            unknowns.append({
                "unknown": msg,
                "type": "unanswered_question",
                "source_ref": f"anamnesis.jsonl:{anamnesis.get('anamnesis_id', 'unknown')}",
            })

    if not unknowns:
        warnings.append("open_unknowns empty: no unknowns derivable from replay")
    return unknowns


def _build_next_questions(open_unknowns: list[dict[str, Any]]) -> list[str]:
    questions: list[str] = []
    for unknown in open_unknowns:
        if unknown.get("type") == "missing_evidence":
            questions.append(f"Podrías subir evidencia sobre: {unknown.get('unknown', '')}")
        elif unknown.get("type") == "unanswered_question":
            questions.append(f"Necesitamos responder: {unknown.get('unknown', '')}")
    return questions


def _build_trace_refs(replay: dict[str, Any]) -> dict[str, Any]:
    anamnesis = replay.get("anamnesis_record")
    investigation = replay.get("investigation_record")
    latest_run = replay.get("latest_pipeline_run_record")
    return {
        "anamnesis_id": anamnesis.get("anamnesis_id") if anamnesis else None,
        "investigation_id": investigation.get("investigation_id") if investigation else None,
        "latest_pipeline_run_id": latest_run.get("run_id") if latest_run else None,
    }


def build_snapshot_from_replay(
    *,
    storage_dir: Path,
    tenant_id: str,
    intake_id: str,
) -> OrganizationalCaseFileSnapshot:
    if not tenant_id or not tenant_id.strip():
        raise SnapshotBuildError(
            tenant_id=tenant_id or "",
            intake_id=intake_id or "",
            missing_field="tenant_id",
            reason="tenant_id is required and must be non-empty",
        )
    if not intake_id or not intake_id.strip():
        raise SnapshotBuildError(
            tenant_id=tenant_id or "",
            intake_id=intake_id or "",
            missing_field="intake_id",
            reason="intake_id is required and must be non-empty",
        )

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    replay_tenant = replay.get("tenant_id", tenant_id)
    replay_intake = replay.get("intake_id", intake_id)

    if not replay_tenant or not replay_intake:
        raise SnapshotBuildError(
            tenant_id=tenant_id,
            intake_id=intake_id,
            missing_field="tenant_id" if not replay_tenant else "intake_id",
            reason="replay returned empty identity fields",
        )

    case_status = _derive_status(replay.get("status", "NOT_FOUND"))
    warnings: list[str] = list(replay.get("warnings") or [])

    evidence_refs = _build_evidence_refs(replay.get("evidence_records") or [])
    run_refs = _build_run_refs(replay.get("pipeline_run_records") or [])
    owner_answer_refs = _build_owner_answer_refs(replay.get("owner_answer_records") or [])
    evidence_request_refs = _build_evidence_request_refs(replay.get("evidence_request_records") or [])

    available_variables = _extract_available_variables(replay, warnings)
    missing_variables = _extract_missing_variables(replay, warnings)
    open_unknowns = _extract_open_unknowns(replay, warnings)
    next_questions = _build_next_questions(open_unknowns)
    trace_refs = _build_trace_refs(replay)

    snapshot = OrganizationalCaseFileSnapshot(
        case_id=replay_intake,
        tenant_id=replay_tenant,
        intake_id=replay_intake,
        case_status=case_status,
        evidence_refs=evidence_refs,
        run_refs=run_refs,
        owner_answer_refs=owner_answer_refs,
        evidence_request_refs=evidence_request_refs,
        available_variables=available_variables,
        missing_variables=missing_variables,
        open_unknowns=open_unknowns,
        next_questions=next_questions,
        trace_refs=trace_refs,
        warnings=warnings,
        coverage={},
    )

    object.__setattr__(snapshot, "coverage", _compute_coverage(snapshot))
    return snapshot


__all__ = [
    "OrganizationalCaseFileSnapshot",
    "SnapshotBuildError",
    "SnapshotStatus",
    "build_snapshot_from_replay",
]

from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    taxonomic_intake: dict[str, Any] | None = None
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    run_refs: list[dict[str, Any]] = field(default_factory=list)
    owner_answer_refs: list[dict[str, Any]] = field(default_factory=list)
    evidence_request_refs: list[dict[str, Any]] = field(default_factory=list)
    available_variables: list[dict[str, Any]] = field(default_factory=list)
    missing_variables: list[dict[str, Any]] = field(default_factory=list)
    open_unknowns: list[dict[str, Any]] = field(default_factory=list)
    next_questions: list[dict[str, Any]] = field(default_factory=list)
    trace_refs: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)


def build_snapshot_from_replay(
    *,
    storage_dir: Path,
    tenant_id: str,
    intake_id: str,
) -> OrganizationalCaseFileSnapshot:
    """Builds an OrganizationalCaseFileSnapshot from replay data.

    Raises SnapshotBuildError if tenant_id or intake_id are empty or if the case_status
    cannot be resolved.
    """
    if not tenant_id:
        raise SnapshotBuildError(
            tenant_id=tenant_id or "",
            intake_id=intake_id or "",
            missing_field="tenant_id",
            reason="tenant_id must be a non-empty string",
        )
    if not intake_id:
        raise SnapshotBuildError(
            tenant_id=tenant_id or "",
            intake_id=intake_id or "",
            missing_field="intake_id",
            reason="intake_id must be a non-empty string",
        )

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    replay_status = replay.get("status")
    if replay_status == "NOT_FOUND":
        case_status: SnapshotStatus = "NOT_FOUND"
    elif replay_status == "PARTIAL_REPLAY":
        case_status = "PARTIAL_SNAPSHOT"
    elif replay_status == "REPLAY_READY":
        case_status = "SNAPSHOT_READY"
    else:
        case_status = "NOT_FOUND"

    if not case_status:
        raise SnapshotBuildError(
            tenant_id=tenant_id,
            intake_id=intake_id,
            missing_field="case_status",
            reason="case_status is required and must not be empty",
        )

    warnings = list(replay.get("warnings") or [])
    taxonomic_intake = replay.get("taxonomic_intake")
    if taxonomic_intake is None and replay.get("anamnesis_record") is not None:
        warnings.append("taxonomic_intake missing from replay")
    available_variables_has_derived_entries = False
    missing_variables_is_derived = False
    open_unknowns_has_heuristic_entries = False
    next_questions_is_derived = False

    # Map evidence references
    evidence_refs: list[dict[str, Any]] = []
    for record in replay.get("evidence_records", []):
        ev_id = record.get("evidence_id")
        if not ev_id:
            warnings.append("evidence_id is missing in evidence record")
        evidence_refs.append({
            "evidence_id": ev_id,
            "evidence_type": record.get("evidence_type") or "unknown",
            "source_kind": record.get("source_kind") or "unknown",
            "status": record.get("status") or "unknown",
            "trace_ref": f"evidences.jsonl:{ev_id}",
        })

    # Map run references
    run_refs: list[dict[str, Any]] = []
    for record in replay.get("pipeline_run_records", []):
        run_id = record.get("run_id")
        if not run_id:
            warnings.append("run_id is missing in pipeline run record")
        ref: dict[str, Any] = {
            "run_id": run_id,
            "pipeline_name": record.get("pipeline_name") or "unknown",
            "status": record.get("status") or "unknown",
            "trace_ref": f"pipeline_runs.jsonl:{run_id}",
        }
        if "output_hash" in record:
            ref["output_hash"] = record["output_hash"]
        run_refs.append(ref)

    # Map owner answer references
    owner_answer_refs: list[dict[str, Any]] = []
    for record in replay.get("owner_answer_records", []):
        answer_id = record.get("answer_id")
        if not answer_id:
            warnings.append("answer_id is missing in owner answer record")
        owner_answer_refs.append({
            "answer_id": answer_id,
            "question_ref": record.get("question_ref") or "unknown",
            "answer_kind": record.get("answer_kind") or "unknown",
            "trace_ref": f"owner_answers.jsonl:{answer_id}",
        })

    # Map evidence request references
    evidence_request_refs: list[dict[str, Any]] = []
    for record in replay.get("evidence_request_records", []):
        request_id = record.get("request_id")
        if not request_id:
            warnings.append("request_id is missing in evidence request record")
        evidence_request_refs.append({
            "request_id": request_id,
            "requested_evidence": record.get("requested_evidence") or [],
            "status": record.get("status") or "unknown",
            "trace_ref": f"evidence_requests.jsonl:{request_id}",
        })

    # Extract available variables (highest priority first)
    available_variables: list[dict[str, Any]] = []
    seen_variables: set[str] = set()

    # 1. Pipeline runs
    latest_run = replay.get("latest_pipeline_run_record")
    if latest_run and isinstance(latest_run, dict):
        run_id = latest_run.get("run_id") or "unknown"
        metadata = latest_run.get("metadata") or {}
        for field_name in ["computed_variables", "variables", "detected_variables", "structured_summary"]:
            val = metadata.get(field_name)
            if isinstance(val, dict):
                if field_name == "structured_summary":
                    sub_comp = val.get("computed_variables") or val.get("variables")
                    if isinstance(sub_comp, dict):
                        for k, v in sub_comp.items():
                            if k not in seen_variables:
                                seen_variables.add(k)
                                available_variables.append({
                                    "variable": k,
                                    "source": "pipeline_output",
                                    "value": v,
                                    "trace_ref": f"pipeline_runs.jsonl:{run_id}",
                                })
                else:
                    for k, v in val.items():
                        if k not in seen_variables:
                            seen_variables.add(k)
                            available_variables.append({
                                "variable": k,
                                "source": "pipeline_output",
                                "value": v,
                                "trace_ref": f"pipeline_runs.jsonl:{run_id}",
                            })

    # Fallback to other run records if any
    for run in replay.get("pipeline_run_records", []):
        run_id = run.get("run_id") or "unknown"
        metadata = run.get("metadata") or {}
        for field_name in ["computed_variables", "variables", "detected_variables", "structured_summary"]:
            val = metadata.get(field_name)
            if isinstance(val, dict):
                if field_name == "structured_summary":
                    sub_comp = val.get("computed_variables") or val.get("variables")
                    if isinstance(sub_comp, dict):
                        for k, v in sub_comp.items():
                            if k not in seen_variables:
                                seen_variables.add(k)
                                available_variables.append({
                                    "variable": k,
                                    "source": "pipeline_output",
                                    "value": v,
                                    "trace_ref": f"pipeline_runs.jsonl:{run_id}",
                                })
                else:
                    for k, v in val.items():
                        if k not in seen_variables:
                            seen_variables.add(k)
                            available_variables.append({
                                "variable": k,
                                "source": "pipeline_output",
                                "value": v,
                                "trace_ref": f"pipeline_runs.jsonl:{run_id}",
                            })

    # 2. Owner answers
    for record in replay.get("owner_answer_records", []):
        q_ref = record.get("question_ref")
        if q_ref:
            var_name = q_ref.split(":")[-1] if ":" in q_ref else q_ref
            if var_name not in seen_variables:
                available_variables_has_derived_entries = True
                seen_variables.add(var_name)
                available_variables.append({
                    "variable": var_name,
                    "source": "owner_declared",
                    "value": record.get("raw_owner_answer"),
                    "trace_ref": f"owner_answers.jsonl:{record.get('answer_id')}",
                })

    # 3. Evidence records metadata
    for record in replay.get("evidence_records", []):
        ev_id = record.get("evidence_id") or "unknown"
        metadata = record.get("metadata") or {}
        for field_name in ["detected_variables", "computed_variables", "variables", "structured_evidence"]:
            val = metadata.get(field_name)
            if isinstance(val, dict):
                if field_name == "structured_evidence":
                    sub_comp = val.get("computed_variables") or val.get("variables")
                    if isinstance(sub_comp, dict):
                        for k, v in sub_comp.items():
                            if k not in seen_variables:
                                seen_variables.add(k)
                                available_variables.append({
                                    "variable": k,
                                    "source": "structured_evidence",
                                    "value": v,
                                    "trace_ref": f"evidences.jsonl:{ev_id}",
                                })
                else:
                    for k, v in val.items():
                        if k not in seen_variables:
                            seen_variables.add(k)
                            available_variables.append({
                                "variable": k,
                                "source": "structured_evidence",
                                "value": v,
                                "trace_ref": f"evidences.jsonl:{ev_id}",
                            })

    # Compare requested vs. received evidence
    received_types = {
        record.get("evidence_type")
        for record in replay.get("evidence_records", [])
        if record.get("status") != "REJECTED" and record.get("evidence_type")
    }

    missing_variables: list[dict[str, Any]] = []
    seen_missing: set[str] = set()

    for req_record in replay.get("evidence_request_records", []):
        req_id = req_record.get("request_id")
        reason = req_record.get("request_reason") or "Requested but not provided"
        requested = req_record.get("requested_evidence") or []
        for req_ev in requested:
            if req_ev not in received_types:
                if req_ev not in seen_missing:
                    missing_variables_is_derived = True
                    seen_missing.add(req_ev)
                    missing_variables.append({
                        "variable": req_ev,
                        "reason": reason,
                        "requested_in": req_id,
                    })

    # Open unknowns
    open_unknowns: list[dict[str, Any]] = []
    seen_unknowns: set[str] = set()

    inv_record = replay.get("investigation_record")
    if inv_record and isinstance(inv_record, dict):
        inv_id = inv_record.get("investigation_id")
        inv_goal = inv_record.get("investigation_goal") or inv_record.get("declared_question") or inv_record.get("owner_prompt")
        if inv_goal and inv_goal not in seen_unknowns:
            seen_unknowns.add(inv_goal)
            open_unknowns.append({
                "unknown": inv_goal,
                "type": "unanswered_question",
                "source_ref": f"investigations.jsonl:{inv_id}" if inv_id else None,
            })

    # Message from anamnesis if no active investigation axis
    anam_record = replay.get("anamnesis_record")
    if not inv_record and anam_record and isinstance(anam_record, dict):
        anam_id = anam_record.get("anamnesis_id")
        msg = anam_record.get("raw_owner_message")
        if msg and msg not in seen_unknowns:
            seen_unknowns.add(msg)
            open_unknowns.append({
                "unknown": msg,
                "type": "unanswered_question",
                "source_ref": f"anamnesis.jsonl:{anam_id}" if anam_id else None,
            })

    # Unfulfilled evidence requests
    for req_record in replay.get("evidence_request_records", []):
        reason = req_record.get("request_reason")
        req_id = req_record.get("request_id")
        if req_record.get("status") in ["OPEN", "WAITING_UPLOAD", "WAITING", None] or req_id in [mv["requested_in"] for mv in missing_variables]:
            if reason and reason not in seen_unknowns:
                seen_unknowns.add(reason)
                open_unknowns.append({
                    "unknown": reason,
                    "type": "missing_evidence",
                    "source_ref": f"evidence_requests.jsonl:{req_id}" if req_id else None,
                })

    # Uncertainty in owner answers
    uncertainty_keywords = ["no sé", "no se", "no estoy seguro", "no estoy segura", "no tengo", "no sabe", "no sabría", "no sabria", "no tengo certeza"]
    for ans_record in replay.get("owner_answer_records", []):
        ans = ans_record.get("raw_owner_answer")
        ans_id = ans_record.get("answer_id")
        if ans:
            ans_lower = ans.lower()
            if any(kw in ans_lower for kw in uncertainty_keywords):
                open_unknowns_has_heuristic_entries = True
                unknown_text = f"Duda declarada: {ans}"
                if unknown_text not in seen_unknowns:
                    seen_unknowns.add(unknown_text)
                    open_unknowns.append({
                        "unknown": unknown_text,
                        "type": "unanswered_question",
                        "source_ref": f"owner_answers.jsonl:{ans_id}" if ans_id else None,
                    })

    # Next questions
    next_questions: list[dict[str, Any]] = []
    for mv in missing_variables:
        next_questions_is_derived = True
        var = mv["variable"]
        next_questions.append({
            "question": f"¿Podés subir la evidencia de {var}?",
            "source_ref": f"evidence_requests.jsonl:{mv['requested_in']}" if mv.get("requested_in") else None,
        })
    for unknown in open_unknowns:
        if unknown["type"] == "unanswered_question":
            text = unknown["unknown"]
            if text.startswith("Duda declarada: "):
                text = text[len("Duda declarada: "):]
            next_questions_is_derived = True
            next_questions.append({
                "question": f"¿Podemos profundizar o aclarar: {text}?",
                "source_ref": unknown["source_ref"],
            })

    # Trace refs
    anam_id = None
    if anam_record:
        anam_id = anam_record.get("anamnesis_id")
    elif inv_record:
        anam_id = inv_record.get("anamnesis_id")

    inv_id = None
    if inv_record:
        inv_id = inv_record.get("investigation_id")

    run_id = None
    if latest_run:
        run_id = latest_run.get("run_id")

    trace_refs = {
        "anamnesis_id": anam_id,
        "investigation_id": inv_id,
        "latest_pipeline_run_id": run_id,
    }

    # Coverage metrics calculation
    total_fields = 15
    field_provenance = {
        "case_id": "derived_from_replay" if intake_id else "empty_with_warning",
        "tenant_id": "populated_from_replay" if tenant_id else "empty_with_warning",
        "intake_id": "populated_from_replay" if intake_id else "empty_with_warning",
        "case_status": "populated_from_replay" if case_status else "empty_with_warning",
        "taxonomic_intake": "populated_from_replay" if taxonomic_intake is not None else "empty_with_warning",
        "evidence_refs": "populated_from_replay" if evidence_refs else "empty_with_warning",
        "run_refs": "populated_from_replay" if run_refs else "empty_with_warning",
        "owner_answer_refs": "populated_from_replay" if owner_answer_refs else "empty_with_warning",
        "evidence_request_refs": "populated_from_replay" if evidence_request_refs else "empty_with_warning",
        "available_variables": (
            "derived_from_replay"
            if available_variables and available_variables_has_derived_entries
            else "populated_from_replay"
            if available_variables
            else "empty_with_warning"
        ),
        "missing_variables": "derived_from_replay" if missing_variables_is_derived else "empty_with_warning",
        "open_unknowns": (
            "inferred_or_heuristic"
            if open_unknowns and open_unknowns_has_heuristic_entries
            else "populated_from_replay"
            if open_unknowns
            else "empty_with_warning"
        ),
        "next_questions": "derived_from_replay" if next_questions_is_derived else "empty_with_warning",
        "trace_refs": "populated_from_replay" if any(trace_refs.values()) else "empty_with_warning",
        "warnings": "populated_from_replay" if warnings else "empty_with_warning",
    }
    populated = sum(1 for value in field_provenance.values() if value == "populated_from_replay")
    derived = sum(1 for value in field_provenance.values() if value == "derived_from_replay")
    inferred_or_heuristic = sum(1 for value in field_provenance.values() if value == "inferred_or_heuristic")
    empty_with_warning = sum(1 for value in field_provenance.values() if value == "empty_with_warning")
    coverage_from_replay = float(populated) / total_fields
    heuristic_ratio = float(inferred_or_heuristic) / total_fields

    coverage = {
        "total_fields": total_fields,
        "populated_from_replay": populated,
        "derived_from_replay": derived,
        "empty_with_warning": empty_with_warning,
        "inferred_or_heuristic": inferred_or_heuristic,
        "coverage_from_replay": coverage_from_replay,
        "heuristic_ratio": heuristic_ratio,
        "field_provenance": field_provenance,
    }

    return OrganizationalCaseFileSnapshot(
        case_id=intake_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        case_status=case_status,
        taxonomic_intake=taxonomic_intake,
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
        coverage=coverage,
    )


def compose_ocf_snapshot(
    *,
    storage_dir: Path,
    tenant_id: str,
    intake_id: str,
) -> dict[str, Any]:
    """Composes a dictionary representing the minimum OCF snapshot."""
    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )
    return asdict(snapshot)

from __future__ import annotations

from pymia.contracts.presentation_labels_v1 import label_for_field, label_for_pathology
from pymia.contracts.vertical_slice_copy_v1 import vertical_slice_copy_for
from pymia.smartpyme.question_alignment_gate import align_next_question


def _build_owner_question(entry: dict) -> tuple[str | None, str | None]:
    qs = entry.get("next_audit_questions", [])
    if not qs:
        return None, None
    pathology_code = entry.get("pathology_code", "")
    formula_id = entry.get("formula_id", "")
    missing = entry.get("missing_evidence", [])
    pathology_label = label_for_pathology(pathology_code)
    humanized_fields = [label_for_field(f) for f in missing]
    if humanized_fields:
        if len(humanized_fields) == 1:
            field_text = humanized_fields[0]
        elif len(humanized_fields) == 2:
            field_text = f"{humanized_fields[0]} y {humanized_fields[1]}"
        else:
            field_text = ", ".join(humanized_fields[:-1]) + f" y {humanized_fields[-1]}"
        owner_q = vertical_slice_copy_for("owner_question_missing_field").format(
            pathology_label=pathology_label,
            field_text=field_text,
        )
    else:
        owner_q = vertical_slice_copy_for("owner_question_missing_generic").format(
            pathology_label=pathology_label,
        )
    tech_parts = [f"Referencia técnica: {formula_id}"]
    if missing:
        tech_parts.append(f"inputs faltantes: {', '.join(missing)}")
    tech_ref = "; ".join(tech_parts)
    return owner_q, tech_ref


def _requested_evidence_from_report(report: dict) -> list[str]:
    requested: list[str] = []
    structured_summary = report.get("structured_evidence_summary") or {}
    if structured_summary.get("status") == "available":
        for entry in structured_summary.get("catalog_reconciliation") or []:
            for item in entry.get("missing_evidence") or []:
                if item not in requested:
                    requested.append(item)
    for item in report.get("missing_evidence") or []:
        if item not in requested:
            requested.append(item)
    return requested


def _resolve_owner_question_and_reference(report: dict, message: str) -> tuple[str | None, str | None]:
    structured_summary = report.get("structured_evidence_summary") or {}
    reconciliation = structured_summary.get("catalog_reconciliation") if structured_summary.get("status") == "available" else None
    owner_question = None
    tech_reference = None
    if reconciliation:
        question_candidates = [e for e in reconciliation if e.get("next_audit_questions")]
        alignment = align_next_question(message, question_candidates)
        if alignment["status"] == "MISALIGNED":
            owner_question = alignment["final_question_text"]
            tech_reference = alignment["technical_reference"]
        else:
            for entry in question_candidates:
                owner_q, tech_ref = _build_owner_question(entry)
                if owner_q:
                    owner_question = owner_q
                    tech_reference = tech_ref
                    break
    if not owner_question and report.get("next_questions"):
        owner_question = str(report["next_questions"][0])
    return owner_question, tech_reference

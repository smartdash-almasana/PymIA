from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.smartpyme.excel_lab_ingestion_v1 import build_structured_evidence_from_xlsx


def extract_formula_ids_from_intake_record(intake_record: Mapping[str, Any]) -> list[str]:
    evidence_requests = intake_record.get("evidence_requests") if isinstance(intake_record, Mapping) else None
    if not isinstance(evidence_requests, list):
        return []

    formula_ids: list[str] = []
    seen: set[str] = set()

    for request in evidence_requests:
        if not isinstance(request, Mapping):
            continue

        values: list[str] = []
        raw_formula_ids = request.get("formula_ids")
        if isinstance(raw_formula_ids, list):
            values.extend(str(item).strip() for item in raw_formula_ids if str(item).strip())

        raw_formula_id = request.get("formula_id")
        if isinstance(raw_formula_id, str) and raw_formula_id.strip():
            values.append(raw_formula_id.strip())

        for formula_id in values:
            if formula_id in seen:
                continue
            seen.add(formula_id)
            formula_ids.append(formula_id)

    return formula_ids


def build_structured_evidence_context(
    *,
    excel_path: str | Path,
    tenant_id: str,
    intake_record: Mapping[str, Any],
    document_type: str = "xlsx_operational_evidence",
) -> dict[str, Any]:
    evidence = build_structured_evidence_from_xlsx(
        excel_path=excel_path,
        tenant_id=tenant_id,
        document_type=document_type,
    )
    formula_ids = extract_formula_ids_from_intake_record(intake_record)
    return {
        "structured_evidence": evidence.model_dump(mode="json"),
        "formula_ids": list(formula_ids),
    }


__all__ = [
    "extract_formula_ids_from_intake_record",
    "build_structured_evidence_context",
]

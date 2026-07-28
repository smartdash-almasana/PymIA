from __future__ import annotations

from pymia.contracts.evidence_v1 import StructuredEvidence

from .models import EvidenceItem


def extract_evidence_pool(evidence: StructuredEvidence) -> list[EvidenceItem]:
    pool: list[EvidenceItem] = []

    for key, value in evidence.computed_variables.items():
        pool.append(
            EvidenceItem(
                id=f"computed:{key}",
                source="computed_variables",
                metric=key,
                value=value,
                context=f"Computed metric {key}",
            )
        )

    sheet_reports = evidence.metadata.get("sheet_reports", {})
    if isinstance(sheet_reports, dict):
        for sheet_name, status in sheet_reports.items():
            pool.append(
                EvidenceItem(
                    id=f"sheet:{sheet_name}:status",
                    source="sheet_reports",
                    metric="sheet_status",
                    value=status,
                    context=f"Sheet {sheet_name} is {status}",
                )
            )

    signals = evidence.metadata.get("signals", [])
    if isinstance(signals, list):
        for idx, signal in enumerate(signals):
            if not isinstance(signal, dict):
                continue
            sid = str(signal.get("signal_id") or f"signal_{idx+1}")
            metric = str(signal.get("signal_type") or "signal")
            severity = signal.get("severity")
            context = str(signal.get("description") or "")
            pool.append(
                EvidenceItem(
                    id=f"signal:{sid}",
                    source="signals",
                    metric=metric,
                    value=severity,
                    context=context,
                    details={
                        "suggested_action": signal.get("suggested_action"),
                        "raw": signal,
                    },
                )
            )

    return pool

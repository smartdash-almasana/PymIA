from __future__ import annotations

from .models import NarrativeReport


def render_markdown(report: NarrativeReport, *, include_trace_ids: bool = False) -> str:
    parts: list[str] = []
    for section in report.sections:
        parts.append(f"## {section.title}")
        for claim in section.claims:
            if include_trace_ids:
                refs = ", ".join(claim.evidence_ids)
                parts.append(f"- {claim.text} [{refs}]")
            else:
                parts.append(f"- {claim.text}")
        parts.append("")
    return "\n".join(parts).strip()

from __future__ import annotations

from pymia.smartpyme.finding_projection import ActionableFinding

from .models import EvidenceItem, NarrativeClaim, NarrativeReport, NarrativeSection


def build_evidence_pool_from_actionable_findings(
    findings: list[ActionableFinding],
) -> list[EvidenceItem]:
    pool: list[EvidenceItem] = []
    for index, finding in enumerate(findings, start=1):
        evidence_id = f"actionable_finding:{index}:{finding.metric}"
        pool.append(
            EvidenceItem(
                id=evidence_id,
                source="actionable_findings",
                metric=finding.metric,
                value=finding.severity,
                context=finding.difference,
                details={
                    "entity": finding.entity,
                    "source_comparison": finding.source_comparison,
                    "recommendation": finding.recommendation,
                    "evidence_refs": list(finding.evidence_refs),
                },
            )
        )
    return pool


def build_narrative_report_from_actionable_findings(
    findings: list[ActionableFinding],
) -> NarrativeReport:
    evidence_pool = build_evidence_pool_from_actionable_findings(findings)
    if not evidence_pool:
        return NarrativeReport(
            sections=[],
            trace={
                "version": "actionable_findings_v1",
                "findings_count": 0,
                "claims_count": 0,
                "status": "EMPTY",
            },
        )

    findings_section = NarrativeSection(title="Hallazgos principales", claims=[])
    actions_section = NarrativeSection(title="Acciones sugeridas", claims=[])

    for item, finding in zip(evidence_pool, findings, strict=True):
        findings_section.claims.append(
            NarrativeClaim(
                text=f"{finding.entity}: {finding.difference}.",
                evidence_ids=[item.id],
                expected_metric=finding.metric,
            )
        )
        if finding.recommendation:
            actions_section.claims.append(
                NarrativeClaim(
                    text=f"{finding.entity}: {finding.recommendation}",
                    evidence_ids=[item.id],
                    expected_metric=finding.metric,
                )
            )

    sections = [findings_section]
    if actions_section.claims:
        sections.append(actions_section)

    return NarrativeReport(
        sections=sections,
        trace={
            "version": "actionable_findings_v1",
            "findings_count": len(findings),
            "claims_count": sum(len(section.claims) for section in sections),
            "evidence_count": len(evidence_pool),
            "status": "OK",
        },
    )


__all__ = [
    "build_evidence_pool_from_actionable_findings",
    "build_narrative_report_from_actionable_findings",
]

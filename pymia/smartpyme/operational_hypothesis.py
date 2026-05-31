"""Operational hypothesis contract for SmartPyme.

Pure model helpers. It does NOT persist or execute analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HypothesisStatus(str, Enum):
    ABIERTA = "ABIERTA"
    EN_CONTRASTE = "EN_CONTRASTE"
    CONFIRMADA = "CONFIRMADA"
    DESCARTADA = "DESCARTADA"
    EVIDENCIA_INSUFICIENTE = "EVIDENCIA_INSUFICIENTE"


@dataclass
class OperationalHypothesis:
    hypothesis_id: str
    tenant_id: str
    intake_id: str
    formulation: str
    source: str
    domain: str
    related_symptoms: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    candidate_pathology_codes: list[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.ABIERTA
    findings_refs: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    closed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_hypothesis(
    *,
    hypothesis_id: str,
    tenant_id: str,
    intake_id: str,
    formulation: str,
    source: str,
    domain: str,
    related_symptoms: list[str] | None = None,
    required_evidence: list[str] | None = None,
    candidate_pathology_codes: list[str] | None = None,
) -> OperationalHypothesis:
    """Create an operational hypothesis contract object.

    Does NOT execute any kernel logic.
    """
    for name, value in {
        "hypothesis_id": hypothesis_id,
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "formulation": formulation,
        "source": source,
        "domain": domain,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    return OperationalHypothesis(
        hypothesis_id=hypothesis_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        formulation=formulation,
        source=source,
        domain=domain,
        related_symptoms=list(related_symptoms or []),
        required_evidence=list(required_evidence or []),
        candidate_pathology_codes=list(candidate_pathology_codes or []),
    )


_CANDIDATE_PATHOLOGY_CODES_BY_SYMPTOM: dict[str, tuple[str, ...]] = {
    "DESCUADRE_DINERO": ("LIQ_001", "LIQ_002", "PYME_013", "PYME_026", "PYME_046"),
    "MARGEN_DUDOSO": ("REN_001", "REN_002", "PYME_014", "PYME_017", "PYME_044", "PYME_048", "PYME_049"),
    "DATOS_DUPLICADOS": ("PYME_018", "PYME_022", "PYME_038"),
    "STOCK_INCONSISTENTE": ("INV_001", "INV_002", "PYME_008", "PYME_042"),
    "SOBRECARGA_MANUAL": ("PYME_015", "PYME_020", "PYME_040", "PYME_047"),
    "COSTO_INCIERTO": ("REN_002", "PYME_014", "PYME_048", "PYME_049"),
    "DOCUMENTACION_DESORDENADA": ("PYME_018", "PYME_022", "PYME_038"),
    "MAESTRO_DESORDENADO": ("PYME_018", "PYME_022"),
}


def derive_candidate_pathology_codes(candidate_symptoms: list[str]) -> list[str]:
    """Derive documented candidate pathologies without selecting a diagnosis."""
    codes: list[str] = []
    for symptom in candidate_symptoms:
        if not isinstance(symptom, str):
            continue
        for code in _CANDIDATE_PATHOLOGY_CODES_BY_SYMPTOM.get(symptom.strip(), ()):
            if code not in codes:
                codes.append(code)
    return codes


def build_operational_hypotheses_for_intake(
    *,
    tenant_id: str,
    intake_id: str,
    candidate_symptoms: list[str],
    candidate_domains: list[str],
    required_evidence: list[str],
) -> list[OperationalHypothesis]:
    """Build lightweight, contrastable hypotheses for a formal intake.

    This is intentionally conservative: one aggregate hypothesis anchors the
    current symptoms to the formal intake without diagnosing or running formulas.
    """
    symptoms = [
        symptom.strip()
        for symptom in candidate_symptoms
        if isinstance(symptom, str) and symptom.strip() and symptom.strip() != "DESCONOCIDO"
    ]
    if not symptoms:
        return []

    domains = [
        domain.strip()
        for domain in candidate_domains
        if isinstance(domain, str) and domain.strip() and domain.strip() != "DESCONOCIDO"
    ]
    domain = domains[0] if domains else "desconocido"
    evidence = list(dict.fromkeys(
        item.strip()
        for item in required_evidence
        if isinstance(item, str) and item.strip()
    ))
    formulation = (
        "Hipótesis operativa abierta a contrastar "
        f"en {domain}: {', '.join(symptoms)}"
    )
    return [
        create_hypothesis(
            hypothesis_id=f"{intake_id}_hyp_000",
            tenant_id=tenant_id,
            intake_id=intake_id,
            formulation=formulation,
            source="intake_interrogation",
            domain=domain,
            related_symptoms=symptoms,
            required_evidence=evidence,
            candidate_pathology_codes=derive_candidate_pathology_codes(symptoms),
        )
    ]


def update_hypothesis_status(
    hypothesis: OperationalHypothesis,
    new_status: HypothesisStatus | str,
    *,
    closed_at: str | None = None,
) -> OperationalHypothesis:
    """Return a new hypothesis with updated status.

    Does NOT mutate the input hypothesis.
    """
    if not isinstance(hypothesis, OperationalHypothesis):
        raise ValueError("hypothesis must be OperationalHypothesis")

    if isinstance(new_status, str):
        try:
            new_status = HypothesisStatus(new_status)
        except ValueError as exc:
            raise ValueError(f"invalid new_status: {new_status!r}") from exc

    if closed_at is None and new_status in {
        HypothesisStatus.CONFIRMADA,
        HypothesisStatus.DESCARTADA,
        HypothesisStatus.EVIDENCIA_INSUFICIENTE,
    }:
        closed_at = datetime.now(timezone.utc).isoformat()

    return replace(hypothesis, status=new_status, closed_at=closed_at)


__all__ = [
    "HypothesisStatus",
    "OperationalHypothesis",
    "create_hypothesis",
    "derive_candidate_pathology_codes",
    "build_operational_hypotheses_for_intake",
    "update_hypothesis_status",
]

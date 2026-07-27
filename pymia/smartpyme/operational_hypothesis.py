"""Operational hypothesis contract for SmartPyme.

Pure model helpers. It does NOT persist or execute analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pymia.services.catalog_loader_v1 import get_candidate_formula_ids_by_pathology_codes, load_formula_catalog_v1
from pymia.contracts.catalogs_v1 import FormulaCatalogV1
from pymia.smartpyme.evidence_requirement import EvidenceRequirement, create_evidence_requirement


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
    candidate_formula_ids: list[str] = field(default_factory=list)
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
    candidate_formula_ids: list[str] | None = None,
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
        candidate_formula_ids=list(candidate_formula_ids or []),
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
    candidate_pathology_codes = derive_candidate_pathology_codes(symptoms)
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
            candidate_pathology_codes=candidate_pathology_codes,
            candidate_formula_ids=get_candidate_formula_ids_by_pathology_codes(
                candidate_pathology_codes
            ),
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


def derive_evidence_requirements_from_formulas(
    hypothesis: OperationalHypothesis,
    *,
    tenant_id: str,
    intake_id: str,
    formula_catalog: FormulaCatalogV1 | None = None,
) -> list[EvidenceRequirement]:
    """Derive EvidenceRequirement objects from the hypothesis candidate_formula_ids.

    For each formula in candidate_formula_ids, reads required_evidence from the
    catalog and creates one EvidenceRequirement per unique evidence_type.

    Rules:
    - Uses the injected formula_catalog when provided (for tests).
    - Deduplicates by evidence_type while preserving every related formula_id.
    - blocks_analysis=True when formula.calculation_state == "CALCULABLE".
    - priority derived from priority_robustez (alta→1, media→2, else→3).
    - Does NOT execute formulas.
    - Does NOT persist anything.
    - Does NOT modify the hypothesis.
    """
    if not isinstance(hypothesis, OperationalHypothesis):
        raise ValueError("hypothesis must be an OperationalHypothesis")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id must be a non-empty string")
    if not isinstance(intake_id, str) or not intake_id.strip():
        raise ValueError("intake_id must be a non-empty string")

    if not hypothesis.candidate_formula_ids:
        return []

    catalog = formula_catalog if formula_catalog is not None else load_formula_catalog_v1()

    # Build lookup: formula_id -> entry
    formula_by_id = {f.formula_id: f for f in catalog.formulas}

    _PRIORITY_MAP = {"alta": 1, "media": 2}

    requirements_by_evidence_type: dict[str, EvidenceRequirement] = {}
    requirements: list[EvidenceRequirement] = []

    for formula_id in hypothesis.candidate_formula_ids:
        formula = formula_by_id.get(formula_id)
        if formula is None:
            continue

        priority_raw = getattr(formula, "priority_robustez", None) or "media"
        priority = _PRIORITY_MAP.get(str(priority_raw), 3)
        blocks = formula.calculation_state == "CALCULABLE"

        for evidence_type in formula.required_evidence:
            evidence_type = evidence_type.strip()
            if not evidence_type:
                continue
            existing = requirements_by_evidence_type.get(evidence_type)
            if existing is not None:
                if formula_id not in existing.formula_ids:
                    existing.formula_ids.append(formula_id)
                existing.blocks_analysis = existing.blocks_analysis or blocks
                existing.priority = min(existing.priority, priority)
                continue

            req_id = f"{intake_id}_catreq_{formula_id}_{evidence_type[:30]}"

            requirement = create_evidence_requirement(
                    requirement_id=req_id,
                    tenant_id=tenant_id,
                    intake_id=intake_id,
                    hypothesis_id=hypothesis.hypothesis_id,
                    formula_id=formula_id,
                    formula_ids=[formula_id],
                    evidence_type=evidence_type,
                    description=(
                        f"Requerimiento para fórmula '{formula.name}' "
                        f"(patología {formula.pathology_code})"
                    ),
                    required_fields=[],
                    reason=(
                        f"Necesario para contrastar hipótesis '{hypothesis.formulation[:60]}' "
                        f"mediante fórmula {formula_id}"
                    ),
                    blocks_analysis=blocks,
                    priority=priority,
                    telegram_message=(
                        f"Para analizar tu caso necesito: {evidence_type.replace('_', ' ')}"
                    ),
            )
            requirements_by_evidence_type[evidence_type] = requirement
            requirements.append(requirement)

    return requirements


__all__ = [
    "HypothesisStatus",
    "OperationalHypothesis",
    "create_hypothesis",
    "derive_candidate_pathology_codes",
    "build_operational_hypotheses_for_intake",
    "update_hypothesis_status",
    "derive_evidence_requirements_from_formulas",
]

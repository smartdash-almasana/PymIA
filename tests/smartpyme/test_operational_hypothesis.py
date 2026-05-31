from __future__ import annotations

from pymia.smartpyme.operational_hypothesis import (
    HypothesisStatus,
    build_operational_hypotheses_for_intake,
    create_hypothesis,
    derive_candidate_pathology_codes,
    update_hypothesis_status,
)
from pymia.services.catalog_loader_v1 import load_pathology_catalog_v1


def test_create_hypothesis_valid():
    h = create_hypothesis(
        hypothesis_id="h1",
        tenant_id="t1",
        intake_id="i1",
        formulation="margen erosionado",
        source="interrogation",
        domain="comercial",
        related_symptoms=["MARGEN_DUDOSO"],
    )
    assert h.status == HypothesisStatus.ABIERTA


def test_update_status_valid_transition():
    h = create_hypothesis(
        hypothesis_id="h1",
        tenant_id="t1",
        intake_id="i1",
        formulation="margen erosionado",
        source="interrogation",
        domain="comercial",
    )
    h2 = update_hypothesis_status(h, HypothesisStatus.EN_CONTRASTE)
    assert h.status == HypothesisStatus.ABIERTA
    assert h2.status == HypothesisStatus.EN_CONTRASTE


def test_update_does_not_mutate_input():
    h = create_hypothesis(
        hypothesis_id="h1",
        tenant_id="t1",
        intake_id="i1",
        formulation="margen erosionado",
        source="interrogation",
        domain="comercial",
    )
    before = h.to_dict()
    _ = update_hypothesis_status(h, "CONFIRMADA")
    assert h.to_dict() == before


def test_derive_candidate_pathology_codes_keeps_multiple_candidates():
    codes = derive_candidate_pathology_codes(["MARGEN_DUDOSO"])
    assert codes == [
        "REN_001",
        "REN_002",
        "PYME_014",
        "PYME_017",
        "PYME_044",
        "PYME_048",
        "PYME_049",
    ]


def test_build_hypothesis_candidates_exist_in_pathology_catalog():
    hypotheses = build_operational_hypotheses_for_intake(
        tenant_id="t1",
        intake_id="i1",
        candidate_symptoms=["MARGEN_DUDOSO", "SOBRECARGA_MANUAL"],
        candidate_domains=["comercial"],
        required_evidence=["excel_ventas_costos"],
    )
    catalog_codes = {
        entry.pathology_code
        for entry in load_pathology_catalog_v1().pathologies
    }
    assert hypotheses
    assert isinstance(hypotheses[0].candidate_pathology_codes, list)
    assert set(hypotheses[0].candidate_pathology_codes) <= catalog_codes

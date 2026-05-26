from __future__ import annotations

from pymia.smartpyme.operational_hypothesis import (
    HypothesisStatus,
    create_hypothesis,
    update_hypothesis_status,
)


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

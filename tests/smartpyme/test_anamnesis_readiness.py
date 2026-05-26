from __future__ import annotations

from pymia.smartpyme.anamnesis_readiness import (
    ReadinessStatus,
    evaluate_anamnesis_readiness,
)
from pymia.smartpyme.taxonomy import create_taxonomy_snapshot


def _base_snapshot(confidence: float):
    return create_taxonomy_snapshot(
        tenant_id="t1",
        organism_type="comercio",
        industry="retail",
        size="micro",
        complexity="mono_canal",
        sales_channels=["local"],
        operational_flow_stages=["compra", "venta_minorista"],
        systems_available=["excel"],
        confidence=confidence,
    )


def test_ready_with_confidence_and_valid_symptoms():
    s = _base_snapshot(0.8)
    ir = {"candidate_symptoms": ["MARGEN_DUDOSO"]}
    r = evaluate_anamnesis_readiness(s, ir)
    assert r.status == ReadinessStatus.READY


def test_needs_more_info_with_low_confidence():
    s = _base_snapshot(0.4)
    ir = {"candidate_symptoms": ["MARGEN_DUDOSO"]}
    r = evaluate_anamnesis_readiness(s, ir)
    assert r.status == ReadinessStatus.NEEDS_MORE_INFO


def test_needs_more_info_with_empty_candidate_symptoms():
    s = _base_snapshot(0.9)
    ir = {"candidate_symptoms": []}
    r = evaluate_anamnesis_readiness(s, ir)
    assert r.status == ReadinessStatus.NEEDS_MORE_INFO


def test_needs_more_info_with_only_desconocido():
    s = _base_snapshot(0.9)
    ir = {"candidate_symptoms": ["DESCONOCIDO"]}
    r = evaluate_anamnesis_readiness(s, ir)
    assert r.status == ReadinessStatus.NEEDS_MORE_INFO


def test_blocked_on_invalid_input_contract():
    ir = {"candidate_symptoms": ["MARGEN_DUDOSO"]}
    r = evaluate_anamnesis_readiness(snapshot=None, interrogation_result=ir)  # type: ignore[arg-type]
    assert r.status == ReadinessStatus.BLOCKED
    assert r.blocking_reasons

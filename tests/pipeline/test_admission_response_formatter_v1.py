"""
Tests para el formatter de respuesta del pipeline de admisión v1 — PymIA.
"""
import uuid
import pytest
from pymia.contracts.admission_v1 import DDIArtifact, SymptomNode, HypothesisNode
from pymia.pipeline.admission.v1.response_formatter import AdmissionResponseFormatterV1


@pytest.fixture
def formatter() -> AdmissionResponseFormatterV1:
    return AdmissionResponseFormatterV1()


@pytest.fixture
def sample_artifact() -> DDIArtifact:
    pyme_id = uuid.uuid4()
    symptom = SymptomNode(claim="vendemos mucho pero no queda plata")

    h1 = HypothesisNode(description="Tensión de caja", confidence_score=4.5, evidence_required=["ventas", "costos"])
    h2 = HypothesisNode(description="Margen erosionado", confidence_score=3.0, evidence_required=["ventas", "lista de precios"])
    h3 = HypothesisNode(description="Fuga operativa", confidence_score=3.0, evidence_required=["costos", "movimientos de caja"])

    hypotheses = [h1, h2, h3]

    return DDIArtifact(
        pyme_id=pyme_id,
        symptoms=[symptom],
        hypotheses=hypotheses,
        primary_hypothesis_id=h1.node_id,
    )


def test_formatter_includes_symptom(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert "Entiendo la señal: vendemos mucho pero no queda plata." in response


def test_formatter_keeps_uncertainty_without_technical_label(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert "Todavía no lo tomo como una conclusión cerrada" in response
    assert "lectura preliminar" in response
    assert "Estado epistemológico" not in response


def test_formatter_includes_primary_hypothesis_naturally(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert "Lo primero que revisaría es tensión de caja." in response


def test_formatter_includes_other_hypotheses_naturally(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    assert "También puede estar mezclado con margen erosionado, fuga operativa." in response


def test_formatter_includes_evidence_as_bullets(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    for evidence in ["costos", "lista de precios", "movimientos de caja", "ventas"]:
        assert f"- {evidence}" in response


def test_formatter_adheres_to_style_guide(formatter: AdmissionResponseFormatterV1, sample_artifact: DDIArtifact):
    response = formatter.format_response(sample_artifact)
    forbidden_terms = [
        "Hermes",
        "workflow",
        "job",
        "authorization",
        "orchestration",
        "lo paso a PymIA",
        "diagnóstico confirmado",
    ]
    for term in forbidden_terms:
        assert term not in response


def test_formatter_no_hypotheses_returns_none(formatter: AdmissionResponseFormatterV1):
    pyme_id = uuid.uuid4()
    artifact = DDIArtifact(
        pyme_id=pyme_id,
        symptoms=[SymptomNode(claim="un síntoma sin hipótesis")],
    )
    response = formatter.format_response(artifact)
    assert response is None

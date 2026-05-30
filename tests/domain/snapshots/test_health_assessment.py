"""Tests para HealthAssessment snapshot."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from pymia.domain.primitives.functional_organ import FunctionalOrgan
from pymia.domain.snapshots.health_assessment import HealthAssessment
from pymia.domain.types.functional_organ_type import FunctionalOrganType
from pymia.domain.types.health_classification import HealthClassification


def _make_organ(
    organ_type: FunctionalOrganType,
    state: str = "sano",
    capacity_score: float = 80.0,
    observed_at: datetime | None = None,
) -> FunctionalOrgan:
    """Helper para crear FunctionalOrgan con valores por defecto."""
    if observed_at is None:
        observed_at = datetime.now(timezone.utc)

    kwargs: dict = {
        "organ_type": organ_type,
        "state": state,
        "capacity_score": capacity_score,
        "observed_at": observed_at,
        "description": f"Descripción del órgano {organ_type.value}",
    }
    if state in ("enfermo", "critico"):
        kwargs["symptoms"] = [f"Síntoma de {organ_type.value}"]

    return FunctionalOrgan(**kwargs)


def _make_full_organs(
    state: str = "sano",
    capacity_score: float = 80.0,
    base_time: datetime | None = None,
) -> list[FunctionalOrgan]:
    """Crea los 7 órganos con el mismo estado y score."""
    if base_time is None:
        base_time = datetime.now(timezone.utc)
    return [
        _make_organ(t, state=state, capacity_score=capacity_score, observed_at=base_time)
        for t in FunctionalOrganType
    ]


def _make_assessment(**kwargs) -> HealthAssessment:
    """Helper para crear HealthAssessment con valores por defecto."""
    base_time = kwargs.get("assessed_at", datetime.now(timezone.utc))
    defaults = {
        "id": uuid4(),
        "organization_id": uuid4(),
        "organs": _make_full_organs(base_time=base_time),
        "assessed_at": base_time,
    }
    defaults.update(kwargs)
    return HealthAssessment(**defaults)


class TestHealthAssessmentConstruction:
    """Tests de construcción válida."""

    def test_valid_construction_minimal(self):
        """Construcción mínima con 7 órganos sanos."""
        assessment = _make_assessment()
        assert len(assessment.organs) == 7
        assert assessment.organization_id is not None
        assert assessment.assessor is None
        assert assessment.notes is None

    def test_valid_construction_full(self):
        """Construcción completa con todos los campos."""
        assessment = _make_assessment(
            assessor="consultor@pymia.com",
            notes="Evaluación trimestral Q2",
            metadata={"source": "quarterly_review"},
        )
        assert assessment.assessor == "consultor@pymia.com"
        assert assessment.notes == "Evaluación trimestral Q2"
        assert assessment.metadata == {"source": "quarterly_review"}

    def test_entity_has_uuid_id(self):
        """Cada instancia tiene UUID único."""
        a1 = _make_assessment()
        a2 = _make_assessment()
        assert a1.id != a2.id


class TestHealthAssessmentInvariants:
    """Tests de invariantes de dominio."""

    def test_rejects_wrong_organ_count(self):
        """Debe tener exactamente 7 órganos."""
        with pytest.raises(ValueError, match="7 elementos"):
            _make_assessment(organs=_make_full_organs()[:5])

    def test_rejects_duplicate_organ_types(self):
        """No puede haber dos órganos del mismo tipo."""
        base_time = datetime.now(timezone.utc)
        organs = _make_full_organs(base_time=base_time)
        # Reemplazar el segundo órgano por otro del mismo tipo que el primero
        organs[1] = _make_organ(
            FunctionalOrganType.CIRCULATORIO, observed_at=base_time
        )
        with pytest.raises(ValueError, match="mismo organ_type"):
            _make_assessment(organs=organs)

    def test_rejects_missing_organ_type(self):
        """Todos los tipos del enum deben estar representados."""
        base_time = datetime.now(timezone.utc)
        # Crear 7 órganos pero todos del mismo tipo
        organs = [
            _make_organ(FunctionalOrganType.CIRCULATORIO, observed_at=base_time)
            for _ in range(7)
        ]
        with pytest.raises(ValueError, match="mismo organ_type"):
            _make_assessment(organs=organs)

    def test_rejects_naive_assessed_at(self):
        """assessed_at debe ser timezone-aware."""
        with pytest.raises(ValueError, match="timezone-aware"):
            _make_assessment(assessed_at=datetime.now())  # naive

    def test_rejects_empty_assessor(self):
        """assessor no puede estar vacío tras strip."""
        with pytest.raises(ValueError, match="assessor"):
            _make_assessment(assessor="   ")


class TestHealthAssessmentProperties:
    """Tests de properties derivadas."""

    def test_global_score_is_average(self):
        """global_score es el promedio de capacity_score."""
        base_time = datetime.now(timezone.utc)
        scores = [90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 30.0]
        organs = [
            _make_organ(t, capacity_score=s, observed_at=base_time)
            for t, s in zip(FunctionalOrganType, scores)
        ]
        assessment = _make_assessment(organs=organs)
        expected = sum(scores) / len(scores)
        assert assessment.global_score == expected

    def test_clinical_classification_sano(self):
        """Todos sanos con buen score -> SANO."""
        assessment = _make_assessment(
            organs=_make_full_organs(state="sano", capacity_score=85.0)
        )
        assert assessment.clinical_classification == HealthClassification.SANO

    def test_clinical_classification_fragil_by_score(self):
        """Score bajo sin órganos enfermos -> FRAGIL."""
        assessment = _make_assessment(
            organs=_make_full_organs(state="sano", capacity_score=55.0)
        )
        assert assessment.clinical_classification == HealthClassification.FRAGIL

    def test_clinical_classification_fragil_by_organ(self):
        """Algún órgano frágil -> FRAGIL."""
        base_time = datetime.now(timezone.utc)
        organs = _make_full_organs(state="sano", capacity_score=85.0, base_time=base_time)
        organs[0] = _make_organ(
            FunctionalOrganType.CIRCULATORIO,
            state="fragil",
            capacity_score=60.0,
            observed_at=base_time,
        )
        assessment = _make_assessment(organs=organs)
        assert assessment.clinical_classification == HealthClassification.FRAGIL

    def test_clinical_classification_enfermo(self):
        """Algún órgano enfermo -> ENFERMO (aunque otros estén sanos)."""
        base_time = datetime.now(timezone.utc)
        organs = _make_full_organs(state="sano", capacity_score=85.0, base_time=base_time)
        organs[0] = _make_organ(
            FunctionalOrganType.CIRCULATORIO,
            state="enfermo",
            capacity_score=40.0,
            observed_at=base_time,
        )
        assessment = _make_assessment(organs=organs)
        assert assessment.clinical_classification == HealthClassification.ENFERMO

    def test_clinical_classification_critico_has_priority(self):
        """CRITICO tiene prioridad sobre ENFERMO."""
        base_time = datetime.now(timezone.utc)
        organs = _make_full_organs(state="sano", capacity_score=85.0, base_time=base_time)
        organs[0] = _make_organ(
            FunctionalOrganType.CIRCULATORIO,
            state="enfermo",
            capacity_score=40.0,
            observed_at=base_time,
        )
        organs[1] = _make_organ(
            FunctionalOrganType.RESPIRATORIO,
            state="critico",
            capacity_score=15.0,
            observed_at=base_time,
        )
        assessment = _make_assessment(organs=organs)
        assert assessment.clinical_classification == HealthClassification.CRITICO


class TestHealthAssessmentQueries:
    """Tests de métodos de consulta."""

    def test_critical_and_unhealthy_organs(self):
        """critical_organs y unhealthy_organs retornan listas correctas."""
        base_time = datetime.now(timezone.utc)
        organs = _make_full_organs(state="sano", capacity_score=85.0, base_time=base_time)
        organs[0] = _make_organ(
            FunctionalOrganType.CIRCULATORIO,
            state="critico",
            capacity_score=10.0,
            observed_at=base_time,
        )
        organs[1] = _make_organ(
            FunctionalOrganType.RESPIRATORIO,
            state="enfermo",
            capacity_score=40.0,
            observed_at=base_time,
        )
        assessment = _make_assessment(organs=organs)

        assert len(assessment.critical_organs()) == 1
        assert assessment.critical_organs()[0].organ_type == FunctionalOrganType.CIRCULATORIO

        assert len(assessment.unhealthy_organs()) == 2
        unhealthy_types = {o.organ_type for o in assessment.unhealthy_organs()}
        assert unhealthy_types == {
            FunctionalOrganType.CIRCULATORIO,
            FunctionalOrganType.RESPIRATORIO,
        }

    def test_fragile_and_healthy_organs(self):
        """fragile_organs y healthy_organs retornan listas correctas."""
        base_time = datetime.now(timezone.utc)
        organs = _make_full_organs(state="sano", capacity_score=85.0, base_time=base_time)
        organs[0] = _make_organ(
            FunctionalOrganType.CIRCULATORIO,
            state="fragil",
            capacity_score=60.0,
            observed_at=base_time,
        )
        assessment = _make_assessment(organs=organs)

        assert len(assessment.fragile_organs()) == 1
        assert len(assessment.healthy_organs()) == 6

    def test_get_organ_returns_correct(self):
        """get_organ retorna el órgano del tipo solicitado."""
        assessment = _make_assessment()
        organ = assessment.get_organ(FunctionalOrganType.DIGESTIVO)
        assert organ.organ_type == FunctionalOrganType.DIGESTIVO


class TestHealthAssessmentSerialization:
    """Tests de serialización."""

    def test_to_dict_and_from_dict_roundtrip(self):
        """Roundtrip to_dict -> from_dict preserva todos los campos."""
        base_time = datetime.now(timezone.utc)
        org_id = uuid4()
        organs = _make_full_organs(state="sano", capacity_score=80.0, base_time=base_time)
        original = _make_assessment(
            organization_id=org_id,
            organs=organs,
            assessed_at=base_time,
            assessor="consultor@pymia.com",
            notes="Evaluación de prueba",
            metadata={"source": "test"},
        )

        data = original.to_dict()
        restored = HealthAssessment.from_dict(data)

        assert restored.id == original.id
        assert restored.organization_id == original.organization_id
        assert len(restored.organs) == 7
        assert restored.assessed_at == original.assessed_at
        assert restored.assessor == original.assessor
        assert restored.notes == original.notes
        assert restored.metadata == {"source": "test"}
        assert restored.global_score == original.global_score
        assert restored.clinical_classification == original.clinical_classification

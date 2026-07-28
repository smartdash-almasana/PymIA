"""Tests para OrganizationalPathology entity (M10)."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from pymia.domain.types.functional_organ_type import FunctionalOrganType
from pymia.domain.types.pathology_severity import PathologySeverity
from pymia.domain.types.pathology_stage import PathologyStage
from pymia.domain.types.pathology_status import PathologyStatus
from pymia.domain.types.pathology_type import PathologyType
from pymia.domain.entities.organizational_pathology import OrganizationalPathology


def _make_pathology(**kwargs):
    """Helper para crear OrganizationalPathology con valores por defecto."""
    base_time = kwargs.get("diagnosed_at", datetime.now(timezone.utc))

    defaults = {
        "id": uuid4(),
        "name": "Fatiga decisional crónica del fundador",
        "description": "El fundador toma todas las decisiones sin delegar, generando cuellos de botella",
        "pathology_type": PathologyType.FATIGA_DECISIONAL_CRONICA,
        "severity": PathologySeverity.MODERADA,
        "stage": PathologyStage.AGUDA,
        "affected_organ_types": [FunctionalOrganType.NERVIOSO],
        "symptoms": ["Decisiones demoradas", "Cuellos de botella en aprobación"],
        "diagnosed_at": base_time,
        "created_at": base_time,
        "updated_at": base_time,
    }
    defaults.update(kwargs)
    return OrganizationalPathology(**defaults)


class TestOrganizationalPathologyConstruction:
    """Tests de construcción válida."""

    def test_valid_construction_minimal(self):
        """Construcción mínima con campos requeridos."""
        pathology = _make_pathology()
        assert pathology.status == PathologyStatus.ACTIVA
        assert pathology.name == "Fatiga decisional crónica del fundador"
        assert pathology.pathology_type == PathologyType.FATIGA_DECISIONAL_CRONICA
        assert len(pathology.affected_organ_types) == 1
        assert len(pathology.symptoms) == 2

    def test_valid_construction_full(self):
        """Construcción completa con todos los campos."""
        org_id = uuid4()
        assessment_id = uuid4()
        ki_id = uuid4()
        pathology = _make_pathology(
            organization_id=org_id,
            detected_in_assessment_id=assessment_id,
            evidence_knowledge_item_ids=[ki_id],
            metadata={"source": "entrevista_fundador"},
        )
        assert pathology.organization_id == org_id
        assert pathology.detected_in_assessment_id == assessment_id
        assert len(pathology.evidence_knowledge_item_ids) == 1
        assert pathology.metadata == {"source": "entrevista_fundador"}

    def test_entity_has_uuid_id(self):
        """Cada instancia tiene UUID único."""
        p1 = _make_pathology()
        p2 = _make_pathology()
        assert p1.id != p2.id


class TestOrganizationalPathologyInvariants:
    """Tests de invariantes de dominio."""

    def test_rejects_short_name(self):
        """name debe tener mínimo 5 caracteres."""
        with pytest.raises(ValueError, match="name"):
            _make_pathology(name="ABC")

    def test_rejects_short_description(self):
        """description debe tener mínimo 10 caracteres."""
        with pytest.raises(ValueError, match="description"):
            _make_pathology(description="Muy corta")

    def test_rejects_empty_affected_organ_types(self):
        """affected_organ_types no puede estar vacío."""
        with pytest.raises(ValueError, match="affected_organ_types"):
            _make_pathology(affected_organ_types=[])

    def test_rejects_duplicate_organ_types(self):
        """affected_organ_types no puede contener duplicados."""
        with pytest.raises(ValueError, match="duplicados"):
            _make_pathology(
                affected_organ_types=[
                    FunctionalOrganType.NERVIOSO,
                    FunctionalOrganType.NERVIOSO,
                ]
            )

    def test_rejects_grave_severity_without_symptoms(self):
        """severity GRAVE/CRITICA requiere symptoms no vacío."""
        with pytest.raises(ValueError, match="symptoms"):
            _make_pathology(
                severity=PathologySeverity.GRAVE,
                symptoms=[],
            )

    def test_rejects_resuelta_without_resolved_at(self):
        """status RESUELTA requiere resolved_at."""
        with pytest.raises(ValueError, match="RESUELTA"):
            _make_pathology(status=PathologyStatus.RESUELTA)

    def test_rejects_cronificada_with_aguda_stage(self):
        """status CRONIFICADA requiere stage CRONICA."""
        with pytest.raises(ValueError, match="CRONIFICADA"):
            _make_pathology(
                status=PathologyStatus.CRONIFICADA,
                stage=PathologyStage.AGUDA,
            )

    def test_rejects_inconsistent_timestamps(self):
        """Timestamps deben ser coherentes."""
        base_time = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="diagnosed_at"):
            _make_pathology(
                diagnosed_at=base_time - timedelta(hours=1),  # antes de created_at
                created_at=base_time,
            )


class TestOrganizationalPathologyMethods:
    """Tests de métodos de dominio."""

    def test_mark_resolved_transitions_correctly(self):
        """mark_resolved: ACTIVA → RESUELTA."""
        base_time = datetime.now(timezone.utc)
        pathology = _make_pathology(diagnosed_at=base_time)
        resolved_at = base_time + timedelta(days=30)
        pathology.mark_resolved(
            resolution_reason="Intervención exitosa con coaching ejecutivo",
            resolved_at=resolved_at,
        )
        assert pathology.status == PathologyStatus.RESUELTA
        assert pathology.resolution_reason == "Intervención exitosa con coaching ejecutivo"
        assert pathology.resolved_at == resolved_at

    def test_mark_chronic_transitions_correctly(self):
        """mark_chronic: ACTIVA + AGUDA → CRONIFICADA + CRONICA."""
        base_time = datetime.now(timezone.utc)
        pathology = _make_pathology(
            diagnosed_at=base_time,
            stage=PathologyStage.AGUDA,
        )
        chronic_at = base_time + timedelta(days=90)
        pathology.mark_chronic(chronic_at=chronic_at)
        assert pathology.status == PathologyStatus.CRONIFICADA
        assert pathology.stage == PathologyStage.CRONICA
        assert pathology.updated_at == chronic_at

    def test_reactivate_from_resuelta(self):
        """reactivate desde RESUELTA → ACTIVA."""
        base_time = datetime.now(timezone.utc)
        pathology = _make_pathology(diagnosed_at=base_time)
        pathology.mark_resolved(
            resolution_reason="Mejora temporal",
            resolved_at=base_time + timedelta(days=30),
        )
        reactivated_at = base_time + timedelta(days=60)
        pathology.reactivate(reactivated_at=reactivated_at)
        assert pathology.status == PathologyStatus.ACTIVA
        assert pathology.resolved_at is None
        assert pathology.resolution_reason is None

    def test_reactivate_from_cronificada(self):
        """reactivate desde CRONIFICADA → ACTIVA."""
        base_time = datetime.now(timezone.utc)
        pathology = _make_pathology(
            diagnosed_at=base_time,
            stage=PathologyStage.AGUDA,
        )
        pathology.mark_chronic(chronic_at=base_time + timedelta(days=90))
        reactivated_at = base_time + timedelta(days=120)
        pathology.reactivate(reactivated_at=reactivated_at)
        assert pathology.status == PathologyStatus.ACTIVA
        # stage se mantiene CRONICA (no se resetea automáticamente)

    def test_rejects_mark_resolved_from_resuelta(self):
        """mark_resolved desde RESUELTA eleva ValueError."""
        base_time = datetime.now(timezone.utc)
        pathology = _make_pathology(diagnosed_at=base_time)
        pathology.mark_resolved(
            resolution_reason="Resuelta",
            resolved_at=base_time + timedelta(days=30),
        )
        with pytest.raises(ValueError, match="ACTIVA"):
            pathology.mark_resolved(
                resolution_reason="Intento de resolver de nuevo",
                resolved_at=base_time + timedelta(days=60),
            )

    def test_rejects_mark_chronic_from_cronica(self):
        """mark_chronic desde stage CRONICA eleva ValueError."""
        pathology = _make_pathology(stage=PathologyStage.CRONICA)
        with pytest.raises(ValueError, match="AGUDA"):
            pathology.mark_chronic(chronic_at=datetime.now(timezone.utc))

    def test_rejects_reactivate_from_activa(self):
        """reactivate desde ACTIVA eleva ValueError."""
        pathology = _make_pathology()
        with pytest.raises(ValueError, match="RESUELTA o CRONIFICADA"):
            pathology.reactivate(reactivated_at=datetime.now(timezone.utc))


class TestOrganizationalPathologySerialization:
    """Tests de serialización."""

    def test_to_dict_and_from_dict_roundtrip(self):
        """Roundtrip to_dict → from_dict preserva todos los campos."""
        org_id = uuid4()
        assessment_id = uuid4()
        ki_id = uuid4()
        original = _make_pathology(
            organization_id=org_id,
            detected_in_assessment_id=assessment_id,
            evidence_knowledge_item_ids=[ki_id],
            metadata={"source": "diagnostico_trimestral"},
        )

        data = original.to_dict()
        restored = OrganizationalPathology.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.pathology_type == original.pathology_type
        assert restored.severity == original.severity
        assert restored.stage == original.stage
        assert restored.status == original.status
        assert restored.affected_organ_types == original.affected_organ_types
        assert restored.symptoms == original.symptoms
        assert restored.evidence_knowledge_item_ids == original.evidence_knowledge_item_ids
        assert restored.organization_id == original.organization_id
        assert restored.detected_in_assessment_id == original.detected_in_assessment_id
        assert restored.metadata == {"source": "diagnostico_trimestral"}

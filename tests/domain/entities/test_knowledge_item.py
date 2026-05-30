"""Tests para KnowledgeItem - entidad epistémica de Capa 3."""
import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from dataclasses import FrozenInstanceError

from pymia.domain.entities.knowledge_item import KnowledgeItem
from pymia.domain.types.epistemic_state import EpistemicState


# ============================================================
# Helpers
# ============================================================

def _make_ki(
    statement="Las PyMEs argentinas tienen decisión concentrada en el dueño",
    source="observation",
    evidence=None,
    tags=None,
    epistemic_state=EpistemicState.DECLARED,
    confidence=0.5,
    related_ki_ids=None,
    tenant_id=None,
    created_at=None,
    updated_at=None,
    validated_at=None,
    refuted_at=None,
    metadata=None,
):
    """Factory helper con defaults válidos."""
    return KnowledgeItem(
        id=uuid4(),
        statement=statement,
        source=source,
        evidence=evidence if evidence is not None else [],
        tags=tags if tags is not None else [],
        epistemic_state=epistemic_state,
        confidence=confidence,
        related_ki_ids=related_ki_ids if related_ki_ids is not None else [],
        tenant_id=tenant_id,
        created_at=created_at if created_at is not None else datetime.now(timezone.utc),
        updated_at=updated_at if updated_at is not None else datetime.now(timezone.utc),
        validated_at=validated_at,
        refuted_at=refuted_at,
        metadata=metadata,
    )


# ============================================================
# Construcción válida
# ============================================================

class TestValidConstruction:
    def test_valid_construction_minimal(self):
        """KI mínimo: statement + source."""
        ki = _make_ki()
        assert ki.statement.startswith("Las PyMEs")
        assert ki.source == "observation"
        assert ki.epistemic_state == EpistemicState.DECLARED
        assert ki.confidence == 0.5

    def test_valid_construction_full(self):
        """KI con todos los campos poblados."""
        tenant_id = uuid4()
        other_ki_id = uuid4()
        created_at = datetime.now(timezone.utc)
        validated_time = created_at + timedelta(seconds=1)
        
        ki = _make_ki(
            evidence=["Entrevista 1", "Análisis documental"],
            tags=["pyme", "decision"],
            epistemic_state=EpistemicState.VALIDATED,
            confidence=0.85,
            related_ki_ids=[other_ki_id],
            tenant_id=tenant_id,
            created_at=created_at,
            updated_at=validated_time,
            validated_at=validated_time,
            metadata={"domain": "organizational"},
        )
        
        assert len(ki.evidence) == 2
        assert len(ki.tags) == 2
        assert ki.epistemic_state == EpistemicState.VALIDATED
        assert ki.confidence == 0.85
        assert ki.related_ki_ids == [other_ki_id]
        assert ki.tenant_id == tenant_id
        assert ki.validated_at == validated_time
        assert ki.metadata["domain"] == "organizational"

    def test_entity_has_uuid_id(self):
        """KI tiene UUID único."""
        ki1 = _make_ki()
        ki2 = _make_ki()
        assert isinstance(ki1.id, UUID)
        assert ki1.id != ki2.id


# ============================================================
# Invariantes de contenido
# ============================================================

class TestContentInvariants:
    def test_rejects_short_statement(self):
        """Statement debe tener mínimo 10 caracteres."""
        with pytest.raises(ValueError, match="statement"):
            _make_ki(statement="Corto")

    def test_rejects_invalid_source(self):
        """Source debe estar en el vocabulario permitido."""
        with pytest.raises(ValueError, match="source"):
            _make_ki(source="invalid_source")

    def test_rejects_confidence_out_of_range(self):
        """Confidence debe estar en [0.0, 1.0]."""
        with pytest.raises(ValueError, match="confidence"):
            _make_ki(confidence=1.5)
        
        with pytest.raises(ValueError, match="confidence"):
            _make_ki(confidence=-0.1)

    def test_rejects_empty_tags_or_duplicates(self):
        """Tags no pueden estar vacíos ni duplicados."""
        # String vacío
        with pytest.raises(ValueError, match="tags"):
            _make_ki(tags=["pyme", ""])
        
        # Duplicados
        with pytest.raises(ValueError, match="tags"):
            _make_ki(tags=["pyme", "pyme"])


# ============================================================
# Invariantes de estado
# ============================================================

class TestStateInvariants:
    def test_validated_requires_evidence(self):
        """KI en estado VALIDATED requiere evidence no vacía."""
        with pytest.raises(ValueError, match="evidence"):
            _make_ki(
                epistemic_state=EpistemicState.VALIDATED,
                evidence=[],
            )

    def test_observed_requires_evidence(self):
        """KI en estado OBSERVED requiere evidence no vacía."""
        with pytest.raises(ValueError, match="evidence"):
            _make_ki(
                epistemic_state=EpistemicState.OBSERVED,
                evidence=[],
            )

    def test_validated_at_only_when_validated(self):
        """validated_at solo puede existir si estado es VALIDATED."""
        with pytest.raises(ValueError, match="validated_at"):
            _make_ki(
                epistemic_state=EpistemicState.DECLARED,
                validated_at=datetime.now(timezone.utc),
            )

    def test_refuted_at_only_when_refuted(self):
        """refuted_at solo puede existir si estado es REFUTED."""
        with pytest.raises(ValueError, match="refuted_at"):
            _make_ki(
                epistemic_state=EpistemicState.DECLARED,
                refuted_at=datetime.now(timezone.utc),
            )


# ============================================================
# Invariantes de red epistémica
# ============================================================

class TestNetworkInvariants:
    def test_rejects_self_reference_in_related_ki_ids(self):
        """related_ki_ids no puede contener auto-referencia."""
        ki_id = uuid4()
        with pytest.raises(ValueError, match="auto-referencia"):
            KnowledgeItem(
                id=ki_id,
                statement="Las PyMEs argentinas tienen decisión concentrada en el dueño",
                source="observation",
                related_ki_ids=[ki_id],
            )

    def test_rejects_duplicate_related_ki_ids(self):
        """related_ki_ids no puede contener duplicados."""
        other_id = uuid4()
        with pytest.raises(ValueError, match="related_ki_ids"):
            _make_ki(related_ki_ids=[other_id, other_id])


# ============================================================
# Invariantes temporales
# ============================================================

class TestTemporalInvariants:
    def test_rejects_inconsistent_timestamps(self):
        """updated_at debe ser >= created_at."""
        past = datetime.now(timezone.utc) - timedelta(days=1)
        present = datetime.now(timezone.utc)
        
        with pytest.raises(ValueError, match="updated_at"):
            KnowledgeItem(
                id=uuid4(),
                statement="Las PyMEs argentinas tienen decisión concentrada en el dueño",
                source="observation",
                created_at=present,
                updated_at=past,
            )


# ============================================================
# Métodos de dominio - ciclo de vida
# ============================================================

class TestLifecycleMethods:
    def test_validate_transitions_to_validated(self):
        """validate: OBSERVED → VALIDATED."""
        ki = _make_ki(
            epistemic_state=EpistemicState.OBSERVED,
            evidence=["Evidencia inicial"],
        )
        
        ki.validate(["Nueva evidencia"])
        
        assert ki.epistemic_state == EpistemicState.VALIDATED
        assert ki.validated_at is not None
        assert "Nueva evidencia" in ki.evidence

    def test_refute_transitions_to_refuted(self):
        """refute: VALIDATED → REFUTED."""
        created_at = datetime.now(timezone.utc)
        validated_at = created_at + timedelta(seconds=1)
        ki = _make_ki(
            epistemic_state=EpistemicState.VALIDATED,
            evidence=["Evidencia"],
            created_at=created_at,
            updated_at=validated_at,
            validated_at=validated_at,
        )
        
        ki.refute("Evidencia contradictoria encontrada")
        
        assert ki.epistemic_state == EpistemicState.REFUTED
        assert ki.refuted_at is not None
        assert "refutation_reasons" in ki.metadata
        assert "Evidencia contradictoria encontrada" in ki.metadata["refutation_reasons"]

    def test_archive_transitions_to_archived(self):
        """archive: cualquier estado → ARCHIVED."""
        ki = _make_ki()
        
        ki.archive("Conocimiento obsoleto")
        
        assert ki.epistemic_state == EpistemicState.ARCHIVED
        assert ki.metadata["archive_reason"] == "Conocimiento obsoleto"

    def test_reopen_from_refuted_to_declared(self):
        """reopen: REFUTED → DECLARED."""
        created_at = datetime.now(timezone.utc)
        refuted_at = created_at + timedelta(seconds=1)
        ki = _make_ki(
            epistemic_state=EpistemicState.REFUTED,
            created_at=created_at,
            updated_at=refuted_at,
            refuted_at=refuted_at,
        )
        
        ki.reopen()
        
        assert ki.epistemic_state == EpistemicState.DECLARED
        assert ki.refuted_at is None

    def test_rejects_invalid_transition_archived_to_anything(self):
        """ARCHIVED es terminal, no permite transiciones."""
        ki = _make_ki(epistemic_state=EpistemicState.ARCHIVED)
        
        with pytest.raises(ValueError, match="ARCHIVED"):
            ki.validate(["evidence"])
        
        with pytest.raises(ValueError, match="ARCHIVED"):
            ki.refute("reason")
        
        with pytest.raises(ValueError, match="ARCHIVED"):
            ki.archive("otra razón")
        
        with pytest.raises(ValueError, match="ARCHIVED"):
            ki.reopen()

    def test_rejects_invalid_transition_validated_to_declared(self):
        """No se puede des-validar (VALIDATED → DECLARED prohibido)."""
        created_at = datetime.now(timezone.utc)
        validated_at = created_at + timedelta(seconds=1)
        ki = _make_ki(
            epistemic_state=EpistemicState.VALIDATED,
            evidence=["Evidencia"],
            created_at=created_at,
            updated_at=validated_at,
            validated_at=validated_at,
        )
        
        # reopen solo funciona desde REFUTED
        with pytest.raises(ValueError, match="REFUTED"):
            ki.reopen()


# ============================================================
# Serialización
# ============================================================

class TestSerialization:
    def test_to_dict_and_from_dict_roundtrip(self):
        """to_dict + from_dict debe reconstruir KI idéntico."""
        tenant_id = uuid4()
        other_ki_id = uuid4()
        created_at = datetime.now(timezone.utc)
        validated_time = created_at + timedelta(seconds=1)
        
        ki_original = KnowledgeItem(
            id=uuid4(),
            statement="Las PyMEs argentinas tienen decisión concentrada en el dueño",
            source="observation",
            evidence=["Entrevista 1", "Análisis documental"],
            tags=["pyme", "decision"],
            epistemic_state=EpistemicState.VALIDATED,
            confidence=0.85,
            related_ki_ids=[other_ki_id],
            tenant_id=tenant_id,
            created_at=created_at,
            updated_at=validated_time,
            validated_at=validated_time,
            metadata={"domain": "organizational"},
        )
        
        # Serializar
        data = ki_original.to_dict()
        
        # Verificar estructura
        assert isinstance(data["id"], str)
        assert data["epistemic_state"] == "validated"
        assert isinstance(data["created_at"], str)
        
        # Reconstruir
        ki_reconstructed = KnowledgeItem.from_dict(data)
        
        # Verificar igualdad
        assert ki_reconstructed.id == ki_original.id
        assert ki_reconstructed.statement == ki_original.statement
        assert ki_reconstructed.source == ki_original.source
        assert ki_reconstructed.evidence == ki_original.evidence
        assert ki_reconstructed.tags == ki_original.tags
        assert ki_reconstructed.epistemic_state == ki_original.epistemic_state
        assert ki_reconstructed.confidence == ki_original.confidence
        assert ki_reconstructed.related_ki_ids == ki_original.related_ki_ids
        assert ki_reconstructed.tenant_id == ki_original.tenant_id
        assert ki_reconstructed.validated_at == ki_original.validated_at
        assert ki_reconstructed.metadata == ki_original.metadata

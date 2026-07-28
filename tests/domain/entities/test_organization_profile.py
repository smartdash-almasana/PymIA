"""
Tests para OrganizationProfile - entidad núcleo de Capa 2.

Valida:
- Construcción válida (mínima y completa)
- 9 invariantes de dominio
- Mutabilidad (entidad, no VO)
- Serialización to_dict / from_dict
- Métodos de dominio (add_commitment, add_relationship, mark_validated)

Trazabilidad:
- PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §2, §4, §5
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import uuid4

import pytest

from pymia.domain.entities.organization_profile import OrganizationProfile
from pymia.domain.primitives.exchange_commitment import ExchangeCommitment
from pymia.domain.primitives.organizational_constraint import OrganizationalConstraint
from pymia.domain.primitives.structural_relationship import StructuralRelationship
from pymia.domain.types.constraint_type import ConstraintType
from pymia.domain.types.epistemic_state import EpistemicState
from pymia.domain.types.relationship_weight import RelationshipWeight


def _make_commitment() -> ExchangeCommitment:
    return ExchangeCommitment(
        id=uuid4(),
        parties=["Textiles SA", "Cliente X"],
        object="Venta 100 remeras",
        conditions="Pago contado",
    )


def _make_constraint() -> OrganizationalConstraint:
    return OrganizationalConstraint(
        id=uuid4(),
        constraint_type=ConstraintType.CAJA,
        magnitude="limitada",
        description="Caja limitada",
        observed_at=datetime.now(timezone.utc),
    )


def _make_relationship(source_id=None, target_id=None) -> StructuralRelationship:
    return StructuralRelationship(
        id=uuid4(),
        source_id=source_id or uuid4(),
        target_id=target_id or uuid4(),
        weight=RelationshipWeight.ALTO,
        relationship_kind="comercial",
        description="Relación comercial",
    )


def _make_profile(**overrides) -> OrganizationProfile:
    defaults = dict(
        id=uuid4(),
        name="Textiles SA",
        identity_declared="Fábrica premium",
        identity_observed="Mix producción/importación",
        identity_operational="Productor textil",
        exchange_commitments=[_make_commitment()],
        constraints=[_make_constraint()],
        decision_principal="Dueño",
        founded_at=datetime(2010, 1, 1, tzinfo=timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return OrganizationProfile(**defaults)


# ============================================================================
# Construcción válida (3 tests)
# ============================================================================


def test_valid_construction_minimal():
    """Construcción válida con campos mínimos requeridos."""
    profile = _make_profile()
    assert profile.name == "Textiles SA"
    assert len(profile.exchange_commitments) == 1
    assert len(profile.constraints) == 1


def test_valid_construction_full():
    """Construcción válida con todos los campos poblados."""
    profile = _make_profile(
        relationships=[_make_relationship()],
        flow_revenue="Ventas mayoristas",
        flow_transformation="Producción textil",
        flow_expenses="Salarios + insumos",
        flow_result="Margen 30%",
        decision_process="Reunión semanal",
        decision_information="Excel + intuición",
        metadata={"sector": "textil"},
    )
    assert profile.flow_revenue == "Ventas mayoristas"
    assert profile.metadata == {"sector": "textil"}


def test_entity_has_uuid_id():
    """OrganizationProfile tiene UUID propio (entidad, no VO)."""
    p1 = _make_profile()
    p2 = _make_profile()
    assert isinstance(p1.id, type(uuid4()))
    assert p1.id != p2.id


# ============================================================================
# Invariantes de dominio (9 tests)
# ============================================================================


def test_rejects_empty_name():
    """name no vacío."""
    with pytest.raises(ValueError, match="name"):
        _make_profile(name="")


def test_rejects_short_name():
    """name largo >= 2."""
    with pytest.raises(ValueError, match="name"):
        _make_profile(name="X")


def test_rejects_empty_identity_declared():
    """identity_declared no vacío."""
    with pytest.raises(ValueError, match="identity_declared"):
        _make_profile(identity_declared="")


def test_rejects_empty_identity_observed():
    """identity_observed no vacío."""
    with pytest.raises(ValueError, match="identity_observed"):
        _make_profile(identity_observed="")


def test_rejects_empty_identity_operational():
    """identity_operational no vacío."""
    with pytest.raises(ValueError, match="identity_operational"):
        _make_profile(identity_operational="")


def test_rejects_empty_exchange_commitments():
    """exchange_commitments no vacío (MODEL §4: sin compromisos no hay organización)."""
    with pytest.raises(ValueError, match="exchange_commitment"):
        _make_profile(exchange_commitments=[])


def test_rejects_empty_constraints():
    """constraints no vacío (MODEL §7: toda PyME tiene restricciones)."""
    with pytest.raises(ValueError, match="constraint"):
        _make_profile(constraints=[])


def test_rejects_empty_decision_principal():
    """decision_principal no vacío (invariante PyME: decisión concentrada)."""
    with pytest.raises(ValueError, match="decision_principal"):
        _make_profile(decision_principal="")


def test_rejects_founded_at_after_created_at():
    """founded_at <= created_at (coherencia temporal)."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="founded_at"):
        _make_profile(
            founded_at=now + timedelta(days=1),
            created_at=now,
        )


def test_rejects_duplicate_commitment_ids():
    """exchange_commitments sin IDs duplicados."""
    commitment = _make_commitment()
    # Crear segundo commitment con mismo ID
    dup = ExchangeCommitment(
        id=commitment.id,
        parties=["A", "B"],
        object="Otro",
        conditions="Otras",
    )
    with pytest.raises(ValueError, match="IDs duplicados"):
        _make_profile(exchange_commitments=[commitment, dup])


def test_rejects_duplicate_relationship_pairs():
    """relationships sin pares (source_id, target_id) duplicados."""
    source = uuid4()
    target = uuid4()
    r1 = _make_relationship(source_id=source, target_id=target)
    r2 = _make_relationship(source_id=source, target_id=target)
    with pytest.raises(ValueError, match="duplicados"):
        _make_profile(relationships=[r1, r2])


# ============================================================================
# Mutabilidad (1 test)
# ============================================================================


def test_entity_is_mutable():
    """OrganizationProfile es mutable (entidad, no VO frozen)."""
    profile = _make_profile()
    original_name = profile.name
    profile.name = "Nuevo Nombre SA"
    assert profile.name == "Nuevo Nombre SA"
    assert profile.name != original_name


# ============================================================================
# Métodos de dominio (3 tests)
# ============================================================================


def test_to_dict_serialization():
    """to_dict produce estructura JSON-compatible."""
    profile = _make_profile()
    d = profile.to_dict()
    assert d["id"] == str(profile.id)
    assert d["name"] == "Textiles SA"
    assert "identity" in d
    assert "exchange_commitments" in d
    assert "constraints" in d
    assert "flow" in d
    assert "decision" in d
    assert d["epistemic_state"] == "declared"


def test_from_dict_roundtrip():
    """from_dict reconstruye el perfil desde to_dict."""
    original = _make_profile(
        relationships=[_make_relationship()],
        flow_revenue="Ventas",
        metadata={"k": "v"},
    )
    data = original.to_dict()
    reconstructed = OrganizationProfile.from_dict(data)
    assert reconstructed.id == original.id
    assert reconstructed.name == original.name
    assert reconstructed.identity_declared == original.identity_declared
    assert len(reconstructed.exchange_commitments) == len(original.exchange_commitments)
    assert len(reconstructed.relationships) == len(original.relationships)
    assert reconstructed.flow_revenue == "Ventas"
    assert reconstructed.metadata == {"k": "v"}


def test_mark_validated_changes_epistemic_state():
    """mark_validated cambia epistemic_state a VALIDATED."""
    profile = _make_profile()
    assert profile.epistemic_state == EpistemicState.DECLARED
    profile.mark_validated()
    assert profile.epistemic_state == EpistemicState.VALIDATED


# ============================================================================
# Composición (2 tests)
# ============================================================================


def test_add_commitment_validates_uniqueness():
    """add_commitment rechaza ID duplicado."""
    profile = _make_profile()
    commitment = _make_commitment()
    profile.add_commitment(commitment)
    with pytest.raises(ValueError, match="ya existe"):
        profile.add_commitment(commitment)


def test_add_relationship_validates_no_duplicates():
    """add_relationship rechaza par (source, target) duplicado."""
    profile = _make_profile()
    source = uuid4()
    target = uuid4()
    r1 = _make_relationship(source_id=source, target_id=target)
    r2 = _make_relationship(source_id=source, target_id=target)
    profile.add_relationship(r1)
    with pytest.raises(ValueError, match="ya existe"):
        profile.add_relationship(r2)

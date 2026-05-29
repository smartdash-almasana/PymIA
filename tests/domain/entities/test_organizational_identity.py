"""
Tests para OrganizationalIdentity — entidad de dominio (Capa 2).

18 tests que validan:
- Construcción válida (mínima y completa)
- 9 invariantes de dominio
- Mutabilidad
- Métodos de dominio (to_dict, from_dict, register_crisis, resolve_crisis, mark_validated)
"""
from uuid import uuid4

import pytest

from pymia.domain.entities.organizational_identity import OrganizationalIdentity
from pymia.domain.primitives.identity_crisis import IdentityCrisis
from pymia.domain.types.epistemic_state import EpistemicState
from pymia.domain.types.identity_layer import IdentityLayer


# ============================================================================
# Fixtures
# ============================================================================

def _make_identity(**overrides):
    """Helper para crear OrganizationalIdentity con valores válidos por defecto."""
    defaults = {
        "id": uuid4(),
        "identity_declared": "Empresa de servicios tecnológicos",
        "identity_observed": "Consultora de desarrollo de software",
        "identity_desired": "Líder regional en soluciones cloud",
        "identity_perceived": "Proveedor confiable de software a medida",
        "core_persistent": ["calidad técnica", "relaciones de largo plazo"],
        "layer_adaptable": ["servicios cloud", "metodologías ágiles"],
        "layer_peripheral": ["herramientas de desarrollo", "oficina física"],
        "active_crises": [],
        "divergence_declared_observed": 0.3,
        "divergence_desired_observed": 0.5,
        "divergence_perceived_declared": 0.2,
        "epistemic_state": EpistemicState.DECLARED,
    }
    defaults.update(overrides)
    return OrganizationalIdentity(**defaults)


def _make_crisis(severity: int = 5, **overrides):
    """Helper para crear IdentityCrisis con valores válidos."""
    defaults = {
        "id": uuid4(),
        "crisis_type": "negacion",
        "affected_layers": [IdentityLayer.NUCLEO_PERSISTENTE],
        "severity": severity,
        "description": "Crisis de identidad detectada",
    }
    defaults.update(overrides)
    return IdentityCrisis(**defaults)


# ============================================================================
# 1. Construcción válida (3 tests)
# ============================================================================

def test_valid_construction_minimal():
    """Construcción mínima válida: solo campos requeridos."""
    identity = OrganizationalIdentity(
        id=uuid4(),
        identity_declared="Empresa tecnológica",
        identity_observed="Consultora de software",
        identity_desired="Líder regional",
        identity_perceived="Proveedor confiable",
        core_persistent=["calidad técnica"],
    )
    assert identity.identity_declared == "Empresa tecnológica"
    assert identity.layer_adaptable == []
    assert identity.layer_peripheral == []
    assert identity.active_crises == []


def test_valid_construction_full():
    """Construcción completa con todos los campos poblados."""
    crisis = _make_crisis()
    identity = _make_identity(active_crises=[crisis])
    assert len(identity.active_crises) == 1
    assert len(identity.core_persistent) == 2
    assert len(identity.layer_adaptable) == 2


def test_entity_has_uuid_id():
    """Verificación de que el ID es UUID válido."""
    identity = _make_identity()
    assert isinstance(identity.id, type(uuid4()))


# ============================================================================
# 2. Invariantes de identidad (4 tests)
# ============================================================================

def test_rejects_empty_identity_declared():
    """Rechaza identity_declared vacío o muy corto."""
    with pytest.raises(ValueError, match="identity_declared"):
        _make_identity(identity_declared="ab")  # largo < 3


def test_rejects_empty_identity_observed():
    """Rechaza identity_observed vacío o muy corto."""
    with pytest.raises(ValueError, match="identity_observed"):
        _make_identity(identity_observed="   ")  # whitespace


def test_rejects_empty_identity_desired():
    """Rechaza identity_desired vacío o muy corto."""
    with pytest.raises(ValueError, match="identity_desired"):
        _make_identity(identity_desired="")


def test_rejects_empty_identity_perceived():
    """Rechaza identity_perceived vacío o muy corto."""
    with pytest.raises(ValueError, match="identity_perceived"):
        _make_identity(identity_perceived="x")


# ============================================================================
# 3. Invariantes de capas (2 tests)
# ============================================================================

def test_rejects_empty_core_persistent():
    """Rechaza core_persistent vacío."""
    with pytest.raises(ValueError, match="core_persistent"):
        _make_identity(core_persistent=[])


def test_allows_empty_adaptable_and_peripheral():
    """Permite layer_adaptable y layer_peripheral vacías."""
    identity = _make_identity(layer_adaptable=[], layer_peripheral=[])
    assert identity.layer_adaptable == []
    assert identity.layer_peripheral == []


# ============================================================================
# 4. Invariantes de divergencia (2 tests)
# ============================================================================

def test_rejects_divergence_below_zero():
    """Rechaza divergencia menor que 0.0."""
    with pytest.raises(ValueError, match="divergence_declared_observed"):
        _make_identity(divergence_declared_observed=-0.1)


def test_rejects_divergence_above_one():
    """Rechaza divergencia mayor que 1.0."""
    with pytest.raises(ValueError, match="divergence_desired_observed"):
        _make_identity(divergence_desired_observed=1.5)


# ============================================================================
# 5. Invariantes de crisis (2 tests)
# ============================================================================

def test_rejects_duplicate_crisis_ids():
    """Rechaza crisis con IDs duplicados."""
    crisis_id = uuid4()
    crisis1 = _make_crisis(id=crisis_id)
    crisis2 = _make_crisis(id=crisis_id)
    
    with pytest.raises(ValueError, match="IDs duplicados"):
        _make_identity(active_crises=[crisis1, crisis2])


def test_high_severity_crisis_requires_high_divergence():
    """Crisis con severity >= 7 requiere divergence >= 0.5."""
    crisis = _make_crisis(severity=8)
    
    with pytest.raises(ValueError, match="severity >= 7"):
        _make_identity(
            active_crises=[crisis],
            divergence_declared_observed=0.3,  # < 0.5
        )


# ============================================================================
# 6. Métodos de dominio (4 tests)
# ============================================================================

def test_to_dict_serialization():
    """Verifica que to_dict produce estructura JSON-compatible."""
    identity = _make_identity()
    d = identity.to_dict()
    
    assert "id" in d
    assert "identities" in d
    assert d["identities"]["declared"] == identity.identity_declared
    assert "layers" in d
    assert "divergences" in d
    assert d["divergences"]["declared_observed"] == 0.3


def test_from_dict_roundtrip():
    """Verifica reconstrucción completa desde diccionario."""
    crisis = _make_crisis()
    identity = _make_identity(active_crises=[crisis])
    
    d = identity.to_dict()
    reconstructed = OrganizationalIdentity.from_dict(d)
    
    assert reconstructed.id == identity.id
    assert reconstructed.identity_declared == identity.identity_declared
    assert len(reconstructed.active_crises) == 1
    assert reconstructed.active_crises[0].severity == crisis.severity


def test_register_crisis_validates_uniqueness():
    """register_crisis valida que no haya duplicados."""
    identity = _make_identity()
    crisis = _make_crisis()
    
    identity.register_crisis(crisis)
    assert len(identity.active_crises) == 1
    
    with pytest.raises(ValueError, match="Ya existe una crisis"):
        identity.register_crisis(crisis)


def test_resolve_crisis_removes_from_active():
    """resolve_crisis remueve crisis de la lista activa."""
    crisis = _make_crisis()
    identity = _make_identity(active_crises=[crisis])
    
    identity.resolve_crisis(crisis.id)
    assert len(identity.active_crises) == 0


# ============================================================================
# 7. Estado epistémico (1 test)
# ============================================================================

def test_mark_validated_changes_epistemic_state():
    """mark_validated cambia epistemic_state a VALIDATED."""
    identity = _make_identity(epistemic_state=EpistemicState.DECLARED)
    
    identity.mark_validated()
    assert identity.epistemic_state == EpistemicState.VALIDATED


# ============================================================================
# 8. Tests adicionales de validación (2 tests)
# ============================================================================

def test_layer_adaptable_rejects_empty_strings():
    """layer_adaptable no puede contener strings vacíos."""
    with pytest.raises(ValueError, match="layer_adaptable"):
        _make_identity(layer_adaptable=["servicio válido", "   "])


def test_layer_peripheral_rejects_empty_strings():
    """layer_peripheral no puede contener strings vacíos."""
    with pytest.raises(ValueError, match="layer_peripheral"):
        _make_identity(layer_peripheral=["", "herramienta válida"])

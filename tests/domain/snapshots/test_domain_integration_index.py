"""Tests para DomainIntegrationIndex."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from pymia.domain.snapshots.domain_integration_index import DomainIntegrationIndex
from pymia.domain.types.integration_chain_status import IntegrationChainStatus


def _make_index(**kwargs):
    defaults = {
        "id": uuid4(),
        "integration_summary": "Índice de integración del núcleo dominio V1",
        "completed_chains": {
            "estructura": IntegrationChainStatus.COMPLETA,
            "epistemica": IntegrationChainStatus.COMPLETA,
            "clinica": IntegrationChainStatus.COMPLETA,
        },
        "open_gaps": [],
        "generated_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return DomainIntegrationIndex(**defaults)


def test_valid_minimal_index():
    index = _make_index()
    assert index.is_v1_closed()
    assert not index.has_open_gaps()
    assert index.chain_count() == 3


def test_valid_index_with_ids_and_gaps():
    index = _make_index(
        completed_chains={
            "estructura": IntegrationChainStatus.COMPLETA,
            "tracking": IntegrationChainStatus.DIFERIDA,
        },
        open_gaps=["tracking longitudinal diferido"],
        included_entity_ids=[uuid4()],
        included_snapshot_ids=[uuid4()],
        included_knowledge_item_ids=[uuid4()],
        organization_id=uuid4(),
        generated_by="PymIA",
        metadata={"version": "v1"},
    )
    assert not index.is_v1_closed()
    assert index.has_open_gaps()
    assert index.entity_count() == 1
    assert index.snapshot_count() == 1
    assert index.knowledge_item_count() == 1


def test_is_frozen():
    index = _make_index()
    with pytest.raises(FrozenInstanceError):
        index.integration_summary = "otro"


def test_rejects_short_summary():
    with pytest.raises(ValueError, match="integration_summary"):
        _make_index(integration_summary="corto")


def test_rejects_empty_completed_chains():
    with pytest.raises(ValueError, match="completed_chains"):
        _make_index(completed_chains={})


def test_rejects_invalid_chain_status():
    with pytest.raises(ValueError, match="IntegrationChainStatus"):
        _make_index(completed_chains={"estructura": "completa"})


def test_rejects_empty_chain_name():
    with pytest.raises(ValueError, match="nombres vacíos"):
        _make_index(completed_chains={"   ": IntegrationChainStatus.COMPLETA})


def test_rejects_duplicate_open_gaps():
    with pytest.raises(ValueError, match="open_gaps"):
        _make_index(open_gaps=["gap", "gap"])


def test_rejects_duplicate_entity_ids():
    eid = uuid4()
    with pytest.raises(ValueError, match="included_entity_ids"):
        _make_index(included_entity_ids=[eid, eid])


def test_rejects_duplicate_snapshot_ids():
    sid = uuid4()
    with pytest.raises(ValueError, match="included_snapshot_ids"):
        _make_index(included_snapshot_ids=[sid, sid])


def test_rejects_duplicate_knowledge_item_ids():
    kid = uuid4()
    with pytest.raises(ValueError, match="included_knowledge_item_ids"):
        _make_index(included_knowledge_item_ids=[kid, kid])


def test_rejects_naive_generated_at():
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_index(generated_at=datetime.now())


def test_rejects_empty_generated_by():
    with pytest.raises(ValueError, match="generated_by"):
        _make_index(generated_by="   ")


def test_to_dict_and_from_dict_roundtrip():
    index = _make_index(
        included_entity_ids=[uuid4(), uuid4()],
        included_snapshot_ids=[uuid4()],
        included_knowledge_item_ids=[uuid4()],
        organization_id=uuid4(),
        generated_by="PymIA",
        metadata={"k": "v"},
    )
    data = index.to_dict()
    restored = DomainIntegrationIndex.from_dict(data)
    assert restored == index
    assert data["completed_chains"]["estructura"] == "completa"
    assert data["metadata"] == {"k": "v"}

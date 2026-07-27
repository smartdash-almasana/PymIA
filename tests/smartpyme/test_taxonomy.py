from __future__ import annotations

import copy
import pytest

from pymia.smartpyme.taxonomy import (
    TaxonomyType,
    create_taxonomy_snapshot,
    confirm_field,
)


def test_create_taxonomy_snapshot_valid():
    s = create_taxonomy_snapshot(
        tenant_id="t1",
        organism_type=TaxonomyType.comercio,
        industry="retail",
        size="micro",
        complexity="mono_canal",
        sales_channels=["local"],
        operational_flow_stages=["compra", "venta_minorista"],
        systems_available=["excel"],
        confidence=0.6,
    )
    assert s.tenant_id == "t1"
    assert s.organism_type == TaxonomyType.comercio
    assert s.confidence == 0.6


def test_confidence_out_of_range_fails():
    with pytest.raises(ValueError):
        create_taxonomy_snapshot(
            tenant_id="t1",
            organism_type="comercio",
            industry="retail",
            size="micro",
            complexity="mono",
            confidence=1.2,
        )


def test_confirm_field_does_not_mutate_and_increases_confidence():
    s = create_taxonomy_snapshot(
        tenant_id="t1",
        organism_type="comercio",
        industry="retail",
        size="micro",
        complexity="mono",
        confidence=0.5,
    )
    before = copy.deepcopy(s.to_dict())
    updated = confirm_field(s, "industry", "retail_moda", increment=0.2)
    assert s.to_dict() == before
    assert updated.industry == "retail_moda"
    assert updated.confidence == 0.7


def test_confirm_field_invalid_field_fails():
    s = create_taxonomy_snapshot(
        tenant_id="t1",
        organism_type="comercio",
        industry="retail",
        size="micro",
        complexity="mono",
        confidence=0.5,
    )
    with pytest.raises(ValueError):
        confirm_field(s, "field_x", "abc")

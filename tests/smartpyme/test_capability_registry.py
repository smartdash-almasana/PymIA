from __future__ import annotations

import pytest

from pymia.smartpyme.capability_registry import (
    get_capability,
    is_dispatcher_available,
    is_pipeline_certified,
    list_capabilities,
    load_registry,
)


def test_registry_loads_and_has_schema() -> None:
    registry = load_registry()
    assert "capabilities" in registry
    assert isinstance(registry["capabilities"], list)
    assert registry["capabilities"]
    first = registry["capabilities"][0]
    assert "capability_id" in first
    assert "status" in first


def test_get_excel_diagnostic_is_pipeline_certified() -> None:
    capability = get_capability("excel_diagnostic")
    assert capability["status"] == "PIPELINE_CERTIFIED"
    assert is_pipeline_certified("excel_diagnostic") is True


def test_supplier_duplicate_check_is_dispatcher_available_and_pipeline_certified() -> None:
    capability = get_capability("supplier_duplicate_check")
    assert capability["status"] == "PIPELINE_CERTIFIED"
    assert is_dispatcher_available("supplier_duplicate_check") is True
    assert is_pipeline_certified("supplier_duplicate_check") is True


def test_capability_ids_are_unique() -> None:
    capability_ids = [item["capability_id"] for item in list_capabilities()]
    assert len(capability_ids) == len(set(capability_ids))


def test_unknown_capability_raises_key_error() -> None:
    with pytest.raises(KeyError):
        get_capability("missing_capability")

from __future__ import annotations

import importlib

from pymia.smartpyme.service_1_column_understanding_canonical_extension_gate_v1 import (
    BLOCKED,
    PARTIAL,
    SCHEMA_VERSION,
    STATUS_READY,
    build_service_1_column_understanding_canonical_extension_gate_v1,
)


def test_gate_materializes_all_current_canonical_gaps() -> None:
    gate = build_service_1_column_understanding_canonical_extension_gate_v1()

    assert gate.schema_version == SCHEMA_VERSION
    assert gate.status == STATUS_READY
    assert {item.column_name for item in gate.candidates} == {
        "stock_inicial",
        "entradas",
        "salidas",
        "stock_final",
        "cliente",
        "medio_pago",
        "proveedor",
        "bonif",
    }


def test_gate_does_not_authorize_any_extension() -> None:
    gate = build_service_1_column_understanding_canonical_extension_gate_v1()

    assert gate.supported_count == 0
    assert gate.partial_count + gate.blocked_count == len(gate.candidates)
    assert gate.catalog_mutation_authorized is False
    assert gate.runtime_authorized is False
    assert gate.frontend_wiring_authorized is False


def test_stock_gaps_are_partial_not_mapped() -> None:
    gate = build_service_1_column_understanding_canonical_extension_gate_v1()
    by_name = {item.column_name: item for item in gate.candidates}

    for column_name in {"stock_inicial", "stock_final"}:
        item = by_name[column_name]
        assert item.status == PARTIAL
        assert any("stock" in value for value in item.matching_variables)
        assert item.blocking_reason


def test_unsupported_business_entities_remain_blocked() -> None:
    gate = build_service_1_column_understanding_canonical_extension_gate_v1()
    by_name = {item.column_name: item for item in gate.candidates}

    for column_name in {"proveedor", "bonif"}:
        assert by_name[column_name].status == BLOCKED
        assert by_name[column_name].matching_variables == ()
        assert "Add formula/catalog evidence" in (by_name[column_name].blocking_reason or "")


def test_gate_preserves_catalog_derivation_rule() -> None:
    gate = build_service_1_column_understanding_canonical_extension_gate_v1()

    assert gate.metadata["observational_only"] is True
    assert gate.metadata["variable_catalog_status"] == "CATALOG_ONLY_NOT_RUNTIME"
    assert gate.metadata["derivation_rule"] == "Unique required_variables from formula_catalog.v1.json."


def test_module_has_no_frontend_or_runtime_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_canonical_extension_gate_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_canonical_extension_gate_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
        "import openai",
        "import anthropic",
        "requests.",
        "subprocess",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION

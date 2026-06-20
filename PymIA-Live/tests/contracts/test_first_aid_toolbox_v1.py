from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from pymia.contracts.first_aid_toolbox_v1 import (
    get_first_aid_component,
    is_allowed_for_first_aid,
    list_first_aid_components,
    list_first_aid_compositions,
    load_first_aid_toolbox_contract,
    requires_guardrails,
)


def test_first_aid_toolbox_contract_loads_valid_json():
    contract = load_first_aid_toolbox_contract()

    assert isinstance(contract, dict)
    assert contract["schema_version"] == "1.0"
    assert contract["contract_id"] == "FIRST_AID_TOOLBOX_PACK_CONTRACT_V1"
    assert contract["status"] == "CANDIDATE_CONTRACT"
    assert contract["runtime_impact"] == "NONE"
    assert contract["implementation_authorized"] is False


def test_first_aid_toolbox_contract_file_is_parseable_json():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "first_aid_toolbox_v1.json"

    assert contract_path.exists()
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    assert payload["contract_id"] == "FIRST_AID_TOOLBOX_PACK_CONTRACT_V1"


def test_first_aid_toolbox_counts_match_expected_counts():
    contract = load_first_aid_toolbox_contract()
    components = contract["components"]
    counts = Counter(component["decision"] for component in components)
    expected_counts = contract["expected_counts"]

    assert len(components) == expected_counts["components_total"] == 27
    assert counts["USE_IN_PHASE_1"] == expected_counts["USE_IN_PHASE_1"] == 13
    assert counts["USE_IN_PHASE_1_WITH_GUARDRAILS"] == expected_counts["USE_IN_PHASE_1_WITH_GUARDRAILS"] == 9
    assert counts["NOT_FOR_PHASE_1_PHASE_2"] == expected_counts["NOT_FOR_PHASE_1_PHASE_2"] == 5
    assert counts["REVIEW_REQUIRED"] == expected_counts["REVIEW_REQUIRED"] == 0
    assert counts["DO_NOT_MIGRATE"] == expected_counts["DO_NOT_MIGRATE"] == 0
    assert counts["USE_IN_PHASE_1"] + counts["USE_IN_PHASE_1_WITH_GUARDRAILS"] == expected_counts[
        "phase_1_components_total"
    ] == 22


def test_first_aid_toolbox_has_unique_component_ids():
    components = list_first_aid_components()
    component_ids = [component["id"] for component in components]

    assert len(component_ids) == len(set(component_ids))


def test_first_aid_toolbox_components_use_allowed_decisions_and_types():
    contract = load_first_aid_toolbox_contract()
    allowed_decisions = set(contract["allowed_decisions"])
    allowed_component_types = set(contract["allowed_component_types"])

    for component in contract["components"]:
        assert component["decision"] in allowed_decisions
        assert component["component_type"] in allowed_component_types
        assert component["owner_limit"].strip()


def test_first_aid_toolbox_known_phase_1_components_are_allowed():
    assert is_allowed_for_first_aid("flujo_de_fondos") is True
    assert is_allowed_for_first_aid("proyeccion_ventas") is True
    assert is_allowed_for_first_aid("ExcelStructureValidationPack") is True
    assert is_allowed_for_first_aid("weekly_brief_structure") is True


def test_first_aid_toolbox_known_guardrail_components_require_guardrails():
    assert requires_guardrails("precio_margen") is True
    assert requires_guardrails("rentabilidad_por_producto") is True
    assert requires_guardrails("StockDesvioAlertRule") is True


def test_first_aid_toolbox_phase_2_components_are_not_allowed_for_first_aid():
    for component_id in [
        "auto_stock",
        "compras_y_proveedores",
        "control_de_gastos",
        "punto_equilibrio",
        "stock_control",
    ]:
        assert is_allowed_for_first_aid(component_id) is False
        assert requires_guardrails(component_id) is False


def test_first_aid_toolbox_unknown_component_is_not_allowed():
    assert get_first_aid_component("unknown_component") is None
    assert is_allowed_for_first_aid("unknown_component") is False
    assert requires_guardrails("unknown_component") is False


def test_first_aid_toolbox_rejects_blank_component_id():
    with pytest.raises(ValueError):
        get_first_aid_component(" ")


def test_first_aid_toolbox_compositions_are_closed_over_known_phase_1_components():
    known_components = {component["id"] for component in list_first_aid_components()}
    allowed_phase_1_components = {
        component["id"]
        for component in list_first_aid_components()
        if component["decision"] in {"USE_IN_PHASE_1", "USE_IN_PHASE_1_WITH_GUARDRAILS"}
    }

    compositions = list_first_aid_compositions()
    assert len(compositions) == load_first_aid_toolbox_contract()["expected_counts"]["compositions_total"] == 5

    for composition in compositions:
        assert composition["id"].strip()
        assert composition["output_limit"].strip()
        assert composition["component_ids"]
        for component_id in composition["component_ids"]:
            assert component_id in known_components
            assert component_id in allowed_phase_1_components


def test_first_aid_toolbox_smartexcel_is_separate_addendum_not_master_component():
    contract = load_first_aid_toolbox_contract()
    component_ids = {component["id"] for component in contract["components"]}

    smart_excel_addendum = contract["smart_excel_addendum"]
    assert smart_excel_addendum["status"] == "CANDIDATE_ADDENDUM_SEPARATE"
    assert smart_excel_addendum["included_in_master"] is False
    assert smart_excel_addendum["component_count"] == 7
    assert smart_excel_addendum["cross_cutting_count"] == 13
    assert smart_excel_addendum["do_not_migrate_count"] == 9

    assert "top_deudores_payload" not in component_ids
    assert "structured_warnings_payload" not in component_ids
    assert "exclude_ambiguous_amounts_rule" not in component_ids


def test_first_aid_toolbox_forbidden_language_is_declared():
    owner_language = load_first_aid_toolbox_contract()["owner_language"]

    for forbidden_verb in ["diagnostica", "confirma", "certifica", "garantiza"]:
        assert forbidden_verb in owner_language["forbidden_verbs"]

    for forbidden_claim in [
        "diagnóstico integral de la empresa",
        "rentabilidad real confirmada",
        "precio óptimo definitivo",
        "causa raíz confirmada",
    ]:
        assert forbidden_claim in owner_language["forbidden_claims"]


def test_first_aid_toolbox_loader_does_not_expose_runtime_keys():
    contract = load_first_aid_toolbox_contract()

    forbidden_runtime_keys = {"loader", "plugin", "executor", "entrypoint", "runtime_path", "module_path"}
    assert forbidden_runtime_keys.isdisjoint(contract.keys())
    for component in contract["components"]:
        assert forbidden_runtime_keys.isdisjoint(component.keys())

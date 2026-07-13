from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_entrypoint import evaluate_first_aid_entrypoint
from pymia.smartpyme.first_aid_toolbox_selector import select_first_aid_toolbox
from pymia.smartpyme import first_aid_toolbox_selector


def _ready_entrypoint():
    return evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Mirame este Excel y sacame algo en limpio.",
        has_file=True,
    )


def test_select_first_aid_toolbox_ready_returns_phase_1_components_and_compositions():
    selection = select_first_aid_toolbox(_ready_entrypoint())

    assert selection["status"] == "TOOLBOX_SELECTION_READY"
    assert selection["tenant_id"] == "tenant_1"
    assert selection["intake_id"] == "intake_1"
    assert selection["allowed_to_present_toolbox"] is True
    assert selection["next_allowed_action"] == "present_first_aid_toolbox_candidates"
    assert len(selection["components"]) == 22
    assert len(selection["compositions"]) == 5
    assert selection["warnings"] == []


def test_select_first_aid_toolbox_ready_does_not_include_phase_2_components():
    selection = select_first_aid_toolbox(_ready_entrypoint())
    component_ids = {component["id"] for component in selection["components"]}

    assert "flujo_de_fondos" in component_ids
    assert "precio_margen" in component_ids
    assert "auto_stock" not in component_ids
    assert "compras_y_proveedores" not in component_ids
    assert "control_de_gastos" not in component_ids
    assert "punto_equilibrio" not in component_ids
    assert "stock_control" not in component_ids


def test_select_first_aid_toolbox_compositions_are_enriched_with_component_views():
    selection = select_first_aid_toolbox(_ready_entrypoint())
    compositions_by_id = {composition["id"]: composition for composition in selection["compositions"]}

    excel_triage = compositions_by_id["excel_triage_basic"]
    assert excel_triage["component_ids"] == [
        "ExcelStructureValidationPack",
        "flujo_de_fondos",
        "proyeccion_ventas",
        "partial_data_copy",
        "not_calculable_na_copy",
    ]
    assert [component["id"] for component in excel_triage["components"]] == excel_triage["component_ids"]
    assert all(component["owner_limit"].strip() for component in excel_triage["components"])


def test_select_first_aid_toolbox_keeps_smartexcel_out_of_selection():
    selection = select_first_aid_toolbox(_ready_entrypoint())
    component_ids = {component["id"] for component in selection["components"]}

    assert "top_deudores_payload" not in component_ids
    assert "structured_warnings_payload" not in component_ids
    assert "exclude_ambiguous_amounts_rule" not in component_ids


def test_select_first_aid_toolbox_needs_evidence_blocks_selection():
    entrypoint = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Sacame algo en limpio de esta planilla.",
        has_file=False,
    )

    selection = select_first_aid_toolbox(entrypoint)

    assert selection["status"] == "TOOLBOX_SELECTION_NEEDS_EVIDENCE"
    assert selection["allowed_to_present_toolbox"] is False
    assert selection["next_allowed_action"] == "request_minimal_evidence"
    assert selection["components"] == []
    assert selection["compositions"] == []
    assert selection["warnings"] == [
        "FIRST_AID toolbox selection requires minimal evidence before presenting candidates."
    ]


def test_select_first_aid_toolbox_not_first_aid_blocks_selection():
    entrypoint = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="No sé si gano y no me cierra la caja.",
        has_file=True,
        taxonomic_intake={"dolores_declarados": ["no sé si gano"]},
    )

    selection = select_first_aid_toolbox(entrypoint)

    assert selection["status"] == "TOOLBOX_SELECTION_NOT_ALLOWED"
    assert selection["allowed_to_present_toolbox"] is False
    assert selection["next_allowed_action"] == "request_cross_source_evidence"
    assert selection["components"] == []
    assert selection["compositions"] == []
    assert selection["warnings"] == ["FIRST_AID toolbox selection is not allowed for this service depth."]


def test_select_first_aid_toolbox_rejects_invalid_verdict_shape():
    with pytest.raises(ValueError):
        select_first_aid_toolbox({})  # type: ignore[arg-type]

    verdict = _ready_entrypoint()
    verdict["tenant_id"] = ""
    with pytest.raises(ValueError):
        select_first_aid_toolbox(verdict)


def test_first_aid_toolbox_selector_does_not_touch_runtime_or_pipeline():
    source = inspect.getsource(first_aid_toolbox_selector)

    assert "vertical_pipeline" not in source
    assert "diagnostic_core" not in source
    assert "ocf_snapshot" not in source
    assert "case_replay" not in source
    assert "storage" not in source
    assert "subprocess" not in source
    assert "argparse" not in source
    assert "open(" not in source


def test_first_aid_toolbox_selector_only_depends_on_entrypoint_and_contract():
    source = inspect.getsource(first_aid_toolbox_selector)

    assert "first_aid_entrypoint" in source
    assert "first_aid_toolbox_v1" in source
    assert "formula_engine_service" not in source
    assert "pathology_engine_service" not in source

from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.first_aid_entrypoint import evaluate_first_aid_entrypoint
from pymia.smartpyme.first_aid_toolbox_owner_output import build_first_aid_toolbox_owner_view
from pymia.smartpyme.first_aid_toolbox_selector import select_first_aid_toolbox
from pymia.smartpyme import first_aid_toolbox_owner_output


def _ready_selection():
    entrypoint = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Mirame este Excel y sacame algo en limpio.",
        has_file=True,
    )
    return select_first_aid_toolbox(entrypoint)


def _joined_output_text(output: dict) -> str:
    values: list[str] = []
    for value in output.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    values.extend(str(nested_value) for nested_value in item.values())
                else:
                    values.append(str(item))
        else:
            values.append(str(value))
    return "\n".join(values)


def test_toolbox_owner_output_ready_presents_five_safe_options():
    output = build_first_aid_toolbox_owner_view(selection=_ready_selection())

    assert output["status"] == "PRESENT_TOOLBOX_OPTIONS"
    assert "primera revisión limitada" in output["message"]
    assert len(output["options"]) == 5
    assert output["next_question"] == "¿Con cuál de estas opciones querés empezar?"
    assert output["warnings"] == []

    option_ids = [option["option_id"] for option in output["options"]]
    assert option_ids == [
        "excel_triage_basic",
        "cash_ordering_basic",
        "price_margin_basic",
        "operational_alert_basic",
        "stock_minimal_alert",
    ]


def test_toolbox_owner_output_ready_contains_limits_for_every_option():
    output = build_first_aid_toolbox_owner_view(selection=_ready_selection())

    for option in output["options"]:
        assert option["title"].strip()
        assert option["description"].strip()
        assert option["limit"].strip()

    assert len(output["limits"]) == 4
    assert "revisión inicial" in output["limits"][0]
    assert "evaluación completa" in output["limits"][0]
    assert "evidencia disponible" in output["limits"][1]


def test_toolbox_owner_output_needs_evidence_blocks_options():
    entrypoint = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Ordename esta planilla.",
        has_file=False,
    )
    selection = select_first_aid_toolbox(entrypoint)

    output = build_first_aid_toolbox_owner_view(selection=selection)

    assert output["status"] == "REQUEST_EVIDENCE_BEFORE_TOOLBOX"
    assert output["options"] == []
    assert "fuente mínima" in output["message"]
    assert output["next_question"] == "¿Qué archivo, planilla o fuente querés que revisemos primero?"
    assert output["warnings"] == [
        "FIRST_AID toolbox selection requires minimal evidence before presenting candidates."
    ]


def test_toolbox_owner_output_not_allowed_redirects_without_options():
    entrypoint = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="No sé si gano y no me cierra la caja.",
        has_file=True,
        taxonomic_intake={"dolores_declarados": ["no sé si gano"]},
    )
    selection = select_first_aid_toolbox(entrypoint)

    output = build_first_aid_toolbox_owner_view(selection=selection)

    assert output["status"] == "REDIRECT_BEFORE_TOOLBOX"
    assert output["options"] == []
    assert "necesita más contexto" in output["message"]
    assert output["next_question"] == "¿Cuál es el problema principal que querés ordenar primero?"
    assert output["warnings"] == ["FIRST_AID toolbox selection is not allowed for this service depth."]


def test_toolbox_owner_output_does_not_expose_technical_ids_or_sources():
    output = build_first_aid_toolbox_owner_view(selection=_ready_selection())
    text = _joined_output_text(output)

    forbidden_terms = [
        "tenant_id",
        "intake_id",
        "service_depth",
        "Exceland",
        "SmartCounter",
        "SmartD",
        "component_type",
        "USE_IN_PHASE_1",
        "WITH_GUARDRAILS",
        "NOT_FOR_PHASE_1",
        "first_aid_toolbox_v1",
    ]

    for term in forbidden_terms:
        assert term not in text


def test_toolbox_owner_output_does_not_promise_confirmation_or_execution():
    output = build_first_aid_toolbox_owner_view(selection=_ready_selection())
    text = _joined_output_text(output).lower()

    forbidden_terms = [
        "certifica",
        "garantiza",
        "resultados confirmados",
        "diagnóstico completo disponible",
        "causa raíz confirmada",
        "ejecutar herramienta",
        "herramienta ejecutada",
    ]

    for term in forbidden_terms:
        assert term not in text

    assert "no confirma" in text
    assert "no valida" in text


def test_toolbox_owner_output_rejects_invalid_selection():
    with pytest.raises(ValueError):
        build_first_aid_toolbox_owner_view(selection={})  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        build_first_aid_toolbox_owner_view(selection={"status": "UNKNOWN"})  # type: ignore[arg-type]


def test_toolbox_owner_output_does_not_touch_runtime_or_pipeline():
    source = inspect.getsource(first_aid_toolbox_owner_output)

    assert "vertical_pipeline" not in source
    assert "diagnostic_core" not in source
    assert "ocf_snapshot" not in source
    assert "case_replay" not in source
    assert "storage" not in source
    assert "subprocess" not in source
    assert "argparse" not in source
    assert "open(" not in source
    assert "formula_engine_service" not in source
    assert "pathology_engine_service" not in source


def test_toolbox_owner_output_only_depends_on_selector_contract_shape():
    source = inspect.getsource(first_aid_toolbox_owner_output)

    assert "first_aid_toolbox_selector" in source
    assert "first_aid_entrypoint" not in source
    assert "first_aid_toolbox_v1" not in source

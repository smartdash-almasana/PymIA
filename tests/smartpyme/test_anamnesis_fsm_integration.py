"""
Tests para Anamnesis FSM Integration (wrapper offline con progressive_context).

Contrato vigente:
- Primer contacto obligatorio: FICHA_PYME_INICIAL
- profile_step inicial: ASK_CONTACT_NAME
- profile_data.raw_first_message conserva el primer mensaje
- No taxonomy/hypotheses/evidence antes de completar ficha
"""

import ast
import json

import pytest

from pymia.smartpyme.anamnesis_fsm import FSMPhase
from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    AnamnesisTurnOutput,
    run_anamnesis_turn,
)


def _complete_initial_profile(tenant_id: str, session_id: str, first_message: str = "hola") -> dict:
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id=tenant_id,
            session_id=session_id,
            message_text=first_message,
            previous_progressive_context=None,
        )
    )
    context = output.updated_progressive_context

    answers = [
        "Juan Perez",
        "Textiles JP",
        "2",
        "textil",
        "2",
        "6,5",
        "1",
        "no tengo",
        "1",
        "3",
        "1,4",
        "dueno",
        "+5491122334455",
        "juan@example.com",
    ]

    for answer in answers:
        output = run_anamnesis_turn(
            AnamnesisTurnInput(
                tenant_id=tenant_id,
                session_id=session_id,
                message_text=answer,
                previous_progressive_context=context,
            )
        )
        context = output.updated_progressive_context

    assert context["phase"] == FSMPhase.FICHA_PYME_INICIAL.value
    assert context["fsm_state"]["profile_step"] == "INITIAL_PROFILE_COMPLETE"
    return context


def test_import_smoke():
    assert AnamnesisTurnInput is not None
    assert AnamnesisTurnOutput is not None
    assert run_anamnesis_turn is not None


def test_primer_turno_inicia_ficha_obligatoria_y_conserva_mensaje():
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T001",
            session_id="S001",
            message_text="vendo mucho pero no se si gano plata",
            previous_progressive_context=None,
        )
    )

    assert output.phase == FSMPhase.FICHA_PYME_INICIAL.value
    assert "ficha" in output.reply_text.lower()
    assert output.updated_progressive_context["fsm_state"]["profile_step"] == "ASK_CONTACT_NAME"
    assert output.updated_progressive_context["fsm_state"]["profile_data"]["raw_first_message"] == "vendo mucho pero no se si gano plata"
    assert output.updated_progressive_context["has_taxonomy"] is False
    assert output.updated_progressive_context["has_hypotheses"] is False
    assert output.updated_progressive_context["has_evidence_requests"] is False


def test_segundo_turno_avanza_paso_de_ficha():
    output1 = run_anamnesis_turn(
        AnamnesisTurnInput("T002", "S002", "hola", None)
    )
    output2 = run_anamnesis_turn(
        AnamnesisTurnInput("T002", "S002", "Juan Perez", output1.updated_progressive_context)
    )

    assert output2.phase == FSMPhase.FICHA_PYME_INICIAL.value
    assert output2.updated_progressive_context["fsm_state"]["profile_step"] == "ASK_COMPANY_NAME"
    assert output2.updated_progressive_context["fsm_state"]["profile_data"]["contact"]["full_name"] == "Juan Perez"


def test_no_hay_taxonomia_ni_hipotesis_antes_de_ficha_completa():
    output1 = run_anamnesis_turn(AnamnesisTurnInput("T003", "S003", "fabrico ropa", None))
    output2 = run_anamnesis_turn(
        AnamnesisTurnInput("T003", "S003", "dueno", output1.updated_progressive_context)
    )

    for out in (output1, output2):
        assert out.updated_progressive_context["has_taxonomy"] is False
        assert out.updated_progressive_context["has_hypotheses"] is False
        assert out.updated_progressive_context["has_evidence_requests"] is False


def test_taxonomia_aparece_despues_de_ficha_completa():
    ready_context = _complete_initial_profile("T004", "S004")
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T004",
            session_id="S004",
            message_text="fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre",
            previous_progressive_context=ready_context,
        )
    )

    assert output.updated_progressive_context["has_taxonomy"] is True
    fsm_state = output.updated_progressive_context["fsm_state"]
    assert fsm_state["taxonomy"] is not None
    assert fsm_state["taxonomy"]["organism_type"] == "textil"


def test_taxonomia_se_rehidrata_entre_turnos():
    ready_context = _complete_initial_profile("T005", "S005")
    output1 = run_anamnesis_turn(
        AnamnesisTurnInput("T005", "S005", "fabrico ropa y vendo por mayor", ready_context)
    )
    output2 = run_anamnesis_turn(
        AnamnesisTurnInput("T005", "S005", "el margen es bajo", output1.updated_progressive_context)
    )

    fsm2 = output2.updated_progressive_context["fsm_state"]
    assert fsm2["taxonomy"] is not None
    assert fsm2["taxonomy"]["organism_type"] == "textil"


def test_hipotesis_y_evidencia_despues_de_taxonomia_y_sintoma():
    ready_context = _complete_initial_profile("T006", "S006")
    output1 = run_anamnesis_turn(
        AnamnesisTurnInput("T006", "S006", "fabrico ropa y vendo por mayor", ready_context)
    )
    output2 = run_anamnesis_turn(
        AnamnesisTurnInput("T006", "S006", "el margen es bajo, no gano plata", output1.updated_progressive_context)
    )

    assert output2.has_hypotheses is True
    assert output2.has_evidence_requests is True
    assert output2.phase == FSMPhase.SOLICITUD_EVIDENCIA.value


def test_contexto_corrupto_fail_closed_reinicia_ficha():
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T007",
            session_id="S007",
            message_text="hola",
            previous_progressive_context={"broken": True},
        )
    )

    assert output.phase == FSMPhase.FICHA_PYME_INICIAL.value
    assert output.updated_progressive_context["fsm_state"]["profile_step"] == "ASK_CONTACT_NAME"


def test_contexto_none_sesion_nueva():
    output = run_anamnesis_turn(
        AnamnesisTurnInput("T008", "S008", "hola", None)
    )
    assert output.phase == FSMPhase.FICHA_PYME_INICIAL.value


def test_sesiones_independientes():
    output_a = run_anamnesis_turn(
        AnamnesisTurnInput("T009", "S_A", "fabrico ropa", None)
    )
    output_b = run_anamnesis_turn(
        AnamnesisTurnInput("T009", "S_B", "hola", None)
    )

    assert output_a.updated_progressive_context["fsm_state"]["profile_data"]["raw_first_message"] == "fabrico ropa"
    assert output_b.updated_progressive_context["fsm_state"]["profile_data"]["raw_first_message"] == "hola"


def test_output_json_serializable():
    output = run_anamnesis_turn(
        AnamnesisTurnInput("T010", "S010", "hola", None)
    )
    serialized = json.dumps(
        {
            "reply_text": output.reply_text,
            "updated_progressive_context": output.updated_progressive_context,
            "phase": output.phase,
            "has_hypotheses": output.has_hypotheses,
            "has_evidence_requests": output.has_evidence_requests,
            "readiness_status": output.readiness_status,
        },
        ensure_ascii=False,
    )
    parsed = json.loads(serialized)
    assert parsed["phase"] == FSMPhase.FICHA_PYME_INICIAL.value


def test_progressive_context_contiene_tenant_y_phase():
    output = run_anamnesis_turn(
        AnamnesisTurnInput("T011", "S011", "hola", None)
    )
    assert output.updated_progressive_context["tenant_id"] == "T011"
    assert output.updated_progressive_context["phase"] == FSMPhase.FICHA_PYME_INICIAL.value


def test_input_es_inmutable():
    input_data = AnamnesisTurnInput("T012", "S012", "hola")
    with pytest.raises(Exception):
        input_data.message_text = "otro"


def test_output_es_inmutable():
    output = run_anamnesis_turn(
        AnamnesisTurnInput("T013", "S013", "hola", None)
    )
    with pytest.raises(Exception):
        output.reply_text = "otro"


def test_tenant_id_obligatorio():
    with pytest.raises(ValueError, match="tenant_id"):
        run_anamnesis_turn(AnamnesisTurnInput("", "S014", "hola", None))


def test_session_id_obligatorio():
    with pytest.raises(ValueError, match="session_id"):
        run_anamnesis_turn(AnamnesisTurnInput("T015", "", "hola", None))


def test_no_pide_excel_en_primer_turno():
    output = run_anamnesis_turn(
        AnamnesisTurnInput("T016", "S016", "hola", None)
    )
    assert "excel" not in output.reply_text.lower()
    assert "archivo" not in output.reply_text.lower()


def test_no_diagnostica_en_primer_turno():
    output = run_anamnesis_turn(
        AnamnesisTurnInput("T017", "S017", "no se si gano plata", None)
    )
    forbidden = ["tu problema", "diagnóstico", "margen bajo"]
    text = output.reply_text.lower()
    for phrase in forbidden:
        assert phrase not in text


def test_no_importa_modulos_prohibidos():
    with open("pymia/smartpyme/anamnesis_fsm_integration.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    forbidden_modules = {
        "pymia.smartpyme.excel_diagnostic",
        "pymia.smartpyme.supplier_duplicate_check",
        "pymia.smartpyme.classifications.supplier_duplicate_check",
        "pymia.smartpyme.microservice_dispatcher",
        "pymia.smartpyme.runtime_bridge",
        "pymia.hermes.adapter",
        "telegram",
        "requests",
        "httpx",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_modules
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_modules

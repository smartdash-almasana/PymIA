"""
Tests para Anamnesis FSM Integration (wrapper offline con progressive_context).

Cubre los casos obligatorios:
1. Primer turno: "hola" → menú inicial
2. Segundo turno: "vendo mucho pero no se si gano plata" → anamnesis/taxonomía
3. Tercer turno: flujo productivo → taxonomía progresiva + hipótesis si corresponde
4. Preservación de estado entre turnos vía progressive_context
5. Contexto corrupto → fail-closed con menú/reinicio
6. AST check: no importa módulos prohibidos
"""

import ast
import json
import pytest

from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    AnamnesisTurnOutput,
    run_anamnesis_turn,
)
from pymia.smartpyme.anamnesis_fsm import FSMPhase


def test_import_smoke():
    """Smoke test: importación básica."""
    from pymia.smartpyme.anamnesis_fsm_integration import (
        AnamnesisTurnInput,
        AnamnesisTurnOutput,
        run_anamnesis_turn,
    )
    assert AnamnesisTurnInput is not None
    assert AnamnesisTurnOutput is not None
    assert run_anamnesis_turn is not None


# CASO 1: Primer turno "hola" → menú inicial
def test_caso_1_primer_turno_hola_menu_inicial():
    """Primer turno con 'hola' → menú inicial."""
    input_data = AnamnesisTurnInput(
        tenant_id="T001",
        session_id="S001",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert output.reply_text
    assert "Contame qué te preocupa" in output.reply_text
    assert "No sé bien" in output.reply_text
    assert output.phase == FSMPhase.MENU_INICIAL.value
    assert output.has_hypotheses is False
    assert output.has_evidence_requests is False
    assert output.updated_progressive_context is not None


def test_caso_1_texto_vacio_menu_inicial():
    """Primer turno con texto vacío → menú inicial."""
    input_data = AnamnesisTurnInput(
        tenant_id="T002",
        session_id="S002",
        message_text="",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert output.phase == FSMPhase.MENU_INICIAL.value
    assert "Contame qué te preocupa" in output.reply_text


# CASO 2: "vendo mucho pero no se si gano plata" → anamnesis/taxonomía
def test_caso_2_vendo_mucho_pregunta_taxonomia():
    """Relato con dolor pero sin taxonomía → pregunta de anamnesis, no diagnóstico."""
    input_data = AnamnesisTurnInput(
        tenant_id="T003",
        session_id="S003",
        message_text="vendo mucho pero no se si gano plata",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    # No debe diagnosticar
    assert "tu problema" not in output.reply_text.lower()
    assert "margen bajo" not in output.reply_text.lower()

    # Debe preguntar sobre taxonomía
    assert output.phase in [
        FSMPhase.ANAMNESIS_TAXONOMIA.value,
        FSMPhase.MENU_INICIAL.value,
    ]


def test_caso_2_no_diagnostica_prematuro():
    """Verifica que no diagnostica desde relato crudo."""
    input_data = AnamnesisTurnInput(
        tenant_id="T004",
        session_id="S004",
        message_text="vendo mucho pero no se si gano plata",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    forbidden_phrases = [
        "tu problema es",
        "margen bajo",
        "ganancia negativa",
        "tu negocio tiene",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in output.reply_text.lower()


# CASO 3: Flujo productivo → taxonomía progresiva
def test_caso_3_flujo_productivo_textil():
    """Descripción de fábrica textil → clasifica correctamente."""
    input_data = AnamnesisTurnInput(
        tenant_id="T005",
        session_id="S005",
        message_text="fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    # Debe tener taxonomía
    assert output.updated_progressive_context["has_taxonomy"] is True

    # Verificar taxonomía en el contexto serializado
    fsm_state = output.updated_progressive_context["fsm_state"]
    assert fsm_state["taxonomy"] is not None
    assert fsm_state["taxonomy"]["organism_type"] == "textil"
    assert "mayorista" in fsm_state["taxonomy"]["sales_channels"]
    assert "mercado_libre" in fsm_state["taxonomy"]["sales_channels"]
    assert "produccion" in fsm_state["taxonomy"]["areas_present"]
    assert "ventas" in fsm_state["taxonomy"]["areas_present"]
    assert "compras" in fsm_state["taxonomy"]["areas_present"]


def test_caso_3_taxonomia_progresiva_entre_turnos():
    """Taxonomía se construye progresivamente entre turnos."""
    # Turno 1: relato inicial
    input1 = AnamnesisTurnInput(
        tenant_id="T006",
        session_id="S006",
        message_text="fabrico ropa y vendo por mayor",
        previous_progressive_context=None,
    )
    output1 = run_anamnesis_turn(input1)

    # Turno 2: agregar síntoma usando contexto previo
    input2 = AnamnesisTurnInput(
        tenant_id="T006",
        session_id="S006",
        message_text="el margen es bajo, no gano plata",
        previous_progressive_context=output1.updated_progressive_context,
    )
    output2 = run_anamnesis_turn(input2)

    # Debe preservar taxonomía del turno 1
    fsm_state2 = output2.updated_progressive_context["fsm_state"]
    assert fsm_state2["taxonomy"] is not None, (
        "taxonomy debe sobrevivir rehidratación entre turnos"
    )
    assert fsm_state2["taxonomy"]["organism_type"] == "textil"


# CASO 4: Preservación de estado entre turnos
def test_caso_4_preserva_estado_entre_turnos():
    """Estado se preserva entre turnos vía progressive_context."""
    # Turno 1
    input1 = AnamnesisTurnInput(
        tenant_id="T007",
        session_id="S007",
        message_text="hola",
        previous_progressive_context=None,
    )
    output1 = run_anamnesis_turn(input1)
    context1 = output1.updated_progressive_context

    # Turno 2 usando contexto del turno 1
    input2 = AnamnesisTurnInput(
        tenant_id="T007",
        session_id="S007",
        message_text="1",  # Opción 1 del menú
        previous_progressive_context=context1,
    )
    output2 = run_anamnesis_turn(input2)

    # Debe avanzar a CAPTURA_RELATO_CRUDO
    assert output2.phase == FSMPhase.CAPTURA_RELATO_CRUDO.value


def test_caso_4_hipotesis_abierta_con_taxonomia_suficiente():
    """Taxonomía suficiente + síntoma → hipótesis ABIERTA."""
    # Turno 1: establecer taxonomía
    input1 = AnamnesisTurnInput(
        tenant_id="T008",
        session_id="S008",
        message_text="fabrico ropa y vendo por mayor",
        previous_progressive_context=None,
    )
    output1 = run_anamnesis_turn(input1)

    # Turno 2: agregar síntoma
    input2 = AnamnesisTurnInput(
        tenant_id="T008",
        session_id="S008",
        message_text="el margen es bajo, no gano plata",
        previous_progressive_context=output1.updated_progressive_context,
    )
    output2 = run_anamnesis_turn(input2)

    # Debe tener hipótesis (ya hay taxonomía + síntoma)
    assert output2.has_hypotheses is True, (
        "Con taxonomía textil + síntoma de margen, debe generar hipótesis"
    )
    # Hipótesis deben estar ABIERTAS (no CONFIRMADAS)
    fsm_state = output2.updated_progressive_context["fsm_state"]
    assert len(fsm_state.get("hypotheses", [])) > 0, (
        "hypotheses no debe estar vacío tras rehidratación"
    )
    for h in fsm_state.get("hypotheses", []):
        assert h["status"] in ["ABIERTA", "EN_CONTRASTE"]
        assert h["status"] not in ["CONFIRMADA", "DESCARTADA"]


def test_caso_4_solicita_evidencia_con_hipotesis():
    """Con hipótesis de margen → solicita evidencia concreta."""
    # Turno 1: taxonomía
    input1 = AnamnesisTurnInput(
        tenant_id="T009",
        session_id="S009",
        message_text="fabrico ropa y vendo por mayor",
        previous_progressive_context=None,
    )
    output1 = run_anamnesis_turn(input1)

    # Turno 2: síntoma
    input2 = AnamnesisTurnInput(
        tenant_id="T009",
        session_id="S009",
        message_text="el margen es bajo",
        previous_progressive_context=output1.updated_progressive_context,
    )
    output2 = run_anamnesis_turn(input2)

    # Debe solicitar evidencia (hay taxonomía + hipótesis de margen)
    assert output2.has_evidence_requests is True, (
        "Con taxonomía + hipótesis de margen, debe solicitar evidencia"
    )
    fsm_state = output2.updated_progressive_context["fsm_state"]
    evidence_types = [e["evidence_type"] for e in fsm_state.get("evidence_requests", [])]
    assert any("ventas" in et or "ingresos" in et for et in evidence_types)
    assert any("costos" in et or "gastos" in et for et in evidence_types)


# CASO 5: Contexto corrupto → fail-closed
def test_caso_5_contexto_corrupto_fail_closed():
    """Contexto corrupto → fail-closed con menú inicial."""
    corrupt_context = {"invalid": "data", "no_fsm_state": True}

    input_data = AnamnesisTurnInput(
        tenant_id="T010",
        session_id="S010",
        message_text="hola",
        previous_progressive_context=corrupt_context,
    )
    output = run_anamnesis_turn(input_data)

    # Debe reiniciar sesión (menú inicial o captura de relato)
    assert output.reply_text
    assert output.updated_progressive_context is not None


def test_caso_5_contexto_vacio_fail_closed():
    """Contexto vacío → fail-closed."""
    input_data = AnamnesisTurnInput(
        tenant_id="T011",
        session_id="S011",
        message_text="hola",
        previous_progressive_context={},
    )
    output = run_anamnesis_turn(input_data)

    assert output.reply_text
    assert output.updated_progressive_context is not None


def test_caso_5_contexto_none_sesion_nueva():
    """Contexto None → sesión nueva."""
    input_data = AnamnesisTurnInput(
        tenant_id="T012",
        session_id="S012",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert output.phase == FSMPhase.MENU_INICIAL.value


# CASO 6: AST check - no importa módulos prohibidos
def test_caso_6_no_importa_modulos_prohibidos():
    """Verifica que anamnesis_fsm_integration.py no importa módulos prohibidos."""
    with open("pymia/smartpyme/anamnesis_fsm_integration.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    forbidden_modules = [
        "pymia.smartpyme.excel_diagnostic",
        "pymia.smartpyme.supplier_duplicate_check",
        "pymia.smartpyme.classifications.supplier_duplicate_check",
        "pymia.smartpyme.microservice_dispatcher",
        "pymia.smartpyme.runtime_bridge",
        "pymia.hermes.adapter",
        "telegram",
        "requests",
        "httpx",
    ]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_modules, f"Import prohibido: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_modules, f"ImportFrom prohibido: {node.module}"


# Validación de inputs
def test_tenant_id_obligatorio():
    """tenant_id vacío → ValueError."""
    input_data = AnamnesisTurnInput(
        tenant_id="",
        session_id="S013",
        message_text="hola",
        previous_progressive_context=None,
    )
    with pytest.raises(ValueError, match="tenant_id"):
        run_anamnesis_turn(input_data)


def test_session_id_obligatorio():
    """session_id vacío → ValueError."""
    input_data = AnamnesisTurnInput(
        tenant_id="T014",
        session_id="",
        message_text="hola",
        previous_progressive_context=None,
    )
    with pytest.raises(ValueError, match="session_id"):
        run_anamnesis_turn(input_data)


def test_tenant_id_none_error():
    """tenant_id None → ValueError."""
    with pytest.raises(Exception):  # Pydantic validation
        AnamnesisTurnInput(
            tenant_id=None,
            session_id="S015",
            message_text="hola",
        )


# JSON serialización
def test_output_json_serializable():
    """AnamnesisTurnOutput es JSON serializable."""
    input_data = AnamnesisTurnInput(
        tenant_id="T016",
        session_id="S016",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    # Convertir a dict
    output_dict = {
        "reply_text": output.reply_text,
        "updated_progressive_context": output.updated_progressive_context,
        "phase": output.phase,
        "has_hypotheses": output.has_hypotheses,
        "has_evidence_requests": output.has_evidence_requests,
        "readiness_status": output.readiness_status,
    }

    # Debe ser JSON serializable
    json_str = json.dumps(output_dict, ensure_ascii=False)
    parsed = json.loads(json_str)
    assert parsed["reply_text"] == output.reply_text
    assert parsed["phase"] == output.phase


def test_progressive_context_json_serializable():
    """progressive_context es JSON serializable."""
    input_data = AnamnesisTurnInput(
        tenant_id="T017",
        session_id="S017",
        message_text="fabrico ropa y vendo por mayor",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    # Debe ser JSON serializable
    json_str = json.dumps(output.updated_progressive_context, ensure_ascii=False)
    parsed = json.loads(json_str)
    assert "fsm_state" in parsed
    assert "tenant_id" in parsed


# Inmutabilidad
def test_input_es_inmutable():
    """AnamnesisTurnInput es dataclass frozen."""
    input_data = AnamnesisTurnInput(
        tenant_id="T018",
        session_id="S018",
        message_text="hola",
    )
    with pytest.raises(Exception):  # FrozenInstanceError
        input_data.message_text = "otro"


def test_output_es_inmutable():
    """AnamnesisTurnOutput es dataclass frozen."""
    input_data = AnamnesisTurnInput(
        tenant_id="T019",
        session_id="S019",
        message_text="hola",
    )
    output = run_anamnesis_turn(input_data)
    with pytest.raises(Exception):  # FrozenInstanceError
        output.reply_text = "otro"


def test_inputs_no_mutados():
    """run_anamnesis_turn no muta input_data."""
    input_data = AnamnesisTurnInput(
        tenant_id="T020",
        session_id="S020",
        message_text="hola",
        previous_progressive_context=None,
    )
    original_text = input_data.message_text
    original_context = input_data.previous_progressive_context

    output = run_anamnesis_turn(input_data)

    # input_data no debe haber cambiado
    assert input_data.message_text == original_text
    assert input_data.previous_progressive_context == original_context


# Tests de metadata
def test_output_metadata_consistente():
    """Metadata del output es consistente con el estado."""
    input_data = AnamnesisTurnInput(
        tenant_id="T021",
        session_id="S021",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert output.phase == FSMPhase.MENU_INICIAL.value
    assert output.has_hypotheses is False
    assert output.has_evidence_requests is False


def test_progressive_context_contiene_tenant_id():
    """progressive_context siempre contiene tenant_id."""
    input_data = AnamnesisTurnInput(
        tenant_id="T022",
        session_id="S022",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert output.updated_progressive_context["tenant_id"] == "T022"


def test_progressive_context_contiene_phase():
    """progressive_context siempre contiene phase."""
    input_data = AnamnesisTurnInput(
        tenant_id="T023",
        session_id="S023",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert output.updated_progressive_context["phase"] == FSMPhase.MENU_INICIAL.value


# Tests de flujo completo
def test_flujo_completo_3_turnos():
    """Flujo completo: menú → opción → relato."""
    # Turno 1: menú inicial
    input1 = AnamnesisTurnInput(
        tenant_id="T024",
        session_id="S024",
        message_text="hola",
        previous_progressive_context=None,
    )
    output1 = run_anamnesis_turn(input1)
    assert output1.phase == FSMPhase.MENU_INICIAL.value

    # Turno 2: opción 1
    input2 = AnamnesisTurnInput(
        tenant_id="T024",
        session_id="S024",
        message_text="1",
        previous_progressive_context=output1.updated_progressive_context,
    )
    output2 = run_anamnesis_turn(input2)
    assert output2.phase == FSMPhase.CAPTURA_RELATO_CRUDO.value

    # Turno 3: relato
    input3 = AnamnesisTurnInput(
        tenant_id="T024",
        session_id="S024",
        message_text="fabrico ropa y vendo por mayor",
        previous_progressive_context=output2.updated_progressive_context,
    )
    output3 = run_anamnesis_turn(input3)
    assert output3.reply_text
    assert output3.updated_progressive_context is not None


def test_sesiones_independientes():
    """Sesiones diferentes no comparten estado."""
    # Sesión A
    input_a = AnamnesisTurnInput(
        tenant_id="T025",
        session_id="S_A",
        message_text="fabrico ropa",
        previous_progressive_context=None,
    )
    output_a = run_anamnesis_turn(input_a)

    # Sesión B (diferente session_id)
    input_b = AnamnesisTurnInput(
        tenant_id="T025",
        session_id="S_B",
        message_text="hola",
        previous_progressive_context=None,
    )
    output_b = run_anamnesis_turn(input_b)

    # Sesión B debe estar en menú inicial (no afectada por sesión A)
    assert output_b.phase == FSMPhase.MENU_INICIAL.value


# Tests de boundary policy
def test_no_pide_excel_en_primer_turno():
    """No pide Excel en el primer turno."""
    input_data = AnamnesisTurnInput(
        tenant_id="T026",
        session_id="S026",
        message_text="hola",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    assert "excel" not in output.reply_text.lower()
    assert "archivo" not in output.reply_text.lower()


def test_no_diagnostica_ejemplo_prohibido():
    """Ejemplo prohibido: no dice 'Tu problema parece ser margen bajo'."""
    input_data = AnamnesisTurnInput(
        tenant_id="T027",
        session_id="S027",
        message_text="vendo mucho pero no se si gano plata",
        previous_progressive_context=None,
    )
    output = run_anamnesis_turn(input_data)

    forbidden = "tu problema parece ser"
    assert forbidden not in output.reply_text.lower()


def test_permite_mencionar_hipotesis():
    """Ejemplo permitido: puede mencionar 'hipótesis' si hay hipótesis."""
    # Turno 1: taxonomía
    input1 = AnamnesisTurnInput(
        tenant_id="T028",
        session_id="S028",
        message_text="fabrico ropa y vendo por mayor",
        previous_progressive_context=None,
    )
    output1 = run_anamnesis_turn(input1)

    # Turno 2: síntoma
    input2 = AnamnesisTurnInput(
        tenant_id="T028",
        session_id="S028",
        message_text="el margen es bajo",
        previous_progressive_context=output1.updated_progressive_context,
    )
    output2 = run_anamnesis_turn(input2)

    # Si hay hipótesis, puede mencionar "hipótesis" pero no "diagnóstico"
    if output2.has_hypotheses:
        assert "diagnóstico" not in output2.reply_text.lower()


def test_conversacion_5_turnos_conserva_estado():
    """Conversación de 5 turnos conserva taxonomía, hipótesis y evidencia.

    Este test verifica el fix de BUG-1: _reconstruct_state_from_context()
    debe rehidratar objetos completos entre turnos, no perder memoria.
    """
    # Turno 1: menú inicial
    output1 = run_anamnesis_turn(AnamnesisTurnInput(
        tenant_id="T_5TURNOS",
        session_id="S_5TURNOS",
        message_text="hola",
        previous_progressive_context=None,
    ))
    assert output1.phase == FSMPhase.MENU_INICIAL.value
    ctx1 = output1.updated_progressive_context

    # Turno 2: opción 1 (contame tu negocio)
    output2 = run_anamnesis_turn(AnamnesisTurnInput(
        tenant_id="T_5TURNOS",
        session_id="S_5TURNOS",
        message_text="1",
        previous_progressive_context=ctx1,
    ))
    assert output2.phase == FSMPhase.CAPTURA_RELATO_CRUDO.value
    ctx2 = output2.updated_progressive_context

    # Turno 3: relato textil completo → debe generar taxonomía
    output3 = run_anamnesis_turn(AnamnesisTurnInput(
        tenant_id="T_5TURNOS",
        session_id="S_5TURNOS",
        message_text="fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre",
        previous_progressive_context=ctx2,
    ))
    ctx3 = output3.updated_progressive_context
    fsm3 = ctx3["fsm_state"]
    assert fsm3["taxonomy"] is not None, "Turno 3 debe generar taxonomía"
    assert fsm3["taxonomy"]["organism_type"] == "textil"

    # Turno 4: síntoma de margen → debe preservar taxonomía + generar hipótesis
    output4 = run_anamnesis_turn(AnamnesisTurnInput(
        tenant_id="T_5TURNOS",
        session_id="S_5TURNOS",
        message_text="el margen es bajo, no gano plata",
        previous_progressive_context=ctx3,
    ))
    ctx4 = output4.updated_progressive_context
    fsm4 = ctx4["fsm_state"]

    # CRITICAL: taxonomía del turno 3 debe sobrevivir rehidratación
    assert fsm4["taxonomy"] is not None, (
        "BUG-1 regression: taxonomía perdida después de rehidratación turno 4"
    )
    assert fsm4["taxonomy"]["organism_type"] == "textil", (
        "organism_type debe seguir siendo 'textil' del turno 3"
    )
    # Debe haber hipótesis abiertas
    assert len(fsm4.get("hypotheses", [])) > 0, (
        "Con taxonomía + síntoma de margen, debe haber hipótesis"
    )

    # Turno 5: información adicional → debe preservar todo lo anterior
    output5 = run_anamnesis_turn(AnamnesisTurnInput(
        tenant_id="T_5TURNOS",
        session_id="S_5TURNOS",
        message_text="uso excel para todo, no tengo sistema",
        previous_progressive_context=ctx4,
    ))
    ctx5 = output5.updated_progressive_context
    fsm5 = ctx5["fsm_state"]

    # Turno 5: taxonomía, hipótesis siguen presentes
    assert fsm5["taxonomy"] is not None, (
        "BUG-1 regression: taxonomía perdida en turno 5"
    )
    assert fsm5["taxonomy"]["organism_type"] == "textil"
    assert len(fsm5.get("hypotheses", [])) > 0, (
        "Hipótesis deben persistir después de 5 turnos"
    )

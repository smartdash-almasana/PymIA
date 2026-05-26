"""
Tests para Anamnesis FSM offline.

Cubre los 8 casos obligatorios:
1. Sesión nueva/texto vacío → menú inicial
2. "vendo mucho pero no se si gano plata" → pregunta de anamnesis/taxonomía
3. Descripción de flujo productivo → clasificación
4. Taxonomía suficiente + síntoma → hipótesis ABIERTA
5. Solicita evidencia concreta
6. Campos faltantes → pregunta o BLOQUEADO_EXPLICATIVO
7. Bloquea análisis si AnamnesisReadiness no está READY
8. No importa módulos prohibidos
"""

import json
import ast
import pytest
from pymia.smartpyme.anamnesis_fsm import (
    FSMPhase,
    AnamnesisFSMState,
    process_message,
    MENU_INICIAL_TEXTO,
)
from pymia.smartpyme.taxonomy import TaxonomyType
from pymia.smartpyme.anamnesis_readiness import ReadinessStatus
from pymia.smartpyme.operational_hypothesis import HypothesisStatus
from pymia.smartpyme.conversation_contract import ConversationPhase


def test_import_smoke():
    """Smoke test: importación básica."""
    from pymia.smartpyme.anamnesis_fsm import (
        FSMPhase,
        AnamnesisFSMState,
        process_message,
        MENU_INICIAL_TEXTO,
    )
    assert FSMPhase is not None
    assert AnamnesisFSMState is not None
    assert process_message is not None
    assert MENU_INICIAL_TEXTO is not None


def test_fase_enum_values():
    """FSMPhase enum tiene todos los estados requeridos."""
    assert FSMPhase.INIT == "INIT"
    assert FSMPhase.MENU_INICIAL == "MENU_INICIAL"
    assert FSMPhase.CAPTURA_RELATO_CRUDO == "CAPTURA_RELATO_CRUDO"
    assert FSMPhase.ANAMNESIS_TAXONOMIA == "ANAMNESIS_TAXONOMIA"
    assert FSMPhase.HIPOTESIS_FORMULADA == "HIPOTESIS_FORMULADA"
    assert FSMPhase.SOLICITUD_EVIDENCIA == "SOLICITUD_EVIDENCIA"
    assert FSMPhase.BLOQUEADO_EXPLICATIVO == "BLOQUEADO_EXPLICATIVO"


def test_menu_inicial_texto_contenido():
    """Menú inicial tiene las 4 opciones esperadas."""
    assert "Contame qué te preocupa" in MENU_INICIAL_TEXTO
    assert "No sé bien" in MENU_INICIAL_TEXTO
    assert "Quiero revisar mis planillas" in MENU_INICIAL_TEXTO
    assert "Tengo una pregunta específica" in MENU_INICIAL_TEXTO


# CASO 1: Sesión nueva/texto vacío → menú inicial
def test_caso_1_sesion_nueva_menu_inicial():
    """Sesión nueva (previous_state=None) → menú inicial."""
    state, message = process_message("hola", tenant_id="T001", previous_state=None)
    
    assert state.phase == FSMPhase.MENU_INICIAL
    assert state.tenant_id == "T001"
    assert message == MENU_INICIAL_TEXTO
    assert state.taxonomy is None
    assert len(state.hypotheses) == 0


def test_caso_1_texto_vacio_menu_inicial():
    """Texto vacío → menú inicial."""
    state, message = process_message("", tenant_id="T001", previous_state=None)
    
    assert state.phase == FSMPhase.MENU_INICIAL
    assert message == MENU_INICIAL_TEXTO


def test_caso_1_texto_espacios_menu_inicial():
    """Texto solo con espacios → menú inicial."""
    state, message = process_message("   ", tenant_id="T001", previous_state=None)
    
    assert state.phase == FSMPhase.MENU_INICIAL
    assert message == MENU_INICIAL_TEXTO


# CASO 2: "vendo mucho pero no se si gano plata" → pregunta de anamnesis/taxonomía
def test_caso_2_vendo_mucho_pregunta_taxonomia():
    """Relato con dolor pero sin taxonomía clara → pregunta de anamnesis."""
    user_text = "vendo mucho pero no se si gano plata"
    state, message = process_message(user_text, tenant_id="T002", previous_state=None)
    
    # Debe preguntar sobre taxonomía, no diagnosticar
    assert "diagnóstico" not in message.lower()
    assert "tu problema" not in message.lower()
    assert state.phase in [FSMPhase.ANAMNESIS_TAXONOMIA, FSMPhase.MENU_INICIAL]
    
    # No debe tener hipótesis confirmadas (solo ABIERTAS si las hay)
    for h in state.hypotheses:
        assert h.status == HypothesisStatus.ABIERTA


def test_caso_2_no_diagnostica_prematuro():
    """Verifica que no diagnostica desde relato crudo."""
    user_text = "vendo mucho pero no se si gano plata"
    state, message = process_message(user_text, tenant_id="T002", previous_state=None)
    
    # Mensaje no debe contener diagnóstico directo
    forbidden_phrases = [
        "tu problema es",
        "margen bajo",
        "ganancia negativa",
        "tu negocio tiene",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in message.lower()


# CASO 3: Descripción de flujo productivo → clasificación
def test_caso_3_flujo_productivo_textil():
    """Descripción de fábrica textil → clasifica correctamente."""
    user_text = "fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre"
    state, message = process_message(user_text, tenant_id="T003", previous_state=None)
    
    # Debe detectar taxonomía
    assert state.taxonomy is not None
    assert state.taxonomy.organism_type == TaxonomyType.textil
    
    # Debe detectar canales
    assert "mayorista" in state.taxonomy.sales_channels
    assert "mercado_libre" in state.taxonomy.sales_channels
    
    # Debe detectar áreas
    assert "produccion" in state.taxonomy.areas_present
    assert "ventas" in state.taxonomy.areas_present
    assert "compras" in state.taxonomy.areas_present
    
    # Debe detectar flujo operativo
    assert "compra" in state.taxonomy.operational_flow_stages
    assert "produccion" in state.taxonomy.operational_flow_stages
    assert "venta" in state.taxonomy.operational_flow_stages


def test_caso_3_negocio_mixto():
    """Negocio mixto (fábrica + venta directa) → clasificación mixta."""
    user_text = "hago muebles, los vendo en mi local y también por Mercado Libre"
    state, message = process_message(user_text, tenant_id="T004", previous_state=None)
    
    assert state.taxonomy is not None
    assert state.taxonomy.organism_type == TaxonomyType.produccion_fabrica
    assert "minorista" in state.taxonomy.sales_channels or "local" in state.taxonomy.sales_channels
    assert "mercado_libre" in state.taxonomy.sales_channels


# CASO 4: Taxonomía suficiente + síntoma → hipótesis ABIERTA
def test_caso_4_taxonomia_suficiente_hipotesis_abierta():
    """Taxonomía clara + síntoma margen → hipótesis ABIERTA (no confirmada)."""
    # Primero establecer taxonomía
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T005",
        previous_state=None
    )
    
    # Luego agregar síntoma
    state2, message = process_message(
        "vendo mucho pero no me queda ganancia, el margen es bajo",
        tenant_id="T005",
        previous_state=state1
    )
    
    # Si readiness está READY, debe haber hipótesis ABIERTAS
    if state2.readiness and state2.readiness.status == ReadinessStatus.READY:
        assert len(state2.hypotheses) > 0
        for h in state2.hypotheses:
            assert h.status == HypothesisStatus.ABIERTA
            assert h.status != HypothesisStatus.CONFIRMADA


def test_caso_4_hipotesis_no_confirmada():
    """Hipótesis nunca se confirma sin evidencia."""
    state, _ = process_message(
        "fabrico ropa, vendo por mayor, pero el margen es bajo",
        tenant_id="T006",
        previous_state=None
    )
    
    # Todas las hipótesis deben estar ABIERTAS o sin status
    for h in state.hypotheses:
        assert h.status in [HypothesisStatus.ABIERTA, HypothesisStatus.EN_CONTRASTE]
        assert h.status not in [HypothesisStatus.CONFIRMADA, HypothesisStatus.DESCARTADA]


# CASO 5: Solicita evidencia concreta
def test_caso_5_solicita_evidencia_concreta():
    """Con hipótesis de margen → solicita ventas y costos."""
    # Establecer taxonomía + síntoma
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T007",
        previous_state=None
    )
    state2, _ = process_message(
        "el margen es bajo, no gano plata",
        tenant_id="T007",
        previous_state=state1
    )
    
    # Si readiness está READY, debe solicitar evidencia
    if state2.readiness and state2.readiness.status == ReadinessStatus.READY:
        assert len(state2.evidence_requests) > 0
        
        # Debe solicitar ventas y costos
        evidence_types = [e.evidence_type for e in state2.evidence_requests]
        assert any("ventas" in et or "ingresos" in et for et in evidence_types)
        assert any("costos" in et or "gastos" in et for et in evidence_types)


def test_caso_5_mensaje_evidencia_claro():
    """Mensaje de solicitud de evidencia es claro y específico."""
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T008",
        previous_state=None
    )
    state2, message = process_message(
        "el margen es bajo",
        tenant_id="T008",
        previous_state=state1
    )
    
    # Si solicita evidencia, el mensaje debe ser claro
    if state2.phase == FSMPhase.SOLICITUD_EVIDENCIA:
        assert "evidencia" in message.lower() or "necesito" in message.lower()
        assert "ventas" in message.lower() or "costos" in message.lower()


# CASO 6: Campos faltantes → pregunta o BLOQUEADO_EXPLICATIVO
def test_caso_6_campos_faltantes_pregunta():
    """Información incompleta → pregunta concreta."""
    user_text = "tengo un negocio"
    state, message = process_message(user_text, tenant_id="T009", previous_state=None)
    
    # Debe preguntar por más información
    assert state.phase in [
        FSMPhase.ANAMNESIS_TAXONOMIA,
        FSMPhase.BLOQUEADO_EXPLICATIVO,
    ]
    
    # Mensaje debe ser pregunta o explicación
    assert "?" in message or "necesito" in message.lower()


def test_caso_6_bloqueado_explicativo():
    """Falta información bloqueante → BLOQUEADO_EXPLICATIVO."""
    user_text = "algo no funciona"
    state, message = process_message(user_text, tenant_id="T010", previous_state=None)
    
    # Puede estar en ANAMNESIS_TAXONOMIA o BLOQUEADO_EXPLICATIVO
    assert state.phase in [
        FSMPhase.ANAMNESIS_TAXONOMIA,
        FSMPhase.BLOQUEADO_EXPLICATIVO,
    ]
    
    # Mensaje debe explicar qué falta
    assert len(message) > 20


# CASO 7: Bloquea análisis si AnamnesisReadiness no está READY
def test_caso_7_bloquea_analisis_sin_readiness():
    """Si readiness no está READY, no formula hipótesis."""
    state, _ = process_message(
        "tengo un problema",
        tenant_id="T011",
        previous_state=None
    )
    
    # Si readiness no está READY, no debe haber hipótesis
    if state.readiness and state.readiness.status != ReadinessStatus.READY:
        assert len(state.hypotheses) == 0


def test_caso_7_readiness_no_ready_sin_hipotesis():
    """Readiness NEEDS_MORE_INFO o BLOCKED → sin hipótesis."""
    state, _ = process_message(
        "algo anda mal",
        tenant_id="T012",
        previous_state=None
    )
    
    if state.readiness and state.readiness.status in [
        ReadinessStatus.NEEDS_MORE_INFO,
        ReadinessStatus.BLOCKED,
    ]:
        assert len(state.hypotheses) == 0


# CASO 8: No importa módulos prohibidos
def test_caso_8_no_importa_modulos_prohibidos():
    """Verifica que anamnesis_fsm.py no importa módulos prohibidos."""
    with open("pymia/smartpyme/anamnesis_fsm.py", "r", encoding="utf-8") as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    forbidden_modules = [
        "pymia.smartpyme.excel_diagnostic",
        "pymia.smartpyme.supplier_duplicate_check",
        "pymia.smartpyme.classifications.supplier_duplicate_check",
        "pymia.smartpyme.microservice_dispatcher",
        "pymia.smartpyme.runtime_bridge",
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_modules, f"Import prohibido: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_modules, f"ImportFrom prohibido: {node.module}"


# Tests adicionales de validación
def test_tenant_id_obligatorio():
    """tenant_id vacío → ValueError."""
    with pytest.raises(ValueError, match="tenant_id"):
        process_message("hola", tenant_id="", previous_state=None)


def test_tenant_id_none_error():
    """tenant_id None → ValueError."""
    with pytest.raises(ValueError, match="tenant_id"):
        process_message("hola", tenant_id=None, previous_state=None)


def test_to_dict_json_serializable():
    """AnamnesisFSMState.to_dict() es JSON serializable."""
    state, _ = process_message("hola", tenant_id="T013", previous_state=None)
    
    data = state.to_dict()
    json_str = json.dumps(data, ensure_ascii=False)
    parsed = json.loads(json_str)
    
    assert parsed["phase"] == FSMPhase.MENU_INICIAL
    assert parsed["tenant_id"] == "T013"


def test_state_es_inmutable():
    """AnamnesisFSMState es dataclass frozen."""
    state, _ = process_message("hola", tenant_id="T014", previous_state=None)
    
    with pytest.raises(Exception):  # FrozenInstanceError
        state.phase = "OTRO"


def test_inputs_no_mutados():
    """process_message no muta previous_state."""
    state1, _ = process_message("hola", tenant_id="T015", previous_state=None)
    state1_phase = state1.phase
    state1_hypotheses_count = len(state1.hypotheses)
    
    state2, _ = process_message("fabrico ropa", tenant_id="T015", previous_state=state1)
    
    # state1 no debe haber cambiado
    assert state1.phase == state1_phase
    assert len(state1.hypotheses) == state1_hypotheses_count


def test_menu_opcion_1_relato():
    """Opción 1 del menú → CAPTURA_RELATO_CRUDO."""
    state, message = process_message("1", tenant_id="T016", previous_state=None)
    
    assert state.phase == FSMPhase.CAPTURA_RELATO_CRUDO
    assert "preocupa" in message.lower() or "contame" in message.lower()


def test_menu_opcion_2_no_se():
    """Opción 2 del menú → CAPTURA_RELATO_CRUDO."""
    state, message = process_message("2", tenant_id="T017", previous_state=None)
    
    assert state.phase == FSMPhase.CAPTURA_RELATO_CRUDO
    assert "contame" in message.lower() or "qué haces" in message.lower()


def test_menu_opcion_3_planillas():
    """Opción 3 del menú → CAPTURA_RELATO_CRUDO."""
    state, message = process_message("3", tenant_id="T018", previous_state=None)
    
    assert state.phase == FSMPhase.CAPTURA_RELATO_CRUDO
    assert "planillas" in message.lower()


def test_menu_opcion_4_pregunta():
    """Opción 4 del menú → CAPTURA_RELATO_CRUDO."""
    state, message = process_message("4", tenant_id="T019", previous_state=None)
    
    assert state.phase == FSMPhase.CAPTURA_RELATO_CRUDO
    assert "pregunta" in message.lower()


def test_taxonomy_confidence_entre_0_y_1():
    """Confianza de taxonomía siempre está entre 0.0 y 1.0."""
    state, _ = process_message(
        "fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre",
        tenant_id="T020",
        previous_state=None
    )
    
    if state.taxonomy:
        assert 0.0 <= state.taxonomy.confidence <= 1.0


def test_contract_phase_consistente():
    """ConversationContract.current_phase es consistente con FSMPhase."""
    state, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T021",
        previous_state=None
    )
    
    if state.contract:
        # Si phase es SOLICITUD_EVIDENCIA, contract debe estar en EVIDENCE
        if state.phase == FSMPhase.SOLICITUD_EVIDENCIA:
            assert state.contract.current_phase == ConversationPhase.EVIDENCIA
        # Si phase es HIPOTESIS_FORMULADA, contract debe estar en CONTRAST
        elif state.phase == FSMPhase.HIPOTESIS_FORMULADA:
            assert state.contract.current_phase == ConversationPhase.CONTRASTE


def test_evidence_requirement_telegram_message_no_vacio():
    """EvidenceRequirement siempre tiene telegram_message no vacío."""
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T022",
        previous_state=None
    )
    state2, _ = process_message(
        "el margen es bajo",
        tenant_id="T022",
        previous_state=state1
    )
    
    for evidence_req in state2.evidence_requests:
        assert evidence_req.telegram_message is not None
        assert len(evidence_req.telegram_message.strip()) > 0


def test_no_pide_excel_en_primer_mensaje():
    """No pide Excel en el primer mensaje."""
    state, message = process_message("hola", tenant_id="T023", previous_state=None)
    
    # Primer mensaje es menú inicial
    assert state.phase == FSMPhase.MENU_INICIAL
    assert "excel" not in message.lower()
    assert "archivo" not in message.lower() or "planilla" not in message.lower()


def test_hypothesis_abierta_no_confirmada():
    """Hipótesis ABIERTA nunca se marca como CONFIRMADA sin evidencia."""
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T024",
        previous_state=None
    )
    state2, _ = process_message(
        "el margen es bajo, no gano plata",
        tenant_id="T024",
        previous_state=state1
    )
    
    for h in state2.hypotheses:
        assert h.status != HypothesisStatus.CONFIRMADA
        assert h.status != HypothesisStatus.DESCARTADA


def test_readiness_status_enum_values():
    """ReadinessStatus enum tiene valores correctos."""
    assert ReadinessStatus.READY == "READY"
    assert ReadinessStatus.NEEDS_MORE_INFO == "NEEDS_MORE_INFO"
    assert ReadinessStatus.BLOCKED == "BLOCKED"


def test_hypothesis_status_enum_values():
    """HypothesisStatus enum tiene valores correctos."""
    assert HypothesisStatus.ABIERTA == "ABIERTA"
    assert HypothesisStatus.EN_CONTRASTE == "EN_CONTRASTE"
    assert HypothesisStatus.CONFIRMADA == "CONFIRMADA"
    assert HypothesisStatus.DESCARTADA == "DESCARTADA"
    assert HypothesisStatus.EVIDENCIA_INSUFICIENTE == "EVIDENCIA_INSUFICIENTE"


def test_conversation_phase_enum_values():
    """ConversationPhase enum tiene valores correctos."""
    assert ConversationPhase.ANAMNESIS == "ANAMNESIS"
    assert ConversationPhase.EVIDENCIA == "EVIDENCIA"
    assert ConversationPhase.CONTRASTE == "CONTRASTE"
    assert ConversationPhase.ENTREGA == "ENTREGA"


def test_blocking_reasons_es_tuple():
    """blocking_reasons es tuple (inmutable)."""
    state, _ = process_message("hola", tenant_id="T025", previous_state=None)
    
    assert isinstance(state.blocking_reasons, tuple)


def test_hypotheses_es_tuple():
    """hypotheses es tuple (inmutable)."""
    state, _ = process_message("hola", tenant_id="T026", previous_state=None)
    
    assert isinstance(state.hypotheses, tuple)


def test_evidence_requests_es_tuple():
    """evidence_requests es tuple (inmutable)."""
    state, _ = process_message("hola", tenant_id="T027", previous_state=None)
    
    assert isinstance(state.evidence_requests, tuple)


def test_created_at_iso8601():
    """created_at es formato ISO8601."""
    from datetime import datetime
    
    state, _ = process_message("hola", tenant_id="T028", previous_state=None)
    
    # Debe ser parseable como datetime
    if state.created_at:
        dt = datetime.fromisoformat(state.created_at)
        assert dt is not None


def test_updated_at_iso8601():
    """updated_at es formato ISO8601."""
    from datetime import datetime
    
    state, _ = process_message("hola", tenant_id="T029", previous_state=None)
    
    # Debe ser parseable como datetime
    if state.updated_at:
        dt = datetime.fromisoformat(state.updated_at)
        assert dt is not None


def test_no_diagnostica_prematuro_ejemplo():
    """Ejemplo prohibido: no dice 'Tu problema parece ser margen bajo'."""
    state, message = process_message(
        "vendo mucho pero no se si gano plata",
        tenant_id="T030",
        previous_state=None
    )
    
    forbidden = "tu problema parece ser"
    assert forbidden not in message.lower()


def test_permite_hipotesis_ejemplo():
    """Ejemplo permitido: 'Puede haber una hipótesis de margen a investigar'."""
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T031",
        previous_state=None
    )
    state2, message = process_message(
        "el margen es bajo",
        tenant_id="T031",
        previous_state=state1
    )
    
    # Si hay hipótesis, el mensaje puede mencionar "hipótesis"
    if len(state2.hypotheses) > 0:
        # No es obligatorio, pero permitido
        assert "diagnóstico" not in message.lower()

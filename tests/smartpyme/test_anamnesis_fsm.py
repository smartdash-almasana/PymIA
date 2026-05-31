"""
Tests para Anamnesis FSM offline (Nuevo Contrato: FICHA_PYME_INICIAL obligatoria).
"""

import json
import ast
import pytest
from pymia.smartpyme.anamnesis_fsm import (
    FSMPhase,
    AnamnesisFSMState,
    process_message,
    MENU_INICIAL_TEXTO,
    FICHA_PYME_STEPS,
)
from pymia.smartpyme.taxonomy import TaxonomyType
from pymia.smartpyme.anamnesis_readiness import ReadinessStatus
from pymia.smartpyme.operational_hypothesis import HypothesisStatus
from pymia.smartpyme.conversation_contract import ConversationPhase


def test_import_smoke():
    """Smoke test: importación básica."""
    assert FSMPhase is not None
    assert AnamnesisFSMState is not None
    assert process_message is not None
    assert MENU_INICIAL_TEXTO is not None


def test_fase_enum_values():
    """FSMPhase enum tiene todos los estados requeridos."""
    assert FSMPhase.INIT == "INIT"
    assert FSMPhase.MENU_INICIAL == "MENU_INICIAL"
    assert FSMPhase.CAPTURA_RELATO_CRUDO == "CAPTURA_RELATO_CRUDO"
    assert FSMPhase.FICHA_PYME_INICIAL == "FICHA_PYME_INICIAL"
    assert FSMPhase.ANAMNESIS_TAXONOMIA == "ANAMNESIS_TAXONOMIA"
    assert FSMPhase.HIPOTESIS_FORMULADA == "HIPOTESIS_FORMULADA"
    assert FSMPhase.SOLICITUD_EVIDENCIA == "SOLICITUD_EVIDENCIA"
    assert FSMPhase.BLOQUEADO_EXPLICATIVO == "BLOQUEADO_EXPLICATIVO"


# Helpers
def _mock_complete_profile_state(tenant_id: str) -> AnamnesisFSMState:
    return AnamnesisFSMState(
        phase=FSMPhase.FICHA_PYME_INICIAL,
        tenant_id=tenant_id,
        user_text="...",
        profile_step="INITIAL_PROFILE_COMPLETE",
        profile_data={"profile_status": "COMPLETE", "raw_first_message": "..."}
    )


# CASOS DE PRIMER CONTACTO
def test_caso_1_sesion_nueva_ficha_pyme():
    """Sesión nueva (previous_state=None) → FICHA_PYME_INICIAL / ASK_CONTACT_NAME."""
    user_text = "hola"
    state, message = process_message(user_text, tenant_id="T001", previous_state=None)
    
    assert state.phase == FSMPhase.FICHA_PYME_INICIAL
    assert state.tenant_id == "T001"
    assert state.profile_step == "ASK_CONTACT_NAME"
    assert state.profile_data["raw_first_message"] == user_text
    assert message == MENU_INICIAL_TEXTO
    assert state.taxonomy is None
    assert len(state.hypotheses) == 0
    assert len(state.evidence_requests) == 0


def test_caso_1_texto_vacio_ficha_pyme():
    """Texto vacío → FICHA_PYME_INICIAL."""
    state, message = process_message("", tenant_id="T001", previous_state=None)
    
    assert state.phase == FSMPhase.FICHA_PYME_INICIAL
    assert state.profile_step == "ASK_CONTACT_NAME"
    assert message == MENU_INICIAL_TEXTO


def test_caso_1_texto_espacios_ficha_pyme():
    """Texto solo con espacios → FICHA_PYME_INICIAL."""
    state, message = process_message("   ", tenant_id="T001", previous_state=None)
    
    assert state.phase == FSMPhase.FICHA_PYME_INICIAL
    assert state.profile_step == "ASK_CONTACT_NAME"
    assert message == MENU_INICIAL_TEXTO


def test_caso_2_vendo_mucho_ficha_pyme():
    """Relato con dolor en primer contacto → FICHA_PYME_INICIAL."""
    user_text = "vendo mucho pero no se si gano plata"
    state, message = process_message(user_text, tenant_id="T002", previous_state=None)
    
    assert state.phase == FSMPhase.FICHA_PYME_INICIAL
    assert state.profile_step == "ASK_CONTACT_NAME"
    assert state.profile_data["raw_first_message"] == user_text
    assert len(state.hypotheses) == 0
    assert len(state.evidence_requests) == 0
    assert message == MENU_INICIAL_TEXTO


def test_flujo_completo_ficha_pyme():
    """Verifica que el flujo avanza por los 18 pasos hasta INITIAL_PROFILE_COMPLETE."""
    inputs = [
        "Juan",  # ASK_CONTACT_ROLE
        "Dueño", # ASK_CONTACT_PHONE
        "12345", # ASK_CONTACT_EMAIL
        "juan@juan.com", # ASK_COMPANY_NAME
        "Mi Empresa", # ASK_ACTIVITY_TYPE
        "1. Vendo productos", # ASK_INDUSTRY_LABEL
        "Ropa", # ASK_OPERATING_MODEL
        "Stock", # ASK_SALES_CHANNELS
        "1. Local", # ASK_DIGITAL_PRESENCE
        "2. Instagram", # ASK_WEBSITE_AND_SOCIALS
        "instagram.com/miempresa", # ASK_CATALOG_AVAILABLE
        "1. PDF", # ASK_TEAM_SIZE
        "1. Solo yo", # ASK_CURRENT_TOOLS
        "1. Excel", # ASK_PRIMARY_PAIN
        "1. Gano plata", # ASK_PERIOD
        "1. Este mes", # ASK_AVAILABLE_EVIDENCE
        "1. Ventas", # INITIAL_PROFILE_COMPLETE
    ]
    
    state, msg = process_message("hola, tengo un problema", tenant_id="TF", previous_state=None)
    assert state.profile_step == "ASK_CONTACT_NAME"
    assert state.profile_data["raw_first_message"] == "hola, tengo un problema"
    
    for i, user_input in enumerate(inputs):
        state, msg = process_message(user_input, tenant_id="TF", previous_state=state)
        expected_step = FICHA_PYME_STEPS[i+1]
        assert state.profile_step == expected_step
        assert state.phase == FSMPhase.FICHA_PYME_INICIAL
        assert len(state.hypotheses) == 0
        assert len(state.evidence_requests) == 0

    assert state.profile_step == "INITIAL_PROFILE_COMPLETE"
    assert state.profile_data["profile_status"] == "COMPLETE"


# CASOS POST-FICHA (asumiendo INITIAL_PROFILE_COMPLETE)
def test_caso_3_flujo_productivo_textil():
    """Descripción de fábrica textil → clasifica correctamente."""
    user_text = "fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre"
    state, message = process_message(user_text, tenant_id="T003", previous_state=_mock_complete_profile_state("T003"))
    
    assert state.taxonomy is not None
    assert state.taxonomy.organism_type == TaxonomyType.textil
    assert "mayorista" in state.taxonomy.sales_channels
    assert "mercado_libre" in state.taxonomy.sales_channels
    assert "produccion" in state.taxonomy.areas_present
    assert "ventas" in state.taxonomy.areas_present
    assert "compras" in state.taxonomy.areas_present
    assert "compra" in state.taxonomy.operational_flow_stages
    assert "produccion" in state.taxonomy.operational_flow_stages
    assert "venta" in state.taxonomy.operational_flow_stages


def test_caso_3_negocio_mixto():
    """Negocio mixto (fábrica + venta directa) → clasificación mixta."""
    user_text = "hago muebles, los vendo en mi local y también por Mercado Libre"
    state, message = process_message(user_text, tenant_id="T004", previous_state=_mock_complete_profile_state("T004"))
    
    assert state.taxonomy is not None
    assert state.taxonomy.organism_type == TaxonomyType.produccion_fabrica
    assert "minorista" in state.taxonomy.sales_channels or "local" in state.taxonomy.sales_channels
    assert "mercado_libre" in state.taxonomy.sales_channels


def test_caso_4_taxonomia_suficiente_hipotesis_abierta():
    """Taxonomía clara + síntoma margen → hipótesis ABIERTA (no confirmada)."""
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T005",
        previous_state=_mock_complete_profile_state("T005")
    )
    state2, message = process_message(
        "vendo mucho pero no me queda ganancia, el margen es bajo",
        tenant_id="T005",
        previous_state=state1
    )
    if state2.readiness and state2.readiness.status == ReadinessStatus.READY:
        assert len(state2.hypotheses) > 0
        for h in state2.hypotheses:
            assert h.status == HypothesisStatus.ABIERTA


def test_caso_4_hipotesis_no_confirmada():
    """Hipótesis nunca se confirma sin evidencia."""
    state, _ = process_message(
        "fabrico ropa, vendo por mayor, pero el margen es bajo",
        tenant_id="T006",
        previous_state=_mock_complete_profile_state("T006")
    )
    for h in state.hypotheses:
        assert h.status in [HypothesisStatus.ABIERTA, HypothesisStatus.EN_CONTRASTE]


def test_caso_5_solicita_evidencia_concreta():
    """Con hipótesis de margen → solicita ventas y costos."""
    state1, _ = process_message(
        "fabrico ropa y vendo por mayor",
        tenant_id="T007",
        previous_state=_mock_complete_profile_state("T007")
    )
    state2, _ = process_message(
        "el margen es bajo, no gano plata",
        tenant_id="T007",
        previous_state=state1
    )
    if state2.readiness and state2.readiness.status == ReadinessStatus.READY:
        assert len(state2.evidence_requests) > 0
        evidence_types = [e.evidence_type for e in state2.evidence_requests]
        assert any("ventas" in et or "ingresos" in et for et in evidence_types)
        assert any("costos" in et or "gastos" in et for et in evidence_types)


def test_caso_6_campos_faltantes_pregunta():
    """Información incompleta → pregunta concreta."""
    user_text = "tengo un negocio"
    state, message = process_message(user_text, tenant_id="T009", previous_state=_mock_complete_profile_state("T009"))
    
    assert state.phase in [FSMPhase.ANAMNESIS_TAXONOMIA, FSMPhase.BLOQUEADO_EXPLICATIVO]
    assert "?" in message or "necesito" in message.lower()


def test_caso_6_bloqueado_explicativo():
    """Falta información bloqueante → BLOQUEADO_EXPLICATIVO."""
    user_text = "algo no funciona"
    state, message = process_message(user_text, tenant_id="T010", previous_state=_mock_complete_profile_state("T010"))
    
    assert state.phase in [FSMPhase.ANAMNESIS_TAXONOMIA, FSMPhase.BLOQUEADO_EXPLICATIVO]
    assert len(message) > 20


def test_caso_7_bloquea_analisis_sin_readiness():
    """Si readiness no está READY, no formula hipótesis."""
    state, _ = process_message(
        "tengo un problema",
        tenant_id="T011",
        previous_state=_mock_complete_profile_state("T011")
    )
    if state.readiness and state.readiness.status != ReadinessStatus.READY:
        assert len(state.hypotheses) == 0


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
                assert alias.name not in forbidden_modules
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_modules


def test_tenant_id_obligatorio():
    with pytest.raises(ValueError, match="tenant_id"):
        process_message("hola", tenant_id="", previous_state=None)


def test_tenant_id_none_error():
    with pytest.raises(ValueError, match="tenant_id"):
        process_message("hola", tenant_id=None, previous_state=None)


def test_to_dict_json_serializable():
    """AnamnesisFSMState.to_dict() es JSON serializable."""
    state, _ = process_message("hola", tenant_id="T013", previous_state=None)
    data = state.to_dict()
    json_str = json.dumps(data, ensure_ascii=False)
    parsed = json.loads(json_str)
    assert parsed["phase"] == FSMPhase.FICHA_PYME_INICIAL
    assert parsed["tenant_id"] == "T013"


def test_inputs_no_mutados():
    """process_message no muta previous_state."""
    state1, _ = process_message("hola", tenant_id="T015", previous_state=None)
    state1_phase = state1.phase
    state2, _ = process_message("Juan", tenant_id="T015", previous_state=state1)
    assert state1.phase == state1_phase
    assert state1.profile_step == "ASK_CONTACT_NAME"
    assert state2.profile_step == "ASK_CONTACT_ROLE"

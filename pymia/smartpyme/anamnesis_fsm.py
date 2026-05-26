"""
Anamnesis FSM offline - Máquina de estados determinística para conversación inicial.

Este módulo implementa un FSM puro y determinístico para guiar la anamnesis
conversacional sin I/O, sin persistencia, sin Telegram y sin ejecución de microservicios.

Estados:
- INIT: sesión nueva
- MENU_INICIAL: presentación de opciones
- CAPTURA_RELATO_CRUDO: recepción de narrativa del dueño
- ANAMNESIS_TAXONOMIA: construcción de BusinessTaxonomySnapshot
- HIPOTESIS_FORMULADA: hipótesis ABIERTA (no confirmada)
- SOLICITUD_EVIDENCIA: pedido de evidencia concreta
- BLOQUEADO_EXPLICATIVO: falta información bloqueante
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import re

from pymia.smartpyme.taxonomy import (
    BusinessTaxonomySnapshot,
    TaxonomyType,
    create_taxonomy_snapshot,
)
from pymia.smartpyme.anamnesis_readiness import (
    AnamnesisReadiness,
    ReadinessStatus,
    evaluate_anamnesis_readiness,
)
from pymia.smartpyme.operational_hypothesis import (
    OperationalHypothesis,
    HypothesisStatus,
    create_hypothesis,
)
from pymia.smartpyme.conversation_contract import (
    ConversationContract,
    ConversationPhase,
    create_conversation_contract,
)
from pymia.smartpyme.evidence_requirement import (
    EvidenceRequirement,
    create_evidence_requirement,
)

__all__ = [
    "FSMPhase",
    "AnamnesisFSMState",
    "process_message",
    "MENU_INICIAL_TEXTO",
]


class FSMPhase(str, Enum):
    """Fases del FSM de anamnesis."""
    INIT = "INIT"
    MENU_INICIAL = "MENU_INICIAL"
    CAPTURA_RELATO_CRUDO = "CAPTURA_RELATO_CRUDO"
    ANAMNESIS_TAXONOMIA = "ANAMNESIS_TAXONOMIA"
    HIPOTESIS_FORMULADA = "HIPOTESIS_FORMULADA"
    SOLICITUD_EVIDENCIA = "SOLICITUD_EVIDENCIA"
    BLOQUEADO_EXPLICATIVO = "BLOQUEADO_EXPLICATIVO"


MENU_INICIAL_TEXTO = """Hola. Antes de revisar números necesito entender tu negocio.

1. Contame qué te preocupa
2. No sé bien, pero algo no me cierra
3. Quiero revisar mis planillas
4. Tengo una pregunta específica"""


@dataclass(frozen=True)
class AnamnesisFSMState:
    """Estado del FSM de anamnesis."""
    phase: str
    tenant_id: str
    user_text: str
    taxonomy: Optional[BusinessTaxonomySnapshot] = None
    contract: Optional[ConversationContract] = None
    hypotheses: tuple[OperationalHypothesis, ...] = ()
    evidence_requests: tuple[EvidenceRequirement, ...] = ()
    readiness: Optional[AnamnesisReadiness] = None
    blocking_reasons: tuple[str, ...] = ()
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "tenant_id": self.tenant_id,
            "user_text": self.user_text,
            "taxonomy": self.taxonomy.to_dict() if self.taxonomy else None,
            "contract": self.contract.to_dict() if self.contract else None,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "evidence_requests": [e.to_dict() for e in self.evidence_requests],
            "readiness": self.readiness.to_dict() if self.readiness else None,
            "blocking_reasons": list(self.blocking_reasons),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def _detect_organism_type(text: str) -> str:
    """Detecta tipo de organismo desde narrativa."""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in ["fabrico", "produzco", "elaboro", "manufactura", "corto", "coso"]):
        return TaxonomyType.INDUSTRIA
    if any(kw in text_lower for kw in ["revendo", "compro y vendo", "distribuidor"]):
        return TaxonomyType.COMERCIO
    if any(kw in text_lower for kw in ["servicio", "consultoría", "asesoro"]):
        return TaxonomyType.SERVICIOS
    if any(kw in text_lower for kw in ["logística", "transporte", "envíos"]):
        return TaxonomyType.LOGISTICA
    
    return TaxonomyType.DESCONOCIDO


def _detect_sales_channels(text: str) -> list[str]:
    """Detecta canales de venta desde narrativa."""
    text_lower = text.lower()
    channels = []
    
    if "mayor" in text_lower or "mayorista" in text_lower:
        channels.append("mayorista")
    if "minorista" in text_lower or "local" in text_lower or "tienda" in text_lower:
        channels.append("minorista")
    if "mercado libre" in text_lower or "ml" in text_lower:
        channels.append("mercado_libre")
    if "online" in text_lower or "web" in text_lower or "ecommerce" in text_lower:
        channels.append("online")
    
    return channels if channels else ["desconocido"]


def _detect_areas(text: str) -> list[str]:
    """Detecta áreas presentes desde narrativa."""
    text_lower = text.lower()
    areas = []
    
    if any(kw in text_lower for kw in ["stock", "inventario", "almacén"]):
        areas.append("stock")
    if any(kw in text_lower for kw in ["caja", "banco", "cobros", "pagos"]):
        areas.append("caja")
    if any(kw in text_lower for kw in ["producción", "fabricación", "elaboración"]):
        areas.append("produccion")
    if any(kw in text_lower for kw in ["ventas", "vendo"]):
        areas.append("ventas")
    if any(kw in text_lower for kw in ["compras", "proveedores"]):
        areas.append("compras")
    if any(kw in text_lower for kw in ["sueldos", "empleados", "rrhh"]):
        areas.append("rrhh")
    
    return areas if areas else ["desconocido"]


def _detect_symptoms(text: str) -> list[str]:
    """Detecta síntomas candidatos desde narrativa."""
    text_lower = text.lower()
    symptoms = []
    
    if any(kw in text_lower for kw in ["margen", "ganancia", "no gano", "no me queda"]):
        symptoms.append("margen_erosionado")
    if any(kw in text_lower for kw in ["stock", "inventario", "parado", "no rota"]):
        symptoms.append("stock_estancado")
    if any(kw in text_lower for kw in ["caja", "efectivo", "no entra"]):
        symptoms.append("flujo_caja_negativo")
    if any(kw in text_lower for kw in ["precios", "subir", "bajar"]):
        symptoms.append("precios_desalineados")
    
    return symptoms


def process_message(
    user_text: str,
    tenant_id: str,
    previous_state: Optional[AnamnesisFSMState] = None,
) -> tuple[AnamnesisFSMState, str]:
    """
    Procesa mensaje del usuario y devuelve nuevo estado + mensaje para el usuario.
    
    Args:
        user_text: texto del dueño
        tenant_id: identificador del tenant
        previous_state: estado previo (None si es sesión nueva)
    
    Returns:
        (nuevo_estado, mensaje_para_usuario)
    
    Raises:
        ValueError: si tenant_id vacío
    """
    if not tenant_id or not isinstance(tenant_id, str):
        raise ValueError("tenant_id obligatorio")
    
    user_text = user_text.strip() if user_text else ""
    
    # Sesión nueva o texto vacío → menú inicial
    if previous_state is None or not user_text:
        new_state = AnamnesisFSMState(
            phase=FSMPhase.MENU_INICIAL,
            tenant_id=tenant_id,
            user_text=user_text,
            created_at=_now_iso(),
            updated_at=_now_iso(),
        )
        return new_state, MENU_INICIAL_TEXTO
    
    # Detectar si el texto es un número de menú
    if user_text in ["1", "2", "3", "4"]:
        if user_text == "1":
            new_state = AnamnesisFSMState(
                phase=FSMPhase.CAPTURA_RELATO_CRUDO,
                tenant_id=tenant_id,
                user_text=user_text,
                contract=create_conversation_contract(
                    tenant_id=tenant_id,
                    current_phase=ConversationPhase.ANAMNESIS,
                ),
                created_at=_now_iso(),
                updated_at=_now_iso(),
            )
            return new_state, "Perfecto. Contame con tus palabras qué te preocupa de tu negocio."
        elif user_text == "2":
            new_state = AnamnesisFSMState(
                phase=FSMPhase.CAPTURA_RELATO_CRUDO,
                tenant_id=tenant_id,
                user_text=user_text,
                contract=create_conversation_contract(
                    tenant_id=tenant_id,
                    current_phase=ConversationPhase.ANAMNESIS,
                ),
                created_at=_now_iso(),
                updated_at=_now_iso(),
            )
            return new_state, "Entendido. Contame un poco qué haces, qué vendés, y qué sentís que no está funcionando."
        elif user_text == "3":
            new_state = AnamnesisFSMState(
                phase=FSMPhase.CAPTURA_RELATO_CRUDO,
                tenant_id=tenant_id,
                user_text=user_text,
                contract=create_conversation_contract(
                    tenant_id=tenant_id,
                    current_phase=ConversationPhase.ANAMNESIS,
                ),
                created_at=_now_iso(),
                updated_at=_now_iso(),
            )
            return new_state, "Bien. Contame qué planillas tenés y qué información registran."
        elif user_text == "4":
            new_state = AnamnesisFSMState(
                phase=FSMPhase.CAPTURA_RELATO_CRUDO,
                tenant_id=tenant_id,
                user_text=user_text,
                contract=create_conversation_contract(
                    tenant_id=tenant_id,
                    current_phase=ConversationPhase.ANAMNESIS,
                ),
                created_at=_now_iso(),
                updated_at=_now_iso(),
            )
            return new_state, "Dale. Escribí tu pregunta y te contesto lo que pueda."
    
    # Proceso de anamnesis: detectar taxonomía, síntomas, hipótesis
    taxonomy_data = _extract_taxonomy_from_text(user_text, previous_state)
    symptoms = _detect_symptoms(user_text)
    
    # Crear o actualizar taxonomía
    if taxonomy_data.get("organism_type") and taxonomy_data["organism_type"] != TaxonomyType.DESCONOCIDO:
        try:
            taxonomy = create_taxonomy_snapshot(
                tenant_id=tenant_id,
                organism_type=taxonomy_data["organism_type"],
                sales_channels=taxonomy_data.get("sales_channels", []),
                operational_flow_stages=taxonomy_data.get("operational_flow_stages", []),
                areas_present=taxonomy_data.get("areas_present", []),
                jurisdiction="AR",
                currency="ARS",
                confidence=taxonomy_data.get("confidence", 0.7),
            )
        except Exception:
            taxonomy = previous_state.taxonomy if previous_state else None
    else:
        taxonomy = previous_state.taxonomy if previous_state else None
    
    # Evaluar readiness
    if taxonomy and symptoms:
        readiness = evaluate_anamnesis_readiness(
            taxonomy=taxonomy,
            candidate_symptoms=symptoms,
            evidence_available=taxonomy_data.get("evidence_available", []),
        )
    else:
        readiness = AnamnesisReadiness(
            status=ReadinessStatus.NEEDS_MORE_INFO,
            taxonomy_complete=False,
            narrative_sufficient=bool(user_text),
            blocking_reasons=("Falta información de taxonomía o síntomas",),
            tenant_id=tenant_id,
        )
    
    # Si readiness está READY y hay síntomas → formular hipótesis
    hypotheses = list(previous_state.hypotheses) if previous_state else []
    if readiness.status == ReadinessStatus.READY and symptoms and taxonomy:
        for symptom in symptoms:
            hypothesis = create_hypothesis(
                tenant_id=tenant_id,
                formulation=f"Posible problema relacionado con {symptom.replace('_', ' ')}",
                domain=symptom,
                related_symptoms=(symptom,),
                required_evidence=(f"evidencia_{symptom}",),
            )
            hypotheses.append(hypothesis)
    
    # Si hay hipótesis abiertas → solicitar evidencia
    evidence_requests = list(previous_state.evidence_requests) if previous_state else []
    if hypotheses and readiness.status == ReadinessStatus.READY:
        for hypothesis in hypotheses:
            if hypothesis.status == HypothesisStatus.ABIERTA:
                if "margen" in hypothesis.domain:
                    evidence_requests.append(create_evidence_requirement(
                        tenant_id=tenant_id,
                        evidence_type="ventas_del_periodo",
                        description="Listado de ventas con fechas, importes y productos",
                        priority="ALTA",
                    ))
                    evidence_requests.append(create_evidence_requirement(
                        tenant_id=tenant_id,
                        evidence_type="costos_y_gastos",
                        description="Listado de costos, gastos y facturas de proveedores",
                        priority="ALTA",
                    ))
                elif "stock" in hypothesis.domain:
                    evidence_requests.append(create_evidence_requirement(
                        tenant_id=tenant_id,
                        evidence_type="inventario_actual",
                        description="Listado de productos en stock con cantidades y antigüedad",
                        priority="ALTA",
                    ))
    
    # Determinar fase y mensaje
    if not taxonomy or taxonomy.organism_type == TaxonomyType.DESCONOCIDO:
        phase = FSMPhase.ANAMNESIS_TAXONOMIA
        message = "Para poder ayudarte mejor necesito entender un poco más sobre tu negocio. ¿Qué tipo de actividad haces? ¿Vendés productos, fabricás algo, o das servicios?"
    elif hypotheses and readiness.status == ReadinessStatus.READY:
        phase = FSMPhase.HIPOTESIS_FORMULADA
        hypothesis_text = " y ".join([h.formulation for h in hypotheses])
        message = f"Puede haber una hipótesis a investigar: {hypothesis_text}. Para avanzar necesito evidencia concreta."
        
        if evidence_requests:
            phase = FSMPhase.SOLICITUD_EVIDENCIA
            evidence_desc = " y ".join([e.description for e in evidence_requests[:2]])
            message = f"Puede haber una hipótesis a investigar. Para avanzar necesito: {evidence_desc}. ¿Podés compartirlos?"
    elif readiness.status == ReadinessStatus.BLOCKED:
        phase = FSMPhase.BLOQUEADO_EXPLICATIVO
        blocking = " y ".join(readiness.blocking_reasons) if readiness.blocking_reasons else "Falta información esencial"
        message = f"No puedo avanzar todavía porque {blocking}. ¿Podés contarme más sobre eso?"
    else:
        phase = FSMPhase.ANAMNESIS_TAXONOMIA
        message = "Gracias por la información. Para entender mejor tu situación, ¿podrías contarme cómo es tu flujo de trabajo? ¿Qué comprás, qué producís, y cómo vendés?"
    
    # Actualizar contrato
    contract_phase = ConversationPhase.ANAMNESIS
    if phase == FSMPhase.HIPOTESIS_FORMULADA:
        contract_phase = ConversationPhase.CONTRAST
    elif phase == FSMPhase.SOLICITUD_EVIDENCIA:
        contract_phase = ConversationPhase.EVIDENCE
    
    contract = previous_state.contract if previous_state else create_conversation_contract(
        tenant_id=tenant_id,
        current_phase=contract_phase,
    )
    if contract.current_phase != contract_phase:
        from pymia.smartpyme.conversation_contract import update_contract_phase
        contract = update_contract_phase(contract, contract_phase)
    
    new_state = AnamnesisFSMState(
        phase=phase,
        tenant_id=tenant_id,
        user_text=user_text,
        taxonomy=taxonomy,
        contract=contract,
        hypotheses=tuple(hypotheses),
        evidence_requests=tuple(evidence_requests),
        readiness=readiness,
        blocking_reasons=readiness.blocking_reasons if readiness else (),
        created_at=previous_state.created_at if previous_state else _now_iso(),
        updated_at=_now_iso(),
    )
    
    return new_state, message


def _extract_taxonomy_from_text(text: str, previous_state: Optional[AnamnesisFSMState]) -> dict:
    """Extrae datos de taxonomía desde narrativa."""
    organism_type = _detect_organism_type(text)
    sales_channels = _detect_sales_channels(text)
    areas = _detect_areas(text)
    
    # Detectar flujo operativo
    flow_stages = []
    text_lower = text.lower()
    if "compro" in text_lower or "compra" in text_lower:
        flow_stages.append("compra")
    if "fabrico" in text_lower or "produzco" in text_lower:
        flow_stages.append("produccion")
    if "empaco" in text_lower or "empaquetar" in text_lower:
        flow_stages.append("empaque")
    if "vendo" in text_lower or "venta" in text_lower:
        flow_stages.append("venta")
    
    confidence = 0.5
    if organism_type != TaxonomyType.DESCONOCIDO:
        confidence += 0.2
    if len(sales_channels) > 0 and sales_channels[0] != "desconocido":
        confidence += 0.2
    if len(areas) > 0 and areas[0] != "desconocido":
        confidence += 0.1
    
    confidence = min(confidence, 1.0)
    
    return {
        "organism_type": organism_type,
        "sales_channels": sales_channels,
        "operational_flow_stages": flow_stages,
        "areas_present": areas,
        "confidence": confidence,
        "evidence_available": [],
    }


def _now_iso() -> str:
    """Timestamp UTC ISO8601."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

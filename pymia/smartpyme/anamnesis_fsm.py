"""
Anamnesis FSM offline - Máquina de estados determinística para conversación inicial.

Este módulo guía la anamnesis conversacional sin I/O, sin persistencia, sin Telegram
ni ejecución de microservicios. Solo usa contratos puros de SmartPyme.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pymia.smartpyme.anamnesis_readiness import (
    AnamnesisReadiness,
    ReadinessStatus,
    evaluate_anamnesis_readiness,
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
from pymia.smartpyme.operational_hypothesis import (
    HypothesisStatus,
    OperationalHypothesis,
    create_hypothesis,
)
from pymia.smartpyme.taxonomy import (
    BusinessTaxonomySnapshot,
    TaxonomyType,
    create_taxonomy_snapshot,
)

__all__ = [
    "FSMPhase",
    "AnamnesisFSMState",
    "process_message",
    "MENU_INICIAL_TEXTO",
]


class FSMPhase(str, Enum):
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
    phase: FSMPhase | str
    tenant_id: str
    user_text: str
    taxonomy: BusinessTaxonomySnapshot | None = None
    contract: ConversationContract | None = None
    hypotheses: tuple[OperationalHypothesis, ...] = ()
    evidence_requests: tuple[EvidenceRequirement, ...] = ()
    readiness: AnamnesisReadiness | None = None
    blocking_reasons: tuple[str, ...] = ()
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.value if isinstance(self.phase, Enum) else self.phase,
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_contract(tenant_id: str, phase: ConversationPhase = ConversationPhase.ANAMNESIS) -> ConversationContract:
    return create_conversation_contract(
        contract_id=f"contract-{tenant_id}",
        tenant_id=tenant_id,
        anamnesis_ref=f"anamnesis-{tenant_id}",
        taxonomy_ref=f"taxonomy-{tenant_id}",
        current_phase=phase,
        allowed_actions=["preguntar", "pedir_evidencia", "formular_hipotesis_abierta"],
        forbidden_actions=["diagnosticar", "saltar_gate", "ejecutar_microservicio"],
    )


def _detect_organism_type(text: str) -> TaxonomyType | None:
    t = text.lower()
    if any(k in t for k in ["ropa", "tela", "coso", "corto", "talles"]):
        return TaxonomyType.textil
    if any(k in t for k in ["fabrico", "produzco", "elaboro", "manufactura", "hago muebles"]):
        return TaxonomyType.produccion_fabrica
    if any(k in t for k in ["revendo", "compro y vendo", "local", "tienda", "comercio"]):
        return TaxonomyType.comercio
    if any(k in t for k in ["servicio", "consultoría", "asesoro"]):
        return TaxonomyType.servicios
    if any(k in t for k in ["logística", "transporte", "envíos", "distribuyo"]):
        return TaxonomyType.distribucion
    if any(k in t for k in ["restaurante", "bar", "comida", "gastronom"]):
        return TaxonomyType.gastronomia
    return None


def _detect_sales_channels(text: str) -> list[str]:
    t = text.lower()
    channels: list[str] = []
    if "mayor" in t or "mayorista" in t:
        channels.append("mayorista")
    if "minorista" in t or "local" in t or "tienda" in t:
        channels.append("minorista")
    if "mercado libre" in t or " ml" in t:
        channels.append("mercado_libre")
    if "online" in t or "web" in t or "ecommerce" in t:
        channels.append("online")
    return channels


def _detect_areas(text: str) -> list[str]:
    t = text.lower()
    areas: list[str] = []
    if any(k in t for k in ["stock", "inventario", "almacén", "deposito", "depósito"]):
        areas.append("stock")
    if any(k in t for k in ["caja", "banco", "cobros", "pagos"]):
        areas.append("caja")
    if any(k in t for k in ["producción", "produccion", "fabric", "elabor", "coso", "corto"]):
        areas.append("produccion")
    if any(k in t for k in ["ventas", "vendo", "venta"]):
        areas.append("ventas")
    if any(k in t for k in ["compras", "proveedores", "compro", "materia prima", "tela"]):
        areas.append("compras")
    if any(k in t for k in ["sueldos", "empleados", "rrhh"]):
        areas.append("rrhh")
    return areas


def _detect_flow(text: str) -> list[str]:
    t = text.lower()
    stages: list[str] = []
    if any(k in t for k in ["compro", "compras", "materia prima", "proveedores", "tela"]):
        stages.append("compra")
    if any(k in t for k in ["fabrico", "produzco", "elaboro", "corto", "coso", "hago"]):
        stages.append("produccion")
    if any(k in t for k in ["empaco", "empaque", "packaging"]):
        stages.append("empaque")
    if any(k in t for k in ["vendo", "venta", "mayor", "minorista", "mercado libre", "local"]):
        stages.append("venta")
    return stages


def _detect_systems(text: str) -> list[str]:
    t = text.lower()
    systems: list[str] = []
    if "excel" in t or "planilla" in t:
        systems.append("excel")
    if "sistema" in t or "erp" in t:
        systems.append("sistema")
    return systems or ["pendiente_confirmacion"]


def _detect_symptoms(text: str) -> list[str]:
    t = text.lower()
    symptoms: list[str] = []
    if any(k in t for k in ["margen", "ganancia", "no gano", "no me queda", "gano plata"]):
        symptoms.append("margen_erosionado")
    if any(k in t for k in ["stock", "inventario", "parado", "no rota"]):
        symptoms.append("stock_estancado")
    if any(k in t for k in ["caja", "efectivo", "no entra"]):
        symptoms.append("flujo_caja_negativo")
    if any(k in t for k in ["precios", "subir", "bajar"]):
        symptoms.append("precios_desalineados")
    return symptoms


def _merge_unique(*items: list[str]) -> list[str]:
    out: list[str] = []
    for group in items:
        for item in group:
            if item and item not in out:
                out.append(item)
    return out


def _taxonomy_from_text(text: str, tenant_id: str, previous: BusinessTaxonomySnapshot | None) -> BusinessTaxonomySnapshot | None:
    organism_type = _detect_organism_type(text) or (previous.organism_type if previous else None)
    if organism_type is None:
        return previous
    sales_channels = _merge_unique(previous.sales_channels if previous else [], _detect_sales_channels(text))
    areas_present = _merge_unique(previous.areas_present if previous else [], _detect_areas(text))
    flow = _merge_unique(previous.operational_flow_stages if previous else [], _detect_flow(text))
    systems = _merge_unique(previous.systems_available if previous else [], _detect_systems(text))
    confidence = 0.8 if flow and sales_channels and systems else 0.55
    if previous:
        confidence = max(previous.confidence, confidence)
    return create_taxonomy_snapshot(
        tenant_id=tenant_id,
        organism_type=organism_type,
        industry=organism_type.value,
        size="pendiente_confirmacion",
        complexity="multi_area" if len(areas_present) >= 3 or len(sales_channels) >= 2 else "simple",
        sales_channels=sales_channels,
        operational_flow_stages=flow,
        areas_present=areas_present,
        systems_available=systems,
        jurisdiction="AR",
        currency="ARS",
        confidence=confidence,
    )


def _readiness_for(tenant_id: str, taxonomy: BusinessTaxonomySnapshot | None, symptoms: list[str]) -> AnamnesisReadiness:
    if taxonomy is None:
        return AnamnesisReadiness(
            tenant_id=tenant_id,
            anamnesis_id="anamnesis_needs_info",
            status=ReadinessStatus.NEEDS_MORE_INFO,
            taxonomy_complete=False,
            narrative_sufficient=bool(symptoms),
            blocking_reasons=[],
            missing_taxonomy_fields=["organism_type", "operational_flow_stages", "sales_channels", "systems_available"],
        )
    return evaluate_anamnesis_readiness(taxonomy, {"candidate_symptoms": symptoms})


def _hypothesis_for(tenant_id: str, symptom: str) -> OperationalHypothesis:
    return create_hypothesis(
        hypothesis_id=f"hyp-{tenant_id}-{symptom}",
        tenant_id=tenant_id,
        intake_id=f"intake-{tenant_id}",
        formulation=f"Hipótesis abierta a contrastar sobre {symptom.replace('_', ' ')}",
        source="anamnesis_fsm",
        domain=symptom,
        related_symptoms=[symptom],
        required_evidence=["ventas_del_periodo", "costos_y_gastos"] if "margen" in symptom else ["inventario_actual"],
    )


def _evidence_for(tenant_id: str, hypothesis: OperationalHypothesis) -> list[EvidenceRequirement]:
    if "margen" in hypothesis.domain:
        return [
            create_evidence_requirement(
                requirement_id=f"req-{tenant_id}-ventas",
                tenant_id=tenant_id,
                intake_id=hypothesis.intake_id,
                hypothesis_id=hypothesis.hypothesis_id,
                evidence_type="ventas_del_periodo",
                description="ventas del período con fechas, importes y productos",
                required_fields=["fecha", "producto", "importe"],
                reason="contrastar hipótesis de margen",
                blocks_analysis=True,
                priority=1,
                telegram_message="Para contrastar margen necesito ventas del período con fechas, productos e importes.",
            ),
            create_evidence_requirement(
                requirement_id=f"req-{tenant_id}-costos",
                tenant_id=tenant_id,
                intake_id=hypothesis.intake_id,
                hypothesis_id=hypothesis.hypothesis_id,
                evidence_type="costos_y_gastos",
                description="costos, gastos o facturas/listas de proveedor",
                required_fields=["producto", "costo"],
                reason="comparar ventas contra costos",
                blocks_analysis=True,
                priority=1,
                telegram_message="También necesito costos, gastos o facturas/listas de proveedor para comparar contra ventas.",
            ),
        ]
    if "stock" in hypothesis.domain:
        return [
            create_evidence_requirement(
                requirement_id=f"req-{tenant_id}-stock",
                tenant_id=tenant_id,
                intake_id=hypothesis.intake_id,
                hypothesis_id=hypothesis.hypothesis_id,
                evidence_type="inventario_actual",
                description="inventario actual con productos y cantidades",
                required_fields=["producto", "cantidad"],
                reason="contrastar hipótesis de stock",
                blocks_analysis=True,
                priority=1,
                telegram_message="Para contrastar stock necesito inventario actual con productos y cantidades.",
            )
        ]
    return []


def process_message(
    user_text: str,
    tenant_id: str,
    previous_state: AnamnesisFSMState | None = None,
) -> tuple[AnamnesisFSMState, str]:
    if not tenant_id or not isinstance(tenant_id, str):
        raise ValueError("tenant_id obligatorio")
    text = user_text.strip() if user_text else ""
    now = _now_iso()

    if previous_state is None and (not text or text.lower() in {"hola", "buenas", "inicio"}):
        return (
            AnamnesisFSMState(
                phase=FSMPhase.MENU_INICIAL,
                tenant_id=tenant_id,
                user_text=text,
                created_at=now,
                updated_at=now,
            ),
            MENU_INICIAL_TEXTO,
        )

    if text in {"1", "2", "3", "4"}:
        prompts = {
            "1": "Perfecto. Contame con tus palabras qué te preocupa de tu negocio.",
            "2": "Entendido. Contame qué hacés, qué vendés y qué sentís que no está funcionando.",
            "3": "Bien. Antes de pedir planillas, contame qué tipo de negocio tenés y cómo funciona.",
            "4": "Dale. Escribí tu pregunta y la encuadramos sin diagnosticar sin evidencia.",
        }
        return (
            AnamnesisFSMState(
                phase=FSMPhase.CAPTURA_RELATO_CRUDO,
                tenant_id=tenant_id,
                user_text=text,
                contract=_base_contract(tenant_id),
                created_at=previous_state.created_at if previous_state else now,
                updated_at=now,
            ),
            prompts[text],
        )

    previous_taxonomy = previous_state.taxonomy if previous_state else None
    taxonomy = _taxonomy_from_text(text, tenant_id, previous_taxonomy)
    symptoms = _detect_symptoms(text)
    readiness = _readiness_for(tenant_id, taxonomy, symptoms)

    previous_hypotheses = list(previous_state.hypotheses) if previous_state else []
    new_hypotheses: list[OperationalHypothesis] = []
    if readiness.status == ReadinessStatus.READY:
        existing_domains = {h.domain for h in previous_hypotheses}
        for symptom in symptoms:
            if symptom not in existing_domains:
                new_hypotheses.append(_hypothesis_for(tenant_id, symptom))
    hypotheses = previous_hypotheses + new_hypotheses

    evidence_requests = list(previous_state.evidence_requests) if previous_state else []
    if new_hypotheses:
        for hypothesis in new_hypotheses:
            if hypothesis.status == HypothesisStatus.ABIERTA:
                evidence_requests.extend(_evidence_for(tenant_id, hypothesis))

    if not taxonomy:
        phase = FSMPhase.ANAMNESIS_TAXONOMIA
        message = "Para poder ayudarte necesito entender tu negocio: ¿vendés productos, fabricás algo o prestás servicios?"
    elif evidence_requests:
        phase = FSMPhase.SOLICITUD_EVIDENCIA
        descriptions = " y ".join(e.description for e in evidence_requests[:2])
        message = f"Puede haber una hipótesis a investigar. Para avanzar necesito {descriptions}."
    elif readiness.status == ReadinessStatus.READY and hypotheses:
        phase = FSMPhase.HIPOTESIS_FORMULADA
        message = "Puede haber una hipótesis abierta a contrastar. Todavía no es diagnóstico; falta evidencia."
    elif readiness.status == ReadinessStatus.BLOCKED:
        phase = FSMPhase.BLOQUEADO_EXPLICATIVO
        reason = "; ".join(readiness.blocking_reasons) or "falta información esencial"
        message = f"No puedo avanzar todavía porque {reason}. ¿Podés contarme más?"
    else:
        phase = FSMPhase.ANAMNESIS_TAXONOMIA
        message = "Gracias. Para seguir necesito confirmar cómo funciona tu negocio y qué registros tenés."

    contract_phase = ConversationPhase.EVIDENCIA if evidence_requests else ConversationPhase.HIPOTESIS if hypotheses else ConversationPhase.ANAMNESIS
    state = AnamnesisFSMState(
        phase=phase,
        tenant_id=tenant_id,
        user_text=text,
        taxonomy=taxonomy,
        contract=_base_contract(tenant_id, contract_phase),
        hypotheses=tuple(hypotheses),
        evidence_requests=tuple(evidence_requests),
        readiness=readiness,
        blocking_reasons=tuple(readiness.blocking_reasons),
        created_at=previous_state.created_at if previous_state else now,
        updated_at=now,
    )
    return state, message

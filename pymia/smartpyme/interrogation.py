"""
SmartPyme Interrogation Taxonomy Slice.

Slice mínimo determinístico de interrogatorio inicial previo al análisis.
NO diagnostica. NO ejecuta análisis. NO procesa documentos.
Recibe relato crudo + selectores estructurales opcionales.
Devuelve contexto, síntomas candidatos, dominio y evidencia requerida.

Principio central:
    Los selectores ubican el organismo.
    El texto/audio expresa el síntoma.

Ver: docs/smartpyme/SMARTPYME_INTERROGATION_SLICE.md
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Estados del interrogatorio
# ---------------------------------------------------------------------------
STATUS_RAW_CAPTURED = "RAW_CAPTURED"
STATUS_NEEDS_ORGANISM_CONTEXT = "NEEDS_ORGANISM_CONTEXT"
STATUS_OWNER_CLAIM_REFORMULATED = "OWNER_CLAIM_REFORMULATED"
STATUS_WAITING_OWNER_CONFIRMATION = "WAITING_OWNER_CONFIRMATION"
STATUS_NEEDS_DISAMBIGUATION = "NEEDS_DISAMBIGUATION"
STATUS_HYPOTHESIS_OPEN = "HYPOTHESIS_OPEN"
STATUS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
STATUS_READY_FOR_TAXONOMIC_ROUTING = "READY_FOR_TAXONOMIC_ROUTING"
STATUS_BLOCKED_INSUFFICIENT_CONTEXT = "BLOCKED_INSUFFICIENT_CONTEXT"

ALLOWED_STATUSES = (
    STATUS_RAW_CAPTURED,
    STATUS_NEEDS_ORGANISM_CONTEXT,
    STATUS_OWNER_CLAIM_REFORMULATED,
    STATUS_WAITING_OWNER_CONFIRMATION,
    STATUS_NEEDS_DISAMBIGUATION,
    STATUS_HYPOTHESIS_OPEN,
    STATUS_NEEDS_EVIDENCE,
    STATUS_READY_FOR_TAXONOMIC_ROUTING,
    STATUS_BLOCKED_INSUFFICIENT_CONTEXT,
)


# ---------------------------------------------------------------------------
# Síntomas operacionales mínimos
# ---------------------------------------------------------------------------
SYMPTOM_DESCUADRE_DINERO = "DESCUADRE_DINERO"
SYMPTOM_MARGEN_DUDOSO = "MARGEN_DUDOSO"
SYMPTOM_DATOS_DUPLICADOS = "DATOS_DUPLICADOS"
SYMPTOM_STOCK_INCONSISTENTE = "STOCK_INCONSISTENTE"
SYMPTOM_SOBRECARGA_MANUAL = "SOBRECARGA_MANUAL"
SYMPTOM_COSTO_INCIERTO = "COSTO_INCIERTO"
SYMPTOM_DOCUMENTACION_DESORDENADA = "DOCUMENTACION_DESORDENADA"
SYMPTOM_MAESTRO_DESORDENADO = "MAESTRO_DESORDENADO"
SYMPTOM_DESCONOCIDO = "DESCONOCIDO"

ALLOWED_SYMPTOMS = (
    SYMPTOM_DESCUADRE_DINERO,
    SYMPTOM_MARGEN_DUDOSO,
    SYMPTOM_DATOS_DUPLICADOS,
    SYMPTOM_STOCK_INCONSISTENTE,
    SYMPTOM_SOBRECARGA_MANUAL,
    SYMPTOM_COSTO_INCIERTO,
    SYMPTOM_DOCUMENTACION_DESORDENADA,
    SYMPTOM_MAESTRO_DESORDENADO,
    SYMPTOM_DESCONOCIDO,
)


# ---------------------------------------------------------------------------
# Dominios candidatos
# ---------------------------------------------------------------------------
DOMAIN_FINANZAS = "finanzas"
DOMAIN_COMERCIAL = "comercial"
DOMAIN_PROVEEDORES = "proveedores"
DOMAIN_STOCK = "stock"
DOMAIN_PRODUCCION = "produccion"
DOMAIN_ADMINISTRACION = "administracion"
DOMAIN_AUTOMATIZACION = "automatizacion"
DOMAIN_DATOS_MAESTROS = "datos_maestros"
DOMAIN_DESCONOCIDO = "desconocido"

ALLOWED_DOMAINS = (
    DOMAIN_FINANZAS,
    DOMAIN_COMERCIAL,
    DOMAIN_PROVEEDORES,
    DOMAIN_STOCK,
    DOMAIN_PRODUCCION,
    DOMAIN_ADMINISTRACION,
    DOMAIN_AUTOMATIZACION,
    DOMAIN_DATOS_MAESTROS,
    DOMAIN_DESCONOCIDO,
)


# ---------------------------------------------------------------------------
# Clasificaciones sugeridas (solo las reales implementadas)
# ---------------------------------------------------------------------------
CLASSIFICATION_EXCEL_DIAGNOSTIC = "excel_diagnostic"
CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK = "supplier_duplicate_check"


# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------
@dataclass
class StructuredSelectors:
    """Microcuestionario estructural no inductivo.
    Ubica el organismo, no diagnostica el síntoma."""
    sales_channel: Optional[str] = None        # Local / Mayorista / ML / Ecommerce / Instagram / Mixto
    operation_type: Optional[str] = None       # Revendo / Produzco / Servicios / Distribuyo / Mixto
    stock_mode: Optional[str] = None           # Sí / No / Informal
    tools_used: Optional[str] = None           # Excel / Sistema / Cuaderno / Varios
    evidence_available: Optional[str] = None   # Excel / PDF / Capturas / AudioTexto / NoSe
    employee_range: Optional[str] = None
    marketplace_presence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class EvidenceNeed:
    evidence_type: str
    description: str
    required_fields: List[str]
    reason: str


@dataclass
class ClarificationQuestion:
    question: str
    target_symptom: str
    target_domain: str


@dataclass
class InterrogationResult:
    raw_input: str
    normalized_terms: List[str]
    business_context: Dict[str, Any]
    reformulation: str
    confirmation_question: str
    semantic_signals: List[str]
    candidate_symptoms: List[str]
    candidate_domains: List[str]
    clarification_questions: List[ClarificationQuestion]
    evidence_needs: List[EvidenceNeed]
    status: str
    suggested_classification: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_input": self.raw_input,
            "normalized_terms": self.normalized_terms,
            "business_context": self.business_context,
            "reformulation": self.reformulation,
            "confirmation_question": self.confirmation_question,
            "semantic_signals": self.semantic_signals,
            "candidate_symptoms": self.candidate_symptoms,
            "candidate_domains": self.candidate_domains,
            "clarification_questions": [
                {"question": q.question,
                 "target_symptom": q.target_symptom,
                 "target_domain": q.target_domain}
                for q in self.clarification_questions
            ],
            "evidence_needs": [
                {"evidence_type": e.evidence_type,
                 "description": e.description,
                 "required_fields": e.required_fields,
                 "reason": e.reason}
                for e in self.evidence_needs
            ],
            "status": self.status,
            "suggested_classification": self.suggested_classification,
        }


# ---------------------------------------------------------------------------
# Patrones léxicos (minúsculas, sin tildes, normalizado)
# ---------------------------------------------------------------------------
_LEX_PATTERNS: Dict[str, List[str]] = {
    SYMPTOM_DESCUADRE_DINERO: [
        "no me cierra", "no cierra", "plata", "caja", "banco",
        "cobros", "no coincide", "falta plata", "no llega",
    ],
    SYMPTOM_MARGEN_DUDOSO: [
        "margen", "precio", "costo", "no me queda", "no queda",
        "vendo mucho pero", "no queda nada", "rentabilidad",
    ],
    SYMPTOM_DATOS_DUPLICADOS: [
        "duplicad", "repetid", "cuit", "razon social", "razón social",
        "dos veces", "proveedor repetid",
    ],
    SYMPTOM_STOCK_INCONSISTENTE: [
        "stock", "deposito", "depósito", "faltante", "sistema dice",
        "no coincide stock", "mercaderia", "mercadería",
    ],
    SYMPTOM_SOBRECARGA_MANUAL: [
        "copio", "a mano", "manual", "doble carga", "excel imposible",
        "reingreso", "cargo dos veces",
    ],
    SYMPTOM_COSTO_INCIERTO: [
        "no se cuanto cuesta", "no sé cuánto cuesta", "costo real",
        "costos incompletos",
    ],
    SYMPTOM_DOCUMENTACION_DESORDENADA: [
        "papeles", "facturas desorden", "facturas desordén",
        "documentacion desorden", "documentación desorden",
    ],
    SYMPTOM_MAESTRO_DESORDENADO: [
        "maestro", "listado de proveed", "listado de client",
        "listado de product", "base desorden",
    ],
}


# Preguntas de desambiguación específicas por síntoma
_CLARIFICATION_QUESTIONS: Dict[str, str] = {
    SYMPTOM_DESCUADRE_DINERO: (
        "Cuando decís que no te cierra la plata, "
        "¿hablás de caja/banco, ventas/cobros, costos/margen, "
        "gastos/retiros o todavía no estás seguro?"
    ),
    SYMPTOM_MARGEN_DUDOSO: (
        "¿Querés revisar si los precios cubren los costos, "
        "si hay productos sin costo o si el margen bajó en un período?"
    ),
    SYMPTOM_DATOS_DUPLICADOS: (
        "¿Los duplicados están en proveedores, clientes, productos u otro listado?"
    ),
    SYMPTOM_STOCK_INCONSISTENTE: (
        "¿La diferencia está entre sistema y depósito, "
        "entre ventas y stock, o en movimientos sin registrar?"
    ),
    SYMPTOM_SOBRECARGA_MANUAL: (
        "¿Qué tarea se repite, con qué frecuencia y en qué archivos o sistemas ocurre?"
    ),
    SYMPTOM_COSTO_INCIERTO: (
        "¿Querés revisar costos por producto, por proveedor, o por período?"
    ),
    SYMPTOM_DOCUMENTACION_DESORDENADA: (
        "¿El desorden está en facturas, comprobantes, remitos, o en todo junto?"
    ),
    SYMPTOM_MAESTRO_DESORDENADO: (
        "¿El listado desordenado es de proveedores, clientes, productos u otro?"
    ),
}


# Dominios por síntoma
_DOMAIN_BY_SYMPTOM: Dict[str, str] = {
    SYMPTOM_DESCUADRE_DINERO: DOMAIN_FINANZAS,
    SYMPTOM_MARGEN_DUDOSO: DOMAIN_COMERCIAL,
    SYMPTOM_DATOS_DUPLICADOS: DOMAIN_PROVEEDORES,
    SYMPTOM_STOCK_INCONSISTENTE: DOMAIN_STOCK,
    SYMPTOM_SOBRECARGA_MANUAL: DOMAIN_AUTOMATIZACION,
    SYMPTOM_COSTO_INCIERTO: DOMAIN_COMERCIAL,
    SYMPTOM_DOCUMENTACION_DESORDENADA: DOMAIN_ADMINISTRACION,
    SYMPTOM_MAESTRO_DESORDENADO: DOMAIN_DATOS_MAESTROS,
}


# Reformulaciones no diagnósticas
_REFORMULATIONS: Dict[str, str] = {
    SYMPTOM_DESCUADRE_DINERO: (
        "Entiendo que la señal principal es que la plata no cierra, "
        "pero todavía no sabemos si viene de caja, margen, cobros o gastos."
    ),
    SYMPTOM_MARGEN_DUDOSO: (
        "Entiendo que hay una duda sobre si lo que vendés cubre los costos "
        "o si el margen es el que esperás."
    ),
    SYMPTOM_DATOS_DUPLICADOS: (
        "Entiendo que hay un problema de entidades repetidas o mal identificadas, "
        "posiblemente alrededor de CUIT o razón social."
    ),
    SYMPTOM_STOCK_INCONSISTENTE: (
        "Entiendo que lo que dice el sistema o las planillas no coincide "
        "con lo que hay realmente en el depósito."
    ),
    SYMPTOM_SOBRECARGA_MANUAL: (
        "Entiendo que hay una tarea manual repetitiva que consume tiempo "
        "y probablemente depende de planillas o sistemas desconectados."
    ),
    SYMPTOM_COSTO_INCIERTO: (
        "Entiendo que no está claro cuánto cuestan realmente ciertos productos o servicios."
    ),
    SYMPTOM_DOCUMENTACION_DESORDENADA: (
        "Entiendo que la documentación operativa está desordenada y eso complica la gestión."
    ),
    SYMPTOM_MAESTRO_DESORDENADO: (
        "Entiendo que el listado maestro de alguna entidad clave está desordenado "
        "o inconsistente."
    ),
}


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _normalize(text: str) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    # No eliminamos tildes para preservar fidelidad del raw_input,
    # pero sí normalizamos espacios y puntuación básica para el matching.
    t = re.sub(r"\s+", " ", t)
    return t


def _detect_signals(normalized_text: str) -> List[str]:
    signals: List[str] = []
    for symptom, patterns in _LEX_PATTERNS.items():
        for pat in patterns:
            if pat in normalized_text:
                signals.append(pat)
    return signals


def _map_symptoms(signals: List[str], normalized_text: str) -> List[str]:
    symptoms: List[str] = []
    for symptom, patterns in _LEX_PATTERNS.items():
        for pat in patterns:
            if pat in signals or pat in normalized_text:
                if symptom not in symptoms:
                    symptoms.append(symptom)
                break
    # Refinamiento específico: proveedores duplicados => añadir MAESTRO_DESORDENADO
    if SYMPTOM_DATOS_DUPLICADOS in symptoms:
        if any(k in normalized_text for k in ("proveed", "cuit", "razon social", "razón social")):
            if SYMPTOM_MAESTRO_DESORDENADO not in symptoms:
                symptoms.append(SYMPTOM_MAESTRO_DESORDENADO)
    return symptoms


def _has_tabular_evidence(selectors: Optional[StructuredSelectors],
                          normalized_text: str) -> bool:
    if selectors and selectors.evidence_available:
        ev = selectors.evidence_available.lower()
        if "excel" in ev or "export" in ev or "sistema" in ev:
            return True
    return any(k in normalized_text for k in ("excel", "planilla", "archivo", "export"))


def _build_business_context(selectors: Optional[StructuredSelectors]) -> Dict[str, Any]:
    if selectors is None:
        return {}
    return selectors.to_dict()


def _resolve_status(symptoms: List[str],
                    has_selectors: bool,
                    has_clear_signal: bool) -> str:
    if not symptoms or symptoms == [SYMPTOM_DESCONOCIDO]:
        if has_selectors:
            return STATUS_NEEDS_DISAMBIGUATION
        return STATUS_NEEDS_ORGANISM_CONTEXT
    if not has_clear_signal:
        return STATUS_NEEDS_DISAMBIGUATION
    # Si hay síntoma claro pero necesita desambiguación (ej. descuadre)
    disambig_symptoms = {SYMPTOM_DESCUADRE_DINERO, SYMPTOM_SOBRECARGA_MANUAL}
    if any(s in disambig_symptoms for s in symptoms):
        return STATUS_NEEDS_DISAMBIGUATION
    return STATUS_NEEDS_EVIDENCE


def _resolve_suggested_classification(symptoms: List[str],
                                    normalized_text: str,
                                    selectors: Optional[StructuredSelectors]) -> Optional[str]:
    # Regla 3: proveedores duplicados -> supplier_duplicate_check
    if SYMPTOM_DATOS_DUPLICADOS in symptoms or SYMPTOM_MAESTRO_DESORDENADO in symptoms:
        if any(k in normalized_text for k in ("proveed", "cuit", "razon social", "razón social")):
            return CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK
    # Reglas 2 y 5: margen/costo/sobrecarga -> excel_diagnostic solo si hay evidencia tabular
    margin_symptoms = {SYMPTOM_MARGEN_DUDOSO, SYMPTOM_COSTO_INCIERTO,
                        SYMPTOM_DESCUADRE_DINERO, SYMPTOM_SOBRECARGA_MANUAL}
    if any(s in margin_symptoms for s in symptoms):
        if _has_tabular_evidence(selectors, normalized_text):
            return CLASSIFICATION_EXCEL_DIAGNOSTIC
    return None


def _build_evidence_needs(symptoms: List[str],
                          normalized_text: str,
                          selectors: Optional[StructuredSelectors]) -> List[EvidenceNeed]:
    needs: List[EvidenceNeed] = []
    if SYMPTOM_DATOS_DUPLICADOS in symptoms or SYMPTOM_MAESTRO_DESORDENADO in symptoms:
        if any(k in normalized_text for k in ("proveed", "cuit", "razon social", "razón social")):
            needs.append(EvidenceNeed(
                evidence_type="excel_proveedores",
                description="Listado de proveedores en Excel o similar.",
                required_fields=["proveedor", "cuit", "razon_social"],
                reason="Para detectar duplicados por CUIT, razón social y variaciones legales.",
            ))
    if SYMPTOM_MARGEN_DUDOSO in symptoms or SYMPTOM_COSTO_INCIERTO in symptoms:
        needs.append(EvidenceNeed(
            evidence_type="excel_ventas_costos",
            description="Listado de ventas y costos por producto o período.",
            required_fields=["producto", "venta_neta", "costo_directo"],
            reason="Para revisar si precios cubren costos y calcular margen real.",
        ))
    if SYMPTOM_DESCUADRE_DINERO in symptoms:
        needs.append(EvidenceNeed(
            evidence_type="excel_caja_banco",
            description="Movimientos de caja, banco o conciliación.",
            required_fields=["fecha", "concepto", "monto"],
            reason="Para identificar origen del descuadre (caja, cobros, gastos).",
        ))
    if SYMPTOM_STOCK_INCONSISTENTE in symptoms:
        needs.append(EvidenceNeed(
            evidence_type="excel_stock",
            description="Listado de stock teórico vs real o movimientos de depósito.",
            required_fields=["producto", "stock_sistema", "stock_real"],
            reason="Para medir diferencias y detectar movimientos sin registrar.",
        ))
    if SYMPTOM_SOBRECARGA_MANUAL in symptoms:
        needs.append(EvidenceNeed(
            evidence_type="descripcion_tarea",
            description="Descripción breve de la tarea repetitiva, frecuencia y archivos involucrados.",
            required_fields=["tarea", "frecuencia", "archivo_o_sistema"],
            reason="Para evaluar si se puede automatizar y con qué herramienta.",
        ))
    return needs


def _build_clarification_questions(symptoms: List[str]) -> List[ClarificationQuestion]:
    questions: List[ClarificationQuestion] = []
    for s in symptoms:
        if s in _CLARIFICATION_QUESTIONS:
            questions.append(ClarificationQuestion(
                question=_CLARIFICATION_QUESTIONS[s],
                target_symptom=s,
                target_domain=_DOMAIN_BY_SYMPTOM.get(s, DOMAIN_DESCONOCIDO),
            ))
    return questions


def _build_reformulation(symptoms: List[str]) -> str:
    if not symptoms or symptoms == [SYMPTOM_DESCONOCIDO]:
        return (
            "Recibí tu mensaje pero todavía no tengo suficiente señal "
            "para encuadrar el tipo de problema. Necesito que me cuentes un poco más."
        )
    # Usar la reformulación del primer síntoma dominante
    primary = symptoms[0]
    return _REFORMULATIONS.get(primary, "Entiendo que hay un problema operativo pero necesito más detalle.")


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def run_interrogation(
    raw_text: str,
    structured_selectors: Optional[StructuredSelectors] = None,
) -> InterrogationResult:
    """
    Ejecuta el slice mínimo determinístico de interrogatorio.

    No diagnostica. No ejecuta análisis. No reemplaza clasificaciones reales.
    """
    if not isinstance(raw_text, str):
        raise TypeError("raw_text debe ser str")

    normalized = _normalize(raw_text)
    has_selectors = (structured_selectors is not None and
                     bool(structured_selectors.to_dict()))

    # Texto vacío o demasiado corto
    if not normalized or len(normalized) < 3:
        return InterrogationResult(
            raw_input=raw_text,
            normalized_terms=[],
            business_context=_build_business_context(structured_selectors),
            reformulation=(
                "No recibí relato suficiente. Contame con tus palabras qué te preocupa."
            ),
            confirmation_question=(
                "¿Podés escribir o mandar por audio qué querés entender de tu negocio?"
            ),
            semantic_signals=[],
            candidate_symptoms=[SYMPTOM_DESCONOCIDO],
            candidate_domains=[DOMAIN_DESCONOCIDO],
            clarification_questions=[],
            evidence_needs=[],
            status=STATUS_BLOCKED_INSUFFICIENT_CONTEXT,
            suggested_classification=None,
        )

    signals = _detect_signals(normalized)
    symptoms = _map_symptoms(signals, normalized)
    if not symptoms:
        symptoms = [SYMPTOM_DESCONOCIDO]

    domains = []
    for s in symptoms:
        d = _DOMAIN_BY_SYMPTOM.get(s, DOMAIN_DESCONOCIDO)
        if d not in domains:
            domains.append(d)
    # Ajuste por datos duplicados + maestro
    if SYMPTOM_MAESTRO_DESORDENADO in symptoms and DOMAIN_DATOS_MAESTROS not in domains:
        domains.append(DOMAIN_DATOS_MAESTROS)

    has_clear_signal = symptoms != [SYMPTOM_DESCONOCIDO] and bool(signals)
    status = _resolve_status(symptoms, has_selectors, has_clear_signal)
    suggested = _resolve_suggested_classification(symptoms, normalized, structured_selectors)
    evidence = _build_evidence_needs(symptoms, normalized, structured_selectors)
    questions = _build_clarification_questions(symptoms)
    reformulation = _build_reformulation(symptoms)

    confirmation = (
        "¿Esta lectura es correcta o querés corregir algo antes de pedir documentos?"
    )

    return InterrogationResult(
        raw_input=raw_text,
        normalized_terms=signals,
        business_context=_build_business_context(structured_selectors),
        reformulation=reformulation,
        confirmation_question=confirmation,
        semantic_signals=signals,
        candidate_symptoms=symptoms,
        candidate_domains=domains,
        clarification_questions=questions,
        evidence_needs=evidence,
        status=status,
        suggested_classification=suggested,
    )


__all__ = [
    "StructuredSelectors",
    "InterrogationResult",
    "EvidenceNeed",
    "ClarificationQuestion",
    "run_interrogation",
    "ALLOWED_STATUSES",
    "ALLOWED_SYMPTOMS",
    "ALLOWED_DOMAINS",
    "STATUS_RAW_CAPTURED",
    "STATUS_NEEDS_ORGANISM_CONTEXT",
    "STATUS_OWNER_CLAIM_REFORMULATED",
    "STATUS_WAITING_OWNER_CONFIRMATION",
    "STATUS_NEEDS_DISAMBIGUATION",
    "STATUS_HYPOTHESIS_OPEN",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_READY_FOR_TAXONOMIC_ROUTING",
    "STATUS_BLOCKED_INSUFFICIENT_CONTEXT",
    "SYMPTOM_DESCUADRE_DINERO",
    "SYMPTOM_MARGEN_DUDOSO",
    "SYMPTOM_DATOS_DUPLICADOS",
    "SYMPTOM_STOCK_INCONSISTENTE",
    "SYMPTOM_SOBRECARGA_MANUAL",
    "SYMPTOM_COSTO_INCIERTO",
    "SYMPTOM_DOCUMENTACION_DESORDENADA",
    "SYMPTOM_MAESTRO_DESORDENADO",
    "SYMPTOM_DESCONOCIDO",
    "DOMAIN_FINANZAS",
    "DOMAIN_COMERCIAL",
    "DOMAIN_PROVEEDORES",
    "DOMAIN_STOCK",
    "DOMAIN_PRODUCCION",
    "DOMAIN_ADMINISTRACION",
    "DOMAIN_AUTOMATIZACION",
    "DOMAIN_DATOS_MAESTROS",
    "DOMAIN_DESCONOCIDO",
]

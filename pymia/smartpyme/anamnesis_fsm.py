"""
Anamnesis FSM offline - Máquina de estados determinística para conversación inicial.

Este módulo guía la ficha PyME inicial y la anamnesis conversacional sin I/O,
sin persistencia, sin Telegram ni ejecución de microservicios. Solo usa contratos
puros de SmartPyme.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    "FICHA_PYME_STEPS",
]


class FSMPhase(str, Enum):
    INIT = "INIT"
    MENU_INICIAL = "MENU_INICIAL"
    CAPTURA_RELATO_CRUDO = "CAPTURA_RELATO_CRUDO"
    FICHA_PYME_INICIAL = "FICHA_PYME_INICIAL"
    ANAMNESIS_TAXONOMIA = "ANAMNESIS_TAXONOMIA"
    HIPOTESIS_FORMULADA = "HIPOTESIS_FORMULADA"
    SOLICITUD_EVIDENCIA = "SOLICITUD_EVIDENCIA"
    BLOQUEADO_EXPLICATIVO = "BLOQUEADO_EXPLICATIVO"


MENU_INICIAL_TEXTO = """Bienvenido a PymIA.

Antes de analizar una consulta necesito armar la ficha básica de tu empresa. Te voy a hacer preguntas cortas, una por vez.

Primera pregunta: ¿cuál es tu nombre y apellido?"""


FICHA_PYME_STEPS: tuple[str, ...] = (
    "ASK_CONTACT_NAME",
    "ASK_CONTACT_ROLE",
    "ASK_CONTACT_PHONE",
    "ASK_CONTACT_EMAIL",
    "ASK_COMPANY_NAME",
    "ASK_ACTIVITY_TYPE",
    "ASK_INDUSTRY_LABEL",
    "ASK_OPERATING_MODEL",
    "ASK_SALES_CHANNELS",
    "ASK_DIGITAL_PRESENCE",
    "ASK_WEBSITE_AND_SOCIALS",
    "ASK_CATALOG_AVAILABLE",
    "ASK_TEAM_SIZE",
    "ASK_CURRENT_TOOLS",
    "ASK_PRIMARY_PAIN",
    "ASK_PERIOD",
    "ASK_AVAILABLE_EVIDENCE",
    "INITIAL_PROFILE_COMPLETE",
)

ACTIVITY_OPTIONS = (
    "1. Vendo productos",
    "2. Fabrico o produzco",
    "3. Presto servicios",
    "4. Compro y revendo",
    "5. Transporte / logística",
    "6. Gastronomía / alimentos",
    "7. Agro / vivero / plantas",
    "8. Otro / mixto",
)
SALES_CHANNEL_OPTIONS = (
    "1. Local físico",
    "2. WhatsApp",
    "3. Instagram / redes",
    "4. Web propia",
    "5. Marketplace",
    "6. Mayorista",
    "7. Distribuidores / vendedores",
    "8. Otro / mixto",
)
DIGITAL_PRESENCE_OPTIONS = (
    "1. Página web",
    "2. Instagram",
    "3. Facebook",
    "4. TikTok",
    "5. LinkedIn",
    "6. Mercado Libre / marketplace",
    "7. Google Maps / Perfil de Empresa",
    "8. WhatsApp Business",
    "9. No tengo presencia online",
)
CATALOG_OPTIONS = (
    "1. Catálogo PDF",
    "2. Lista de precios Excel",
    "3. Catálogo web",
    "4. Fotos o publicaciones en redes",
    "5. Sistema / ERP",
    "6. No tengo catálogo armado",
)
TEAM_SIZE_OPTIONS = (
    "1. Solo yo",
    "2. 2 a 5 personas",
    "3. 6 a 15 personas",
    "4. 16 a 50 personas",
    "5. Más de 50 personas",
)
TOOLS_OPTIONS = (
    "1. Excel / Google Sheets",
    "2. Sistema de gestión / ERP",
    "3. Mercado Pago / bancos",
    "4. WhatsApp / cuaderno / papel",
    "5. Contador / estudio",
    "6. Varios mezclados",
)
PAIN_OPTIONS = (
    "1. No sé si gano plata",
    "2. No me cierra la caja o banco",
    "3. Tengo problemas de stock",
    "4. No sé si mis precios están bien",
    "5. Proveedores me aumentan y no sé el impacto",
    "6. Pierdo mucho tiempo con Excel/manual",
    "7. Quiero ordenar mis archivos",
    "8. Otro problema",
)
PERIOD_OPTIONS = (
    "1. Este mes",
    "2. Mes pasado",
    "3. Últimos 3 meses",
    "4. Temporada / campaña",
    "5. Año completo",
    "6. No sé todavía",
)
EVIDENCE_OPTIONS = (
    "1. Ventas",
    "2. Compras / facturas",
    "3. Lista de precios",
    "4. Costos",
    "5. Stock",
    "6. Caja / banco / Mercado Pago",
    "7. Un Excel mezclado",
    "8. No sé qué tengo",
)


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
    profile_step: str | None = None
    profile_data: dict[str, Any] = field(default_factory=dict)

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
            "profile_step": self.profile_step,
            "profile_data": self.profile_data,
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


def _default_profile(raw_first_message: str) -> dict[str, Any]:
    return {
        "raw_first_message": raw_first_message,
        "profile_status": "IN_PROGRESS",
        "contact": {"full_name": None, "role": None, "phone": None, "email": None},
        "company": {"legal_or_trade_name": None},
        "business_taxonomy": {"activity_type": None, "industry_label": None},
        "business_model": {"operating_model": None, "sales_channels": []},
        "digital_presence": {
            "presence_channels": [],
            "website_url": None,
            "social_links": [],
            "marketplace_links": [],
        },
        "commercial_catalog": {"has_catalog": None, "catalog_type": None, "catalog_links_or_files": []},
        "company_profile": {"team_size_range": None},
        "current_tools": {"primary_information_system": None},
        "initial_problem": {"primary_pain": None},
        "analysis_scope": {"period": None},
        "evidence": {"available": []},
    }


def _with_profile_value(profile: dict[str, Any], path: tuple[str, ...], value: Any) -> dict[str, Any]:
    updated: dict[str, Any] = {**profile}
    cursor: dict[str, Any] = updated
    for key in path[:-1]:
        current = cursor.get(key)
        if not isinstance(current, dict):
            current = {}
        current = {**current}
        cursor[key] = current
        cursor = current
    cursor[path[-1]] = value
    return updated


def _append_profile_values(profile: dict[str, Any], path: tuple[str, ...], values: list[str]) -> dict[str, Any]:
    current: Any = profile
    for key in path:
        if not isinstance(current, dict):
            current = []
            break
        current = current.get(key)
    existing = current if isinstance(current, list) else []
    merged = list(existing)
    for value in values:
        if value and value not in merged:
            merged.append(value)
    return _with_profile_value(profile, path, merged)


def _options_text(options: tuple[str, ...]) -> str:
    return "\n".join(options)


def _first_profile_message() -> str:
    return MENU_INICIAL_TEXTO


def _next_prompt(step: str) -> str:
    prompts = {
        "ASK_CONTACT_ROLE": "¿Cuál es tu rol en la empresa? Por ejemplo: dueño, socio, gerente, administración o ventas.",
        "ASK_CONTACT_PHONE": "¿Cuál es tu teléfono o WhatsApp de contacto?",
        "ASK_CONTACT_EMAIL": "¿Cuál es tu email de contacto? Si no usás email, respondé 'no tengo'.",
        "ASK_COMPANY_NAME": "¿Cómo se llama tu empresa o marca comercial?",
        "ASK_ACTIVITY_TYPE": "¿Qué describe mejor a tu empresa?\n" + _options_text(ACTIVITY_OPTIONS),
        "ASK_INDUSTRY_LABEL": "¿En qué rubro trabajás concretamente? Por ejemplo: ropa, calzado, ferretería, repuestos, alimentos, textil, transporte, vivero, consultoría, salud, educación u otro.",
        "ASK_OPERATING_MODEL": "¿Cómo funciona principalmente tu operación? Contame si vendés de stock, fabricás a pedido, prestás servicios por turno/proyecto, comprás y revendés, o si es mixto.",
        "ASK_SALES_CHANNELS": "¿Por dónde vendés hoy? Podés elegir una o varias opciones.\n" + _options_text(SALES_CHANNEL_OPTIONS),
        "ASK_DIGITAL_PRESENCE": "¿Qué presencia online tiene hoy tu empresa? Podés elegir una o varias opciones.\n" + _options_text(DIGITAL_PRESENCE_OPTIONS),
        "ASK_WEBSITE_AND_SOCIALS": "Pasame los links disponibles: página web, Instagram, Facebook, TikTok, LinkedIn, Mercado Libre, Google Maps u otros. Si no tenés, respondé 'no tengo'.",
        "ASK_CATALOG_AVAILABLE": "¿Tenés catálogo, lista de precios o productos para compartir?\n" + _options_text(CATALOG_OPTIONS),
        "ASK_TEAM_SIZE": "Para ubicar escala: ¿cuántas personas trabajan en la empresa contando dueños, empleados y colaboradores?\n" + _options_text(TEAM_SIZE_OPTIONS),
        "ASK_CURRENT_TOOLS": "¿Dónde llevás hoy la información principal del negocio?\n" + _options_text(TOOLS_OPTIONS),
        "ASK_PRIMARY_PAIN": "¿Qué querés entender o resolver primero?\n" + _options_text(PAIN_OPTIONS),
        "ASK_PERIOD": "¿Qué período querés mirar primero?\n" + _options_text(PERIOD_OPTIONS),
        "ASK_AVAILABLE_EVIDENCE": "¿Qué información tenés disponible para empezar? Podés elegir una o varias opciones.\n" + _options_text(EVIDENCE_OPTIONS),
        "INITIAL_PROFILE_COMPLETE": "Perfecto. Ya tengo la ficha inicial de tu empresa. Ahora puedo decirte qué evidencia necesitamos para avanzar y qué análisis corresponde hacer primero.",
    }
    return prompts[step]


def _norm(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _has(text: str, *needles: str) -> bool:
    t = _norm(text)
    return any(n in t for n in needles)


def _map_activity_type(text: str) -> str:
    t = _norm(text)
    if t.startswith("1") or _has(t, "vendo productos", "comercio"):
        return "commerce_products"
    if t.startswith("2") or _has(t, "fabrico", "produzco", "produccion", "producción"):
        return "manufacturing"
    if t.startswith("3") or _has(t, "servicio"):
        return "services"
    if t.startswith("4") or _has(t, "revendo", "compro y revendo", "distrib"):
        return "resale_distribution"
    if t.startswith("5") or _has(t, "transporte", "logistica", "logística"):
        return "transport_logistics"
    if t.startswith("6") or _has(t, "gastronomia", "gastronomía", "alimentos", "comida"):
        return "food_gastronomy"
    if t.startswith("7") or _has(t, "agro", "vivero", "plantas"):
        return "agro_plants"
    return "other_mixed"


def _map_multi_options(text: str, mapping: dict[str, tuple[str, ...]]) -> list[str]:
    t = _norm(text)
    values: list[str] = []
    for value, hints in mapping.items():
        if any(hint in t.split() or hint in t for hint in hints):
            values.append(value)
    return values or [text.strip()]


def _map_sales_channels(text: str) -> list[str]:
    return _map_multi_options(text, {
        "physical_store": ("1", "local", "fisico", "físico"),
        "whatsapp": ("2", "whatsapp"),
        "social_media": ("3", "instagram", "redes", "facebook", "tiktok"),
        "own_website": ("4", "web", "pagina", "página"),
        "marketplace": ("5", "marketplace", "mercado libre"),
        "wholesale": ("6", "mayorista", "mayor"),
        "distributors": ("7", "distribuidores", "vendedores", "viajantes"),
        "other_mixed": ("8", "otro", "mixto"),
    })


def _map_digital_presence(text: str) -> list[str]:
    return _map_multi_options(text, {
        "website": ("1", "web", "pagina", "página"),
        "instagram": ("2", "instagram"),
        "facebook": ("3", "facebook"),
        "tiktok": ("4", "tiktok"),
        "linkedin": ("5", "linkedin"),
        "marketplace": ("6", "mercado libre", "marketplace"),
        "google_business": ("7", "google", "maps"),
        "whatsapp_business": ("8", "whatsapp"),
        "none": ("9", "no tengo", "ninguna"),
    })


def _map_catalog(text: str) -> tuple[bool, str]:
    t = _norm(text)
    if t.startswith("6") or "no tengo" in t:
        return False, "none"
    if t.startswith("1") or "pdf" in t:
        return True, "pdf_catalog"
    if t.startswith("2") or "excel" in t or "lista" in t:
        return True, "excel_price_list"
    if t.startswith("3") or "web" in t:
        return True, "web_catalog"
    if t.startswith("4") or "fotos" in t or "redes" in t:
        return True, "social_posts"
    if t.startswith("5") or "erp" in t or "sistema" in t:
        return True, "erp_catalog"
    return True, text.strip()


def _map_team_size(text: str) -> str:
    t = _norm(text)
    if t.startswith("1") or "solo" in t:
        return "solo_owner"
    if t.startswith("2") or "2" in t or "5" in t:
        return "team_2_5"
    if t.startswith("3") or "6" in t or "15" in t:
        return "team_6_15"
    if t.startswith("4") or "16" in t or "50" in t:
        return "team_16_50"
    return "team_50_plus"


def _map_tools(text: str) -> str:
    t = _norm(text)
    if t.startswith("1") or "excel" in t or "sheets" in t:
        return "spreadsheet"
    if t.startswith("2") or "erp" in t or "sistema" in t:
        return "erp"
    if t.startswith("3") or "mercado pago" in t or "banco" in t:
        return "payments_banks"
    if t.startswith("4") or "whatsapp" in t or "papel" in t or "cuaderno" in t:
        return "manual_informal"
    if t.startswith("5") or "contador" in t:
        return "accountant"
    return "mixed_tools"


def _map_primary_pain(text: str) -> str:
    t = _norm(text)
    if t.startswith("1") or "gano plata" in t or "rentabilidad" in t:
        return "profitability_uncertainty"
    if t.startswith("2") or "caja" in t or "banco" in t:
        return "cash_bank_mismatch"
    if t.startswith("3") or "stock" in t:
        return "stock_uncertainty"
    if t.startswith("4") or "precios" in t:
        return "pricing_uncertainty"
    if t.startswith("5") or "proveedores" in t:
        return "supplier_cost_pressure"
    if t.startswith("6") or "excel" in t or "manual" in t:
        return "manual_process_overload"
    if t.startswith("7") or "archivos" in t:
        return "file_disorder"
    return "other_problem"


def _map_period(text: str) -> str:
    t = _norm(text)
    if t.startswith("1") or "este mes" in t:
        return "current_month"
    if t.startswith("2") or "mes pasado" in t:
        return "last_month"
    if t.startswith("3") or "3 meses" in t or "tres meses" in t:
        return "last_3_months"
    if t.startswith("4") or "temporada" in t or "campaña" in t:
        return "season"
    if t.startswith("5") or "año" in t or "anio" in t:
        return "full_year"
    return "unknown_period"


def _map_evidence(text: str) -> list[str]:
    return _map_multi_options(text, {
        "sales_records": ("1", "ventas"),
        "purchase_invoices": ("2", "compras", "facturas"),
        "price_list": ("3", "lista", "precios"),
        "cost_records": ("4", "costos"),
        "stock_records": ("5", "stock"),
        "cash_bank_records": ("6", "caja", "banco", "mercado pago"),
        "mixed_excel": ("7", "excel", "mezclado"),
        "unknown_evidence": ("8", "no se", "no sé"),
    })


def _advance_profile(previous_state: AnamnesisFSMState | None, text: str) -> tuple[dict[str, Any], str]:
    if previous_state is None or not previous_state.profile_data:
        return _default_profile(text), "ASK_CONTACT_NAME"
    step = previous_state.profile_step or "ASK_CONTACT_NAME"
    profile = dict(previous_state.profile_data)
    next_step_by_step = {
        "ASK_CONTACT_NAME": "ASK_CONTACT_ROLE",
        "ASK_CONTACT_ROLE": "ASK_CONTACT_PHONE",
        "ASK_CONTACT_PHONE": "ASK_CONTACT_EMAIL",
        "ASK_CONTACT_EMAIL": "ASK_COMPANY_NAME",
        "ASK_COMPANY_NAME": "ASK_ACTIVITY_TYPE",
        "ASK_ACTIVITY_TYPE": "ASK_INDUSTRY_LABEL",
        "ASK_INDUSTRY_LABEL": "ASK_OPERATING_MODEL",
        "ASK_OPERATING_MODEL": "ASK_SALES_CHANNELS",
        "ASK_SALES_CHANNELS": "ASK_DIGITAL_PRESENCE",
        "ASK_DIGITAL_PRESENCE": "ASK_WEBSITE_AND_SOCIALS",
        "ASK_WEBSITE_AND_SOCIALS": "ASK_CATALOG_AVAILABLE",
        "ASK_CATALOG_AVAILABLE": "ASK_TEAM_SIZE",
        "ASK_TEAM_SIZE": "ASK_CURRENT_TOOLS",
        "ASK_CURRENT_TOOLS": "ASK_PRIMARY_PAIN",
        "ASK_PRIMARY_PAIN": "ASK_PERIOD",
        "ASK_PERIOD": "ASK_AVAILABLE_EVIDENCE",
        "ASK_AVAILABLE_EVIDENCE": "INITIAL_PROFILE_COMPLETE",
    }
    if step == "ASK_CONTACT_NAME":
        profile = _with_profile_value(profile, ("contact", "full_name"), text)
    elif step == "ASK_CONTACT_ROLE":
        profile = _with_profile_value(profile, ("contact", "role"), text)
    elif step == "ASK_CONTACT_PHONE":
        profile = _with_profile_value(profile, ("contact", "phone"), text)
    elif step == "ASK_CONTACT_EMAIL":
        profile = _with_profile_value(profile, ("contact", "email"), text)
    elif step == "ASK_COMPANY_NAME":
        profile = _with_profile_value(profile, ("company", "legal_or_trade_name"), text)
    elif step == "ASK_ACTIVITY_TYPE":
        profile = _with_profile_value(profile, ("business_taxonomy", "activity_type"), _map_activity_type(text))
    elif step == "ASK_INDUSTRY_LABEL":
        profile = _with_profile_value(profile, ("business_taxonomy", "industry_label"), text)
    elif step == "ASK_OPERATING_MODEL":
        profile = _with_profile_value(profile, ("business_model", "operating_model"), text)
    elif step == "ASK_SALES_CHANNELS":
        profile = _append_profile_values(profile, ("business_model", "sales_channels"), _map_sales_channels(text))
    elif step == "ASK_DIGITAL_PRESENCE":
        profile = _append_profile_values(profile, ("digital_presence", "presence_channels"), _map_digital_presence(text))
    elif step == "ASK_WEBSITE_AND_SOCIALS":
        profile = _append_profile_values(profile, ("digital_presence", "social_links"), [text])
        if "http" in text or "." in text:
            profile = _with_profile_value(profile, ("digital_presence", "website_url"), text)
    elif step == "ASK_CATALOG_AVAILABLE":
        has_catalog, catalog_type = _map_catalog(text)
        profile = _with_profile_value(profile, ("commercial_catalog", "has_catalog"), has_catalog)
        profile = _with_profile_value(profile, ("commercial_catalog", "catalog_type"), catalog_type)
    elif step == "ASK_TEAM_SIZE":
        profile = _with_profile_value(profile, ("company_profile", "team_size_range"), _map_team_size(text))
    elif step == "ASK_CURRENT_TOOLS":
        profile = _with_profile_value(profile, ("current_tools", "primary_information_system"), _map_tools(text))
    elif step == "ASK_PRIMARY_PAIN":
        profile = _with_profile_value(profile, ("initial_problem", "primary_pain"), _map_primary_pain(text))
    elif step == "ASK_PERIOD":
        profile = _with_profile_value(profile, ("analysis_scope", "period"), _map_period(text))
    elif step == "ASK_AVAILABLE_EVIDENCE":
        profile = _append_profile_values(profile, ("evidence", "available"), _map_evidence(text))
        profile = _with_profile_value(profile, ("profile_status",), "COMPLETE")
    return profile, next_step_by_step.get(step, "INITIAL_PROFILE_COMPLETE")


def _profile_state(tenant_id: str, text: str, now: str, previous_state: AnamnesisFSMState | None) -> tuple[AnamnesisFSMState, str]:
    profile, next_step = _advance_profile(previous_state, text)
    message = _first_profile_message() if previous_state is None or not previous_state.profile_data else _next_prompt(next_step)
    return (
        AnamnesisFSMState(
            phase=FSMPhase.FICHA_PYME_INICIAL,
            tenant_id=tenant_id,
            user_text=text,
            contract=_base_contract(tenant_id),
            created_at=previous_state.created_at if previous_state else now,
            updated_at=now,
            profile_step=next_step,
            profile_data=profile,
            taxonomy=previous_state.taxonomy if previous_state else None,
        ),
        message,
    )


def _detect_organism_type(text: str) -> TaxonomyType | None:
    t = text.lower()
    if any(k in t for k in ["ropa", "tela", "coso", "corto", "talles", "textil"]):
        return TaxonomyType.textil
    if any(k in t for k in ["fabrico", "produzco", "elaboro", "manufactura", "hago muebles"]):
        return TaxonomyType.produccion_fabrica
    if any(k in t for k in ["revendo", "compro y vendo", "local", "tienda", "comercio"]):
        return TaxonomyType.comercio
    if any(k in t for k in ["servicio", "consultoría", "asesoro"]):
        return TaxonomyType.servicios
    if any(k in t for k in ["logística", "transporte", "envíos", "distribuyo", "distribuidora"]):
        return TaxonomyType.distribucion
    if any(k in t for k in ["restaurante", "bar", "comida", "gastronom", "alimentos"]):
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


def _profile_is_complete(state: AnamnesisFSMState | None) -> bool:
    return bool(state and state.profile_step == "INITIAL_PROFILE_COMPLETE")


def process_message(user_text: str, tenant_id: str, previous_state: AnamnesisFSMState | None = None) -> tuple[AnamnesisFSMState, str]:
    if not tenant_id or not isinstance(tenant_id, str):
        raise ValueError("tenant_id obligatorio")
    text = user_text.strip() if user_text else ""
    now = _now_iso()

    if previous_state is None or (previous_state.phase == FSMPhase.FICHA_PYME_INICIAL and not _profile_is_complete(previous_state)):
        return _profile_state(tenant_id, text, now, previous_state)

    previous_taxonomy = previous_state.taxonomy if previous_state else None
    taxonomy = _taxonomy_from_text(text, tenant_id, previous_taxonomy)
    symptoms = _detect_symptoms(text)
    readiness = _readiness_for(tenant_id, taxonomy, symptoms)

    previous_hypotheses = list(previous_state.hypotheses) if previous_state else []
    new_hypotheses: list[OperationalHypothesis] = []
    if readiness.status == ReadinessStatus.READY:
        known_domains = {h.domain for h in previous_hypotheses}
        for symptom in symptoms:
            if symptom not in known_domains:
                new_hypotheses.append(_hypothesis_for(tenant_id, symptom))

    hypotheses = tuple(previous_hypotheses + new_hypotheses)
    evidence_requests: list[EvidenceRequirement] = list(previous_state.evidence_requests) if previous_state else []
    for hypothesis in new_hypotheses:
        evidence_requests.extend(_evidence_for(tenant_id, hypothesis))

    if taxonomy is None:
        phase = FSMPhase.ANAMNESIS_TAXONOMIA
        message = _next_prompt("ASK_ACTIVITY_TYPE")
    elif readiness.status != ReadinessStatus.READY:
        phase = FSMPhase.ANAMNESIS_TAXONOMIA
        missing = ", ".join(readiness.missing_taxonomy_fields) or "contexto operativo"
        message = f"Todavía falta completar la ficha operativa: {missing}. Sigamos con la próxima pregunta de contexto."
    elif evidence_requests:
        phase = FSMPhase.SOLICITUD_EVIDENCIA
        message = "Para avanzar sin adivinar necesito evidencia concreta: " + "; ".join(e.telegram_message for e in evidence_requests[:2])
    elif hypotheses:
        phase = FSMPhase.HIPOTESIS_FORMULADA
        message = "Ya tengo hipótesis abiertas, pero siguen sin diagnóstico hasta contrastar evidencia."
    else:
        phase = FSMPhase.BLOQUEADO_EXPLICATIVO
        message = "Con lo que me diste todavía no puedo armar un caso. Necesito más contexto operativo."

    return (
        AnamnesisFSMState(
            phase=phase,
            tenant_id=tenant_id,
            user_text=text,
            taxonomy=taxonomy,
            contract=_base_contract(tenant_id),
            hypotheses=hypotheses,
            evidence_requests=tuple(evidence_requests),
            readiness=readiness,
            blocking_reasons=tuple(readiness.blocking_reasons),
            created_at=previous_state.created_at if previous_state else now,
            updated_at=now,
            profile_step=previous_state.profile_step if previous_state else None,
            profile_data=previous_state.profile_data if previous_state else {},
        ),
        message,
    )

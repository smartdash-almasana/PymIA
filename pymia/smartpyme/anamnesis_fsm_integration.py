"""
Integración offline del FSM de anamnesis con sesión/progressive_context.

Este módulo provee un wrapper puro y determinístico que:
- Recibe tenant_id, session_id, message_text y previous_progressive_context
- Reconstruye AnamnesisFSMState desde progressive_context si existe
- Llama a process_message() del FSM offline
- Devuelve reply_text + updated_progressive_context serializable

NO usa Telegram, NO usa red, NO usa I/O, NO ejecuta microservicios,
NO lee Excel, NO diagnostica.

Este wrapper es consumible por conversa-engine/main.py o por cualquier
capa superior (Hermes real, bot, CLI) sin acoplamiento directo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.anamnesis_fsm import (
    FSMPhase,
    AnamnesisFSMState,
    process_message,
)
from pymia.smartpyme.anamnesis_readiness import (
    AnamnesisReadiness,
    ReadinessStatus,
)
from pymia.smartpyme.conversation_contract import (
    ConversationContract,
    ConversationPhase,
    create_conversation_contract,
)
from pymia.smartpyme.evidence_requirement import EvidenceRequirement
from pymia.smartpyme.intake import (
    create_intake_record,
)
from pymia.smartpyme.interrogation import StructuredSelectors
from pymia.smartpyme.operational_hypothesis import OperationalHypothesis
from pymia.smartpyme.post_ficha_evidence_gate import (
    apply_post_ficha_evidence_turn,
    is_post_ficha_evidence_input,
    merge_previous_post_ficha_evidence_context,
)
from pymia.smartpyme.taxonomy import BusinessTaxonomySnapshot

__all__ = [
    "AnamnesisTurnInput",
    "AnamnesisTurnOutput",
    "build_structured_selectors_from_profile_data",
    "run_anamnesis_turn",
]


@dataclass(frozen=True)
class AnamnesisTurnInput:
    """
    Entrada de un turno de anamnesis.

    Campos
    ------
    tenant_id:
        Identificador del tenant. Obligatorio.

    session_id:
        Identificador de sesión (puede ser user_id, chat_id, etc.).
        Obligatorio para trazabilidad.

    message_text:
        Texto del usuario. Puede ser vacío (→ menú inicial).

    previous_progressive_context:
        Contexto previo serializado (dict). None si es sesión nueva.
        Debe contener al menos "fsm_state" con el snapshot anterior.
    """

    tenant_id: str
    session_id: str
    message_text: str
    previous_progressive_context: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Fail-closed input validation for integration boundary.

        Does NOT execute runtime logic; only validates basic contract shape.
        """
        if self.tenant_id is None or not isinstance(self.tenant_id, str):
            raise ValueError("tenant_id obligatorio")
        if self.session_id is None or not isinstance(self.session_id, str):
            raise ValueError("session_id obligatorio")


@dataclass(frozen=True)
class AnamnesisTurnOutput:
    """
    Salida de un turno de anamnesis.

    Campos
    ------
    reply_text:
        Mensaje para el usuario en castellano de negocio.

    updated_progressive_context:
        Contexto serializable para el próximo turno.
        Contiene fsm_state, taxonomy, contract, hypotheses, evidence_requests.

    phase:
        Fase actual del FSM (para logging/debug).

    has_hypotheses:
        True si hay hipótesis ABIERTAS.

    has_evidence_requests:
        True si hay evidencia solicitada.

    readiness_status:
        Status de AnamnesisReadiness (READY, NEEDS_MORE_INFO, BLOCKED).
    """

    reply_text: str
    updated_progressive_context: dict[str, Any]
    phase: str
    has_hypotheses: bool
    has_evidence_requests: bool
    readiness_status: str | None = None


def build_structured_selectors_from_profile_data(profile_data: dict[str, Any]) -> StructuredSelectors:
    """Traduce profile_data de Ficha PyME a StructuredSelectors de forma pura y determinística."""
    profile = profile_data if isinstance(profile_data, dict) else {}
    business_taxonomy = profile.get("business_taxonomy") if isinstance(profile.get("business_taxonomy"), dict) else {}
    current_tools = profile.get("current_tools") if isinstance(profile.get("current_tools"), dict) else {}
    company_profile = profile.get("company_profile") if isinstance(profile.get("company_profile"), dict) else {}
    business_model = profile.get("business_model") if isinstance(profile.get("business_model"), dict) else {}
    digital_presence = profile.get("digital_presence") if isinstance(profile.get("digital_presence"), dict) else {}
    evidence = profile.get("evidence") if isinstance(profile.get("evidence"), dict) else {}

    activity_type = str(business_taxonomy.get("activity_type") or "").strip()
    primary_information_system = str(current_tools.get("primary_information_system") or "").strip()
    team_size_range = str(company_profile.get("team_size_range") or "").strip()

    raw_sales_channels = business_model.get("sales_channels")
    sales_channels = [str(x).strip().lower() for x in raw_sales_channels if str(x).strip()] if isinstance(raw_sales_channels, list) else []

    raw_presence_channels = digital_presence.get("presence_channels")
    presence_channels = [str(x).strip().lower() for x in raw_presence_channels if str(x).strip()] if isinstance(raw_presence_channels, list) else []

    raw_available = evidence.get("available")
    available_evidence = [str(x).strip().lower() for x in raw_available if str(x).strip()] if isinstance(raw_available, list) else []

    operation_type_map = {
        "manufacturing": "Produzco",
        "commerce_products": "Revendo",
        "resale_distribution": "Distribuyo",
        "services": "Servicios",
        "transport_logistics": "Servicios",
        "food_gastronomy": "Produzco",
        "agro_plants": "Produzco",
        "other_mixed": "Mixto",
    }
    operation_type = operation_type_map.get(activity_type, "Mixto")

    tools_map = {
        "spreadsheet": "Excel",
        "erp": "Sistema",
        "manual_informal": "Cuaderno",
        "payments_banks": "Varios",
        "accountant": "Varios",
        "mixed_tools": "Varios",
    }
    tools_used = tools_map.get(primary_information_system)

    employee_map = {
        "solo_owner": "1",
        "team_2_5": "2 a 5",
        "team_6_15": "6 a 15",
        "team_16_50": "16 a 50",
        "team_50_plus": "Más de 50",
    }
    employee_range = employee_map.get(team_size_range)

    sales_channel = None
    if len(sales_channels) > 1:
        sales_channel = "Mixto"
    elif sales_channels:
        channel = sales_channels[0]
        if "wholesale" in channel:
            sales_channel = "Mayorista"
        elif "physical_store" in channel:
            sales_channel = "Local"
        elif "marketplace" in channel:
            sales_channel = "Marketplace"
        elif "ecommerce" in channel or "web" in channel or "own_website" in channel:
            sales_channel = "Ecommerce"
        elif channel in {"social", "social_media", "instagram", "whatsapp"} or "instagram" in channel:
            sales_channel = "Instagram / WhatsApp"

    marketplace_presence = None
    marketplace_tokens = {"marketplace", "mercado_libre", "mercado libre"}
    marketplace_found = any(
        any(token in value for token in marketplace_tokens)
        for value in sales_channels + presence_channels
    )
    has_any_market_data = bool(sales_channels or presence_channels)
    if marketplace_found:
        marketplace_presence = "Sí"
    elif has_any_market_data:
        marketplace_presence = "No"

    has_excel = any(
        token in available_evidence
        for token in ("sales_records", "cost_records", "price_list", "mixed_excel", "spreadsheet")
    )
    has_pdf = any(token in available_evidence for token in ("purchase_invoices", "pdf", "invoices"))
    has_captures = any(token in available_evidence for token in ("screenshots", "images"))
    has_no_idea = any(token in available_evidence for token in ("no_idea", "unknown"))

    evidence_available = None
    if has_excel:
        evidence_available = "Excel"
    elif has_pdf:
        evidence_available = "PDF"
    elif has_captures:
        evidence_available = "Capturas"
    elif has_no_idea:
        evidence_available = "NoSe"

    stock_mode = None
    if activity_type in {
        "commerce_products",
        "resale_distribution",
        "manufacturing",
        "food_gastronomy",
        "agro_plants",
    }:
        stock_mode = "Informal"
    elif activity_type in {"services", "transport_logistics"}:
        stock_mode = "No"

    return StructuredSelectors(
        sales_channel=sales_channel,
        operation_type=operation_type,
        stock_mode=stock_mode,
        tools_used=tools_used,
        evidence_available=evidence_available,
        employee_range=employee_range,
        marketplace_presence=marketplace_presence,
    )


def _reconstruct_state_from_context(
    tenant_id: str,
    context: dict[str, Any],
) -> AnamnesisFSMState | None:
    """
    Reconstruye AnamnesisFSMState desde progressive_context serializado.

    Si el contexto está corrupto o incompleto, devuelve None (fail-closed).
    Cada sub-objeto se reconstruye de forma independiente: si uno falla,
    queda None/vacío sin bloquear los demás.
    """
    if not context or not isinstance(context, dict):
        return None

    fsm_state_dict = context.get("fsm_state")
    if not fsm_state_dict or not isinstance(fsm_state_dict, dict):
        return None

    try:
        phase_str = fsm_state_dict.get("phase", "INIT")
        phase = FSMPhase(phase_str) if phase_str in [p.value for p in FSMPhase] else FSMPhase.INIT

        # --- Reconstruir taxonomy ---
        taxonomy = _reconstruct_taxonomy(tenant_id, fsm_state_dict.get("taxonomy"))

        # --- Reconstruir contract ---
        contract = _reconstruct_contract(fsm_state_dict.get("contract"))

        # --- Reconstruir hypotheses ---
        hypotheses = _reconstruct_hypotheses(fsm_state_dict.get("hypotheses", []))

        # --- Reconstruir evidence_requests ---
        evidence_requests = _reconstruct_evidence_requests(fsm_state_dict.get("evidence_requests", []))

        # --- Reconstruir readiness ---
        readiness = _reconstruct_readiness(fsm_state_dict.get("readiness"))

        # Reconstruir blocking_reasons
        blocking_reasons = tuple(fsm_state_dict.get("blocking_reasons", []))

        return AnamnesisFSMState(
            phase=phase,
            tenant_id=tenant_id,
            user_text=fsm_state_dict.get("user_text", ""),
            taxonomy=taxonomy,
            contract=contract,
            hypotheses=hypotheses,
            evidence_requests=evidence_requests,
            readiness=readiness,
            blocking_reasons=blocking_reasons,
            created_at=fsm_state_dict.get("created_at", ""),
            updated_at=fsm_state_dict.get("updated_at", ""),
            profile_step=fsm_state_dict.get("profile_step"),
            profile_data=fsm_state_dict.get("profile_data", {}),
        )
    except Exception:
        # Fail-closed: contexto corrupto → None (sesión nueva)
        return None


def _reconstruct_taxonomy(
    tenant_id: str, taxonomy_dict: dict[str, Any] | None
) -> BusinessTaxonomySnapshot | None:
    """Reconstruct BusinessTaxonomySnapshot from dict. None on failure."""
    if not taxonomy_dict or not isinstance(taxonomy_dict, dict):
        return None
    try:
        from pymia.smartpyme.taxonomy import TaxonomyType, create_taxonomy_snapshot

        organism_raw = taxonomy_dict.get("organism_type", "")
        organism = TaxonomyType(organism_raw)
        return create_taxonomy_snapshot(
            tenant_id=tenant_id,
            organism_type=organism,
            industry=taxonomy_dict.get("industry", ""),
            size=taxonomy_dict.get("size", "pendiente_confirmacion"),
            complexity=taxonomy_dict.get("complexity", "simple"),
            sales_channels=taxonomy_dict.get("sales_channels", []),
            operational_flow_stages=taxonomy_dict.get("operational_flow_stages", []),
            areas_present=taxonomy_dict.get("areas_present", []),
            systems_available=taxonomy_dict.get("systems_available", []),
            jurisdiction=taxonomy_dict.get("jurisdiction", "AR"),
            currency=taxonomy_dict.get("currency", "ARS"),
            confidence=float(taxonomy_dict.get("confidence", 0.0)),
        )
    except Exception:
        return None


def _reconstruct_contract(
    contract_dict: dict[str, Any] | None,
) -> ConversationContract | None:
    """Reconstruct ConversationContract from dict. None on failure."""
    if not contract_dict or not isinstance(contract_dict, dict):
        return None
    try:
        return create_conversation_contract(
            contract_id=contract_dict.get("contract_id", ""),
            tenant_id=contract_dict.get("tenant_id", ""),
            anamnesis_ref=contract_dict.get("anamnesis_ref", ""),
            taxonomy_ref=contract_dict.get("taxonomy_ref", ""),
            current_phase=contract_dict.get("current_phase", "ANAMNESIS"),
            allowed_actions=contract_dict.get("allowed_actions", []),
            forbidden_actions=contract_dict.get("forbidden_actions", []),
        )
    except Exception:
        return None


def _reconstruct_hypotheses(
    hypotheses_dicts: list[dict[str, Any]],
) -> tuple[OperationalHypothesis, ...]:
    """Reconstruct tuple of OperationalHypothesis from list of dicts."""
    if not hypotheses_dicts or not isinstance(hypotheses_dicts, list):
        return ()
    result: list[OperationalHypothesis] = []
    for h_dict in hypotheses_dicts:
        if not isinstance(h_dict, dict):
            continue
        try:
            from pymia.smartpyme.operational_hypothesis import HypothesisStatus as HS

            status_raw = h_dict.get("status", "ABIERTA")
            try:
                status = HS(status_raw)
            except ValueError:
                status = HS.ABIERTA

            hyp = OperationalHypothesis(
                hypothesis_id=h_dict.get("hypothesis_id", ""),
                tenant_id=h_dict.get("tenant_id", ""),
                intake_id=h_dict.get("intake_id", ""),
                formulation=h_dict.get("formulation", ""),
                source=h_dict.get("source", ""),
                domain=h_dict.get("domain", ""),
                related_symptoms=list(h_dict.get("related_symptoms", [])),
                required_evidence=list(h_dict.get("required_evidence", [])),
                status=status,
                findings_refs=list(h_dict.get("findings_refs", [])),
                created_at=h_dict.get("created_at", ""),
                closed_at=h_dict.get("closed_at"),
            )
            result.append(hyp)
        except Exception:
            continue  # Skip corrupted hypothesis, keep rest
    return tuple(result)


def _reconstruct_evidence_requests(
    evidence_dicts: list[dict[str, Any]],
) -> tuple[EvidenceRequirement, ...]:
    """Reconstruct tuple of EvidenceRequirement from list of dicts."""
    if not evidence_dicts or not isinstance(evidence_dicts, list):
        return ()
    result: list[EvidenceRequirement] = []
    for e_dict in evidence_dicts:
        if not isinstance(e_dict, dict):
            continue
        try:
            er = EvidenceRequirement(
                requirement_id=e_dict.get("requirement_id", ""),
                tenant_id=e_dict.get("tenant_id", ""),
                intake_id=e_dict.get("intake_id", ""),
                hypothesis_id=e_dict.get("hypothesis_id", ""),
                evidence_type=e_dict.get("evidence_type", ""),
                description=e_dict.get("description", ""),
                required_fields=list(e_dict.get("required_fields", [])),
                reason=e_dict.get("reason", ""),
                blocks_analysis=bool(e_dict.get("blocks_analysis", True)),
                priority=int(e_dict.get("priority", 1)),
                telegram_message=e_dict.get("telegram_message", ""),
                enables_classification=e_dict.get("enables_classification"),
                source_tank=e_dict.get("source_tank"),
                created_at=e_dict.get("created_at", ""),
            )
            result.append(er)
        except Exception:
            continue  # Skip corrupted requirement, keep rest
    return tuple(result)


def _reconstruct_readiness(
    readiness_dict: dict[str, Any] | None,
) -> AnamnesisReadiness | None:
    """Reconstruct AnamnesisReadiness from dict. None on failure."""
    if not readiness_dict or not isinstance(readiness_dict, dict):
        return None
    try:
        status_raw = readiness_dict.get("status", "NEEDS_MORE_INFO")
        try:
            status = ReadinessStatus(status_raw)
        except ValueError:
            status = ReadinessStatus.NEEDS_MORE_INFO

        return AnamnesisReadiness(
            tenant_id=readiness_dict.get("tenant_id", ""),
            anamnesis_id=readiness_dict.get("anamnesis_id", ""),
            status=status,
            taxonomy_complete=bool(readiness_dict.get("taxonomy_complete", False)),
            narrative_sufficient=bool(readiness_dict.get("narrative_sufficient", False)),
            blocking_reasons=list(readiness_dict.get("blocking_reasons", [])),
            missing_taxonomy_fields=list(readiness_dict.get("missing_taxonomy_fields", [])),
            open_hypotheses_count=int(readiness_dict.get("open_hypotheses_count", 0)),
            pending_evidence_count=int(readiness_dict.get("pending_evidence_count", 0)),
        )
    except Exception:
        return None


def _serialize_state_to_context(state: AnamnesisFSMState) -> dict[str, Any]:
    """
    Serializa AnamnesisFSMState a dict para progressive_context.
    """
    return {
        "fsm_state": state.to_dict(),
        "tenant_id": state.tenant_id,
        "phase": state.phase.value if isinstance(state.phase, FSMPhase) else state.phase,
        "has_taxonomy": state.taxonomy is not None,
        "has_hypotheses": len(state.hypotheses) > 0,
        "has_evidence_requests": len(state.evidence_requests) > 0,
        "readiness_status": (
            state.readiness.status.value
            if state.readiness and hasattr(state.readiness.status, "value")
            else None
        ),
    }


def _is_initial_profile_complete(state: AnamnesisFSMState) -> bool:
    if state.profile_step != "INITIAL_PROFILE_COMPLETE":
        return False
    profile_data = state.profile_data if isinstance(state.profile_data, dict) else {}
    profile_status = profile_data.get("profile_status")
    if profile_status is None:
        return True
    return profile_status == "COMPLETE"


def _get_existing_post_ficha_routing(context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(context, dict):
        return None
    projection = context.get("post_ficha_routing")
    if not isinstance(projection, dict):
        return None
    intake_id = projection.get("intake_id")
    if isinstance(intake_id, str) and intake_id.strip():
        return projection
    return None


def _build_post_ficha_routing_projection(
    *,
    tenant_id: str,
    profile_data: dict[str, Any],
    raw_first_message: str,
) -> dict[str, Any]:
    selectors = build_structured_selectors_from_profile_data(profile_data)
    intake_record = create_intake_record(
        tenant_id=tenant_id,
        raw_text=raw_first_message,
        structured_selectors=selectors,
    )
    return {
        "intake_id": intake_record.intake_id,
        "intake_state": intake_record.intake_state,
        "suggested_next_state": intake_record.suggested_next_state,
        "candidate_symptoms": intake_record.interrogation_result.get("candidate_symptoms", []),
        "evidence_requests": [
            {
                "request_id": req.request_id,
                "evidence_type": req.evidence_type,
                "description": req.description,
                "reason": req.reason,
                "status": req.status,
            }
            for req in intake_record.evidence_requests
        ],
    }


def _build_post_ficha_reply(post_ficha_routing: dict[str, Any]) -> str:
    evidence_requests = post_ficha_routing.get("evidence_requests")
    if isinstance(evidence_requests, list) and evidence_requests:
        descriptions: list[str] = []
        for item in evidence_requests[:2]:
            if not isinstance(item, dict):
                continue
            description = str(item.get("description") or "").strip()
            if description:
                descriptions.append(description)
        if descriptions:
            lines = [
                "Ya tengo la ficha inicial.",
                "Para avanzar sin adivinar necesito esta evidencia mínima:",
            ]
            for idx, description in enumerate(descriptions, start=1):
                lines.append(f"{idx}. {description}")
            return "\n".join(lines)
    return (
        "Ya tengo la ficha inicial.\n"
        "Antes de pedir documentos necesito aclarar el frente operativo que querés ordenar primero."
    )


def run_anamnesis_turn(input_data: AnamnesisTurnInput) -> AnamnesisTurnOutput:
    """
    Ejecuta un turno de anamnesis usando el FSM offline.

    Args:
        input_data: AnamnesisTurnInput con tenant_id, session_id, message_text,
                    y opcionalmente previous_progressive_context.

    Returns:
        AnamnesisTurnOutput con reply_text, updated_progressive_context,
        y metadata del estado actual.

    Raises:
        ValueError: Si tenant_id o session_id están vacíos.
    """
    if (
        not isinstance(input_data.tenant_id, str)
        or not input_data.tenant_id.strip()
    ):
        raise ValueError("tenant_id obligatorio")
    if (
        not isinstance(input_data.session_id, str)
        or not input_data.session_id.strip()
    ):
        raise ValueError("session_id obligatorio")

    # Reconstruir estado previo desde progressive_context
    previous_state = None
    if input_data.previous_progressive_context:
        previous_state = _reconstruct_state_from_context(
            tenant_id=input_data.tenant_id,
            context=input_data.previous_progressive_context,
        )

    # Llamar al FSM offline
    try:
        new_state, reply_text = process_message(
            user_text=input_data.message_text,
            tenant_id=input_data.tenant_id,
            previous_state=previous_state,
        )
    except Exception as e:
        # Fail-closed: error en FSM → menú inicial
        new_state, reply_text = process_message(
            user_text="",
            tenant_id=input_data.tenant_id,
            previous_state=None,
        )

    # Serializar nuevo estado a progressive_context
    updated_context = _serialize_state_to_context(new_state)
    existing_post_ficha_routing = _get_existing_post_ficha_routing(input_data.previous_progressive_context)
    if existing_post_ficha_routing is not None:
        updated_context["post_ficha_routing"] = existing_post_ficha_routing
    updated_context = merge_previous_post_ficha_evidence_context(
        previous_context=input_data.previous_progressive_context,
        updated_context=updated_context,
    )

    handled_evidence_input = False
    if is_post_ficha_evidence_input(input_data.message_text):
        try:
            updated_context, reply_text = apply_post_ficha_evidence_turn(
                tenant_id=input_data.tenant_id,
                message_text=input_data.message_text,
                previous_context=input_data.previous_progressive_context,
                updated_context=updated_context,
            )
            handled_evidence_input = True
        except ValueError as exc:
            reply_text = str(exc)
            if not reply_text:
                reply_text = (
                    "No pude registrar la evidencia. "
                    "Usá: EVIDENCE::<source_kind>::<evidence_type>::<source_ref>."
                )
            handled_evidence_input = True

    if _is_initial_profile_complete(new_state) and not handled_evidence_input:
        post_ficha_routing = updated_context.get("post_ficha_routing")
        if not (isinstance(post_ficha_routing, dict) and str(post_ficha_routing.get("intake_id") or "").strip()):
            profile_data = new_state.profile_data if isinstance(new_state.profile_data, dict) else {}
            raw_first_message = str(profile_data.get("raw_first_message") or "").strip()
            if not raw_first_message:
                raw_first_message = str(input_data.message_text or "").strip()
            post_ficha_routing = _build_post_ficha_routing_projection(
                tenant_id=input_data.tenant_id,
                profile_data=profile_data,
                raw_first_message=raw_first_message,
            )
            updated_context["post_ficha_routing"] = post_ficha_routing
        reply_text = _build_post_ficha_reply(post_ficha_routing)

    # Extraer metadata para output
    phase_str = new_state.phase.value if isinstance(new_state.phase, FSMPhase) else new_state.phase
    has_hypotheses = len(new_state.hypotheses) > 0
    has_evidence_requests = len(new_state.evidence_requests) > 0
    readiness_status = None
    if new_state.readiness and hasattr(new_state.readiness.status, "value"):
        readiness_status = new_state.readiness.status.value

    return AnamnesisTurnOutput(
        reply_text=reply_text,
        updated_progressive_context=updated_context,
        phase=phase_str,
        has_hypotheses=has_hypotheses,
        has_evidence_requests=has_evidence_requests,
        readiness_status=readiness_status,
    )

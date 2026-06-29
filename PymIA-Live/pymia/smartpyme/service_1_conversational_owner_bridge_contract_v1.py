from __future__ import annotations

import hashlib
import unicodedata
from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
BRIDGE_KIND: Final[str] = "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"

ALLOWED_OWNER_INTENTS: Final[tuple[str, ...]] = (
    "OWNER_ASKS_STATUS",
    "OWNER_ASKS_EXPLANATION",
    "OWNER_PROVIDES_CLARIFICATION",
    "OWNER_PROVIDES_CORRECTION",
    "OWNER_REQUESTS_RERUN",
    "OWNER_ASKS_NEXT_STEP",
    "OWNER_ASKS_DELIVERY_SUMMARY",
    "OWNER_PROVIDES_UNSUPPORTED_MESSAGE",
    "UNKNOWN",
)

ALLOWED_RESPONSE_SCOPE: Final[tuple[str, ...]] = (
    "explain_existing_state",
    "summarize_existing_delivery_candidate",
    "ask_for_missing_evidence",
    "capture_owner_clarification",
    "capture_owner_correction",
    "explain_next_safe_step",
)

FORBIDDEN_RESPONSE_SCOPE: Final[tuple[str, ...]] = (
    "invent_case_truth",
    "diagnose_without_evidence",
    "promise_final_delivery",
    "authorize_runtime",
    "execute_tools",
    "trigger_pipeline",
    "mutate_case",
    "publish_outputs",
    "provide_legal_tax_accounting_certainty",
    "act_as_human_operator",
)

NEXT_ACTION_BY_INTENT: Final[dict[str, str]] = {
    "OWNER_ASKS_STATUS": "PREPARE_STATUS_EXPLANATION_CANDIDATE",
    "OWNER_ASKS_EXPLANATION": "PREPARE_STATE_EXPLANATION_CANDIDATE",
    "OWNER_PROVIDES_CLARIFICATION": "PREPARE_OWNER_CLARIFICATION_CAPTURE_CANDIDATE",
    "OWNER_PROVIDES_CORRECTION": "PREPARE_OWNER_CORRECTION_CAPTURE_CANDIDATE",
    "OWNER_REQUESTS_RERUN": "PREPARE_RERUN_REQUEST_CANDIDATE",
    "OWNER_ASKS_NEXT_STEP": "PREPARE_NEXT_STEP_EXPLANATION_CANDIDATE",
    "OWNER_ASKS_DELIVERY_SUMMARY": "PREPARE_DELIVERY_SUMMARY_CANDIDATE",
    "OWNER_PROVIDES_UNSUPPORTED_MESSAGE": "BLOCK_UNSUPPORTED_MESSAGE",
    "UNKNOWN": "BLOCK_UNSUPPORTED_MESSAGE",
}

ConversationalOwnerBridgeStatusV1 = Literal[
    "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_MISSING_OWNER_MESSAGE",
    "BLOCKED_UNSUPPORTED_INTENT",
    "BLOCKED_MISSING_STATE_REFS",
    "BLOCKED_UNSAFE_SESSION_FLAGS",
    "UNKNOWN",
]

ConversationalOwnerIntentV1 = Literal[
    "OWNER_ASKS_STATUS",
    "OWNER_ASKS_EXPLANATION",
    "OWNER_PROVIDES_CLARIFICATION",
    "OWNER_PROVIDES_CORRECTION",
    "OWNER_REQUESTS_RERUN",
    "OWNER_ASKS_NEXT_STEP",
    "OWNER_ASKS_DELIVERY_SUMMARY",
    "OWNER_PROVIDES_UNSUPPORTED_MESSAGE",
    "UNKNOWN",
]


class Service1ConversationalOwnerBridgeContractInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    owner_message: str
    owner_intent: str | None
    service_1_state_refs: dict[str, str]
    generated_folder_refs: dict[str, str]
    owner_delivery_packet_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    notes: list[str]


class Service1ConversationalOwnerBridgeCandidateV1(TypedDict):
    bridge_kind: Literal["CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    owner_message_ref_candidate: str
    normalized_owner_message: str
    owner_intent: ConversationalOwnerIntentV1
    service_1_state_refs: dict[str, str]
    generated_folder_refs: dict[str, str]
    owner_delivery_packet_ref: str | None
    saas_job_orchestration_ref: str | None
    next_conversational_action: str
    safe_context_refs_for_future_llm: dict[str, str]
    allowed_response_scope: list[str]
    forbidden_response_scope: list[str]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    prompt_runtime_authorized: Literal[False]
    chatbot_authorized: Literal[False]
    tool_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1ConversationalOwnerBridgeContractResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: ConversationalOwnerBridgeStatusV1
    conversational_owner_bridge_candidate: Service1ConversationalOwnerBridgeCandidateV1 | None
    blocked_reason: str | None
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    prompt_runtime_authorized: Literal[False]
    chatbot_authorized: Literal[False]
    tool_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_conversational_owner_bridge_contract_v1(
    bridge_input: Service1ConversationalOwnerBridgeContractInputV1,
) -> Service1ConversationalOwnerBridgeContractResultV1:
    """Build a pure owner-conversation bridge candidate for Servicio 1.

    This adapter only validates session safety, normalizes the owner message,
    classifies a conservative intent, preserves safe refs, and proposes the next
    conversational action. It does not call LLMs, prompts, chatbots, APIs,
    tools, pipelines, runners, delivery, storage, or mutation layers.
    """
    session = bridge_input.get("saas_case_session_candidate")
    if session is None:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=_notes(bridge_input.get("notes"), "Conversational owner bridge requires a SaaS case session candidate."),
        )
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason="saas_case_session_candidate_invalid",
            notes=_notes(bridge_input.get("notes"), "Conversational owner bridge requires a valid SaaS case session candidate."),
        )

    session_validation = _validate_session(session)
    if session_validation is not None:
        status, reason = session_validation
        return _result(
            status=status,
            blocked_reason=reason,
            notes=_notes(bridge_input.get("notes"), "SaaS case session candidate is invalid or unsafe for conversational bridging."),
        )

    normalized_owner_message = _normalize_owner_message(bridge_input.get("owner_message"))
    if normalized_owner_message is None:
        return _result(
            status="BLOCKED_MISSING_OWNER_MESSAGE",
            blocked_reason="owner_message_required",
            notes=_notes(bridge_input.get("notes"), "Conversational owner bridge requires a non-empty owner_message."),
        )

    service_1_state_refs = _clean_refs_map(bridge_input.get("service_1_state_refs"))
    if not service_1_state_refs:
        return _result(
            status="BLOCKED_MISSING_STATE_REFS",
            blocked_reason="service_1_state_refs_required",
            notes=_notes(bridge_input.get("notes"), "Conversational owner bridge requires service_1_state_refs."),
        )

    owner_intent_value = bridge_input.get("owner_intent")
    if owner_intent_value is not None:
        explicit_intent = _normalize_explicit_intent(owner_intent_value)
        if explicit_intent is None:
            return _result(
                status="BLOCKED_UNSUPPORTED_INTENT",
                blocked_reason="owner_intent_not_supported",
                notes=_notes(bridge_input.get("notes"), "Explicit owner_intent is not supported by this contract."),
            )
        owner_intent: ConversationalOwnerIntentV1 = explicit_intent
    else:
        owner_intent = _classify_owner_intent(normalized_owner_message)

    owner_ref = str(session["owner_ref"]).strip()
    case_ref = str(session["case_ref"]).strip()
    source_session_ref = _source_session_ref(session)
    generated_folder_refs = _clean_refs_map(bridge_input.get("generated_folder_refs"))
    owner_message_ref_candidate = _owner_message_ref_candidate(
        owner_ref=owner_ref,
        case_ref=case_ref,
        normalized_owner_message=normalized_owner_message,
    )
    owner_delivery_packet_ref = _optional_candidate_ref(
        bridge_input.get("owner_delivery_packet_candidate"),
        preferred_keys=("owner_delivery_packet_ref", "packet_ref", "source_pipeline_run_ref", "case_ref", "case_id"),
        fallback_prefix="owner_delivery_packet",
    )
    saas_job_orchestration_ref = _optional_candidate_ref(
        bridge_input.get("saas_job_orchestration_candidate"),
        preferred_keys=("saas_job_orchestration_ref", "job_ref", "source_session_ref", "case_ref"),
        fallback_prefix="saas_job_orchestration",
    )

    candidate: Service1ConversationalOwnerBridgeCandidateV1 = {
        "bridge_kind": BRIDGE_KIND,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "owner_message_ref_candidate": owner_message_ref_candidate,
        "normalized_owner_message": normalized_owner_message,
        "owner_intent": owner_intent,
        "service_1_state_refs": dict(service_1_state_refs),
        "generated_folder_refs": dict(generated_folder_refs),
        "owner_delivery_packet_ref": owner_delivery_packet_ref,
        "saas_job_orchestration_ref": saas_job_orchestration_ref,
        "next_conversational_action": NEXT_ACTION_BY_INTENT[owner_intent],
        "safe_context_refs_for_future_llm": _safe_context_refs_for_future_llm(
            source_session_ref=source_session_ref,
            owner_message_ref_candidate=owner_message_ref_candidate,
            service_1_state_refs=service_1_state_refs,
            generated_folder_refs=generated_folder_refs,
            owner_delivery_packet_ref=owner_delivery_packet_ref,
            saas_job_orchestration_ref=saas_job_orchestration_ref,
        ),
        "allowed_response_scope": list(ALLOWED_RESPONSE_SCOPE),
        "forbidden_response_scope": list(FORBIDDEN_RESPONSE_SCOPE),
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "prompt_runtime_authorized": False,
        "chatbot_authorized": False,
        "tool_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }

    return _result(
        status="CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY",
        conversational_owner_bridge_candidate=candidate,
        notes=_notes(bridge_input.get("notes"), "Conversational owner bridge candidate created without LLM, runtime, mutation, or execution authorization."),
    )


def _validate_session(
    session: dict[str, object],
) -> tuple[Literal["BLOCKED_INVALID_SESSION", "BLOCKED_UNSAFE_SESSION_FLAGS"], str] | None:
    if session.get("session_kind") != SESSION_KIND:
        return ("BLOCKED_INVALID_SESSION", "session_kind_must_be_saas_case_session_candidate")
    if session.get("service_name") != SERVICE_NAME:
        return ("BLOCKED_INVALID_SESSION", "session_service_name_must_be_service_1")
    if _clean_required_ref(session.get("owner_ref")) is None:
        return ("BLOCKED_INVALID_SESSION", "session_owner_ref_required")
    if _clean_required_ref(session.get("case_ref")) is None:
        return ("BLOCKED_INVALID_SESSION", "session_case_ref_required")
    if session.get("api_exposed") is not False:
        return ("BLOCKED_UNSAFE_SESSION_FLAGS", "session_api_exposed_must_be_false")
    if session.get("runtime_authorized") is not False:
        return ("BLOCKED_UNSAFE_SESSION_FLAGS", "session_runtime_authorized_must_be_false")
    if session.get("job_authorized") is not False:
        return ("BLOCKED_UNSAFE_SESSION_FLAGS", "session_job_authorized_must_be_false")
    if session.get("file_upload_authorized") is not False:
        return ("BLOCKED_UNSAFE_SESSION_FLAGS", "session_file_upload_authorized_must_be_false")
    return None


def _normalize_owner_message(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    return normalized


def _normalize_explicit_intent(value: object) -> ConversationalOwnerIntentV1 | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    if normalized not in ALLOWED_OWNER_INTENTS:
        return None
    return normalized  # type: ignore[return-value]


def _classify_owner_intent(normalized_owner_message: str) -> ConversationalOwnerIntentV1:
    matching_text = _matching_text(normalized_owner_message)

    if _contains_any(
        matching_text,
        ("auditoria legal", "certificacion", "impuestos finales", "servicio 2"),
    ):
        return "OWNER_PROVIDES_UNSUPPORTED_MESSAGE"
    if _contains_any(matching_text, ("esta mal", "corregi", "no es asi")):
        return "OWNER_PROVIDES_CORRECTION"
    if _contains_any(matching_text, ("aclaro", "falto", "agrego", "sumo")):
        return "OWNER_PROVIDES_CLARIFICATION"
    if _contains_any(
        matching_text,
        ("corre de nuevo", "reprocesa", "recalcula", "volve a correr"),
    ):
        return "OWNER_REQUESTS_RERUN"
    if _contains_any(matching_text, ("siguiente paso", "que hago ahora", "proximo")):
        return "OWNER_ASKS_NEXT_STEP"
    if _contains_any(matching_text, ("que me entregaste", "resumen", "entrega", "informe")):
        return "OWNER_ASKS_DELIVERY_SUMMARY"
    if _contains_any(matching_text, ("no entiendo", "explicame", "que significa", "por que")):
        return "OWNER_ASKS_EXPLANATION"
    if _contains_any(matching_text, ("estado", "que paso", "como va", "termino")):
        return "OWNER_ASKS_STATUS"
    return "UNKNOWN"


def _matching_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_marks.lower()


def _contains_any(value: str, candidates: tuple[str, ...]) -> bool:
    return any(candidate in value for candidate in candidates)


def _source_session_ref(session: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_case_session:unknown"


def _owner_message_ref_candidate(
    *,
    owner_ref: str,
    case_ref: str,
    normalized_owner_message: str,
) -> str:
    message_hash = hashlib.sha1(normalized_owner_message.encode("utf-8")).hexdigest()[:12]
    return f"owner_message_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:{message_hash}"


def _optional_candidate_ref(
    value: object,
    *,
    preferred_keys: tuple[str, ...],
    fallback_prefix: str,
) -> str | None:
    if not isinstance(value, dict) or not value:
        return None
    for key in preferred_keys:
        ref_value = value.get(key)
        if isinstance(ref_value, str) and ref_value.strip():
            if key.endswith("_ref") or key.endswith("_id"):
                return ref_value.strip()
            return f"{fallback_prefix}:{_safe_ref(ref_value)}"
    kind = _clean_required_ref(value.get("packet_kind")) or _clean_required_ref(value.get("job_kind"))
    if kind is not None:
        return f"{fallback_prefix}:{_safe_ref(kind)}"
    return fallback_prefix + ":unknown"


def _safe_context_refs_for_future_llm(
    *,
    source_session_ref: str,
    owner_message_ref_candidate: str,
    service_1_state_refs: dict[str, str],
    generated_folder_refs: dict[str, str],
    owner_delivery_packet_ref: str | None,
    saas_job_orchestration_ref: str | None,
) -> dict[str, str]:
    safe_refs: dict[str, str] = {
        "source_session_ref": source_session_ref,
        "owner_message_ref_candidate": owner_message_ref_candidate,
    }
    for key, value in service_1_state_refs.items():
        safe_refs[f"service_1_state_ref:{key}"] = value
    for key, value in generated_folder_refs.items():
        safe_refs[f"generated_folder_ref:{key}"] = value
    if owner_delivery_packet_ref is not None:
        safe_refs["owner_delivery_packet_ref"] = owner_delivery_packet_ref
    if saas_job_orchestration_ref is not None:
        safe_refs["saas_job_orchestration_ref"] = saas_job_orchestration_ref
    return safe_refs


def _safe_ref(value: str) -> str:
    return " ".join(value.strip().split()).replace(" ", "_")


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _clean_refs_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    clean: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(item, str) or not item.strip():
            continue
        clean[key] = item
    return clean


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: ConversationalOwnerBridgeStatusV1,
    conversational_owner_bridge_candidate: Service1ConversationalOwnerBridgeCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1ConversationalOwnerBridgeContractResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "conversational_owner_bridge_candidate": conversational_owner_bridge_candidate,
        "blocked_reason": blocked_reason,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "prompt_runtime_authorized": False,
        "chatbot_authorized": False,
        "tool_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "BRIDGE_KIND",
    "SESSION_KIND",
    "ALLOWED_OWNER_INTENTS",
    "ALLOWED_RESPONSE_SCOPE",
    "FORBIDDEN_RESPONSE_SCOPE",
    "NEXT_ACTION_BY_INTENT",
    "Service1ConversationalOwnerBridgeContractInputV1",
    "Service1ConversationalOwnerBridgeCandidateV1",
    "Service1ConversationalOwnerBridgeContractResultV1",
    "build_service_1_conversational_owner_bridge_contract_v1",
]

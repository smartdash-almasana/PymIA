"""Upload-first semantic reception wiring for Servicio 1.

This module narrows the existing assisted web application to the reception layer:
Excel is parsed by the existing canonical intake, semantic interpretation is
performed through the injected bounded provider, and owner corroboration is
presented one question at a time.

It does not create a second XLSX parser and does not modify the productive
Servicio 1 calculation root.
"""
from __future__ import annotations

from http import HTTPStatus
from pathlib import Path
from typing import Any, Mapping, Sequence

import pymia.smartpyme.service_1_assisted_web_v1 as base
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    semantic_provider_from_environment_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_OWNER_DIALOGUE_REQUIRED,
    revise_service_1_assisted_semantic_decision_v1,
    run_service_1_assisted_semantic_initial_v1,
)


class Service1SemanticReceptionWebApplicationV1(base.AssistedWebApplicationV1):
    """Existing web application with bounded LLM semantics and sequential HITL."""

    @staticmethod
    def _normalize_dialogue_decision(question: Mapping[str, Any]) -> dict[str, Any]:
        normalized = dict(question)
        if not normalized.get("column_refs") and not normalized.get("relationship_refs"):
            column_ref = str(normalized.get("column_ref") or "").strip()
            if column_ref:
                normalized["column_refs"] = [column_ref]
        if not str(normalized.get("presentation_text") or "").strip():
            proposed = str(normalized.get("proposed_meaning") or "").strip()
            if not proposed:
                proposed = str(normalized.get("proposed_label") or "").strip()
            column_name = str(normalized.get("column_name") or "").strip()
            if proposed:
                subject = column_name or str(normalized.get("column_ref") or "").strip() or "este dato"
                normalized["presentation_text"] = (
                    f"PymIA interpreta que {subject} se refiere a {proposed}. ¿Es correcto?"
                )
        return normalized

    def _decorate_dialogue_decision(
        self,
        *,
        session_id: str,
        question: Mapping[str, Any],
    ) -> dict[str, Any]:
        state = self.session(session_id)
        normalized = self._normalize_dialogue_decision(question)
        assistance = state.semantic_assistance_state if isinstance(state.semantic_assistance_state, Mapping) else {}
        dialogue = assistance.get("dialogue_plan") if isinstance(assistance.get("dialogue_plan"), Mapping) else {}
        decisions = [item for item in (dialogue.get("decisions") or []) if isinstance(item, Mapping)]
        total = len(decisions) or len(state.semantic_questions) or 1
        completed = min(len(state.semantic_dialogue_responses), total)
        normalized["progress_total"] = total
        normalized["progress_completed"] = completed
        normalized["progress_current"] = min(completed + 1, total)

        refs = [str(ref).strip() for ref in (normalized.get("column_refs") or []) if str(ref).strip()]
        profile = assistance.get("workbook_profile") if isinstance(assistance.get("workbook_profile"), Mapping) else {}
        profile_columns = [item for item in (profile.get("columns") or []) if isinstance(item, Mapping)]
        matched = next(
            (item for item in profile_columns if str(item.get("column_ref") or "").strip() in refs),
            None,
        )
        if isinstance(matched, Mapping):
            normalized["sheet_name"] = str(matched.get("sheet_name") or "").strip()
            normalized["column_name"] = str(matched.get("column_name") or "").strip()
            normalized["sample_values"] = list(matched.get("sample_values") or [])[:5]
            normalized["inferred_type"] = str(matched.get("inferred_type") or "").strip()

        validated = assistance.get("validated_packet") if isinstance(assistance.get("validated_packet"), Mapping) else {}
        proposal_refs = {str(ref).strip() for ref in (normalized.get("proposal_refs") or []) if str(ref).strip()}
        semantic_decision = next(
            (
                item
                for item in (validated.get("decisions") or [])
                if isinstance(item, Mapping)
                and str(item.get("decision_id") or "").strip() in proposal_refs
            ),
            None,
        )
        if isinstance(semantic_decision, Mapping):
            normalized["proposed_semantic_role"] = semantic_decision.get("semantic_role")
            normalized["proposed_variable_name"] = semantic_decision.get("variable_name")
            normalized["assistant_rationale"] = semantic_decision.get("rationale") or semantic_decision.get("reason")

        decision_id = str(normalized.get("decision_id") or "").strip()
        normalized["chat_messages"] = [dict(item) for item in state.semantic_chat_messages.get(decision_id, [])]
        normalized["chat_suggestion"] = dict(state.semantic_chat_suggestions.get(decision_id, {}))
        return normalized

    def _render_one_pending_question(
        self,
        *,
        session_id: str,
        message: str | None = None,
    ) -> tuple[int, str] | None:
        state = self.session(session_id)
        if not state.semantic_questions:
            return None
        question = state.semantic_questions[0]
        visible_questions = [dict(question)] if isinstance(question, Mapping) else []
        if isinstance(question, Mapping) and question.get("question_kind") == "UNIT_MEANING":
            return (
                HTTPStatus.OK,
                base._derived_unit_questions_page(
                    visible_questions,
                    message,
                    ingestion_output=state.ingestion_output or {},
                ),
            )
        if state.semantic_assistance_state is not None and isinstance(question, Mapping):
            return (
                HTTPStatus.OK,
                base._assisted_semantic_dialogue_page(
                    [self._decorate_dialogue_decision(session_id=session_id, question=question)],
                    message,
                ),
            )
        return (
            HTTPStatus.OK,
            base._semantic_questions_page(
                visible_questions,
                message,
            ),
        )

    def receive_xlsx(
        self,
        *,
        session_id: str,
        filename: str,
        content: bytes,
        selected_launch_review: str | None = None,
    ) -> tuple[int, str]:
        status, page = super().receive_xlsx(
            session_id=session_id,
            filename=filename,
            content=content,
            selected_launch_review=selected_launch_review,
        )
        state = self.session(session_id)

        if selected_launch_review is None and state.ingestion_output:
            # Upload-first journey: do not turn the owner into a column parser before
            # an analysis is chosen. Semantic interpretation starts when an analysis
            # establishes which meanings are material.
            state.semantic_questions = []
            state.semantic_answers = {}
            state.semantic_scope_answers = {}
            state.semantic_assistance_state = None
            state.semantic_dialogue_responses = {}
            state.semantic_chat_messages = {}
            state.semantic_chat_suggestions = {}
            return HTTPStatus.OK, base._analysis_menu_page(state)

        sequential = self._render_one_pending_question(session_id=session_id)
        return sequential if sequential is not None else (status, page)

    def run_review(
        self,
        *,
        session_id: str,
        requested_capability: str,
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if requested_capability not in base._REVIEW_BY_REF and requested_capability != "working_capital":
            return super().run_review(
                session_id=session_id,
                requested_capability=requested_capability,
            )
        if not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "Primero subí un archivo de Excel."
            )

        state.selected_launch_review = requested_capability
        state.semantic_dialogue_responses = {}
        state.semantic_chat_messages = {}
        state.semantic_chat_suggestions = {}
        semantic_scope = (
            base._WORKING_CAPITAL_COMPONENT_CAPABILITIES
            if requested_capability == "working_capital"
            else ()
        )
        assistance_state = run_service_1_assisted_semantic_initial_v1(
            ingestion_output=state.ingestion_output,
            requested_capability=requested_capability,
            provider=self._semantic_provider,
            compatible_tenant_memory_hints=self._compatible_tenant_memory_hints(state),
            semantic_scope_capabilities=semantic_scope,
            atomic_confirmation=True,
        )
        state.last_review_result = assistance_state

        if assistance_state.get("status") == STATUS_OWNER_DIALOGUE_REQUIRED:
            state.semantic_assistance_state = assistance_state
            state.semantic_questions = list(assistance_state.get("owner_questions") or [])
            sequential = self._render_one_pending_question(session_id=session_id)
            if sequential is not None:
                return sequential
            return HTTPStatus.OK, base._blocked_message_page(
                "La interpretación necesita confirmación pero no produjo una pregunta válida."
            )

        state.semantic_questions = []
        state.semantic_assistance_state = None
        return HTTPStatus.OK, base._blocked_message_page(
            str(assistance_state.get("detail") or assistance_state.get("blocked_reason") or "La comprensión semántica no pudo iniciarse de forma segura.")
        )

    @staticmethod
    def _allowed_role_variable_pairs(assistance: Mapping[str, Any]) -> list[dict[str, str]]:
        context = assistance.get("context")
        hypotheses = getattr(context, "deterministic_hypotheses", ())
        pairs: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for raw in hypotheses:
            if not isinstance(raw, Mapping):
                continue
            candidates: list[Mapping[str, Any]] = [raw]
            candidates.extend(
                item
                for item in (raw.get("candidate_meanings") or [])
                if isinstance(item, Mapping)
            )
            for item in candidates:
                role = str(
                    item.get("semantic_role")
                    or item.get("primary_semantic_role")
                    or ""
                ).strip()
                variable = str(
                    item.get("variable_name")
                    or item.get("primary_variable_name")
                    or ""
                ).strip()
                pair = (role, variable)
                if role and variable and pair not in seen:
                    seen.add(pair)
                    pairs.append({"semantic_role": role, "variable_name": variable})
        return pairs

    def confirm_meanings(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if state.semantic_assistance_state is not None and state.semantic_questions:
            current = state.semantic_questions[0]
            if isinstance(current, Mapping):
                decision_id = str(current.get("decision_id") or "").strip()
                action = str(fields.get(f"action_{decision_id}") or "").strip().upper()
                is_atomic_column = (
                    len([ref for ref in (current.get("column_refs") or []) if str(ref).strip()]) == 1
                    and not [ref for ref in (current.get("relationship_refs") or []) if str(ref).strip()]
                )
                if is_atomic_column and action in {"REJECT", "CORRECT"}:
                    correction = str(fields.get(f"correction_{decision_id}") or "").strip()
                    if not correction:
                        return self._render_one_pending_question(
                            session_id=session_id,
                            message="Contame con tus palabras qué significa esta columna para poder proponerte una corrección.",
                        ) or (HTTPStatus.BAD_REQUEST, base._error_page("Falta la corrección."))
                    return self.semantic_assist(
                        session_id=session_id,
                        fields={
                            "decision_id": decision_id,
                            "assistant_message": correction,
                            "correction_mode": "1",
                        },
                    )
            # The page exposes exactly one semantic transaction. Restrict the base
            # coordinator to that visible decision; accumulated prior responses live
            # in semantic_dialogue_responses and are replayed by the base reentry.
            state.semantic_questions = [state.semantic_questions[0]]
        status, page = super().confirm_meanings(
            session_id=session_id,
            fields=fields,
        )
        sequential = self._render_one_pending_question(session_id=session_id)
        return sequential if sequential is not None else (status, page)

    def semantic_assist(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        """Answer a bounded owner question about the currently visible column.

        This helper never confirms, persists, calculates or changes semantic truth.
        It only explains the current proposal and may suggest language for a later
        owner correction.
        """
        state = self.session(session_id)
        if not isinstance(state.semantic_assistance_state, Mapping) or not state.semantic_questions:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "No hay una columna pendiente para consultar."
            )
        current = state.semantic_questions[0]
        if not isinstance(current, Mapping):
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "La columna pendiente no tiene un estado semántico válido."
            )
        decision_id = str(current.get("decision_id") or "").strip()
        requested_id = str(fields.get("decision_id") or "").strip()
        if not decision_id or requested_id != decision_id:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "La consulta no corresponde a la columna actualmente visible."
            )
        owner_message = str(fields.get("assistant_message") or "").strip()
        if not owner_message:
            return self._render_one_pending_question(
                session_id=session_id,
                message="Escribí qué querés aclarar sobre esta columna.",
            ) or (HTTPStatus.BAD_REQUEST, base._error_page("Falta la consulta."))

        decorated = self._decorate_dialogue_decision(session_id=session_id, question=current)
        allowed_pairs = self._allowed_role_variable_pairs(state.semantic_assistance_state)
        bounded_context = {
            "decision_id": decision_id,
            "column_refs": list(decorated.get("column_refs") or []),
            "sheet_name": decorated.get("sheet_name"),
            "column_name": decorated.get("column_name"),
            "inferred_type": decorated.get("inferred_type"),
            "sample_values": list(decorated.get("sample_values") or [])[:5],
            "proposed_semantic_role": decorated.get("proposed_semantic_role"),
            "proposed_variable_name": decorated.get("proposed_variable_name"),
            "proposal_text": decorated.get("presentation_text"),
            "rationale": decorated.get("assistant_rationale") or decorated.get("materiality_reason"),
            "owner_message": owner_message,
            "allowed_role_variable_pairs": allowed_pairs,
            "confirmed_so_far": [
                {
                    "decision_id": item_id,
                    "action": response.get("action"),
                    "correction_text": response.get("correction_text"),
                }
                for item_id, response in state.semantic_dialogue_responses.items()
            ],
        }

        reply_text = ""
        suggestion: dict[str, str] = {}
        assistant = getattr(self._semantic_provider, "assist", None)
        if callable(assistant):
            try:
                raw_reply = assistant(bounded_context)
                if isinstance(raw_reply, Mapping):
                    reply_text = str(
                        raw_reply.get("response_text")
                        or raw_reply.get("message")
                        or ""
                    ).strip()
                    suggested_role = str(raw_reply.get("suggested_semantic_role") or "").strip()
                    suggested_variable = str(raw_reply.get("suggested_variable_name") or "").strip()
                    allowed = {
                        (item["semantic_role"], item["variable_name"])
                        for item in allowed_pairs
                    }
                    if suggested_role and suggested_variable and (suggested_role, suggested_variable) in allowed:
                        suggestion = {
                            "semantic_role": suggested_role,
                            "variable_name": suggested_variable,
                            "reason": str(raw_reply.get("suggestion_reason") or "").strip(),
                            "owner_text": owner_message,
                        }
                else:
                    reply_text = str(raw_reply or "").strip()
            except Exception:  # fail closed: chat help must never block owner control
                reply_text = ""
                suggestion = {}
        if suggestion:
            state.semantic_chat_suggestions[decision_id] = suggestion
        else:
            state.semantic_chat_suggestions.pop(decision_id, None)
        if not reply_text:
            proposal = str(decorated.get("presentation_text") or "").strip()
            reply_text = (
                f"La propuesta actual es: {proposal} "
                "Si no coincide con tu negocio, explicá qué significa. Si puedo mapearlo de forma segura al catálogo permitido, te mostraré una propuesta nueva para confirmar."
            )

        history = state.semantic_chat_messages.setdefault(decision_id, [])
        history.append({"role": "owner", "text": owner_message})
        history.append({"role": "assistant", "text": reply_text})
        return self._render_one_pending_question(session_id=session_id) or (
            HTTPStatus.OK,
            base._blocked_message_page("No quedó una columna pendiente para mostrar."),
        )

    def semantic_revise(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        """Turn one bounded LLM suggestion into a new validated owner proposal."""
        state = self.session(session_id)
        if not isinstance(state.semantic_assistance_state, Mapping) or not state.semantic_questions:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "No hay una corrección semántica pendiente."
            )
        current = state.semantic_questions[0]
        if not isinstance(current, Mapping):
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "La corrección no tiene una decisión semántica válida."
            )
        decision_id = str(current.get("decision_id") or "").strip()
        requested_id = str(fields.get("decision_id") or "").strip()
        suggestion = state.semantic_chat_suggestions.get(decision_id) or {}
        if not decision_id or requested_id != decision_id or not suggestion:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "No hay una propuesta asistida válida para esta columna."
            )

        revised = revise_service_1_assisted_semantic_decision_v1(
            previous_state=dict(state.semantic_assistance_state),
            decision_id=decision_id,
            semantic_role=str(suggestion.get("semantic_role") or ""),
            variable_name=str(suggestion.get("variable_name") or ""),
            owner_correction_text=str(suggestion.get("owner_text") or ""),
        )
        if revised.get("status") != STATUS_OWNER_DIALOGUE_REQUIRED:
            detail = revised.get("detail") or revised.get("blocked_reason")
            return self._render_one_pending_question(
                session_id=session_id,
                message=f"No pude convertir esa explicación en una interpretación segura: {detail}",
            ) or (HTTPStatus.OK, base._blocked_message_page("La corrección quedó pendiente."))

        state.semantic_assistance_state = revised
        state.semantic_questions = list(revised.get("owner_questions") or [])
        state.semantic_dialogue_responses.pop(decision_id, None)
        state.semantic_chat_suggestions.pop(decision_id, None)
        return self._render_one_pending_question(
            session_id=session_id,
            message="Revisé la interpretación con tu explicación. Confirmala si ahora representa correctamente la columna.",
        ) or (HTTPStatus.OK, base._blocked_message_page("La corrección no produjo una pregunta confirmable."))


def create_semantic_reception_server_v1(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    output_dir: str | Path | None = None,
    persist_tenant_confirmation: Any = None,
    load_tenant_memory: Any = None,
    load_prior_semantic_contract: Any = None,
    load_persisted_cases: Any = None,
    load_persisted_case: Any = None,
    require_tenant_persistence: bool = False,
    tenant_identity_resolver: Any = None,
    radar_policy_store: Any = None,
    semantic_provider: Any = None,
):
    application = Service1SemanticReceptionWebApplicationV1(
        output_dir=output_dir,
        persist_tenant_confirmation=persist_tenant_confirmation,
        load_tenant_memory=load_tenant_memory,
        load_prior_semantic_contract=load_prior_semantic_contract,
        load_persisted_cases=load_persisted_cases,
        load_persisted_case=load_persisted_case,
        require_tenant_persistence=require_tenant_persistence,
        radar_policy_store=radar_policy_store,
        semantic_provider=semantic_provider or semantic_provider_from_environment_v1(),
    )
    return base.ThreadingHTTPServer(
        (host, port),
        base._handler_for(
            application,
            tenant_identity_resolver=tenant_identity_resolver,
        ),
    )


__all__ = [
    "Service1SemanticReceptionWebApplicationV1",
    "create_semantic_reception_server_v1",
]

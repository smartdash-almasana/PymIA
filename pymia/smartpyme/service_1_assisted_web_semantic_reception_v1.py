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

    def _render_one_pending_question(
        self,
        *,
        session_id: str,
        message: str | None = None,
    ) -> tuple[int, str] | None:
        state = self.session(session_id)
        if not state.semantic_questions:
            return None
        state.semantic_questions = [state.semantic_questions[0]]
        question = state.semantic_questions[0]
        if isinstance(question, Mapping) and question.get("question_kind") == "UNIT_MEANING":
            return (
                HTTPStatus.OK,
                base._derived_unit_questions_page(
                    state.semantic_questions,
                    message,
                    ingestion_output=state.ingestion_output or {},
                ),
            )
        if state.semantic_assistance_state is not None:
            return (
                HTTPStatus.OK,
                base._assisted_semantic_dialogue_page(
                    [self._normalize_dialogue_decision(question)],
                    message,
                ),
            )
        return (
            HTTPStatus.OK,
            base._semantic_questions_page(
                state.semantic_questions,
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
        semantic_scope = (
            base._WORKING_CAPITAL_COMPONENT_CAPABILITIES
            if requested_capability == "working_capital"
            else ()
        )
        packet = base._run_product_root(
            ingestion_output=state.ingestion_output,
            requested_capability=requested_capability,
            output_dir=self._review_output_dir(session_id=session_id),
            deliver_result=requested_capability in {"sold_vs_collected_gap", "net_margin_real"},
            semantic_provider=self._semantic_provider,
            compatible_tenant_memory_hints=self._compatible_tenant_memory_hints(state),
            semantic_scope_capabilities=semantic_scope,
            use_assisted_semantics=True,
        )
        state.last_review_result = packet

        if packet.get("status") == base.STATUS_NEEDS_OWNER:
            assistance_state = packet.get("semantic_assistance_state")
            if not isinstance(assistance_state, dict):
                return HTTPStatus.OK, base._blocked_message_page(
                    "La interpretación semántica no produjo un estado trazable."
                )
            state.semantic_assistance_state = assistance_state
            state.semantic_questions = list(packet.get("owner_questions") or [])
            sequential = self._render_one_pending_question(session_id=session_id)
            if sequential is not None:
                return sequential
            return HTTPStatus.OK, base._blocked_message_page(
                "La interpretación necesita confirmación pero no produjo una pregunta válida."
            )

        state.semantic_questions = []
        if packet.get("status") == base.STATUS_BLOCKED:
            return HTTPStatus.OK, base._blocked_result_page(
                packet,
                requested_capability,
                ingestion_output=state.ingestion_output,
            )
        return HTTPStatus.OK, base._evaluated_result_page(
            packet,
            requested_capability,
            ingestion_output=state.ingestion_output,
        )

    def confirm_meanings(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        status, page = super().confirm_meanings(
            session_id=session_id,
            fields=fields,
        )
        sequential = self._render_one_pending_question(session_id=session_id)
        return sequential if sequential is not None else (status, page)


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

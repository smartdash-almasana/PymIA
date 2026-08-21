"""Upload-first semantic reception wiring for Servicio 1.

This module narrows the existing assisted web application to the reception layer:
Excel is parsed by the existing canonical intake, semantic interpretation is
performed through the injected bounded provider, and workbook-first owner
corroboration is limited to the grouped reading and material unresolved points.

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
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    run_service_1_governed_analysis_v1,
)
from pymia.smartpyme.service_1_result_memory_v1 import (
    Service1ResultMemoryRecordV1,
    service_1_result_memory_record_from_mapping_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_CONFIRMED,
    STATUS_OWNER_DIALOGUE_FOLLOWUP,
    STATUS_OWNER_DIALOGUE_REQUIRED,
    revise_service_1_assisted_semantic_decision_v1,
    run_service_1_assisted_semantic_initial_v1,
    run_service_1_assisted_semantic_reentry_v1,
)
from pymia.smartpyme.service_1_computability_v1 import STATUS_COMPUTABLE
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    build_computability_decision_from_confirmed_bindings_v1,
)
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import (
    F12_COMMERCIAL_ANALYSIS_IDS,
    STATUS_READY as F10_STATUS_READY,
    build_service_1_dynamic_analysis_discovery_v1,
    project_service_1_dynamic_discovery_menu_v1,
)
from pymia.smartpyme.service_1_ui_v1 import render_analysis_result_sets_v1


_DISCOVERY_SCHEMA_VERSION = "SERVICE_1_POST_SEMANTIC_ANALYSIS_DISCOVERY_V1"
_ROLE_LABELS_ES: dict[str, str] = {
    "operation_date": "fecha de operación",
    "sales_amount": "importe de ventas",
    "collected_amount": "importe cobrado",
    "accounts_receivable_amount": "cuentas por cobrar",
    "period_sales_total": "ventas del período",
    "period_costs_total": "costos del período",
    "period_taxes_total": "impuestos y comisiones del período",
    "initial_balance": "saldo inicial",
    "expected_collections": "cobros previstos",
    "expected_payments": "pagos previstos",
    "period_days": "días del período",
    "days": "días del período",
    "current_assets": "activo corriente",
    "current_liabilities": "pasivo corriente",
}


def _discovery_capability_ref_v1(launch_ref: str) -> str:
    ref = str(launch_ref or "").strip()
    if ref in base._REVIEW_BY_REF:
        return ref
    if ref in base._LAUNCH_REVIEW_BY_REF and base._WORKING_CAPITAL_COMPONENT_CAPABILITIES:
        return base._WORKING_CAPITAL_COMPONENT_CAPABILITIES[0]
    return ref


def _friendly_missing_group_v1(group: Sequence[str]) -> str:
    labels = [
        _ROLE_LABELS_ES.get(str(role).strip(), str(role).strip().replace("_", " "))
        for role in group
        if str(role).strip()
    ]
    return " o ".join(labels)


def build_service_1_post_semantic_analysis_discovery_v1(
    *,
    confirmed_bindings: Mapping[str, Any],
) -> dict[str, Any]:
    """Expose F10 AnalysisPlan discovery plus legacy launch compatibility.

    The F10 result is the technical source of truth for the new AnalysisPlan
    path. ``available`` / ``blocked`` remain a compatibility projection for the
    pre-F10 launch routes until F11 product wiring replaces them.
    """
    if (
        not isinstance(confirmed_bindings, Mapping)
        or confirmed_bindings.get("status") != STATUS_CONFIRMED_BINDINGS
    ):
        return {
            "schema_version": _DISCOVERY_SCHEMA_VERSION,
            "status": "BLOCKED",
            "blocked_reason": "CONFIRMED_BINDINGS_REQUIRED",
            "available": [],
            "blocked": [],
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    analysis_discovery = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=confirmed_bindings,
        commercially_exposed_analysis_ids=F12_COMMERCIAL_ANALYSIS_IDS,
    )
    if analysis_discovery.status != F10_STATUS_READY:
        return {
            "schema_version": _DISCOVERY_SCHEMA_VERSION,
            "status": "BLOCKED",
            "blocked_reason": analysis_discovery.blocked_reason or "F10_DISCOVERY_BLOCKED",
            "available": [],
            "blocked": [],
            "analysis_plans": [],
            "technically_available_analysis_ids": [],
            "commercially_exposed_analysis_ids": [],
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    analysis_menu = project_service_1_dynamic_discovery_menu_v1(analysis_discovery)
    if analysis_menu.get("status") != "READY":
        return {
            "schema_version": _DISCOVERY_SCHEMA_VERSION,
            "status": "BLOCKED",
            "blocked_reason": analysis_menu.get("blocked_reason") or "F12_MENU_PROJECTION_BLOCKED",
            "available": [],
            "blocked": [],
            "analysis_menu_available": [],
            "analysis_menu_blocked": [],
            "analysis_plans": [item.to_dict() for item in analysis_discovery.analyses],
            "technically_available_analysis_ids": [item.analysis_id for item in analysis_discovery.technically_available],
            "commercially_exposed_analysis_ids": [item.analysis_id for item in analysis_discovery.commercially_exposed],
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    available: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for launch_ref, name, question in base._LAUNCH_REVIEW_OPTIONS:
        capability_ref = _discovery_capability_ref_v1(launch_ref)
        decision = build_computability_decision_from_confirmed_bindings_v1(
            confirmed_bindings=dict(confirmed_bindings),
            requested_capability=capability_ref,
        )
        decision_payload = decision.to_dict()
        governed = decision_payload.get("governed_computation_input")
        source_bindings = (
            dict(governed.get("source_bindings") or {})
            if isinstance(governed, Mapping)
            else {}
        )
        item = {
            "launch_ref": launch_ref,
            "name": name,
            "question": question,
            "canonical_capability_ref": capability_ref,
            "p8_status": decision.status,
            "p8_reason": decision.reason,
            "evidence_used": source_bindings,
            "missing_evidence": [
                _friendly_missing_group_v1(group)
                for group in decision.missing_role_groups
                if _friendly_missing_group_v1(group)
            ],
            "why_needed": f"Hace falta para responder de forma trazable: {question}",
        }
        if decision.status == STATUS_COMPUTABLE:
            available.append(item)
        else:
            blocked.append(item)

    return {
        "schema_version": _DISCOVERY_SCHEMA_VERSION,
        "status": "READY",
        "blocked_reason": None,
        "available": available,
        "blocked": blocked,
        "analysis_menu_available": [list(item) for item in (analysis_menu.get("available") or [])],
        "analysis_menu_blocked": [dict(item) for item in (analysis_menu.get("blocked") or []) if isinstance(item, Mapping)],
        "analysis_plans": [item.to_dict() for item in analysis_discovery.analyses],
        "technically_available_analysis_ids": [
            item.analysis_id for item in analysis_discovery.technically_available
        ],
        "commercially_exposed_analysis_ids": [
            item.analysis_id for item in analysis_discovery.commercially_exposed
        ],
        "legacy_launch_compatibility": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


class Service1SemanticReceptionWebApplicationV1(base.AssistedWebApplicationV1):
    """Existing web application with bounded LLM semantics and sequential HITL."""

    def __init__(
        self,
        *,
        persist_result_memory: Any = None,
        load_result_memory: Any = None,
        load_result_memory_record: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._persist_result_memory = persist_result_memory
        self._load_result_memory = load_result_memory
        self._load_result_memory_record = load_result_memory_record

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
                    f"Entendí {subject} como {proposed}. ¿Está bien?"
                )
        return normalized

    @staticmethod
    def _owner_accept_is_resolved(*, state: Any, question: Mapping[str, Any]) -> bool:
        """Return True only when SEM-5 can project ACCEPT into concrete owner evidence."""
        assistance = (
            state.semantic_assistance_state
            if isinstance(state.semantic_assistance_state, Mapping)
            else {}
        )
        validated = (
            assistance.get("validated_packet")
            if isinstance(assistance.get("validated_packet"), Mapping)
            else {}
        )
        proposal_refs = [
            str(ref).strip()
            for ref in (question.get("proposal_refs") or [])
            if str(ref).strip()
        ]
        # Legacy/non-SEM-5 questions keep their existing behavior. Productive SEM-4
        # decisions always carry proposal_refs and are checked against SEM-5 shape.
        if not proposal_refs:
            return True
        decisions = {
            str(item.get("decision_id") or "").strip(): item
            for item in (validated.get("decisions") or [])
            if isinstance(item, Mapping) and str(item.get("decision_id") or "").strip()
        }
        for proposal_ref in proposal_refs:
            item = decisions.get(proposal_ref)
            if not isinstance(item, Mapping):
                return False
            source_kind = str(item.get("source_kind") or "").strip()
            targets = [
                str(ref).strip()
                for ref in (item.get("target_refs") or [])
                if str(ref).strip()
            ]
            if source_kind in {"CONCEPT", "DUPLICATE_SEMANTICS"}:
                if not str(item.get("semantic_role") or "").strip() or not targets:
                    return False
                continue
            if source_kind == "RELATIONSHIP":
                if len(targets) != 2 or not str(item.get("relationship_type") or "").strip():
                    return False
                continue
            # MATERIAL_AMBIGUITY and any unknown source kind contain no concrete
            # semantic fact that owner ACCEPT can safely turn into canonical evidence.
            return False
        return True

    def _drop_unresolved_accept_responses(self, *, state: Any) -> None:
        """Keep replayed owner responses aligned with the currently active dialogue plan."""
        assistance = (
            state.semantic_assistance_state
            if isinstance(state.semantic_assistance_state, Mapping)
            else {}
        )
        dialogue = (
            assistance.get("dialogue_plan")
            if isinstance(assistance.get("dialogue_plan"), Mapping)
            else {}
        )
        decisions = {
            str(item.get("decision_id") or "").strip(): item
            for item in (dialogue.get("decisions") or [])
            if isinstance(item, Mapping) and str(item.get("decision_id") or "").strip()
        }
        for decision_id, response in list(state.semantic_dialogue_responses.items()):
            current_id = str(decision_id).strip()
            question = decisions.get(current_id)
            # A previous semantic pass may have produced a different grouped decision
            # id. Never replay that stale response into the current SEM-8 plan.
            if not isinstance(question, Mapping):
                state.semantic_dialogue_responses.pop(decision_id, None)
                continue
            if str(response.get("action") or "").strip().upper() == "ACCEPT" and not self._owner_accept_is_resolved(
                state=state,
                question=question,
            ):
                state.semantic_dialogue_responses.pop(decision_id, None)

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

        normalized["accept_enabled"] = self._owner_accept_is_resolved(
            state=state,
            question=normalized,
        )
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

    def _post_semantic_analysis_menu_page(self, *, session_id: str) -> tuple[int, str]:
        state = self.session(session_id)
        assistance = (
            state.semantic_assistance_state
            if isinstance(state.semantic_assistance_state, Mapping)
            else {}
        )
        semantic_run = assistance.get("semantic_run")
        discovery = build_service_1_post_semantic_analysis_discovery_v1(
            confirmed_bindings=(semantic_run if isinstance(semantic_run, Mapping) else {})
        )
        if discovery.get("status") != "READY":
            return HTTPStatus.OK, base._blocked_message_page(
                "La semántica quedó cerrada, pero PymIA no pudo proyectar de forma segura qué análisis son computables."
            )
        ingestion = state.ingestion_output if isinstance(state.ingestion_output, Mapping) else {}
        filename = str(ingestion.get("filename") or ingestion.get("source_file_ref") or "").strip()
        available = [
            (str(item[0]), str(item[1]), str(item[2]))
            for item in discovery.get("analysis_menu_available") or []
            if isinstance(item, (list, tuple)) and len(item) == 3
        ]
        available.extend(
            (
                str(item.get("launch_ref") or ""),
                str(item.get("name") or ""),
                str(item.get("question") or ""),
            )
            for item in (discovery.get("available") or [])
            if isinstance(item, Mapping) and str(item.get("launch_ref") or "").strip()
        )
        blocked = [
            dict(item)
            for item in discovery.get("analysis_menu_blocked") or []
            if isinstance(item, Mapping)
        ]
        blocked.extend(
            dict(item)
            for item in (discovery.get("blocked") or [])
            if isinstance(item, Mapping)
        )
        return HTTPStatus.OK, base.render_analysis_menu_v1(
            available,
            filename=filename,
            blocked_options=blocked,
        )

    def analysis_menu(self, *, session_id: str) -> tuple[int, str]:
        """Return to the analysis menu for the workbook already confirmed in-session."""
        state = self.session(session_id)
        assistance = state.semantic_assistance_state if isinstance(state.semantic_assistance_state, Mapping) else {}
        semantic_run = assistance.get("semantic_run") if isinstance(assistance, Mapping) else None
        if not isinstance(semantic_run, Mapping) or semantic_run.get("status") != STATUS_CONFIRMED_BINDINGS:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "Primero terminá de revisar el archivo para elegir otro análisis."
            )
        return self._post_semantic_analysis_menu_page(session_id=session_id)

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
            state.semantic_questions = []
            state.semantic_answers = {}
            state.semantic_scope_answers = {}
            state.semantic_assistance_state = None
            state.semantic_dialogue_responses = {}
            state.semantic_chat_messages = {}
            state.semantic_chat_suggestions = {}
            assistance_state = run_service_1_assisted_semantic_initial_v1(
                ingestion_output=state.ingestion_output,
                requested_capability=None,
                provider=self._semantic_provider,
                compatible_tenant_memory_hints=self._compatible_tenant_memory_hints(state),
            )
            state.last_review_result = assistance_state
            if assistance_state.get("status") == STATUS_OWNER_DIALOGUE_REQUIRED:
                state.semantic_assistance_state = assistance_state
                state.semantic_questions = list(assistance_state.get("owner_questions") or [])
                sequential = self._render_one_pending_question(session_id=session_id)
                if sequential is not None:
                    return sequential
                return HTTPStatus.OK, base._blocked_message_page(
                    "La comprensión semántica requiere intervención del dueño pero no produjo una pregunta válida."
                )
            if assistance_state.get("status") == STATUS_CONFIRMED:
                state.semantic_assistance_state = assistance_state
                state.semantic_questions = []
                return self._post_semantic_analysis_menu_page(session_id=session_id)
            return HTTPStatus.OK, base._blocked_message_page(
                str(
                    assistance_state.get("detail")
                    or assistance_state.get("blocked_reason")
                    or "La comprensión semántica no pudo iniciarse de forma segura."
                )
            )

        sequential = self._render_one_pending_question(session_id=session_id)
        return sequential if sequential is not None else (status, page)

    @staticmethod
    def _tenant_id_for_state(state: Any) -> str:
        tenant = str(getattr(state, "tenant_id", "") or "").strip()
        if not tenant and getattr(state, "tenant_identity_contract", None) is not None:
            tenant = str(
                getattr(state.tenant_identity_contract, "tenant_id", "") or ""
            ).strip()
        return tenant

    @staticmethod
    def _validated_result_memory_record(
        raw_record: Any,
        *,
        tenant_id: str,
        memory_record_id: str | None = None,
    ) -> Service1ResultMemoryRecordV1:
        if isinstance(raw_record, Service1ResultMemoryRecordV1):
            record = service_1_result_memory_record_from_mapping_v1(raw_record.to_dict())
        elif isinstance(raw_record, Mapping):
            record = service_1_result_memory_record_from_mapping_v1(raw_record)
        else:
            raise TypeError("result memory loader returned an invalid record")
        if record.tenant_id != tenant_id:
            raise ValueError("result memory crossed tenant boundary")
        expected_id = str(memory_record_id or "").strip()
        if expected_id and record.memory_record_id != expected_id:
            raise ValueError("result memory crossed record boundary")
        return record

    def result_memory_history(
        self,
        *,
        session_id: str,
        analysis_id: str,
        limit: int = 100,
    ) -> tuple[dict[str, Any], ...]:
        state = self.session(session_id)
        tenant = self._tenant_id_for_state(state)
        if not tenant or self._load_result_memory is None:
            return ()
        records = self._load_result_memory(tenant, analysis_id, limit=limit)
        return tuple(
            self._validated_result_memory_record(record, tenant_id=tenant).to_dict()
            for record in records
        )

    def recent_cases(self, *, session_id: str) -> tuple[int, str]:
        """List transient cases plus durable F13 ResultSets for the active tenant."""
        scope = self._case_scope(session_id=session_id)
        snapshots = list(self._case_snapshots.get(scope, {}).values())
        state = self.session(session_id)
        tenant = self._tenant_id_for_state(state)

        if tenant and self._load_persisted_cases is not None:
            try:
                persisted = self._load_persisted_cases(tenant)
            except Exception:
                if self._require_tenant_persistence:
                    return HTTPStatus.BAD_REQUEST, base._error_page(
                        "No pudimos recuperar los casos persistidos del tenant."
                    )
                persisted = ()
            seen_case_ids = {str(item.get("case_id") or "").strip() for item in snapshots}
            for item in persisted:
                row = dict(item)
                case_id = str(row.get("case_id") or "").strip()
                if case_id and case_id not in seen_case_ids:
                    snapshots.append(row)
                    seen_case_ids.add(case_id)

        if tenant and self._load_result_memory is not None:
            try:
                durable_records = self._load_result_memory(tenant, None, limit=100)
                validated_records = tuple(
                    self._validated_result_memory_record(record, tenant_id=tenant)
                    for record in durable_records
                )
            except Exception:
                return HTTPStatus.BAD_REQUEST, base._error_page(
                    "No pudimos recuperar de forma íntegra los resultados persistidos del tenant."
                )
            seen_refs = {str(item.get("case_ref") or "").strip() for item in snapshots}
            for record in validated_records:
                if record.memory_record_id in seen_refs:
                    continue
                snapshots.append(
                    {
                        "case_ref": record.memory_record_id,
                        "case_id": record.case_id,
                        "service_ref": record.analysis_id,
                        "service_name": f"Resultado guardado · {record.analysis_id}",
                        "status": "RESULTADO PERSISTIDO",
                        "kind": "persisted_result_memory",
                        "updated_at": record.executed_at,
                        "memory_record_id": record.memory_record_id,
                    }
                )
                seen_refs.add(record.memory_record_id)

        snapshots.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        return HTTPStatus.OK, base._recent_cases_page(snapshots)

    def open_case(self, *, session_id: str, case_ref: str) -> tuple[int, str]:
        """Reopen an immutable F13 ResultSet without XLSX, semantics, or recalculation."""
        memory_record_id = str(case_ref or "").strip()
        if not memory_record_id.startswith("s1rm_"):
            return super().open_case(session_id=session_id, case_ref=case_ref)

        state = self.session(session_id)
        tenant = self._tenant_id_for_state(state)
        if not tenant:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "No hay un tenant identificado para reabrir este resultado."
            )
        if self._load_result_memory_record is None:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "La memoria longitudinal de resultados no está disponible en este entorno."
            )
        try:
            raw_record = self._load_result_memory_record(tenant, memory_record_id)
            if raw_record is None:
                return HTTPStatus.NOT_FOUND, base._error_page(
                    "No encontramos ese resultado persistido para este tenant."
                )
            record = self._validated_result_memory_record(
                raw_record,
                tenant_id=tenant,
                memory_record_id=memory_record_id,
            )
        except Exception:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "El resultado persistido no superó la validación de identidad e integridad."
            )

        packet = {
            "schema_version": "SERVICE_1_F13_RESULT_MEMORY_REENTRY_V1",
            "status": "READY",
            "analysis_id": record.analysis_id,
            "title": record.analysis_id,
            "question": "Resultado persistido de una ejecución gobernada anterior.",
            "result_set": record.to_dict()["result_set"],
            "result_memory": {
                "status": "REENTERED",
                "memory_record_id": record.memory_record_id,
                "period": record.period.to_dict(),
                "artifact_ref": record.artifact_ref,
                "result_set_integrity_digest": record.result_set_integrity_digest,
                "executed_at": record.executed_at,
            },
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
        return HTTPStatus.OK, render_analysis_result_sets_v1((packet,))

    def _execute_f12_analysis(self, *, session_id: str, analysis_id: str) -> dict[str, Any]:
        """Web adapter: request one analysis from the canonical product root."""
        state = self.session(session_id)
        assistance = (
            state.semantic_assistance_state
            if isinstance(state.semantic_assistance_state, Mapping)
            else {}
        )
        confirmed_run = assistance.get("semantic_run")
        ingestion = state.ingestion_output
        return run_service_1_governed_analysis_v1(
            ingestion_output=(ingestion if isinstance(ingestion, Mapping) else {}),
            confirmed_bindings=(confirmed_run if isinstance(confirmed_run, Mapping) else {}),
            analysis_id=analysis_id,
            tenant_identity_contract=state.tenant_identity_contract,
            persist_result_memory=self._persist_result_memory,
        )

    def run_selected_reviews(
        self,
        *,
        session_id: str,
        requested_capabilities: Sequence[str],
    ) -> tuple[int, str]:
        requested = tuple(
            dict.fromkeys(
                str(value or "").strip()
                for value in requested_capabilities
                if str(value or "").strip()
            )
        )
        if not requested:
            return HTTPStatus.BAD_REQUEST, self._post_semantic_analysis_menu_page(session_id=session_id)[1]
        if not any(value in F12_COMMERCIAL_ANALYSIS_IDS for value in requested):
            return super().run_selected_reviews(
                session_id=session_id,
                requested_capabilities=requested,
            )
        if any(value not in F12_COMMERCIAL_ANALYSIS_IDS for value in requested):
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "No se pueden mezclar análisis workbook-first con revisiones legacy en la misma ejecución."
            )

        state = self.session(session_id)
        state.last_review_result = None
        packets = [
            self._execute_f12_analysis(session_id=session_id, analysis_id=analysis_id)
            for analysis_id in requested
        ]
        blocked = [packet for packet in packets if packet.get("status") != "READY"]
        if blocked:
            return self._post_semantic_analysis_menu_page(session_id=session_id)
        state.last_review_result = {
            "schema_version": "SERVICE_1_F12_ANALYSIS_BUNDLE_V1",
            "status": "READY",
            "analysis_ids": list(requested),
            "results": packets,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
        return HTTPStatus.OK, render_analysis_result_sets_v1(packets)

    def run_review(
        self,
        *,
        session_id: str,
        requested_capability: str,
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "Primero subí un archivo de Excel."
            )

        if requested_capability in F12_COMMERCIAL_ANALYSIS_IDS:
            state.last_review_result = None
            packet = self._execute_f12_analysis(
                session_id=session_id,
                analysis_id=requested_capability,
            )
            if packet.get("status") != "READY":
                return self._post_semantic_analysis_menu_page(session_id=session_id)
            state.last_review_result = packet
            return HTTPStatus.OK, render_analysis_result_sets_v1((packet,))

        assistance = (
            state.semantic_assistance_state
            if isinstance(state.semantic_assistance_state, Mapping)
            else {}
        )
        confirmed_run = assistance.get("semantic_run")
        is_post_discovery_launch = (
            requested_capability in base._LAUNCH_REVIEW_BY_REF
            or requested_capability == "working_capital"
        )
        if (
            is_post_discovery_launch
            and isinstance(confirmed_run, Mapping)
            and confirmed_run.get("status") == STATUS_CONFIRMED_BINDINGS
        ):
            discovery = build_service_1_post_semantic_analysis_discovery_v1(
                confirmed_bindings=confirmed_run
            )
            available_refs = {
                str(item.get("launch_ref") or "").strip()
                for item in (discovery.get("available") or [])
                if isinstance(item, Mapping)
            }
            if discovery.get("status") != "READY" or requested_capability not in available_refs:
                return self._post_semantic_analysis_menu_page(session_id=session_id)

            state.selected_launch_review = requested_capability
            if requested_capability == "working_capital":
                return super().run_working_capital(
                    session_id=session_id,
                    semantic_run_override=confirmed_run,
                )

            packet = base._run_product_root(
                ingestion_output=state.ingestion_output,
                requested_capability=requested_capability,
                output_dir=self._review_output_dir(session_id=session_id),
                deliver_result=requested_capability in {"sold_vs_collected_gap", "net_margin_real"},
                semantic_run_override=confirmed_run,
            )
            state.last_review_result = packet
            case_id = str(
                state.ingestion_output.get("case_id")
                or state.ingestion_output.get("source_file_ref")
                or requested_capability
            ).strip()
            service_name = base._LAUNCH_REVIEW_BY_REF.get(
                requested_capability,
                base._REVIEW_BY_REF.get(
                    requested_capability,
                    (requested_capability, requested_capability, ""),
                ),
            )[1]
            blocked = packet.get("status") in {base.STATUS_BLOCKED, base.STATUS_NEEDS_OWNER}
            self._remember_case(
                session_id=session_id,
                case_id=case_id,
                service_ref=requested_capability,
                service_name=service_name,
                status="FALTA INFORMACIÓN" if blocked else "LISTO",
                kind="review",
                packet=packet,
                ingestion_output=state.ingestion_output,
            )
            rendered = (
                base._blocked_result_page(
                    packet,
                    requested_capability,
                    ingestion_output=state.ingestion_output,
                    semantic_answers=state.semantic_answers,
                )
                if blocked
                else base._evaluated_result_page(
                    packet,
                    requested_capability,
                    ingestion_output=state.ingestion_output,
                )
            )
            return self._complete_selected_review(
                session_id=session_id,
                requested_capability=requested_capability,
                packet=packet,
                rendered_page=rendered,
            )

        if requested_capability not in base._REVIEW_BY_REF and requested_capability != "working_capital":
            return super().run_review(
                session_id=session_id,
                requested_capability=requested_capability,
            )

        # Backwards-compatible capability-scoped entrypoint for callers that did
        # not traverse workbook-first reception/discovery.
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
    def _allowed_role_variable_pairs(
        assistance: Mapping[str, Any],
        *,
        column_refs: Sequence[str] | None = None,
    ) -> list[dict[str, str]]:
        context = assistance.get("context")
        hypotheses = getattr(context, "deterministic_hypotheses", ())
        target_refs = {
            str(ref).strip()
            for ref in (column_refs or [])
            if str(ref).strip()
        }
        pairs: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for raw in hypotheses:
            if not isinstance(raw, Mapping):
                continue
            sheet = str(raw.get("sheet_name") or "").strip()
            column = str(raw.get("column_name") or "").strip()
            if target_refs and sheet and column:
                ref = f"{sheet}.{column}"
                if ref not in target_refs:
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
        self._drop_unresolved_accept_responses(state=state)
        if state.semantic_assistance_state is not None and state.semantic_questions:
            current = state.semantic_questions[0]
            if isinstance(current, Mapping):
                decision_id = str(current.get("decision_id") or "").strip()
                action = str(fields.get(f"action_{decision_id}") or "").strip().upper()
                decorated = self._decorate_dialogue_decision(
                    session_id=session_id,
                    question=current,
                )
                if action == "ACCEPT" and not bool(decorated.get("accept_enabled", True)):
                    state.semantic_dialogue_responses.pop(decision_id, None)
                    return self._render_one_pending_question(
                        session_id=session_id,
                        message=(
                            "Todavía no hay un significado concreto para confirmar. "
                            "Explicame con tus palabras qué representa esta columna o elegí no usarla."
                        ),
                    ) or (HTTPStatus.BAD_REQUEST, base._error_page("Falta resolver la interpretación."))
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
                if state.selected_launch_review is None:
                    return self._confirm_workbook_first_semantics(
                        session_id=session_id,
                        fields=fields,
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

    def _confirm_workbook_first_semantics(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if not isinstance(state.semantic_assistance_state, dict) or not state.semantic_questions:
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "No hay una interpretación asistida pendiente para confirmar."
            )
        current = state.semantic_questions[0]
        if not isinstance(current, Mapping):
            return HTTPStatus.OK, base._blocked_message_page(
                "La decisión semántica no tiene identidad trazable."
            )
        decision_id = str(current.get("decision_id") or "").strip()
        dialogue = (
            state.semantic_assistance_state.get("dialogue_plan")
            if isinstance(state.semantic_assistance_state.get("dialogue_plan"), Mapping)
            else {}
        )
        active_decision_ids = {
            str(item.get("decision_id") or "").strip()
            for item in (dialogue.get("decisions") or [])
            if isinstance(item, Mapping) and str(item.get("decision_id") or "").strip()
        }
        if decision_id not in active_decision_ids:
            state.semantic_dialogue_responses.pop(decision_id, None)
            fresh_questions = [
                dict(item)
                for item in (state.semantic_assistance_state.get("owner_questions") or [])
                if isinstance(item, Mapping)
                and str(item.get("decision_id") or "").strip() in active_decision_ids
            ]
            state.semantic_questions = fresh_questions
            refreshed = self._render_one_pending_question(
                session_id=session_id,
                message="Actualicé la lectura del archivo. Revisá esta versión para continuar.",
            )
            if refreshed is not None:
                return refreshed
            return HTTPStatus.BAD_REQUEST, base._error_page(
                "La revisión del archivo cambió. Volvé a revisar los datos antes de continuar."
            )
        action = str(fields.get(f"action_{decision_id}") or "").strip().upper()
        if not decision_id or action not in {"ACCEPT", "SKIP"}:
            return self._render_one_pending_question(
                session_id=session_id,
                message="Elegí confirmar o no usar la interpretación visible.",
            ) or (HTTPStatus.BAD_REQUEST, base._error_page("Falta la confirmación."))

        state.semantic_dialogue_responses[decision_id] = {
            "decision_id": decision_id,
            "action": action,
        }
        actor_id = str(state.owner_actor_id or "").strip()
        actor_role = str(state.owner_actor_role or "").strip()
        if not actor_id or not actor_role:
            if self._require_tenant_persistence:
                return HTTPStatus.BAD_REQUEST, base._error_page(
                    "Falta la identidad verificada de la persona que confirma."
                )
            actor_id = f"session:{session_id}"
            actor_role = "SESSION_OWNER"

        ingestion = state.ingestion_output if isinstance(state.ingestion_output, Mapping) else {}
        file_ref = str(ingestion.get("source_file_ref") or ingestion.get("filename") or "").strip() or None
        reentered = run_service_1_assisted_semantic_reentry_v1(
            previous_state=state.semantic_assistance_state,
            owner_responses=[
                dict(item)
                for key, item in state.semantic_dialogue_responses.items()
                if str(key).strip() in active_decision_ids
            ],
            owner_actor_id=actor_id,
            owner_actor_role=actor_role,
            file_ref=file_ref,
        )
        state.last_review_result = reentered
        if reentered.get("status") == STATUS_OWNER_DIALOGUE_FOLLOWUP:
            state.semantic_assistance_state = reentered
            state.semantic_questions = list(reentered.get("owner_questions") or [])
            sequential = self._render_one_pending_question(session_id=session_id)
            if sequential is not None:
                return sequential
        if reentered.get("status") == STATUS_CONFIRMED:
            state.semantic_assistance_state = reentered
            state.semantic_questions = []
            try:
                self._persist_owner_confirmation_events(
                    state=state,
                    packet={"semantic_run": reentered.get("semantic_run")},
                )
            except base.Service1AssistedWebTenantPersistenceErrorV1:
                return HTTPStatus.OK, base._blocked_message_page(
                    "La confirmación fue recibida, pero no pudo guardarse de forma durable."
                )
            return self._post_semantic_analysis_menu_page(session_id=session_id)
        return HTTPStatus.OK, base._blocked_message_page(
            str(
                reentered.get("detail")
                or reentered.get("blocked_reason")
                or "La confirmación semántica no pudo cerrarse de forma segura."
            )
        )

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
        current_refs = [
            str(ref).strip()
            for ref in (decorated.get("column_refs") or [])
            if str(ref).strip()
        ]
        interaction_mode = (
            "CORRECTION"
            if str(fields.get("correction_mode") or "").strip() == "1"
            else "CONVERSATION"
        )
        allowed_pairs = self._allowed_role_variable_pairs(
            state.semantic_assistance_state,
            column_refs=current_refs,
        )
        bounded_context = {
            "decision_id": decision_id,
            "interaction_mode": interaction_mode,
            "column_refs": current_refs,
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
            "owner_can_skip": len(current_refs) == 1 and not list(decorated.get("relationship_refs") or []),
            "requested_capability": state.selected_launch_review,
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
    persist_result_memory: Any = None,
    load_result_memory: Any = None,
    load_result_memory_record: Any = None,
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
        persist_result_memory=persist_result_memory,
        load_result_memory=load_result_memory,
        load_result_memory_record=load_result_memory_record,
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

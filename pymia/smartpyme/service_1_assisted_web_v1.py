"""Local, assisted HTML flow for the single Servicio 1 product root."""
from __future__ import annotations

import argparse
import html
import json
import math
import secrets
import tempfile
import threading
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import parse_qs, urlsplit

from pymia.smartpyme.service_1_column_understanding_engine_v1 import normalize_service_1_column_understanding_header_v1
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    STATUS_READY as STRUCTURAL_MEMORY_READY,
    select_service_1_compatible_tenant_memory_hints_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    STATUS_READY as WORKBOOK_PROFILE_READY,
    build_service_1_workbook_profile_v1,
)
from pymia.smartpyme.service_1_owner_unit_confirmation_event_v1 import (
    ALLOWED_UNIT_KINDS,
    build_service_1_owner_unit_confirmation_event_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    STATUS_UNCONFIRMED_READY as CANONICAL_UNCONFIRMED_READY,
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_assisted_web_tenant_wiring_v1 import (
    Service1AssistedWebTenantPersistenceErrorV1,
    build_service_1_assisted_web_tenant_identity_v1,
    persist_service_1_assisted_web_owner_events_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_owner_policy_wiring_v1 import (
    build_consorcios_radar_owner_menu_v1,
    evaluate_consorcios_radar_observation_with_owner_policy_v1,
    persist_consorcios_radar_owner_policy_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_plug_v1 import (
    project_bank_reconciliation_to_radar_v1,
    project_collection_aging_to_radar_v1,
    project_expense_variance_to_radar_v1,
)
from pymia.smartpyme.service_1_radar_supabase_persistence_v1 import (
    Service1RadarSupabasePersistenceAdapterV1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_NEEDS_OWNER,
    STATUS_RECONCILIATION_NEEDS_EVIDENCE,
    STATUS_RECONCILIATION_NEEDS_OWNER,
    STATUS_RECONCILIATION_REVIEW_READY,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_legacy_semantic_reentry_compat_v1 import (
    resolve_service_1_legacy_semantic_run_v1,
)
from pymia.smartpyme.service_1_reconciliation_human_review_decision_v1 import (
    ALLOWED_DECISIONS as ALLOWED_RECONCILIATION_DECISIONS,
    build_reconciliation_human_review_decision_v1,
)
from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
)
from pymia.smartpyme.service_1_reconciliation_workpaper_xlsx_v1 import (
    build_service_1_reconciliation_workpaper_xlsx_v1,
)
from pymia.smartpyme.service_1_supabase_identity_resolver_v1 import (
    SERVICE_1_ACCESS_TOKEN_COOKIE,
    Service1SupabaseIdentityResolverV1,
)
from pymia.smartpyme.service_1_supabase_persistence_v1 import (
    Service1SupabasePersistenceAdapterV1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)

_MODULE_DIR = Path(__file__).resolve().parent
_TEMPLATE_PATH = _MODULE_DIR / "templates" / "service_1_assisted_web_v1.html"
_STYLES_PATH = _MODULE_DIR / "static" / "service_1_assisted_web_v1.css"

_REVIEW_OPTIONS: tuple[tuple[str, str, str], ...] = (
    ("sold_vs_collected_gap", "Ventas y cobros", "Compará lo vendido con lo cobrado en el período."),
    ("net_margin_real", "Margen neto real", "Compará el margen real estimado a partir del precio, los costos y los impuestos."),
    ("projected_closing_cash_balance", "Saldo de caja proyectado", "Calculá un saldo de cierre a partir de movimientos confirmados."),
    ("dso", "Tiempo de cobro", "Conocé la relación entre cuentas por cobrar, ventas y días del período."),
    ("payment_collection_gap", "Cobros y pagos", "Compará los tiempos ya calculados de cobro y de pago."),
    ("reorder_point", "Punto de reposición", "Calculá cuándo conviene revisar la reposición según datos confirmados."),
    ("inventory_turnover", "Rotación de inventario", "Mostrá la relación entre inventario y costo registrado."),
    ("current_ratio", "Relación de corto plazo", "Compará activos y pasivos corrientes confirmados."),
    ("sales_concentration", "Concentración de ventas", "Mostrá qué parte de las ventas registradas corresponde al producto principal."),
    ("interest_burden_ratio", "Carga de intereses", "Compará intereses registrados con el resultado operativo informado."),
    ("adjusted_operating_cash_flow", "Flujo operativo ajustado", "Calculá una relación a partir de resultados y movimientos confirmados."),
    ("index_update_ratio", "Actualización entre índices", "Compará un índice de cierre con un índice de origen."),
)
_REVIEW_BY_REF = {item[0]: item for item in _REVIEW_OPTIONS}

_LAUNCH_REVIEW_OPTIONS: tuple[tuple[str, str, str], ...] = (
    (
        "sold_vs_collected_gap",
        "Ventas vs. cobros",
        "Vas a ver cuánto vendiste, cuánto cobraste y qué diferencia quedó pendiente de revisar.",
    ),
    (
        "net_margin_real",
        "Margen real",
        "Vas a ver cuánto margen dejan tus ventas usando los precios, costos e impuestos disponibles.",
    ),
    (
        "working_capital",
        "Caja y corto plazo",
        "Vas a revisar caja proyectada, tiempo de cobro y capacidad de cubrir obligaciones de corto plazo.",
    ),
)
_LAUNCH_REVIEW_BY_REF = {item[0]: item for item in _LAUNCH_REVIEW_OPTIONS}
_WORKING_CAPITAL_COMPONENT_CAPABILITIES: tuple[str, ...] = (
    "projected_closing_cash_balance",
    "dso",
    "current_ratio",
)

_LAUNCH_REVIEW_RELEVANT_HEADERS: dict[str, frozenset[str]] = {}
_LAUNCH_REVIEW_RELEVANT_ROLES: dict[str, frozenset[str]] = {}

_RECONCILIATION_OPTIONS: tuple[tuple[str, str, str], ...] = (
    (
        BANK_RECONCILIATION,
        "Conciliación bancaria",
        "Compará el extracto bancario con tus cobros o movimientos internos.",
    ),
    (
        MERCADO_PAGO_BANK_RECONCILIATION,
        "Mercado Pago ↔ Banco",
        "Compará las liquidaciones de Mercado Pago con las acreditaciones bancarias.",
    ),
)
_RECONCILIATION_BY_TYPE = {item[0]: item for item in _RECONCILIATION_OPTIONS}

_RECONCILIATION_NUMERIC_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {
    BANK_RECONCILIATION: {
        "bank": ("importe",),
        "internal": ("importe",),
    },
    MERCADO_PAGO_BANK_RECONCILIATION: {
        "mercado_pago": (
            "importe_bruto",
            "comision",
            "retencion",
            "importe_neto",
        ),
        "bank": ("importe",),
    },
}

_RECONCILIATION_DATE_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {
    BANK_RECONCILIATION: {
        "bank": ("fecha",),
        "internal": ("fecha",),
    },
    MERCADO_PAGO_BANK_RECONCILIATION: {
        "mercado_pago": ("fecha_operacion",),
        "bank": ("fecha",),
    },
}

_RECONCILIATION_SOURCES: dict[str, tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]] = {
    BANK_RECONCILIATION: (
        (
            "bank",
            "Extracto bancario",
            (
                ("id", "ID del movimiento"),
                ("fecha", "Fecha"),
                ("importe", "Importe"),
                ("referencia", "Referencia"),
            ),
        ),
        (
            "internal",
            "Cobros o movimientos internos",
            (
                ("id", "ID del movimiento"),
                ("fecha", "Fecha"),
                ("importe", "Importe"),
                ("referencia", "Referencia"),
            ),
        ),
    ),
    MERCADO_PAGO_BANK_RECONCILIATION: (
        (
            "mercado_pago",
            "Liquidaciones de Mercado Pago",
            (
                ("operacion_mp_id", "ID de operación"),
                ("fecha_operacion", "Fecha de operación"),
                ("importe_bruto", "Importe bruto"),
                ("comision", "Comisión"),
                ("retencion", "Retención"),
                ("importe_neto", "Importe neto"),
                ("lote_id", "Lote"),
                ("referencia", "Referencia"),
            ),
        ),
        (
            "bank",
            "Extracto bancario",
            (
                ("movimiento_banco_id", "ID del movimiento bancario"),
                ("fecha", "Fecha"),
                ("importe", "Importe acreditado"),
                ("lote_id", "Lote"),
                ("referencia", "Referencia"),
            ),
        ),
    ),
}


@dataclass
class ConsorcioCaseContextV1:
    case_id: str
    consorcio_id: str
    consorcio_name: str
    period: str
    source_files: tuple[str, ...] = ()
    requested_review: str | None = None
    case_status: str = "OPEN"
    collection_aging_bindings: dict[str, str] = field(default_factory=dict)
    expense_variance_bindings: dict[str, str] = field(default_factory=dict)


@dataclass
class AssistedWebSessionV1:
    ingestion_output: dict[str, Any] | None = None
    semantic_questions: list[dict[str, Any]] = field(default_factory=list)
    semantic_answers: dict[str, Any] = field(default_factory=dict)
    semantic_scope_answers: dict[str, Any] = field(default_factory=dict)
    semantic_confirmed_roles: dict[str, str] = field(default_factory=dict)
    semantic_assistance_state: dict[str, Any] | None = None
    owner_unit_confirmation_events: list[dict[str, Any]] = field(default_factory=list)
    tenant_id: str | None = None
    cliente_id: str | None = None
    owner_actor_id: str | None = None
    owner_actor_role: str | None = None
    tenant_identity_contract: object | None = None
    reconciliation_type: str | None = None
    reconciliation_intakes: dict[str, dict[str, Any]] = field(default_factory=dict)
    reconciliation_result: dict[str, Any] | None = None
    reconciliation_decisions: list[dict[str, Any]] = field(default_factory=list)
    consorcio_case_context: ConsorcioCaseContextV1 | None = None
    consorcios_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    consorcios_radar_events: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    selected_launch_review: str | None = None
    last_review_result: dict[str, Any] | None = None


class AssistedWebApplicationV1:
    """Small in-memory coordinator. It never stores uploaded workbook bytes."""

    def __init__(
        self,
        *,
        output_dir: str | Path | None = None,
        persist_tenant_confirmation: Callable[[Any, Any], object] | None = None,
        load_tenant_memory: Callable[[str], tuple[dict[str, object], ...]] | None = None,
        load_prior_semantic_contract: Callable[[str, str, str, str, str], object | None] | None = None,
        load_persisted_cases: Callable[[str], tuple[dict[str, object], ...]] | None = None,
        load_persisted_case: Callable[[str, str], dict[str, object] | None] | None = None,
        require_tenant_persistence: bool = False,
        radar_policy_store: object | None = None,
        semantic_provider: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        if require_tenant_persistence and persist_tenant_confirmation is None:
            raise ValueError("tenant persistence adapter is required")
        self._sessions: dict[str, AssistedWebSessionV1] = {}
        self._session_locks: dict[str, threading.RLock] = {}
        self._session_locks_guard = threading.Lock()
        self._case_snapshots: dict[str, dict[str, dict[str, Any]]] = {}
        self._persist_tenant_confirmation = persist_tenant_confirmation
        self._load_tenant_memory = load_tenant_memory
        self._load_prior_semantic_contract = load_prior_semantic_contract
        self._load_persisted_cases = load_persisted_cases
        self._load_persisted_case = load_persisted_case
        self._require_tenant_persistence = require_tenant_persistence
        self._radar_policy_store = radar_policy_store
        self._semantic_provider = semantic_provider or build_service_1_deterministic_semantic_proposal_v1
        self.output_dir = Path(output_dir) if output_dir is not None else Path(tempfile.mkdtemp(prefix="pymia-service-1-web-"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def session(self, session_id: str) -> AssistedWebSessionV1:
        with self._session_locks_guard:
            return self._sessions.setdefault(session_id, AssistedWebSessionV1())

    def session_lock(self, session_id: str) -> threading.RLock:
        with self._session_locks_guard:
            return self._session_locks.setdefault(session_id, threading.RLock())

    def _case_scope(self, *, session_id: str) -> str:
        state = self.session(session_id)
        tenant = str(state.tenant_id or "").strip()
        return f"tenant:{tenant}" if tenant else f"session:{session_id}"

    def _remember_case(
        self,
        *,
        session_id: str,
        case_id: str,
        service_ref: str,
        service_name: str,
        status: str,
        kind: str,
        packet: dict[str, Any],
        ingestion_output: dict[str, Any] | None = None,
    ) -> None:
        normalized_case = str(case_id or "").strip()
        if not normalized_case:
            return
        scope = self._case_scope(session_id=session_id)
        case_ref = f"{normalized_case}::{str(service_ref or kind or 'control').strip()}"
        self._case_snapshots.setdefault(scope, {})[case_ref] = {
            "case_ref": case_ref,
            "case_id": normalized_case,
            "service_ref": str(service_ref or "").strip(),
            "service_name": str(service_name or service_ref or "Control").strip(),
            "status": str(status or "LISTO").strip(),
            "kind": str(kind or "review").strip(),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "packet": deepcopy(packet),
            "ingestion_output": deepcopy(ingestion_output) if isinstance(ingestion_output, dict) else None,
        }

    def recent_cases(self, *, session_id: str) -> tuple[int, str]:
        scope = self._case_scope(session_id=session_id)
        snapshots = list(self._case_snapshots.get(scope, {}).values())
        state = self.session(session_id)
        tenant = str(state.tenant_id or "").strip()
        if tenant and self._load_persisted_cases is not None:
            try:
                persisted = self._load_persisted_cases(tenant)
            except Exception:
                if self._require_tenant_persistence:
                    return HTTPStatus.BAD_REQUEST, _error_page(
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
        snapshots.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        return HTTPStatus.OK, _recent_cases_page(snapshots)

    def open_case(self, *, session_id: str, case_ref: str) -> tuple[int, str]:
        normalized_ref = str(case_ref or "").strip()
        scope = self._case_scope(session_id=session_id)
        scoped = self._case_snapshots.get(scope, {})
        snapshot = scoped.get(normalized_ref)
        if snapshot is None and normalized_ref:
            snapshot = next(
                (
                    item
                    for item in scoped.values()
                    if str(item.get("case_id") or "").strip() == normalized_ref
                ),
                None,
            )
        if snapshot is not None:
            packet = snapshot.get("packet")
            packet = packet if isinstance(packet, dict) else {}
            if snapshot.get("kind") == "reconciliation":
                return HTTPStatus.OK, _reconciliation_result_page(packet)
            if snapshot.get("kind") == "working_capital":
                return HTTPStatus.OK, _working_capital_result_page(packet)
            service_ref = str(snapshot.get("service_ref") or "")
            ingestion_output = snapshot.get("ingestion_output")
            return HTTPStatus.OK, _evaluated_result_page(
                packet,
                service_ref,
                ingestion_output=ingestion_output if isinstance(ingestion_output, dict) else {},
            )

        state = self.session(session_id)
        tenant = str(state.tenant_id or "").strip()
        if tenant and normalized_ref and self._load_persisted_case is not None:
            try:
                persisted_case = self._load_persisted_case(tenant, normalized_ref)
            except Exception:
                if self._require_tenant_persistence:
                    return HTTPStatus.BAD_REQUEST, _error_page(
                        "No pudimos recuperar el caso persistido del tenant."
                    )
                persisted_case = None
            if isinstance(persisted_case, dict):
                return HTTPStatus.OK, _persisted_case_page(persisted_case)
        return HTTPStatus.NOT_FOUND, _error_page("No encontramos ese caso para este tenant.")

    def bind_tenant_identity(
        self,
        *,
        session_id: str,
        tenant_id: str,
        owner_actor_id: str,
        owner_actor_role: str,
        cliente_id: str | None = None,
    ) -> None:
        tenant = str(tenant_id or "").strip()
        actor = str(owner_actor_id or "").strip()
        role = str(owner_actor_role or "").strip()
        if not tenant or not actor or not role:
            raise ValueError("tenant_id, owner_actor_id and owner_actor_role are required")
        state = self.session(session_id)
        client = str(cliente_id).strip() if cliente_id else None
        identity_changed = (
            state.tenant_id != tenant
            or state.cliente_id != client
            or state.owner_actor_id != actor
            or state.owner_actor_role != role
        )
        state.tenant_id = tenant
        state.cliente_id = client
        state.owner_actor_id = actor
        state.owner_actor_role = role
        if identity_changed:
            state.tenant_identity_contract = None

    def radar_owner_menu(self, *, session_id: str) -> tuple[int, str]:
        state = self.session(session_id)
        if state.tenant_identity_contract is None:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado antes de configurar RADAR."
            )
        if self._radar_policy_store is None:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "RADAR todavía no está habilitado en este entorno."
            )
        menu = build_consorcios_radar_owner_menu_v1(
            identity_contract=state.tenant_identity_contract
        )
        return HTTPStatus.OK, _radar_owner_policy_page(menu)

    def save_radar_owner_policy(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if state.tenant_identity_contract is None:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado antes de configurar RADAR."
            )
        if self._radar_policy_store is None:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "RADAR todavía no está habilitado en este entorno."
            )
        comparison_raw = fields.get("comparison_value", "").strip()
        if comparison_raw.lower() in {"true", "false"}:
            comparison_value: str | bool = comparison_raw.lower() == "true"
        else:
            comparison_value = comparison_raw
        try:
            policy = persist_consorcios_radar_owner_policy_v1(
                identity_contract=state.tenant_identity_contract,
                owner_request={
                    "policy_ref": fields.get("policy_ref", "").strip(),
                    "observable_ref": fields.get("observable_ref", "").strip(),
                    "enabled": fields.get("enabled") == "true",
                    "operator": fields.get("operator", "").strip(),
                    "comparison_value": comparison_value,
                    "communication_level": fields.get("communication_level", "").strip(),
                    "confirmed_by_owner": fields.get("confirmed_by_owner") == "true",
                },
                policy_store=self._radar_policy_store,
            )
        except ValueError as exc:
            menu = build_consorcios_radar_owner_menu_v1(
                identity_contract=state.tenant_identity_contract
            )
            return HTTPStatus.BAD_REQUEST, _radar_owner_policy_page(
                menu,
                error=str(exc),
            )
        return HTTPStatus.OK, _radar_owner_policy_saved_page(policy)

    def consorcios_case_workspace(self, *, session_id: str) -> tuple[int, str]:
        state = self.session(session_id)
        if state.tenant_identity_contract is None or not state.ingestion_output or state.consorcio_case_context is None:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado de Consorcios."
            )
        tables = _canonical_tables_for_consorcios(state.ingestion_output)
        if not tables:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "El archivo cargado no tiene tablas utilizables para Consorcios."
            )
        return HTTPStatus.OK, _consorcios_case_workspace_page(
            state.consorcio_case_context,
            tables,
        )

    def consorcios_case_summary(self, *, session_id: str) -> tuple[int, str]:
        state = self.session(session_id)
        context = state.consorcio_case_context
        if state.tenant_identity_contract is None or context is None:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado de Consorcios."
            )
        bank_radar_events: list[dict[str, object]] = []
        if isinstance(state.reconciliation_result, dict):
            bank_radar_events = self._radar_events_for_bank_reconciliation(
                state=state,
                packet=state.reconciliation_result,
            )
        radar_events = [
            event
            for events in state.consorcios_radar_events.values()
            for event in events
        ] + bank_radar_events
        return HTTPStatus.OK, _consorcios_case_summary_page(
            context=context,
            results=state.consorcios_results,
            reconciliation_result=state.reconciliation_result,
            reconciliation_decisions=state.reconciliation_decisions,
            radar_events=radar_events,
        )

    def consorcios_radar_analysis_menu(self, *, session_id: str) -> tuple[int, str]:
        state = self.session(session_id)
        if state.tenant_identity_contract is None or not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado de Consorcios."
            )
        tables = _canonical_tables_for_consorcios(state.ingestion_output)
        if not tables:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "El archivo cargado no tiene tablas utilizables para Consorcios."
            )
        return HTTPStatus.OK, _consorcios_radar_analysis_page(tables)

    def run_consorcios_collection_aging(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if state.tenant_identity_contract is None or not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado de Consorcios."
            )
        tables = _canonical_tables_for_consorcios(state.ingestion_output)
        context = state.consorcio_case_context
        saved = context.collection_aging_bindings if context is not None else {}
        effective = {
            "sheet_name": fields.get("sheet_name", "").strip() or saved.get("sheet_name", ""),
            "unidad_funcional": fields.get("unidad_funcional", "").strip() or saved.get("unidad_funcional", ""),
            "saldo_anterior": fields.get("saldo_anterior", "").strip() or saved.get("saldo_anterior", ""),
            "expensa_mes": fields.get("expensa_mes", "").strip() or saved.get("expensa_mes", ""),
        }
        try:
            table = _selected_consorcios_table(tables, effective["sheet_name"])
            bindings = {
                "unidad_funcional": _selected_consorcios_column(table, effective["unidad_funcional"]),
                "saldo_anterior": _selected_consorcios_column(table, effective["saldo_anterior"]),
                "expensa_mes": _selected_consorcios_column(table, effective["expensa_mes"]),
            }
        except ValueError as exc:
            return HTTPStatus.BAD_REQUEST, _consorcios_case_workspace_page(
                context, tables, error=str(exc)
            ) if context is not None else _consorcios_radar_analysis_page(tables, error=str(exc))
        if context is not None:
            context.collection_aging_bindings = {
                "sheet_name": str(table.get("sheet_name") or ""),
                **bindings,
            }
        approved = list(dict.fromkeys(bindings.values()))
        request = {
            "owner_requested": True,
            "case_id": str(getattr(state.tenant_identity_contract, "case_id", "") or ""),
            "sheet_name": str(table.get("sheet_name") or "Expensas"),
            "rows": list(table.get("rows") or []),
            "field_bindings": bindings,
            "governance": _consorcios_owner_governance(approved),
        }
        packet = run_service_1_product_pipeline_v1(
            ingestion_output=None,
            tool_requests=[],
            output_dir=self._review_output_dir(session_id=session_id),
            collection_aging_request=request,
        )
        if packet.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_message_page(
                "No se pudo calcular la antigüedad de deuda con las columnas confirmadas."
            )
        computation = packet.get("computation_result")
        computation = computation if isinstance(computation, dict) else {}
        try:
            observations = project_collection_aging_to_radar_v1(
                computation_result=computation
            )
            radar_events = self._radar_events_for_observations(
                state=state,
                observations=observations,
            )
        except ValueError:
            radar_events = []
        state.consorcios_results["collection_aging"] = computation
        state.consorcios_radar_events["collection_aging"] = radar_events
        state.last_review_result = packet
        return HTTPStatus.OK, _consorcios_collection_aging_result_page(
            computation,
            radar_events=radar_events,
        )

    def run_consorcios_expense_variance(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if state.tenant_identity_contract is None or not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero cargá un caso identificado de Consorcios."
            )
        tables = _canonical_tables_for_consorcios(state.ingestion_output)
        context = state.consorcio_case_context
        saved = context.expense_variance_bindings if context is not None else {}
        effective = {
            "expense_sheet": fields.get("expense_sheet", "").strip() or saved.get("expense_sheet", ""),
            "expense_rubro": fields.get("expense_rubro", "").strip() or saved.get("expense_rubro", ""),
            "expense_importe": fields.get("expense_importe", "").strip() or saved.get("expense_importe", ""),
            "budget_sheet": fields.get("budget_sheet", "").strip() or saved.get("budget_sheet", ""),
            "budget_rubro": fields.get("budget_rubro", "").strip() or saved.get("budget_rubro", ""),
            "presupuesto_mensual": fields.get("presupuesto_mensual", "").strip() or saved.get("presupuesto_mensual", ""),
            "promedio_historico": fields.get("promedio_historico", "").strip() or saved.get("promedio_historico", ""),
        }
        try:
            expense_table = _selected_consorcios_table(tables, effective["expense_sheet"])
            budget_table = _selected_consorcios_table(tables, effective["budget_sheet"])
            expense_bindings = {
                "rubro": _selected_consorcios_column(expense_table, effective["expense_rubro"]),
                "importe": _selected_consorcios_column(expense_table, effective["expense_importe"]),
            }
            budget_bindings = {
                "rubro": _selected_consorcios_column(budget_table, effective["budget_rubro"]),
                "presupuesto_mensual": _selected_consorcios_column(
                    budget_table, effective["presupuesto_mensual"]
                ),
                "promedio_historico": _selected_consorcios_column(
                    budget_table, effective["promedio_historico"]
                ),
            }
        except ValueError as exc:
            return HTTPStatus.BAD_REQUEST, _consorcios_case_workspace_page(
                context, tables, error=str(exc)
            ) if context is not None else _consorcios_radar_analysis_page(tables, error=str(exc))
        if context is not None:
            context.expense_variance_bindings = {
                "expense_sheet": str(expense_table.get("sheet_name") or ""),
                "expense_rubro": expense_bindings["rubro"],
                "expense_importe": expense_bindings["importe"],
                "budget_sheet": str(budget_table.get("sheet_name") or ""),
                "budget_rubro": budget_bindings["rubro"],
                "presupuesto_mensual": budget_bindings["presupuesto_mensual"],
                "promedio_historico": budget_bindings["promedio_historico"],
            }
        approved = list(
            dict.fromkeys([*expense_bindings.values(), *budget_bindings.values()])
        )
        request = {
            "owner_requested": True,
            "case_id": str(getattr(state.tenant_identity_contract, "case_id", "") or ""),
            "expense_rows": list(expense_table.get("rows") or []),
            "budget_rows": list(budget_table.get("rows") or []),
            "expense_bindings": expense_bindings,
            "budget_bindings": budget_bindings,
            "governance": _consorcios_owner_governance(approved),
        }
        packet = run_service_1_product_pipeline_v1(
            ingestion_output=None,
            tool_requests=[],
            output_dir=self._review_output_dir(session_id=session_id),
            expense_variance_request=request,
        )
        if packet.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_message_page(
                "No se pudo comparar gastos con presupuesto e histórico usando las columnas confirmadas."
            )
        computation = packet.get("computation_result")
        computation = computation if isinstance(computation, dict) else {}
        try:
            observations = project_expense_variance_to_radar_v1(
                computation_result=computation
            )
            radar_events = self._radar_events_for_observations(
                state=state,
                observations=observations,
            )
        except ValueError:
            radar_events = []
        state.consorcios_results["expense_variance"] = computation
        state.consorcios_radar_events["expense_variance"] = radar_events
        state.last_review_result = packet
        return HTTPStatus.OK, _consorcios_expense_variance_result_page(
            computation,
            radar_events=radar_events,
        )

    def _radar_events_for_observations(
        self,
        *,
        state: AssistedWebSessionV1,
        observations: object,
    ) -> list[dict[str, object]]:
        if self._radar_policy_store is None or state.tenant_identity_contract is None:
            return []
        rendered: list[dict[str, object]] = []
        for observation in observations if isinstance(observations, tuple) else tuple(observations or ()):
            events = evaluate_consorcios_radar_observation_with_owner_policy_v1(
                identity_contract=state.tenant_identity_contract,
                observation=observation,
                policy_store=self._radar_policy_store,
            )
            for event in events:
                payload = event.to_dict()
                payload["entity_ref"] = observation.entity_ref
                rendered.append(payload)
        return rendered

    def bind_consorcio_case_context(
        self,
        *,
        session_id: str,
        case_id: str,
        consorcio_id: str,
        consorcio_name: str,
        period: str,
        source_files: tuple[str, ...],
    ) -> None:
        normalized_case = str(case_id or "").strip()
        normalized_consorcio = str(consorcio_id or "").strip()
        normalized_name = str(consorcio_name or "").strip()
        normalized_period = str(period or "").strip()
        if not normalized_case or not normalized_consorcio or not normalized_name or not normalized_period:
            raise ValueError("case_id, consorcio_id, consorcio_name and period are required")
        try:
            datetime.strptime(normalized_period, "%Y-%m")
        except ValueError as error:
            raise ValueError("period must use YYYY-MM") from error
        files = tuple(str(item).strip() for item in source_files if str(item).strip())
        if not files:
            raise ValueError("at least one source file is required")
        state = self.session(session_id)
        state.consorcio_case_context = ConsorcioCaseContextV1(
            case_id=normalized_case,
            consorcio_id=normalized_consorcio,
            consorcio_name=normalized_name,
            period=normalized_period,
            source_files=files,
        )
        state.consorcios_results = {}
        state.consorcios_radar_events = {}
        state.reconciliation_type = None
        state.reconciliation_intakes = {}
        state.reconciliation_result = None
        state.reconciliation_decisions = []

    def _review_output_dir(self, *, session_id: str) -> Path:
        state = self.session(session_id)
        context = state.consorcio_case_context
        if context is None:
            return self.output_dir
        parts = (
            state.tenant_id or "unbound-tenant",
            context.consorcio_id,
            context.period,
            context.case_id,
        )
        safe_parts = tuple(_safe_path_segment(part) for part in parts)
        target = self.output_dir.joinpath("cases", *safe_parts)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def start_reconciliation(self, *, session_id: str, reconciliation_type: str) -> tuple[int, str]:
        if reconciliation_type not in _RECONCILIATION_BY_TYPE:
            return HTTPStatus.BAD_REQUEST, _home_page("Elegí un tipo de conciliación disponible.")
        state = self.session(session_id)
        state.reconciliation_type = reconciliation_type
        state.reconciliation_intakes = {}
        state.reconciliation_result = None
        state.reconciliation_decisions = []
        return HTTPStatus.OK, _reconciliation_upload_page(reconciliation_type)

    def receive_reconciliation_sources(
        self,
        *,
        session_id: str,
        files: dict[str, tuple[str, bytes]],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        reconciliation_type = state.reconciliation_type
        if reconciliation_type not in _RECONCILIATION_SOURCES:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero elegí qué conciliación querés hacer.")

        intakes: dict[str, dict[str, Any]] = {}
        for source_kind, source_label, _ in _RECONCILIATION_SOURCES[reconciliation_type]:
            filename, content = files.get(f"source_{source_kind}", ("", b""))
            if not filename:
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"Falta el archivo: {source_label}.",
                )
            if not filename.lower().endswith(".xlsx"):
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"{source_label}: solo se aceptan archivos .xlsx.",
                )
            intake = build_service_1_web_column_confirmation_intake_boundary_v1(
                uploaded_xlsx_bytes=content,
                uploaded_filename=filename,
            )
            if intake.get("status") == "BLOCKED":
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"No se pudo leer {source_label}. Revisá el archivo.",
                )
            intakes[source_kind] = intake

        state.reconciliation_intakes = intakes
        state.reconciliation_result = None
        state.reconciliation_decisions = []
        return HTTPStatus.OK, _reconciliation_column_confirmation_page(
            reconciliation_type,
            intakes,
        )

    def confirm_reconciliation_columns(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        reconciliation_type = state.reconciliation_type
        intakes = state.reconciliation_intakes
        if reconciliation_type not in _RECONCILIATION_SOURCES or not intakes:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero subí los dos archivos de conciliación.")

        source_packets: list[dict[str, Any]] = []
        case_parts: list[str] = []
        for source_kind, source_label, field_specs in _RECONCILIATION_SOURCES[reconciliation_type]:
            intake = intakes.get(source_kind)
            if not isinstance(intake, dict):
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"Falta el archivo: {source_label}.",
                )
            available_columns = {str(item) for item in intake.get("columns") or []}
            bindings = {
                canonical_field: fields.get(
                    f"bind_{source_kind}_{canonical_field}", ""
                ).strip()
                for canonical_field, _ in field_specs
            }
            if any(not column for column in bindings.values()):
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "Confirmá todas las columnas necesarias para continuar.",
                )
            if any(column not in available_columns for column in bindings.values()):
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "Una de las columnas elegidas ya no coincide con el archivo recibido.",
                )
            if len(set(bindings.values())) != len(bindings):
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "No uses la misma columna para representar dos datos distintos.",
                )

            normalized = intake.get("normalized_table")
            if not isinstance(normalized, dict):
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"No se pudo preparar {source_label} para conciliación.",
                )
            rows = normalized.get("rows")
            if not isinstance(rows, list) or not rows:
                return HTTPStatus.BAD_REQUEST, _reconciliation_upload_page(
                    reconciliation_type,
                    f"{source_label} no contiene movimientos para revisar.",
                )

            normalized_bindings = _normalized_reconciliation_bindings(
                intake=intake,
                visible_bindings=bindings,
            )
            if normalized_bindings is None:
                return HTTPStatus.BAD_REQUEST, _reconciliation_column_confirmation_page(
                    reconciliation_type,
                    intakes,
                    "No se pudo conservar la relación entre una columna visible y su clave interna.",
                )

            approved_columns = list(dict.fromkeys(normalized_bindings.values()))
            source_packets.append(
                {
                    "source_kind": source_kind,
                    "source_ref": str(intake.get("filename") or source_label),
                    "rows": _prepare_reconciliation_rows(
                        rows=rows,
                        bindings=normalized_bindings,
                        reconciliation_type=reconciliation_type,
                        source_kind=source_kind,
                    ),
                    "field_bindings": normalized_bindings,
                    "visible_field_bindings": bindings,
                    "governance": {
                        "p5_status": "CONFIRMED",
                        "p6_decisions": [
                            {"column_ref": column, "status": "APPROVED"}
                            for column in approved_columns
                        ],
                        "p7_status": "REQUIREMENT_MATCHED",
                        "p8_status": "COMPUTABLE",
                        "runtime_authorized": False,
                        "tool_execution_authorized": False,
                        "product_ready": False,
                        "delivery_authorized": False,
                        "diagnosis_generated": False,
                    },
                }
            )
            case_parts.append(str(intake.get("case_id") or source_kind)[-10:])

        packet = run_service_1_product_pipeline_v1(
            ingestion_output=None,
            tool_requests=[],
            output_dir=self.output_dir,
            reconciliation_request={
                "case_id": "web_reconciliation_" + "_".join(case_parts),
                "owner_requested": True,
                "reconciliation_type": reconciliation_type,
                "source_packets": source_packets,
            },
        )
        state.reconciliation_result = packet
        state.reconciliation_decisions = []
        if packet.get("status") == STATUS_RECONCILIATION_NEEDS_OWNER:
            return HTTPStatus.OK, _reconciliation_column_confirmation_page(
                reconciliation_type,
                intakes,
                "Hace falta volver a confirmar el significado de las columnas.",
            )
        if packet.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_message_page(
                "No se pudo preparar la conciliación con estos datos. Revisá los archivos y las columnas elegidas."
            )
        if packet.get("status") == STATUS_RECONCILIATION_REVIEW_READY:
            radar_events = self._radar_events_for_bank_reconciliation(
                state=state, packet=packet
            )
            reconciliation_run = packet.get("reconciliation_run")
            run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
            service_name = _RECONCILIATION_BY_TYPE.get(
                reconciliation_type, ("", "Conciliación", "")
            )[1]
            self._remember_case(
                session_id=session_id,
                case_id=str(run.get("case_id") or ""),
                service_ref=reconciliation_type,
                service_name=service_name,
                status="REQUIERE REVISIÓN",
                kind="reconciliation",
                packet=packet,
            )
            return HTTPStatus.OK, _reconciliation_result_page(
                packet, radar_events=radar_events
            )
        if packet.get("status") == STATUS_RECONCILIATION_NEEDS_EVIDENCE:
            reconciliation_run = packet.get("reconciliation_run")
            assisted_review = (
                reconciliation_run.get("assisted_review")
                if isinstance(reconciliation_run, dict)
                else None
            )
            if isinstance(assisted_review, dict):
                radar_events = self._radar_events_for_bank_reconciliation(
                    state=state, packet=packet
                )
                return HTTPStatus.OK, _reconciliation_result_page(
                    packet, radar_events=radar_events
                )
            return HTTPStatus.OK, _blocked_message_page(
                "Faltan columnas o datos obligatorios para preparar la conciliación. "
                "Revisá los archivos y las columnas elegidas."
            )
        return HTTPStatus.OK, _blocked_message_page(
            "La conciliación quedó en un estado que necesita revisión antes de continuar."
        )

    def _radar_events_for_bank_reconciliation(
        self,
        *,
        state: AssistedWebSessionV1,
        packet: dict[str, Any],
    ) -> list[dict[str, object]]:
        if self._radar_policy_store is None or state.tenant_identity_contract is None:
            return []
        reconciliation_run = packet.get("reconciliation_run")
        run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
        if str(run.get("reconciliation_type") or "") != BANK_RECONCILIATION:
            return []
        assisted_raw = run.get("assisted_review")
        assisted = assisted_raw if isinstance(assisted_raw, dict) else {}
        review_raw = assisted.get("review_result")
        review = review_raw if isinstance(review_raw, dict) else {}
        source_raw = review.get("source_result")
        source_result = source_raw if isinstance(source_raw, dict) else review
        try:
            observations = project_bank_reconciliation_to_radar_v1(
                reconciliation_result=source_result
            )
        except ValueError:
            return []

        rendered: list[dict[str, object]] = []
        for observation in observations:
            events = evaluate_consorcios_radar_observation_with_owner_policy_v1(
                identity_contract=state.tenant_identity_contract,
                observation=observation,
                policy_store=self._radar_policy_store,
            )
            for event in events:
                payload = event.to_dict()
                payload["entity_ref"] = observation.entity_ref
                rendered.append(payload)
        return rendered

    def decide_reconciliation_item(
        self,
        *,
        session_id: str,
        review_item_ref: str,
        decision: str,
        reviewed_by: str,
        observation: str,
    ) -> tuple[int, str]:
        state = self.session(session_id)
        packet = state.reconciliation_result
        if not isinstance(packet, dict):
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Primero ejecutá una conciliación para revisar sus casos."
            )
        chosen = str(decision or "").strip().upper()
        reviewer = str(reviewed_by or "").strip()
        if chosen not in ALLOWED_RECONCILIATION_DECISIONS:
            return HTTPStatus.BAD_REQUEST, _reconciliation_result_page(
                packet,
                decisions=state.reconciliation_decisions,
                error="Elegí Confirmar, Rechazar o Dejar pendiente.",
            )
        if not reviewer:
            return HTTPStatus.BAD_REQUEST, _reconciliation_result_page(
                packet,
                decisions=state.reconciliation_decisions,
                error="Indicá quién realizó la revisión.",
            )
        item_index = _reconciliation_review_item_index(packet)
        selected = item_index.get(str(review_item_ref or "").strip())
        if selected is None:
            return HTTPStatus.BAD_REQUEST, _reconciliation_result_page(
                packet,
                decisions=state.reconciliation_decisions,
                error="Ese caso ya no pertenece a la conciliación actual.",
            )
        reconciliation_run = packet.get("reconciliation_run")
        run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
        record = build_reconciliation_human_review_decision_v1(
            case_id=str(run.get("case_id") or ""),
            reconciliation_type=str(run.get("reconciliation_type") or ""),
            review_item_ref=str(review_item_ref),
            review_category=str(selected["category"]),
            review_item=selected["item"],
            decision=chosen,
            reviewed_by=reviewer,
            observation=observation,
        )
        state.reconciliation_decisions.append(record)
        _append_reconciliation_decision_jsonl(self.output_dir, record)
        return HTTPStatus.OK, _reconciliation_result_page(
            packet,
            decisions=state.reconciliation_decisions,
            notice="Decisión humana registrada. Los movimientos originales no fueron modificados.",
        )

    def build_reconciliation_workpaper(
        self,
        *,
        session_id: str,
    ) -> dict[str, Any]:
        state = self.session(session_id)
        packet = state.reconciliation_result
        if not isinstance(packet, dict):
            raise ValueError("reconciliation result is required")
        return build_service_1_reconciliation_workpaper_xlsx_v1(
            reconciliation_packet=packet,
            human_decisions=state.reconciliation_decisions,
        )

    def receive_xlsx(
        self,
        *,
        session_id: str,
        filename: str,
        content: bytes,
        selected_launch_review: str | None = None,
    ) -> tuple[int, str]:
        if selected_launch_review is not None and selected_launch_review not in {
            "sold_vs_collected_gap",
            "net_margin_real",
            "working_capital",
        }:
            return HTTPStatus.BAD_REQUEST, _error_page("Elegí un servicio disponible.")
        if not filename:
            return HTTPStatus.BAD_REQUEST, _error_page("Elegí un archivo de Excel para continuar.")
        if not filename.lower().endswith(".xlsx"):
            return HTTPStatus.BAD_REQUEST, _error_page("Solo se pueden subir archivos .xlsx.")
        intake = build_service_1_web_column_confirmation_intake_boundary_v1(
            uploaded_xlsx_bytes=content,
            uploaded_filename=filename,
            include_all_sheets=True,
        )
        if intake.get("status") == "BLOCKED":
            return HTTPStatus.BAD_REQUEST, _error_page("No se pudo usar el archivo. Revisá que sea un Excel .xlsx válido.")
        canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
            owner_question_packet=intake,
        )
        if canonical.get("status") != CANONICAL_UNCONFIRMED_READY:
            return HTTPStatus.BAD_REQUEST, _error_page(
                "No se pudo preparar la lectura del archivo."
            )

        state = self.session(session_id)
        if self._require_tenant_persistence and (
            not state.tenant_id
            or not state.owner_actor_id
            or not state.owner_actor_role
        ):
            return HTTPStatus.BAD_REQUEST, _error_page(
                "Falta identificar el tenant y a la persona que confirma antes de procesar el archivo."
            )

        state.ingestion_output = canonical["ingestion_output"]
        state.semantic_questions = []
        state.semantic_answers = {}
        state.semantic_scope_answers = {}
        state.semantic_confirmed_roles = {}
        state.semantic_assistance_state = None
        state.owner_unit_confirmation_events = []
        state.selected_launch_review = selected_launch_review
        state.last_review_result = None
        state.tenant_identity_contract = None

        if state.tenant_id and state.owner_actor_id and state.owner_actor_role:
            case_id = str(
                state.ingestion_output.get("case_id")
                or intake.get("case_id")
                or ""
            ).strip()
            source_system_ref = str(intake.get("source_kind") or "").strip()
            source_context_ref = str(intake.get("schema_version") or "").strip()
            workbook_ref = str(intake.get("filename") or filename).strip()
            try:
                state.tenant_identity_contract = build_service_1_assisted_web_tenant_identity_v1(
                    tenant_id=state.tenant_id,
                    cliente_id=state.cliente_id,
                    case_id=case_id,
                    owner_actor_id=state.owner_actor_id,
                    owner_actor_role=state.owner_actor_role,
                    source_system_ref=source_system_ref,
                    source_context_ref=source_context_ref,
                    workbook_ref=workbook_ref,
                )
            except ValueError:
                return HTTPStatus.BAD_REQUEST, _error_page(
                    "No se pudo establecer una identidad válida para este caso."
                )

        assisted_launch = state.selected_launch_review in {"sold_vs_collected_gap", "net_margin_real", "working_capital"}
        try:
            if assisted_launch:
                first_run = _run_product_root(
                    ingestion_output=state.ingestion_output,
                    requested_capability=state.selected_launch_review,
                    output_dir=self.output_dir,
                    semantic_provider=self._semantic_provider,
                    compatible_tenant_memory_hints=self._compatible_tenant_memory_hints(state),
                    semantic_scope_capabilities=(
                        _WORKING_CAPITAL_COMPONENT_CAPABILITIES
                        if state.selected_launch_review == "working_capital"
                        else ()
                    ),
                    use_assisted_semantics=True,
                )
            else:
                first_run = _run_product_root(
                    ingestion_output=state.ingestion_output,
                    output_dir=self.output_dir,
                )
        except ValueError as error:
            if "requires at least one tool request" in str(error):
                return HTTPStatus.OK, _review_selection_page()
            raise
        if first_run.get("status") == STATUS_NEEDS_OWNER:
            if assisted_launch:
                assistance_state = first_run.get("semantic_assistance_state")
                if not isinstance(assistance_state, dict):
                    return HTTPStatus.OK, _blocked_message_page(
                        "La interpretación asistida no produjo un estado trazable para confirmar."
                    )
                state.semantic_assistance_state = assistance_state
                state.semantic_questions = list(first_run.get("owner_questions") or [])
                return HTTPStatus.OK, _assisted_semantic_dialogue_page(state.semantic_questions)
            scoped_questions, scope_answers = _scope_owner_questions_for_launch_review(
                first_run,
                state.selected_launch_review,
            )
            state.semantic_scope_answers = scope_answers
            state.semantic_questions = scoped_questions
            state.semantic_questions = self._with_tenant_memory_hints(state)
            if not state.semantic_questions and state.selected_launch_review in _LAUNCH_REVIEW_BY_REF:
                state.semantic_answers = dict(state.semantic_scope_answers)
                return self.run_review(
                    session_id=session_id,
                    requested_capability=state.selected_launch_review,
                )
            return HTTPStatus.OK, _semantic_questions_page(state.semantic_questions)
        if first_run.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_result_page(first_run, state.selected_launch_review)
        return HTTPStatus.OK, _review_selection_page()

    def _compatible_tenant_memory_hints(
        self,
        state: AssistedWebSessionV1,
    ) -> tuple[dict[str, Any], ...]:
        if (
            self._load_tenant_memory is None
            or not state.tenant_id
            or not isinstance(state.ingestion_output, dict)
            or state.tenant_identity_contract is None
        ):
            return ()
        try:
            memory_rows = self._load_tenant_memory(state.tenant_id)
            profile = build_service_1_workbook_profile_v1(
                ingestion_output=state.ingestion_output
            )
        except Exception:
            return ()
        if profile.get("status") != WORKBOOK_PROFILE_READY:
            return ()
        source_system_ref = str(
            getattr(state.tenant_identity_contract, "source_system_ref", "") or ""
        ).strip()
        source_context_ref = str(
            getattr(state.tenant_identity_contract, "source_context_ref", "") or ""
        ).strip()
        selection = select_service_1_compatible_tenant_memory_hints_v1(
            tenant_id=state.tenant_id,
            source_system_ref=source_system_ref,
            source_context_ref=source_context_ref,
            workbook_profile=profile,
            memory_rows=tuple(item for item in memory_rows if isinstance(item, Mapping)),
        )
        if selection.get("status") != STRUCTURAL_MEMORY_READY:
            return ()
        return tuple(
            dict(item)
            for item in (selection.get("compatible_hints") or [])
            if isinstance(item, Mapping)
        )

    def _with_tenant_memory_hints(
        self,
        state: AssistedWebSessionV1,
    ) -> list[dict[str, Any]]:
        if self._load_tenant_memory is None or not state.tenant_id:
            return list(state.semantic_questions)
        try:
            memory_rows = self._load_tenant_memory(state.tenant_id)
        except Exception:
            return list(state.semantic_questions)
        latest_by_column: dict[tuple[str, str], dict[str, object]] = {}
        for raw in memory_rows:
            if not isinstance(raw, dict):
                continue
            sheet = str(raw.get("sheet_ref") or "").strip()
            column = str(raw.get("column_ref") or "").strip()
            if sheet and column:
                latest_by_column.setdefault((sheet, column), raw)

        enriched: list[dict[str, Any]] = []
        for question in state.semantic_questions:
            item = dict(question)
            key = (
                str(item.get("sheet_name") or "").strip(),
                str(item.get("column_name") or "").strip(),
            )
            previous = latest_by_column.get(key)
            if previous is not None:
                previous_answer = str(previous.get("owner_answer") or "").strip()
                matching_option = next(
                    (
                        option
                        for option in (item.get("options") or [])
                        if isinstance(option, dict)
                        and str(option.get("option_id") or "").strip() == previous_answer
                    ),
                    None,
                )
                if matching_option is not None:
                    label = str(matching_option.get("label") or "").strip()
                    if label:
                        item["tenant_memory_hint"] = label
            enriched.append(item)
        return enriched

    def confirm_meanings(self, *, session_id: str, fields: dict[str, str]) -> tuple[int, str]:
        state = self.session(session_id)
        if not state.ingestion_output or not state.semantic_questions:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero confirmá las columnas del archivo.")
        if state.semantic_assistance_state is not None:
            if any(
                isinstance(item, Mapping) and item.get("question_kind") == "UNIT_MEANING"
                for item in state.semantic_questions
            ):
                return self._confirm_derived_unit_evidence(
                    session_id=session_id,
                    fields=fields,
                )
            return self._confirm_assisted_semantics(
                session_id=session_id,
                fields=fields,
            )
        answers: dict[str, Any] = {}
        confirmed_roles = dict(state.semantic_confirmed_roles)
        unresolved: list[str] = []
        for question in state.semantic_questions:
            question_id = str(question.get("question_id") or "")
            selected = fields.get(f"answer_{question_id}", "").strip()
            if not selected:
                return HTTPStatus.BAD_REQUEST, _semantic_questions_page(
                    state.semantic_questions,
                    "Elegí una respuesta para cada columna.",
                    selected_answers=answers,
                )
            if selected == "not_sure":
                answers[question_id] = selected
                unresolved.append(question_id)
                continue
            if selected == "OTHER":
                free_text = fields.get(f"other_{question_id}", "").strip()
                if not free_text:
                    return HTTPStatus.BAD_REQUEST, _semantic_questions_page(
                        state.semantic_questions,
                        "Explicá qué significa la columna cuando elegís Otra cosa.",
                        selected_answers={**answers, question_id: selected},
                    )
                answers[question_id] = {"option_id": "OTHER", "free_text": free_text}
            else:
                answers[question_id] = selected
                _capture_confirmed_role_v1(
                    confirmed_roles=confirmed_roles,
                    question_id=question_id,
                    selected=selected,
                    question=question,
                )
        if unresolved:
            state.semantic_answers = answers
            state.semantic_confirmed_roles = confirmed_roles
            return HTTPStatus.OK, _semantic_questions_page(
                state.semantic_questions,
                "Todavía hay columnas sin confirmar. Elegí un significado, 'No usar esta columna' o corregí la interpretación para continuar.",
                selected_answers=answers,
            )
        merged_answers = dict(state.semantic_scope_answers)
        merged_answers.update(answers)
        state.semantic_answers = merged_answers
        state.semantic_questions = []
        if state.consorcio_case_context is not None and state.tenant_identity_contract is not None:
            return self.consorcios_case_workspace(session_id=session_id)
        if state.selected_launch_review in _LAUNCH_REVIEW_BY_REF:
            return self.run_review(
                session_id=session_id,
                requested_capability=state.selected_launch_review,
            )
        return HTTPStatus.OK, _review_selection_page()

    def _confirm_assisted_semantics(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if (
            not isinstance(state.semantic_assistance_state, dict)
            or not isinstance(state.ingestion_output, dict)
            or not state.selected_launch_review
        ):
            return HTTPStatus.BAD_REQUEST, _error_page(
                "No hay una interpretación asistida pendiente para confirmar."
            )
        responses: list[dict[str, Any]] = []
        selected: dict[str, str] = {}
        for decision in state.semantic_questions:
            if not isinstance(decision, Mapping):
                continue
            decision_id = str(decision.get("decision_id") or "").strip()
            if not decision_id:
                return HTTPStatus.OK, _blocked_message_page(
                    "La decisión semántica no tiene identidad trazable."
                )
            action = str(fields.get(f"action_{decision_id}") or "").strip().upper()
            if action not in {"ACCEPT", "REJECT", "CORRECT"}:
                return HTTPStatus.BAD_REQUEST, _assisted_semantic_dialogue_page(
                    state.semantic_questions,
                    "Elegí confirmar, rechazar o corregir cada interpretación.",
                    selected_actions=selected,
                )
            selected[decision_id] = action
            response: dict[str, Any] = {
                "decision_id": decision_id,
                "action": action,
            }
            if action == "CORRECT":
                correction = str(fields.get(f"correction_{decision_id}") or "").strip()
                if not correction:
                    return HTTPStatus.BAD_REQUEST, _assisted_semantic_dialogue_page(
                        state.semantic_questions,
                        "Escribí la corrección cuando elegís corregir una interpretación.",
                        selected_actions=selected,
                    )
                response["correction_text"] = correction
            responses.append(response)

        actor_id = str(state.owner_actor_id or "").strip()
        actor_role = str(state.owner_actor_role or "").strip()
        if not actor_id or not actor_role:
            if self._require_tenant_persistence:
                return HTTPStatus.BAD_REQUEST, _error_page(
                    "Falta la identidad verificada de la persona que confirma."
                )
            actor_id = f"session:{session_id}"
            actor_role = "SESSION_OWNER"

        if state.selected_launch_review == "working_capital":
            component_packets: dict[str, dict[str, Any]] = {}
            followup_packet: dict[str, Any] | None = None
            persisted_confirmation = False
            for capability_ref in _WORKING_CAPITAL_COMPONENT_CAPABILITIES:
                component_packet = _run_product_root(
                    ingestion_output=state.ingestion_output,
                    requested_capability=capability_ref,
                    output_dir=self._review_output_dir(session_id=session_id),
                    deliver_result=False,
                    semantic_assistance_state=state.semantic_assistance_state,
                    semantic_dialogue_responses=responses,
                    semantic_owner_actor_id=actor_id,
                    semantic_owner_actor_role=actor_role,
                    use_assisted_semantics=True,
                )
                component_packets[capability_ref] = component_packet
                if component_packet.get("status") == STATUS_NEEDS_OWNER and followup_packet is None:
                    followup_packet = component_packet
                semantic_run = component_packet.get("semantic_run")
                if (
                    not persisted_confirmation
                    and isinstance(semantic_run, dict)
                    and semantic_run.get("status") == "CONFIRMED_BINDINGS"
                ):
                    try:
                        self._persist_owner_confirmation_events(state=state, packet=component_packet)
                    except Service1AssistedWebTenantPersistenceErrorV1:
                        return HTTPStatus.OK, _blocked_message_page(
                            "La confirmación fue recibida, pero no pudo guardarse de forma durable."
                        )
                    persisted_confirmation = True

            if followup_packet is not None:
                next_state = followup_packet.get("semantic_assistance_state")
                if isinstance(next_state, dict):
                    state.semantic_assistance_state = next_state
                state.semantic_questions = list(followup_packet.get("owner_questions") or [])
                return HTTPStatus.OK, _assisted_semantic_dialogue_page(
                    state.semantic_questions,
                    "La corrección o rechazo requiere una confirmación más granular.",
                )

            computations = {
                capability_ref: packet.get("computation_result")
                if isinstance(packet.get("computation_result"), dict)
                else {}
                for capability_ref, packet in component_packets.items()
            }
            ready = {
                capability_ref: computation
                for capability_ref, computation in computations.items()
                if computation.get("status") == "EVALUATED"
            }
            service_packet: dict[str, Any] = {
                "schema_version": "SERVICE_1_WORKING_CAPITAL_SERVICE_V1",
                "status": (
                    "READY"
                    if len(ready) == len(_WORKING_CAPITAL_COMPONENT_CAPABILITIES)
                    else "NEEDS_EVIDENCE"
                ),
                "service_ref": "working_capital",
                "component_packets": component_packets,
                "computed_components": ready,
                "runtime_authorized": False,
                "tool_execution_authorized": False,
                "delivery_authorized": False,
                "diagnosis_generated": False,
            }
            state.last_review_result = service_packet
            state.semantic_questions = []
            case_id = str(state.ingestion_output.get("case_id") or "").strip()
            self._remember_case(
                session_id=session_id,
                case_id=case_id,
                service_ref="working_capital",
                service_name="Caja y Capital de Trabajo",
                status="LISTO" if service_packet["status"] == "READY" else "FALTA INFORMACIÓN",
                kind="working_capital",
                packet=service_packet,
                ingestion_output=state.ingestion_output,
            )
            return HTTPStatus.OK, _working_capital_result_page(service_packet)

        packet = _run_product_root(
            ingestion_output=state.ingestion_output,
            requested_capability=state.selected_launch_review,
            output_dir=self._review_output_dir(session_id=session_id),
            deliver_result=state.selected_launch_review in {"sold_vs_collected_gap", "net_margin_real"},
            semantic_assistance_state=state.semantic_assistance_state,
            semantic_dialogue_responses=responses,
            semantic_owner_actor_id=actor_id,
            semantic_owner_actor_role=actor_role,
            use_assisted_semantics=True,
        )
        state.last_review_result = packet
        next_state = packet.get("semantic_assistance_state")
        if isinstance(next_state, dict):
            state.semantic_assistance_state = next_state

        semantic_run = packet.get("semantic_run")
        if isinstance(semantic_run, dict) and semantic_run.get("status") == "CONFIRMED_BINDINGS":
            try:
                self._persist_owner_confirmation_events(state=state, packet=packet)
            except Service1AssistedWebTenantPersistenceErrorV1:
                return HTTPStatus.OK, _blocked_message_page(
                    "La confirmación fue recibida, pero no pudo guardarse de forma durable."
                )

        if packet.get("status") == STATUS_NEEDS_OWNER:
            state.semantic_questions = list(packet.get("owner_questions") or [])
            if any(
                isinstance(item, Mapping) and item.get("question_kind") == "UNIT_MEANING"
                for item in state.semantic_questions
            ):
                return HTTPStatus.OK, _derived_unit_questions_page(
                    state.semantic_questions,
                    ingestion_output=state.ingestion_output,
                )
            return HTTPStatus.OK, _assisted_semantic_dialogue_page(
                state.semantic_questions,
                "La corrección o rechazo requiere una confirmación más granular.",
            )

        state.semantic_questions = []
        if packet.get("status") == STATUS_BLOCKED:
            case_id = str(
                state.ingestion_output.get("case_id")
                or state.ingestion_output.get("source_file_ref")
                or state.selected_launch_review
            ).strip()
            service_name = _LAUNCH_REVIEW_BY_REF.get(
                state.selected_launch_review,
                _REVIEW_BY_REF.get(
                    state.selected_launch_review,
                    (state.selected_launch_review, state.selected_launch_review, ""),
                ),
            )[1]
            self._remember_case(
                session_id=session_id,
                case_id=case_id,
                service_ref=state.selected_launch_review,
                service_name=service_name,
                status="FALTA INFORMACIÓN",
                kind="review",
                packet=packet,
                ingestion_output=state.ingestion_output,
            )
            return HTTPStatus.OK, _blocked_result_page(
                packet,
                state.selected_launch_review,
                ingestion_output=state.ingestion_output,
            )

        case_id = str(state.ingestion_output.get("case_id") or "").strip()
        service_name = _LAUNCH_REVIEW_BY_REF.get(
            state.selected_launch_review,
            _REVIEW_BY_REF.get(
                state.selected_launch_review,
                (state.selected_launch_review, state.selected_launch_review, ""),
            ),
        )[1]
        self._remember_case(
            session_id=session_id,
            case_id=case_id,
            service_ref=state.selected_launch_review,
            service_name=service_name,
            status="LISTO",
            kind="review",
            packet=packet,
            ingestion_output=state.ingestion_output,
        )
        return HTTPStatus.OK, _evaluated_result_page(
            packet,
            state.selected_launch_review,
            ingestion_output=state.ingestion_output,
        )

    def _confirm_derived_unit_evidence(
        self,
        *,
        session_id: str,
        fields: dict[str, str],
    ) -> tuple[int, str]:
        state = self.session(session_id)
        if (
            not isinstance(state.semantic_assistance_state, dict)
            or not isinstance(state.ingestion_output, dict)
            or not state.selected_launch_review
        ):
            return HTTPStatus.BAD_REQUEST, _error_page(
                "No hay una interpretación confirmada a la cual asociar esta unidad."
            )

        actor_id = str(state.owner_actor_id or "").strip()
        actor_role = str(state.owner_actor_role or "").strip()
        if not actor_id or not actor_role:
            if self._require_tenant_persistence:
                return HTTPStatus.BAD_REQUEST, _error_page(
                    "Falta la identidad verificada de la persona que confirma la unidad."
                )
            actor_id = f"session:{session_id}"
            actor_role = "SESSION_OWNER"

        new_events: list[dict[str, Any]] = []
        selected_units: dict[str, str] = {}
        deferred = False
        for question in state.semantic_questions:
            if not isinstance(question, Mapping) or question.get("question_kind") != "UNIT_MEANING":
                return HTTPStatus.BAD_REQUEST, _error_page(
                    "La evidencia pendiente no corresponde a una confirmación de unidad válida."
                )
            question_id = str(question.get("question_id") or "").strip()
            selected = str(fields.get(f"unit_{question_id}") or "").strip()
            if selected == "not_sure":
                selected_units[question_id] = selected
                deferred = True
                continue
            if selected not in ALLOWED_UNIT_KINDS:
                return HTTPStatus.BAD_REQUEST, _derived_unit_questions_page(
                    state.semantic_questions,
                    "Elegí cómo está expresado el descuento antes de continuar.",
                    selected_units=selected_units,
                    ingestion_output=state.ingestion_output,
                )
            selected_units[question_id] = selected
            try:
                event = build_service_1_owner_unit_confirmation_event_v1(
                    case_id=str(question.get("case_id") or "").strip(),
                    sheet_ref=str(question.get("sheet_ref") or "").strip(),
                    column_ref=str(question.get("column_ref") or "").strip(),
                    semantic_role=str(question.get("semantic_role") or "").strip(),
                    unit_kind=selected,
                    owner_answer=selected,
                    question_ref=question_id,
                    file_ref=str(
                        state.ingestion_output.get("source_file_ref")
                        or state.ingestion_output.get("filename")
                        or ""
                    ).strip()
                    or None,
                    provenance={
                        "producer": "service_1_assisted_web_v1",
                        "owner_actor_id": actor_id,
                        "owner_actor_role": actor_role,
                    },
                )
            except ValueError:
                return HTTPStatus.OK, _blocked_message_page(
                    "La confirmación de unidad no pudo convertirse en evidencia válida."
                )
            new_events.append(event.to_dict())

        if deferred:
            case_id = str(
                state.ingestion_output.get("case_id")
                or state.ingestion_output.get("source_file_ref")
                or state.selected_launch_review
            ).strip()
            service_name = _LAUNCH_REVIEW_BY_REF.get(
                state.selected_launch_review,
                _REVIEW_BY_REF.get(
                    state.selected_launch_review,
                    (state.selected_launch_review, state.selected_launch_review, ""),
                ),
            )[1]
            pending_packet = {
                "status": STATUS_NEEDS_OWNER,
                "blocked_reason": "DISCOUNT_UNIT_CONFIRMATION_REQUIRED",
                "derived_evidence": {
                    "status": "DERIVED_EVIDENCE_NEEDS_EVIDENCE",
                    "blocked_reason": "DISCOUNT_UNIT_CONFIRMATION_REQUIRED",
                    "evidence_requirements": ["DISCOUNT_UNIT_CONFIRMATION_REQUIRED"],
                },
                "computation_executed": False,
                "runtime_authorized": False,
                "tool_execution_authorized": False,
                "delivery_authorized": False,
                "diagnosis_generated": False,
            }
            self._remember_case(
                session_id=session_id,
                case_id=case_id,
                service_ref=state.selected_launch_review,
                service_name=service_name,
                status="FALTA INFORMACIÓN",
                kind="review",
                packet=pending_packet,
                ingestion_output=state.ingestion_output,
            )
            return HTTPStatus.OK, _unit_confirmation_deferred_page(state.semantic_questions)

        state.owner_unit_confirmation_events.extend(new_events)
        packet = _run_product_root(
            ingestion_output=state.ingestion_output,
            requested_capability=state.selected_launch_review,
            output_dir=self._review_output_dir(session_id=session_id),
            deliver_result=state.selected_launch_review in {"sold_vs_collected_gap", "net_margin_real"},
            semantic_assistance_state=state.semantic_assistance_state,
            owner_unit_confirmation_events=tuple(state.owner_unit_confirmation_events),
            use_assisted_semantics=True,
        )
        state.last_review_result = packet
        state.semantic_questions = []

        if packet.get("status") == STATUS_NEEDS_OWNER:
            state.semantic_questions = list(packet.get("owner_questions") or [])
            return HTTPStatus.OK, _derived_unit_questions_page(
                state.semantic_questions,
                "Todavía falta una confirmación material para completar la derivación.",
                ingestion_output=state.ingestion_output,
            )

        case_id = str(
            state.ingestion_output.get("case_id")
            or state.ingestion_output.get("source_file_ref")
            or state.selected_launch_review
        ).strip()
        service_name = _LAUNCH_REVIEW_BY_REF.get(
            state.selected_launch_review,
            _REVIEW_BY_REF.get(
                state.selected_launch_review,
                (state.selected_launch_review, state.selected_launch_review, ""),
            ),
        )[1]
        if packet.get("status") == STATUS_BLOCKED:
            self._remember_case(
                session_id=session_id,
                case_id=case_id,
                service_ref=state.selected_launch_review,
                service_name=service_name,
                status="FALTA INFORMACIÓN",
                kind="review",
                packet=packet,
                ingestion_output=state.ingestion_output,
            )
            return HTTPStatus.OK, _blocked_result_page(
                packet,
                state.selected_launch_review,
                ingestion_output=state.ingestion_output,
            )

        self._remember_case(
            session_id=session_id,
            case_id=case_id,
            service_ref=state.selected_launch_review,
            service_name=service_name,
            status="LISTO",
            kind="review",
            packet=packet,
            ingestion_output=state.ingestion_output,
        )
        return HTTPStatus.OK, _evaluated_result_page(
            packet,
            state.selected_launch_review,
            ingestion_output=state.ingestion_output,
        )

    def run_working_capital(self, *, session_id: str) -> tuple[int, str]:
        state = self.session(session_id)
        if not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero subí y confirmá un archivo de Excel.")
        capability_refs = (
            "projected_closing_cash_balance",
            "dso",
            "current_ratio",
        )
        packets: dict[str, dict[str, Any]] = {}
        for capability_ref in capability_refs:
            packets[capability_ref] = _run_product_root(
                ingestion_output=state.ingestion_output,
                owner_answers=state.semantic_answers,
                requested_capability=capability_ref,
                output_dir=self._review_output_dir(session_id=session_id),
                deliver_result=False,
            )
        computations = {
            capability_ref: packet.get("computation_result")
            if isinstance(packet.get("computation_result"), dict)
            else {}
            for capability_ref, packet in packets.items()
        }
        ready = {
            capability_ref: computation
            for capability_ref, computation in computations.items()
            if computation.get("status") == "EVALUATED"
        }
        service_packet: dict[str, Any] = {
            "schema_version": "SERVICE_1_WORKING_CAPITAL_SERVICE_V1",
            "status": "READY" if len(ready) == len(capability_refs) else "NEEDS_EVIDENCE",
            "service_ref": "working_capital",
            "component_packets": packets,
            "computed_components": ready,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
        case_id = str(state.ingestion_output.get("case_id") or "").strip()
        self._remember_case(
            session_id=session_id,
            case_id=case_id,
            service_ref="working_capital",
            service_name="Caja y Capital de Trabajo",
            status="LISTO" if service_packet["status"] == "READY" else "FALTA INFORMACIÓN",
            kind="working_capital",
            packet=service_packet,
            ingestion_output=state.ingestion_output,
        )
        return HTTPStatus.OK, _working_capital_result_page(service_packet)

    def run_review(self, *, session_id: str, requested_capability: str) -> tuple[int, str]:
        state = self.session(session_id)
        if requested_capability == "working_capital":
            return self.run_working_capital(session_id=session_id)
        if requested_capability not in _REVIEW_BY_REF:
            return HTTPStatus.BAD_REQUEST, _review_selection_page("Elegí una revisión disponible.")
        if not state.ingestion_output:
            return HTTPStatus.BAD_REQUEST, _error_page("Primero subí y confirmá un archivo de Excel.")
        review_output_dir = self._review_output_dir(session_id=session_id)
        packet = _run_product_root(
            ingestion_output=state.ingestion_output,
            owner_answers=state.semantic_answers,
            requested_capability=requested_capability,
            output_dir=review_output_dir,
            deliver_result=requested_capability in {"sold_vs_collected_gap", "net_margin_real"},
        )
        if state.consorcio_case_context is not None:
            state.consorcio_case_context.requested_review = requested_capability
        state.last_review_result = packet

        semantic_run = packet.get("semantic_run")
        if isinstance(semantic_run, dict) and semantic_run.get("status") == "CONFIRMED_BINDINGS":
            try:
                self._persist_owner_confirmation_events(state=state, packet=packet)
            except Service1AssistedWebTenantPersistenceErrorV1:
                return HTTPStatus.OK, _blocked_message_page(
                    "La confirmación fue recibida, pero no pudo guardarse de forma durable. No se registró como memoria del tenant."
                )

        if packet.get("status") == STATUS_NEEDS_OWNER:
            if state.consorcio_case_context is not None:
                state.consorcio_case_context.case_status = "IN_REVIEW"
            state.semantic_questions = list(packet.get("owner_questions") or [])
            if any(not str(question.get("question_id") or "").strip() for question in state.semantic_questions):
                return HTTPStatus.OK, _blocked_message_page("No se puede continuar con esa descripción. Elegí una opción clara o volvé a confirmar las columnas.")
            return HTTPStatus.OK, _semantic_questions_page(state.semantic_questions, "Hace falta una precisión más para continuar.")
        if packet.get("status") == STATUS_BLOCKED:
            if state.consorcio_case_context is not None:
                state.consorcio_case_context.case_status = "IN_REVIEW"
            case_id = str(
                state.ingestion_output.get("case_id")
                or state.ingestion_output.get("source_file_ref")
                or requested_capability
            ).strip()
            service_name = _LAUNCH_REVIEW_BY_REF.get(
                requested_capability,
                _REVIEW_BY_REF.get(requested_capability, (requested_capability, requested_capability, "")),
            )[1]
            self._remember_case(
                session_id=session_id,
                case_id=case_id,
                service_ref=requested_capability,
                service_name=service_name,
                status="FALTA INFORMACIÓN",
                kind="review",
                packet=packet,
                ingestion_output=state.ingestion_output,
            )
            return HTTPStatus.OK, _blocked_result_page(
                packet,
                requested_capability,
                ingestion_output=state.ingestion_output,
                semantic_answers=state.semantic_answers,
            )

        if state.consorcio_case_context is not None:
            state.consorcio_case_context.case_status = "READY"

        service_name = _LAUNCH_REVIEW_BY_REF.get(
            requested_capability,
            _REVIEW_BY_REF.get(requested_capability, (requested_capability, requested_capability, "")),
        )[1]
        case_id = str(
            state.ingestion_output.get("case_id")
            or state.ingestion_output.get("source_file_ref")
            or requested_capability
        ).strip()
        self._remember_case(
            session_id=session_id,
            case_id=case_id,
            service_ref=requested_capability,
            service_name=service_name,
            status="LISTO",
            kind="review",
            packet=packet,
            ingestion_output=state.ingestion_output,
        )
        return HTTPStatus.OK, _evaluated_result_page(
            packet,
            requested_capability,
            ingestion_output=state.ingestion_output,
        )

    def _persist_owner_confirmation_events(
        self,
        *,
        state: AssistedWebSessionV1,
        packet: dict[str, Any],
    ) -> None:
        semantic_run = packet.get("semantic_run")
        semantic = semantic_run if isinstance(semantic_run, dict) else {}
        events = semantic.get("owner_confirmation_events") or []
        if not events:
            return

        if self._persist_tenant_confirmation is None or state.tenant_identity_contract is None:
            if self._require_tenant_persistence:
                raise Service1AssistedWebTenantPersistenceErrorV1(
                    "tenant persistence is required but identity or adapter is unavailable"
                )
            return

        persist_service_1_assisted_web_owner_events_v1(
            identity_contract=state.tenant_identity_contract,
            semantic_run=semantic,
            ingestion_output=state.ingestion_output,
            persist_contract=self._persist_tenant_confirmation,
            load_prior_contract=self._load_prior_semantic_contract,
        )

    def read_sales_collections_delivery(self, *, session_id: str) -> tuple[str, bytes]:
        return self._read_last_review_delivery(
            session_id=session_id,
            expected_capability="sold_vs_collected_gap",
            unavailable_message="sales and collections delivery is unavailable",
        )

    def read_net_margin_delivery(self, *, session_id: str) -> tuple[str, bytes]:
        return self._read_last_review_delivery(
            session_id=session_id,
            expected_capability="net_margin_real",
            unavailable_message="net margin delivery is unavailable",
        )

    def _read_last_review_delivery(
        self,
        *,
        session_id: str,
        expected_capability: str,
        unavailable_message: str,
    ) -> tuple[str, bytes]:
        packet = self.session(session_id).last_review_result
        if not isinstance(packet, dict):
            raise ValueError(unavailable_message)
        outcome = packet.get("bounded_outcome")
        outcome = outcome if isinstance(outcome, dict) else {}
        if outcome.get("capability_ref") != expected_capability:
            raise ValueError(unavailable_message)
        delivery_result = packet.get("delivery_result")
        delivery_packet = delivery_result if isinstance(delivery_result, dict) else {}
        delivery = delivery_packet.get("delivery")
        delivery = delivery if isinstance(delivery, dict) else {}
        output_path = str(delivery.get("output_path") or "").strip()
        if not output_path:
            raise ValueError(unavailable_message)
        target = Path(output_path)
        expected_dir = self._review_output_dir(session_id=session_id).resolve()
        if not target.is_file() or target.parent.resolve() != expected_dir:
            raise ValueError("delivery path is invalid")
        return target.name, target.read_bytes()


def _scope_owner_questions_for_launch_review(packet, selected_launch_review):
    questions = [dict(item) for item in (packet.get("owner_questions") or []) if isinstance(item, dict)]
    review_ref = str(selected_launch_review or "").strip()
    relevant_roles = _LAUNCH_REVIEW_RELEVANT_ROLES.get(review_ref)
    relevant_headers = _LAUNCH_REVIEW_RELEVANT_HEADERS.get(review_ref, frozenset())
    if not relevant_roles or not questions:
        return questions, {}
    semantic_run = packet.get("semantic_run") if isinstance(packet.get("semantic_run"), dict) else {}
    gate = semantic_run.get("gate_packet") if isinstance(semantic_run.get("gate_packet"), dict) else {}
    candidates = gate.get("owner_confirmation_candidates")
    candidate_list = list(candidates) if isinstance(candidates, (list, tuple)) else []
    relevant_refs = set()
    for candidate in candidate_list:
        roles = {str(role).strip() for role in (getattr(candidate, "candidate_semantic_roles", ()) or ()) if str(role).strip()}
        if not roles.intersection(relevant_roles):
            continue
        metadata = dict(getattr(candidate, "metadata", {}) or {})
        ref_id = str(metadata.get("column_ref_id") or metadata.get("question_id") or getattr(candidate, "source_column_name", "") or "").strip()
        if ref_id:
            relevant_refs.add(ref_id)
    visible = []
    exclusions = {}
    for question in questions:
        ref_id = str(question.get("question_id") or question.get("field_id") or question.get("column_name") or "").strip()
        column_name = str(question.get("column_name") or "").strip()
        normalized_header = normalize_service_1_column_understanding_header_v1(column_name)
        if ref_id in relevant_refs or normalized_header in relevant_headers:
            visible.append(question)
        elif ref_id:
            exclusions[ref_id] = {"option_id": "IGNORE", "scope_excluded": True}
    return visible, exclusions


def _run_product_root(
    *,
    ingestion_output: dict[str, Any],
    owner_answers: Any = None,
    requested_capability: str | None = None,
    output_dir: str | Path | None = None,
    deliver_result: bool = False,
    semantic_provider: Any = None,
    semantic_assistance_state: Mapping[str, Any] | None = None,
    semantic_dialogue_responses: Sequence[Mapping[str, Any]] | None = None,
    semantic_owner_actor_id: str | None = None,
    semantic_owner_actor_role: str | None = None,
    compatible_tenant_memory_hints: Sequence[Mapping[str, Any]] = (),
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] = (),
    semantic_scope_capabilities: Sequence[str] = (),
    use_assisted_semantics: bool = False,
) -> dict[str, Any]:
    sheet_name = str(ingestion_output.get("sheet_name") or "sheet1")
    semantic_run_override = None
    if owner_answers is not None and not use_assisted_semantics:
        semantic_run_override = resolve_service_1_legacy_semantic_run_v1(
            ingestion_output=ingestion_output,
            sheet_name=sheet_name,
            owner_answers=owner_answers,
        )
    return run_service_1_product_pipeline_v1(
        ingestion_output=ingestion_output,
        tool_requests=[],
        output_dir=output_dir or tempfile.gettempdir(),
        sheet_name=sheet_name,
        semantic_run_override=semantic_run_override,
        requested_capability=requested_capability,
        deliver_result=deliver_result,
        semantic_provider=semantic_provider,
        semantic_assistance_state=semantic_assistance_state,
        semantic_dialogue_responses=semantic_dialogue_responses,
        semantic_owner_actor_id=semantic_owner_actor_id,
        semantic_owner_actor_role=semantic_owner_actor_role,
        compatible_tenant_memory_hints=compatible_tenant_memory_hints,
        owner_unit_confirmation_events=owner_unit_confirmation_events,
        semantic_scope_capabilities=semantic_scope_capabilities,
        use_assisted_semantics=use_assisted_semantics,
    )


def create_assisted_web_server_v1(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    output_dir: str | Path | None = None,
    persist_tenant_confirmation: Callable[[Any, Any], object] | None = None,
    load_tenant_memory: Callable[[str], tuple[dict[str, object], ...]] | None = None,
    load_prior_semantic_contract: Callable[[str, str, str, str, str], object | None] | None = None,
    load_persisted_cases: Callable[[str], tuple[dict[str, object], ...]] | None = None,
    load_persisted_case: Callable[[str, str], dict[str, object] | None] | None = None,
    require_tenant_persistence: bool = False,
    tenant_identity_resolver: Callable[[BaseHTTPRequestHandler], dict[str, str] | None] | None = None,
    radar_policy_store: object | None = None,
    semantic_provider: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> ThreadingHTTPServer:
    application = AssistedWebApplicationV1(
        output_dir=output_dir,
        persist_tenant_confirmation=persist_tenant_confirmation,
        load_tenant_memory=load_tenant_memory,
        load_prior_semantic_contract=load_prior_semantic_contract,
        load_persisted_cases=load_persisted_cases,
        load_persisted_case=load_persisted_case,
        require_tenant_persistence=require_tenant_persistence,
        radar_policy_store=radar_policy_store,
        semantic_provider=semantic_provider,
    )
    return ThreadingHTTPServer(
        (host, port),
        _handler_for(application, tenant_identity_resolver=tenant_identity_resolver),
    )


def _handler_for(
    application: AssistedWebApplicationV1,
    *,
    tenant_identity_resolver: Callable[[BaseHTTPRequestHandler], dict[str, str] | None] | None = None,
) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            session_id = self._session_id()
            with application.session_lock(session_id):
                self._do_GET_locked(session_id)

        def _do_GET_locked(self, session_id: str) -> None:
            parsed = urlsplit(self.path)
            if parsed.path == "/" and tenant_identity_resolver is not None:
                try:
                    identity = tenant_identity_resolver(self)
                    if identity is not None:
                        application.bind_tenant_identity(
                            session_id=session_id,
                            tenant_id=identity.get("tenant_id", ""),
                            cliente_id=identity.get("cliente_id") or None,
                            owner_actor_id=identity.get("owner_actor_id", ""),
                            owner_actor_role=identity.get("owner_actor_role", ""),
                        )
                except ValueError:
                    self._send_html(
                        HTTPStatus.OK,
                        _login_page(),
                        session_id=session_id,
                    )
                    return
            if (
                parsed.path in {"/cases", "/case"}
                and tenant_identity_resolver is not None
                and not str(application.session(session_id).tenant_id or "").strip()
            ):
                try:
                    identity = tenant_identity_resolver(self)
                    if identity is not None:
                        application.bind_tenant_identity(
                            session_id=session_id,
                            tenant_id=identity.get("tenant_id", ""),
                            cliente_id=identity.get("cliente_id") or None,
                            owner_actor_id=identity.get("owner_actor_id", ""),
                            owner_actor_role=identity.get("owner_actor_role", ""),
                        )
                except ValueError as exc:
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _error_page(str(exc)),
                        session_id=session_id,
                    )
                    return
            if parsed.path == "/":
                self._send_html(HTTPStatus.OK, _home_page())
            elif parsed.path == "/cases":
                status, content_html = application.recent_cases(session_id=session_id)
                self._send_html(status, content_html, session_id=session_id)
            elif parsed.path == "/case":
                query = parse_qs(parsed.query)
                case_ref = str((query.get("case_ref") or [""])[-1]).strip()
                status, content_html = application.open_case(
                    session_id=session_id,
                    case_ref=case_ref,
                )
                self._send_html(status, content_html, session_id=session_id)
            elif parsed.path == "/static/service_1_assisted_web_v1.css":
                self._send(HTTPStatus.OK, _STYLES_PATH.read_bytes(), "text/css; charset=utf-8")
            elif self.path == "/healthz":
                self._send(HTTPStatus.OK, b'{"status":"ok"}', "application/json; charset=utf-8")
            elif self.path == "/radar":
                session_id = self._session_id()
                status, content_html = application.radar_owner_menu(session_id=session_id)
                self._send_html(status, content_html, session_id=session_id)
            elif self.path == "/consorcios-case":
                session_id = self._session_id()
                status, content_html = application.consorcios_case_workspace(session_id=session_id)
                self._send_html(status, content_html, session_id=session_id)
            elif self.path == "/consorcios-case-summary":
                session_id = self._session_id()
                status, content_html = application.consorcios_case_summary(session_id=session_id)
                self._send_html(status, content_html, session_id=session_id)
            elif self.path == "/consorcios-radar-analysis":
                session_id = self._session_id()
                status, content_html = application.consorcios_radar_analysis_menu(session_id=session_id)
                self._send_html(status, content_html, session_id=session_id)
            elif self.path == "/download-sales-collections":
                session_id = self._session_id()
                try:
                    filename, content = application.read_sales_collections_delivery(
                        session_id=session_id
                    )
                except ValueError:
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _error_page("Primero completá la revisión de ventas y cobranzas."),
                        session_id=session_id,
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    session_id=session_id,
                    extra_headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    },
                )
            elif self.path == "/download-net-margin":
                session_id = self._session_id()
                try:
                    filename, content = application.read_net_margin_delivery(
                        session_id=session_id
                    )
                except ValueError:
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _error_page("Primero completá la revisión de margen neto real."),
                        session_id=session_id,
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    session_id=session_id,
                    extra_headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    },
                )
            elif self.path == "/download-reconciliation-workpaper":
                session_id = self._session_id()
                try:
                    workpaper = application.build_reconciliation_workpaper(
                        session_id=session_id
                    )
                except ValueError:
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _error_page("Primero prepará una conciliación para generar el papel de trabajo."),
                        session_id=session_id,
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    workpaper["content"],
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    session_id=session_id,
                    extra_headers={
                        "Content-Disposition": f'attachment; filename="{workpaper["filename"]}"'
                    },
                )
            else:
                self._send_html(HTTPStatus.NOT_FOUND, _error_page("No encontramos esa página."))

        def do_POST(self) -> None:  # noqa: N802
            session_id = self._session_id()
            with application.session_lock(session_id):
                self._do_POST_locked(session_id)

        def _do_POST_locked(self, session_id: str) -> None:
            if self.path == "/login":
                fields = _form_fields(self)
                authenticator = getattr(tenant_identity_resolver, "sign_in_with_password", None)
                if not callable(authenticator):
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _login_page("El acceso web no está configurado."),
                        session_id=session_id,
                    )
                    return
                try:
                    token = authenticator(
                        fields.get("email", ""),
                        fields.get("password", ""),
                    )
                except ValueError:
                    self._send_html(
                        HTTPStatus.BAD_REQUEST,
                        _login_page("No pudimos iniciar sesión con esos datos."),
                        session_id=session_id,
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    _document(_home_page()).encode("utf-8"),
                    "text/html; charset=utf-8",
                    session_id=session_id,
                    extra_headers={
                        "Set-Cookie": (
                            f"{SERVICE_1_ACCESS_TOKEN_COOKIE}={token}; Path=/; "
                            "SameSite=Lax; HttpOnly; Secure"
                        ),
                        "Cache-Control": "no-store",
                    },
                )
                return
            try:
                if tenant_identity_resolver is not None:
                    identity = tenant_identity_resolver(self)
                    if identity is not None:
                        application.bind_tenant_identity(
                            session_id=session_id,
                            tenant_id=identity.get("tenant_id", ""),
                            cliente_id=identity.get("cliente_id") or None,
                            owner_actor_id=identity.get("owner_actor_id", ""),
                            owner_actor_role=identity.get("owner_actor_role", ""),
                        )
                if self.path == "/upload":
                    upload_fields, upload_files = _multipart_form(self)
                    if "file" not in upload_files:
                        raise ValueError("file field required")
                    filename, content = upload_files["file"]
                    launch_review = upload_fields.get("launch_review", "").strip()
                    consorcio_id = upload_fields.get("consorcio_id", "").strip()
                    consorcio_name = upload_fields.get("consorcio_name", "").strip()
                    period = upload_fields.get("period", "").strip()
                    has_case_context = any((consorcio_id, consorcio_name, period))
                    if has_case_context:
                        if not all((consorcio_id, consorcio_name, period)):
                            raise ValueError("consorcio context is incomplete")
                        application.bind_consorcio_case_context(
                            session_id=session_id,
                            case_id=f"consorcio-{_safe_path_segment(consorcio_id)}-{period}",
                            consorcio_id=consorcio_id,
                            consorcio_name=consorcio_name,
                            period=period,
                            source_files=(filename,),
                        )
                    status, content_html = application.receive_xlsx(
                        session_id=session_id,
                        filename=filename,
                        content=content,
                        selected_launch_review=launch_review or None,
                    )
                elif self.path == "/upload-reconciliation":
                    _, files = _multipart_form(self)
                    status, content_html = application.receive_reconciliation_sources(
                        session_id=session_id,
                        files=files,
                    )
                else:
                    fields = _form_fields(self)
                    if self.path == "/start-reconciliation":
                        status, content_html = application.start_reconciliation(
                            session_id=session_id,
                            reconciliation_type=fields.get("reconciliation_type", ""),
                        )
                    elif self.path == "/confirm-reconciliation-columns":
                        status, content_html = application.confirm_reconciliation_columns(
                            session_id=session_id,
                            fields=fields,
                        )
                    elif self.path == "/decide-reconciliation-item":
                        status, content_html = application.decide_reconciliation_item(
                            session_id=session_id,
                            review_item_ref=fields.get("review_item_ref", ""),
                            decision=fields.get("decision", ""),
                            reviewed_by=fields.get("reviewed_by", ""),
                            observation=fields.get("observation", ""),
                        )
                    elif self.path == "/confirm-meanings":
                        status, content_html = application.confirm_meanings(session_id=session_id, fields=fields)
                    elif self.path == "/run-review":
                        status, content_html = application.run_review(session_id=session_id, requested_capability=fields.get("review", ""))
                    elif self.path == "/save-radar-policy":
                        status, content_html = application.save_radar_owner_policy(
                            session_id=session_id,
                            fields=fields,
                        )
                    elif self.path == "/run-consorcios-collection-aging":
                        status, content_html = application.run_consorcios_collection_aging(
                            session_id=session_id,
                            fields=fields,
                        )
                    elif self.path == "/run-consorcios-expense-variance":
                        status, content_html = application.run_consorcios_expense_variance(
                            session_id=session_id,
                            fields=fields,
                        )
                    else:
                        status, content_html = HTTPStatus.NOT_FOUND, _error_page("No encontramos esa acción.")
            except ValueError:
                status, content_html = HTTPStatus.BAD_REQUEST, _error_page("No se pudo leer el envío. Probá de nuevo.")
            if self.headers.get("HX-Request") == "true":
                self._send_fragment(status, content_html, session_id=session_id)
            else:
                self._send_html(status, content_html, session_id=session_id)

        def _session_id(self) -> str:
            cookie = self.headers.get("Cookie", "")
            for part in cookie.split(";"):
                name, _, value = part.strip().partition("=")
                if name == "service1_session" and value:
                    return value
            return secrets.token_urlsafe(18)

        def _send_fragment(self, status: int, content: str, *, session_id: str | None = None) -> None:
            self._send(status, content.encode("utf-8"), "text/html; charset=utf-8", session_id=session_id)

        def _send_html(self, status: int, content: str, *, session_id: str | None = None) -> None:
            self._send(status, _document(content).encode("utf-8"), "text/html; charset=utf-8", session_id=session_id)

        def _send(
            self,
            status: int,
            body: bytes,
            content_type: str,
            *,
            session_id: str | None = None,
            extra_headers: dict[str, str] | None = None,
        ) -> None:
            self.send_response(int(status))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for name, value in (extra_headers or {}).items():
                self.send_header(name, value)
            if session_id is not None:
                self.send_header("Set-Cookie", f"service1_session={session_id}; Path=/; SameSite=Lax; HttpOnly")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def _multipart_file(handler: BaseHTTPRequestHandler) -> tuple[str, bytes]:
    _, files = _multipart_form(handler)
    if "file" not in files:
        raise ValueError("file field required")
    return files["file"]


def _multipart_form(
    handler: BaseHTTPRequestHandler,
) -> tuple[dict[str, str], dict[str, tuple[str, bytes]]]:
    content_type = handler.headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type:
        raise ValueError("multipart form data required")
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0 or length > 40 * 1024 * 1024:
        raise ValueError("invalid upload size")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
        + handler.rfile.read(length)
    )
    fields: dict[str, str] = {}
    files: dict[str, tuple[str, bytes]] = {}
    for part in message.iter_parts():
        name = str(part.get_param("name", header="content-disposition") or "").strip()
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True)
        raw = payload if isinstance(payload, bytes) else b""
        if filename is not None:
            files[name] = (filename, raw)
        else:
            fields[name] = raw.decode("utf-8", errors="replace")
    return fields, files


def _form_fields(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length).decode("utf-8", errors="replace")
    parsed = parse_qs(raw, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _safe_path_segment(value: str) -> str:
    raw = str(value or "").strip()
    safe = "".join(character if character.isalnum() or character in {"-", "_", "."} else "_" for character in raw)
    safe = safe.strip("._")
    if not safe:
        raise ValueError("invalid case path segment")
    return safe[:120]


def _document(content: str) -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    visual_system = """
    <style>
      :root{--ink:#17201c;--ink-strong:#0d1512;--muted:#5d6760;--paper:#f4f1e8;--paper-2:#fbfaf5;--paper-3:#ece7dc;--rule:#c9c4b7;--rule-strong:#8e978f;--green:#1d5b43;--green-strong:#123c2d;--green-soft:#dfe9e2;--amber:#8b5b16;--amber-soft:#f2e7c8;--red:#873b34;--red-soft:#f0ddda;--slate:#49534d;--white:#fffef9;--sans:"Aptos","Segoe UI",system-ui,sans-serif;--mono:"IBM Plex Mono","Cascadia Mono",Consolas,monospace;--serif:Georgia,"Times New Roman",serif;color-scheme:light;font-family:var(--sans);color:var(--ink);background:var(--paper-3)}
      *{box-sizing:border-box}html{min-width:320px;background:var(--paper-3)}body{margin:0;min-height:100vh;background:linear-gradient(rgba(71,82,75,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(71,82,75,.035) 1px,transparent 1px),var(--paper);background-size:32px 32px;color:var(--ink);line-height:1.45}a{color:var(--green-strong);text-underline-offset:.16em}a:hover{color:var(--green)}button,input,select{font:inherit}
      .pymia-frame{min-height:100vh}.app-topbar{min-height:62px;display:grid;grid-template-columns:minmax(280px,1fr) auto;align-items:center;gap:1rem;padding:.75rem 1.15rem;background:var(--ink-strong);color:#edf2ed;border-bottom:4px solid var(--green)}.app-brand{display:flex;align-items:center;gap:.65rem;min-width:0}.brand-mark{display:inline-grid;grid-template-columns:repeat(3,4px);gap:3px;align-items:end;width:18px;height:20px}.brand-mark i{display:block;width:4px;background:#8fb59e}.brand-mark i:nth-child(1){height:20px}.brand-mark i:nth-child(2){height:13px}.brand-mark i:nth-child(3){height:7px}.brand-word{font-family:var(--mono);font-size:.86rem;letter-spacing:.16em;font-weight:700}.brand-divider{color:#9aa39c}.brand-system{font-size:.72rem;letter-spacing:.14em;color:#aebbb4;font-weight:700}.system-context{display:flex;align-items:center;gap:1.25rem;font-family:var(--mono);font-size:.62rem;color:#b9c4be;white-space:nowrap}.system-context b{color:#dce4df;letter-spacing:.08em;font-weight:700}
      .workspace{display:grid;grid-template-columns:184px minmax(0,1fr);min-height:calc(100vh - 62px)}.service-rail{background:#e5e0d5;border-right:1px solid var(--rule-strong);padding:1rem .8rem;position:sticky;top:0;align-self:start;min-height:calc(100vh - 62px)}.rail-index{display:inline-block;font-family:var(--mono);font-size:1.6rem;letter-spacing:-.04em;font-weight:700;color:var(--green-strong);border-top:5px solid var(--green);padding-top:.15rem;margin-bottom:1.2rem}.service-rail nav{display:grid;border-top:1px solid var(--rule-strong)}.service-rail nav a,.rail-disabled{position:relative;display:block;padding:.66rem .2rem .66rem 2.1rem;border-bottom:1px solid var(--rule);text-decoration:none;color:var(--ink-strong);font-size:.82rem;font-weight:680}.service-rail nav a::before,.rail-disabled::before{content:attr(data-ref);position:absolute;left:.1rem;top:.72rem;font-family:var(--mono);font-size:.58rem;letter-spacing:.08em;color:#6d766f}.service-rail nav a:hover{background:rgba(255,255,255,.48)}.rail-disabled{color:#5d6760}.rail-note{margin-top:1.3rem;padding-top:.8rem;border-top:3px double var(--rule-strong);font-family:var(--mono);font-size:.58rem;line-height:1.6;letter-spacing:.11em;color:#5d6760}
      .app-shell{width:min(1120px,calc(100% - 48px));margin:0 auto;padding:1.6rem 0 3rem}main#app{max-width:none;margin:0;padding:0;background:transparent;border:0}main#app>h1,.result-head h1{margin:.15rem 0 .65rem;font-family:var(--serif);font-size:clamp(1.75rem,3vw,2.55rem);line-height:1.05;font-weight:700;letter-spacing:-.025em;color:var(--ink-strong)}main#app>p,section>p,fieldset>p,details>p{color:var(--slate)}.eyebrow{display:inline-block;margin:0 0 .45rem;font-family:var(--mono);font-size:.66rem;text-transform:uppercase;letter-spacing:.16em;color:var(--green-strong);font-weight:700}.eyebrow::before{content:"PYMIA / ";color:#5d6760}
      section,fieldset,details,.choice,.notice{border-radius:0}section{margin:1rem 0;padding:1rem 1.05rem 1.1rem;background:var(--paper-2);border:1px solid var(--rule);border-left:4px solid #9da69f}section>h2{margin:0 0 .65rem;font-size:.9rem;line-height:1.2;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-strong)}section>h2::before{content:"§ ";color:var(--green);font-family:var(--mono)}hr{border:0;border-top:3px double var(--rule-strong);margin:1.35rem 0}
      form{display:grid;gap:.75rem}fieldset{margin:.4rem 0;padding:.95rem 1rem 1rem;background:#f8f5ed;border:1px solid var(--rule-strong)}legend{padding:0 .4rem;font-family:var(--mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--green-strong)}label{display:grid;gap:.28rem;cursor:pointer;color:var(--ink);font-size:.9rem}input[type=text],input[type=month],input[type=number],input[type=file],select{width:100%;min-height:2.7rem;padding:.58rem .68rem;border:1px solid #9aa39c;border-radius:0;background:var(--white);color:var(--ink-strong)}input[type=radio],input[type=checkbox]{accent-color:var(--green)}button{min-height:2.65rem;width:fit-content;padding:.55rem 1rem;border:1px solid var(--green-strong);border-radius:0;background:var(--green-strong);color:white;font-family:var(--mono);font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;cursor:pointer}button:hover{background:var(--green)}
      .choice{position:relative;padding:.9rem .9rem .9rem 2.8rem;background:var(--paper-2);border:1px solid var(--rule);border-left:3px solid var(--rule-strong)}.choice::before{content:"SERVICE";position:absolute;left:.55rem;top:1.05rem;writing-mode:vertical-rl;transform:rotate(180deg);font-family:var(--mono);font-size:.5rem;letter-spacing:.14em;color:#5d6760}.choice:has(input:checked){border-color:var(--green);border-left-color:var(--green);background:#edf2ed}.choice strong{font-size:.96rem;color:var(--ink-strong)}.choice span{display:block;margin:.25rem 0 0 1.7rem;color:var(--muted);font-size:.83rem}.notice{margin:1rem 0;padding:.8rem .9rem;background:#eeece5;border:1px solid var(--rule);border-left:4px solid var(--green);color:var(--ink);font-size:.86rem}p[role=alert]{padding:.72rem .85rem;background:var(--red-soft);border:1px solid #d0a29c;border-left:4px solid var(--red);color:#662a25}
      .result-head{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:1.2rem;align-items:start;padding:.85rem 0 1rem;border-top:5px solid var(--ink-strong);border-bottom:1px solid var(--rule-strong);margin-bottom:1rem}.status-chip{display:inline-flex;align-items:center;min-height:2rem;padding:.35rem .55rem;border:1px solid currentColor;border-radius:0;font-family:var(--mono);font-size:.64rem;letter-spacing:.08em;font-weight:700;text-transform:uppercase;background:var(--paper-2)}.status-chip::before{content:"STATUS / ";opacity:.62}.status-ready{color:var(--green-strong);background:var(--green-soft)}.status-review{color:var(--amber);background:var(--amber-soft)}.status-missing{color:var(--red);background:var(--red-soft)}.result{font-family:var(--mono);font-size:clamp(1.45rem,3vw,2.15rem);letter-spacing:-.03em;font-variant-numeric:tabular-nums}
      .metric-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin:1rem 0;border:1px solid var(--rule-strong);background:var(--rule)}.metric{min-width:0;padding:.85rem .9rem;background:var(--paper-2);border-right:1px solid var(--rule)}.metric:last-child{border-right:0}.metric small{display:block;color:var(--muted);font-size:.68rem;font-family:var(--mono);text-transform:uppercase;letter-spacing:.08em}.metric strong{display:block;margin-top:.3rem;font-family:var(--mono);font-size:1.25rem;font-variant-numeric:tabular-nums;color:var(--ink-strong)}
      .result-actions{display:flex;flex-wrap:wrap;gap:.55rem;margin:1rem 0}.result-actions a{display:inline-flex;align-items:center;min-height:2.55rem;padding:.55rem .8rem;border:1px solid var(--green-strong);background:var(--green-strong);color:white;text-decoration:none;font-family:var(--mono);font-size:.68rem;letter-spacing:.05em;font-weight:700;text-transform:uppercase}.result-actions a.secondary{background:transparent;color:var(--green-strong);border-color:var(--rule-strong)}table{width:100%;border-collapse:collapse;background:var(--paper-2);border:1px solid var(--rule-strong);font-size:.83rem}th,td{padding:.62rem .68rem;border-bottom:1px solid var(--rule);vertical-align:top}th{text-align:left;font-family:var(--mono);font-size:.64rem;letter-spacing:.07em;text-transform:uppercase;color:#59635d;background:#ece8de;font-weight:700}td{font-variant-numeric:tabular-nums;color:var(--ink-strong)}tbody tr:hover{background:#f4f0e6}
      details{margin:.65rem 0;border:1px solid var(--rule);background:var(--paper-2)}summary{padding:.7rem .8rem;cursor:pointer;font-family:var(--mono);font-size:.72rem;letter-spacing:.04em;font-weight:700;text-transform:uppercase}details>*:not(summary){margin-left:.8rem;margin-right:.8rem}details>form,details>ol,details>ul{margin-bottom:.8rem}ol,ul{padding-left:1.25rem}li+li{margin-top:.35rem}.skip-link{position:absolute;left:-9999px}.skip-link:focus{left:.75rem;top:.75rem;z-index:999;background:var(--white);color:var(--ink);padding:.5rem .7rem;border:2px solid var(--green)}:focus-visible{outline:3px solid #bb7a1c;outline-offset:2px}
      @media(max-width:1024px){.workspace{grid-template-columns:148px minmax(0,1fr)}.service-rail nav a,.rail-disabled{padding-left:1.9rem;font-size:.78rem}.app-shell{width:min(100% - 32px,980px)}.system-context{gap:.65rem;font-size:.56rem}}
      @media(max-width:768px){.app-topbar{grid-template-columns:1fr;gap:.4rem}.system-context{display:none}.workspace{display:block}.service-rail{position:static;min-height:auto;padding:.55rem .7rem;border-right:0;border-bottom:1px solid var(--rule-strong)}.rail-index,.rail-note{display:none}.service-rail nav{grid-template-columns:repeat(5,minmax(0,1fr));border-top:0;gap:0}.service-rail nav a,.rail-disabled{padding:.5rem .35rem .45rem;text-align:center;border-bottom:0;border-right:1px solid var(--rule);font-size:.68rem}.service-rail nav a::before,.rail-disabled::before{position:static;display:block;margin-bottom:.12rem}.service-rail nav>:nth-child(6){display:none}.app-shell{width:min(100% - 24px,720px);padding-top:1rem}.metric-grid{grid-template-columns:1fr}.metric{border-right:0;border-bottom:1px solid var(--rule)}.metric:last-child{border-bottom:0}.result-head{grid-template-columns:1fr}.choice span{margin-left:0}}
      @media(max-width:390px){.app-topbar{min-height:56px;padding:.65rem .8rem}.brand-system,.brand-divider{display:none}.service-rail nav{grid-template-columns:repeat(5,1fr);overflow-x:auto}.service-rail nav a,.rail-disabled{min-width:62px;font-size:.62rem}.app-shell{width:calc(100% - 18px)}main#app>h1,.result-head h1{font-size:1.65rem}section,fieldset{padding:.8rem}table{display:block;overflow-x:auto;white-space:nowrap}button,.result-actions a{width:100%;justify-content:center}}
      /* PYMIA ENTERPRISE WORKSTATION — presentation-only override */
      :root{--ink:#18211d;--ink-strong:#0f1713;--muted:#66716b;--paper:#f5f7f5;--paper-2:#ffffff;--paper-3:#eef1ee;--rule:#d9dfda;--rule-strong:#b8c1ba;--green:#185c43;--green-strong:#104632;--green-soft:#e8f1ec;--amber:#8a5b12;--amber-soft:#fff7e4;--red:#9b4038;--red-soft:#fff0ee;--slate:#52605a;--white:#ffffff;--sans:"Aptos","Segoe UI",Inter,system-ui,sans-serif;--mono:"Cascadia Mono","SFMono-Regular",Consolas,monospace;--serif:var(--sans)}
      html,body{background:#f5f7f5}body{background:#f5f7f5;font-size:15px;line-height:1.5;color:var(--ink)}
      .app-topbar{height:64px;min-height:64px;display:flex;justify-content:space-between;padding:0 24px;background:#fff;color:var(--ink-strong);border-bottom:1px solid var(--rule);box-shadow:0 1px 0 rgba(15,23,19,.02)}
      .app-brand{gap:.55rem}.brand-mark{width:18px;height:18px;grid-template-columns:repeat(3,3px);gap:2px}.brand-mark i{width:3px;background:var(--green)}.brand-mark i:nth-child(1){height:18px}.brand-mark i:nth-child(2){height:12px}.brand-mark i:nth-child(3){height:7px}.brand-word{font-family:var(--sans);font-size:.92rem;letter-spacing:.08em;font-weight:800}.brand-divider{color:#c1c8c3}.brand-system{font-size:.72rem;letter-spacing:.09em;color:#69736d;font-weight:700}.system-context{font-family:var(--sans);font-size:.72rem;color:#6d7771;gap:1rem}.system-context span{padding-left:1rem;border-left:1px solid var(--rule)}.system-context b{color:#323c36;letter-spacing:.03em;font-size:.67rem}
      .workspace{grid-template-columns:220px minmax(0,1fr);min-height:calc(100vh - 64px)}
      .service-rail{position:sticky;top:0;min-height:calc(100vh - 64px);padding:22px 14px;background:#17231d;border-right:0;color:#e9efeb}
      .rail-index{display:flex;align-items:center;justify-content:center;width:38px;height:38px;margin:0 8px 26px;padding:0;border:1px solid #3c5046;border-radius:8px;color:#fff;background:#203128;font-family:var(--sans);font-size:.78rem;letter-spacing:.08em;font-weight:800}
      .service-rail nav{gap:4px;border:0}.service-rail nav a,.rail-disabled{min-height:42px;display:flex;align-items:center;padding:0 10px 0 44px;border:0;border-radius:7px;color:#bdc9c2;font-size:.82rem;font-weight:600}.service-rail nav a::before,.rail-disabled::before{left:12px;top:50%;transform:translateY(-50%);display:grid;place-items:center;width:22px;height:22px;border:1px solid #3b4d44;border-radius:5px;color:#8fa096;font-family:var(--mono);font-size:.55rem}.service-rail nav a:hover{background:#203128;color:#fff}.service-rail nav a:first-child{background:#24372d;color:#fff}.service-rail nav a:first-child::before{border-color:#5e7e6c;color:#cfe1d7;background:#1b4935}.rail-disabled{opacity:.56}.rail-note{position:absolute;left:22px;right:22px;bottom:22px;margin:0;padding:14px 0 0;border-top:1px solid #34463d;color:#82938a;font-size:.56rem;letter-spacing:.1em}
      .app-shell{width:min(1180px,calc(100% - 64px));margin:0 auto;padding:40px 0 64px}
      main#app{max-width:none}main#app>h1,.result-head h1{font-family:var(--sans);font-size:clamp(1.9rem,3vw,2.8rem);font-weight:750;letter-spacing:-.045em;line-height:1.05;color:#111a15;margin:.18rem 0 .7rem}main#app>p{max-width:780px;font-size:1rem;color:#61706a}.eyebrow{font-family:var(--sans);font-size:.69rem;letter-spacing:.08em;color:#557064;font-weight:800}.eyebrow::before{content:""}
      .page-intro{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;padding-bottom:28px;margin-bottom:24px;border-bottom:1px solid var(--rule)}.page-kicker{display:flex;align-items:center;gap:8px;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#66736c;font-weight:800}.page-kicker::before{content:"";width:8px;height:8px;border-radius:50%;background:#2d7a58;box-shadow:0 0 0 3px #e3efe8}.page-intro h1{margin:8px 0 8px;font-size:clamp(2rem,3vw,3rem);letter-spacing:-.05em;line-height:1.03}.page-intro p{max-width:780px;margin:0;color:#5f6d66;font-size:1rem}.env-badge{display:inline-flex;align-items:center;gap:7px;padding:7px 10px;border:1px solid #cfd8d2;border-radius:999px;background:#fff;color:#47534d;font-size:.68rem;font-weight:800;white-space:nowrap}.env-badge::before{content:"";width:7px;height:7px;border-radius:50%;background:#2b7a57}
      section{margin:18px 0;padding:0;background:#fff;border:1px solid var(--rule);border-left:1px solid var(--rule);border-radius:10px;overflow:hidden;box-shadow:0 1px 2px rgba(18,31,24,.03)}section>h2{margin:0;padding:16px 18px 13px;border-bottom:1px solid var(--rule);font-size:.76rem;letter-spacing:.06em;color:#536159;background:#fafbfa}section>h2::before{content:""}section>p,section>form,section>table,section>ul,section>details,section>.service-grid,section>.section-body{margin-left:18px;margin-right:18px}section>p:first-of-type{margin-top:16px}section>p:last-child{margin-bottom:18px}
      .service-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:16px;margin-bottom:18px}.service-grid .choice{margin:0}
      form{gap:12px}.choice{display:block;position:relative;padding:16px 16px 16px 44px;border:1px solid #d8dfda;border-left:1px solid #d8dfda;border-radius:8px;background:#fff;transition:border-color .15s,box-shadow .15s,background .15s}.choice::before{display:none}.choice:hover{border-color:#aebdb3;box-shadow:0 2px 8px rgba(17,31,23,.05)}.choice:has(input:checked){border-color:#2b7052;background:#f5faf7;box-shadow:0 0 0 1px #2b7052}.choice>input{position:absolute;left:16px;top:19px}.choice strong{font-size:.9rem;font-weight:750;color:#19231e}.choice span{margin:5px 0 0;color:#69756f;font-size:.79rem;line-height:1.42}.service-code{display:block;margin-bottom:5px;font-family:var(--mono);font-size:.58rem;letter-spacing:.06em;color:#708078;text-transform:uppercase}.service-state{display:inline-flex;margin-top:10px;padding:3px 6px;border-radius:4px;background:#edf5f0;color:#2e674d;font-size:.58rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase}
      fieldset{margin:6px 0;padding:16px;border:1px solid #d9dfda;border-radius:8px;background:#fbfcfb}legend{font-family:var(--sans);font-size:.68rem;letter-spacing:.05em;color:#526159}label{font-size:.82rem;font-weight:650;color:#3f4b45}input[type=text],input[type=month],input[type=number],input[type=file],select{min-height:42px;padding:8px 10px;border:1px solid #cbd3ce;border-radius:7px;background:#fff;color:#17211c;box-shadow:inset 0 1px 1px rgba(17,31,23,.02)}input:focus,select:focus{border-color:#2c6f53;outline:3px solid #e0eee6;outline-offset:0}
      button{min-height:42px;padding:0 16px;border:1px solid #174e39;border-radius:7px;background:#185c43;font-family:var(--sans);font-size:.74rem;letter-spacing:.01em;font-weight:750;text-transform:none;box-shadow:0 1px 2px rgba(15,50,35,.15)}button:hover{background:#124b36}.button-row{display:flex;gap:8px;flex-wrap:wrap}
      .notice{border-radius:8px;margin:16px 0;padding:12px 14px;background:#f4f7f5;border:1px solid #d8dfda;border-left:3px solid #39745a;color:#4f5e56;font-size:.82rem}.notice strong{color:#24322a}.upload-band{display:grid;grid-template-columns:minmax(220px,1fr) minmax(220px,1.2fr) auto;gap:12px;align-items:end;margin:4px 18px 18px;padding:16px;border:1px solid #d7dfd9;border-radius:8px;background:#f8faf8}.upload-copy{display:grid;gap:3px;align-self:center}.upload-copy strong{font-size:.84rem}.upload-copy span{font-size:.72rem;color:#6a7770}.upload-band>label.file-field{display:none}.upload-band input[type=file]{margin:0}.upload-band button{white-space:nowrap}.context-details{margin:0 18px 18px!important;background:#fbfcfb}.context-details fieldset{border:0;margin:0;border-top:1px solid var(--rule);border-radius:0}.service-grid--two{grid-template-columns:repeat(2,minmax(0,1fr))}.operations-footer{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}.operations-footer>div{display:grid;gap:3px;padding:13px 14px;border-top:2px solid #1d5f45;background:#eef4f0}.operations-footer strong{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#315945}.operations-footer span{font-size:.78rem;color:#607068}.semantic-memory{display:grid;grid-template-columns:120px minmax(0,1fr);gap:12px;margin:12px 0;padding:10px 12px;border:1px solid #dbe2dd;border-radius:7px;background:#f8faf9;font-size:.78rem}.semantic-memory b{font-size:.62rem;letter-spacing:.06em;color:#65736b}.semantic-memory span{color:#55635c}
      .semantic-card{padding:0!important}.semantic-card legend{display:block;width:100%;padding:14px 16px;border-bottom:1px solid var(--rule);font-size:.82rem;color:#28362f}.semantic-grid{display:grid;grid-template-columns:1fr 1.35fr;gap:0}.semantic-detected{padding:16px;border-right:1px solid var(--rule);background:#fafbfa}.semantic-detected small,.semantic-owner small{display:block;margin-bottom:7px;font-size:.6rem;font-weight:800;letter-spacing:.07em;color:#728078;text-transform:uppercase}.semantic-owner{padding:16px}.semantic-owner label{padding:6px 0;font-weight:600}.semantic-options{display:grid;gap:2px;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--rule)}.semantic-owner .owner-label{margin-top:8px;color:#315d49}.semantic-detected>strong{display:block;font-family:var(--mono);font-size:.76rem;color:#2f3d35}.semantic-detected>p{font-size:.8rem;color:#66736c}
      .semantic-review-form{display:block;gap:0}.semantic-review-head{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(320px,.9fr);gap:18px;padding:9px 14px;border:1px solid var(--rule);border-bottom:0;border-radius:8px 8px 0 0;background:#eef2ef;color:#69766f;font-size:.61rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase}.semantic-review-list{border:1px solid var(--rule);border-radius:0 0 8px 8px;background:#fff;overflow:hidden}.semantic-review-row{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(320px,.9fr);gap:18px;align-items:center;padding:12px 14px;border-bottom:1px solid var(--rule)}.semantic-review-row:last-child{border-bottom:0}.semantic-review-row:hover{background:#fafcfa}.semantic-review-datum{min-width:0}.semantic-review-datum .semantic-sheet{display:block;margin-bottom:2px;font-family:var(--mono);font-size:.58rem;letter-spacing:.05em;color:#7a867f;text-transform:uppercase}.semantic-review-datum strong{display:block;font-size:.84rem;color:#1b2720;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.semantic-review-datum p{margin:3px 0 0;max-width:680px;color:#6b7770;font-size:.73rem;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.semantic-review-decision{display:grid;grid-template-columns:minmax(180px,1fr) minmax(150px,.8fr);gap:6px 8px;align-items:end}.semantic-review-decision small{grid-column:1/-1;margin:0;font-size:.57rem;font-weight:800;letter-spacing:.07em;color:#728078;text-transform:uppercase}.semantic-proposal{grid-column:1/-1;margin:0;color:#34443b;font-size:.76rem}.semantic-proposal strong{color:#174f39}.semantic-owner-label{grid-column:1/-1;margin:0;font-size:.63rem;color:#315d49}.semantic-review-decision select,.semantic-review-decision input[type=text]{width:100%;min-height:36px;height:36px;padding:6px 8px;font-size:.75rem}.semantic-review-actions{position:sticky;bottom:0;z-index:5;display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:12px;padding:10px 12px;border:1px solid #cfd8d2;border-radius:8px;background:rgba(255,255,255,.96);box-shadow:0 -8px 24px rgba(22,35,28,.06);backdrop-filter:blur(8px)}.semantic-review-actions span{font-size:.7rem;color:#69766f}.semantic-memory-detail{margin:7px 0 0!important;border:0;background:transparent}.semantic-memory-detail summary{display:inline-flex;padding:0;color:#557064;font-size:.65rem;font-weight:700}.semantic-memory-detail .semantic-memory{margin:6px 0 0;padding:8px 10px;grid-template-columns:90px minmax(0,1fr);font-size:.68rem}
      .result-head{padding:0 0 22px;margin-bottom:18px;border-top:0;border-bottom:1px solid var(--rule)}.status-chip{min-height:28px;padding:0 9px;border-radius:999px;font-family:var(--sans);font-size:.61rem;letter-spacing:.04em}.status-chip::before{content:""}.metric-grid{gap:10px;border:0;background:transparent}.metric{padding:16px;border:1px solid var(--rule);border-radius:9px;background:#fff}.metric:last-child{border:1px solid var(--rule)}.metric small{font-family:var(--sans);font-size:.62rem}.metric strong{font-family:var(--sans);font-size:1.45rem;letter-spacing:-.03em}.result{font-family:var(--sans);font-size:clamp(1.7rem,3vw,2.4rem);font-weight:750;letter-spacing:-.04em}
      .result-actions{padding-top:8px}.result-actions a{min-height:40px;padding:0 14px;border-radius:7px;font-family:var(--sans);font-size:.7rem;letter-spacing:0;text-transform:none}.result-actions a.secondary{background:#fff;color:#334139;border-color:#cbd3ce}
      table{border:1px solid var(--rule);border-radius:8px;overflow:hidden;font-size:.8rem}th,td{padding:11px 12px}th{font-family:var(--sans);font-size:.61rem;background:#f7f9f7;color:#68756e}tbody tr:hover{background:#f8faf8}.case-id{font-family:var(--mono);font-size:.68rem;color:#65736b}.case-status{display:inline-flex;padding:3px 7px;border-radius:999px;background:#eef4f0;color:#39634e;font-size:.61rem;font-weight:800}
      details{border-radius:8px;background:#fff}summary{font-family:var(--sans);font-size:.72rem;letter-spacing:.01em;text-transform:none}.recon-workbench{display:grid;grid-template-columns:1fr 1fr;gap:12px}.review-item{padding:14px;border:1px solid var(--rule);border-radius:8px;background:#fff}
      @media(max-width:1024px){.workspace{grid-template-columns:190px minmax(0,1fr)}.app-shell{width:min(100% - 40px,1020px)}.service-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.system-context span:first-child{display:none}}
      @media(max-width:768px){.app-topbar{height:60px;min-height:60px;padding:0 16px}.workspace{display:block}.service-rail{position:static;min-height:auto;padding:8px;background:#17231d}.rail-index,.rail-note{display:none}.service-rail nav{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:4px}.service-rail nav a,.rail-disabled{min-height:38px;padding:0 6px;border-radius:5px;justify-content:center;text-align:center;font-size:.68rem}.service-rail nav a::before,.rail-disabled::before{display:none}.service-rail nav>:nth-child(6){display:none}.app-shell{width:min(100% - 28px,720px);padding:28px 0 48px}.service-grid{grid-template-columns:1fr}.page-intro{grid-template-columns:1fr}.env-badge{width:max-content}.semantic-grid,.recon-workbench{grid-template-columns:1fr}.semantic-detected{border-right:0;border-bottom:1px solid var(--rule)}.semantic-review-head{display:none}.semantic-review-list{border-radius:8px}.semantic-review-row{grid-template-columns:1fr;gap:10px;padding:14px}.semantic-review-datum p{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}.semantic-review-decision{grid-template-columns:1fr}.semantic-review-decision small,.semantic-owner-label{grid-column:1}.semantic-review-actions{align-items:stretch;flex-direction:column}.semantic-review-actions button{width:100%}.metric-grid{grid-template-columns:1fr}}
      @media(max-width:390px){.brand-system,.brand-divider{display:none}.app-shell{width:calc(100% - 20px)}.service-rail nav{grid-template-columns:repeat(4,1fr)}.service-rail nav>:nth-child(5),.service-rail nav>:nth-child(6){display:none}.page-intro h1,main#app>h1,.result-head h1{font-size:1.75rem}section>p,section>form,section>table,section>ul,section>details,section>.service-grid,section>.section-body{margin-left:12px;margin-right:12px}section>h2{padding-left:12px;padding-right:12px}.semantic-memory{grid-template-columns:1fr}button,.result-actions a{width:100%;justify-content:center}}
      /* CLIENT JOURNEY — interaction-first override */
      .app-topbar{height:58px;min-height:58px;padding:0 max(18px,calc((100vw - 1180px)/2));border-bottom:1px solid #dfe4e0;background:#fff;box-shadow:none}.app-brand{color:#17231d;text-decoration:none}.brand-system,.brand-divider,.system-context{display:none}.simple-nav{display:flex;align-items:center;gap:6px}.simple-nav a{padding:8px 10px;border-radius:6px;color:#56635c;text-decoration:none;font-size:.78rem;font-weight:700}.simple-nav a:hover{background:#f0f5f2;color:#174f39}.app-shell{width:min(980px,calc(100% - 40px));padding:34px 0 64px}.page-intro{align-items:start}.page-intro h1{max-width:720px}.page-intro p{max-width:720px}.env-badge{margin-top:3px}
      .flow-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;margin:20px 0 24px;border:1px solid #d7ded9;border-radius:8px;overflow:hidden;background:#d7ded9}.flow-step{padding:11px 13px;background:#fff;color:#68756e;font-size:.75rem;line-height:1.35}.flow-step strong{display:block;margin-bottom:2px;color:#35423b;font-size:.65rem;letter-spacing:.04em;text-transform:uppercase}.flow-step.is-current{background:#edf5f0;box-shadow:inset 0 -3px #247454}.flow-step.is-done strong:before{content:"✓ ";color:#247454}
      .control-workspace{padding:0 0 18px!important;border:1px solid #d9dfda!important;border-radius:10px!important;background:#fff!important;overflow:hidden}.control-workspace>h2,.control-workspace>.workspace-heading{margin:0;padding:16px 18px 13px;border-bottom:1px solid #dfe4e0;background:#fafbfa}.workspace-heading{display:flex;align-items:end;justify-content:space-between;gap:20px}.workspace-heading h2{margin:0 0 3px;font-size:.92rem;text-transform:none;letter-spacing:-.01em}.workspace-heading p{margin:0;color:#6a7770;font-size:.78rem}.control-workspace>form{margin:16px 18px 0}.control-workspace .service-grid{margin:0}.secondary-tools{margin-top:28px;border:1px solid #d9dfda;border-radius:8px;background:#fff}.secondary-tools>summary{padding:12px 14px;color:#617068;font-size:.78rem;font-weight:700}.secondary-tools>section{margin:0;border:0;border-top:1px solid #dfe4e0;border-radius:0;box-shadow:none}.operations-footer{margin-top:22px}.operations-footer>div{border-radius:7px;border-top:0;border-left:3px solid #2e7254;background:#eef5f0}
      .semantic-card{margin:0 0 14px!important;border-radius:9px!important;overflow:hidden}.semantic-card legend{font-size:.72rem!important;text-transform:none!important;letter-spacing:0!important;background:#f8faf8}.semantic-detected small,.semantic-owner small{font-size:.61rem!important}.semantic-detected>strong{font-size:.82rem!important}.semantic-owner>p{font-size:.9rem;color:#26342c}.semantic-owner label{display:block;margin:7px 0;padding:9px 10px;border:1px solid #d8dfda;border-radius:7px;background:#fff}.semantic-owner label:has(input:checked){border-color:#2c7052;background:#f0f7f3}.semantic-owner input[type=radio]{margin-right:7px}.semantic-owner input[type=text]{margin-top:8px}.semantic-evidence-values{margin:12px 0;padding:11px 12px;border:1px solid #dfe4e0;border-radius:7px;background:#f7f9f7}.semantic-evidence-values ul{display:flex;flex-wrap:wrap;gap:6px;margin:7px 0;padding:0;list-style:none}.semantic-evidence-values code{display:inline-block;padding:4px 7px;border:1px solid #d2dad4;border-radius:5px;background:#fff;font-family:var(--mono);font-size:.74rem}.semantic-evidence-values p{margin:0;color:#6b7770;font-size:.7rem}.semantic-review-actions{margin-top:12px}.semantic-review-actions span{font-size:.74rem}.semantic-review-actions button{min-width:120px}
      .result-head{padding-top:8px}.metric-grid{margin-top:20px}.result-actions{margin-top:22px}.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
      /* COMMERCIAL FRIENDLY FINISH */
      body{background:#f6f8f6;color:#17211b}.app-shell{width:min(1040px,calc(100% - 48px));padding-top:38px}.app-topbar{border-bottom:1px solid #e3e8e4}.brand-word{font-size:1rem;letter-spacing:.065em}.simple-nav a{font-size:.8rem;color:#5a675f}.page-intro{margin-bottom:18px;padding-bottom:22px;border-bottom:0}.page-intro h1{max-width:780px;font-size:clamp(2.25rem,4vw,3.35rem);font-weight:760;letter-spacing:-.055em}.page-intro p{max-width:760px;font-size:1.02rem;line-height:1.6;color:#637068}.page-kicker{color:#2f6b50}.env-badge{background:#f0f6f2;border-color:#d4e2d8;color:#315c48}.flow-steps{margin:14px 0 22px;border-color:#e0e5e1;background:#e0e5e1;box-shadow:0 1px 2px rgba(18,35,25,.03)}.flow-step{padding:12px 14px;font-size:.76rem}.flow-step strong{font-size:.64rem}.control-workspace{box-shadow:0 8px 28px rgba(28,50,38,.055)!important;border-color:#dfe5e0!important}.workspace-heading{padding:20px 22px 16px!important;background:#fff!important}.workspace-heading h2{font-size:1.05rem}.workspace-heading p{font-size:.82rem}.control-workspace>form{margin:18px 22px 0}.service-grid{gap:12px}.service-grid .choice{min-height:148px;padding:20px 18px 18px 48px;border-color:#dde4df;border-radius:10px;background:#fff}.service-grid .choice>input{left:18px;top:23px}.service-grid .choice strong{font-size:1rem;letter-spacing:-.012em}.service-grid .choice span{margin-top:8px;font-size:.81rem;line-height:1.48}.service-grid .choice:hover{border-color:#aebdb3;box-shadow:0 7px 22px rgba(25,47,35,.07);transform:translateY(-1px)}.service-grid .choice:has(input:checked){border-color:#287052;background:#f5faf7;box-shadow:0 0 0 2px rgba(40,112,82,.12)}.service-state{position:absolute;right:12px;top:12px;margin:0!important}.upload-band{grid-template-columns:minmax(170px,.8fr) minmax(280px,1.35fr) auto;margin:18px 0 22px;padding:18px 18px;border:1px dashed #aebdb3;border-radius:10px;background:#f8fbf9}.upload-copy strong{font-size:.92rem}.upload-copy span{font-size:.75rem}.upload-band input[type=file]{min-height:44px;background:#fff}.upload-band button{min-height:44px;padding-inline:20px}.context-details{margin:0 0 4px!important}.secondary-tools{margin-top:22px;background:#fbfcfb}.operations-footer>div{padding:15px 16px;background:#f2f7f4}.operations-footer strong{font-size:.7rem}.operations-footer span{font-size:.8rem;line-height:1.45}
      .semantic-card{box-shadow:0 5px 20px rgba(25,46,35,.04)}.semantic-card legend{padding:15px 18px!important;font-size:.78rem!important;font-weight:750!important}.semantic-detected,.semantic-owner{padding:18px}.semantic-detected small,.semantic-owner small{color:#61736a}.semantic-owner>p{margin:0 0 12px;font-size:.95rem;line-height:1.5}.semantic-owner label{position:relative;margin:8px 0;padding:11px 12px 11px 38px;line-height:1.4}.semantic-owner label input[type=radio]{position:absolute;left:13px;top:13px}.semantic-owner label strong{display:block;font-size:.86rem}.choice-help{display:block;margin-top:3px!important;color:#69766f!important;font-size:.74rem!important;font-weight:450!important}.semantic-evidence-values{padding:13px 14px;background:#f5f8f6}.semantic-evidence-values small{margin:0!important}.semantic-evidence-values code{font-size:.8rem}.semantic-review-actions{padding:12px 14px;border-radius:9px}.semantic-review-actions button{min-width:132px}
      .result-head{align-items:start;margin-top:4px;padding-bottom:20px}.result-head h1{font-size:clamp(2rem,3.4vw,3rem)}.result-head p{max-width:700px;margin:.45rem 0 0;color:#65716a}.metric-grid{gap:12px}.metric{padding:18px 18px;border-radius:10px}.metric strong{font-size:1.6rem}.metric--focus{border-color:#9ec2ad;background:#f1f8f4}.result-summary{padding:20px 22px!important;border-left:4px solid #2a7354!important;background:#fff!important}.result-summary>h2{padding:0 0 10px!important;border:0!important;background:transparent!important}.result-summary .result{margin:.15rem 0 .4rem;font-size:clamp(2rem,5vw,3rem)}.result-finding{font-size:1rem!important;line-height:1.55;color:#34433a!important}.result-detail{margin:10px 0;border-color:#dfe5e0;background:#fff}.result-detail summary{padding:13px 15px;font-size:.8rem;color:#3f5047}.result-detail .detail-body{padding:0 15px 14px;color:#5f6d65}.result-detail .detail-body p,.result-detail .detail-body ul{margin-top:8px}.result-actions a{min-height:42px}.notice{margin-top:16px}
      @media(max-width:768px){.app-topbar{padding:0 14px}.app-shell{width:min(100% - 24px,720px);padding-top:22px}.page-intro h1{font-size:2.05rem}.flow-steps{grid-template-columns:1fr}.flow-step{padding:9px 11px}.workspace-heading{display:block}.control-workspace>form{margin-left:12px;margin-right:12px}.simple-nav a{padding:7px 8px}.semantic-grid{grid-template-columns:1fr}.semantic-detected{border-right:0;border-bottom:1px solid #dfe4e0}.upload-band{grid-template-columns:1fr}.upload-band button{width:100%}.operations-footer{grid-template-columns:1fr}.service-grid .choice{min-height:auto}}
      @media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
    </style>
    """
    if "</head>" in template:
        template = template.replace("</head>", visual_system + "</head>")
    shell = (
        '<div class="pymia-frame">'
        '<header class="app-topbar">'
        '<a class="app-brand" href="/" aria-label="PymIA inicio">'
        '<span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>'
        '<span class="brand-word">PYMIA</span>'
        '</a>'
        '<nav class="simple-nav" aria-label="Navegación principal">'
        '<a href="/">Inicio</a>'
        '<a href="/cases">Mis casos</a>'
        '</nav>'
        '</header>'
        f'<div class="app-shell">{content}</div>'
        '</div>'
    )
    return template.replace("{{content}}", shell)


def _recent_cases_page(snapshots: list[dict[str, Any]]) -> str:
    if not snapshots:
        return """
        <main id="app" tabindex="-1">
          <p class="eyebrow">Casos</p>
          <h1>Casos recientes</h1>
          <section><p>Todavía no hay controles terminados en esta sesión.</p><a href="/">Iniciar un control</a></section>
        </main>"""
    rows = "".join(
        f'''<tr>
          <td><strong>{_esc(item.get("service_name"))}</strong></td>
          <td>{_esc(item.get("status"))}</td>
          <td>{_esc(item.get("updated_at"))}</td>
          <td><a href="/case?case_ref={_esc(item.get("case_ref"))}">Abrir caso</a></td>
        </tr>'''
        for item in snapshots
    )
    return f"""
    <main id="app" tabindex="-1">
      <p class="eyebrow">Casos</p>
      <div class="result-head"><div><h1>Casos recientes</h1><p>Volvé a abrir resultados ya ejecutados sin repetir el control.</p></div><a class="secondary" href="/">Nuevo control</a></div>
      <section aria-label="Listado de casos recientes">
        <table><thead><tr><th>Servicio</th><th>Estado</th><th>Actualizado</th><th>Acción</th></tr></thead><tbody>{rows}</tbody></table>
      </section>
      <p class="notice">Los casos con evidencia owner persistida sobreviven reinicios. Los resultados completos y archivos de entrega sólo se reabren mientras exista su snapshot de ejecución.</p>
    </main>"""


def _persisted_case_page(case: dict[str, Any]) -> str:
    evidence = case.get("evidence")
    rows = evidence if isinstance(evidence, list) else []
    evidence_rows = "".join(
        f'''<tr>
          <td>{_esc(item.get("sheet_ref"))}</td>
          <td>{_esc(item.get("column_ref"))}</td>
          <td>{_esc(item.get("owner_answer"))}</td>
          <td>{_esc(item.get("confirmed_at"))}</td>
        </tr>'''
        for item in rows
        if isinstance(item, dict)
    )
    return f"""
    <main id="app" tabindex="-1">
      <p class="eyebrow">Caso persistido</p>
      <div class="result-head"><div><h1>Servicio 1 · evidencia confirmada</h1><p>Reingreso durable del caso {_esc(case.get("case_id"))}.</p></div><a class="secondary" href="/cases">Volver a casos</a></div>
      <section>
        <dl>
          <dt>Archivo de origen</dt><dd>{_esc(case.get("workbook_ref"))}</dd>
          <dt>Tenant</dt><dd>{_esc(case.get("tenant_id"))}</dd>
          <dt>Actor</dt><dd>{_esc(case.get("owner_actor_id"))}</dd>
        </dl>
      </section>
      <section aria-label="Evidencia confirmada por el dueño">
        <h2>Evidencia confirmada por el dueño</h2>
        <table><thead><tr><th>Hoja</th><th>Columna</th><th>Confirmación</th><th>Fecha</th></tr></thead><tbody>{evidence_rows}</tbody></table>
      </section>
      <p class="notice">La evidencia semántica es durable y no se reinterpreta al reingresar. El resultado completo y su archivo de entrega requieren un snapshot de ejecución todavía disponible.</p>
    </main>"""


def _login_page(error: str | None = None) -> str:
    return f"""
    <main id="app" tabindex="-1">
      <header class="page-intro">
        <div>
          <div class="page-kicker">Servicio 1 · Acceso</div>
          <h1>Ingresar a PymIA</h1>
          <p>Iniciá sesión para trabajar con los controles y la evidencia de tu empresa.</p>
        </div>
      </header>
      {_error(error)}
      <section aria-labelledby="login-title">
        <h2 id="login-title">Cuenta</h2>
        <form action="/login" method="post">
          <label for="email">Correo electrónico</label>
          <input id="email" name="email" type="email" autocomplete="username" required>
          <label for="password">Contraseña</label>
          <input id="password" name="password" type="password" autocomplete="current-password" required>
          <button type="submit">Ingresar</button>
        </form>
      </section>
    </main>"""


def _home_page(error: str | None = None) -> str:
    launch_states = {
        "sold_vs_collected_gap": "",
        "net_margin_real": "",
        "working_capital": "EN PRUEBA",
    }
    launch_options = "".join(
        (
            f'<label class="choice"><input type="radio" name="launch_review" value="{_esc(ref)}" required>'
            f'<strong>{_esc(name)}</strong><span>{_esc(description)}</span>'
            + (f'<span class="service-state">{_esc(launch_states[ref])}</span>' if launch_states.get(ref) else "")
            + '</label>'
        )
        for ref, name, description in _LAUNCH_REVIEW_OPTIONS
    )
    reconciliation_options = "".join(
        f'<label class="choice"><input type="radio" name="reconciliation_type" value="{_esc(ref)}" required>'
        f'<span class="service-code">RECON / {index:02d}</span><strong>{_esc(name)}</strong>'
        f'<span>{_esc(description)}</span><span class="service-state">DISPONIBLE</span></label>'
        for index, (ref, name, description) in enumerate(_RECONCILIATION_OPTIONS, start=1)
    )
    return f"""
    <main id="app" tabindex="-1">
      <header class="page-intro">
        <div>
          <div class="page-kicker">PymIA · Revisá tus números</div>
          <h1>¿Qué querés controlar hoy?</h1>
          <p>Elegí qué querés entender y subí el Excel que ya usás. PymIA ordena la información, te consulta sólo cuando una duda puede cambiar el resultado y te muestra de dónde sale cada número.</p>
        </div>
        <span class="env-badge">Operativo</span>
      </header>
      {_error(error)}

      <div class="flow-steps" aria-label="Cómo funciona">
        <div class="flow-step is-current"><strong>1 · Subir</strong>Elegís el control y el archivo.</div>
        <div class="flow-step"><strong>2 · Confirmar</strong>Revisás únicamente las dudas importantes.</div>
        <div class="flow-step"><strong>3 · Resultado</strong>Ves el cálculo, sus datos y sus límites.</div>
      </div>

      <section class="control-workspace" aria-labelledby="launch-controls">
        <div class="workspace-heading">
          <div><h2 id="launch-controls">Elegí qué querés revisar</h2><p>No hace falta preparar una planilla especial.</p></div>
        </div>
        <form action="/upload" method="post" enctype="multipart/form-data" hx-post="/upload" hx-target="#app" hx-swap="outerHTML">
          <div class="service-grid">{launch_options}</div>
          <div class="upload-band">
            <div class="upload-copy"><strong>Subí tu Excel</strong><span>.xlsx · PymIA no modifica el archivo original</span></div>
            <label class="file-field" for="file">Seleccionar archivo</label>
            <input id="file" name="file" type="file" accept=".xlsx" required>
            <button type="submit">Revisar este Excel</button>
          </div>
          <details class="context-details">
            <summary>Agregar contexto de consorcio, sólo si corresponde</summary>
            <fieldset>
              <label for="consorcio_id">Código del consorcio</label>
              <input id="consorcio_id" name="consorcio_id" type="text" autocomplete="off">
              <label for="consorcio_name">Nombre del consorcio</label>
              <input id="consorcio_name" name="consorcio_name" type="text" autocomplete="organization">
              <label for="period">Período</label>
              <input id="period" name="period" type="month">
            </fieldset>
          </details>
        </form>
      </section>

      <details class="secondary-tools">
        <summary>Necesito conciliar dos archivos</summary>
        <section aria-labelledby="bank-reconciliation">
          <h2 id="bank-reconciliation">Conciliación</h2>
          <div class="section-body"><p>Compará dos fuentes y revisá únicamente diferencias y coincidencias dudosas.</p></div>
          <form action="/start-reconciliation" method="post" hx-post="/start-reconciliation" hx-target="#app" hx-swap="outerHTML">
            <div class="service-grid service-grid--two">{reconciliation_options}</div>
            <button type="submit">Abrir conciliación</button>
          </form>
        </section>
      </details>

      <div class="operations-footer">
        <div><strong>No adivina</strong><span>Si un dato importante es ambiguo, te lo muestra antes de calcular.</span></div>
        <div><strong>Podés dejarlo pendiente</strong><span>Si no podés confirmar algo, el caso queda abierto sin inventar una respuesta.</span></div>
      </div>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _reconciliation_upload_page(
    reconciliation_type: str,
    error: str | None = None,
) -> str:
    _, title, description = _RECONCILIATION_BY_TYPE[reconciliation_type]
    file_fields = "".join(
        f'''<fieldset><legend>{_esc(source_label)}</legend>
          <label for="source_{_esc(source_kind)}">Elegir Excel</label>
          <input id="source_{_esc(source_kind)}" name="source_{_esc(source_kind)}" type="file" accept=".xlsx" required>
        </fieldset>'''
        for source_kind, source_label, _ in _RECONCILIATION_SOURCES[reconciliation_type]
    )
    return f"""
    <main id="app" tabindex="-1">
      <h1>{_esc(title)}</h1>
      {_error(error)}
      <p>{_esc(description)}</p>
      <p>Necesitamos las dos fuentes. No modificamos ninguno de los archivos.</p>
      <form action="/upload-reconciliation" method="post" enctype="multipart/form-data" hx-post="/upload-reconciliation" hx-target="#app" hx-swap="outerHTML">
        {file_fields}
        <button type="submit">Revisar archivos</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _reconciliation_column_confirmation_page(
    reconciliation_type: str,
    intakes: dict[str, dict[str, Any]],
    error: str | None = None,
) -> str:
    _, title, _ = _RECONCILIATION_BY_TYPE[reconciliation_type]
    source_blocks: list[str] = []
    for source_kind, source_label, field_specs in _RECONCILIATION_SOURCES[reconciliation_type]:
        intake = intakes[source_kind]
        columns = [str(item) for item in intake.get("columns") or []]
        selectors: list[str] = []
        for canonical_field, field_label in field_specs:
            options = '<option value="">Elegí una columna</option>' + "".join(
                f'<option value="{_esc(column)}">{_esc(column)}</option>'
                for column in columns
            )
            selectors.append(
                f'''<label for="bind_{_esc(source_kind)}_{_esc(canonical_field)}">{_esc(field_label)}</label>
                <select id="bind_{_esc(source_kind)}_{_esc(canonical_field)}" name="bind_{_esc(source_kind)}_{_esc(canonical_field)}" required>{options}</select>'''
            )
        source_blocks.append(
            f'''<fieldset><legend>{_esc(source_label)}</legend>
              <p>Archivo: <strong>{_esc(intake.get("filename"))}</strong></p>
              <p>Decinos qué columna representa cada dato. PymIA no lo va a adivinar.</p>
              {''.join(selectors)}
            </fieldset>'''
        )
    return f"""
    <main id="app" tabindex="-1">
      <h1>Confirmar columnas para { _esc(title.lower()) }</h1>
      {_error(error)}
      <form action="/confirm-reconciliation-columns" method="post" hx-post="/confirm-reconciliation-columns" hx-target="#app" hx-swap="outerHTML">
        {''.join(source_blocks)}
        <button type="submit">Cruzar movimientos</button>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _normalized_reconciliation_bindings(
    *,
    intake: dict[str, Any],
    visible_bindings: dict[str, str],
) -> dict[str, str] | None:
    column_refs = intake.get("column_refs")
    if not isinstance(column_refs, list):
        return None

    normalized_by_visible: dict[str, str] = {}
    for ref in column_refs:
        if not isinstance(ref, dict):
            return None
        visible = str(ref.get("column_name") or "").strip()
        normalized = str(ref.get("normalized_column_name") or "").strip()
        if not visible or not normalized:
            return None
        previous = normalized_by_visible.get(visible)
        if previous is not None and previous != normalized:
            return None
        normalized_by_visible[visible] = normalized

    normalized_bindings: dict[str, str] = {}
    for canonical_field, visible_column in visible_bindings.items():
        normalized_column = normalized_by_visible.get(visible_column)
        if not normalized_column:
            return None
        normalized_bindings[canonical_field] = normalized_column
    return normalized_bindings


def _prepare_reconciliation_rows(
    *,
    rows: list[Any],
    bindings: dict[str, str],
    reconciliation_type: str,
    source_kind: str,
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    numeric_fields = _RECONCILIATION_NUMERIC_FIELDS.get(
        reconciliation_type, {}
    ).get(source_kind, ())
    date_fields = _RECONCILIATION_DATE_FIELDS.get(
        reconciliation_type, {}
    ).get(source_kind, ())
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        for canonical_field in numeric_fields:
            source_column = bindings.get(canonical_field, "")
            if not source_column:
                continue
            numeric = _confirmed_numeric_value(row.get(source_column))
            if numeric is not None:
                row[source_column] = numeric
        for canonical_field in date_fields:
            source_column = bindings.get(canonical_field, "")
            if not source_column:
                continue
            confirmed_date = _confirmed_date_value(row.get(source_column))
            if confirmed_date is not None:
                row[source_column] = confirmed_date
        prepared.append(row)
    return prepared


def _confirmed_date_value(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.date().isoformat()


def _confirmed_numeric_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    candidates = [text]
    if text.count(",") == 1 and "." not in text:
        whole, fractional = text.split(",", 1)
        if whole.lstrip("+-").isdigit() and fractional.isdigit() and len(fractional) <= 2:
            candidates.append(whole + "." + fractional)
    for candidate in candidates:
        try:
            number = float(candidate)
        except ValueError:
            continue
        if math.isfinite(number):
            return number
    return None


def _reconciliation_result_page(
    packet: dict[str, Any],
    *,
    decisions: list[dict[str, Any]] | None = None,
    notice: str | None = None,
    error: str | None = None,
    radar_events: list[dict[str, object]] | None = None,
) -> str:
    reconciliation_run = packet.get("reconciliation_run")
    run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
    review_raw = run.get("assisted_review")
    review = review_raw if isinstance(review_raw, dict) else {}
    summary_raw = review.get("review_summary")
    summary = summary_raw if isinstance(summary_raw, dict) else {}
    reconciliation_type = str(run.get("reconciliation_type") or "")
    title = _RECONCILIATION_BY_TYPE.get(
        reconciliation_type,
        ("", "Conciliación", ""),
    )[1]
    pending_label = (
        "Operaciones de Mercado Pago sin acreditación"
        if reconciliation_type == MERCADO_PAGO_BANK_RECONCILIATION
        else "Movimientos internos sin banco"
    )
    metrics = (
        ("Coincidencias claras", summary.get("confirmed_candidates", 0)),
        ("Coincidencias probables", summary.get("probable_candidates", 0)),
        ("Casos dudosos", summary.get("ambiguous_groups", 0)),
        ("Diferencias de importe", summary.get("amount_differences", 0)),
        ("Diferencias de fecha", summary.get("date_differences", 0)),
        ("Movimientos bancarios sin pareja", summary.get("bank_pending", 0)),
        (pending_label, summary.get("internal_pending", 0)),
        ("Faltantes de evidencia", summary.get("missing_evidence", 0)),
        ("Inconsistencias de cálculo", summary.get("calculation_inconsistencies", 0)),
    )
    rows = "".join(
        f"<tr><th>{_esc(label)}</th><td>{_esc(value)}</td></tr>"
        for label, value in metrics
    )
    status_note = (
        "Falta evidencia en uno o más movimientos. Revisá los casos señalados antes de tomar una decisión."
        if packet.get("status") == STATUS_RECONCILIATION_NEEDS_EVIDENCE
        else "El cruce está preparado para revisión humana."
    )
    decision_history = list(decisions or [])
    details = _reconciliation_detail_sections(
        packet=packet,
        decisions=decision_history,
    )
    decision_count = len(decision_history)
    radar_panel = _radar_event_panel(radar_events or [])
    return f"""
    <main id="app" tabindex="-1">
      <div class="result-head"><div><p class="eyebrow">Resultado del control</p><h1>{_esc(title)}</h1></div><span class="status-chip status-review">REQUIERE REVISIÓN</span></div>
      {_error(error)}
      {f'<p class="notice">{_esc(notice)}</p>' if notice else ''}
      <section aria-labelledby="recon-summary"><h2 id="recon-summary">Qué encontramos</h2><p><strong>Revisión humana requerida.</strong> {_esc(status_note)}</p><p>Decisiones registradas en esta revisión: <strong>{decision_count}</strong>.</p><table><tbody>{rows}</tbody></table></section>
      {radar_panel}
      <section aria-labelledby="recon-review"><h2 id="recon-review">Qué necesita revisión</h2>{details}</section>
      <section aria-labelledby="recon-limits"><h2 id="recon-limits">Qué puede y qué no puede concluir PymIA</h2><p>PymIA no marcó ningún movimiento como conciliado, no modificó los archivos y no realizó ningún cierre contable.</p></section>
      <div class="result-actions"><a href="/download-reconciliation-workpaper">Descargar papel de trabajo (.xlsx)</a><a class="secondary" href="/">Volver a controles</a></div>
      <p>El archivo incluye resultados, decisiones humanas y casos todavía pendientes.</p>
      <div aria-live="polite">Resultado de conciliación listo para revisar.</div>
    </main>"""


def _radar_event_panel(events: list[dict[str, object]]) -> str:
    if not events:
        return ""
    items = []
    for event in events:
        level = str(event.get("communication_level") or "")
        observable_ref = str(event.get("observable_ref") or "")
        observed_value = event.get("observed_value")
        operator = str(event.get("operator") or "")
        comparison_value = event.get("comparison_value")
        items.append(
            "<li>"
            f"<strong>{_esc(level)}</strong> — {_esc(observable_ref)}: "
            f"valor observado <strong>{_esc(observed_value)}</strong>; "
            f"regla del dueño {_esc(operator)} {_esc(comparison_value)}."
            "</li>"
        )
    return (
        '<section aria-label="Eventos RADAR">'
        '<h2>RADAR</h2>'
        '<p>Se cumplieron reglas de observación que configuraste para este tenant.</p>'
        f"<ul>{''.join(items)}</ul>"
        '<p>El nivel mostrado es el nivel de comunicación elegido por el dueño; no es una severidad asignada por PymIA.</p>'
        "</section>"
    )


def _reconciliation_review_sections(
    packet: dict[str, Any],
) -> list[tuple[str, str, list[Any]]]:
    reconciliation_run = packet.get("reconciliation_run")
    run = reconciliation_run if isinstance(reconciliation_run, dict) else {}
    review_raw = run.get("assisted_review")
    review = review_raw if isinstance(review_raw, dict) else {}
    review_result_raw = review.get("review_result")
    review_result = review_result_raw if isinstance(review_result_raw, dict) else {}
    reconciliation_type = str(run.get("reconciliation_type") or "")
    if reconciliation_type == BANK_RECONCILIATION:
        return [
            ("exact", "Coincidencias claras", _summary_items(review_result, "exact_matches_summary")),
            ("probable", "Coincidencias probables", _summary_items(review_result, "probable_matches_summary")),
            ("ambiguous", "Casos dudosos", _summary_items(review_result, "ambiguous_matches_summary")),
            ("amount_difference", "Diferencias de importe", _summary_items(review_result, "amount_differences_summary")),
            ("date_difference", "Diferencias de fecha", _summary_items(review_result, "date_differences_summary")),
            ("bank_pending", "Banco sin pareja", _summary_items(review_result, "bank_pending_summary")),
            ("internal_pending", "Movimientos internos sin banco", _summary_items(review_result, "internal_pending_summary")),
            ("missing_evidence", "Faltantes de evidencia", _summary_items(review_result, "missing_evidence_summary")),
        ]
    if reconciliation_type == MERCADO_PAGO_BANK_RECONCILIATION:
        return [
            ("exact", "Coincidencias claras", _list_value(review_result, "conciliaciones")),
            ("ambiguous", "Casos dudosos", _list_value(review_result, "ambiguos")),
            ("amount_difference", "Diferencias de importe", _list_value(review_result, "diferencias_importe")),
            ("bank_pending", "Banco sin operación de Mercado Pago", _list_value(review_result, "movimientos_banco_sin_operacion_mp")),
            ("internal_pending", "Mercado Pago sin acreditación", _list_value(review_result, "operaciones_mp_sin_acreditacion")),
            ("calculation_inconsistency", "Inconsistencias de cálculo", _list_value(review_result, "inconsistencias_calculo")),
            ("missing_evidence", "Faltantes de evidencia", _list_value(review_result, "faltantes_evidencia")),
        ]
    return []


def _reconciliation_review_item_index(
    packet: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for category, _, items in _reconciliation_review_sections(packet):
        for position, raw_item in enumerate(items, start=1):
            item = raw_item if isinstance(raw_item, dict) else {"value": raw_item}
            item_ref = f"{category}:{position}"
            index[item_ref] = {
                "category": category,
                "item": item,
            }
    return index


def _reconciliation_detail_sections(
    *,
    packet: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> str:
    latest = {
        str(record.get("review_item_ref") or ""): record
        for record in decisions
        if isinstance(record, dict)
    }
    rendered_sections: list[str] = []
    for category, label, items in _reconciliation_review_sections(packet):
        if not items:
            continue
        rendered_items: list[str] = []
        for position, raw_item in enumerate(items, start=1):
            item = raw_item if isinstance(raw_item, dict) else {"value": raw_item}
            item_ref = f"{category}:{position}"
            current = latest.get(item_ref)
            current_text = ""
            if current:
                observation = str(current.get("observation") or "").strip()
                reviewer = str(current.get("reviewed_by") or "").strip()
                current_text = (
                    f'<p><strong>Última decisión:</strong> {_esc(current.get("decision"))}'
                    f' · Revisó: {_esc(reviewer)}'
                    f' · {_esc(current.get("decided_at"))}'
                    f'{" · " + _esc(observation) if observation else ""}</p>'
                )
            rendered_items.append(
                f'''<li>
                  <p>{_reconciliation_item_text(item)}</p>
                  {current_text}
                  <form action="/decide-reconciliation-item" method="post" hx-post="/decide-reconciliation-item" hx-target="#app" hx-swap="outerHTML">
                    <input type="hidden" name="review_item_ref" value="{_esc(item_ref)}">
                    <label for="reviewed_by_{_esc(category)}_{position}">Revisado por</label>
                    <input id="reviewed_by_{_esc(category)}_{position}" name="reviewed_by" type="text" required>
                    <label for="observation_{_esc(category)}_{position}">Observación</label>
                    <input id="observation_{_esc(category)}_{position}" name="observation" type="text" placeholder="Opcional">
                    <div>
                      <button type="submit" name="decision" value="CONFIRM">Confirmar</button>
                      <button type="submit" name="decision" value="REJECT">Rechazar</button>
                      <button type="submit" name="decision" value="PENDING">Dejar pendiente</button>
                    </div>
                  </form>
                </li>'''
            )
        rendered_sections.append(
            f"<details open><summary>{_esc(label)} ({len(items)})</summary><ol>{''.join(rendered_items)}</ol></details>"
        )
    return "".join(rendered_sections)


def _append_reconciliation_decision_jsonl(
    output_dir: Path,
    record: dict[str, Any],
) -> Path:
    target = output_dir / "reconciliation_human_decisions.jsonl"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return target


def _list_value(container: dict[str, Any], key: str) -> list[Any]:
    value = container.get(key)
    return value if isinstance(value, list) else []


def _summary_items(container: dict[str, Any], key: str) -> list[Any]:
    summary = container.get(key)
    if not isinstance(summary, dict):
        return []
    items = summary.get("items")
    return items if isinstance(items, list) else []


def _reconciliation_item_text(item: Any) -> str:
    if not isinstance(item, dict):
        return _esc(item)
    labels = {
        "banco_id": "Banco",
        "interno_id": "Interno",
        "movimiento_banco_id": "Banco",
        "operacion_mp_id": "Mercado Pago",
        "lote_id": "Lote",
        "referencia": "Referencia",
        "criterio": "Criterio",
        "importe": "Importe",
        "importe_banco": "Importe banco",
        "importe_interno": "Importe interno",
        "diferencia_absoluta": "Diferencia",
        "dias": "Días",
    }
    parts: list[str] = []
    for key, value in item.items():
        if key in {"evidencia", "requires_human_review", "tipo_match"}:
            continue
        if isinstance(value, dict):
            nested = ", ".join(
                f"{labels.get(str(nested_key), str(nested_key).replace('_', ' ').capitalize())}: {nested_value}"
                for nested_key, nested_value in value.items()
                if not isinstance(nested_value, (dict, list))
            )
            if nested:
                parts.append(nested)
        elif not isinstance(value, list):
            parts.append(
                f"{labels.get(str(key), str(key).replace('_', ' ').capitalize())}: {value}"
            )
    return _esc(" · ".join(parts) or "Caso para revisar")


def _tenant_memory_note(memory_hint: str) -> str:
    if not memory_hint:
        return '<div class="semantic-memory"><b>MEMORIA PREVIA</b><span>Sin antecedente aplicable para esta columna.</span></div>'
    return (
        '<div class="semantic-memory"><b>MEMORIA PREVIA</b><span>La vez anterior confirmaste: '
        f'<strong>{_esc(memory_hint)}</strong>. Es antecedente, no decisión automática.</span></div>'
    )


def _unit_column_evidence_preview(
    ingestion_output: Mapping[str, Any] | None,
    *,
    sheet_ref: str,
    column_ref: str,
    limit: int = 8,
) -> tuple[list[str], int]:
    if not isinstance(ingestion_output, Mapping):
        return [], 0

    evidence = ingestion_output.get("column_evidence")
    if isinstance(evidence, Mapping):
        for item in evidence.values():
            if not isinstance(item, Mapping):
                continue
            if (
                str(item.get("sheet_name") or "").strip() == sheet_ref
                and str(item.get("column_name") or "").strip() == column_ref
            ):
                values = item.get("sample_values")
                if isinstance(values, list):
                    samples: list[str] = []
                    seen: set[str] = set()
                    for value in values:
                        if value is None or (isinstance(value, str) and not value.strip()):
                            continue
                        text = str(value)
                        if text not in seen and len(samples) < limit:
                            seen.add(text)
                            samples.append(text)
                    return samples, len([value for value in values if value not in (None, "")])

    tables = ingestion_output.get("normalized_tables")
    if not isinstance(tables, list):
        return [], 0
    samples = []
    seen: set[str] = set()
    populated = 0
    for table in tables:
        if not isinstance(table, Mapping):
            continue
        if str(table.get("sheet_name") or "").strip() != sheet_ref:
            continue
        rows = table.get("rows")
        if not isinstance(rows, list):
            continue
        headers = [str(value or "").strip() for value in (table.get("headers") or [])]
        normalized_headers = [str(value or "").strip() for value in (table.get("normalized_headers") or [])]
        candidate_keys = [column_ref]
        if column_ref in headers:
            index = headers.index(column_ref)
            if index < len(normalized_headers) and normalized_headers[index]:
                candidate_keys.insert(0, normalized_headers[index])
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            key = next((candidate for candidate in candidate_keys if candidate in row), None)
            if key is None:
                continue
            value = row.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            populated += 1
            text = str(value)
            if text not in seen and len(samples) < limit:
                seen.add(text)
                samples.append(text)
    return samples, populated


def _derived_unit_questions_page(
    questions: list[dict[str, Any]],
    error: str | None = None,
    *,
    selected_units: dict[str, str] | None = None,
    ingestion_output: Mapping[str, Any] | None = None,
) -> str:
    selected_units = selected_units or {}
    cards: list[str] = []
    for question in questions:
        if not isinstance(question, Mapping) or question.get("question_kind") != "UNIT_MEANING":
            continue
        question_id = str(question.get("question_id") or "").strip()
        sheet_ref = str(question.get("sheet_ref") or "").strip()
        column_ref = str(question.get("column_ref") or "").strip()
        selected = selected_units.get(question_id, "")
        samples, _ = _unit_column_evidence_preview(
            ingestion_output,
            sheet_ref=sheet_ref,
            column_ref=column_ref,
        )
        if samples:
            sample_items = "".join(f"<li><code>{_esc(value)}</code></li>" for value in samples)
            sample_block = (
                '<div class="semantic-evidence-values"><small>Valores observados en esta columna</small>'
                f'<ul>{sample_items}</ul><p>Muestra visible: {len(samples)} valores distintos de la evidencia disponible.</p></div>'
            )
        else:
            sample_block = (
                '<div class="semantic-evidence-values"><small>Valores observados en esta columna</small>'
                '<p>No hay valores no vacíos disponibles para mostrar.</p></div>'
            )
        unit_copy = {
            "DISCOUNT_FRACTION_0_1": ("Es un porcentaje escrito como decimal", "0,10 significa 10%"),
            "DISCOUNT_PERCENT_0_100": ("Es un porcentaje escrito como número", "10 significa 10%"),
            "DISCOUNT_LINE_AMOUNT": ("Es un importe de dinero", "10 significa $10 descontados"),
        }
        option_rows: list[str] = []
        for option in (question.get("options") or []):
            if not isinstance(option, Mapping):
                continue
            unit_kind = str(option.get("unit_kind") or "").strip()
            label, example = unit_copy.get(
                unit_kind,
                (str(option.get("label") or "").strip(), str(option.get("example") or "").strip()),
            )
            option_rows.append(
                f'<label><input type="radio" name="unit_{_esc(question_id)}" value="{_esc(unit_kind)}" required'
                f'{" checked" if unit_kind == selected else ""}> '
                f'<strong>{_esc(label)}</strong><span class="choice-help">{_esc(example)}</span></label>'
            )
        options = "".join(option_rows)
        options += (
            f'<label><input type="radio" name="unit_{_esc(question_id)}" value="not_sure" required'
            f'{" checked" if selected == "not_sure" else ""}> '
            '<strong>No lo puedo confirmar ahora</strong><span class="choice-help">Lo dejamos pendiente. PymIA no supone una respuesta ni calcula con una unidad inventada.</span></label>'
        )
        cards.append(
            f'<fieldset class="semantic-card"><legend>Descuento en tu Excel</legend>'
            f'<div class="semantic-grid"><div class="semantic-detected">'
            f'<small>Columna encontrada</small><strong>{_esc(column_ref)} · hoja {_esc(sheet_ref)}</strong>'
            f'{sample_block}<p>Esta respuesta cambia la forma de calcular el importe final de cada venta.</p></div>'
            f'<div class="semantic-owner"><small>Elegí la opción que corresponde</small>'
            f'<p>¿Cómo están guardados estos descuentos en tu archivo?</p>{options}</div></div></fieldset>'
        )
    return f"""
    <main id="app" tabindex="-1">
      <header class="page-intro">
        <div><div class="page-kicker">Paso 2 de 3 · Una última duda</div>
        <h1>Confirmá cómo está expresado el descuento</h1>
        <p>Te mostramos valores reales de esa columna para que puedas decidir. Si no lo sabés ahora, dejalo pendiente: PymIA no va a suponerlo.</p></div>
        <span class="env-badge">1 dato por revisar</span>
      </header>
      <div class="flow-steps" aria-label="Progreso">
        <div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div>
        <div class="flow-step is-current"><strong>2 · Confirmar</strong>Revisá esta duda.</div>
        <div class="flow-step"><strong>3 · Resultado</strong>Se calcula si alcanza la evidencia.</div>
      </div>
      {_error(error)}
      <form action="/confirm-meanings" method="post" hx-post="/confirm-meanings" hx-target="#app" hx-swap="outerHTML">
        {''.join(cards)}
        <div class="semantic-review-actions"><span>Solo una respuesta que confirmes se usa para calcular.</span><button type="submit">Continuar</button></div>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _unit_confirmation_deferred_page(questions: list[dict[str, Any]]) -> str:
    refs = [
        f"{str(question.get('sheet_ref') or '').strip()}.{str(question.get('column_ref') or '').strip()}"
        for question in questions
        if isinstance(question, Mapping) and question.get("question_kind") == "UNIT_MEANING"
    ]
    evidence = " · ".join(ref for ref in refs if ref and ref != ".")
    return f"""
    <main id="app" tabindex="-1">
      <header class="page-intro">
        <div><div class="page-kicker">Caso abierto · Confirmación pendiente</div>
        <h1>No calculamos sin esa confirmación</h1>
        <p>Elegiste no confirmar ahora cómo está expresado el descuento. PymIA conserva el caso abierto y no supone una unidad.</p></div>
        <span class="env-badge">FALTA INFORMACIÓN</span>
      </header>
      <section>
        <h2>Evidencia pendiente</h2>
        <p><strong>{_esc(evidence or "Unidad del descuento")}</strong></p>
        <p>Cuando puedas verificarlo en tu sistema o con la persona responsable, volvé a ejecutar el control con esa evidencia.</p>
      </section>
      <section>
        <p><a href="/">Volver a Operaciones</a> · <a href="/cases">Ver casos</a></p>
      </section>
      <div class="notice" aria-live="polite">No se generó ningún cálculo ni confirmación de unidad.</div>
    </main>"""


def _friendly_semantic_ref(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "Dato del Excel"
    if "->" in raw:
        left, right = raw.split("->", 1)
        return f"{_friendly_semantic_ref(left)} ↔ {_friendly_semantic_ref(right)}"
    if "." in raw:
        sheet, column = raw.split(".", 1)
        return f"{column} · hoja {sheet}"
    return raw.replace("_", " ")


def _assisted_semantic_dialogue_page(
    decisions: list[dict[str, Any]],
    error: str | None = None,
    *,
    selected_actions: dict[str, str] | None = None,
) -> str:
    selected_actions = selected_actions or {}
    rows: list[str] = []
    for decision in decisions:
        if not isinstance(decision, Mapping):
            continue
        decision_id = str(decision.get("decision_id") or "").strip()
        if not decision_id:
            continue
        kind = str(decision.get("decision_kind") or "DECISION").strip()
        presentation = str(decision.get("presentation_text") or "").strip()
        materiality = str(decision.get("materiality_reason") or "").strip()
        refs = [
            _friendly_semantic_ref(ref)
            for ref in (
                list(decision.get("column_refs") or [])
                + list(decision.get("relationship_refs") or [])
            )
            if str(ref).strip()
        ]
        selected = selected_actions.get(decision_id, "")
        rows.append(
            f'<fieldset class="semantic-card"><legend>Dato a revisar</legend>'
            f'<div class="semantic-grid"><div class="semantic-detected">'
            f'<small>Lo que encontramos en tu Excel</small><strong>{_esc(" · ".join(refs) or decision_id)}</strong>'
            f'<p>{_esc(materiality)}</p></div><div class="semantic-owner">'
            f'<small>Lo que necesitamos confirmar</small><p>{_esc(presentation)}</p>'
            f'<label><input type="radio" name="action_{_esc(decision_id)}" value="ACCEPT" required'
            f'{" checked" if selected == "ACCEPT" else ""}> Sí, es correcto</label>'
            f'<label><input type="radio" name="action_{_esc(decision_id)}" value="REJECT"'
            f'{" checked" if selected == "REJECT" else ""}> No, no es correcto</label>'
            f'<label><input type="radio" name="action_{_esc(decision_id)}" value="CORRECT"'
            f'{" checked" if selected == "CORRECT" else ""}> Quiero corregirlo</label>'
            f'<input type="text" name="correction_{_esc(decision_id)}" placeholder="Contanos cómo debería interpretarse, si corresponde">'
            f'</div></div></fieldset>'
        )
    return f"""
    <main id="app" tabindex="-1">
      <header class="page-intro">
        <div><div class="page-kicker">Paso 2 de 3 · Confirmar</div>
        <h1>Necesito confirmar {len(rows)} {"dato" if len(rows) == 1 else "datos"}</h1>
        <p>Mostramos únicamente las dudas que pueden cambiar el resultado. Revisalas con la información de tu negocio.</p></div>
        <span class="env-badge">{len(rows)} por revisar</span>
      </header>
      <div class="flow-steps" aria-label="Progreso">
        <div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div>
        <div class="flow-step is-current"><strong>2 · Confirmar</strong>Revisá estas dudas.</div>
        <div class="flow-step"><strong>3 · Resultado</strong>Se calcula después.</div>
      </div>
      {_error(error)}
      <form action="/confirm-meanings" method="post" hx-post="/confirm-meanings" hx-target="#app" hx-swap="outerHTML">
        {''.join(rows)}
        <div class="semantic-review-actions"><span>Si algo no coincide, corregilo antes de seguir.</span><button type="submit">Continuar</button></div>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _semantic_questions_page(
    questions: list[dict[str, Any]],
    error: str | None = None,
    *,
    selected_answers: dict[str, Any] | None = None,
) -> str:
    rows = []
    selected_answers = selected_answers or {}
    for question in questions:
        raw_question_id = str(question.get("question_id") or "")
        question_id = _esc(raw_question_id)
        previous = selected_answers.get(raw_question_id)
        previous_option = str(previous.get("option_id") if isinstance(previous, dict) else previous or "").strip()
        previous_other = str(previous.get("free_text") if isinstance(previous, dict) else "").strip()
        raw_options = [
            option
            for option in (question.get("options") or [])
            if isinstance(option, dict)
        ]
        option_items = "".join(
            f'<option name="answer_{question_id}" value="{_esc(option.get("option_id"))}"{" selected" if str(option.get("option_id") or "").strip() == previous_option else ""}>{_esc(option.get("label"))}</option>'
            for option in raw_options
        )
        proposed_option = next(
            (
                option
                for option in raw_options
                if str(option.get("option_id") or "").strip() not in {"OTHER", "IGNORE"}
            ),
            None,
        )
        proposal = (
            f'<p class="semantic-proposal">PymIA interpreta: <strong>{_esc(proposed_option.get("label"))}</strong>. ¿Es correcto?</p>'
            if proposed_option is not None
            else ""
        )
        memory_hint = str(question.get("tenant_memory_hint") or "").strip()
        memory_note = (
            f'<details class="semantic-memory-detail"><summary>Memoria previa</summary>{_tenant_memory_note(memory_hint)}</details>'
            if memory_hint
            else ""
        )
        sheet_name = _esc(question.get("sheet_name") or "Hoja")
        column_name = _esc(question.get("column_name") or "Columna")
        rows.append(f"""
        <div class="semantic-review-row">
          <div class="semantic-review-datum">
            <span class="semantic-sheet">{sheet_name}</span>
            <strong>{column_name}</strong>
            <p>{_esc(question.get('context'))}</p>
            {memory_note}
          </div>
          <div class="semantic-review-decision">
            <small>Lo que PymIA propone</small>
            {proposal}
            <label for="answer_{question_id}" class="semantic-owner-label">Lo que owner confirma</label>
            <select id="answer_{question_id}" name="answer_{question_id}" required>
              <option value="" disabled{" selected" if not previous_option else ""}>Seleccionar significado…</option>
              {option_items}
              <option value="not_sure"{" selected" if previous_option == "not_sure" else ""}>No estoy seguro</option>
            </select>
            <input id="other_{question_id}" name="other_{question_id}" type="text" value="{_esc(previous_other)}" placeholder="Otra interpretación, sólo si corresponde">
          </div>
        </div>""")
    return f"""
    <main id="app" tabindex="-1">
      <header class="page-intro"><div><div class="page-kicker">Paso 2 de 3 · Confirmar</div><h1>{"Confirmar qué " + "significa cada dato"}</h1><p>PymIA ya descartó lo que no necesita. Revisá solamente estas columnas antes de continuar.</p></div><span class="env-badge">{len(questions)} por revisar</span></header>
      <div class="flow-steps" aria-label="Progreso">
        <div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div>
        <div class="flow-step is-current"><strong>2 · Confirmar</strong>Revisá las dudas.</div>
        <div class="flow-step"><strong>3 · Resultado</strong>Se calcula después.</div>
      </div>
      {_error(error)}
      <form class="semantic-review-form" action="/confirm-meanings" method="post" hx-post="/confirm-meanings" hx-target="#app" hx-swap="outerHTML">
        <div class="semantic-review-head"><span>Dato del Excel</span><span>Qué significa</span></div>
        <div class="semantic-review-list">{''.join(rows)}</div>
        <div class="semantic-review-actions"><span>Podés dejar una columna como “No estoy seguro” y retomarla después.</span><button type="submit">Continuar</button></div>
      </form>
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _review_selection_page(error: str | None = None) -> str:
    options = "".join(
        f'<label class="choice"><input type="radio" name="review" value="{_esc(ref)}" required><strong>{_esc(name)}</strong><span>{_esc(description)}</span></label>'
        for ref, name, description in _REVIEW_OPTIONS
    )
    return f"""
    <main id="app" tabindex="-1"><h1>¿Qué querés revisar?</h1>{_error(error)}
      <form action="/run-review" method="post" hx-post="/run-review" hx-target="#app" hx-swap="outerHTML">{options}<button type="submit">Ver resultado</button></form>
      <hr><p><a href="/radar">Configurar RADAR para este consorcio</a></p>
      <div class="notice" aria-live="polite"></div></main>"""


def _evaluated_result_page(
    packet: dict[str, Any],
    requested_capability: str,
    *,
    ingestion_output: dict[str, Any] | None = None,
) -> str:
    if requested_capability == "sold_vs_collected_gap":
        return _sales_collections_result_page(
            packet,
            ingestion_output=ingestion_output or {},
        )
    _, title, _ = _REVIEW_BY_REF[requested_capability]
    computation = packet.get("computation_result") if isinstance(packet.get("computation_result"), dict) else {}
    typed = computation.get("typed_result") if isinstance(computation.get("typed_result"), dict) else {}
    outcome = packet.get("bounded_outcome") if isinstance(packet.get("bounded_outcome"), dict) else {}
    value = _result_value(computation=computation, typed=typed, outcome=outcome)
    unit = typed.get("unit", "")
    data = _data_used(computation, outcome)
    limitations = outcome.get("limitations") if isinstance(outcome.get("limitations"), (list, tuple)) else []
    finding = outcome.get("finding") or "El cálculo se completó con los datos confirmados."
    download = (
        '<p><a href="/download-net-margin">Descargar resultado de margen neto real (.xlsx)</a></p>'
        if requested_capability == "net_margin_real" and packet.get("delivery_generated") is True
        else '<p class="notice">La descarga no está habilitada para esta revisión.</p>'
    )
    return f"""
    <main id="app" tabindex="-1">
      <div class="flow-steps" aria-label="Progreso">
        <div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div>
        <div class="flow-step is-done"><strong>2 · Confirmar</strong>Dudas resueltas.</div>
        <div class="flow-step is-current"><strong>3 · Resultado</strong>Listo para revisar.</div>
      </div>
      <div class="result-head"><div><p class="eyebrow">Resultado</p><h1>{_esc(title)}</h1><p>Calculado únicamente con los datos que PymIA pudo usar de forma segura.</p></div><span class="status-chip status-ready">LISTO</span></div>
      <section class="result-summary" aria-labelledby="summary-title"><h2 id="summary-title">Tu resultado</h2><p class="result"><strong>{_esc(value)} {_esc(unit)}</strong></p><p class="result-finding">{_esc(finding)}</p></section>
      <details class="result-detail"><summary>Datos utilizados</summary><div class="detail-body">{data}</div></details>
      <details class="result-detail"><summary>Qué conviene tener en cuenta</summary><div class="detail-body">
        <p>Este resultado surge de una relación matemática sobre los datos confirmados. No atribuye automáticamente causas ni decisiones de negocio.</p>
        <ul>{''.join(f'<li>{_esc(item)}</li>' for item in limitations)}</ul>
        <p><strong>Cómo se calculó:</strong> se aplicó el cálculo definido para esta revisión sobre los datos confirmados.</p>
      </div></details>
      <div class="result-actions">{download.replace('<p>', '').replace('</p>', '')}<a class="secondary" href="/">Revisar otro Excel</a><a class="secondary" href="/cases">Ver mis casos</a></div>
      <div class="notice" aria-live="polite">Resultado listo. Podés descargarlo o volver a revisar otro archivo.</div>
    </main>"""


def _working_capital_result_page(packet: dict[str, Any]) -> str:
    components = packet.get("computed_components") if isinstance(packet.get("computed_components"), dict) else {}
    cash = components.get("projected_closing_cash_balance") if isinstance(components.get("projected_closing_cash_balance"), dict) else {}
    dso = components.get("dso") if isinstance(components.get("dso"), dict) else {}
    ratio = components.get("current_ratio") if isinstance(components.get("current_ratio"), dict) else {}

    cash_value = (cash.get("computed") or {}).get("projected_closing_balance") if isinstance(cash.get("computed"), dict) else None
    dso_value = (dso.get("computed") or {}).get("dso_days") if isinstance(dso.get("computed"), dict) else None
    ratio_value = (ratio.get("computed") or {}).get("current_ratio_value") if isinstance(ratio.get("computed"), dict) else None
    ready_count = sum(value is not None for value in (cash_value, dso_value, ratio_value))
    complete = packet.get("status") == "READY"
    status_label = "LISTO" if complete else "FALTA INFORMACIÓN"
    status_class = "status-ready" if complete else "status-missing"

    def metric(label: str, value: object, suffix: str = "") -> str:
        rendered = "No disponible" if value is None else f"{value}{suffix}"
        return f'<div class="metric"><small>{_esc(label)}</small><strong>{_esc(rendered)}</strong></div>'

    missing = []
    if cash_value is None:
        missing.append("saldo inicial, cobros esperados y pagos esperados")
    if dso_value is None:
        missing.append("cuentas por cobrar, ventas del período y días")
    if ratio_value is None:
        missing.append("activo corriente y pasivo corriente")

    return f"""
    <main id="app" tabindex="-1">
      <div class="flow-steps" aria-label="Progreso">
        <div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div>
        <div class="flow-step is-done"><strong>2 · Confirmar</strong>Dudas resueltas.</div>
        <div class="flow-step is-current"><strong>3 · Resultado</strong>Listo para revisar.</div>
      </div>
      <div class="result-head"><div><p class="eyebrow">Resultado</p><h1>Caja y Capital de Trabajo</h1><p>Tres indicadores para entender la posición inmediata del negocio con la información disponible.</p></div><span class="status-chip {status_class}">{status_label}</span></div>
      <div class="metric-grid">
        {metric('Caja proyectada', cash_value)}
        {metric('Tiempo de cobro', dso_value, ' días')}
        {metric('Relación de corto plazo', ratio_value)}
      </div>
      <section class="result-summary"><h2>Qué encontramos</h2><p>Se pudieron calcular <strong>{ready_count} de 3</strong> indicadores con los datos recibidos.</p></section>
      <details class="result-detail" {'open' if missing else ''}><summary>{'Qué falta para completar el análisis' if missing else 'Datos utilizados y alcance'}</summary><div class="detail-body">
        {'<p>No faltan datos para estos tres indicadores.</p>' if not missing else '<ul>' + ''.join(f'<li>Faltan datos suficientes para { _esc(item) }.</li>' for item in missing) + '</ul>'}
        <p>Estos números describen relaciones matemáticas sobre datos confirmados. No determinan por sí solos insolvencia, mala gestión, necesidad de financiamiento ni causas del descalce.</p>
      </div></details>
      <div class="result-actions"><a class="secondary" href="/">Revisar otro Excel</a><a class="secondary" href="/cases">Ver mis casos</a></div>
      <div class="notice" aria-live="polite">Resultado de caja y corto plazo listo para revisar.</div>
    </main>"""


def _sales_collections_result_page(
    packet: dict[str, Any],
    *,
    ingestion_output: dict[str, Any],
) -> str:
    computation = packet.get("computation_result") if isinstance(packet.get("computation_result"), dict) else {}
    outcome = packet.get("bounded_outcome") if isinstance(packet.get("bounded_outcome"), dict) else {}
    inputs = computation.get("inputs") if isinstance(computation.get("inputs"), dict) else {}
    computed = computation.get("computed") if isinstance(computation.get("computed"), dict) else {}
    sold = float(inputs.get("sold_amount", 0.0))
    collected = float(inputs.get("collected_amount", 0.0))
    gap = float(computed.get("gap_amount", sold - collected))
    ratio = computed.get("collection_ratio")
    classification = str(computation.get("classification") or "")
    if gap > 0:
        commercial_finding = f"Las ventas registradas superan las cobranzas registradas por {_format_amount(gap)}."
        classification_label = "Diferencia todavía no compensada por cobranzas"
    elif gap < 0:
        commercial_finding = (
            f"Las cobranzas registradas superan las ventas registradas por {_format_amount(abs(gap))}. "
            "Revisá si existen cobranzas de otro período, anticipos o ventas faltantes."
        )
        classification_label = "Cobranzas superiores a las ventas registradas"
    else:
        commercial_finding = "Las ventas y cobranzas registradas coinciden para la información analizada."
        classification_label = "Ventas y cobranzas coincidentes"
    rate_text = (
        f"{float(ratio) * 100:.2f}%"
        if sold > 0 and isinstance(ratio, (int, float))
        else "no calculable porque no hay ventas registradas."
    )
    aggregation = computation.get("aggregation") if isinstance(computation.get("aggregation"), dict) else {}
    sources = aggregation.get("sources") if isinstance(aggregation.get("sources"), dict) else {}
    source_rows = "".join(
        f"<li>{_esc(variable)}: hoja <strong>{_esc(details.get('sheet_name'))}</strong>, "
        f"columna <strong>{_esc(details.get('column_name'))}</strong></li>"
        for variable, details in sources.items()
        if isinstance(details, dict)
    )
    filename = str(ingestion_output.get("filename") or ingestion_output.get("source_file_ref") or "").strip()
    explicit_period = ingestion_output.get("period")
    if explicit_period is None and isinstance(ingestion_output.get("provenance"), dict):
        explicit_period = ingestion_output["provenance"].get("period")
    period_text = (
        str(explicit_period).strip()
        if explicit_period is not None and str(explicit_period).strip()
        else "no identificado explícitamente en los archivos recibidos."
    )
    limitations = outcome.get("limitations") if isinstance(outcome.get("limitations"), (list, tuple)) else []
    download = (
        '<p><a href="/download-sales-collections">Descargar resultado de ventas y cobranzas (.xlsx)</a></p>'
        if packet.get("delivery_generated") is True
        else '<p class="notice">La descarga no está disponible para este resultado.</p>'
    )
    status_class = "status-review" if gap != 0 else "status-ready"
    status_label = "REQUIERE REVISIÓN" if gap != 0 else "LISTO"
    return f"""
    <main id="app" tabindex="-1">
      <div class="flow-steps" aria-label="Progreso">
        <div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div>
        <div class="flow-step is-done"><strong>2 · Confirmar</strong>Dudas resueltas.</div>
        <div class="flow-step is-current"><strong>3 · Resultado</strong>Listo para revisar.</div>
      </div>
      <div class="result-head"><div><p class="eyebrow">Resultado</p><h1>Ventas vs. cobros</h1><p><strong>Ventas y cobranzas</strong> · Cuánto vendiste, cuánto cobraste y qué diferencia queda en los registros analizados.</p></div><span class="status-chip {status_class}">{status_label}</span></div>
      <div class="metric-grid">
        <div class="metric"><small>Total vendido</small><strong>{_esc(_format_amount(sold))}</strong></div>
        <div class="metric"><small>Total cobrado</small><strong>{_esc(_format_amount(collected))}</strong></div>
        <div class="metric metric--focus"><small>Diferencia</small><strong>{_esc(_format_amount(gap))}</strong></div>
      </div>
      <section class="result-summary" aria-labelledby="finding-title"><h2 id="finding-title">Qué significa</h2><p class="result-finding"><strong>{_esc(commercial_finding)}</strong></p><p>Porcentaje cobrado: <strong>{_esc(rate_text)}</strong>. {_esc(classification_label)}.</p></section>
      <details class="result-detail"><summary>Datos utilizados</summary><div class="detail-body"><p>Archivo: <strong>{_esc(filename or 'archivo recibido')}</strong></p><ul>{source_rows or '<li>Columnas confirmadas del archivo recibido.</li>'}</ul><p>Período: {_esc(period_text)}</p></div></details>
      <details class="result-detail"><summary>Qué conviene tener en cuenta</summary><div class="detail-body"><ul>{''.join(f'<li>{_esc(item)}</li>' for item in limitations)}</ul><p>La diferencia muestra lo que surge de los registros recibidos; no determina por sí sola la causa.</p></div></details>
      <div class="result-actions">{download.replace('<p>', '').replace('</p>', '')}<a class="secondary" href="/">Revisar otro Excel</a><a class="secondary" href="/cases">Ver mis casos</a></div>
      <div class="notice" aria-live="polite">Resultado listo para revisar.</div>
    </main>"""


def _format_amount(value: float) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _result_value(*, computation: dict[str, Any], typed: dict[str, Any], outcome: dict[str, Any]) -> Any:
    if "value" in typed:
        return typed["value"]
    if "value" in computation:
        return computation["value"]
    computed = outcome.get("computed_results")
    if isinstance(computed, dict) and computed:
        return next(iter(computed.values()))
    return "No disponible"


def _data_used(computation: dict[str, Any], outcome: dict[str, Any]) -> str:
    provenance = computation.get("provenance") if isinstance(computation.get("provenance"), dict) else {}
    variables = provenance.get("variables") if isinstance(provenance.get("variables"), dict) else {}
    values = list(variables.values()) if variables else list((outcome.get("inputs_used") or {}).values())
    if not values:
        return "<p>Se usaron las columnas confirmadas del archivo.</p>"
    return "<ul>" + "".join(f"<li>Dato confirmado {index}: {_esc(value)}</li>" for index, value in enumerate(values, start=1)) + "</ul>"


def _capture_confirmed_role_v1(
    *, confirmed_roles: dict[str, str], question_id: str, selected: str, question: dict[str, Any]
) -> None:
    for option in question.get("options") or []:
        if not isinstance(option, dict) or str(option.get("option_id") or "").strip() != selected:
            continue
        linked = option.get("linked_hypothesis")
        if isinstance(linked, dict):
            role = str(linked.get("semantic_role") or "").strip()
            if role:
                confirmed_roles[question_id] = role
        return


def _blocked_result_page(packet: dict[str, Any], requested_capability: str | None = None, *, ingestion_output: dict[str, Any] | None = None, semantic_answers: dict[str, Any] | None = None) -> str:
    title = _REVIEW_BY_REF.get(
        requested_capability or "",
        _LAUNCH_REVIEW_BY_REF.get(requested_capability or "", ("", "Resultado", "")),
    )[1]
    decision = packet.get("computability_decision")
    decision = decision if isinstance(decision, dict) else {}
    groups = decision.get("missing_role_groups")
    groups = groups if isinstance(groups, list) else []
    labels = {
        "period_sales_total": "ventas totales del período",
        "period_costs_total": "costos totales del período",
        "period_taxes_total": "impuestos y comisiones del período",
        "sales_amount": "importe vendido",
        "collected_amount": "importe cobrado",
        "operation_date": "fecha de operación",
    }
    missing = []
    for group in groups:
        if isinstance(group, list):
            missing.append(" o ".join(labels.get(str(role), str(role).replace("_", " ")) for role in group))

    if requested_capability == "net_margin_real":
        derived = packet.get("derived_evidence")
        derived = derived if isinstance(derived, dict) else {}
        requirements = [str(item) for item in (derived.get("evidence_requirements") or [])]
        derived_block = str(derived.get("blocked_reason") or "").strip()
        if "DISCOUNT_UNIT_CONFIRMATION_REQUIRED" in requirements:
            evidence = (
                "<p><strong>Encontramos ventas, cantidades, precios y costos. Falta una sola definición sobre la columna de descuento.</strong></p>"
                "<p>Necesitamos saber si sus valores representan un porcentaje o un importe de dinero. Hasta confirmarlo, el margen queda pendiente.</p>"
            )
            next_step = "Volvé a revisar el descuento cuando puedas confirmar cómo está guardado en tu archivo."
        elif derived_block == "BLOCK_DERIVED_EVIDENCE_RELATIONSHIP_NOT_CONFIRMED":
            evidence = (
                "<p><strong>Encontramos las ventas y los costos, pero necesitamos confirmar cómo se relacionan los productos entre ambas hojas.</strong></p>"
                "<p>PymIA no une columnas por parecido de nombre porque una relación equivocada cambiaría el resultado.</p>"
            )
            next_step = "Confirmá qué columna identifica al mismo producto en Ventas y en Productos."
        else:
            evidence = (
                "<p><strong>Con la información actual no alcanza para cerrar el margen de forma segura.</strong></p>"
                "<p>Usamos sólo los datos presentes y confirmados. Si faltan impuestos, comisiones u otro componente necesario, el caso queda abierto en lugar de completar valores por suposición.</p>"
            )
            next_step = "Agregá el dato que falta y volvé a revisar el archivo."

    else:
        evidence = "<ul>" + "".join(f"<li>{_esc(item)}</li>" for item in missing) + "</ul>" if missing else "<p>El control necesita evidencia adicional antes de poder calcularse.</p>"
        next_step = "Subí evidencia complementaria o elegí otro control compatible con este archivo."

    return f'<main id="app" tabindex="-1"><div class="flow-steps" aria-label="Progreso"><div class="flow-step is-done"><strong>1 · Subir</strong>Excel recibido.</div><div class="flow-step is-done"><strong>2 · Confirmar</strong>Revisión realizada.</div><div class="flow-step is-current"><strong>3 · Resultado</strong>Falta un dato para completarlo.</div></div><header class="page-intro"><div><div class="page-kicker">Resultado pendiente</div><h1>Todavía no podemos cerrar {_esc(title)}</h1><p>No completamos valores por suposición. Lo que ya confirmaste queda asociado al caso para poder retomarlo.</p></div><span class="env-badge">FALTA INFORMACIÓN</span></header><section class="result-summary"><h2>Qué falta</h2>{evidence}</section><section><h2>Cómo seguir</h2><p><strong>{_esc(next_step)}</strong></p><p>Cuando esté ese dato, PymIA puede volver a ejecutar el control.</p><div class="result-actions"><a href="/">Revisar o subir otro Excel</a><a class="secondary" href="/cases">Ver mis casos</a></div></section><div class="notice" aria-live="polite">Caso guardado. No se generó un resultado incompleto. La descarga no está habilitada hasta completar la información necesaria.</div></main>'


def _canonical_tables_for_consorcios(ingestion_output: dict[str, Any]) -> list[dict[str, Any]]:
    raw = ingestion_output.get("normalized_tables")
    tables = [item for item in (raw or []) if isinstance(item, dict)]
    return [table for table in tables if isinstance(table.get("rows"), list) and table.get("rows")]


def _selected_consorcios_table(tables: list[dict[str, Any]], sheet_name: str) -> dict[str, Any]:
    selected = str(sheet_name or "").strip()
    for table in tables:
        if str(table.get("sheet_name") or "").strip() == selected:
            return table
    raise ValueError("Elegí una hoja disponible.")


def _consorcios_table_columns(table: dict[str, Any]) -> tuple[str, ...]:
    rows = table.get("rows")
    if not isinstance(rows, list):
        return ()
    columns: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in row:
            ref = str(key or "").strip()
            if ref and ref not in columns:
                columns.append(ref)
    return tuple(columns)


def _selected_consorcios_column(table: dict[str, Any], column: str) -> str:
    selected = str(column or "").strip()
    if selected not in _consorcios_table_columns(table):
        raise ValueError("Elegí una columna disponible.")
    return selected


def _consorcios_owner_governance(approved_columns: list[str]) -> dict[str, object]:
    return {
        "p5_status": "CONFIRMED",
        "p6_decisions": [
            {"column_ref": column, "status": "APPROVED"}
            for column in approved_columns
        ],
        "p7_status": "REQUIREMENT_MATCHED",
        "p8_status": "COMPUTABLE",
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _column_select(name: str, columns: tuple[str, ...]) -> str:
    options = '<option value="">Elegir columna</option>' + "".join(
        f'<option value="{_esc(column)}">{_esc(column)}</option>' for column in columns
    )
    return f'<select name="{_esc(name)}" required>{options}</select>'


def _sheet_select(name: str, tables: list[dict[str, Any]]) -> str:
    options = '<option value="">Elegir hoja</option>' + "".join(
        f'<option value="{_esc(table.get("sheet_name"))}">{_esc(table.get("sheet_name"))}</option>'
        for table in tables
    )
    return f'<select name="{_esc(name)}" required>{options}</select>'


def _consorcios_case_workspace_page(
    context: ConsorcioCaseContextV1,
    tables: list[dict[str, Any]],
    error: str | None = None,
) -> str:
    union_columns: list[str] = []
    for table in tables:
        for column in _consorcios_table_columns(table):
            if column not in union_columns:
                union_columns.append(column)
    columns = tuple(union_columns)

    aging_saved = all(
        context.collection_aging_bindings.get(key)
        for key in ("sheet_name", "unidad_funcional", "saldo_anterior", "expensa_mes")
    )
    if aging_saved:
        aging_block = """
        <p>Las columnas de este control ya fueron confirmadas para este caso.</p>
        <form action="/run-consorcios-collection-aging" method="post" hx-post="/run-consorcios-collection-aging" hx-target="#app" hx-swap="outerHTML">
          <button type="submit">Revisar cobranzas y deuda</button>
        </form>"""
    else:
        aging_block = f"""
        <p>Confirmá únicamente qué columnas representan estos datos para este caso.</p>
        <form action="/run-consorcios-collection-aging" method="post" hx-post="/run-consorcios-collection-aging" hx-target="#app" hx-swap="outerHTML">
          <label>Hoja {_sheet_select('sheet_name', tables)}</label>
          <label>Unidad funcional {_column_select('unidad_funcional', columns)}</label>
          <label>Saldo anterior {_column_select('saldo_anterior', columns)}</label>
          <label>Expensa del mes {_column_select('expensa_mes', columns)}</label>
          <button type="submit">Confirmar y revisar cobranzas</button>
        </form>"""

    expense_saved = all(
        context.expense_variance_bindings.get(key)
        for key in (
            "expense_sheet", "expense_rubro", "expense_importe", "budget_sheet",
            "budget_rubro", "presupuesto_mensual", "promedio_historico",
        )
    )
    if expense_saved:
        expense_block = """
        <p>Las columnas de gastos y presupuesto ya fueron confirmadas para este caso.</p>
        <form action="/run-consorcios-expense-variance" method="post" hx-post="/run-consorcios-expense-variance" hx-target="#app" hx-swap="outerHTML">
          <button type="submit">Revisar gastos</button>
        </form>"""
    else:
        expense_block = f"""
        <p>Confirmá únicamente las relaciones necesarias para comparar gastos.</p>
        <form action="/run-consorcios-expense-variance" method="post" hx-post="/run-consorcios-expense-variance" hx-target="#app" hx-swap="outerHTML">
          <label>Hoja de gastos {_sheet_select('expense_sheet', tables)}</label>
          <label>Rubro gasto {_column_select('expense_rubro', columns)}</label>
          <label>Importe gasto {_column_select('expense_importe', columns)}</label>
          <label>Hoja de presupuesto {_sheet_select('budget_sheet', tables)}</label>
          <label>Rubro presupuesto {_column_select('budget_rubro', columns)}</label>
          <label>Presupuesto mensual {_column_select('presupuesto_mensual', columns)}</label>
          <label>Promedio histórico {_column_select('promedio_historico', columns)}</label>
          <button type="submit">Confirmar y revisar gastos</button>
        </form>"""

    files = "".join(f"<li>{_esc(name)}</li>" for name in context.source_files)
    return f"""
    <main id="app" tabindex="-1">
      <h1>{_esc(context.consorcio_name)} · {_esc(context.period)}</h1>
      {_error(error)}
      <p>Estado del caso: <strong>{_esc(context.case_status)}</strong></p>
      <h2>Archivos del período</h2>
      <ul>{files}</ul>
      <section>
        <h2>Cobranzas y deuda</h2>
        {aging_block}
      </section>
      <section>
        <h2>Gastos</h2>
        {expense_block}
      </section>
      <section>
        <h2>Banco</h2>
        <p>Compará movimientos del banco con los registros internos y revisá excepciones.</p>
        <form action="/start-reconciliation" method="post" hx-post="/start-reconciliation" hx-target="#app" hx-swap="outerHTML">
          <input type="hidden" name="reconciliation_type" value="BANK_RECONCILIATION">
          <button type="submit">Conciliar banco</button>
        </form>
      </section>
      <section>
        <h2>RADAR</h2>
        <p>Definí qué situaciones querés que PymIA te comunique para este tenant.</p>
        <p><a href="/radar">Configurar RADAR</a></p>
      </section>
      <hr>
      <p><a href="/consorcios-case-summary">Ver resumen del período</a></p>
    </main>"""


def _consorcios_case_summary_page(
    *,
    context: ConsorcioCaseContextV1,
    results: dict[str, dict[str, Any]],
    reconciliation_result: dict[str, Any] | None,
    reconciliation_decisions: list[dict[str, Any]],
    radar_events: list[dict[str, object]],
) -> str:
    aging = results.get("collection_aging") if isinstance(results.get("collection_aging"), dict) else None
    expense = results.get("expense_variance") if isinstance(results.get("expense_variance"), dict) else None

    aging_rows = aging.get("rows") if isinstance(aging, dict) and isinstance(aging.get("rows"), list) else []
    expense_rows = expense.get("rows") if isinstance(expense, dict) and isinstance(expense.get("rows"), list) else []

    aging_status = (
        f"Realizado · {len(aging_rows)} unidad(es) revisada(s)"
        if aging is not None
        else "Pendiente"
    )
    expense_status = (
        f"Realizado · {len(expense_rows)} rubro(s) revisado(s)"
        if expense is not None
        else "Pendiente"
    )

    bank_status = "Pendiente"
    pending_review = 0
    download_block = "<p>No hay archivos descargables generados todavía.</p>"
    if isinstance(reconciliation_result, dict):
        item_index = _reconciliation_review_item_index(reconciliation_result)
        latest_decisions = {
            str(record.get("review_item_ref") or ""): str(record.get("decision") or "").upper()
            for record in reconciliation_decisions
            if isinstance(record, dict)
        }
        pending_review = sum(
            1
            for item_ref in item_index
            if latest_decisions.get(item_ref) not in {"CONFIRM", "REJECT"}
        )
        bank_status = f"Realizado · {len(item_index)} caso(s) para revisión"
        download_block = '<p><a href="/download-reconciliation-workpaper">Descargar papel de trabajo bancario (.xlsx)</a></p>'

    level_counts: dict[str, int] = {}
    for event in radar_events:
        level = str(event.get("communication_level") or "").strip()
        if level:
            level_counts[level] = level_counts.get(level, 0) + 1
    radar_summary = (
        "<ul>" + "".join(
            f"<li><strong>{_esc(level)}</strong>: {_esc(count)}</li>"
            for level, count in sorted(level_counts.items())
        ) + "</ul>"
        if level_counts
        else "<p>Sin eventos RADAR para los controles ejecutados en este caso.</p>"
    )

    return f"""
    <main id="app" tabindex="-1">
      <h1>Resumen del período</h1>
      <p><strong>{_esc(context.consorcio_name)}</strong> · {_esc(context.period)}</p>
      <p>Estado del caso: <strong>{_esc(context.case_status)}</strong></p>

      <section>
        <h2>Cobranzas y deuda</h2>
        <p>{_esc(aging_status)}</p>
      </section>
      <section>
        <h2>Gastos</h2>
        <p>{_esc(expense_status)}</p>
      </section>
      <section>
        <h2>Banco</h2>
        <p>{_esc(bank_status)}</p>
      </section>
      <section>
        <h2>RADAR</h2>
        {radar_summary}
        <p>Los niveles son los niveles de comunicación definidos por el dueño; PymIA no asigna severidad.</p>
      </section>
      <section>
        <h2>Pendientes de revisión</h2>
        <p>{_esc(pending_review)} caso(s) bancario(s) todavía requieren una decisión humana.</p>
      </section>
      <section>
        <h2>Descargas</h2>
        {download_block}
      </section>
      <p><a href="/consorcios-case">Volver al caso</a></p>
    </main>"""


def _consorcios_radar_analysis_page(
    tables: list[dict[str, Any]], error: str | None = None
) -> str:
    union_columns: list[str] = []
    for table in tables:
        for column in _consorcios_table_columns(table):
            if column not in union_columns:
                union_columns.append(column)
    columns = tuple(union_columns)
    return f"""
    <main id="app" tabindex="-1">
      <h1>Analizar Consorcio con RADAR</h1>
      {_error(error)}
      <p>Elegí las hojas y columnas que representan cada dato. PymIA no asigna significado sin tu confirmación.</p>
      <h2>Antigüedad de deuda</h2>
      <form action="/run-consorcios-collection-aging" method="post" hx-post="/run-consorcios-collection-aging" hx-target="#app" hx-swap="outerHTML">
        <label>Hoja {_sheet_select('sheet_name', tables)}</label>
        <label>Unidad funcional {_column_select('unidad_funcional', columns)}</label>
        <label>Saldo anterior {_column_select('saldo_anterior', columns)}</label>
        <label>Expensa del mes {_column_select('expensa_mes', columns)}</label>
        <button type="submit">Calcular y evaluar RADAR</button>
      </form>
      <h2>Gastos contra presupuesto e histórico</h2>
      <form action="/run-consorcios-expense-variance" method="post" hx-post="/run-consorcios-expense-variance" hx-target="#app" hx-swap="outerHTML">
        <label>Hoja de gastos {_sheet_select('expense_sheet', tables)}</label>
        <label>Rubro gasto {_column_select('expense_rubro', columns)}</label>
        <label>Importe gasto {_column_select('expense_importe', columns)}</label>
        <label>Hoja de presupuesto {_sheet_select('budget_sheet', tables)}</label>
        <label>Rubro presupuesto {_column_select('budget_rubro', columns)}</label>
        <label>Presupuesto mensual {_column_select('presupuesto_mensual', columns)}</label>
        <label>Promedio histórico {_column_select('promedio_historico', columns)}</label>
        <button type="submit">Comparar y evaluar RADAR</button>
      </form>
      <p><a href="/radar">Configurar reglas RADAR</a></p>
    </main>"""


def _consorcios_collection_aging_result_page(
    computation: dict[str, Any], *, radar_events: list[dict[str, object]]
) -> str:
    rows = computation.get("rows") if isinstance(computation.get("rows"), list) else []
    body = "".join(
        f'<tr><td>{_esc(row.get("unidad_funcional"))}</td><td>{_esc(row.get("saldo_anterior"))}</td><td>{_esc(row.get("expensa_mes"))}</td><td>{_esc(row.get("periodos_equivalentes"))}</td></tr>'
        for row in rows if isinstance(row, dict)
    )
    return f"""
    <main id="app" tabindex="-1"><h1>Antigüedad de deuda</h1>
      <table><thead><tr><th>Unidad</th><th>Saldo anterior</th><th>Expensa mes</th><th>Períodos equivalentes</th></tr></thead><tbody>{body}</tbody></table>
      {_radar_event_panel(radar_events)}
      <p><a href="/consorcios-case">Volver al caso</a></p>
    </main>"""


def _consorcios_expense_variance_result_page(
    computation: dict[str, Any], *, radar_events: list[dict[str, object]]
) -> str:
    rows = computation.get("rows") if isinstance(computation.get("rows"), list) else []
    body = "".join(
        f'<tr><td>{_esc(row.get("rubro"))}</td><td>{_esc(row.get("gasto_real"))}</td><td>{_esc(row.get("desvio_presupuesto_pct"))}</td><td>{_esc(row.get("desvio_promedio_pct"))}</td></tr>'
        for row in rows if isinstance(row, dict)
    )
    return f"""
    <main id="app" tabindex="-1"><h1>Gastos del consorcio</h1>
      <table><thead><tr><th>Rubro</th><th>Gasto real</th><th>Desvío presupuesto %</th><th>Desvío histórico %</th></tr></thead><tbody>{body}</tbody></table>
      {_radar_event_panel(radar_events)}
      <p><a href="/consorcios-case">Volver al caso</a></p>
    </main>"""


def _radar_owner_policy_page(menu: dict[str, object], error: str | None = None) -> str:
    observables = menu.get("observables") if isinstance(menu.get("observables"), list) else []
    cards: list[str] = []
    for item in observables:
        if not isinstance(item, dict):
            continue
        operators = item.get("supported_operators") if isinstance(item.get("supported_operators"), list) else []
        operator_options = "".join(
            f'<option value="{_esc(operator)}">{_esc(operator)}</option>'
            for operator in operators
        )
        observable_kind = str(item.get("observable_kind") or "")
        if observable_kind == "OPERATION":
            comparison_control = '<select name="comparison_value" required><option value="true">Sí</option><option value="false">No</option></select>'
        else:
            comparison_control = '<input name="comparison_value" type="number" step="any" required>'
        cards.append(f"""
        <section class="choice">
          <h2>{_esc(item.get('display_name'))}</h2>
          <p>{_esc(item.get('description') or '')}</p>
          <p>Unidad: {_esc(item.get('unit'))} · Alcance: {_esc(item.get('entity_scope'))}</p>
          <form action="/save-radar-policy" method="post" hx-post="/save-radar-policy" hx-target="#app" hx-swap="outerHTML">
            <input type="hidden" name="observable_ref" value="{_esc(item.get('observable_ref'))}">
            <input type="hidden" name="enabled" value="true">
            <label>Identificador de esta regla</label>
            <input name="policy_ref" type="text" required autocomplete="off">
            <label>Condición</label>
            <select name="operator" required>{operator_options}</select>
            <label>Valor de comparación</label>
            {comparison_control}
            <label>Nivel de comunicación</label>
            <select name="communication_level" required>
              <option value="REPORT">Reporte a demanda</option>
              <option value="NOTIFICATION">Notificación</option>
              <option value="ALERT">Alerta</option>
              <option value="URGENCY">Urgencia</option>
            </select>
            <label><input type="checkbox" name="confirmed_by_owner" value="true" required> Confirmo que esta condición y este nivel fueron elegidos por mí.</label>
            <button type="submit">Guardar regla RADAR</button>
          </form>
        </section>""")
    return f"""
    <main id="app" tabindex="-1">
      <h1>Configurar RADAR del consorcio</h1>
      {_error(error)}
      <p>Elegí qué querés observar, la frontera matemática y cómo querés que PymIA lo comunique.</p>
      <p>RADAR no decide por vos qué es riesgo, positivo o urgente.</p>
      {''.join(cards)}
      <div class="notice" aria-live="polite"></div>
    </main>"""


def _radar_owner_policy_saved_page(policy: object) -> str:
    return f"""
    <main id="app" tabindex="-1">
      <h1>Regla RADAR guardada</h1>
      <p><strong>{_esc(getattr(policy, 'observable_ref', ''))}</strong></p>
      <p>Condición: {_esc(getattr(policy, 'operator', ''))} {_esc(getattr(policy, 'comparison_value', ''))}</p>
      <p>Nivel: {_esc(getattr(policy, 'communication_level', ''))}</p>
      <p>La regla quedó asociada al tenant identificado y confirmada por el dueño.</p>
      <p><a href="/radar">Configurar otra regla</a></p>
      <div aria-live="polite">Regla RADAR guardada.</div>
    </main>"""


def _blocked_message_page(message: str) -> str:
    return f'<main id="app" tabindex="-1"><h1>No se puede continuar</h1><p role="alert">{_esc(message)}</p><p>La descarga no está habilitada.</p><div aria-live="polite">Necesita revisión.</div></main>'


def _error_page(message: str) -> str:
    return f'<main id="app" tabindex="-1"><h1>Revisar información de mi negocio</h1><p role="alert">{_esc(message)}</p><a href="/">Volver al inicio</a><div aria-live="polite">Necesita revisión.</div></main>'


def _error(message: str | None) -> str:
    return f'<p role="alert">{_esc(message)}</p>' if message else ""


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Servicio 1 assisted web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    tenant_identity_resolver = Service1SupabaseIdentityResolverV1.from_environment()
    tenant_persistence = Service1SupabasePersistenceAdapterV1.from_environment()
    radar_policy_store = Service1RadarSupabasePersistenceAdapterV1.from_environment()
    server = create_assisted_web_server_v1(
        host=args.host,
        port=args.port,
        persist_tenant_confirmation=tenant_persistence,
        load_tenant_memory=tenant_persistence.list_owner_confirmation_memory,
        load_prior_semantic_contract=tenant_persistence.load_current_semantic_contract,
        load_persisted_cases=tenant_persistence.list_persisted_cases,
        load_persisted_case=tenant_persistence.load_persisted_case,
        require_tenant_persistence=True,
        tenant_identity_resolver=tenant_identity_resolver,
        radar_policy_store=radar_policy_store,
    )
    print(f"Servicio 1 disponible en http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()


__all__ = ["AssistedWebApplicationV1", "AssistedWebSessionV1", "create_assisted_web_server_v1", "main"]

"""Local, assisted HTML flow for the single Servicio 1 product root."""
from __future__ import annotations

import argparse
import html
import json
import math
import secrets
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs

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
        require_tenant_persistence: bool = False,
        radar_policy_store: object | None = None,
    ) -> None:
        if require_tenant_persistence and persist_tenant_confirmation is None:
            raise ValueError("tenant persistence adapter is required")
        self._sessions: dict[str, AssistedWebSessionV1] = {}
        self._persist_tenant_confirmation = persist_tenant_confirmation
        self._load_tenant_memory = load_tenant_memory
        self._load_prior_semantic_contract = load_prior_semantic_contract
        self._require_tenant_persistence = require_tenant_persistence
        self._radar_policy_store = radar_policy_store
        self.output_dir = Path(output_dir) if output_dir is not None else Path(tempfile.mkdtemp(prefix="pymia-service-1-web-"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def session(self, session_id: str) -> AssistedWebSessionV1:
        return self._sessions.setdefault(session_id, AssistedWebSessionV1())

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
        self.session(session_id).consorcio_case_context = ConsorcioCaseContextV1(
            case_id=normalized_case,
            consorcio_id=normalized_consorcio,
            consorcio_name=normalized_name,
            period=normalized_period,
            source_files=files,
        )

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

    def receive_xlsx(self, *, session_id: str, filename: str, content: bytes) -> tuple[int, str]:
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

        try:
            first_run = _run_product_root(
                ingestion_output=state.ingestion_output,
                output_dir=self.output_dir,
            )
        except ValueError as error:
            if "requires at least one tool request" in str(error):
                return HTTPStatus.OK, _review_selection_page()
            raise
        if first_run.get("status") == STATUS_NEEDS_OWNER:
            state.semantic_questions = list(first_run.get("owner_questions") or [])
            state.semantic_questions = self._with_tenant_memory_hints(state)
            return HTTPStatus.OK, _semantic_questions_page(state.semantic_questions)
        if first_run.get("status") == STATUS_BLOCKED:
            return HTTPStatus.OK, _blocked_result_page(first_run)
        return HTTPStatus.OK, _review_selection_page()

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
        answers: dict[str, Any] = {}
        for question in state.semantic_questions:
            question_id = str(question.get("question_id") or "")
            selected = fields.get(f"answer_{question_id}", "").strip()
            if not selected:
                return HTTPStatus.BAD_REQUEST, _semantic_questions_page(state.semantic_questions, "Elegí una respuesta para cada columna.")
            if selected == "not_sure":
                return HTTPStatus.OK, _blocked_message_page("No se puede continuar hasta confirmar el significado de esas columnas. Podés volver a elegir el archivo cuando tengas esa información.")
            if selected == "OTHER":
                free_text = fields.get(f"other_{question_id}", "").strip()
                if not free_text:
                    return HTTPStatus.BAD_REQUEST, _semantic_questions_page(state.semantic_questions, "Explicá qué significa la columna cuando elegís Otra cosa.")
                answers[question_id] = {"option_id": "OTHER", "free_text": free_text}
            else:
                answers[question_id] = selected
        state.semantic_answers = answers
        state.semantic_questions = []
        if state.consorcio_case_context is not None and state.tenant_identity_contract is not None:
            return self.consorcios_case_workspace(session_id=session_id)
        return HTTPStatus.OK, _review_selection_page()

    def run_review(self, *, session_id: str, requested_capability: str) -> tuple[int, str]:
        state = self.session(session_id)
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
            return HTTPStatus.OK, _blocked_result_page(packet, requested_capability)

        if state.consorcio_case_context is not None:
            state.consorcio_case_context.case_status = "READY"

        try:
            self._persist_owner_confirmation_events(state=state, packet=packet)
        except Service1AssistedWebTenantPersistenceErrorV1:
            return HTTPStatus.OK, _blocked_message_page(
                "La confirmación fue recibida, pero no pudo guardarse de forma durable. No se registró como memoria del tenant."
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


def _run_product_root(
    *,
    ingestion_output: dict[str, Any],
    owner_answers: Any = None,
    requested_capability: str | None = None,
    output_dir: str | Path | None = None,
    deliver_result: bool = False,
) -> dict[str, Any]:
    return run_service_1_product_pipeline_v1(
        ingestion_output=ingestion_output,
        tool_requests=[],
        output_dir=output_dir or tempfile.gettempdir(),
        sheet_name=str(ingestion_output.get("sheet_name") or "sheet1"),
        owner_answers=owner_answers,
        requested_capability=requested_capability,
        deliver_result=deliver_result,
    )


def create_assisted_web_server_v1(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    output_dir: str | Path | None = None,
    persist_tenant_confirmation: Callable[[Any, Any], object] | None = None,
    load_tenant_memory: Callable[[str], tuple[dict[str, object], ...]] | None = None,
    load_prior_semantic_contract: Callable[[str, str, str, str, str], object | None] | None = None,
    require_tenant_persistence: bool = False,
    tenant_identity_resolver: Callable[[BaseHTTPRequestHandler], dict[str, str] | None] | None = None,
    radar_policy_store: object | None = None,
) -> ThreadingHTTPServer:
    application = AssistedWebApplicationV1(
        output_dir=output_dir,
        persist_tenant_confirmation=persist_tenant_confirmation,
        load_tenant_memory=load_tenant_memory,
        load_prior_semantic_contract=load_prior_semantic_contract,
        require_tenant_persistence=require_tenant_persistence,
        radar_policy_store=radar_policy_store,
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
            if self.path == "/":
                self._send_html(HTTPStatus.OK, _home_page())
            elif self.path == "/static/service_1_assisted_web_v1.css":
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
                    status, content_html = application.receive_xlsx(session_id=session_id, filename=filename, content=content)
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
    return template.replace("{{content}}", content)


def _home_page(error: str | None = None) -> str:
    reconciliation_options = "".join(
        f'<label class="choice"><input type="radio" name="reconciliation_type" value="{_esc(ref)}" required><strong>{_esc(name)}</strong><span>{_esc(description)}</span></label>'
        for ref, name, description in _RECONCILIATION_OPTIONS
    )
    return f"""
    <main id="app" tabindex="-1">
      <h1>Revisar información de mi negocio</h1>
      {_error(error)}
      <p>Subí un archivo de Excel y te ayudaremos a entenderlo paso a paso.</p>
      <form action="/upload" method="post" enctype="multipart/form-data" hx-post="/upload" hx-target="#app" hx-swap="outerHTML">
        <label for="file">Elegir archivo</label>
        <input id="file" name="file" type="file" accept=".xlsx" required>
        <details>
          <summary>Contexto de Consorcios (si corresponde)</summary>
          <label for="consorcio_id">Código del edificio/consorcio</label>
          <input id="consorcio_id" name="consorcio_id" type="text" autocomplete="off">
          <label for="consorcio_name">Nombre del edificio/consorcio</label>
          <input id="consorcio_name" name="consorcio_name" type="text" autocomplete="off">
          <label for="period">Período</label>
          <input id="period" name="period" type="month">
          <p>Si completás uno de estos datos, completá los tres.</p>
        </details>
        <p>Tu archivo no se modifica.</p>
        <p>Antes de hacer cálculos, te pediremos que confirmes qué significa cada dato.</p>
        <button type="submit">Continuar</button>
      </form>
      <hr>
      <h2>Conciliar movimientos</h2>
      <p>Si querés comparar dos fuentes, elegí qué tipo de conciliación necesitás.</p>
      <form action="/start-reconciliation" method="post" hx-post="/start-reconciliation" hx-target="#app" hx-swap="outerHTML">
        {reconciliation_options}
        <button type="submit">Empezar conciliación</button>
      </form>
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
      <h1>{_esc(title)}</h1>
      {_error(error)}
      {f'<p class="notice">{_esc(notice)}</p>' if notice else ''}
      <p><strong>Revisión humana requerida.</strong> {_esc(status_note)}</p>
      <p>Decisiones registradas en esta revisión: <strong>{decision_count}</strong>.</p>
      <table><tbody>{rows}</tbody></table>
      {radar_panel}
      {details}
      <p><a href="/download-reconciliation-workpaper">Descargar papel de trabajo (.xlsx)</a></p>
      <p>El archivo incluye resultados, decisiones humanas y casos todavía pendientes.</p>
      <p class="notice">PymIA no marcó ningún movimiento como conciliado, no modificó los archivos y no realizó ningún cierre contable.</p>
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
        return ""
    return (
        '<p class="notice">La vez anterior confirmaste: '
        f'<strong>{_esc(memory_hint)}</strong>. Confirmalo nuevamente para continuar.</p>'
    )


def _semantic_questions_page(questions: list[dict[str, Any]], error: str | None = None) -> str:
    items = []
    for question in questions:
        question_id = _esc(question.get("question_id"))
        options = "".join(
            f'<label><input type="radio" name="answer_{question_id}" value="{_esc(option.get("option_id"))}" required> {_esc(option.get("label"))}</label>'
            for option in question.get("options") or []
        )
        memory_hint = str(question.get("tenant_memory_hint") or "").strip()
        memory_note = _tenant_memory_note(memory_hint)
        items.append(f"""
        <fieldset><legend>{_esc(question.get('question') or '¿Qué representa esta columna?')}</legend>
          <p>{_esc(question.get('context'))}</p>{memory_note}{options}
          <label><input type="radio" name="answer_{question_id}" value="not_sure"> No estoy seguro</label>
          <label for="other_{question_id}">Si elegís Otra cosa, explicala</label><input id="other_{question_id}" name="other_{question_id}" type="text">
        </fieldset>""")
    return f"""
    <main id="app" tabindex="-1"><h1>Confirmar qué significa cada dato</h1>{_error(error)}
      <form action="/confirm-meanings" method="post" hx-post="/confirm-meanings" hx-target="#app" hx-swap="outerHTML">{''.join(items)}<button type="submit">Continuar</button></form>
      <div class="notice" aria-live="polite"></div></main>"""


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
    <main id="app" tabindex="-1"><h1>{_esc(title)}</h1>
      <p class="result"><strong>{_esc(value)} {_esc(unit)}</strong></p><p>{_esc(finding)}</p>
      <h2>Datos utilizados</h2>{data}
      <p>Este cálculo describe una relación matemática a partir de los datos confirmados.</p>
      <p>No determina por sí solo causas, problemas del negocio ni acciones a tomar.</p>
      <details><summary>Ver cómo se calculó</summary><p>Se aplicó el cálculo definido para esta revisión sobre los datos confirmados.</p></details>
      <h2>Límites de interpretación</h2><ul>{''.join(f'<li>{_esc(item)}</li>' for item in limitations)}</ul>
      {download}
      <div aria-live="polite">Resultado listo para revisar.</div></main>"""


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
    return f"""
    <main id="app" tabindex="-1">
      <h1>Ventas y cobranzas</h1>
      <p>¿Qué vendiste, qué cobraste y qué diferencia queda en tus registros?</p>
      <table><tbody>
        <tr><th>Total vendido</th><td>{_esc(_format_amount(sold))}</td></tr>
        <tr><th>Total cobrado</th><td>{_esc(_format_amount(collected))}</td></tr>
        <tr><th>Diferencia</th><td>{_esc(_format_amount(gap))}</td></tr>
        <tr><th>Porcentaje cobrado</th><td>{_esc(rate_text)}</td></tr>
        <tr><th>Clasificación</th><td>{_esc(classification_label)}</td></tr>
      </tbody></table>
      <p><strong>{_esc(commercial_finding)}</strong></p>
      <h2>Fuentes utilizadas</h2>
      <p>Archivo: <strong>{_esc(filename or 'archivo recibido')}</strong></p>
      <ul>{source_rows or '<li>Columnas confirmadas del archivo recibido.</li>'}</ul>
      <p>Período: {_esc(period_text)}</p>
      <h2>Límites de interpretación</h2>
      <ul>{''.join(f'<li>{_esc(item)}</li>' for item in limitations)}</ul>
      {download}
      <div aria-live="polite">Resultado de ventas y cobranzas listo para revisar.</div>
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


def _blocked_result_page(packet: dict[str, Any], requested_capability: str | None = None) -> str:
    title = _REVIEW_BY_REF.get(requested_capability or "", ("", "Resultado", ""))[1]
    return _blocked_message_page(f"No se puede completar {title.lower()} con los datos confirmados. Revisá las columnas elegidas o seleccioná otra revisión.")


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
        require_tenant_persistence=True,
        tenant_identity_resolver=tenant_identity_resolver,
        radar_policy_store=radar_policy_store,
    )
    print(f"Servicio 1 disponible en http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()


__all__ = ["AssistedWebApplicationV1", "AssistedWebSessionV1", "create_assisted_web_server_v1", "main"]

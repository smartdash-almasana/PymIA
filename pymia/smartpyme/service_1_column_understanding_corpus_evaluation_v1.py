"""Service 1 — Column Understanding Corpus Evaluation V1.

Pure evaluation harness for the standalone column understanding engine.
No I/O, no frontend, no orchestrator, no delivery, no LLM.

The goal is to evaluate whether the engine is mature enough to be wired
into human-facing web questions. It runs a small in-memory corpus of
PyME-like Excel column layouts, compares predicted hypotheses against
expected meanings, and reports precision/safety metrics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understandings_from_matrix_v1,
)


SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_CORPUS_EVALUATION_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

VERDICT_READY_FOR_FRONTEND: Final[str] = "READY_FOR_FRONTEND"
VERDICT_READY_WITH_FIXES: Final[str] = "READY_WITH_FIXES"
VERDICT_NOT_READY: Final[str] = "NOT_READY"

OUTCOME_EXACT_MATCH: Final[str] = "EXACT_MATCH"
OUTCOME_SAFE_QUESTION: Final[str] = "SAFE_QUESTION"
OUTCOME_SAFE_UNKNOWN: Final[str] = "SAFE_UNKNOWN"
OUTCOME_FALSE_CONFIDENT: Final[str] = "FALSE_CONFIDENT"
OUTCOME_MISSED_QUESTION: Final[str] = "MISSED_QUESTION"

ROLE_UNKNOWN: Final[str] = "unknown"


@dataclass(frozen=True)
class Service1ColumnUnderstandingCorpusColumnV1:
    column_name: str
    sample_values: tuple[Any, ...]
    inferred_type: str
    expected_semantic_role: str
    expected_variable_name: str
    must_be_confirmed: bool = False
    dangerous_if_wrong: bool = False
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnUnderstandingCorpusCaseV1:
    case_id: str
    file_name: str
    sheet_name: str
    business_scenario: str
    columns: tuple[Service1ColumnUnderstandingCorpusColumnV1, ...]

    def to_matrix(self) -> ColumnConfirmationMatrix:
        entries = [
            ColumnConfirmationEntry(
                original_column_name=column.column_name,
                sheet_name=self.sheet_name,
                sample_values=list(column.sample_values),
                inferred_type=column.inferred_type,
                suggested_semantic_role=ROLE_UNKNOWN,
                suggested_data_type=column.inferred_type,
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            )
            for column in self.columns
        ]
        return ColumnConfirmationMatrix(file_name=self.file_name, entries=entries)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnUnderstandingEvaluationRowV1:
    case_id: str
    sheet_name: str
    column_name: str
    expected_semantic_role: str
    expected_variable_name: str
    predicted_semantic_role: str
    predicted_variable_name: str
    confidence: float
    owner_question_needed: bool
    outcome: str
    dangerous_if_wrong: bool
    evidence: tuple[str, ...]
    owner_question_text: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnUnderstandingCorpusEvaluationV1:
    schema_version: str
    service_name: str
    status: str
    verdict: str
    cases_count: int
    columns_count: int
    exact_matches: int
    safe_questions: int
    safe_unknowns: int
    false_confident: int
    missed_questions: int
    dangerous_errors: int
    exact_match_rate: float
    safe_resolution_rate: float
    rows: tuple[Service1ColumnUnderstandingEvaluationRowV1, ...]
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


STATUS_READY: Final[str] = "CORPUS_EVALUATION_READY"


def build_default_service_1_column_understanding_corpus_v1() -> tuple[Service1ColumnUnderstandingCorpusCaseV1, ...]:
    """Return a deterministic PyME corpus for column-understanding evaluation."""
    return (
        Service1ColumnUnderstandingCorpusCaseV1(
            case_id="S1-CUE-001",
            file_name="ventas_simple.xlsx",
            sheet_name="Ventas",
            business_scenario="Venta simple con precio, costo y total.",
            columns=(
                _col("fecha", ("2026-06-01", "2026-06-02"), "date", "operation_date", "business_period"),
                _col("producto", ("Harina", "Azucar"), "text", "product_name", "product"),
                _col("cantidad", (10, 5, 2), "number", "quantity", "volume_sold"),
                _col("precio_unitario", (100, 250, 75), "number", "unit_sale_price", "sale_price", must=True, dangerous=True),
                _col("costo_unitario", (60, 150, 40), "number", "unit_cost_candidate", "cost", must=True, dangerous=True),
                _col("venta_total", (1000, 1250, 150), "number", "sales_amount", "sold_amount", must=True, dangerous=True),
            ),
        ),
        Service1ColumnUnderstandingCorpusCaseV1(
            case_id="S1-CUE-002",
            file_name="ventas_descuentos_impuestos.xlsx",
            sheet_name="Ventas_Detalle",
            business_scenario="Venta dificil con importes ambiguos, descuentos e impuestos.",
            columns=(
                _col("fecha_emision", ("2026-06-01", "2026-06-02"), "date", "operation_date", "business_period"),
                _col("codigo", ("SKU-1", "SKU-2"), "text", "product_identifier", "product_id"),
                _col("descripcion", ("Harina 1kg", "Azucar 1kg"), "text", "product_name", "product"),
                _col("precio_lista", (130, 260), "number", "list_price", "list_price", must=True, dangerous=True),
                _col("bonif", (10, 15), "number", "discount_candidate", "discount", must=True, dangerous=False),
                _col("iva", (21, 21), "number", "tax_amount", "taxes", must=True, dangerous=False),
                _col("importe_total", (1200, 2400), "number", "sales_amount", "sold_amount", must=True, dangerous=True),
            ),
        ),
        Service1ColumnUnderstandingCorpusCaseV1(
            case_id="S1-CUE-003",
            file_name="stock_movimientos.xlsx",
            sheet_name="Stock",
            business_scenario="Stock e inventario con columnas fuera del alcance actual del engine.",
            columns=(
                _col("sku", ("A-1", "B-2"), "text", "product_identifier", "product_id"),
                _col("producto", ("Harina", "Azucar"), "text", "product_name", "product"),
                _col("stock_inicial", (100, 80), "number", "opening_stock", "opening_stock", must=True),
                _col("entradas", (10, 20), "number", "stock_inflow", "stock_inflow", must=True),
                _col("salidas", (5, 8), "number", "stock_outflow", "stock_outflow", must=True),
                _col("stock_final", (105, 92), "number", "closing_stock", "closing_stock", must=True),
            ),
        ),
        Service1ColumnUnderstandingCorpusCaseV1(
            case_id="S1-CUE-004",
            file_name="caja_cobros.xlsx",
            sheet_name="Cobros",
            business_scenario="Caja/cobros con factura, cliente, cobrado y pendiente.",
            columns=(
                _col("fecha", ("2026-06-03", "2026-06-04"), "date", "operation_date", "business_period"),
                _col("cliente", ("Cliente A", "Cliente B"), "text", "customer_name", "customer", must=True),
                _col("factura", ("F001-1", "F001-2"), "text", "document_reference", "document_ref"),
                _col("cobrado", (5000, 3200), "number", "collected_amount", "collected_amount", must=True, dangerous=True),
                _col("pendiente", (1200, 0), "number", "accounts_receivable_amount", "accounts_receivable", must=True, dangerous=True),
                _col("medio_pago", ("Transferencia", "Efectivo"), "text", "payment_method", "payment_method", must=True),
            ),
        ),
        Service1ColumnUnderstandingCorpusCaseV1(
            case_id="S1-CUE-005",
            file_name="compras_costos.xlsx",
            sheet_name="Compras",
            business_scenario="Compras/costos con proveedor, unidades, subtotal e IVA.",
            columns=(
                _col("fecha", ("2026-06-05", "2026-06-06"), "date", "operation_date", "business_period"),
                _col("proveedor", ("Proveedor A", "Proveedor B"), "text", "supplier_name", "supplier", must=True),
                _col("producto", ("Harina", "Azucar"), "text", "product_name", "product"),
                _col("unidades", (30, 50), "number", "quantity", "volume_sold", must=True),
                _col("costo", (70, 120), "number", "unit_cost_candidate", "cost", must=True, dangerous=True),
                _col("subtotal", (2100, 6000), "number", "subtotal_amount", "subtotal_amount", must=True, dangerous=True),
                _col("iva", (441, 1260), "number", "tax_amount", "taxes", must=True),
            ),
        ),
        Service1ColumnUnderstandingCorpusCaseV1(
            case_id="S1-CUE-006",
            file_name="columnas_raras.xlsx",
            sheet_name="Datos",
            business_scenario="Columnas raras o genericas que deben quedar fail-closed.",
            columns=(
                _col("x1", ("A", "B"), "text", ROLE_UNKNOWN, ROLE_UNKNOWN, must=True),
                _col("monto", (1000, 2000), "number", ROLE_UNKNOWN, ROLE_UNKNOWN, must=True, dangerous=True),
                _col("valor", (50, 60), "number", ROLE_UNKNOWN, ROLE_UNKNOWN, must=True, dangerous=True),
                _col("ref", ("R-1", "R-2"), "text", ROLE_UNKNOWN, ROLE_UNKNOWN, must=True),
                _col("concepto", ("Ajuste", "Nota"), "text", ROLE_UNKNOWN, ROLE_UNKNOWN, must=True),
                _col("obs", ("sin novedad", "revisar"), "text", ROLE_UNKNOWN, ROLE_UNKNOWN, must=True),
            ),
        ),
    )


def evaluate_service_1_column_understanding_corpus_v1(
    corpus: tuple[Service1ColumnUnderstandingCorpusCaseV1, ...] | None = None,
) -> Service1ColumnUnderstandingCorpusEvaluationV1:
    selected_corpus = corpus or build_default_service_1_column_understanding_corpus_v1()
    rows: list[Service1ColumnUnderstandingEvaluationRowV1] = []

    for case in selected_corpus:
        matrix = case.to_matrix()
        understandings = build_column_understandings_from_matrix_v1(matrix)
        by_column = {understanding.column_name: understanding for understanding in understandings}
        expected_by_column = {column.column_name: column for column in case.columns}
        for column in case.columns:
            understanding = by_column[column.column_name]
            primary = understanding.primary_hypothesis
            predicted_role = primary.semantic_role if primary is not None else ROLE_UNKNOWN
            predicted_variable = primary.variable_name if primary is not None else ROLE_UNKNOWN
            outcome = _classify_outcome(
                expected=column,
                predicted_role=predicted_role,
                predicted_variable=predicted_variable,
                owner_question_needed=understanding.owner_question_needed,
            )
            rows.append(
                Service1ColumnUnderstandingEvaluationRowV1(
                    case_id=case.case_id,
                    sheet_name=case.sheet_name,
                    column_name=column.column_name,
                    expected_semantic_role=column.expected_semantic_role,
                    expected_variable_name=column.expected_variable_name,
                    predicted_semantic_role=predicted_role,
                    predicted_variable_name=predicted_variable,
                    confidence=understanding.confidence,
                    owner_question_needed=understanding.owner_question_needed,
                    outcome=outcome,
                    dangerous_if_wrong=column.dangerous_if_wrong,
                    evidence=tuple(understanding.evidence),
                    owner_question_text=understanding.owner_question_text,
                )
            )
        if set(by_column) != set(expected_by_column):
            raise ValueError(f"corpus case {case.case_id} did not evaluate every expected column")

    exact_matches = sum(1 for row in rows if row.outcome == OUTCOME_EXACT_MATCH)
    supported_scope_rows = [row for row in rows if row.expected_semantic_role != ROLE_UNKNOWN]
    supported_scope_exact_matches = sum(
        1 for row in supported_scope_rows if row.outcome == OUTCOME_EXACT_MATCH
    )
    supported_scope_exact_match_rate = (
        supported_scope_exact_matches / len(supported_scope_rows)
        if supported_scope_rows
        else 0.0
    )
    safe_questions = sum(1 for row in rows if row.outcome == OUTCOME_SAFE_QUESTION)
    safe_unknowns = sum(1 for row in rows if row.outcome == OUTCOME_SAFE_UNKNOWN)
    false_confident = sum(1 for row in rows if row.outcome == OUTCOME_FALSE_CONFIDENT)
    missed_questions = sum(1 for row in rows if row.outcome == OUTCOME_MISSED_QUESTION)
    dangerous_errors = sum(
        1
        for row in rows
        if row.dangerous_if_wrong and row.outcome in {OUTCOME_FALSE_CONFIDENT, OUTCOME_MISSED_QUESTION}
    )
    columns_count = len(rows)
    exact_match_rate = exact_matches / columns_count if columns_count else 0.0
    safe_resolution_rate = (
        (exact_matches + safe_questions + safe_unknowns) / columns_count if columns_count else 0.0
    )
    verdict = _resolve_verdict(
        exact_match_rate=supported_scope_exact_match_rate,
        safe_resolution_rate=safe_resolution_rate,
        dangerous_errors=dangerous_errors,
        false_confident=false_confident,
        missed_questions=missed_questions,
    )

    return Service1ColumnUnderstandingCorpusEvaluationV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=STATUS_READY,
        verdict=verdict,
        cases_count=len(selected_corpus),
        columns_count=columns_count,
        exact_matches=exact_matches,
        safe_questions=safe_questions,
        safe_unknowns=safe_unknowns,
        false_confident=false_confident,
        missed_questions=missed_questions,
        dangerous_errors=dangerous_errors,
        exact_match_rate=round(exact_match_rate, 4),
        safe_resolution_rate=round(safe_resolution_rate, 4),
        rows=tuple(rows),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={
            "corpus_policy": "in_memory_excel_like_column_layouts",
            "frontend_wiring_allowed": verdict == VERDICT_READY_FOR_FRONTEND,
            "supported_scope_columns_count": len(supported_scope_rows),
            "supported_scope_exact_matches": supported_scope_exact_matches,
            "supported_scope_exact_match_rate": round(supported_scope_exact_match_rate, 4),
            "direct_resolution_coverage": round(exact_match_rate, 4),
            "intentional_unknown_columns_count": columns_count - len(supported_scope_rows),
            "known_scope_gap": "generic headers remain fail-closed and require owner context",
        },
    )


def _col(
    column_name: str,
    sample_values: tuple[Any, ...],
    inferred_type: str,
    expected_semantic_role: str,
    expected_variable_name: str,
    *,
    must: bool = False,
    dangerous: bool = False,
    notes: str | None = None,
) -> Service1ColumnUnderstandingCorpusColumnV1:
    return Service1ColumnUnderstandingCorpusColumnV1(
        column_name=column_name,
        sample_values=sample_values,
        inferred_type=inferred_type,
        expected_semantic_role=expected_semantic_role,
        expected_variable_name=expected_variable_name,
        must_be_confirmed=must,
        dangerous_if_wrong=dangerous,
        notes=notes,
    )


def _classify_outcome(
    *,
    expected: Service1ColumnUnderstandingCorpusColumnV1,
    predicted_role: str,
    predicted_variable: str,
    owner_question_needed: bool,
) -> str:
    expected_unknown = expected.expected_semantic_role == ROLE_UNKNOWN
    predicted_unknown = predicted_role == ROLE_UNKNOWN
    exact = (
        predicted_role == expected.expected_semantic_role
        and predicted_variable == expected.expected_variable_name
    )

    if exact and not expected_unknown:
        return OUTCOME_EXACT_MATCH
    if expected_unknown and predicted_unknown and owner_question_needed:
        return OUTCOME_SAFE_UNKNOWN
    if expected.must_be_confirmed and owner_question_needed:
        return OUTCOME_SAFE_QUESTION
    if expected.must_be_confirmed and not owner_question_needed:
        return OUTCOME_MISSED_QUESTION
    if not expected_unknown and predicted_unknown and owner_question_needed:
        return OUTCOME_SAFE_QUESTION
    if not exact and not predicted_unknown and not owner_question_needed:
        return OUTCOME_FALSE_CONFIDENT
    if not exact and not predicted_unknown and owner_question_needed:
        return OUTCOME_SAFE_QUESTION
    return OUTCOME_SAFE_UNKNOWN


def _resolve_verdict(
    *,
    exact_match_rate: float,
    safe_resolution_rate: float,
    dangerous_errors: int,
    false_confident: int,
    missed_questions: int,
) -> str:
    if dangerous_errors > 0 or false_confident > 0 or missed_questions > 0:
        return VERDICT_NOT_READY
    if exact_match_rate >= 0.8 and safe_resolution_rate >= 0.95:
        return VERDICT_READY_FOR_FRONTEND
    if safe_resolution_rate >= 0.9:
        return VERDICT_READY_WITH_FIXES
    return VERDICT_NOT_READY


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_READY",
    "VERDICT_READY_FOR_FRONTEND",
    "VERDICT_READY_WITH_FIXES",
    "VERDICT_NOT_READY",
    "OUTCOME_EXACT_MATCH",
    "OUTCOME_SAFE_QUESTION",
    "OUTCOME_SAFE_UNKNOWN",
    "OUTCOME_FALSE_CONFIDENT",
    "OUTCOME_MISSED_QUESTION",
    "Service1ColumnUnderstandingCorpusColumnV1",
    "Service1ColumnUnderstandingCorpusCaseV1",
    "Service1ColumnUnderstandingEvaluationRowV1",
    "Service1ColumnUnderstandingCorpusEvaluationV1",
    "build_default_service_1_column_understanding_corpus_v1",
    "evaluate_service_1_column_understanding_corpus_v1",
]

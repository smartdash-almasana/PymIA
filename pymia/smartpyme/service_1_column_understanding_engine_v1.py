"""Service 1 — Column Understanding Engine V1.

Pure deterministic engine. No I/O. No LLM. No delivery. No runtime. No
tool execution. No mutation of inputs. Fail-closed.

For every column in a ``ColumnConfirmationMatrix`` (or in an isolated
input dict), the engine emits a ``Service1ColumnUnderstandingV1`` whose
shape is fixed by ``service_1_column_understanding_engine_contract_v1``.

The engine remains a pure component, but its matrix entrypoint is consumed by
the canonical Servicio 1 semantic bridge. Composition, owner dialogue and
execution authorization remain outside this module.

Design rules:

* Pure function of inputs. Two identical inputs produce two identical
  outputs (timestamps are absent from the contract).
* No mutation: inputs are read; the engine never assigns to caller
  data structures.
* Header name, inferred data type, sample values, and the co-column
  context of the sheet all contribute to the score of each candidate
  hypothesis. The engine never relies on the header alone.
* When the engine cannot reach the high-confidence threshold
  (``MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS``), it stays fail-closed and
  surfaces a structured owner question with multi-choice options. The
  question reads as a human operating system, not a confirmation
  request.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Final

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
)

from pymia.smartpyme.service_1_column_understanding_engine_contract_v1 import (
    HIGH_CONFIDENCE_THRESHOLD,
    INFERRED_DATA_TYPE_DATE,
    INFERRED_DATA_TYPE_EMPTY,
    INFERRED_DATA_TYPE_MIXED,
    INFERRED_DATA_TYPE_NUMBER,
    INFERRED_DATA_TYPE_TEXT,
    MAX_ALTERNATIVES,
    MAX_CANDIDATE_MEANINGS,
    MAX_OWNER_ANSWER_OPTIONS,
    MIN_CONFIDENCE_FOR_OWNER_QUESTION,
    MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS,
    OWNER_ANSWER_OTHER,
    SEMANTIC_ROLE_UNKNOWN,
    VARIABLE_NAME_UNKNOWN,
    Service1ColumnOwnerAnswerOptionV1,
    Service1ColumnUnderstandingHypothesisV1,
    Service1ColumnUnderstandingV1,
    build_service_1_column_understanding_v1,
    confidence_band_v1,
)


SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_ENGINE_V1"

HEADER_WEIGHT: Final[float] = 0.5
EXACT_HEADER_BONUS: Final[float] = 0.15
TYPE_WEIGHT: Final[float] = 0.35
CONTEXT_WEIGHT: Final[float] = 0.15
CO_COLUMN_BOOST: Final[float] = 0.1
CO_COLUMN_PENALTY: Final[float] = 0.15
SHEET_CONTEXT_BOOST: Final[float] = 0.2
SHEET_CONTEXT_PENALTY: Final[float] = 0.3
TYPE_CONTRADICTION_PENALTY: Final[float] = 0.3

# Headers that are semantically dangerous despite a strong lexical match.
# They must remain owner-confirmed until the engine has enough business
# context to distinguish list price vs effective sale price and subtotal
# vs final invoiced amount.
_OWNER_CONFIRMATION_REQUIRED_HEADERS: Final[frozenset[str]] = frozenset(
    {
        "precio_lista",
        "subtotal",
        "bonif",
        "descuento",
        "descuento_pct",
        "cobrado",
        "pendiente",
        "iva",
        "monto",
        "valor",
        "fecha_pago",
    }
)

_SHEET_ROLE_BOOSTS: Final[dict[str, tuple[str, ...]]] = {
    "sales_amount": ("venta", "ventas"),
    "purchase_amount": ("compra", "compras"),
}

_SHEET_ROLE_PENALTIES: Final[dict[str, tuple[str, ...]]] = {
    "sales_amount": ("compra", "compras", "caja", "banco"),
    "product_name": ("caja", "banco"),
}

# These headers describe consolidated amounts for one reporting period.  They
# are distinct from transaction-level totals and unit amounts: their meaning is
# only ready for P6 when the sibling period totals establish the same-period
# context on the sheet.
_PERIOD_TOTAL_HEADERS_BY_ROLE: Final[dict[str, frozenset[str]]] = {
    "period_sales_total": frozenset(
        {"ventas_periodo", "ventas_totales_periodo", "facturacion_periodo"}
    ),
    "period_costs_total": frozenset(
        {"costos_periodo", "costos_totales_periodo", "cmv_total", "cmv_periodo"}
    ),
    "period_taxes_total": frozenset(
        {"impuestos_periodo", "impuestos_y_comisiones", "impuestos_comisiones_periodo"}
    ),
}

_LEGACY_ROLE_BY_PERIOD_HEADER: Final[dict[str, str]] = {
    "ventas_periodo": "sales_amount",
    "cmv_periodo": "cost_of_goods_sold",
}

_NON_ALNUM_RE: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9_]+")
_UNDERSCORE_RE: Final[re.Pattern[str]] = re.compile(r"_+")
_DATE_TEXT_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[ T].*)?$"
)
_SLASH_DATE_RE: Final[re.Pattern[str]] = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_INT_RE: Final[re.Pattern[str]] = re.compile(r"^-?\d+$")
_FLOAT_RE: Final[re.Pattern[str]] = re.compile(r"^-?\d+(?:\.\d+)?$")


class _RoleRule:
    __slots__ = (
        "semantic_role",
        "variable_name",
        "header_keywords",
        "expected_data_types",
        "contradicting_data_types",
        "co_column_boosts",
        "co_column_penalties",
        "risk_text",
        "owner_label",
        "owner_question_text",
        "owner_option_description",
    )

    def __init__(
        self,
        *,
        semantic_role: str,
        variable_name: str,
        header_keywords: tuple[str, ...],
        expected_data_types: frozenset[str],
        contradicting_data_types: frozenset[str],
        co_column_boosts: frozenset[str],
        co_column_penalties: frozenset[str],
        risk_text: str,
        owner_label: str,
        owner_question_text: str,
        owner_option_description: str,
    ) -> None:
        self.semantic_role = semantic_role
        self.variable_name = variable_name
        self.header_keywords = header_keywords
        self.expected_data_types = expected_data_types
        self.contradicting_data_types = contradicting_data_types
        self.co_column_boosts = co_column_boosts
        self.co_column_penalties = co_column_penalties
        self.risk_text = risk_text
        self.owner_label = owner_label
        self.owner_question_text = owner_question_text
        self.owner_option_description = owner_option_description


_ROLE_RULES: Final[tuple[_RoleRule, ...]] = (
    _RoleRule(
        semantic_role="operation_date",
        variable_name="business_period",
        header_keywords=("fecha", "fecha_venta", "fecha_operacion", "date", "fecha_emision"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"venta_total", "precio_venta", "costo_unitario", "cantidad", "producto", "cliente", "factura", "comprobante"}),
        co_column_penalties=frozenset({"stock", "stock_final", "saldo"}),
        risk_text=(
            "Si esta columna no representa la fecha de la operacion, los calculos "
            "que dependen del periodo (ventas del mes, DSO, etc.) quedaran alineados "
            "al periodo equivocado."
        ),
        owner_label="Fecha de la operacion",
        owner_question_text="¿Esta columna es la fecha en que ocurrio cada operacion?",
        owner_option_description="Indica la fecha de cada venta, compra o movimiento.",
    ),
    _RoleRule(
        semantic_role="operation_time",
        variable_name="operation_time",
        header_keywords=("hora", "hora_venta", "hora_operacion", "operation_time", "time"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT, INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset(),
        co_column_boosts=frozenset({"fecha", "fecha_venta", "venta_total", "producto", "sucursal", "canal"}),
        co_column_penalties=frozenset({"stock", "saldo"}),
        risk_text="La hora de la operación no debe confundirse con una fecha completa ni con una duración.",
        owner_label="Hora de la operación",
        owner_question_text="¿Esta columna indica la hora en que ocurrió cada operación?",
        owner_option_description="Hora del día asociada a cada venta, compra o movimiento.",
    ),
    _RoleRule(
        semantic_role="transaction_identifier",
        variable_name="transaction_id",
        header_keywords=("venta_id", "ventaid", "id_venta", "transaction_id", "operacion_id", "id_operacion", "operation_id"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT, INFERRED_DATA_TYPE_NUMBER}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"fecha", "venta_total", "producto_id", "cantidad", "precio_unitario"}),
        co_column_penalties=(),
        risk_text="El identificador de transacción debe distinguir una operación y no confundirse con producto, sucursal o comprobante.",
        owner_label="Identificador de la operación",
        owner_question_text="¿Esta columna identifica de forma estable cada venta u operación?",
        owner_option_description="Código interno de la transacción u operación registrada.",
    ),
    _RoleRule(
        semantic_role="quantity",
        variable_name="volume_sold",
        header_keywords=("cantidad", "unidades", "qty", "quantity", "cant", "unidades_vendidas"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"producto", "precio_venta", "costo_unitario", "venta_total", "sku"}),
        co_column_penalties=frozenset({"fecha"}),
        risk_text=(
            "Si esta columna no es la cantidad de unidades, todos los calculos de "
            "volumen, ticket promedio y costo total por cantidad quedaran subestimados "
            "o sobreestimados."
        ),
        owner_label="Cantidad de unidades",
        owner_question_text="¿Esta columna indica cuantas unidades se vendieron, compraron o movieron?",
        owner_option_description="Numero entero o decimal de unidades por operacion.",
    ),
    _RoleRule(
        semantic_role="unit_sale_price",
        variable_name="sale_price",
        header_keywords=("precio_unitario", "precio_venta", "precio", "unit_price", "sale_price", "pvp", "precio_publico"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"producto", "cantidad", "venta_total", "sku", "categoria"}),
        co_column_penalties=frozenset({"costo_unitario"}),
        risk_text=(
            "Si esta columna es costo o lista y la usamos como precio de venta, las "
            "patologias de margen y de pricing van a diagnosticar una rentabilidad "
            "falsa."
        ),
        owner_label="Precio de venta unitario",
        owner_question_text="¿Esta columna es el precio de venta por unidad (antes o despues de descuento)?",
        owner_option_description="Importe por unidad cobrado al cliente final.",
    ),
    _RoleRule(
        semantic_role="unit_cost_candidate",
        variable_name="cost",
        header_keywords=("costo_unitario", "costo", "unit_cost", "cost", "costo_producto"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"producto", "cantidad", "precio_venta", "sku"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es costo unitario, las patologias de margen bruto y "
            "rentabilidad van a calcular margen sobre el numero equivocado."
        ),
        owner_label="Costo unitario",
        owner_question_text="¿Esta columna es el costo por unidad (costo de reposicion, costo promedio o costo real)?",
        owner_option_description="Importe por unidad que cuesta el producto.",
    ),
    _RoleRule(
        semantic_role="sales_amount",
        variable_name="sold_amount",
        header_keywords=("venta_total", "total_venta", "importe_venta", "importe_total", "ventas_periodo", "sales_amount", "sold_amount"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"cantidad", "precio_venta", "producto", "cliente", "fecha"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es el total facturado, las patologias de ventas y de "
            "descalce de caja van a estar midiendo otra cosa."
        ),
        owner_label="Venta total",
        owner_question_text="¿Esta columna es el importe total de la operacion (con o sin impuestos)?",
        owner_option_description="Importe total facturado por operacion.",
    ),
    _RoleRule(
        semantic_role="period_sales_total",
        variable_name="sale_price",
        header_keywords=("ventas_periodo", "ventas_totales_periodo", "facturacion_periodo"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"costos_periodo", "costos_totales_periodo", "cmv_total", "cmv_periodo", "impuestos_periodo", "impuestos_y_comisiones", "impuestos_comisiones_periodo"}),
        co_column_penalties=frozenset({"cantidad", "producto", "precio_unitario"}),
        risk_text="Las ventas consolidadas deben corresponder al mismo período que los costos e impuestos para calcular el margen neto.",
        owner_label="Ventas totales del período",
        owner_question_text="¿Esta columna contiene las ventas totales consolidadas del mismo período que los costos e impuestos informados?",
        owner_option_description="Importe consolidado de ventas para el período analizado.",
    ),
    _RoleRule(
        semantic_role="period_costs_total",
        variable_name="costs",
        header_keywords=("costos_periodo", "costos_totales_periodo", "cmv_total", "cmv_periodo"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"ventas_periodo", "ventas_totales_periodo", "facturacion_periodo", "impuestos_periodo", "impuestos_y_comisiones", "impuestos_comisiones_periodo"}),
        co_column_penalties=frozenset({"cantidad", "producto", "costo_unitario"}),
        risk_text="Los costos consolidados deben corresponder al mismo período que las ventas e impuestos para calcular el margen neto.",
        owner_label="Costos totales del período",
        owner_question_text="¿Esta columna contiene los costos totales consolidados del mismo período que las ventas e impuestos informados?",
        owner_option_description="Importe consolidado de costos para el período analizado.",
    ),
    _RoleRule(
        semantic_role="period_taxes_total",
        variable_name="taxes",
        header_keywords=("impuestos_periodo", "impuestos_y_comisiones", "impuestos_comisiones_periodo"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"ventas_periodo", "ventas_totales_periodo", "facturacion_periodo", "costos_periodo", "costos_totales_periodo", "cmv_total", "cmv_periodo"}),
        co_column_penalties=frozenset({"cantidad", "producto", "iva"}),
        risk_text="Los impuestos y comisiones consolidados deben corresponder al mismo período que las ventas y costos para calcular el margen neto.",
        owner_label="Impuestos y comisiones del período",
        owner_question_text="¿Esta columna contiene impuestos y comisiones totales del mismo período que las ventas y costos informados?",
        owner_option_description="Importe consolidado de impuestos y comisiones para el período analizado.",
    ),
    _RoleRule(
        semantic_role="purchase_amount",
        variable_name="purchase_amount",
        header_keywords=("importe_compra", "monto_compra", "total_compra", "importe_total"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"proveedor", "orden_compra", "costo_unitario", "cantidad_comprada", "fecha_pago"}),
        co_column_penalties=(),
        risk_text=(
            "Si este importe no corresponde a una compra, los analisis de compras y pagos "
            "quedaran asociados al monto equivocado."
        ),
        owner_label="Importe de compra",
        owner_question_text="¿Esta columna es el importe total de la compra?",
        owner_option_description="Importe total asociado a la compra o factura del proveedor.",
    ),
    _RoleRule(
        semantic_role="collected_amount",
        variable_name="collected_amount",
        header_keywords=("cobrado", "importe_cobrado", "monto_cobrado", "collected_amount"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"factura", "cliente", "fecha", "pendiente"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no representa lo efectivamente cobrado, el diagnostico de "
            "caja y cobranzas va a usar un importe equivocado."
        ),
        owner_label="Importe cobrado",
        owner_question_text="¿Esta columna indica cuánto se cobró efectivamente de cada operación?",
        owner_option_description="Importe efectivamente recibido del cliente.",
    ),
    _RoleRule(
        semantic_role="accounts_receivable_amount",
        variable_name="accounts_receivable",
        header_keywords=("pendiente", "saldo_pendiente", "por_cobrar", "accounts_receivable", "cuentas_por_cobrar"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"factura", "cliente", "fecha", "cobrado", "ventas_periodo", "periodo_dias"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es el saldo pendiente de cobro, la deuda de clientes y "
            "los indicadores de cobranza quedaran distorsionados."
        ),
        owner_label="Saldo pendiente de cobro",
        owner_question_text="¿Esta columna indica cuánto queda pendiente de cobrar por operación?",
        owner_option_description="Importe todavía adeudado por el cliente.",
    ),
    _RoleRule(
        semantic_role="initial_balance",
        variable_name="initial_balance",
        header_keywords=("saldo_inicial", "saldo_inicial_caja", "saldo_inicial_caja_banco", "initial_balance"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"cobranzas_esperadas", "pagos_esperados", "expected_collections", "expected_payments"}),
        co_column_penalties=(),
        risk_text="El saldo inicial debe ser el punto de partida explícito de la proyección de caja.",
        owner_label="Saldo inicial",
        owner_question_text="¿Esta columna representa el saldo inicial de caja o banco del período proyectado?",
        owner_option_description="Saldo disponible al inicio del período antes de cobranzas y pagos esperados.",
    ),
    _RoleRule(
        semantic_role="expected_collections",
        variable_name="expected_collections",
        header_keywords=("cobranzas_esperadas", "cobros_esperados", "expected_collections"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"saldo_inicial", "pagos_esperados", "expected_payments"}),
        co_column_penalties=(),
        risk_text="Las cobranzas esperadas deben ser evidencia explícita del período proyectado.",
        owner_label="Cobranzas esperadas",
        owner_question_text="¿Esta columna contiene las cobranzas que se espera recibir en el período?",
        owner_option_description="Importes de cobro previstos para el período proyectado.",
    ),
    _RoleRule(
        semantic_role="expected_payments",
        variable_name="expected_payments",
        header_keywords=("pagos_esperados", "egresos_esperados", "expected_payments"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"saldo_inicial", "cobranzas_esperadas", "expected_collections"}),
        co_column_penalties=(),
        risk_text="Los pagos esperados deben ser evidencia explícita del período proyectado.",
        owner_label="Pagos esperados",
        owner_question_text="¿Esta columna contiene los pagos que se espera realizar en el período?",
        owner_option_description="Importes de pago previstos para el período proyectado.",
    ),
    _RoleRule(
        semantic_role="period_days",
        variable_name="days",
        header_keywords=("periodo_dias", "dias_periodo", "period_days"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"cuentas_por_cobrar", "accounts_receivable", "ventas_periodo", "sales_amount"}),
        co_column_penalties=(),
        risk_text="La duración del período debe ser explícita y consistente con ventas y cuentas por cobrar.",
        owner_label="Días del período",
        owner_question_text="¿Esta columna indica la cantidad de días del período analizado?",
        owner_option_description="Cantidad de días usada como base temporal del indicador.",
    ),
    _RoleRule(
        semantic_role="average_sales",
        variable_name="average_sales",
        header_keywords=("average_sales", "ventas_promedio", "venta_promedio_diaria"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"lead_time", "safety_stock"}),
        co_column_penalties=(),
        risk_text="La venta promedio debe corresponder al mismo SKU y base temporal del plazo de reposición.",
        owner_label="Venta promedio",
        owner_question_text="¿Esta columna representa la venta promedio usada para calcular reposición?",
        owner_option_description="Venta promedio en unidades por día o período confirmado.",
    ),
    _RoleRule(
        semantic_role="lead_time",
        variable_name="lead_time",
        header_keywords=("lead_time", "lead_time_dias", "plazo_reposicion_dias"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"average_sales", "safety_stock"}),
        co_column_penalties=(),
        risk_text="El plazo de reposición debe estar expresado en días para el cálculo gobernado.",
        owner_label="Plazo de reposición",
        owner_question_text="¿Esta columna indica el plazo de reposición en días?",
        owner_option_description="Días entre pedido y disponibilidad del stock.",
    ),
    _RoleRule(
        semantic_role="safety_stock",
        variable_name="safety_stock",
        header_keywords=("safety_stock", "stock_seguridad"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"average_sales", "lead_time"}),
        co_column_penalties=(),
        risk_text="El stock de seguridad debe ser una cantidad explícita y confirmada.",
        owner_label="Stock de seguridad",
        owner_question_text="¿Esta columna representa el stock de seguridad?",
        owner_option_description="Cantidad reservada como stock de seguridad.",
    ),
    _RoleRule(
        semantic_role="cost_of_goods_sold",
        variable_name="cost_of_goods_sold",
        header_keywords=("cost_of_goods_sold", "costo_mercaderia_vendida", "cmv_periodo"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"average_stock", "stock_promedio"}),
        co_column_penalties=(),
        risk_text="El costo de mercadería vendida debe corresponder al mismo período que el stock promedio.",
        owner_label="Costo de mercadería vendida",
        owner_question_text="¿Esta columna contiene el costo de mercadería vendida del período?",
        owner_option_description="CMV total del período confirmado.",
    ),
    _RoleRule(
        semantic_role="average_stock",
        variable_name="average_stock",
        header_keywords=("average_stock", "stock_promedio", "inventario_promedio"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"cost_of_goods_sold", "cmv_periodo"}),
        co_column_penalties=(),
        risk_text="El stock promedio debe corresponder al mismo período y unidad monetaria del CMV.",
        owner_label="Stock promedio",
        owner_question_text="¿Esta columna representa el stock promedio del período?",
        owner_option_description="Valor promedio del inventario durante el período.",
    ),
    _RoleRule(
        semantic_role="current_assets",
        variable_name="current_assets",
        header_keywords=("current_assets", "activo_corriente"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"current_liabilities", "pasivo_corriente"}),
        co_column_penalties=(),
        risk_text="El activo corriente debe provenir del mismo corte contable que el pasivo corriente.",
        owner_label="Activo corriente",
        owner_question_text="¿Esta columna representa el activo corriente?",
        owner_option_description="Saldo de activo corriente del corte confirmado.",
    ),
    _RoleRule(
        semantic_role="current_liabilities",
        variable_name="current_liabilities",
        header_keywords=("current_liabilities", "pasivo_corriente"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"current_assets", "activo_corriente"}),
        co_column_penalties=(),
        risk_text="El pasivo corriente debe provenir del mismo corte contable que el activo corriente.",
        owner_label="Pasivo corriente",
        owner_question_text="¿Esta columna representa el pasivo corriente?",
        owner_option_description="Saldo de pasivo corriente del corte confirmado.",
    ),
    _RoleRule(
        semantic_role="main_sku_sales",
        variable_name="main_sku_sales",
        header_keywords=("main_sku_sales", "ventas_sku_principal"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"total_sales", "ventas_totales"}),
        co_column_penalties=(),
        risk_text="Las ventas del SKU principal deben pertenecer al mismo período que las ventas totales.",
        owner_label="Ventas del SKU principal",
        owner_question_text="¿Esta columna representa las ventas del SKU principal?",
        owner_option_description="Ventas monetarias del SKU con mayor participación en el período.",
    ),
    _RoleRule(
        semantic_role="total_sales",
        variable_name="total_sales",
        header_keywords=("total_sales", "ventas_totales_periodo"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"main_sku_sales", "ventas_sku_principal"}),
        co_column_penalties=(),
        risk_text="Las ventas totales deben corresponder exactamente al período de las ventas del SKU principal.",
        owner_label="Ventas totales",
        owner_question_text="¿Esta columna representa las ventas totales del período?",
        owner_option_description="Ventas monetarias totales del período confirmado.",
    ),
    _RoleRule(
        semantic_role="interest_expense",
        variable_name="interest_expense",
        header_keywords=("interest_expense", "gasto_intereses", "intereses_financieros"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"ebitda"}),
        co_column_penalties=(),
        risk_text="Los intereses deben corresponder al mismo período contable que el EBITDA.",
        owner_label="Gasto por intereses",
        owner_question_text="¿Esta columna representa el gasto financiero por intereses?",
        owner_option_description="Intereses devengados o reconocidos en el período confirmado.",
    ),
    _RoleRule(
        semantic_role="ebitda",
        variable_name="ebitda",
        header_keywords=("ebitda",),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"interest_expense", "gasto_intereses"}),
        co_column_penalties=(),
        risk_text="El resultado operativo debe corresponder al mismo período que el gasto por intereses.",
        owner_label="Resultado operativo (antes de intereses)",
        owner_question_text="¿Esta columna representa el resultado operativo del período?",
        owner_option_description="Resultado operativo del período confirmado.",
    ),
    _RoleRule(
        semantic_role="closing_index",
        variable_name="closing_index",
        header_keywords=("closing_index", "indice_cierre"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"origin_index", "indice_origen"}),
        co_column_penalties=(),
        risk_text="El índice de cierre debe pertenecer a la misma serie que el índice de origen.",
        owner_label="Índice de cierre",
        owner_question_text="¿Esta columna representa el índice de cierre?",
        owner_option_description="Valor del índice al cierre del período confirmado.",
    ),
    _RoleRule(
        semantic_role="origin_index",
        variable_name="origin_index",
        header_keywords=("origin_index", "indice_origen"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"closing_index", "indice_cierre"}),
        co_column_penalties=(),
        risk_text="El índice de origen debe pertenecer a la misma serie que el índice de cierre.",
        owner_label="Índice de origen",
        owner_question_text="¿Esta columna representa el índice de origen?",
        owner_option_description="Valor del índice al origen del período confirmado.",
    ),
    _RoleRule(
        semantic_role="tax_amount",
        variable_name="taxes",
        header_keywords=("iva", "impuesto", "impuestos", "tax", "taxes"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"subtotal", "importe_total", "venta_total", "costo"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no corresponde a impuestos, los importes netos y totales "
            "pueden quedar mal interpretados."
        ),
        owner_label="Impuestos o IVA",
        owner_question_text="¿Esta columna contiene el importe o porcentaje de IVA/impuestos?",
        owner_option_description="Importe o tasa impositiva asociada a la operación.",
    ),
    _RoleRule(
        semantic_role="list_price",
        variable_name="list_price",
        header_keywords=("precio_lista", "list_price", "precio_de_lista"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"producto", "cantidad", "importe_total", "bonif", "descuento_pct"}),
        co_column_penalties=(),
        risk_text="El precio de lista no debe confundirse con el precio efectivo de venta.",
        owner_label="Precio de lista",
        owner_question_text="¿Esta columna es el precio de lista antes de descuentos?",
        owner_option_description="Precio publicado o base antes de bonificaciones/descuentos.",
    ),
    _RoleRule(
        semantic_role="discount_candidate",
        variable_name="discount",
        header_keywords=("bonif", "bonificacion", "descuento", "descuento_pct", "discount"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"precio_lista", "importe_total", "producto"}),
        co_column_penalties=(),
        risk_text="Una bonificacion puede ser importe o porcentaje; la unidad debe confirmarse antes de calcular.",
        owner_label="Descuento o bonificacion",
        owner_question_text="¿Esta columna representa un descuento o bonificacion?",
        owner_option_description="Descuento asociado a la operación; su unidad debe confirmarse.",
    ),
    _RoleRule(
        semantic_role="subtotal_amount",
        variable_name="subtotal_amount",
        header_keywords=("subtotal", "importe_neto", "net_amount"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"iva", "importe_total", "producto", "unidades"}),
        co_column_penalties=(),
        risk_text="El subtotal no debe confundirse con el total final facturado.",
        owner_label="Subtotal",
        owner_question_text="¿Esta columna es el subtotal antes de impuestos u otros ajustes?",
        owner_option_description="Importe parcial previo al total final.",
    ),
    _RoleRule(
        semantic_role="customer_name",
        variable_name="customer",
        header_keywords=("cliente", "customer", "razon_social_cliente"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"factura", "cobrado", "pendiente", "importe_total"}),
        co_column_penalties=(),
        risk_text="Una identificación incorrecta del cliente distorsiona agrupaciones y trazabilidad.",
        owner_label="Cliente",
        owner_question_text="¿Esta columna identifica al cliente de la operación?",
        owner_option_description="Nombre o identificador legible del cliente.",
    ),
    _RoleRule(
        semantic_role="supplier_name",
        variable_name="supplier",
        header_keywords=("proveedor", "supplier", "razon_social_proveedor"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"producto", "costo", "subtotal", "iva"}),
        co_column_penalties=(),
        risk_text="Una identificación incorrecta del proveedor distorsiona compras y comparaciones.",
        owner_label="Proveedor",
        owner_question_text="¿Esta columna identifica al proveedor de la compra?",
        owner_option_description="Nombre o identificador legible del proveedor.",
    ),
    _RoleRule(
        semantic_role="payment_method",
        variable_name="payment_method",
        header_keywords=("medio_pago", "medio_de_pago", "medio_cobro", "medio_de_cobro", "forma_pago", "payment_method"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_NUMBER}),
        co_column_boosts=frozenset({"cobrado", "factura", "cliente", "importe_total"}),
        co_column_penalties=(),
        risk_text="El medio de pago es categórico y no debe confundirse con un importe.",
        owner_label="Medio de pago",
        owner_question_text="¿Esta columna indica el medio o forma de pago/cobro?",
        owner_option_description="Efectivo, transferencia, tarjeta u otro medio.",
    ),
    _RoleRule(
        semantic_role="opening_stock",
        variable_name="opening_stock",
        header_keywords=("stock_inicial", "inventario_inicial", "opening_stock"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"entradas", "salidas", "stock_final", "sku", "producto"}),
        co_column_penalties=(),
        risk_text="El stock inicial define el punto de partida del movimiento de inventario.",
        owner_label="Stock inicial",
        owner_question_text="¿Esta columna es el stock al inicio del período?",
        owner_option_description="Existencia inicial antes de entradas y salidas.",
    ),
    _RoleRule(
        semantic_role="stock_inflow",
        variable_name="stock_inflow",
        header_keywords=("entradas", "entrada_stock", "stock_entradas", "stock_inflow", "compras"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"stock_inicial", "salidas", "stock_final", "sku"}),
        co_column_penalties=(),
        risk_text="Las entradas de stock no deben confundirse con ventas o cantidades facturadas.",
        owner_label="Entradas de stock",
        owner_question_text="¿Esta columna registra unidades que ingresaron al stock?",
        owner_option_description="Unidades incorporadas al inventario durante el período.",
    ),
    _RoleRule(
        semantic_role="stock_outflow",
        variable_name="stock_outflow",
        header_keywords=("salidas", "salida_stock", "stock_salidas", "stock_outflow", "ventas"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"stock_inicial", "entradas", "stock_final", "sku"}),
        co_column_penalties=(),
        risk_text="Las salidas de stock no deben confundirse automáticamente con ventas.",
        owner_label="Salidas de stock",
        owner_question_text="¿Esta columna registra unidades que salieron del stock?",
        owner_option_description="Unidades retiradas del inventario durante el período.",
    ),
    _RoleRule(
        semantic_role="stock_current",
        variable_name="stock_current",
        header_keywords=("stock_actual", "stock_sistema", "stock_declarado_dueno", "conteo_fisico_informado", "stock_current"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"stock_minimo", "sku", "producto", "costo_unitario"}),
        co_column_penalties=(),
        risk_text="El stock actual debe representar existencia disponible o declarada, no un importe monetario.",
        owner_label="Stock actual",
        owner_question_text="¿Esta columna representa el stock actual o existencia disponible?",
        owner_option_description="Unidades actualmente disponibles o declaradas en inventario.",
    ),
    _RoleRule(
        semantic_role="stock_minimum",
        variable_name="stock_minimum",
        header_keywords=("stock_minimo", "inventario_minimo", "minimum_stock", "stock_minimum"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"stock_actual", "sku", "producto", "costo_unitario"}),
        co_column_penalties=(),
        risk_text="El stock mínimo es un umbral operativo y no debe confundirse con existencia actual o precio.",
        owner_label="Stock mínimo",
        owner_question_text="¿Esta columna indica el nivel mínimo de stock definido para el producto?",
        owner_option_description="Umbral mínimo de inventario antes de reposición o revisión.",
    ),
    _RoleRule(
        semantic_role="closing_stock",
        variable_name="closing_stock",
        header_keywords=("stock_final", "inventario_final", "closing_stock"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_MIXED}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE, INFERRED_DATA_TYPE_TEXT}),
        co_column_boosts=frozenset({"stock_inicial", "entradas", "salidas", "sku", "producto"}),
        co_column_penalties=(),
        risk_text="El stock final debe representar existencia al cierre, no movimiento del período.",
        owner_label="Stock final",
        owner_question_text="¿Esta columna es el stock al cierre del período?",
        owner_option_description="Existencia final luego de entradas y salidas.",
    ),
    _RoleRule(
        semantic_role="product_name",
        variable_name="product",
        header_keywords=("producto", "producto_nombre", "nombre_producto", "product", "descripcion"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"cantidad", "precio_venta", "costo_unitario", "sku", "categoria"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es el nombre del producto, no se va a poder agrupar "
            "por item ni cruzar con catalogo."
        ),
        owner_label="Nombre del producto",
        owner_question_text="¿Esta columna identifica el producto, item o servicio vendido?",
        owner_option_description="Nombre legible del producto o servicio.",
    ),
    _RoleRule(
        semantic_role="product_identifier",
        variable_name="product_id",
        header_keywords=("sku", "codigo", "producto_id", "product_id", "producto_codigo", "codigo_producto", "product_code", "cod"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT, INFERRED_DATA_TYPE_NUMBER}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"producto", "precio_venta", "costo_unitario", "cantidad"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es el codigo del producto, los cruces por SKU van a "
            "fallar y se duplicaran registros en la consolidacion."
        ),
        owner_label="Codigo de producto",
        owner_question_text="¿Esta columna es el codigo, SKU o identificador del producto?",
        owner_option_description="Codigo interno o SKU que identifica univocamente al producto.",
    ),
    _RoleRule(
        semantic_role="document_reference",
        variable_name="document_ref",
        header_keywords=("factura", "comprobante", "nro_comprobante", "documento", "invoice", "nro_factura", "ticket", "orden_compra", "cobro_id", "id_movimiento", "referencia_externa"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT, INFERRED_DATA_TYPE_NUMBER}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"cliente", "fecha", "venta_total"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es un identificador de comprobante, no se va a poder "
            "rastrear el documento contra la cobranza o el pago."
        ),
        owner_label="Comprobante",
        owner_question_text="¿Esta columna es el numero de factura, comprobante o ticket?",
        owner_option_description="Numero que identifica el comprobante de la operacion.",
    ),
    _RoleRule(
        semantic_role="employee_identifier",
        variable_name="employee_id",
        header_keywords=(
            "empleado_id", "empleadoid", "id_empleado", "vendedor_id", "vendedorid",
            "id_vendedor", "salesperson_id", "employee_id", "cajero_id", "mozo_id",
        ),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT, INFERRED_DATA_TYPE_NUMBER}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"venta_id", "ventaid", "fecha", "producto_id", "productoid", "cantidad", "precio_unitario", "preciounitario"}),
        co_column_penalties=(),
        risk_text="El identificador del empleado no debe confundirse con el identificador del producto o del comprobante.",
        owner_label="Identificador del empleado o vendedor",
        owner_question_text="¿Esta columna identifica al empleado, vendedor, cajero o mozo que realizó o registró la venta?",
        owner_option_description="Código o identificador de la persona que realizó o registró la operación.",
    ),
    _RoleRule(
        semantic_role="employee_name",
        variable_name="employee_name",
        header_keywords=(
            "empleado", "vendedor", "salesperson", "employee", "cajero", "mozo",
            "responsable_venta", "responsableventa", "usuario_venta", "usuarioventa",
        ),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"venta_id", "ventaid", "fecha", "producto_id", "productoid", "cantidad", "precio_unitario", "preciounitario"}),
        co_column_penalties=(),
        risk_text="El nombre del empleado no debe confundirse con cliente, producto o referencia documental.",
        owner_label="Empleado o vendedor",
        owner_question_text="¿Esta columna indica qué empleado, vendedor, cajero o mozo realizó o registró la venta?",
        owner_option_description="Nombre de la persona asociada a la realización o registro de la operación.",
    ),
    _RoleRule(
        semantic_role="branch_identifier",
        variable_name="branch_id",
        header_keywords=("sucursal_id", "sucursalid", "id_sucursal", "branch_id", "local_id", "tienda_id", "store_id"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT, INFERRED_DATA_TYPE_NUMBER}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"sucursal", "nombre_sucursal", "ciudad", "venta_total", "fecha"}),
        co_column_penalties=(),
        risk_text="El identificador de sucursal no debe confundirse con canal comercial, producto o transacción.",
        owner_label="Identificador de sucursal",
        owner_question_text="¿Esta columna es el código o identificador de la sucursal, local o tienda?",
        owner_option_description="Código estable que identifica una sede física o punto de venta.",
    ),
    _RoleRule(
        semantic_role="branch_name",
        variable_name="branch_name",
        header_keywords=("sucursal", "nombre_sucursal", "sucursal_nombre", "branch", "branch_name", "local", "tienda", "store"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"sucursal_id", "ciudad", "venta_total", "fecha", "canal"}),
        co_column_penalties=(),
        risk_text="La sucursal o local es una dimensión física y no debe confundirse con el canal comercial.",
        owner_label="Sucursal o local",
        owner_question_text="¿Esta columna indica la sucursal, local, tienda o sede donde ocurrió la operación?",
        owner_option_description="Nombre de la sede física o punto de venta asociado a la operación.",
    ),
    _RoleRule(
        semantic_role="city",
        variable_name="city",
        header_keywords=("ciudad", "localidad", "city", "municipio"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"sucursal", "sucursal_id", "direccion", "provincia"}),
        co_column_penalties=(),
        risk_text="La ciudad es una ubicación geográfica y no debe usarse como canal de venta ni como identificador de sucursal.",
        owner_label="Ciudad o localidad",
        owner_question_text="¿Esta columna indica la ciudad o localidad de la sucursal u operación?",
        owner_option_description="Ciudad o localidad geográfica asociada a una sede u operación.",
    ),
    _RoleRule(
        semantic_role="sales_channel",
        variable_name="segment",
        header_keywords=("canal", "canal_venta", "sales_channel", "channel", "medio_venta", "origen_venta"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"venta_total", "producto", "cliente", "categoria"}),
        co_column_penalties=frozenset({"sucursal", "sucursal_id", "local", "tienda"}),
        risk_text=(
            "Si esta columna no representa el canal comercial, las segmentaciones por "
            "canal van a mezclar informacion heterogenea."
        ),
        owner_label="Canal de venta",
        owner_question_text="¿Esta columna indica el canal comercial por el que se realizó la venta?",
        owner_option_description="Canal comercial, por ejemplo mostrador, mayorista, ecommerce o marketplace.",
    ),
    _RoleRule(
        semantic_role="commercial_category",
        variable_name="segment",
        header_keywords=("categoria", "rubro", "familia", "category"),
        expected_data_types=frozenset({INFERRED_DATA_TYPE_TEXT}),
        contradicting_data_types=frozenset({INFERRED_DATA_TYPE_NUMBER, INFERRED_DATA_TYPE_DATE}),
        co_column_boosts=frozenset({"producto", "precio_venta", "costo_unitario", "canal"}),
        co_column_penalties=(),
        risk_text=(
            "Si esta columna no es una categoria o rubro, las segmentaciones por "
            "familia de producto no van a reflejar la estructura real del negocio."
        ),
        owner_label="Categoria o rubro",
        owner_question_text="¿Esta columna es la categoria, rubro o familia del producto?",
        owner_option_description="Agrupacion comercial o rubro del producto.",
    ),
)


def normalize_service_1_column_understanding_header_v1(column_name: object) -> str:
    """Normalize a header for matching and evidence logging.

    Mirrors ``normalize_service_1_column_name_v1`` from the closed
    semantic mapper so that evidence strings and matches stay aligned,
    but is duplicated here on purpose to keep this engine independent
    of the closed chain.
    """
    if not isinstance(column_name, str):
        return ""
    raw_text = column_name.strip()
    if not raw_text:
        return ""
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", raw_text).lower()
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    underscored = re.sub(r"\s+", "_", without_accents)
    cleaned = _NON_ALNUM_RE.sub("_", underscored)
    collapsed = _UNDERSCORE_RE.sub("_", cleaned).strip("_")
    return collapsed


def _coerce_inferred_data_type(inferred_type: str | None) -> str:
    if not inferred_type:
        return INFERRED_DATA_TYPE_TEXT
    normalized = str(inferred_type).strip().lower()
    if normalized in {"int", "integer", "float", "decimal", "numeric"}:
        return INFERRED_DATA_TYPE_NUMBER
    if normalized in {"date", "datetime"}:
        return INFERRED_DATA_TYPE_DATE
    if normalized in {"text", "string"}:
        return INFERRED_DATA_TYPE_TEXT
    if normalized in {"empty", "null", "none"}:
        return INFERRED_DATA_TYPE_EMPTY
    if normalized in {"mixed", "ambiguous"}:
        return INFERRED_DATA_TYPE_MIXED
    return normalized


def _infer_data_type_from_samples(samples: tuple[Any, ...]) -> str:
    if not samples:
        return INFERRED_DATA_TYPE_EMPTY

    numeric = 0
    date_like = 0
    text = 0
    for value in samples:
        if value is None:
            continue
        if isinstance(value, bool):
            text += 1
            continue
        if isinstance(value, (int, float)):
            numeric += 1
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                continue
            if _DATE_TEXT_RE.match(stripped) or _SLASH_DATE_RE.match(stripped):
                date_like += 1
                continue
            if _INT_RE.match(stripped) or _FLOAT_RE.match(stripped):
                numeric += 1
                continue
            text += 1
            continue
        text += 1

    total = numeric + date_like + text
    if total == 0:
        return INFERRED_DATA_TYPE_EMPTY
    if numeric == total:
        return INFERRED_DATA_TYPE_NUMBER
    if date_like == total:
        return INFERRED_DATA_TYPE_DATE
    if text == total:
        return INFERRED_DATA_TYPE_TEXT
    if numeric / total >= 0.6:
        return INFERRED_DATA_TYPE_NUMBER
    if date_like / total >= 0.6:
        return INFERRED_DATA_TYPE_DATE
    if text / total >= 0.6:
        return INFERRED_DATA_TYPE_TEXT
    return INFERRED_DATA_TYPE_MIXED


def _looks_like_excel_serial_dates(samples: tuple[Any, ...]) -> bool:
    if not samples:
        return False
    parsed: list[float] = []
    for value in samples:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return False
        if not number.is_integer() or number < 1 or number > 100000:
            return False
        parsed.append(number)
    return bool(parsed)


def _coerce_co_columns(co_columns: object) -> tuple[str, ...]:
    if co_columns is None:
        return ()
    if isinstance(co_columns, str):
        normalized = normalize_service_1_column_understanding_header_v1(co_columns)
        return (normalized,) if normalized else ()
    if isinstance(co_columns, (list, tuple, set, frozenset)):
        cleaned: list[str] = []
        for item in co_columns:
            normalized = normalize_service_1_column_understanding_header_v1(item)
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)
        return tuple(cleaned)
    return ()


def _has_sufficient_period_total_context(
    *, normalized_header: str, co_columns: tuple[str, ...]
) -> bool:
    """Require the three period-total roles before auto-approving their meaning."""
    own_role = next(
        (
            role
            for role, headers in _PERIOD_TOTAL_HEADERS_BY_ROLE.items()
            if normalized_header in headers
        ),
        None,
    )
    if own_role is None:
        return True
    observed = set(co_columns)
    return all(
        any(header in observed for header in headers)
        for role, headers in _PERIOD_TOTAL_HEADERS_BY_ROLE.items()
        if role != own_role
    )


def _is_period_total_role(semantic_role: str) -> bool:
    return semantic_role in _PERIOD_TOTAL_HEADERS_BY_ROLE


def _score_role(
    *,
    rule: _RoleRule,
    normalized_header: str,
    inferred_data_type: str,
    co_columns: tuple[str, ...],
    sheet_name: str,
) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    score = 0.0
    evidence: list[str] = []
    counter_evidence: list[str] = []

    if rule.semantic_role in {
        "operation_time", "transaction_identifier", "branch_identifier", "branch_name", "city",
    } and not any(keyword and keyword in normalized_header for keyword in rule.header_keywords):
        return 0.0, (), ("dimensional_role_requires_header_evidence",)

    if rule.semantic_role == "sales_channel" and normalized_header in {
        "sucursal", "nombre_sucursal", "sucursal_nombre", "sucursal_id", "sucursalid",
        "id_sucursal", "branch", "branch_name", "branch_id", "local", "local_id",
        "tienda", "tienda_id", "store", "store_id",
    }:
        return 0.0, (), ("branch_header_excluded_from_sales_channel",)

    if normalized_header:
        exact_keyword = next(
            (keyword for keyword in rule.header_keywords if keyword and normalized_header == keyword),
            None,
        )
        if exact_keyword is not None:
            score += HEADER_WEIGHT + EXACT_HEADER_BONUS
            evidence.append(
                f"exact_header_match: '{normalized_header}' equals keyword '{exact_keyword}'"
            )
        else:
            for keyword in rule.header_keywords:
                if keyword and keyword in normalized_header:
                    score += HEADER_WEIGHT
                    evidence.append(
                        f"header_match: '{normalized_header}' contains keyword '{keyword}'"
                    )
                    break

    if inferred_data_type in rule.expected_data_types:
        score += TYPE_WEIGHT
        evidence.append(
            f"inferred_type_compatible: '{inferred_data_type}' aligns with role '{rule.semantic_role}'"
        )
    elif inferred_data_type in rule.contradicting_data_types:
        score -= TYPE_CONTRADICTION_PENALTY
        counter_evidence.append(
            f"inferred_type_contradiction: '{inferred_data_type}' does not match role '{rule.semantic_role}'"
        )

    if co_columns:
        boosted = False
        for co_column in co_columns:
            if co_column in rule.co_column_boosts:
                score += CO_COLUMN_BOOST
                evidence.append(
                    f"co_column_reinforces: co-column '{co_column}' matches role '{rule.semantic_role}'"
                )
                boosted = True
                break
        if not boosted:
            for co_column in co_columns:
                if co_column in rule.co_column_penalties:
                    score -= CO_COLUMN_PENALTY
                    counter_evidence.append(
                        f"co_column_contradicts: co-column '{co_column}' conflicts with role '{rule.semantic_role}'"
                    )
                    break

    if (
        _is_period_total_role(rule.semantic_role)
        and normalized_header in _LEGACY_ROLE_BY_PERIOD_HEADER
        and not _has_sufficient_period_total_context(
            normalized_header=normalized_header,
            co_columns=co_columns,
        )
    ):
        score -= CO_COLUMN_PENALTY
        counter_evidence.append(
            "period_total_context_incomplete: sibling period totals are required"
        )

    if sheet_name:
        normalized_sheet = normalize_service_1_column_understanding_header_v1(sheet_name)
        boost_terms = _SHEET_ROLE_BOOSTS.get(rule.semantic_role, ())
        penalty_terms = _SHEET_ROLE_PENALTIES.get(rule.semantic_role, ())
        if normalized_sheet and any(term in normalized_sheet for term in boost_terms):
            score += SHEET_CONTEXT_BOOST
            evidence.append(
                f"sheet_context_reinforces: '{normalized_sheet}' supports role '{rule.semantic_role}'"
            )
        if normalized_sheet and any(term in normalized_sheet for term in penalty_terms):
            score -= SHEET_CONTEXT_PENALTY
            counter_evidence.append(
                f"sheet_context_contradicts: '{normalized_sheet}' conflicts with role '{rule.semantic_role}'"
            )
        evidence.append(f"sheet_context: '{sheet_name}'")

    bounded = max(0.0, min(1.0, score))
    return bounded, tuple(evidence), tuple(counter_evidence)


def _build_unknown_hypothesis(*, reason: str) -> Service1ColumnUnderstandingHypothesisV1:
    return Service1ColumnUnderstandingHypothesisV1(
        semantic_role=SEMANTIC_ROLE_UNKNOWN,
        variable_name=VARIABLE_NAME_UNKNOWN,
        score=0.0,
        rationale=reason,
    )


def _build_rationale(
    *,
    rule: _RoleRule,
    evidence: tuple[str, ...],
    counter_evidence: tuple[str, ...],
) -> str:
    pieces: list[str] = []
    if evidence:
        pieces.append("Apoya: " + "; ".join(evidence))
    if counter_evidence:
        pieces.append("Desafia: " + "; ".join(counter_evidence))
    if not pieces:
        pieces.append(f"Sin evidencia concluyente para el rol '{rule.semantic_role}'.")
    return " | ".join(pieces)


def _build_owner_question(
    *,
    rule: _RoleRule,
    column_name: str,
    sheet_name: str,
    sample_values: tuple[Any, ...],
) -> str:
    if sample_values:
        sample_hint = ", ".join(repr(value) for value in sample_values[:2])
    else:
        sample_hint = "sin valores de muestra"
    return (
        f"En la hoja '{sheet_name}' veo la columna '{column_name}' "
        f"con valores como {sample_hint}. "
        f"Por el nombre y los datos, podria ser: (A) {rule.owner_question_text} "
        f"o (B) otra cosa. ¿Cual es?"
    )


def build_service_1_owner_options_for_understanding_v1(
    understanding: Service1ColumnUnderstandingV1,
) -> tuple[Service1ColumnOwnerAnswerOptionV1, ...]:
    if not isinstance(understanding, Service1ColumnUnderstandingV1):
        raise ValueError("understanding must be a Service1ColumnUnderstandingV1")
    primary = understanding.primary_hypothesis
    if primary is None:
        return ()
    return _build_owner_options(
        primary=primary,
        alternatives=tuple(understanding.alternatives),
    )


def _build_owner_options(
    *,
    primary: Service1ColumnUnderstandingHypothesisV1,
    alternatives: tuple[Service1ColumnUnderstandingHypothesisV1, ...],
) -> tuple[Service1ColumnOwnerAnswerOptionV1, ...]:
    options: list[Service1ColumnOwnerAnswerOptionV1] = []
    primary_rule = _find_rule(primary.semantic_role)
    primary_label = primary_rule.owner_label if primary_rule is not None else "Esta hipotesis"
    primary_question = primary_rule.owner_question_text if primary_rule is not None else "Esto es lo que sugieren las señales"
    primary_description = primary_rule.owner_option_description if primary_rule is not None else "Seleccionada como hipotesis principal."
    options.append(
        Service1ColumnOwnerAnswerOptionV1(
            option_id="A",
            label=primary_label,
            description=primary_description,
            linked_hypothesis=primary,
        )
    )
    option_letters = ["B", "C", "D"]
    alternative_index = 0
    for letter in option_letters:
        if alternative_index >= len(alternatives):
            break
        alternative = alternatives[alternative_index]
        alternative_index += 1
        alternative_rule = _find_rule(alternative.semantic_role)
        alternative_label = alternative_rule.owner_label if alternative_rule is not None else alternative.semantic_role
        alternative_description = (
            alternative_rule.owner_option_description
            if alternative_rule is not None
            else "Otra hipotesis razonable en base a la evidencia."
        )
        options.append(
            Service1ColumnOwnerAnswerOptionV1(
                option_id=letter,
                label=alternative_label,
                description=alternative_description,
                linked_hypothesis=alternative,
            )
        )
    options.append(
        Service1ColumnOwnerAnswerOptionV1(
            option_id=OWNER_ANSWER_OTHER,
            label="Otra cosa",
            description=(
                "La columna significa algo distinto a las hipotesis listadas. "
                "Si la elegis, el sistema te preguntara cual es."
            ),
            linked_hypothesis=None,
        )
    )
    return tuple(options[:MAX_OWNER_ANSWER_OPTIONS])


def _find_rule(semantic_role: str) -> _RoleRule | None:
    for rule in _ROLE_RULES:
        if rule.semantic_role == semantic_role:
            return rule
    return None


def _format_sample_values_for_question(samples: tuple[Any, ...]) -> str:
    if not samples:
        return "sin valores de muestra"
    formatted: list[str] = []
    for value in samples[:3]:
        if isinstance(value, str):
            formatted.append(f"'{value}'")
        else:
            formatted.append(repr(value))
    return ", ".join(formatted)


def build_column_understanding_v1(
    *,
    column_name: str,
    sheet_name: str,
    sample_values: list[Any] | tuple[Any, ...] | None = None,
    inferred_data_type: str | None = None,
    normalized_header: str | None = None,
    co_column_names: list[str] | tuple[str, ...] | None = None,
    sheet_context: str | None = None,
) -> Service1ColumnUnderstandingV1:
    """Build the understanding for a single column.

    Pure deterministic function. Does not mutate inputs. Returns a
    fail-closed contract instance.
    """
    if not isinstance(column_name, str) or not column_name.strip():
        raise ValueError("column_name must be a non-empty string")
    if not isinstance(sheet_name, str) or not sheet_name.strip():
        raise ValueError("sheet_name must be a non-empty string")

    sample_tuple = tuple(sample_values or ())
    cleaned_samples: list[Any] = []
    for value in sample_tuple:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        cleaned_samples.append(value)
        if len(cleaned_samples) >= 5:
            break
    sample_tuple_final = tuple(cleaned_samples)

    normalized = normalized_header or normalize_service_1_column_understanding_header_v1(column_name)
    if not normalized:
        raise ValueError("normalized_header could not be derived from column_name")

    inferred = (
        _coerce_inferred_data_type(inferred_data_type)
        if inferred_data_type
        else _infer_data_type_from_samples(sample_tuple_final)
    )
    if (
        inferred == INFERRED_DATA_TYPE_NUMBER
        and normalized
        in {"fecha", "fecha_venta", "fecha_operacion", "date", "fecha_emision"}
        and _looks_like_excel_serial_dates(sample_tuple_final)
    ):
        inferred = INFERRED_DATA_TYPE_DATE
    co_columns = _coerce_co_columns(co_column_names)
    effective_sheet = (sheet_context or sheet_name or "").strip() or "unknown_sheet"
    period_total_context_sufficient = _has_sufficient_period_total_context(
        normalized_header=normalized,
        co_columns=co_columns,
    )

    scored: list[tuple[float, _RoleRule, tuple[str, ...], tuple[str, ...]]] = []
    for rule in _ROLE_RULES:
        if (
            period_total_context_sufficient
            and _LEGACY_ROLE_BY_PERIOD_HEADER.get(normalized) == rule.semantic_role
        ):
            continue
        score, evidence, counter_evidence = _score_role(
            rule=rule,
            normalized_header=normalized,
            inferred_data_type=inferred,
            co_columns=co_columns,
            sheet_name=effective_sheet,
        )
        if score <= 0:
            continue
        scored.append((score, rule, evidence, counter_evidence))

    scored.sort(key=lambda item: (item[0], item[1].semantic_role), reverse=True)
    scored = scored[:MAX_CANDIDATE_MEANINGS]

    candidate_meanings: list[Service1ColumnUnderstandingHypothesisV1] = []
    all_evidence: list[str] = []
    all_counter_evidence: list[str] = []
    for score, rule, evidence, counter_evidence in scored:
        rationale = _build_rationale(
            rule=rule,
            evidence=evidence,
            counter_evidence=counter_evidence,
        )
        candidate_meanings.append(
            Service1ColumnUnderstandingHypothesisV1(
                semantic_role=rule.semantic_role,
                variable_name=rule.variable_name,
                score=score,
                rationale=rationale,
            )
        )
        all_evidence.extend(evidence)
        all_counter_evidence.extend(counter_evidence)

    if not candidate_meanings:
        all_evidence.append("no_header_match")
        all_evidence.append("no_type_match")
        all_evidence.append("no_context_match")
        unknown_reason = (
            "Sin coincidencia en nombre, tipo de dato ni contexto de co-columnas."
        )
        candidate_meanings.append(_build_unknown_hypothesis(reason=unknown_reason))
        primary = None
        confidence = 0.0
        owner_question_needed = True
        risk_text = (
            "Sin comprension de la columna no es posible usarla en calculos. "
            "Queda bloqueada hasta que el dueño confirme su significado."
        )
        primary_rule: _RoleRule | None = None
    else:
        top = candidate_meanings[0]
        if top.score >= MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS:
            primary = top
            confidence = top.score
            primary_rule = _find_rule(top.semantic_role)
            period_total_context_missing = (
                _is_period_total_role(top.semantic_role)
                and not period_total_context_sufficient
            )
            owner_question_needed = (
                normalized in _OWNER_CONFIRMATION_REQUIRED_HEADERS
                or period_total_context_missing
                or (
                    top.score < HIGH_CONFIDENCE_THRESHOLD
                    and len(candidate_meanings) > 1
                )
            )
            if normalized in _OWNER_CONFIRMATION_REQUIRED_HEADERS:
                all_evidence.append(
                    f"owner_confirmation_required_for_ambiguous_header: '{normalized}'"
                )
            if period_total_context_missing:
                all_evidence.append(
                    "owner_confirmation_required_for_missing_period_total_context"
                )
            risk_text = primary_rule.risk_text if primary_rule is not None else (
                "Si la columna se interpreta mal, los calculos siguientes quedaran sesgados."
            )
        else:
            primary = None
            confidence = top.score
            primary_rule = _find_rule(top.semantic_role)
            owner_question_needed = True
            if normalized in _OWNER_CONFIRMATION_REQUIRED_HEADERS:
                all_evidence.append(
                    f"owner_confirmation_required_for_ambiguous_header: '{normalized}'"
                )
            risk_text = primary_rule.risk_text if primary_rule is not None else (
                "Sin una interpretacion confirmada, los calculos siguientes pueden estar sesgados."
            )

    if primary is not None:
        alternatives = tuple(
            candidate for candidate in candidate_meanings[1:] if candidate != primary
        )[:MAX_ALTERNATIVES]
    else:
        alternatives = tuple(candidate_meanings[1:])[:MAX_ALTERNATIVES]

    if owner_question_needed and primary is None and candidate_meanings:
        primary = candidate_meanings[0]
        candidate_meanings = [primary] + list(alternatives)
        alternatives = tuple(candidate_meanings[1:])[:MAX_ALTERNATIVES]

    if owner_question_needed and primary is not None:
        anchor_rule = _find_rule(primary.semantic_role)
        if anchor_rule is None:
            question_text = (
                f"En la hoja '{effective_sheet}' veo la columna '{column_name}' "
                f"con valores como {_format_sample_values_for_question(sample_tuple_final)}. "
                f"¿Que significa en tu negocio? (A) {primary.semantic_role}, "
                f"(B) otra cosa."
            )
        else:
            question_text = _build_owner_question(
                rule=anchor_rule,
                column_name=column_name,
                sheet_name=effective_sheet,
                sample_values=sample_tuple_final,
            )
        options = _build_owner_options(primary=primary, alternatives=alternatives)
    else:
        question_text = None
        options = ()

    if not all_evidence:
        all_evidence.append("no_signal")
    all_evidence.append(f"normalized_header: '{normalized}'")
    all_evidence.append(f"inferred_data_type: '{inferred}'")

    metadata: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "confidence_band": confidence_band_v1(confidence),
        "candidate_count": len(candidate_meanings),
        "alternative_count": len(alternatives),
        "co_column_signals": list(co_columns),
        "counter_evidence": list(all_counter_evidence),
        "primary_rule": primary_rule.semantic_role if primary_rule is not None else None,
    }

    return build_service_1_column_understanding_v1(
        column_name=column_name,
        sheet_name=effective_sheet,
        sample_values=sample_tuple_final,
        inferred_data_type=inferred,
        normalized_header=normalized,
        candidate_meanings=tuple(candidate_meanings),
        primary_hypothesis=primary,
        confidence=confidence,
        evidence=tuple(all_evidence),
        alternatives=alternatives,
        risk_if_wrong=risk_text,
        owner_question_needed=owner_question_needed,
        owner_question_text=question_text,
        allowed_owner_answers=options,
        metadata=metadata,
    )


def build_column_understanding_from_entry_v1(
    entry: ColumnConfirmationEntry,
    *,
    co_column_names: list[str] | tuple[str, ...] | None = None,
) -> Service1ColumnUnderstandingV1:
    """Build the understanding for a single ``ColumnConfirmationEntry``.

    The entry is read; it is never mutated. The co-column context must
    be supplied by the caller because the entry itself only describes
    one column.
    """
    if not isinstance(entry, ColumnConfirmationEntry):
        raise ValueError("entry must be a ColumnConfirmationEntry")
    if co_column_names is not None and not isinstance(co_column_names, (list, tuple)):
        raise ValueError("co_column_names must be a list or tuple or None")
    return build_column_understanding_v1(
        column_name=entry.original_column_name,
        sheet_name=entry.sheet_name or "unknown_sheet",
        sample_values=entry.sample_values,
        inferred_data_type=(
            None
            if str(entry.inferred_type or "").strip().lower() == "unknown"
            else entry.inferred_type
        ),
        co_column_names=co_column_names,
    )


def build_column_understandings_from_matrix_v1(
    matrix: ColumnConfirmationMatrix,
) -> tuple[Service1ColumnUnderstandingV1, ...]:
    """Build the understanding for every entry in a matrix.

    The matrix is read; it is never mutated. Co-column context is
    derived per sheet from the other entries in the same sheet.
    """
    if not isinstance(matrix, ColumnConfirmationMatrix):
        raise ValueError("matrix must be a ColumnConfirmationMatrix")

    headers_by_sheet: dict[str, tuple[str, ...]] = {}
    for entry in matrix.entries:
        sheet = (entry.sheet_name or "unknown_sheet").strip() or "unknown_sheet"
        normalized = normalize_service_1_column_understanding_header_v1(
            entry.original_column_name
        )
        if not normalized:
            continue
        headers_by_sheet.setdefault(sheet, ())
        if normalized not in headers_by_sheet[sheet]:
            headers_by_sheet[sheet] = headers_by_sheet[sheet] + (normalized,)

    understandings: list[Service1ColumnUnderstandingV1] = []
    for entry in matrix.entries:
        sheet = (entry.sheet_name or "unknown_sheet").strip() or "unknown_sheet"
        co_columns = tuple(
            header
            for header in headers_by_sheet.get(sheet, ())
            if header
            and header
            != normalize_service_1_column_understanding_header_v1(entry.original_column_name)
        )
        understandings.append(
            build_column_understanding_from_entry_v1(entry, co_column_names=co_columns)
        )
    return tuple(understandings)


__all__ = [
    "SCHEMA_VERSION",
    "HEADER_WEIGHT",
    "TYPE_WEIGHT",
    "CONTEXT_WEIGHT",
    "CO_COLUMN_BOOST",
    "CO_COLUMN_PENALTY",
    "TYPE_CONTRADICTION_PENALTY",
    "normalize_service_1_column_understanding_header_v1",
    "build_service_1_owner_options_for_understanding_v1",
    "build_column_understanding_v1",
    "build_column_understanding_from_entry_v1",
    "build_column_understandings_from_matrix_v1",
]

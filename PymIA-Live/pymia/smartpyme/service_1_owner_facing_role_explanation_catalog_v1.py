from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

from pymia.contracts.column_confirmation_v1 import CalculationRelevance, infer_calculation_relevance

SCHEMA_VERSION: Final[str] = "SERVICE_1_OWNER_FACING_ROLE_EXPLANATION_CATALOG_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
UNKNOWN_ROLE = "unknown"


@dataclass(frozen=True)
class Service1OwnerFacingRoleExplanationV1:
    schema_version: str
    service_name: str
    semantic_role: str
    owner_label: str
    owner_facing_role_explanation: str
    calculation_relevance: str
    known_role: bool
    human_review_required: bool
    runtime_authorized: bool
    recalculation_authorized: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_ROLE_COPY: Final[dict[str, tuple[str, str]]] = {
    "venta_total": (
        "Ventas del periodo",
        "Esta columna representa el importe total vendido o facturado en el periodo analizado.",
    ),
    "precio_venta": (
        "Precio de venta",
        "Esta columna representa el precio de venta en pesos de cada producto, item u operacion.",
    ),
    "costo_unitario": (
        "Costo por unidad",
        "Esta columna representa el valor en pesos que cuesta cada unidad de producto o servicio.",
    ),
    "costo_total": (
        "Costo total",
        "Esta columna representa el costo total en pesos asociado a una operacion, producto o conjunto de unidades.",
    ),
    "margen": (
        "Margen",
        "Esta columna representa la diferencia economica entre lo vendido y su costo asociado.",
    ),
    "cantidad": (
        "Cantidad",
        "Esta columna representa la cantidad de unidades vendidas, compradas o movidas.",
    ),
    "stock": (
        "Stock",
        "Esta columna representa la cantidad disponible de un producto en inventario.",
    ),
    "stock_final": (
        "Stock final",
        "Esta columna representa la cantidad final disponible de un producto luego de movimientos del periodo.",
    ),
    "pago": (
        "Pago",
        "Esta columna representa dinero pagado por la empresa o por una contraparte.",
    ),
    "cobro": (
        "Cobro",
        "Esta columna representa dinero cobrado o recibido por la empresa.",
    ),
    "ingreso": (
        "Ingreso",
        "Esta columna representa una entrada de dinero o valor economico para la empresa.",
    ),
    "egreso": (
        "Egreso",
        "Esta columna representa una salida de dinero o valor economico de la empresa.",
    ),
    "saldo": (
        "Saldo",
        "Esta columna representa un monto pendiente, disponible o acumulado a una fecha determinada.",
    ),
    "gasto": (
        "Gasto",
        "Esta columna representa un gasto o erogacion de la empresa.",
    ),
    "impuesto": (
        "Impuesto",
        "Esta columna representa un importe de impuesto incluido, retenido, percibido o informado.",
    ),
    "descuento": (
        "Descuento",
        "Esta columna representa una rebaja, bonificacion o descuento aplicado sobre una operacion.",
    ),
    "producto": (
        "Producto",
        "Esta columna identifica el producto, item o servicio relacionado con cada operacion.",
    ),
    "sku": (
        "Codigo de producto",
        "Esta columna identifica un codigo interno, SKU o referencia del producto.",
    ),
    "cliente": (
        "Cliente",
        "Esta columna identifica el cliente relacionado con cada operacion.",
    ),
    "proveedor": (
        "Proveedor",
        "Esta columna identifica el proveedor relacionado con cada compra, gasto u operacion.",
    ),
    "fecha": (
        "Fecha",
        "Esta columna representa la fecha de cada operacion, movimiento o registro.",
    ),
    "moneda": (
        "Moneda",
        "Esta columna indica la moneda usada en los importes de la planilla.",
    ),
    "factura": (
        "Factura o comprobante",
        "Esta columna identifica una factura, comprobante, recibo u otro documento asociado.",
    ),
    "canal": (
        "Canal",
        "Esta columna identifica el canal, sucursal, medio de venta o agrupacion comercial de la operacion.",
    ),
    UNKNOWN_ROLE: (
        "Rol no reconocido",
        "Esta columna necesita revision manual antes de usarla para calculos o conclusiones.",
    ),
}


def normalize_semantic_role_v1(semantic_role: str | None) -> str:
    if semantic_role is None:
        return UNKNOWN_ROLE
    normalized = str(semantic_role).strip().lower()
    return normalized or UNKNOWN_ROLE


def known_owner_facing_semantic_roles_v1() -> tuple[str, ...]:
    return tuple(sorted(_ROLE_COPY.keys()))


def explain_owner_facing_semantic_role_v1(
    semantic_role: str | None,
) -> Service1OwnerFacingRoleExplanationV1:
    role = normalize_semantic_role_v1(semantic_role)
    known_role = role in _ROLE_COPY and role != UNKNOWN_ROLE
    lookup_role = role if role in _ROLE_COPY else UNKNOWN_ROLE
    owner_label, explanation = _ROLE_COPY[lookup_role]
    relevance = infer_calculation_relevance(role if known_role else UNKNOWN_ROLE)

    return Service1OwnerFacingRoleExplanationV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        semantic_role=role,
        owner_label=owner_label,
        owner_facing_role_explanation=explanation,
        calculation_relevance=relevance.value,
        known_role=known_role,
        human_review_required=True,
        runtime_authorized=False,
        recalculation_authorized=False,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "UNKNOWN_ROLE",
    "Service1OwnerFacingRoleExplanationV1",
    "explain_owner_facing_semantic_role_v1",
    "known_owner_facing_semantic_roles_v1",
    "normalize_semantic_role_v1",
]

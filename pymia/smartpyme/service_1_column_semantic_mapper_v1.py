from __future__ import annotations

import re
import unicodedata
from typing import Final

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)


ROLE_OPERATION_DATE: Final[str] = "operation_date"
ROLE_DOCUMENT_REFERENCE: Final[str] = "document_reference"
ROLE_PRODUCT_IDENTIFIER: Final[str] = "product_identifier"
ROLE_PRODUCT_NAME: Final[str] = "product_name"
ROLE_COMMERCIAL_CATEGORY: Final[str] = "commercial_category"
ROLE_SALES_CHANNEL: Final[str] = "sales_channel"
ROLE_QUANTITY: Final[str] = "quantity"
ROLE_UNIT_SALE_PRICE: Final[str] = "unit_sale_price"
ROLE_UNIT_COST_CANDIDATE: Final[str] = "unit_cost_candidate"
ROLE_SALES_AMOUNT: Final[str] = "sales_amount"
ROLE_UNKNOWN: Final[str] = "unknown"

VARIABLE_BUSINESS_PERIOD: Final[str] = "business_period"
VARIABLE_DOCUMENT_REF: Final[str] = "document_ref"
VARIABLE_PRODUCT_ID: Final[str] = "product_id"
VARIABLE_PRODUCT: Final[str] = "product"
VARIABLE_SEGMENT: Final[str] = "segment"
VARIABLE_VOLUME_SOLD: Final[str] = "volume_sold"
VARIABLE_SALE_PRICE: Final[str] = "sale_price"
VARIABLE_COST: Final[str] = "cost"
VARIABLE_SOLD_AMOUNT: Final[str] = "sold_amount"
VARIABLE_UNKNOWN: Final[str] = "unknown"

CONFIDENCE_MAPPED: Final[str] = "mapped"
CONFIDENCE_AMBIGUOUS: Final[str] = "ambiguous"
CONFIDENCE_UNKNOWN: Final[str] = "unknown"

_CONFIDENCE_SCORE: Final[dict[str, float]] = {
    CONFIDENCE_MAPPED: 1.0,
    CONFIDENCE_AMBIGUOUS: 0.6,
    CONFIDENCE_UNKNOWN: 0.0,
}

_NON_ALNUM_UNDERSCORE_RE: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9_]+")
_UNDERSCORE_RE: Final[re.Pattern[str]] = re.compile(r"_+")

_MAPPING_BY_NORMALIZED_COLUMN: Final[dict[str, tuple[str, str, bool, str]]] = {
    "fecha": (ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
    "fecha_venta": (ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
    "fecha_operacion": (ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
    "date": (ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
    "comprobante": (ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
    "factura": (ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
    "nro_comprobante": (ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
    "documento": (ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
    "invoice": (ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
    "producto_codigo": (ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
    "codigo_producto": (ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
    "sku": (ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
    "product_code": (ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
    "producto": (ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
    "producto_nombre": (ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
    "nombre_producto": (ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
    "product": (ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
    "categoria": (ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "rubro": (ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "familia": (ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "category": (ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "canal": (ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "canal_venta": (ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "sales_channel": (ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "channel": (ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
    "cantidad": (ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
    "unidades": (ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
    "qty": (ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
    "quantity": (ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
    "precio_unitario": (ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
    "precio_venta": (ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
    "precio": (ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
    "unit_price": (ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
    "sale_price": (ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
    "costo_unitario": (ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
    "costo": (ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
    "unit_cost": (ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
    "cost": (ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
    "venta_total": (ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
    "total_venta": (ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
    "importe_venta": (ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
    "importe_total": (ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
    "sales_amount": (ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
    "sold_amount": (ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
}


def normalize_service_1_column_name_v1(column_name: object) -> str:
    if not isinstance(column_name, str):
        raise ValueError("column_name must be a string")

    text = column_name.strip().lower()
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    underscored = re.sub(r"\s+", "_", without_accents)
    cleaned = _NON_ALNUM_UNDERSCORE_RE.sub("_", underscored)
    collapsed = _UNDERSCORE_RE.sub("_", cleaned).strip("_")
    return collapsed


def build_service_1_column_semantic_candidate_v1(
    entry: ColumnConfirmationEntry,
) -> Service1ColumnSemanticCandidateV1:
    if not isinstance(entry, ColumnConfirmationEntry):
        raise ValueError("entry must be a ColumnConfirmationEntry")

    normalized_column_name = normalize_service_1_column_name_v1(entry.original_column_name)
    role, variable, owner_confirmation_required, confidence_label = _MAPPING_BY_NORMALIZED_COLUMN.get(
        normalized_column_name,
        (ROLE_UNKNOWN, VARIABLE_UNKNOWN, True, CONFIDENCE_UNKNOWN),
    )
    ambiguity_reason = _build_ambiguity_reason(
        source_column_name=entry.original_column_name,
        role=role,
        variable=variable,
        confidence_label=confidence_label,
    )

    return Service1ColumnSemanticCandidateV1(
        source_column_name=entry.original_column_name,
        normalized_column_name=normalized_column_name or ROLE_UNKNOWN,
        sheet_name=entry.sheet_name,
        observed_data_type=entry.inferred_type,
        sample_values=tuple(entry.sample_values),
        candidate_semantic_roles=(role,),
        candidate_variable_names=(variable,),
        confidence=_CONFIDENCE_SCORE[confidence_label],
        ambiguity_reason=ambiguity_reason,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={
            "confidence_label": confidence_label,
            "suggested_data_type": entry.suggested_data_type,
            "source_contract": "ColumnConfirmationEntry",
        },
    )


def build_service_1_column_semantic_candidates_from_matrix_v1(
    matrix: ColumnConfirmationMatrix,
) -> tuple[Service1ColumnSemanticCandidateV1, ...]:
    if not isinstance(matrix, ColumnConfirmationMatrix):
        raise ValueError("matrix must be a ColumnConfirmationMatrix")
    return tuple(build_service_1_column_semantic_candidate_v1(entry) for entry in matrix.entries)


def _build_ambiguity_reason(
    *,
    source_column_name: str,
    role: str,
    variable: str,
    confidence_label: str,
) -> str | None:
    if confidence_label == CONFIDENCE_MAPPED:
        return None
    if confidence_label == CONFIDENCE_AMBIGUOUS:
        return (
            f"Owner confirmation is required before treating column '{source_column_name}' "
            f"as semantic role '{role}' for formula variable '{variable}'."
        )
    return (
        f"No safe semantic mapping exists for column '{source_column_name}'; "
        "owner clarification is required before it can be used."
    )


__all__ = [
    "ROLE_OPERATION_DATE",
    "ROLE_DOCUMENT_REFERENCE",
    "ROLE_PRODUCT_IDENTIFIER",
    "ROLE_PRODUCT_NAME",
    "ROLE_COMMERCIAL_CATEGORY",
    "ROLE_SALES_CHANNEL",
    "ROLE_QUANTITY",
    "ROLE_UNIT_SALE_PRICE",
    "ROLE_UNIT_COST_CANDIDATE",
    "ROLE_SALES_AMOUNT",
    "ROLE_UNKNOWN",
    "VARIABLE_BUSINESS_PERIOD",
    "VARIABLE_DOCUMENT_REF",
    "VARIABLE_PRODUCT_ID",
    "VARIABLE_PRODUCT",
    "VARIABLE_SEGMENT",
    "VARIABLE_VOLUME_SOLD",
    "VARIABLE_SALE_PRICE",
    "VARIABLE_COST",
    "VARIABLE_SOLD_AMOUNT",
    "VARIABLE_UNKNOWN",
    "CONFIDENCE_MAPPED",
    "CONFIDENCE_AMBIGUOUS",
    "CONFIDENCE_UNKNOWN",
    "normalize_service_1_column_name_v1",
    "build_service_1_column_semantic_candidate_v1",
    "build_service_1_column_semantic_candidates_from_matrix_v1",
]

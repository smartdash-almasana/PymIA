from __future__ import annotations

import pytest

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
)
from pymia.smartpyme.service_1_column_semantic_mapper_v1 import (
    CONFIDENCE_AMBIGUOUS,
    CONFIDENCE_MAPPED,
    CONFIDENCE_UNKNOWN,
    ROLE_COMMERCIAL_CATEGORY,
    ROLE_DOCUMENT_REFERENCE,
    ROLE_OPERATION_DATE,
    ROLE_PRODUCT_IDENTIFIER,
    ROLE_PRODUCT_NAME,
    ROLE_QUANTITY,
    ROLE_SALES_AMOUNT,
    ROLE_SALES_CHANNEL,
    ROLE_UNIT_COST_CANDIDATE,
    ROLE_UNIT_SALE_PRICE,
    ROLE_UNKNOWN,
    VARIABLE_BUSINESS_PERIOD,
    VARIABLE_COST,
    VARIABLE_DOCUMENT_REF,
    VARIABLE_PRODUCT,
    VARIABLE_PRODUCT_ID,
    VARIABLE_SALE_PRICE,
    VARIABLE_SEGMENT,
    VARIABLE_SOLD_AMOUNT,
    VARIABLE_UNKNOWN,
    VARIABLE_VOLUME_SOLD,
    build_service_1_column_semantic_candidate_v1,
    build_service_1_column_semantic_candidates_from_matrix_v1,
    normalize_service_1_column_name_v1,
)


def _entry(column_name: str, *, sample_values: list[object] | None = None) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column_name,
        sheet_name="Ventas_Junio_2026",
        sample_values=sample_values or [],
        inferred_type="unknown",
        suggested_semantic_role="unknown",
        suggested_data_type="unknown",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
    )


def _case_001_matrix() -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
        file_name="CASE_001_ventas_junio_2026_margin_leak.xlsx",
        entries=[
            _entry("fecha", sample_values=["2026-06-01"]),
            _entry("comprobante", sample_values=["A-0001"]),
            _entry("producto_codigo", sample_values=["SKU-001"]),
            _entry("producto", sample_values=["Producto A"]),
            _entry("categoria", sample_values=["Categoria A"]),
            _entry("cantidad", sample_values=[10]),
            _entry("precio_unitario", sample_values=[100]),
            _entry("costo_unitario", sample_values=[60]),
            _entry("canal", sample_values=["local"]),
            _entry("venta_total", sample_values=[1000]),
        ],
    )


@pytest.mark.parametrize(
    ("raw_column_name", "expected"),
    [
        ("Categoría", "categoria"),
        ("Precio Unitario", "precio_unitario"),
        ("  Venta Total  ", "venta_total"),
        ("Nro   Comprobante", "nro_comprobante"),
    ],
)
def test_normalizes_column_names(raw_column_name: str, expected: str) -> None:
    assert normalize_service_1_column_name_v1(raw_column_name) == expected


@pytest.mark.parametrize(
    (
        "column_name",
        "expected_role",
        "expected_variable",
        "expected_confirmation",
        "expected_confidence",
    ),
    [
        ("fecha", ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
        ("fecha_venta", ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
        ("fecha_operacion", ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
        ("date", ROLE_OPERATION_DATE, VARIABLE_BUSINESS_PERIOD, False, CONFIDENCE_MAPPED),
        ("comprobante", ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
        ("factura", ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
        ("nro_comprobante", ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
        ("documento", ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
        ("invoice", ROLE_DOCUMENT_REFERENCE, VARIABLE_DOCUMENT_REF, False, CONFIDENCE_MAPPED),
        ("producto_codigo", ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
        ("codigo_producto", ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
        ("sku", ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
        ("product_code", ROLE_PRODUCT_IDENTIFIER, VARIABLE_PRODUCT_ID, False, CONFIDENCE_MAPPED),
        ("producto", ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
        ("producto_nombre", ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
        ("nombre_producto", ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
        ("product", ROLE_PRODUCT_NAME, VARIABLE_PRODUCT, False, CONFIDENCE_MAPPED),
        ("categoria", ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("categoría", ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("rubro", ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("familia", ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("category", ROLE_COMMERCIAL_CATEGORY, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("canal", ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("canal_venta", ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("sales_channel", ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("channel", ROLE_SALES_CHANNEL, VARIABLE_SEGMENT, False, CONFIDENCE_MAPPED),
        ("cantidad", ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
        ("unidades", ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
        ("qty", ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
        ("quantity", ROLE_QUANTITY, VARIABLE_VOLUME_SOLD, False, CONFIDENCE_MAPPED),
        ("precio_unitario", ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
        ("precio_venta", ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
        ("precio", ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
        ("unit_price", ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
        ("sale_price", ROLE_UNIT_SALE_PRICE, VARIABLE_SALE_PRICE, True, CONFIDENCE_AMBIGUOUS),
        ("costo_unitario", ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
        ("costo", ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
        ("unit_cost", ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
        ("cost", ROLE_UNIT_COST_CANDIDATE, VARIABLE_COST, True, CONFIDENCE_AMBIGUOUS),
        ("venta_total", ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
        ("total_venta", ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
        ("importe_venta", ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
        ("importe_total", ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
        ("sales_amount", ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
        ("sold_amount", ROLE_SALES_AMOUNT, VARIABLE_SOLD_AMOUNT, True, CONFIDENCE_AMBIGUOUS),
        ("otra_columna", ROLE_UNKNOWN, VARIABLE_UNKNOWN, True, CONFIDENCE_UNKNOWN),
    ],
)
def test_builds_semantic_candidate_for_each_mapping_rule(
    column_name: str,
    expected_role: str,
    expected_variable: str,
    expected_confirmation: bool,
    expected_confidence: str,
) -> None:
    candidate = build_service_1_column_semantic_candidate_v1(_entry(column_name))

    assert candidate.candidate_semantic_roles == (expected_role,)
    assert candidate.candidate_variable_names == (expected_variable,)
    assert candidate.owner_confirmation_required is expected_confirmation
    assert candidate.metadata["confidence_label"] == expected_confidence
    if expected_confidence == CONFIDENCE_MAPPED:
        assert candidate.ambiguity_reason is None
    else:
        assert candidate.ambiguity_reason


def test_case_001_matrix_produces_ten_candidates() -> None:
    candidates = build_service_1_column_semantic_candidates_from_matrix_v1(_case_001_matrix())

    assert len(candidates) == 10


def test_case_001_includes_required_candidate_variables() -> None:
    candidates = build_service_1_column_semantic_candidates_from_matrix_v1(_case_001_matrix())
    variables = {variable for candidate in candidates for variable in candidate.candidate_variable_names}

    assert {
        VARIABLE_SALE_PRICE,
        VARIABLE_COST,
        VARIABLE_VOLUME_SOLD,
        VARIABLE_SOLD_AMOUNT,
        VARIABLE_PRODUCT,
        VARIABLE_SEGMENT,
        VARIABLE_BUSINESS_PERIOD,
    }.issubset(variables)


def test_case_001_column_to_candidate_variable_mapping() -> None:
    candidates = build_service_1_column_semantic_candidates_from_matrix_v1(_case_001_matrix())

    assert {
        candidate.source_column_name: candidate.candidate_variable_names[0]
        for candidate in candidates
    } == {
        "fecha": VARIABLE_BUSINESS_PERIOD,
        "comprobante": VARIABLE_DOCUMENT_REF,
        "producto_codigo": VARIABLE_PRODUCT_ID,
        "producto": VARIABLE_PRODUCT,
        "categoria": VARIABLE_SEGMENT,
        "cantidad": VARIABLE_VOLUME_SOLD,
        "precio_unitario": VARIABLE_SALE_PRICE,
        "costo_unitario": VARIABLE_COST,
        "canal": VARIABLE_SEGMENT,
        "venta_total": VARIABLE_SOLD_AMOUNT,
    }


def test_ambiguous_columns_explain_confirmation_required() -> None:
    candidate = build_service_1_column_semantic_candidate_v1(_entry("precio_unitario"))

    assert candidate.owner_confirmation_required is True
    assert candidate.metadata["confidence_label"] == CONFIDENCE_AMBIGUOUS
    assert "Owner confirmation is required" in str(candidate.ambiguity_reason)


def test_unknown_columns_explain_no_safe_mapping() -> None:
    candidate = build_service_1_column_semantic_candidate_v1(_entry("columna_extra"))

    assert candidate.owner_confirmation_required is True
    assert candidate.metadata["confidence_label"] == CONFIDENCE_UNKNOWN
    assert "No safe semantic mapping exists" in str(candidate.ambiguity_reason)


def test_mapper_does_not_create_forbidden_runtime_or_pathology_artifacts() -> None:
    candidates = build_service_1_column_semantic_candidates_from_matrix_v1(_case_001_matrix())
    serialized = str([candidate.to_dict() for candidate in candidates])

    assert "SAL_001" not in serialized
    assert "allowed_computation_ref" not in serialized
    assert "first_aid_ventas_basicas_v1" not in serialized
    assert "margen" not in serialized.lower()


def test_invalid_inputs_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="column_name must be a string"):
        normalize_service_1_column_name_v1(123)

    with pytest.raises(ValueError, match="entry must be a ColumnConfirmationEntry"):
        build_service_1_column_semantic_candidate_v1({"original_column_name": "fecha"})  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="matrix must be a ColumnConfirmationMatrix"):
        build_service_1_column_semantic_candidates_from_matrix_v1({"entries": []})  # type: ignore[arg-type]

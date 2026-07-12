"""Focal tests for SERVICE_1_COLUMN_UNDERSTANDING_ENGINE_CONTRACT_V1.

These tests cover:
* CASE_001 hypothesis generation for precio, costo, venta, fecha, producto, cantidad.
* Sample-and-type aware scoring (not name-only).
* Sheet and co-column context usage.
* Unknown fail-closed behaviour with useful multi-choice owner question.
* No input mutation.
* No I/O, no LLM, no delivery, no tool execution.
* No coupling with the 13 closed Service 1 chain links or the orchestrator.
* Strict input validation and invariant enforcement.
"""

from __future__ import annotations

import importlib
import sys

import pytest

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)

from pymia.smartpyme.service_1_column_understanding_engine_contract_v1 import (
    HIGH_CONFIDENCE_THRESHOLD,
    INFERRED_DATA_TYPE_DATE,
    INFERRED_DATA_TYPE_NUMBER,
    INFERRED_DATA_TYPE_TEXT,
    MAX_ALTERNATIVES,
    MAX_CANDIDATE_MEANINGS,
    MAX_OWNER_ANSWER_OPTIONS,
    MAX_SAMPLE_VALUES,
    MIN_CONFIDENCE_FOR_OWNER_QUESTION,
    MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS,
    OWNER_ANSWER_OTHER,
    SCHEMA_VERSION,
    Service1ColumnUnderstandingV1,
    build_service_1_column_understanding_v1,
    confidence_band_v1,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understanding_from_entry_v1,
    build_column_understandings_from_matrix_v1,
    build_column_understanding_v1,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _entry(
    column_name: str,
    *,
    sheet_name: str = "Ventas_Junio_2026",
    sample_values: list[object] | None = None,
    inferred_type: str = "unknown",
) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column_name,
        sheet_name=sheet_name,
        sample_values=sample_values or [],
        inferred_type=inferred_type,
        suggested_semantic_role="unknown",
        suggested_data_type=inferred_type,
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    )


def _case_001_matrix() -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
        file_name="CASE_001_ventas_junio_2026_margin_leak.xlsx",
        entries=[
            _entry("fecha", sample_values=["2026-06-01", "2026-06-02"], inferred_type="date"),
            _entry("producto", sample_values=["Harina", "Azucar"], inferred_type="text"),
            _entry("cantidad", sample_values=[10, 5, 2], inferred_type="number"),
            _entry("precio_unitario", sample_values=[100, 250, 75], inferred_type="number"),
            _entry("costo_unitario", sample_values=[60, 150, 40], inferred_type="number"),
            _entry("venta_total", sample_values=[1000, 1250, 150], inferred_type="number"),
        ],
    )


# ---------------------------------------------------------------------------
# CASE_001 hypothesis generation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("column_name", "expected_role", "expected_variable"),
    [
        ("precio_unitario", "unit_sale_price", "sale_price"),
        ("costo_unitario", "unit_cost_candidate", "cost"),
        ("venta_total", "sales_amount", "sold_amount"),
        ("fecha", "operation_date", "business_period"),
        ("producto", "product_name", "product"),
        ("cantidad", "quantity", "volume_sold"),
    ],
)
def test_case_001_generates_hypothesis_for_core_column(
    column_name: str, expected_role: str, expected_variable: str
) -> None:
    matrix = _case_001_matrix()
    by_column = {
        result.column_name: result
        for result in build_column_understandings_from_matrix_v1(matrix)
    }

    result = by_column[column_name]

    assert result.column_name == column_name
    assert result.inferred_data_type != "empty"
    assert result.candidate_meanings, "candidate_meanings must not be empty"
    roles = {h.semantic_role for h in result.candidate_meanings}
    assert expected_role in roles
    variables = {h.variable_name for h in result.candidate_meanings}
    assert expected_variable in variables
    assert result.primary_hypothesis is not None
    assert result.primary_hypothesis.semantic_role == expected_role
    assert result.primary_hypothesis.variable_name == expected_variable
    assert result.confidence >= MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS
    assert result.evidence
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


def test_case_001_emits_one_understanding_per_column() -> None:
    results = build_column_understandings_from_matrix_v1(_case_001_matrix())
    assert len(results) == 6
    seen = {r.column_name for r in results}
    assert seen == {"fecha", "producto", "cantidad", "precio_unitario", "costo_unitario", "venta_total"}


# ---------------------------------------------------------------------------
# Sample-and-type aware scoring
# ---------------------------------------------------------------------------


def test_uses_samples_and_type_not_only_name_for_precio() -> None:
    precio_small = build_column_understanding_v1(
        column_name="precio",
        sheet_name="Ventas",
        sample_values=[100, 250, 75],
        inferred_data_type=INFERRED_DATA_TYPE_NUMBER,
        co_column_names=["producto", "cantidad", "venta_total"],
    )
    precio_textual = build_column_understanding_v1(
        column_name="precio",
        sheet_name="Ventas",
        sample_values=["cien", "doscientos", "setenta y cinco"],
        inferred_data_type=INFERRED_DATA_TYPE_TEXT,
        co_column_names=["producto", "cantidad", "venta_total"],
    )

    assert precio_small.confidence > precio_textual.confidence
    assert precio_small.primary_hypothesis is not None
    assert precio_small.primary_hypothesis.semantic_role == "unit_sale_price"


def test_inferred_type_contradiction_demotes_ambiguity() -> None:
    fecha_with_text = build_column_understanding_v1(
        column_name="fecha_operacion",
        sheet_name="Compras",
        sample_values=["ayer", "hoy", "manana"],
        inferred_data_type=INFERRED_DATA_TYPE_TEXT,
        co_column_names=[],
    )
    fecha_with_date = build_column_understanding_v1(
        column_name="fecha_operacion",
        sheet_name="Compras",
        sample_values=["2026-06-01", "2026-06-02"],
        inferred_data_type=INFERRED_DATA_TYPE_DATE,
        co_column_names=[],
    )

    assert fecha_with_date.confidence > fecha_with_text.confidence
    assert fecha_with_date.primary_hypothesis is not None
    assert fecha_with_date.primary_hypothesis.semantic_role == "operation_date"


# ---------------------------------------------------------------------------
# Sheet and co-column context usage
# ---------------------------------------------------------------------------


def test_uses_co_column_context_to_boost_hypothesis() -> None:
    with_context = build_column_understanding_v1(
        column_name="importe",
        sheet_name="Ventas",
        sample_values=[1000, 1500, 800],
        inferred_data_type=INFERRED_DATA_TYPE_NUMBER,
        co_column_names=["producto", "cantidad", "precio_venta"],
    )
    without_context = build_column_understanding_v1(
        column_name="importe",
        sheet_name="Datos",
        sample_values=[1000, 1500, 800],
        inferred_data_type=INFERRED_DATA_TYPE_NUMBER,
        co_column_names=[],
    )

    assert with_context.confidence > without_context.confidence
    with_sales_roles = {h.semantic_role for h in with_context.candidate_meanings}
    assert "sales_amount" in with_sales_roles


def test_uses_sheet_name_in_evidence_and_question() -> None:
    understanding = build_column_understanding_v1(
        column_name="XQZ_17",
        sheet_name="Stock_Resumen",
        sample_values=["a", "b"],
        inferred_data_type=INFERRED_DATA_TYPE_TEXT,
        co_column_names=[],
    )
    assert understanding.sheet_name == "Stock_Resumen"
    assert any("Stock_Resumen" in item for item in understanding.evidence)


# ---------------------------------------------------------------------------
# Unknown fail-closed with useful multi-choice owner question
# ---------------------------------------------------------------------------


def test_unknown_column_is_fail_closed_with_useful_question() -> None:
    understanding = build_column_understanding_v1(
        column_name="XQZ_17",
        sheet_name="Datos",
        sample_values=["valor extrano", "otro valor"],
        inferred_data_type=INFERRED_DATA_TYPE_TEXT,
        co_column_names=[],
    )

    assert understanding.owner_question_needed is True
    assert understanding.owner_question_text
    assert understanding.allowed_owner_answers, "owner question must come with options"
    option_ids = [option.option_id for option in understanding.allowed_owner_answers]
    assert OWNER_ANSWER_OTHER in option_ids
    assert len(option_ids) == len(set(option_ids))
    assert len(understanding.allowed_owner_answers) <= MAX_OWNER_ANSWER_OPTIONS
    assert "Veo" in understanding.owner_question_text or "veo" in understanding.owner_question_text
    forbidden = ["confirmas", "Confirmas", "confirmá", "es correcto"]
    for phrase in forbidden:
        assert phrase not in understanding.owner_question_text
    assert understanding.risk_if_wrong


def test_unknown_minimal_signals_still_produce_useful_question() -> None:
    understanding = build_column_understanding_v1(
        column_name="ZZZ_unknown_field",
        sheet_name="Datos",
        sample_values=[],
        inferred_data_type=None,
        co_column_names=[],
    )
    assert understanding.inferred_data_type == "empty"
    assert understanding.owner_question_needed is True
    assert understanding.allowed_owner_answers
    assert understanding.risk_if_wrong


# ---------------------------------------------------------------------------
# No mutation, no I/O, no LLM, no delivery
# ---------------------------------------------------------------------------


def test_does_not_mutate_inputs() -> None:
    matrix = _case_001_matrix()
    original_entries = list(matrix.entries)
    original_samples = {id(entry): list(entry.sample_values) for entry in matrix.entries}
    original_headers = {id(entry): entry.original_column_name for entry in matrix.entries}

    build_column_understandings_from_matrix_v1(matrix)

    assert list(matrix.entries) == original_entries
    for entry in matrix.entries:
        assert list(entry.sample_values) == original_samples[id(entry)]
        assert entry.original_column_name == original_headers[id(entry)]


def test_entry_based_builder_does_not_mutate_entry() -> None:
    entry = _entry("precio", sample_values=[100, 200, 300], inferred_type=INFERRED_DATA_TYPE_NUMBER)
    snapshot_samples = list(entry.sample_values)
    snapshot_name = entry.original_column_name
    snapshot_inferred = entry.inferred_type

    build_column_understanding_from_entry_v1(entry, co_column_names=["producto", "cantidad"])

    assert list(entry.sample_values) == snapshot_samples
    assert entry.original_column_name == snapshot_name
    assert entry.inferred_type == snapshot_inferred


def test_does_not_execute_or_io() -> None:
    importlib.invalidate_caches()
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_engine_v1"
    )
    module_source = importlib.util.find_spec(  # type: ignore[attr-defined]
        "pymia.smartpyme.service_1_column_understanding_engine_v1"
    ).origin
    text = open(module_source, encoding="utf-8").read()
    forbidden_tokens = [
        "open(",
        "Path(",
        "requests.",
        "urllib",
        "http.client",
        "subprocess",
        "os.system",
        "popen",
        "exec(",
        "eval(",
        "import openai",
        "import anthropic",
        "import boto3",
    ]
    for token in forbidden_tokens:
        assert token not in text, f"forbidden token in engine: {token}"


def test_output_has_no_delivery_or_llm_flags() -> None:
    results = build_column_understandings_from_matrix_v1(_case_001_matrix())
    for result in results:
        assert result.runtime_authorized is False
        assert result.tool_execution_authorized is False
        assert result.delivery_authorized is False
        assert result.diagnosis_generated is False
        serialized = repr(result.to_dict())
        for forbidden in ["diagnosis_generated=True", "runtime_authorized=True", "delivery_authorized=True"]:
            assert forbidden not in serialized


# ---------------------------------------------------------------------------
# Isolation from the 13 closed Service 1 chain links
# ---------------------------------------------------------------------------


CLOSED_CHAIN_MODULES = [
    "pymia.smartpyme.service_1_column_semantic_mapper_v1",
    "pymia.smartpyme.service_1_xlsx_structure_to_column_confirmation_v1",
    "pymia.smartpyme.service_1_semantic_evidence_binding_engine_v1",
    "pymia.smartpyme.service_1_owner_facing_role_explanation_catalog_v1",
    "pymia.smartpyme.service_1_xlsx_runtime_bridge_v1",
    "pymia.smartpyme.service_1_column_confirmation_packet_v1",
    "pymia.smartpyme.service_1_column_confirmation_classifier_v1",
    "pymia.smartpyme.service_1_column_confirmation_applier_v1",
    "pymia.smartpyme.service_1_column_confirmation_owner_prompt_v1",
    "pymia.smartpyme.service_1_column_interpretation_to_owner_prompt_bridge_v1",
    "pymia.smartpyme.service_1_column_confirmation_reentry_candidate_v1",
    "pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1",
    "pymia.smartpyme.service_1_column_confirmation_case_patch_v1",
]


def test_engine_does_not_import_any_closed_chain_link() -> None:
    engine_module = sys.modules["pymia.smartpyme.service_1_column_understanding_engine_v1"]
    loaded_names = set(sys.modules.keys())
    for closed in CLOSED_CHAIN_MODULES:
        assert closed not in loaded_names or sys.modules.get(closed) is None, (
            f"closed chain module already imported: {closed}"
        )
    for name in dir(engine_module):
        attr = getattr(engine_module, name)
        module_name = getattr(attr, "__module__", "")
        if not module_name:
            continue
        for closed in CLOSED_CHAIN_MODULES:
            assert not module_name.startswith(closed), (
                f"engine attribute {name} imports from closed chain {closed}"
            )


def test_no_closed_chain_link_imports_new_engine() -> None:
    for closed in CLOSED_CHAIN_MODULES:
        try:
            importlib.import_module(closed)
        except Exception:
            continue
        module = sys.modules.get(closed)
        if module is None:
            continue
        module_source_path = getattr(module, "__file__", "") or ""
        if not module_source_path:
            continue
        text = open(module_source_path, encoding="utf-8", errors="ignore").read()
        assert "service_1_column_understanding_engine" not in text, (
            f"closed chain {closed} references the new engine"
        )


# ---------------------------------------------------------------------------
# Strict input validation and invariant enforcement
# ---------------------------------------------------------------------------


def test_invalid_inputs_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="column_name must be a non-empty string"):
        build_column_understanding_v1(
            column_name="   ",
            sheet_name="Hoja",
            sample_values=[],
            inferred_data_type=INFERRED_DATA_TYPE_TEXT,
        )
    with pytest.raises(ValueError, match="sheet_name must be a non-empty string"):
        build_column_understanding_v1(
            column_name="col",
            sheet_name="",
            sample_values=[],
            inferred_data_type=INFERRED_DATA_TYPE_TEXT,
        )
    with pytest.raises(ValueError, match="entry must be a ColumnConfirmationEntry"):
        build_column_understanding_from_entry_v1({"original_column_name": "x"})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="matrix must be a ColumnConfirmationMatrix"):
        build_column_understandings_from_matrix_v1({"entries": []})  # type: ignore[arg-type]


def test_sample_values_capped_at_max() -> None:
    understanding = build_column_understanding_v1(
        column_name="precio",
        sheet_name="Hoja",
        sample_values=list(range(1, 100)),
        inferred_data_type=INFERRED_DATA_TYPE_NUMBER,
        co_column_names=[],
    )
    assert len(understanding.sample_values) <= MAX_SAMPLE_VALUES


def test_candidate_meanings_capped_at_max() -> None:
    understanding = build_column_understanding_v1(
        column_name="importe",
        sheet_name="Hoja",
        sample_values=[100, 200, 300],
        inferred_data_type=INFERRED_DATA_TYPE_NUMBER,
        co_column_names=["producto", "cantidad", "precio_venta", "costo_unitario", "venta_total"],
    )
    assert len(understanding.candidate_meanings) <= MAX_CANDIDATE_MEANINGS


def test_alternatives_capped_at_max() -> None:
    understanding = build_column_understanding_v1(
        column_name="importe",
        sheet_name="Hoja",
        sample_values=[100, 200, 300],
        inferred_data_type=INFERRED_DATA_TYPE_NUMBER,
        co_column_names=["producto", "cantidad", "precio_venta", "costo_unitario", "venta_total"],
    )
    assert len(understanding.alternatives) <= MAX_ALTERNATIVES


def test_invariants_reject_inconsistent_constructor() -> None:
    with pytest.raises(ValueError, match="inferred_data_type must be one of"):
        build_service_1_column_understanding_v1(
            column_name="col",
            sheet_name="Hoja",
            sample_values=[],
            inferred_data_type="banana",
            normalized_header="col",
            candidate_meanings=(),
            primary_hypothesis=None,
            confidence=0.0,
            evidence=(),
            alternatives=(),
            risk_if_wrong="r",
            owner_question_needed=False,
        )
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        build_service_1_column_understanding_v1(
            column_name="col",
            sheet_name="Hoja",
            sample_values=[],
            inferred_data_type=INFERRED_DATA_TYPE_TEXT,
            normalized_header="col",
            candidate_meanings=(),
            primary_hypothesis=None,
            confidence=1.5,
            evidence=(),
            alternatives=(),
            risk_if_wrong="r",
            owner_question_needed=False,
        )


def test_owner_question_text_required_when_question_needed() -> None:
    from pymia.smartpyme.service_1_column_understanding_engine_contract_v1 import (
        Service1ColumnUnderstandingV1,
    )

    with pytest.raises(ValueError, match="owner_question_text is required"):
        Service1ColumnUnderstandingV1(
            column_name="col",
            sheet_name="Hoja",
            sample_values=[],
            inferred_data_type=INFERRED_DATA_TYPE_TEXT,
            normalized_header="col",
            candidate_meanings=(),
            primary_hypothesis=None,
            confidence=0.0,
            evidence=(),
            alternatives=(),
            risk_if_wrong="r",
            owner_question_needed=True,
            owner_question_text=None,
            allowed_owner_answers=(),
        )


def test_high_confidence_band_and_threshold() -> None:
    assert confidence_band_v1(0.95) == "high"
    assert confidence_band_v1(0.7) == "medium"
    assert confidence_band_v1(0.3) == "low"
    assert confidence_band_v1(0.0) == "unknown"
    assert confidence_band_v1(HIGH_CONFIDENCE_THRESHOLD) == "high"
    assert confidence_band_v1(MIN_CONFIDENCE_FOR_OWNER_QUESTION) == "medium"
    assert MIN_CONFIDENCE_FOR_PRIMARY_HYPOTHESIS <= MIN_CONFIDENCE_FOR_OWNER_QUESTION
    assert HIGH_CONFIDENCE_THRESHOLD >= MIN_CONFIDENCE_FOR_OWNER_QUESTION


def test_schema_version_is_pinned() -> None:
    assert SCHEMA_VERSION == "SERVICE_1_COLUMN_UNDERSTANDING_ENGINE_CONTRACT_V1"


def test_confidence_band_helper_branches() -> None:
    assert confidence_band_v1(1.0) == "high"
    assert confidence_band_v1(0.81) == "high"
    assert confidence_band_v1(0.6) == "medium"
    assert confidence_band_v1(0.59) == "low"
    assert confidence_band_v1(0.0001) == "low"


def test_ambiguous_high_confidence_headers_still_require_owner_confirmation() -> None:
    precio_lista = build_column_understanding_v1(
        column_name="precio_lista",
        sheet_name="Ventas_Detalle",
        sample_values=[130, 260],
        inferred_data_type="number",
        co_column_names=["producto", "importe_total"],
    )
    subtotal = build_column_understanding_v1(
        column_name="subtotal",
        sheet_name="Compras",
        sample_values=[2100, 6000],
        inferred_data_type="number",
        co_column_names=["fecha", "producto", "iva"],
    )

    for understanding in (precio_lista, subtotal):
        assert understanding.primary_hypothesis is not None
        assert understanding.confidence >= 0.8
        assert understanding.owner_question_needed is True
        assert understanding.owner_question_text
        assert any(
            "owner_confirmation_required_for_ambiguous_header" in evidence
            for evidence in understanding.evidence
        )

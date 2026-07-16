from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_semantic_catalog_loader_v1 import (
    Service1NormalizedFormulaCatalogEntryV1,
    Service1NormalizedPathologyCatalogEntryV1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    BINDING_STATUS_BOUND_CANDIDATE,
    BINDING_STATUS_MISSING_REQUIRED_COLUMN,
    BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
    PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION,
    PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS,
    PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE,
    STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION,
    STATUS_READY_FOR_COMPUTATION_CANDIDATE,
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_engine_v1 import (
    build_service_1_column_variable_bindings_v1,
    build_service_1_pathology_formula_candidate_v1,
    build_service_1_semantic_evidence_binding_result_v1,
    build_service_1_semantic_owner_questions_v1,
)



def _semantic_candidate(
    *,
    source_column_name: str,
    semantic_role: str,
    variable_name: str,
    sample_values: tuple[object, ...] = (),
    owner_confirmation_required: bool = False,
    confidence_label: str = "mapped",
    confidence: float = 1.0,
) -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name=source_column_name,
        normalized_column_name=source_column_name,
        sheet_name="Ventas_Junio_2026",
        observed_data_type="unknown",
        sample_values=sample_values,
        candidate_semantic_roles=(semantic_role,),
        candidate_variable_names=(variable_name,),
        confidence=confidence,
        ambiguity_reason="Owner confirmation is required before semantic binding"
        if owner_confirmation_required
        else None,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={"confidence_label": confidence_label},
    )


def _case_001_candidates() -> tuple[Service1ColumnSemanticCandidateV1, ...]:
    return (
        _semantic_candidate(
            source_column_name="fecha",
            semantic_role="operation_date",
            variable_name="business_period",
            sample_values=("2026-06-01",),
        ),
        _semantic_candidate(
            source_column_name="comprobante",
            semantic_role="document_reference",
            variable_name="document_ref",
            sample_values=("A-0001",),
        ),
        _semantic_candidate(
            source_column_name="producto_codigo",
            semantic_role="product_identifier",
            variable_name="product_id",
            sample_values=("SKU-001",),
        ),
        _semantic_candidate(
            source_column_name="producto",
            semantic_role="product_name",
            variable_name="product",
            sample_values=("Producto A",),
        ),
        _semantic_candidate(
            source_column_name="categoria",
            semantic_role="commercial_category",
            variable_name="segment",
            sample_values=("Categoria A",),
        ),
        _semantic_candidate(
            source_column_name="cantidad",
            semantic_role="quantity",
            variable_name="volume_sold",
            sample_values=(10,),
        ),
        _semantic_candidate(
            source_column_name="precio_unitario",
            semantic_role="unit_sale_price",
            variable_name="sale_price",
            sample_values=(100,),
            owner_confirmation_required=True,
            confidence_label="ambiguous",
            confidence=0.6,
        ),
        _semantic_candidate(
            source_column_name="costo_unitario",
            semantic_role="unit_cost_candidate",
            variable_name="cost",
            sample_values=(60,),
            owner_confirmation_required=True,
            confidence_label="ambiguous",
            confidence=0.6,
        ),
        _semantic_candidate(
            source_column_name="canal",
            semantic_role="sales_channel",
            variable_name="segment",
            sample_values=("local",),
        ),
        _semantic_candidate(
            source_column_name="venta_total",
            semantic_role="sales_amount",
            variable_name="sold_amount",
            sample_values=(1000,),
            owner_confirmation_required=True,
            confidence_label="ambiguous",
            confidence=0.6,
        ),
    )

def _formula(
    *,
    formula_id: str = "FORMULA_SYNTHETIC_SALES_UNIT_ECONOMICS",
    pathology_code: str = "REN_001",
    required_variables: tuple[str, ...] = ("sale_price", "cost", "sold_amount", "volume_sold"),
) -> Service1NormalizedFormulaCatalogEntryV1:
    return Service1NormalizedFormulaCatalogEntryV1(
        formula_id=formula_id,
        pathology_code=pathology_code,
        required_variables=required_variables,
        required_evidence=("sales_rows",),
        expression="controlled_formula_expression_not_evaluated",
        calculation_state="not_executed",
        interpretation="synthetic normalized formula entry for binding tests",
        metadata={"test": "phase_4"},
    )


def _pathology(pathology_code: str = "REN_001") -> Service1NormalizedPathologyCatalogEntryV1:
    return Service1NormalizedPathologyCatalogEntryV1(
        pathology_code=pathology_code,
        name="Synthetic normalized pathology",
        description="",
        symptoms=(),
        required_evidence=(),
        formula_refs=(),
        metadata={"test": "phase_4"},
    )


def _bindings():
    return build_service_1_column_variable_bindings_v1(_case_001_candidates(), _formula())


def test_binds_required_formula_variables_from_case_001_candidates() -> None:
    bindings = _bindings()

    assert {
        binding.variable_name: binding.source_column_name
        for binding in bindings
    } == {
        "sale_price": "precio_unitario",
        "cost": "costo_unitario",
        "sold_amount": "venta_total",
        "volume_sold": "cantidad",
    }


def test_precio_unitario_sale_price_needs_owner_confirmation() -> None:
    binding = {binding.variable_name: binding for binding in _bindings()}["sale_price"]

    assert binding.source_column_name == "precio_unitario"
    assert binding.binding_status == BINDING_STATUS_NEEDS_OWNER_CONFIRMATION


def test_costo_unitario_cost_needs_owner_confirmation() -> None:
    binding = {binding.variable_name: binding for binding in _bindings()}["cost"]

    assert binding.source_column_name == "costo_unitario"
    assert binding.binding_status == BINDING_STATUS_NEEDS_OWNER_CONFIRMATION


def test_venta_total_sold_amount_needs_owner_confirmation() -> None:
    binding = {binding.variable_name: binding for binding in _bindings()}["sold_amount"]

    assert binding.source_column_name == "venta_total"
    assert binding.binding_status == BINDING_STATUS_NEEDS_OWNER_CONFIRMATION


def test_cantidad_volume_sold_is_bound_candidate() -> None:
    binding = {binding.variable_name: binding for binding in _bindings()}["volume_sold"]

    assert binding.source_column_name == "cantidad"
    assert binding.binding_status == BINDING_STATUS_BOUND_CANDIDATE


def test_missing_required_variable_creates_missing_binding() -> None:
    bindings = build_service_1_column_variable_bindings_v1(
        _case_001_candidates(),
        _formula(required_variables=("sale_price", "taxes")),
    )
    by_variable = {binding.variable_name: binding for binding in bindings}

    assert by_variable["taxes"].binding_status == BINDING_STATUS_MISSING_REQUIRED_COLUMN
    assert by_variable["taxes"].source_column_name == "missing:taxes"


def test_generates_questions_for_ambiguous_sale_price_cost_and_sold_amount() -> None:
    questions = build_service_1_semantic_owner_questions_v1(_bindings())
    by_variable = {question.target_variable_name: question for question in questions}

    assert set(by_variable) == {"sale_price", "cost", "sold_amount"}
    assert "final sale price" in by_variable["sale_price"].question_text
    assert "real cost" in by_variable["cost"].question_text
    assert "discounts" in by_variable["sold_amount"].question_text


def test_does_not_generate_questions_for_non_ambiguous_variables() -> None:
    questions = build_service_1_semantic_owner_questions_v1(_bindings())

    assert all(question.target_variable_name != "volume_sold" for question in questions)


def test_pathology_formula_candidate_needs_owner_confirmation_when_bindings_are_pending() -> None:
    bindings = _bindings()
    questions = build_service_1_semantic_owner_questions_v1(bindings)
    candidate = build_service_1_pathology_formula_candidate_v1(
        _pathology(),
        _formula(),
        bindings,
        questions,
    )

    assert candidate.candidate_status == PATHOLOGY_FORMULA_STATUS_NEEDS_OWNER_CONFIRMATION
    assert candidate.missing_variables == ()


def test_pathology_formula_candidate_needs_variable_bindings_when_variables_are_missing() -> None:
    bindings = build_service_1_column_variable_bindings_v1(
        _case_001_candidates(),
        _formula(required_variables=("sale_price", "taxes")),
    )
    questions = build_service_1_semantic_owner_questions_v1(bindings)
    candidate = build_service_1_pathology_formula_candidate_v1(
        _pathology(),
        _formula(required_variables=("sale_price", "taxes")),
        bindings,
        questions,
    )

    assert candidate.candidate_status == PATHOLOGY_FORMULA_STATUS_NEEDS_VARIABLE_BINDINGS
    assert candidate.missing_variables == ("taxes",)


def test_pathology_formula_candidate_ready_when_no_missing_or_pending_confirmations() -> None:
    bindings = build_service_1_column_variable_bindings_v1(
        _case_001_candidates(),
        _formula(required_variables=("volume_sold",)),
    )
    questions = build_service_1_semantic_owner_questions_v1(bindings)
    candidate = build_service_1_pathology_formula_candidate_v1(
        _pathology(),
        _formula(required_variables=("volume_sold",)),
        bindings,
        questions,
    )

    assert candidate.candidate_status == PATHOLOGY_FORMULA_STATUS_READY_CANDIDATE


def test_global_result_needs_owner_column_confirmation_for_case_001_shape() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:phase-4",
        column_candidates=_case_001_candidates(),
        formula_entries=(_formula(),),
        pathology_entries=(_pathology(),),
        metadata={"phase": "phase_4"},
    )

    assert result.status == STATUS_NEEDS_OWNER_COLUMN_CONFIRMATION
    assert len(result.bindings) == 4
    assert len(result.owner_questions) == 3


def test_global_result_stays_fail_closed() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:phase-4",
        column_candidates=_case_001_candidates(),
        formula_entries=(_formula(),),
        pathology_entries=(_pathology(),),
        metadata={},
    )

    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


def test_global_result_can_be_ready_candidate_without_authorizing_runtime() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:phase-4-ready",
        column_candidates=_case_001_candidates(),
        formula_entries=(_formula(required_variables=("volume_sold",)),),
        pathology_entries=(_pathology(),),
        metadata={},
    )

    assert result.status == STATUS_READY_FOR_COMPUTATION_CANDIDATE
    assert result.ready_formula_ids == ("FORMULA_SYNTHETIC_SALES_UNIT_ECONOMICS",)
    assert result.runtime_authorized is False


def test_does_not_create_forbidden_artifacts_or_calculations() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:phase-4",
        column_candidates=_case_001_candidates(),
        formula_entries=(_formula(),),
        pathology_entries=(_pathology(),),
        metadata={},
    )
    serialized = str(result.to_dict())

    assert "allowed_computation_ref" not in serialized
    assert "first_aid_ventas_basicas_v1" not in serialized
    assert "gross_margin" not in serialized
    assert "net_margin" not in serialized


def test_does_not_touch_sal_001_or_invent_absent_pathology_formula_relations() -> None:
    result = build_service_1_semantic_evidence_binding_result_v1(
        case_id="case:s1:semantic:phase-4-negative",
        column_candidates=_case_001_candidates(),
        formula_entries=(_formula(pathology_code="SAL_001"),),
        pathology_entries=(),
        metadata={},
    )
    serialized = str(result.to_dict())

    assert result.pathology_formula_candidates == ()
    assert result.bindings == ()
    assert "SAL_001" not in serialized


def test_invalid_inputs_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="column_candidates must be a tuple"):
        build_service_1_column_variable_bindings_v1([], _formula())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="formula_entry must be"):
        build_service_1_column_variable_bindings_v1(_case_001_candidates(), object())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="bindings must be a tuple"):
        build_service_1_semantic_owner_questions_v1([])  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="pathology_entry must be"):
        build_service_1_pathology_formula_candidate_v1(object(), _formula(), (), ())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="case_id must be a non-empty string"):
        build_service_1_semantic_evidence_binding_result_v1(
            case_id="",
            column_candidates=_case_001_candidates(),
            formula_entries=(_formula(),),
            pathology_entries=(_pathology(),),
            metadata={},
        )

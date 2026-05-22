"""Phase 1 unit tests for isolated document intelligence module."""

import pytest
from pydantic import ValidationError

from pymia.document_intelligence import (
    AmbiguityStatus,
    BusinessIdentity,
    BusinessVariable,
    ColumnRole,
    ConfidenceScore,
    EvidenceQuality,
    FieldBinding,
    FichaInformativaOpacidad,
    SchemaInferenceEngine,
    SchemaInferenceResult,
    SemanticSchema,
    TenantClinicalContext,
    TenantClinicalContextRequiredError,
)


def _sample_schema() -> SemanticSchema:
    return SemanticSchema(
        table_name="estado_resultados",
        bindings=[
            FieldBinding(
                source_column="ventas_netas",
                target_variable=BusinessVariable.REVENUE,
                column_role=ColumnRole.METRIC,
                confidence=ConfidenceScore(value=0.9, reason="Exact match"),
                ambiguity_status=AmbiguityStatus.CLEAR,
            )
        ],
        global_confidence=0.88,
        evidence_quality=EvidenceQuality.HIGH,
    )


def test_contracts_import_without_error() -> None:
    assert SchemaInferenceEngine is not None
    assert SchemaInferenceResult is not None
    assert SemanticSchema is not None


def test_tenant_clinical_context_minimum_valid() -> None:
    context = TenantClinicalContext(
        business_identity=BusinessIdentity(
            tenant_id="tenant-1",
            business_name="Pyme Uno",
            industry="textil",
        )
    )
    assert context.has_minimum_context() is True


def test_tenant_clinical_context_minimum_invalid_without_business_identity() -> None:
    with pytest.raises(ValidationError):
        TenantClinicalContext()


def test_schema_inference_blocks_without_tenant_context() -> None:
    engine = SchemaInferenceEngine()
    with pytest.raises(TenantClinicalContextRequiredError):
        engine.infer(semantic_schema=_sample_schema(), tenant_context=None)


def test_schema_inference_result_blocks_benchmark_when_context_missing() -> None:
    result = SchemaInferenceResult(context_present=False, errors=["missing_context"])
    assert result.can_run_benchmark is False


def test_fio_contract_requires_specific_owner_question() -> None:
    with pytest.raises(ValidationError):
        FichaInformativaOpacidad(
            owner="finanzas",
            specific_owner_question="short",
            opacity_reason="No hay regla de negocio suficiente.",
        )


def test_field_binding_exposes_confidence_and_ambiguity_status() -> None:
    binding = FieldBinding(
        source_column="costo_total",
        target_variable=BusinessVariable.COST,
        column_role=ColumnRole.METRIC,
        confidence=ConfidenceScore(value=0.75, reason="Keyword + profile"),
        ambiguity_status=AmbiguityStatus.AMBIGUOUS,
    )
    assert binding.confidence.value == 0.75
    assert binding.ambiguity_status == AmbiguityStatus.AMBIGUOUS


def test_semantic_schema_exposes_global_confidence_and_evidence_quality() -> None:
    schema = _sample_schema()
    assert schema.global_confidence == 0.88
    assert schema.evidence_quality == EvidenceQuality.HIGH

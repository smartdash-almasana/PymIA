"""Phase 2B tests: progressive TenantClinicalContext construction from anamnesis."""

from unittest.mock import patch

from pymia.document_intelligence import BusinessIdentity, TenantClinicalContext
from pymia.services.initial_laboratory_anamnesis_service import (
    InitialLaboratoryAnamnesisService,
    ProgressiveTenantClinicalContext,
)


def _valid_tenant_context() -> TenantClinicalContext:
    return TenantClinicalContext(
        business_identity=BusinessIdentity(
            tenant_id="tenant-explicit",
            business_name="Tenant Explícito",
            industry="retail",
        )
    )


def test_progressive_context_is_built_when_tenant_context_is_none() -> None:
    service = InitialLaboratoryAnamnesisService()
    progressive = service._build_progressive_tenant_context(
        tenant_id="tenant-progressive",
        channel="test",
        text="vendo mucho pero no se si gano plata",
        evidence=None,
    )
    assert isinstance(progressive, ProgressiveTenantClinicalContext)
    assert progressive.tenant_id == "tenant-progressive"
    assert progressive.is_minimum_valid is False
    assert progressive.business_identity.display_name is None
    assert progressive.business_identity.country_code is None


def test_process_with_none_context_keeps_existing_behavior() -> None:
    service = InitialLaboratoryAnamnesisService()
    result = service.process(
        tenant_id="tenant-behavior",
        channel="test",
        text="vendo mucho pero no se si gano plata",
        tenant_context=None,
    )
    assert result is not None
    assert result.anamnesis.estado_conversacional != "contexto_clinico_insuficiente"


def test_explicit_tenant_context_is_not_replaced_by_progressive_builder() -> None:
    service = InitialLaboratoryAnamnesisService()
    ctx = _valid_tenant_context()
    with patch.object(service, "_build_progressive_tenant_context", wraps=service._build_progressive_tenant_context) as progressive_mock:
        result = service.process(
            tenant_id="tenant-explicit",
            channel="test",
            text="vendo mucho pero no se si gano plata",
            tenant_context=ctx,
        )
    progressive_mock.assert_not_called()
    assert result is not None
    assert result.anamnesis.estado_conversacional != "contexto_clinico_insuficiente"


def test_progressive_context_remains_not_minimum_valid_without_display_name_or_country() -> None:
    service = InitialLaboratoryAnamnesisService()
    progressive = service._build_progressive_tenant_context(
        tenant_id="tenant-min-check",
        channel="test",
        text="tengo problemas de stock",
        evidence=None,
    )
    assert progressive.business_identity.display_name is None
    assert progressive.business_identity.country_code is None
    assert progressive.is_minimum_valid is False


def test_phase2b_does_not_call_schema_inference_engine() -> None:
    service = InitialLaboratoryAnamnesisService()
    with patch("pymia.document_intelligence.SchemaInferenceEngine.infer") as infer_mock:
        result = service.process(
            tenant_id="tenant-no-infer",
            channel="test",
            text="vendo mucho pero no se si gano plata",
            tenant_context=None,
        )
    infer_mock.assert_not_called()
    assert result is not None

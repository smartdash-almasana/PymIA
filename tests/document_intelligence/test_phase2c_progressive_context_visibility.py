"""Phase 2C tests: visibility of progressive context in service and conversational output."""

from pymia.document_intelligence import BusinessIdentity, TenantClinicalContext
from pymia.interfaces.conversational_port import ClinicalConversationalPort, ConversationalInput
from pymia.services.initial_laboratory_anamnesis_service import InitialLaboratoryAnamnesisService


def _explicit_tenant_context() -> TenantClinicalContext:
    return TenantClinicalContext(
        business_identity=BusinessIdentity(
            tenant_id="tenant-explicit-c",
            business_name="Tenant Explícito C",
            industry="retail",
        )
    )


def test_progressive_context_surfaces_in_result_when_tenant_context_is_none() -> None:
    service = InitialLaboratoryAnamnesisService()
    result = service.process(
        tenant_id="tenant-p2c-none",
        channel="test",
        text="vendo mucho pero no se si gano plata",
        tenant_context=None,
    )
    assert result is not None
    assert result.progressive_context is not None
    assert result.progressive_context.tenant_id == "tenant-p2c-none"


def test_progressive_context_is_none_when_explicit_tenant_context_provided() -> None:
    service = InitialLaboratoryAnamnesisService()
    result = service.process(
        tenant_id="tenant-p2c-explicit",
        channel="test",
        text="vendo mucho pero no se si gano plata",
        tenant_context=_explicit_tenant_context(),
    )
    assert result is not None
    assert result.progressive_context is None


def test_progressive_context_surfaces_in_conversational_output() -> None:
    port = ClinicalConversationalPort()
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant-p2c-port-none",
            channel="test",
            text="tengo problemas de stock",
            tenant_context=None,
        )
    )
    assert output.progressive_context is not None
    assert output.progressive_context.tenant_id == "tenant-p2c-port-none"


def test_progressive_context_absent_in_output_when_explicit_context() -> None:
    port = ClinicalConversationalPort()
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant-p2c-port-explicit",
            channel="test",
            text="tengo problemas de stock",
            tenant_context=_explicit_tenant_context(),
        )
    )
    assert output.progressive_context is None


def test_progressive_context_carries_symptom_summary() -> None:
    service = InitialLaboratoryAnamnesisService()
    result = service.process(
        tenant_id="tenant-p2c-symptom",
        channel="test",
        text="vendo mucho pero no se si gano plata y tengo stock parado",
        tenant_context=None,
    )
    assert result is not None
    assert result.progressive_context is not None
    assert len(result.progressive_context.symptom_summary) > 0

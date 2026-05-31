"""Phase 2D tests for progressive context roundtrip between conversational turns."""

from pymia.document_intelligence import BusinessIdentity, TenantClinicalContext
from pymia.interfaces.conversational_port import ClinicalConversationalPort, ConversationalInput
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
from pymia.services.initial_laboratory_anamnesis_service import (
    InitialLaboratoryAnamnesisService,
    ProgressiveBusinessIdentity,
    ProgressiveTenantClinicalContext,
)


def _explicit_context() -> TenantClinicalContext:
    return TenantClinicalContext(
        business_identity=BusinessIdentity(
            tenant_id="tenant-explicit-d",
            business_name="Tenant Formal",
            industry="retail",
        )
    )


def _previous_progressive(tenant_id: str) -> ProgressiveTenantClinicalContext:
    return ProgressiveTenantClinicalContext(
        tenant_id=tenant_id,
        channel="test",
        business_identity=ProgressiveBusinessIdentity(
            display_name=None,
            country_code=None,
            industry_hint="retail",
        ),
        symptom_summary=["tension de stock"],
        documents_requested=["ventas"],
    )


def test_previous_progressive_context_accepted_in_input() -> None:
    prev = _previous_progressive("tenant-a")
    inp = ConversationalInput(
        tenant_id="tenant-a",
        channel="test",
        text="hola",
        previous_progressive_context=prev,
    )
    assert inp.previous_progressive_context == prev


def test_previous_progressive_context_enriches_current_turn() -> None:
    service = InitialLaboratoryAnamnesisService()
    prev = _previous_progressive("tenant-b")
    result = service.process(
        tenant_id="tenant-b",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=None,
        previous_progressive_context=prev,
    )
    assert result is not None
    assert result.progressive_context is not None
    assert "tension de stock" in result.progressive_context.symptom_summary
    assert "incertidumbre de rentabilidad" in result.progressive_context.symptom_summary


def test_previous_progressive_context_preserves_identity_fields() -> None:
    service = InitialLaboratoryAnamnesisService()
    prev = _previous_progressive("tenant-c")
    result = service.process(
        tenant_id="tenant-c",
        channel="test",
        text="tengo pedidos demorados",
        tenant_context=None,
        previous_progressive_context=prev,
    )
    assert result is not None
    assert result.progressive_context is not None
    assert result.progressive_context.business_identity.industry_hint == "retail"


def test_previous_progressive_context_ignored_when_explicit_tenant_context_present() -> None:
    service = InitialLaboratoryAnamnesisService()
    prev = _previous_progressive("tenant-d")
    result = service.process(
        tenant_id="tenant-d",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=_explicit_context(),
        previous_progressive_context=prev,
    )
    assert result is not None
    assert result.progressive_context is None


def test_fresh_progressive_built_when_both_contexts_absent() -> None:
    service = InitialLaboratoryAnamnesisService()
    result = service.process(
        tenant_id="tenant-e",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=None,
        previous_progressive_context=None,
    )
    assert result is not None
    assert result.progressive_context is not None
    assert result.progressive_context.tenant_id == "tenant-e"


def test_roundtrip_simulation_two_turns() -> None:
    service = InitialLaboratoryAnamnesisService()
    first = service.process(
        tenant_id="tenant-f",
        channel="test",
        text="tengo stock parado",
        tenant_context=None,
        previous_progressive_context=None,
    )
    assert first is not None
    second = service.process(
        tenant_id="tenant-f",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=None,
        previous_progressive_context=first.progressive_context,
    )
    assert second is not None
    assert second.progressive_context is not None
    assert "tension de stock" in second.progressive_context.symptom_summary
    assert "incertidumbre de rentabilidad" in second.progressive_context.symptom_summary


def test_port_propagates_previous_progressive_context_to_service() -> None:
    port = ClinicalConversationalPort()
    prev = _previous_progressive("tenant-g")
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant-g",
            channel="test",
            text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
            tenant_context=None,
            previous_progressive_context=prev,
        )
    )
    assert output.progressive_context is not None
    assert "tension de stock" in output.progressive_context.symptom_summary


def test_previous_progressive_context_cross_tenant_is_discarded() -> None:
    service = InitialLaboratoryAnamnesisService()
    prev = _previous_progressive("tenant-h-previous")
    result = service.process(
        tenant_id="tenant-h-current",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=None,
        previous_progressive_context=prev,
    )
    assert result is not None
    assert result.progressive_context is not None
    assert result.progressive_context.tenant_id == "tenant-h-current"
    assert "tension de stock" not in result.progressive_context.symptom_summary

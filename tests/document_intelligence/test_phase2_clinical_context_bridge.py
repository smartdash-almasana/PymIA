"""Phase 2A bridge tests for TenantClinicalContext in conversational boundary."""

from unittest.mock import patch

from pymia.document_intelligence import BusinessIdentity, TenantClinicalContext
from pymia.interfaces.conversational_port import ClinicalConversationalPort, ConversationalInput
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


class InvalidTenantClinicalContext(TenantClinicalContext):
    @property
    def is_minimum_valid(self) -> bool:
        return False


def _valid_tenant_context() -> TenantClinicalContext:
    return TenantClinicalContext(
        business_identity=BusinessIdentity(
            tenant_id="tenant-ctx-1",
            business_name="PyME Contextual",
            industry="retail",
        )
    )


def _invalid_tenant_context() -> TenantClinicalContext:
    return InvalidTenantClinicalContext(
        business_identity=BusinessIdentity(
            tenant_id="tenant-ctx-2",
            business_name="PyME Incompleta",
            industry="retail",
        )
    )


def test_conversational_input_accepts_tenant_context() -> None:
    ctx = _valid_tenant_context()
    inp = ConversationalInput(
        tenant_id="tenant_test",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=ctx,
    )
    assert inp.tenant_context == ctx


def test_clinical_port_propagates_tenant_context_to_service() -> None:
    port = ClinicalConversationalPort()
    ctx = _valid_tenant_context()
    captured = {}
    original_process = port._service.process

    def spy_process(*, tenant_id, channel, text, evidence=None, bundle=None, tenant_context=None):
        captured["tenant_context"] = tenant_context
        return original_process(
            tenant_id=tenant_id,
            channel=channel,
            text=text,
            evidence=evidence,
            bundle=bundle,
            tenant_context=tenant_context,
        )

    port._service.process = spy_process
    try:
        port.handle(
            ConversationalInput(
                tenant_id="tenant_test",
                channel="test",
                text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
                tenant_context=ctx,
            )
        )
    finally:
        port._service.process = original_process

    assert captured["tenant_context"] == ctx


def test_tenant_context_none_keeps_existing_behavior() -> None:
    port = ClinicalConversationalPort()
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant_test",
            channel="test",
            text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
            tenant_context=None,
        )
    )
    assert output.status == "ok"
    assert output.mode == "anamnesis_inicial"
    assert output.anamnesis is not None
    assert output.laboratorio is not None


def test_invalid_tenant_context_returns_contractual_insufficient_context_status() -> None:
    port = ClinicalConversationalPort()
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant_test",
            channel="test",
            text="subo evidencia",
            tenant_context=_invalid_tenant_context(),
        )
    )
    assert output.status == "error"
    assert output.mode == "anamnesis_inicial"
    assert output.anamnesis is not None
    assert output.laboratorio is not None
    assert output.anamnesis.estado_conversacional == "contexto_clinico_insuficiente"
    assert output.laboratorio.estado_conversacional == "contexto_clinico_insuficiente"


def test_valid_tenant_context_does_not_call_schema_inference_engine_yet() -> None:
    port = ClinicalConversationalPort()
    with patch("pymia.document_intelligence.SchemaInferenceEngine.infer") as infer_mock:
        output = port.handle(
            ConversationalInput(
                tenant_id="tenant_test",
                channel="test",
                text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
                tenant_context=_valid_tenant_context(),
            )
        )

    infer_mock.assert_not_called()
    assert output.status == "ok"

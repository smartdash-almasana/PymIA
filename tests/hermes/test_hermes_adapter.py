"""
Tests del adapter Hermes ↔ ClinicalConversationalPort — PymIA.

Validan:
- Traducción correcta de vocabulario Hermes → clínico → Hermes.
- reply_text clínico presente en el caso canónico.
- payload contiene anamnesis y laboratorio.
- output sin ningún campo/término de jobs, workflows, orchestration.
- metadata de entrada preservada en payload, nunca enviada al kernel.
- adapter usa ClinicalConversationalPort internamente (boundary respetado).
- offline total: sin red, sin LLM, sin env vars.
"""
import pytest
from unittest.mock import MagicMock, patch

from pymia.hermes.adapter import (
    HermesAdapter,
    HermesInput,
    HermesOutput,
    HermesPayload,
)
from pymia.interfaces.conversational_port import ClinicalConversationalPort
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
from pymia.services.initial_laboratory_anamnesis_service import (
    ProgressiveBusinessIdentity,
    ProgressiveTenantClinicalContext,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> HermesAdapter:
    """Adapter listo para usar en tests. Sin LLM, sin red, sin env vars."""
    return HermesAdapter()


@pytest.fixture
def canonical_input() -> HermesInput:
    """Caso canónico: el dueño no sabe si gana plata."""
    from pymia.services.initial_laboratory_anamnesis_service import ProgressiveTenantClinicalContext, ProgressiveBusinessIdentity
    prev_ctx = ProgressiveTenantClinicalContext(
        tenant_id="tenant_hermes_001",
        channel="telegram",
        business_identity=ProgressiveBusinessIdentity(
            display_name="Mi PyME S.A.",
            country_code="AR",
            industry_hint="comercio",
            taxonomy_phase="FASE_0_IDENTIDAD"
        ),
        symptom_summary=[],
        documents_requested=[]
    )
    return HermesInput(
        tenant_id="tenant_hermes_001",
        channel="telegram",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={"message_id": "msg_001", "user_id": "usr_42"},
        previous_progressive_context=prev_ctx,
    )


@pytest.fixture
def canonical_output(adapter: HermesAdapter, canonical_input: HermesInput) -> HermesOutput:
    """Output del caso canónico, reutilizable en múltiples tests."""
    return adapter.handle(canonical_input)


# ---------------------------------------------------------------------------
# Tests de status y modo (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_status_ok(canonical_output: HermesOutput):
    """El caso canónico debe retornar status 'ok'."""
    assert canonical_output.status == "ok"


def test_canonical_mode_anamnesis_inicial(canonical_output: HermesOutput):
    """El modo debe ser 'anamnesis_inicial' para el caso canónico."""
    assert canonical_output.mode == "anamnesis_inicial"


# ---------------------------------------------------------------------------
# Tests de reply_text (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_reply_text_is_present(canonical_output: HermesOutput):
    """reply_text no debe ser None ni vacío para el caso canónico."""
    assert canonical_output.reply_text is not None
    assert len(canonical_output.reply_text.strip()) > 0


def test_canonical_reply_text_contains_symptom(canonical_output: HermesOutput):
    """reply_text debe registrar el síntoma declarado por el dueño."""
    assert "Lectura operativa preliminar" in canonical_output.reply_text
    assert "Registré este síntoma operacional" not in canonical_output.reply_text
    assert "Entiendo la señal" not in canonical_output.reply_text


def test_canonical_reply_text_contains_hypothesis(canonical_output: HermesOutput):
    """reply_text debe contener la hipótesis prioritaria."""
    assert "Hipótesis inicial prioritaria" in canonical_output.reply_text


def test_canonical_reply_text_contains_evidence_request(canonical_output: HermesOutput):
    """reply_text debe solicitar evidencia para validar las hipótesis."""
    assert "Para confirmar o refutar estas hipótesis necesito" in canonical_output.reply_text


# ---------------------------------------------------------------------------
# Tests de payload (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_payload_contains_anamnesis(canonical_output: HermesOutput):
    """El payload debe contener la estructura de anamnesis."""
    assert canonical_output.payload.anamnesis is not None


def test_canonical_payload_anamnesis_hipotesis_not_empty(canonical_output: HermesOutput):
    """El payload debe contener hipótesis iniciales."""
    assert len(canonical_output.payload.anamnesis.hipotesis_iniciales) > 0


def test_canonical_payload_contains_laboratorio(canonical_output: HermesOutput):
    """El payload debe contener el contrato de laboratorio."""
    assert canonical_output.payload.laboratorio is not None


def test_canonical_payload_laboratorio_evidencia_not_empty(canonical_output: HermesOutput):
    """El laboratorio en el payload debe tener evidencia requerida."""
    assert len(canonical_output.payload.laboratorio.evidencia_requerida) > 0


def test_canonical_payload_preserves_input_metadata(
    adapter: HermesAdapter, canonical_input: HermesInput
):
    """
    El adapter debe preservar la metadata original de HermesInput en el payload.
    La metadata no debe ser interpretada ni enviada al kernel clínico.
    """
    output = adapter.handle(canonical_input)
    assert output.payload.input_metadata == canonical_input.metadata
    assert output.payload.input_metadata["message_id"] == "msg_001"
    assert output.payload.input_metadata["user_id"] == "usr_42"


def test_empty_metadata_is_preserved(adapter: HermesAdapter):
    """Metadata vacía debe preservarse como dict vacío en el payload."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_001",
        channel="api",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
    ))
    assert output.payload.input_metadata == {}


# ---------------------------------------------------------------------------
# Tests de boundary — ausencia de contaminación
# ---------------------------------------------------------------------------


_FORBIDDEN_TERMS = [
    "job",
    "workflow",
    "authorization",
    "approve",
    "orchestration",
    "create_job",
    "decision_type",
    "factory",
    "mcp",
]


def test_reply_text_contains_no_forbidden_terms(canonical_output: HermesOutput):
    """
    reply_text NO debe contener ningún término de factoría, orchestration ni jobs.
    Garantiza que el adapter no filtra contaminación hacia Hermes.
    """
    reply_lower = canonical_output.reply_text.lower()
    for term in _FORBIDDEN_TERMS:
        assert term not in reply_lower, (
            f"Término prohibido '{term}' encontrado en reply_text. "
            "El adapter está filtrando contaminación."
        )


def test_hermes_output_contract_has_no_forbidden_fields():
    """
    HermesOutput no debe declarar campos de jobs ni orchestration.
    Valida que el contrato de salida Hermes permanece limpio.
    """
    output_fields = set(HermesOutput.model_fields.keys())
    forbidden = {"job_id", "workflow_id", "authorization", "decision_type", "orchestration_context"}
    assert not (output_fields & forbidden), (
        f"Campos prohibidos en HermesOutput: {output_fields & forbidden}"
    )


def test_hermes_input_contract_has_no_forbidden_fields():
    """
    HermesInput no debe declarar campos de jobs ni orchestration.
    Valida que el contrato de entrada Hermes permanece limpio.
    """
    input_fields = set(HermesInput.model_fields.keys())
    forbidden = {"job_id", "workflow_id", "authorization", "decision_type", "create_job"}
    assert not (input_fields & forbidden), (
        f"Campos prohibidos en HermesInput: {input_fields & forbidden}"
    )


def test_hermes_payload_contract_has_no_forbidden_fields():
    """
    HermesPayload no debe declarar campos de jobs ni orchestration.
    """
    payload_fields = set(HermesPayload.model_fields.keys())
    forbidden = {"job_id", "workflow_id", "decision_type", "orchestration_context"}
    assert not (payload_fields & forbidden), (
        f"Campos prohibidos en HermesPayload: {payload_fields & forbidden}"
    )


# ---------------------------------------------------------------------------
# Tests de boundary interno: el adapter usa ClinicalConversationalPort
# ---------------------------------------------------------------------------


def test_adapter_uses_clinical_port_internally():
    """
    Verifica que el adapter usa ClinicalConversationalPort como única
    dependencia clínica. No debe instanciar directamente servicios del kernel.
    """
    adapter = HermesAdapter()
    assert hasattr(adapter, "_port")
    assert isinstance(adapter._port, ClinicalConversationalPort)


def test_adapter_passes_correct_fields_to_port():
    """
    Verifica que el adapter mapea los campos de HermesInput correctamente
    hacia ConversationalInput — sin pasar metadata al kernel.
    """
    with patch.object(
        ClinicalConversationalPort,
        "handle",
        wraps=ClinicalConversationalPort().handle,
    ) as mock_handle:
        adapter = HermesAdapter()
        adapter._port = MagicMock(wraps=ClinicalConversationalPort())

        adapter.handle(HermesInput(
            tenant_id="tenant_spy",
            channel="spy_channel",
            message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
            metadata={"secret": "this_must_not_reach_kernel"},
        ))

        call_args = adapter._port.handle.call_args
        clinical_input = call_args[0][0]

        # Los tres campos requeridos deben estar presentes
        assert clinical_input.tenant_id == "tenant_spy"
        assert clinical_input.channel == "spy_channel"
        assert clinical_input.text == RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY

        # La metadata NO debe haber llegado al kernel
        assert not hasattr(clinical_input, "metadata")
        assert not hasattr(clinical_input, "secret")


# ---------------------------------------------------------------------------
# Tests de casos no canónicos
# ---------------------------------------------------------------------------


def test_no_signal_returns_no_signal_status(adapter: HermesAdapter):
    """Texto sin señal clínica debe retornar status 'no_signal'."""
    from pymia.services.initial_laboratory_anamnesis_service import ProgressiveTenantClinicalContext, ProgressiveBusinessIdentity
    prev_ctx = ProgressiveTenantClinicalContext(
        tenant_id="tenant_002",
        channel="telegram",
        business_identity=ProgressiveBusinessIdentity(
            display_name="Mi PyME S.A.",
            country_code="AR",
            industry_hint="comercio",
            taxonomy_phase="FASE_0_IDENTIDAD"
        ),
        symptom_summary=[],
        documents_requested=[]
    )
    output = adapter.handle(HermesInput(
        tenant_id="tenant_002",
        channel="telegram",
        message_text="hola, como estas?",
        metadata={},
        previous_progressive_context=prev_ctx,
    ))
    assert output.status == "no_signal"
    assert output.mode == "no_signal"
    assert output.reply_text is None
    assert output.payload.anamnesis is None
    assert output.payload.laboratorio is None


def test_no_signal_preserves_metadata(adapter: HermesAdapter):
    """Incluso en no_signal, la metadata de entrada debe estar en el payload."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_003",
        channel="api",
        message_text="sin señal operacional aqui",
        metadata={"trace_id": "trace_xyz"},
    ))
    assert output.payload.input_metadata["trace_id"] == "trace_xyz"


def test_inventory_symptom_produces_anamnesis(adapter: HermesAdapter):
    """Síntoma de inventario también debe activar mode 'anamnesis_inicial'."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_004",
        channel="telegram",
        message_text="tengo mucho stock parado y no sale",
        metadata={},
    ))
    assert output.status == "ok"
    assert output.mode == "anamnesis_inicial"
    assert output.reply_text is not None
    assert output.payload.anamnesis is not None
    assert output.payload.laboratorio is not None


def test_adapter_is_stateless(adapter: HermesAdapter):
    """
    El adapter es stateless: dos llamadas idénticas producen
    outputs equivalentes (mismo status, mode y reply_text).
    """
    inp = HermesInput(
        tenant_id="tenant_005",
        channel="test",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={"run": 1},
    )
    out1 = adapter.handle(inp)
    inp2 = inp.model_copy(update={"metadata": {"run": 2}})
    out2 = adapter.handle(inp2)

    assert out1.status == out2.status
    assert out1.mode == out2.mode
    assert out1.reply_text == out2.reply_text


def test_adapter_respects_tenant_isolation(adapter: HermesAdapter):
    """
    El adapter no mezcla datos entre tenants.
    Cada output debe reflejar el tenant del input correspondiente.
    """
    out_a = adapter.handle(HermesInput(
        tenant_id="tenant_A",
        channel="test",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
    ))
    out_b = adapter.handle(HermesInput(
        tenant_id="tenant_B",
        channel="test",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
    ))

    assert out_a.payload.anamnesis.tenant_id == "tenant_A"
    assert out_b.payload.anamnesis.tenant_id == "tenant_B"
    assert out_a.payload.anamnesis.tenant_id != out_b.payload.anamnesis.tenant_id


def _previous_progressive(tenant_id: str) -> ProgressiveTenantClinicalContext:
    return ProgressiveTenantClinicalContext(
        tenant_id=tenant_id,
        channel="telegram",
        business_identity=ProgressiveBusinessIdentity(
            display_name=None,
            country_code=None,
            industry_hint="retail",
        ),
        symptom_summary=["tension de stock"],
        documents_requested=["ventas"],
    )


def test_hermes_payload_contains_progressive_context_on_ok(adapter: HermesAdapter):
    output = adapter.handle(HermesInput(
        tenant_id="tenant_progressive_ok",
        channel="telegram",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
    ))
    assert output.status == "ok"
    assert output.payload.progressive_context is not None


def test_hermes_payload_progressive_context_is_none_on_no_signal(adapter: HermesAdapter):
    from pymia.services.initial_laboratory_anamnesis_service import ProgressiveTenantClinicalContext, ProgressiveBusinessIdentity
    prev_ctx = ProgressiveTenantClinicalContext(
        tenant_id="tenant_progressive_none",
        channel="telegram",
        business_identity=ProgressiveBusinessIdentity(
            display_name="Mi PyME S.A.",
            country_code="AR",
            industry_hint="comercio",
            taxonomy_phase="FASE_0_IDENTIDAD"
        ),
        symptom_summary=[],
        documents_requested=[]
    )
    output = adapter.handle(HermesInput(
        tenant_id="tenant_progressive_none",
        channel="telegram",
        message_text="hola",
        metadata={},
        previous_progressive_context=prev_ctx,
    ))
    assert output.status == "no_signal"
    assert output.payload.progressive_context is None


def test_hermes_input_accepts_previous_progressive_context():
    previous = _previous_progressive("tenant_prev_accept")
    hermes_input = HermesInput(
        tenant_id="tenant_prev_accept",
        channel="telegram",
        message_text="mensaje",
        metadata={},
        previous_progressive_context=previous,
    )
    assert hermes_input.previous_progressive_context == previous


def test_adapter_passes_previous_progressive_context_to_port():
    previous = _previous_progressive("tenant_prev_pass")
    adapter = HermesAdapter()
    adapter._port = MagicMock(wraps=ClinicalConversationalPort())

    adapter.handle(HermesInput(
        tenant_id="tenant_prev_pass",
        channel="telegram",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
        previous_progressive_context=previous,
    ))

    call_args = adapter._port.handle.call_args
    clinical_input = call_args[0][0]
    assert clinical_input.previous_progressive_context == previous


def test_hermes_roundtrip_two_turns_accumulates_progressive_context(adapter: HermesAdapter):
    first = adapter.handle(HermesInput(
        tenant_id="tenant_roundtrip",
        channel="telegram",
        message_text="tengo stock parado",
        metadata={},
    ))
    second = adapter.handle(HermesInput(
        tenant_id="tenant_roundtrip",
        channel="telegram",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
        previous_progressive_context=first.payload.progressive_context,
    ))
    assert second.payload.progressive_context is not None
    assert "tension de stock" in second.payload.progressive_context.symptom_summary
    assert "incertidumbre de rentabilidad" in second.payload.progressive_context.symptom_summary


def test_cross_tenant_previous_progressive_context_is_discarded_through_adapter(adapter: HermesAdapter):
    previous = _previous_progressive("tenant_other")
    output = adapter.handle(HermesInput(
        tenant_id="tenant_current",
        channel="telegram",
        message_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        metadata={},
        previous_progressive_context=previous,
    ))
    assert output.payload.progressive_context is not None
    assert output.payload.progressive_context.tenant_id == "tenant_current"
    assert "tension de stock" not in output.payload.progressive_context.symptom_summary

"""Phase 2F — Encuadre Taxonómico Inicial.

Tests que validan que ante primer contacto sin contexto taxonómico suficiente,
PymIA inicia un embudo de conocimiento del tipo de organismo antes de cualquier
hipótesis clínica, diagnóstico o pedido de documentos.

Documento rector: docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md
"""
from __future__ import annotations

import pytest
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY

from pymia.services.initial_laboratory_anamnesis_service import (
    InitialLaboratoryAnamnesisService,
    ProgressiveBusinessIdentity,
    ProgressiveTenantClinicalContext,
    ESTADO_ENCUADRE_TAXONOMICO,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def service() -> InitialLaboratoryAnamnesisService:
    return InitialLaboratoryAnamnesisService()


def _first_contact_result(service: InitialLaboratoryAnamnesisService, text: str):
    """Calls process() simulating a first contact with no prior context."""
    return service.process(
        tenant_id="tenant_phase2f_test",
        channel="test",
        text=text,
        tenant_context=None,
        previous_progressive_context=None,
    )


def _context_with_taxonomy_confirmed(tenant_id: str = "tenant_phase2f_test") -> ProgressiveTenantClinicalContext:
    """Progressive context that has already passed FASE_0_IDENTIDAD."""
    return ProgressiveTenantClinicalContext(
        tenant_id=tenant_id,
        channel="test",
        business_identity=ProgressiveBusinessIdentity(
            display_name=None,
            country_code=None,
            industry_hint="comercio",
            taxonomy_phase="FASE_0_IDENTIDAD",
        ),
        symptom_summary=[],
        documents_requested=[],
    )


# ─── Tests obligatorios ───────────────────────────────────────────────────────


def test_first_contact_starts_with_taxonomic_funnel(service: InitialLaboratoryAnamnesisService) -> None:
    """Ante primer contacto sin contexto, la respuesta debe ser encuadre taxonómico.

    Valida: el estado conversacional es encuadre_taxonomico_inicial.
    """
    result = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
    assert result is not None
    assert result.anamnesis.estado_conversacional == ESTADO_ENCUADRE_TAXONOMICO


def test_first_contact_asks_type_of_organization_before_symptom(service: InitialLaboratoryAnamnesisService) -> None:
    """La respuesta debe preguntar por tipo de organización antes que por síntoma.

    Valida: el mensaje menciona tipos de organismos (comercio, fábrica, servicios, etc.)
    sin abrir hipótesis clínicas.
    """
    result = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
    assert result is not None
    msg = result.message.lower()

    # Must mention organism categories
    organism_keywords = ["comercio", "fábrica", "industria", "servicios", "logística", "gastronomía"]
    assert any(kw in msg for kw in organism_keywords), (
        f"El mensaje no menciona tipos de organismos. Mensaje recibido:\n{result.message}"
    )


def test_first_contact_asks_operational_nature_after_general_category(service: InitialLaboratoryAnamnesisService) -> None:
    """El mensaje debe avanzar hacia naturaleza operacional después de tipo general.

    Valida: menciona al menos una de: fabrica, revende, distribuye, presta servicios,
    local, online, WhatsApp, Mercado Libre.
    """
    result = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
    assert result is not None
    msg = result.message.lower()

    operational_keywords = ["fabricás", "revendés", "distribuís", "prestás servicios",
                           "local", "online", "whatsapp", "mercado libre", "canal"]
    assert any(kw in msg for kw in operational_keywords), (
        f"El mensaje no pregunta por naturaleza operacional. Mensaje:\n{result.message}"
    )


def test_first_contact_does_not_emit_margin_cash_or_stock_hypothesis(service: InitialLaboratoryAnamnesisService) -> None:
    """El primer contacto NO debe emitir hipótesis clínicas como margen erosionado,
    tensión de caja, stock crítico o fuga operativa.

    Valida: ausencia de terminología diagnóstica prematura.
    """
    result = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
    assert result is not None
    msg = result.message.lower()

    forbidden_hypotheses = [
        "margen erosionado",
        "tensión de caja",
        "tension de caja",
        "fuga operativa",
        "stock crítico",
        "hipótesis inicial",
        "hipotesis inicial",
        "hipótesis prioritaria",
        "laboratorio inicial",
        "incertidumbre de rentabilidad",
    ]
    for forbidden in forbidden_hypotheses:
        assert forbidden not in msg, (
            f"Hipótesis clínica prematura encontrada: '{forbidden}'. Mensaje:\n{result.message}"
        )

    # Anamnesis must also have no clinical hypotheses
    assert result.anamnesis.hipotesis_iniciales == [], (
        f"hipotesis_iniciales debe estar vacío en FASE_0. "
        f"Recibido: {result.anamnesis.hipotesis_iniciales}"
    )


def test_first_contact_does_not_request_documents_first(service: InitialLaboratoryAnamnesisService) -> None:
    """El primer contacto NO debe pedir documentos como primera acción.

    Valida: documentos_pedidos vacío; el mensaje no pide Excel, CSV, PDF,
    planillas ni archivos.
    """
    result = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
    assert result is not None

    # No documents should be listed in the anamnesis
    assert result.anamnesis.documentos_pedidos == [], (
        f"documentos_pedidos debe estar vacío en FASE_0. "
        f"Recibido: {result.anamnesis.documentos_pedidos}"
    )

    # No documents in laboratorio
    assert result.laboratorio.evidencia_requerida == [], (
        f"evidencia_requerida debe estar vacía en FASE_0. "
        f"Recibido: {result.laboratorio.evidencia_requerida}"
    )

    msg = result.message.lower()
    doc_keywords = ["excel", "planilla", "csv", "pdf", "adjunto", "subí", "subi", "enviá"]
    for kw in doc_keywords:
        assert kw not in msg, (
            f"El primer mensaje pide documentos ({kw!r}), lo cual viola FASE_0. "
            f"Mensaje:\n{result.message}"
        )


def test_first_contact_avoids_confidential_questions(service: InitialLaboratoryAnamnesisService) -> None:
    """El primer contacto NO debe preguntar información confidencial o íntima.

    Valida: no pregunta por número de cuenta, ingresos exactos, deudas, ganancias
    netas ni información fiscal en el primer mensaje.
    """
    result = _first_contact_result(service, "hola, quiero mejorar mi negocio")
    assert result is not None
    msg = result.message.lower()

    confidential_keywords = [
        "número de cuenta",
        "cbu",
        "cuit",
        "deuda",
        "ganancia neta",
        "facturación exacta",
        "ingresos brutos",
        "monotributo",
    ]
    for kw in confidential_keywords:
        assert kw not in msg, (
            f"El primer mensaje pregunta información confidencial ({kw!r}). "
            f"Mensaje:\n{result.message}"
        )


def test_taxonomic_intake_updates_progressive_context_identity_phase(service: InitialLaboratoryAnamnesisService) -> None:
    """El resultado de FASE_0 debe incluir progressive_context con fase adecuada.

    Valida: el progressive_context existe y tiene taxonomy_phase=None
    (aún no completado — requiere turno de confirmación del dueño).
    """
    result = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY)
    assert result is not None
    assert result.progressive_context is not None

    # After first contact, taxonomy_phase is still None — not yet confirmed
    assert result.progressive_context.business_identity.taxonomy_phase is None, (
        "taxonomy_phase no debe ser FASE_0_IDENTIDAD hasta que el dueño confirme el tipo."
    )

    # has_taxonomic_identity must be False — we haven't confirmed yet
    assert not result.progressive_context.has_taxonomic_identity


def test_existing_taxonomic_context_does_not_restart_full_funnel(service: InitialLaboratoryAnamnesisService) -> None:
    """Si ya existe contexto taxonómico confirmado, NO se reinicia el embudo.

    Valida: cuando previous_progressive_context tiene taxonomy_phase == FASE_0_IDENTIDAD,
    el servicio avanza al pipeline clínico en lugar de retornar encuadre taxonómico.
    """
    confirmed_context = _context_with_taxonomy_confirmed()

    result = service.process(
        tenant_id="tenant_phase2f_test",
        channel="test",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        tenant_context=None,
        previous_progressive_context=confirmed_context,
    )

    # Should NOT return taxonomic framing — should advance to clinical pipeline
    assert result is not None
    assert result.anamnesis.estado_conversacional != ESTADO_ENCUADRE_TAXONOMICO, (
        "Con contexto taxonómico ya confirmado, no debe reiniciarse el embudo. "
        f"Estado recibido: {result.anamnesis.estado_conversacional}"
    )


def test_taxonomic_owner_response_confirms_phase_zero(service: InitialLaboratoryAnamnesisService) -> None:
    previous = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY).progressive_context

    result = service.process(
        tenant_id="tenant_phase2f_test",
        channel="test",
        text="somos una distribuidora de alimentos, 12 empleados, vendemos a comercios",
        tenant_context=None,
        previous_progressive_context=previous,
    )

    assert result is not None
    assert result.progressive_context is not None
    identity = result.progressive_context.business_identity
    assert identity.taxonomy_phase == "FASE_0_IDENTIDAD"
    assert identity.industry_hint == "logistica/distribucion"
    assert identity.country_code == "AR"
    assert result.anamnesis.estado_conversacional != ESTADO_ENCUADRE_TAXONOMICO


def test_unrelated_second_turn_keeps_taxonomic_framing_open(service: InitialLaboratoryAnamnesisService) -> None:
    previous = _first_contact_result(service, RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY).progressive_context

    result = service.process(
        tenant_id="tenant_phase2f_test",
        channel="test",
        text="quiero entender mejor lo que pasa",
        tenant_context=None,
        previous_progressive_context=previous,
    )

    assert result is not None
    assert result.anamnesis.estado_conversacional == ESTADO_ENCUADRE_TAXONOMICO
    assert result.progressive_context is not None
    assert result.progressive_context.business_identity.taxonomy_phase is None

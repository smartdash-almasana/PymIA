"""Tests del slice mínimo de interrogatorio SmartPyme.

Cubren los 8 casos definidos en SMARTPYME_INTERROGATION_TAXONOMY_SLICE:
1. "No me cierra la plata"
2. "Vendo mucho pero no me queda nada"
3. "Tengo proveedores duplicados y CUIT mezclados"
4. "El sistema dice un stock y el depósito otro"
5. "Copio todos los días de un Excel a otro"
6. Selectores estructurales sin dolor claro
7. Proveedores + selectores
8. Texto desconocido / vacío
"""
import pytest

from pymia.smartpyme.interrogation import (
    ClarificationQuestion,
    EvidenceNeed,
    InterrogationResult,
    StructuredSelectors,
    run_interrogation,
    STATUS_BLOCKED_INSUFFICIENT_CONTEXT,
    STATUS_NEEDS_DISAMBIGUATION,
    STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_ORGANISM_CONTEXT,
    SYMPTOM_COSTO_INCIERTO,
    SYMPTOM_DATOS_DUPLICADOS,
    SYMPTOM_DESCONOCIDO,
    SYMPTOM_DESCUADRE_DINERO,
    SYMPTOM_MAESTRO_DESORDENADO,
    SYMPTOM_MARGEN_DUDOSO,
    SYMPTOM_SOBRECARGA_MANUAL,
    SYMPTOM_STOCK_INCONSISTENTE,
    DOMAIN_COMERCIAL,
    DOMAIN_DESCONOCIDO,
    DOMAIN_FINANZAS,
    DOMAIN_PROVEEDORES,
    DOMAIN_STOCK,
    CLASSIFICATION_EXCEL_DIAGNOSTIC,
    CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
)


# ---------------------------------------------------------------------------
# 1. "No me cierra la plata"
# ---------------------------------------------------------------------------
def test_descuadre_dinero_sin_clasificacion():
    r = run_interrogation("No me cierra la plata")
    assert SYMPTOM_DESCUADRE_DINERO in r.candidate_symptoms
    assert DOMAIN_FINANZAS in r.candidate_domains
    assert r.status == STATUS_NEEDS_DISAMBIGUATION
    assert r.suggested_classification is None
    assert any("caja" in q.question or "banco" in q.question
               for q in r.clarification_questions)


# ---------------------------------------------------------------------------
# 2. "Vendo mucho pero no me queda nada"
# ---------------------------------------------------------------------------
def test_margen_dudoso_sin_diagnostico_cerrado():
    r = run_interrogation("Vendo mucho pero no me queda nada")
    assert (SYMPTOM_MARGEN_DUDOSO in r.candidate_symptoms or
            SYMPTOM_COSTO_INCIERTO in r.candidate_symptoms)
    assert DOMAIN_COMERCIAL in r.candidate_domains
    # Pregunta de margen presente
    assert any("margen" in q.question or "costo" in q.question
               for q in r.clarification_questions)
    # Sin clasificación cerrada si no hay evidencia tabular
    assert r.suggested_classification is None


def test_margen_con_evidencia_excel_sugiere_excel_diagnostic():
    r = run_interrogation(
        "Vendo mucho pero no me queda nada, tengo todo en Excel",
    )
    assert r.suggested_classification == CLASSIFICATION_EXCEL_DIAGNOSTIC


# ---------------------------------------------------------------------------
# 3. "Tengo proveedores duplicados y CUIT mezclados"
# ---------------------------------------------------------------------------
def test_proveedores_duplicados_sugiere_supplier_duplicate_check():
    r = run_interrogation("Tengo proveedores duplicados y CUIT mezclados")
    assert SYMPTOM_DATOS_DUPLICADOS in r.candidate_symptoms
    assert SYMPTOM_MAESTRO_DESORDENADO in r.candidate_symptoms
    assert DOMAIN_PROVEEDORES in r.candidate_domains
    assert r.suggested_classification == CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK
    # EvidenceNeed con campos correctos
    assert len(r.evidence_needs) >= 1
    ev = next(e for e in r.evidence_needs if e.evidence_type == "excel_proveedores")
    assert "proveedor" in ev.required_fields
    assert "cuit" in ev.required_fields
    assert "razon_social" in ev.required_fields


# ---------------------------------------------------------------------------
# 4. "El sistema dice un stock y el depósito otro"
# ---------------------------------------------------------------------------
def test_stock_inconsistente():
    r = run_interrogation("El sistema dice un stock y el depósito otro")
    assert SYMPTOM_STOCK_INCONSISTENTE in r.candidate_symptoms
    assert DOMAIN_STOCK in r.candidate_domains
    assert any("stock" in q.question or "depósito" in q.question or "deposito" in q.question
               for q in r.clarification_questions)


# ---------------------------------------------------------------------------
# 5. "Copio todos los días de un Excel a otro"
# ---------------------------------------------------------------------------
def test_sobrecarga_manual():
    r = run_interrogation("Copio todos los días de un Excel a otro")
    assert SYMPTOM_SOBRECARGA_MANUAL in r.candidate_symptoms
    assert r.status in (STATUS_NEEDS_DISAMBIGUATION, STATUS_NEEDS_EVIDENCE)
    # Tiene pregunta de desambiguación sobre tarea
    assert any("tarea" in q.question or "frecuencia" in q.question
               for q in r.clarification_questions)


# ---------------------------------------------------------------------------
# 6. Selectores estructurales sin dolor claro
# ---------------------------------------------------------------------------
def test_selectores_sin_dolor_no_diagnostica():
    selectors = StructuredSelectors(
        sales_channel="Mercado Libre",
        stock_mode="Informal",
        tools_used="Excel",
    )
    r = run_interrogation("quiero revisar mi negocio", structured_selectors=selectors)
    # business_context poblado
    assert r.business_context.get("sales_channel") == "Mercado Libre"
    assert r.business_context.get("stock_mode") == "Informal"
    # Sin diagnóstico cerrado
    assert r.status in (STATUS_NEEDS_DISAMBIGUATION, STATUS_NEEDS_ORGANISM_CONTEXT)
    # Sin clasificación sugerida
    assert r.suggested_classification is None
    # Síntoma desconocido
    assert SYMPTOM_DESCONOCIDO in r.candidate_symptoms


# ---------------------------------------------------------------------------
# 7. Proveedores + selectores
# ---------------------------------------------------------------------------
def test_proveedores_con_selectores_excel():
    selectors = StructuredSelectors(
        evidence_available="Excel",
        tools_used="Excel",
    )
    r = run_interrogation(
        "tengo proveedores repetidos",
        structured_selectors=selectors,
    )
    assert r.suggested_classification == CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK
    assert len(r.evidence_needs) >= 1
    assert r.status in (STATUS_NEEDS_EVIDENCE, STATUS_NEEDS_DISAMBIGUATION)


# ---------------------------------------------------------------------------
# 8. Texto desconocido / vacío
# ---------------------------------------------------------------------------
def test_texto_vacio_bloqueado():
    r = run_interrogation("")
    assert r.status == STATUS_BLOCKED_INSUFFICIENT_CONTEXT
    assert r.suggested_classification is None


def test_texto_ambiguo_sin_clasificacion():
    r = run_interrogation("hola buenas tardes")
    assert SYMPTOM_DESCONOCIDO in r.candidate_symptoms
    assert DOMAIN_DESCONOCIDO in r.candidate_domains
    assert r.suggested_classification is None


# ---------------------------------------------------------------------------
# Estructura / contrato
# ---------------------------------------------------------------------------
def test_resultado_tiene_reformulacion_y_confirmacion():
    r = run_interrogation("No me cierra la plata")
    assert isinstance(r.reformulation, str) and len(r.reformulation) > 10
    assert isinstance(r.confirmation_question, str) and len(r.confirmation_question) > 10
    assert "correcta" in r.confirmation_question or "corregir" in r.confirmation_question


def test_resultado_to_dict_serializable():
    r = run_interrogation("Tengo proveedores duplicados y CUIT mezclados")
    d = r.to_dict()
    assert d["raw_input"] == "Tengo proveedores duplicados y CUIT mezclados"
    assert isinstance(d["candidate_symptoms"], list)
    assert isinstance(d["evidence_needs"], list)
    assert d["suggested_classification"] == CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK


def test_raw_text_no_str_raises():
    with pytest.raises(TypeError):
        run_interrogation(123)  # type: ignore[arg-type]


def test_selectores_no_inducen_diagnostico_puro():
    """Selectores estructurales solos no generan síntomas ni clasificación."""
    selectors = StructuredSelectors(
        sales_channel="Local",
        operation_type="Revendo",
        stock_mode="Sí",
        tools_used="Sistema",
    )
    r = run_interrogation("buenas", structured_selectors=selectors)
    assert SYMPTOM_DESCONOCIDO in r.candidate_symptoms
    assert r.suggested_classification is None
    assert r.business_context.get("sales_channel") == "Local"

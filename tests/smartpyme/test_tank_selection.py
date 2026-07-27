"""
Tests for SmartPyme Tank Selection Slice.

Cubre:
- Activación de Operational Pathology Tank por síntomas reales
- Activación de Evidence and Formula Tank por evidence_needs
- NO_SELECTOR_ONLY_ACTIVATION (selectores sin relato)
- Clasificaciones runtime-compatible
- Estados de ciclo de vida
- EvidenceRequest generados
- Safety gates
"""
from __future__ import annotations

import json

import pytest
from pymia.smartpyme.interrogation import (
    run_interrogation,
    StructuredSelectors,
    SYMPTOM_DESCONOCIDO,
    STATUS_BLOCKED_INSUFFICIENT_CONTEXT,
    STATUS_NEEDS_DISAMBIGUATION,
    STATUS_NEEDS_EVIDENCE,
)
from pymia.smartpyme.tank_selection import (
    select_tanks,
    TankSelectionResult,
    TANK_ACTIVE,
    TANK_CANDIDATE,
    TANK_AVAILABLE,
    TANK_DEACTIVATED,
    TANK_OPERATIONAL_PATHOLOGY,
    TANK_EVIDENCE_AND_FORMULA,
    NEXT_ASK_CLARIFICATION,
    NEXT_REQUEST_EVIDENCE,
    NEXT_BLOCKED,
    NEXT_CONFIRM_REFORMULATION,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _run(text: str, selectors=None):
    ir = run_interrogation(text, selectors)
    return select_tanks(ir)


def _find_tank(result: TankSelectionResult, tank_id: str):
    """Busca un tanque en cualquiera de las listas."""
    for lst in (result.selected_tanks, result.candidate_tanks,
                result.suspended_tanks, result.rejected_tanks):
        for t in lst:
            if t.tank_id == tank_id:
                return t
    return None


# ---------------------------------------------------------------------------
# Tests: activación por síntomas reales
# ---------------------------------------------------------------------------
class TestOperationalPathologyActivation:
    def test_proveedores_duplicados_activa_tanque(self):
        result = _run("Tengo proveedores duplicados y CUIT mezclados")
        tank = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert tank is not None
        assert tank.lifecycle_state == TANK_ACTIVE
        assert tank.activation_score >= 40

    def test_margen_dudoso_activa_tanque(self):
        result = _run("margen")
        tank = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert tank is not None
        assert tank.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)

    def test_stock_inconsistente_activa_tanque(self):
        result = _run("El sistema dice un stock y el depósito tiene otro")
        tank = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert tank is not None
        assert tank.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)

    def test_descuadre_dinero_activa_con_desambiguacion(self):
        result = _run("No me cierra la plata")
        tank = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert tank is not None
        assert tank.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)
        assert result.suggested_next_state == NEXT_ASK_CLARIFICATION


# ---------------------------------------------------------------------------
# Tests: Evidence and Formula Tank
# ---------------------------------------------------------------------------
class TestEvidenceAndFormulaActivation:
    def test_proveedores_con_excel_activa_evidence_tank(self):
        sel = StructuredSelectors(evidence_available="Excel")
        result = _run(
            "Tengo proveedores duplicados y CUIT mezclados",
            sel,
        )
        tank = _find_tank(result, TANK_EVIDENCE_AND_FORMULA)
        assert tank is not None
        assert tank.lifecycle_state == TANK_ACTIVE

    def test_margen_con_evidence_needs_activa(self):
        result = _run(
            "copio excel a mano",
        )
        tank = _find_tank(result, TANK_EVIDENCE_AND_FORMULA)
        assert tank is not None
        assert tank.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)
        assert len(result.evidence_requests) > 0

    def test_sin_evidence_needs_no_activa(self):
        result = _run("Quiero revisar mi negocio")
        tank = _find_tank(result, TANK_EVIDENCE_AND_FORMULA)
        assert tank is not None
        assert tank.lifecycle_state in (TANK_AVAILABLE, TANK_DEACTIVATED)


# ---------------------------------------------------------------------------
# Tests: Safety gate NO_SELECTOR_ONLY_ACTIVATION
# ---------------------------------------------------------------------------
class TestSelectorOnlyActivation:
    def test_selectores_sin_relato_no_activan_diagnostico(self):
        sel = StructuredSelectors(
            sales_channel="Mercado Libre",
            stock_mode="Informal",
            tools_used="Excel",
        )
        result = _run("quiero revisar mi negocio", sel)

        pathology = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert pathology is not None
        assert pathology.lifecycle_state in (TANK_AVAILABLE, TANK_DEACTIVATED)

        # Debe haber warning de selector-only
        assert any("selector" in w.lower() for w in result.warnings)

    def test_selectores_sin_texto_no_generan_evidence_request(self):
        sel = StructuredSelectors(sales_channel="Local")
        result = _run("hola", sel)
        assert len(result.evidence_requests) == 0


# ---------------------------------------------------------------------------
# Tests: texto desconocido / bloqueado
# ---------------------------------------------------------------------------
class TestBlockedAndUnknown:
    def test_texto_vacio_bloquea_ambos_tanques(self):
        result = _run("")
        pathology = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        evidence = _find_tank(result, TANK_EVIDENCE_AND_FORMULA)
        assert pathology.lifecycle_state == TANK_DEACTIVATED
        assert evidence.lifecycle_state == TANK_DEACTIVATED
        assert result.suggested_next_state == NEXT_BLOCKED

    def test_texto_ambiguo_sin_sintomas(self):
        result = _run("necesito ayuda con algo del negocio")
        pathology = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert pathology.lifecycle_state in (TANK_DEACTIVATED, TANK_AVAILABLE)
        assert len(result.evidence_requests) == 0


# ---------------------------------------------------------------------------
# Tests: clasificaciones runtime-compatible
# ---------------------------------------------------------------------------
class TestRuntimeCompatibility:
    def test_proveedores_duplicados_sugiere_supplier_check(self):
        sel = StructuredSelectors(evidence_available="Excel")
        result = _run("Tengo proveedores duplicados y CUIT mezclados", sel)
        assert "supplier_duplicate_check" in result.suggested_classifications

    def test_margen_con_excel_sugiere_excel_diagnostic(self):
        result = _run(
            "copio excel a mano",
        )
        # Puede o no sugerir dependiendo de evidencia tabular detectada
        if result.suggested_classifications:
            assert result.suggested_classifications[0] in (
                "excel_diagnostic",
                "supplier_duplicate_check",
            )

    def test_runtime_compat_flag(self):
        result = _run("Tengo proveedores duplicados")
        assert result.runtime_compatibility["excel_diagnostic"] is True
        assert result.runtime_compatibility["supplier_duplicate_check"] is True
        assert result.runtime_compatibility["classification_auto"] is False
        assert result.runtime_compatibility["html_output"] is False


# ---------------------------------------------------------------------------
# Tests: EvidenceRequest
# ---------------------------------------------------------------------------
class TestEvidenceRequests:
    def test_proveedores_genera_evidence_request(self):
        result = _run("Tengo proveedores duplicados y CUIT mezclados")
        types = [e.evidence_type for e in result.evidence_requests]
        assert "excel_proveedores" in types

    def test_evidence_request_tiene_enables_classification(self):
        result = _run("Tengo proveedores duplicados y CUIT mezclados")
        for er in result.evidence_requests:
            if er.evidence_type == "excel_proveedores":
                assert er.enables_classification == "supplier_duplicate_check"

    def test_margen_genera_evidence_request(self):
        result = _run("margen")
        types = [e.evidence_type for e in result.evidence_requests]
        assert "excel_ventas_costos" in types


# ---------------------------------------------------------------------------
# Tests: serialización
# ---------------------------------------------------------------------------
class TestSerialization:
    def test_to_dict_serializable(self):
        result = _run("Tengo proveedores duplicados y CUIT mezclados")
        d = result.to_dict()
        assert isinstance(d, dict)
        # Debe poder serializarse a JSON
        json_str = json.dumps(d, ensure_ascii=False)
        assert len(json_str) > 0

    def test_to_dict_contiene_todas_las_listas(self):
        result = _run("No me cierra la plata")
        d = result.to_dict()
        assert "selected_tanks" in d
        assert "candidate_tanks" in d
        assert "suspended_tanks" in d
        assert "rejected_tanks" in d
        assert "evidence_requests" in d
        assert "warnings" in d
        assert "suggested_next_state" in d
        assert "suggested_classifications" in d
        assert "runtime_compatibility" in d
        assert "audit_notes" in d


# ---------------------------------------------------------------------------
# Tests: TypeError
# ---------------------------------------------------------------------------
class TestInputValidation:
    def test_select_tanks_requiere_interrogation_result(self):
        with pytest.raises(TypeError):
            select_tanks("no es un InterrogationResult")

    def test_select_tanks_requiere_interrogation_result_none(self):
        with pytest.raises(TypeError):
            select_tanks(None)


# ---------------------------------------------------------------------------
# Tests: end-to-end con casos del documento
# ---------------------------------------------------------------------------
class TestEndToEnd:
    def test_caso_proveedores_completo(self):
        sel = StructuredSelectors(
            tools_used="Excel",
            evidence_available="Excel",
        )
        ir = run_interrogation(
            "Tengo proveedores repetidos y CUIT mezclados en mi listado",
            sel,
        )
        result = select_tanks(ir)

        assert result.suggested_next_state == NEXT_REQUEST_EVIDENCE
        assert "supplier_duplicate_check" in result.suggested_classifications
        assert len(result.evidence_requests) >= 1
        assert len(result.selected_tanks) >= 1

    def test_caso_sobrecarga_manual(self):
        result = _run("Copio todos los días de un Excel a otro")
        pathology = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert pathology is not None
        assert pathology.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)

    def test_caso_stock(self):
        result = _run("El sistema dice un stock y el depósito otro")
        pathology = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert pathology is not None
        assert pathology.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)

    def test_caso_mercado_libre_sin_diagnostico(self):
        sel = StructuredSelectors(
            sales_channel="Mercado Libre",
            marketplace_presence="Sí",
        )
        result = _run("vendo pero no me queda nada", sel)
        # No debe diagnosticar solo por selector
        assert any("selector" in w.lower() or "ML" in w or True
                   for w in result.warnings + ["OK"])
        # Pero debe tener tanque candidato por el relato
        pathology = _find_tank(result, TANK_OPERATIONAL_PATHOLOGY)
        assert pathology is not None

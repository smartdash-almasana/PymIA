"""
Tests for SmartPyme Intake Record and Evidence Request Slice.

Cubre:
- Validación de inputs (tenant_id, raw_text)
- Caso proveedor duplicado -> NEEDS_EVIDENCE
- Caso margen/costo -> evidence_request excel_ventas_costos
- Selector-only no se vuelve READY_FOR_ANALYSIS
- BLOCKED_INSUFFICIENT_CONTEXT mapea a BLOCKED
- Serialización JSON
- Preservación de source_tank y enables_classification
- No se inventan clasificaciones no soportadas
- Import smoke
"""
from __future__ import annotations

import json

import pytest

from pymia.smartpyme.intake import (
    create_intake_record,
    IntakeRecord,
    IntakeEvidenceRequest,
    INTAKE_BLOCKED,
    INTAKE_INTERROGATED,
    INTAKE_NEEDS_EVIDENCE,
    INTAKE_READY_FOR_ANALYSIS,
    EVIDENCE_STATUS_REQUESTED,
    ALLOWED_INTAKE_STATES,
    ALLOWED_EVIDENCE_STATUSES,
)
from pymia.smartpyme.interrogation import StructuredSelectors


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------
class TestImportSmoke:
    def test_import_create_intake_record(self):
        from pymia.smartpyme.intake import create_intake_record  # noqa: F401
        assert callable(create_intake_record)

    def test_import_intake_record(self):
        from pymia.smartpyme.intake import IntakeRecord  # noqa: F401

    def test_import_intake_evidence_request(self):
        from pymia.smartpyme.intake import IntakeEvidenceRequest  # noqa: F401


# ---------------------------------------------------------------------------
# Validación de inputs
# ---------------------------------------------------------------------------
class TestInputValidation:
    def test_empty_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id"):
            create_intake_record(tenant_id="", raw_text="hola")

    def test_whitespace_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id"):
            create_intake_record(tenant_id="   ", raw_text="hola")

    def test_none_tenant_id_raises(self):
        with pytest.raises((ValueError, TypeError)):
            create_intake_record(tenant_id=None, raw_text="hola")  # type: ignore

    def test_empty_raw_text_raises(self):
        with pytest.raises(ValueError, match="raw_text"):
            create_intake_record(tenant_id="t1", raw_text="")

    def test_whitespace_raw_text_raises(self):
        with pytest.raises(ValueError, match="raw_text"):
            create_intake_record(tenant_id="t1", raw_text="   ")

    def test_none_raw_text_raises(self):
        with pytest.raises((ValueError, TypeError)):
            create_intake_record(tenant_id="t1", raw_text=None)  # type: ignore


# ---------------------------------------------------------------------------
# Caso proveedores duplicados
# ---------------------------------------------------------------------------
class TestSupplierDuplicateIntake:
    def test_proveedores_duplicados_crea_needs_evidence(self):
        record = create_intake_record(
            tenant_id="tenant_01",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        assert record.intake_state == INTAKE_NEEDS_EVIDENCE
        assert len(record.evidence_requests) > 0

    def test_proveedores_duplicados_evidence_type(self):
        record = create_intake_record(
            tenant_id="tenant_01",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        types = [e.evidence_type for e in record.evidence_requests]
        assert "excel_proveedores" in types

    def test_proveedores_duplicados_enables_classification(self):
        record = create_intake_record(
            tenant_id="tenant_01",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        ev = next(
            e for e in record.evidence_requests
            if e.evidence_type == "excel_proveedores"
        )
        assert ev.enables_classification == "supplier_duplicate_check"

    def test_proveedores_duplicados_source_tank(self):
        record = create_intake_record(
            tenant_id="tenant_01",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        ev = next(
            e for e in record.evidence_requests
            if e.evidence_type == "excel_proveedores"
        )
        assert ev.source_tank == "SMARTPYME_EVIDENCE_AND_FORMULA_TANK"


# ---------------------------------------------------------------------------
# Caso margen / costo
# ---------------------------------------------------------------------------
class TestMarginIntake:
    def test_margen_con_excel_crea_evidence_request(self):
        record = create_intake_record(
            tenant_id="tenant_02",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )
        types = [e.evidence_type for e in record.evidence_requests]
        assert "excel_ventas_costos" in types

    def test_margen_evidence_required_fields(self):
        record = create_intake_record(
            tenant_id="tenant_02",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )
        ev = next(
            e for e in record.evidence_requests
            if e.evidence_type == "excel_ventas_costos"
        )
        assert "producto" in ev.required_fields


# ---------------------------------------------------------------------------
# Selector-only no se vuelve READY_FOR_ANALYSIS
# ---------------------------------------------------------------------------
class TestSelectorOnlyIntake:
    def test_selector_only_no_es_ready_for_analysis(self):
        sel = StructuredSelectors(
            sales_channel="Mercado Libre",
            stock_mode="Informal",
            tools_used="Excel",
        )
        record = create_intake_record(
            tenant_id="tenant_03",
            raw_text="quiero revisar mi negocio",
            structured_selectors=sel,
        )
        assert record.intake_state != INTAKE_READY_FOR_ANALYSIS

    def test_selector_only_no_tiene_evidence_requests(self):
        sel = StructuredSelectors(sales_channel="Local")
        record = create_intake_record(
            tenant_id="tenant_03b",
            raw_text="hola",
            structured_selectors=sel,
        )
        assert len(record.evidence_requests) == 0


# ---------------------------------------------------------------------------
# BLOCKED_INSUFFICIENT_CONTEXT
# ---------------------------------------------------------------------------
class TestBlockedIntake:
    def test_texto_muy_corto_bloquea(self):
        # 2 chars normalizados → STATUS_BLOCKED_INSUFFICIENT_CONTEXT
        record = create_intake_record(tenant_id="t04", raw_text="hi")
        assert record.intake_state == INTAKE_BLOCKED

    def test_texto_sin_senal_clara_no_es_ready(self):
        record = create_intake_record(tenant_id="t04b", raw_text="necesito ayuda")
        assert record.intake_state in ALLOWED_INTAKE_STATES
        assert record.intake_state != INTAKE_READY_FOR_ANALYSIS


# ---------------------------------------------------------------------------
# Serialización JSON
# ---------------------------------------------------------------------------
class TestSerialization:
    def test_to_dict_es_json_serializable(self):
        record = create_intake_record(
            tenant_id="tenant_05",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        d = record.to_dict()
        # Debe serializar sin custom encoder
        s = json.dumps(d, ensure_ascii=False)
        assert isinstance(s, str)
        parsed = json.loads(s)
        assert parsed["tenant_id"] == "tenant_05"

    def test_to_dict_contiene_todos_los_campos(self):
        record = create_intake_record(
            tenant_id="tenant_06",
            raw_text="No me cierra la plata",
        )
        d = record.to_dict()
        expected_keys = {
            "intake_id",
            "tenant_id",
            "raw_input",
            "structured_selectors",
            "interrogation_result",
            "tank_selection_result",
            "evidence_requests",
            "intake_state",
            "suggested_next_state",
            "warnings",
            "audit_notes",
            "created_at",
            "hypotheses",
        }
        assert set(d.keys()) == expected_keys

    def test_evidence_request_to_dict(self):
        record = create_intake_record(
            tenant_id="tenant_07",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        assert len(record.evidence_requests) > 0
        ev = record.evidence_requests[0]
        ev_dict = ev.to_dict()
        assert "request_id" in ev_dict
        assert "evidence_type" in ev_dict
        assert "status" in ev_dict
        assert ev_dict["status"] == EVIDENCE_STATUS_REQUESTED

    def test_to_dict_serializa_hypotheses(self):
        record = create_intake_record(
            tenant_id="tenant_07b",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )
        hypotheses = record.to_dict()["hypotheses"]
        assert hypotheses
        assert hypotheses[0]["intake_id"] == record.intake_id


# ---------------------------------------------------------------------------
# No se inventan clasificaciones no soportadas
# ---------------------------------------------------------------------------
class TestNoUnsupportedClassification:
    def test_solo_clasificaciones_reales(self):
        record = create_intake_record(
            tenant_id="tenant_08",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        suggested = record.tank_selection_result.get("suggested_classifications", [])
        allowed = {"excel_diagnostic", "supplier_duplicate_check"}
        for cls in suggested:
            assert cls in allowed, f"Clasificación no soportada: {cls}"

    def test_evidence_requests_solo_runtime_compatible(self):
        record = create_intake_record(
            tenant_id="tenant_09",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )
        for ev in record.evidence_requests:
            if ev.enables_classification:
                assert ev.enables_classification in {
                    "excel_diagnostic",
                    "supplier_duplicate_check",
                }


# ---------------------------------------------------------------------------
# IntakeRecord integridad
# ---------------------------------------------------------------------------
class TestIntakeRecordIntegrity:
    def test_intake_id_unico(self):
        r1 = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        r2 = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        assert r1.intake_id != r2.intake_id

    def test_intake_id_prefix(self):
        r = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        assert r.intake_id.startswith("intake_")

    def test_evidence_request_id_prefix(self):
        r = create_intake_record(
            tenant_id="t1",
            raw_text="Tengo proveedores duplicados y CUIT mezclados",
        )
        for ev in r.evidence_requests:
            assert ev.request_id.startswith(r.intake_id + "_ev_")

    def test_created_at_presente(self):
        r = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        assert r.created_at
        assert "T" in r.created_at  # ISO format

    def test_audit_notes_contienen_info(self):
        r = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        assert len(r.audit_notes) > 0
        audit_text = " ".join(r.audit_notes)
        assert "intake_id" in audit_text
        assert "tenant_id" in audit_text

    def test_interrogation_result_dict(self):
        r = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        assert isinstance(r.interrogation_result, dict)
        assert "status" in r.interrogation_result
        assert "candidate_symptoms" in r.interrogation_result

    def test_tank_selection_result_dict(self):
        r = create_intake_record(tenant_id="t1", raw_text="Tengo proveedores duplicados")
        assert isinstance(r.tank_selection_result, dict)
        assert "suggested_next_state" in r.tank_selection_result
        assert "selected_tanks" in r.tank_selection_result

    def test_hypothesis_uses_formal_intake_id(self):
        r = create_intake_record(
            tenant_id="t1",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )
        assert r.hypotheses
        assert all(h.intake_id == r.intake_id for h in r.hypotheses)

    def test_evidence_requests_link_to_hypothesis(self):
        r = create_intake_record(
            tenant_id="t1",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )
        assert r.hypotheses
        assert r.evidence_requests
        assert all(
            ev.hypothesis_id == r.hypotheses[0].hypothesis_id
            for ev in r.evidence_requests
        )


# ---------------------------------------------------------------------------
# Descuadre dinero -> INTERROGATED (necesita desambiguación)
# ---------------------------------------------------------------------------
class TestDescuadreIntake:
    def test_descuadre_dinero_es_interrogated(self):
        record = create_intake_record(
            tenant_id="tenant_10",
            raw_text="No me cierra la plata",
        )
        assert record.intake_state == INTAKE_INTERROGATED

    def test_descuadre_suggested_next_state(self):
        record = create_intake_record(
            tenant_id="tenant_10b",
            raw_text="No me cierra la plata",
        )
        assert record.suggested_next_state == "ASK_CLARIFICATION"


# ---------------------------------------------------------------------------
# Estados permitidos
# ---------------------------------------------------------------------------
class TestAllowedStates:
    def test_intake_states_definidas(self):
        assert "RECEIVED" in ALLOWED_INTAKE_STATES
        assert "INTERROGATED" in ALLOWED_INTAKE_STATES
        assert "TANKS_SELECTED" in ALLOWED_INTAKE_STATES
        assert "NEEDS_EVIDENCE" in ALLOWED_INTAKE_STATES
        assert "READY_FOR_ANALYSIS" in ALLOWED_INTAKE_STATES
        assert "BLOCKED" in ALLOWED_INTAKE_STATES
        assert "UNSUPPORTED" in ALLOWED_INTAKE_STATES

    def test_evidence_statuses_definidos(self):
        assert "REQUESTED" in ALLOWED_EVIDENCE_STATUSES
        assert "RECEIVED" in ALLOWED_EVIDENCE_STATUSES
        assert "SATISFIED" in ALLOWED_EVIDENCE_STATUSES
        assert "WAIVED" in ALLOWED_EVIDENCE_STATUSES
        assert "BLOCKED" in ALLOWED_EVIDENCE_STATUSES

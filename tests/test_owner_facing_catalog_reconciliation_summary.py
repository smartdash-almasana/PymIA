from pathlib import Path
import pytest
from openpyxl import Workbook

from pymia.faithful_operator import (
    build_owner_facing_catalog_reconciliation_summary,
    handle_owner_message,
    receive_excel_and_build_candidate,
    OperatorState,
    OperatorPhase,
)

def test_pending_data_summary():
    reconciliation = [
        {
            "formula_id": "REN_001_margen_neto_real",
            "pathology_code": "REN_001",
            "status": "pending_data",
            "available_evidence": ["ventas"],
            "missing_evidence": ["impuestos_y_comisiones"],
            "matched_sources": ["sheet:ventas"],
            "required_evidence": ["ventas", "impuestos_y_comisiones"],
            "required_variables": ["ventas_total", "costos_total"],
            "next_audit_questions": [
                {
                    "question": "Falta evidencia para evaluar REN_001. ¿Podés compartir impuestos_y_comisiones?",
                    "requires_data": ["impuestos_y_comisiones"],
                    "priority": "high"
                }
            ]
        }
    ]
    
    summary = build_owner_facing_catalog_reconciliation_summary(reconciliation)
    
    # 1. Says missing evidence, doesn't diagnose
    assert "Falta evidencia" in summary or "falta evidencia" in summary
    assert "Margen Invisible" in summary
    assert "REN_001" not in summary
    assert "REN_001_margen_neto_real" not in summary
    # 5. No variables técnicas crudas tipo impuestos_y_comisiones
    assert "impuestos_y_comisiones" not in summary
    assert "impuestos y comisiones" in summary
    # 6. Uses humanized question
    assert "Falta evidencia para evaluar Margen Invisible. ¿Podés compartir impuestos y comisiones?" in summary
    # Check limit disclaimer
    assert "Límite: Este reporte es una síntesis" in summary
    assert "No representa un diagnóstico" in summary

def test_candidate_summary():
    reconciliation = [
        {
            "formula_id": "LIQ_001_vendido_cobrado",
            "pathology_code": "LIQ_001",
            "status": "candidate",
            "available_evidence": [],
            "missing_evidence": ["cobranzas_del_periodo"],
            "matched_sources": [],
            "required_evidence": ["cobranzas_del_periodo"],
            "required_variables": [],
            "next_audit_questions": [
                {
                    "question": "Falta evidencia para evaluar LIQ_001. ¿Podés compartir cobranzas_del_periodo?",
                    "requires_data": ["cobranzas_del_periodo"],
                    "priority": "medium"
                }
            ]
        }
    ]
    
    summary = build_owner_facing_catalog_reconciliation_summary(reconciliation)
    
    # 2. Mantener hipótesis sin cálculo
    assert "hipótesis posible, todavía no calculable" in summary
    assert "Descalce de Ventas y Cobranzas" in summary
    assert "LIQ_001" not in summary
    assert "cobranzas_del_periodo" not in summary
    assert "cobranzas del periodo" in summary
    assert "Falta evidencia para evaluar Descalce de Ventas y Cobranzas. ¿Podés compartir cobranzas del periodo?" in summary

def test_calculable_summary():
    reconciliation = [
        {
            "formula_id": "REN_001_margen_neto_real",
            "pathology_code": "REN_001",
            "status": "calculable",
            "available_evidence": ["ventas", "costos"],
            "missing_evidence": [],
            "matched_sources": ["sheet:ventas", "sheet:compras"],
            "required_evidence": ["ventas", "costos"],
            "required_variables": [],
            "next_audit_questions": []
        }
    ]
    
    summary = build_owner_facing_catalog_reconciliation_summary(reconciliation)
    
    # 3. Exige confirmación del dueño
    assert "requiere confirmación del dueño" in summary
    assert "Confirmás que los valores calculados son correctos" in summary

def test_limits_to_three_entries():
    # 7. La salida limita a 3 entradas visibles
    reconciliation = [
        {"formula_id": "F1", "pathology_code": "REN_001", "status": "blocked", "missing_evidence": ["m1"]},
        {"formula_id": "F2", "pathology_code": "LIQ_001", "status": "pending_data", "missing_evidence": ["m2"]},
        {"formula_id": "F3", "pathology_code": "INV_001", "status": "candidate", "missing_evidence": ["m3"]},
        {"formula_id": "F4", "pathology_code": "REN_002", "status": "calculable", "missing_evidence": ["m4"]},
    ]
    
    summary = build_owner_facing_catalog_reconciliation_summary(reconciliation)
    lines = summary.split("\n")
    themes = [line for line in lines if line.startswith("- ")]
    assert len(themes) == 3
    # Check that the highest priority statuses are shown: blocked, pending_data, candidate
    assert "Margen Invisible" in summary
    assert "Descalce de Ventas y Cobranzas" in summary
    assert "Stock Crítico" in summary
    assert "Costo de Reposición Ignorado" not in summary

def test_integration_and_c1_compatibility(tmp_path: Path):
    excel = tmp_path / "integration_test.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["fecha", "producto", "ventas", "costo"])
    worksheet.append(["2026-06-01", "A", 100, 60])
    workbook.save(excel)
    
    state = handle_owner_message("tengo un problema con el margen")
    new_state = receive_excel_and_build_candidate(state, excel, storage_dir=tmp_path / "storage")
    
    # 8. receive_excel_and_build_candidate(...) integra el resumen en OperatorState.next_question
    assert new_state.current_state == OperatorPhase.OWNER_CONFIRMATION_PENDING
    assert "Estado general:" in new_state.next_question
    assert "Temas a revisar:" in new_state.next_question
    assert "Límite: Este reporte es una síntesis" in new_state.next_question
    
    # 9. C1 sigue protegido: no romper expectativas de candidate_response
    assert "Reconciliación de catálogos:" in new_state.candidate_response
    assert "fórmulas" in new_state.candidate_response

def test_static_check_no_cafeteria():
    # 10. Test estático: no hay imports ni referencias a cafeteria_margin_focus ni margin_evidence_request
    operator_path = Path(__file__).parent.parent / "pymia" / "faithful_operator.py"
    content = operator_path.read_text(encoding="utf-8")
    assert "cafeteria_margin_focus" not in content
    assert "margin_evidence_request" not in content

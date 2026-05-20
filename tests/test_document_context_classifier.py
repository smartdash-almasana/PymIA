from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure repo root is on path for importing tools.document_context_classifier
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.document_context_classifier import (
    DocumentContextClassifier,
    DocumentContextInput,
)


def test_classifier_tabular_sales_match() -> None:
    payload = DocumentContextInput(
        file_name="ventas_mayo.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        extension=".xlsx",
        entropy_level=0.1,
        sheet_names=["Mayo_2026", "Ventas_Totales"],
        column_headers=["fecha", "producto", "cantidad", "precio_unitario", "total"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.document_context == "ventas"
    assert result.ingestion_route == "INTERNAL_FACT"
    assert result.confidence == "high"
    assert result.decision_code == "SUCCESS"
    assert any("ventas" in r for r in result.reasons)
    assert result.required_followup is None
    assert result.evidence_candidate_type == "ventas_evidence_candidate"


def test_classifier_pdf_forces_bem_ai() -> None:
    # A PDF called "ventas_mayo.pdf" must go to BEM_AI
    payload = DocumentContextInput(
        file_name="ventas_mayo.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        entropy_level=0.1,
        sheet_names=[],
        column_headers=[],
        extracted_text_preview="Ventas de Mayo total",
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.ingestion_route == "BEM_AI"
    assert result.document_context == "ventas" or result.document_context == "desconocido"
    assert result.decision_code == "SUCCESS"
    assert any("PDF" in r or "visual" in r for r in result.reasons)


def test_classifier_image_forces_bem_ai() -> None:
    # An image (png) must go to BEM_AI
    payload = DocumentContextInput(
        file_name="captura_caja.png",
        mime_type="image/png",
        extension=".png",
        entropy_level=0.1,
        sheet_names=[],
        column_headers=[],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.ingestion_route == "BEM_AI"
    assert result.decision_code == "DESCONOCIDO_LOW"
    assert any("visual" in r or "PDF" in r for r in result.reasons)


def test_classifier_low_confidence_triggers_followup() -> None:
    # Low confidence / unknown column names triggers followup
    payload = DocumentContextInput(
        file_name="datos_mezclados.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        extension=".xlsx",
        entropy_level=0.2,
        sheet_names=["Hoja1"],
        column_headers=["columna_a", "columna_b", "columna_c"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.document_context == "desconocido"
    assert result.confidence == "low"
    assert result.decision_code == "NO_KEYWORDS_DETECTED"
    assert result.ingestion_route == "BEM_AI"
    assert result.required_followup is not None
    assert "datos_mezclados.xlsx" in result.required_followup


def test_test_classifier_colision_triggers_followup_warning() -> None:
    # Coexistence of ventas and stock strong keywords causes low confidence and followup
    payload = DocumentContextInput(
        file_name="stock_y_ventas.xlsx",
        extension=".xlsx",
        entropy_level=0.2,
        sheet_names=["Ventas_Stock"],
        column_headers=["vendedor", "clientes", "sku", "deposito", "total"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.confidence == "low"
    assert result.decision_code == "CONTEXT_COLLISION"
    assert result.required_followup is not None
    assert "mezcla" in result.required_followup or "priorizar" in result.required_followup


def test_classifier_stock_does_not_become_sales() -> None:
    # A stock spreadsheet with column "total" must remain "stock" and not "ventas"
    payload = DocumentContextInput(
        file_name="inventario_general.xlsx",
        extension=".xlsx",
        entropy_level=0.1,
        sheet_names=["Stock_Mayo"],
        column_headers=["sku", "stock", "inventario", "deposito", "total"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.document_context == "stock"
    assert result.ingestion_route == "INTERNAL_FACT"
    assert result.confidence == "high"
    assert result.decision_code == "SUCCESS"


def test_classifier_fiscal_is_not_internal_audit_fact() -> None:
    # Fiscal/Impositivo must route to BEM_AI even with high confidence
    payload = DocumentContextInput(
        file_name="declaracion_iva.xlsx",
        extension=".xlsx",
        entropy_level=0.1,
        sheet_names=["AFIP_IVA"],
        column_headers=["impuesto", "iva_compras", "iva_ventas", "retencion", "percepcion"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.document_context == "fiscal/impositivo"
    assert result.ingestion_route == "BEM_AI"
    assert result.decision_code == "ADMINISTRATIVE_BYPASS"
    assert any("administrativa" in r or "desviado" in r for r in result.reasons)


def test_test_classifier_laboral_is_not_internal_audit_fact() -> None:
    # Laboral must route to BEM_AI even with high confidence
    payload = DocumentContextInput(
        file_name="recibos_haberes.xlsx",
        extension=".xlsx",
        entropy_level=0.1,
        sheet_names=["Haberes_Personal"],
        column_headers=["sueldos", "recibo_sueldo", "haberes", "empleado", "cargas_sociales"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.document_context == "laboral"
    assert result.ingestion_route == "BEM_AI"
    assert result.decision_code == "ADMINISTRATIVE_BYPASS"


def test_classifier_text_routes_narrative() -> None:
    # Plain text / narrative claims route directly to NARRATIVE
    payload = DocumentContextInput(
        file_name="",
        mime_type=None,
        extension=None,
        source_type="narrative",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.ingestion_route == "NARRATIVE"
    assert result.document_context == "desconocido"
    assert result.decision_code == "SUCCESS"
    assert result.evidence_candidate_type == "narrative_claim_candidate"


def test_classifier_never_validates_evidence() -> None:
    # is_validated_evidence must ALWAYS be False
    payload = DocumentContextInput(
        file_name="ventas_mayo.xlsx",
        extension=".xlsx",
        entropy_level=0.1,
        sheet_names=["Mayo_2026", "Ventas_Totales"],
        column_headers=["fecha", "producto", "cantidad", "precio_unitario", "total"],
        source_type="file_upload",
    )
    result = DocumentContextClassifier.classify(payload)
    
    assert result.is_validated_evidence is False
    assert result.decision_code == "SUCCESS"

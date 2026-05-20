from __future__ import annotations

import base64
import re
import unicodedata
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

DocumentContext = Literal[
    "ventas", "stock", "caja", "compras", "cobranzas",
    "facturación", "fiscal/impositivo", "laboral", "producción", "desconocido"
]

IngestionRoute = Literal["BEM_AI", "INTERNAL_FACT", "NARRATIVE"]

ClassificationConfidence = Literal["high", "medium", "low"]


class DocumentContextInput(BaseModel):
    file_name: str
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    entropy_level: float = 0.5
    sheet_names: List[str] = Field(default_factory=list)
    column_headers: List[str] = Field(default_factory=list)
    extracted_text_preview: Optional[str] = None
    source_type: str = "file_upload"


class DocumentContextClassification(BaseModel):
    document_context: DocumentContext
    ingestion_route: IngestionRoute
    confidence: ClassificationConfidence
    reasons: List[str] = Field(default_factory=list)
    required_followup: Optional[str] = None
    evidence_candidate_type: str
    is_validated_evidence: bool = False


def _normalize_string(text: str) -> str:
    if not text:
        return ""
    # Preserve 'ñ' and 'Ñ' from being stripped by NFKD normalization
    val = text.replace("ñ", "###n###").replace("Ñ", "###N###")
    nfkd_form = unicodedata.normalize("NFKD", val.lower())
    val_clean = "".join(c for c in nfkd_form if not unicodedata.combining(c))
    val_clean = val_clean.replace("###n###", "ñ").replace("###N###", "ñ")
    return val_clean.strip()


CONTEXT_KEYWORDS: Dict[DocumentContext, Dict[str, set[str]]] = {
    "ventas": {
        "strong": {"ventas", "venta", "facturacion", "facturas", "precio_unitario", "cliente", "clientes", "comprobantes", "vendedor"},
        "weak": {"total", "cantidad", "importe", "monto", "fecha", "subtotal", "descuento"}
    },
    "stock": {
        "strong": {"stock", "inventario", "deposito", "sku", "codigo_producto", "unidades", "existencias", "stock_minimo", "reposicion"},
        "weak": {"cantidad", "detalle", "total", "precio"}
    },
    "caja": {
        "strong": {"caja", "banco", "saldo", "egreso", "ingreso", "conciliacion", "mercado_pago", "bancario", "bancos", "extracto", "caja_chica", "tarjeta"},
        "weak": {"fecha", "monto", "importe", "total"}
    },
    "compras": {
        "strong": {"compras", "compra", "proveedor", "proveedores", "factura_compra", "costo_mercaderia", "remito_compra"},
        "weak": {"fecha", "cantidad", "precio", "total", "importe"}
    },
    "cobranzas": {
        "strong": {"cobranza", "cobranzas", "cobros", "cobros_pendientes", "cuenta_corriente", "ctacte", "saldo_pendiente", "deuda_cliente"},
        "weak": {"monto", "importe", "total", "cliente", "fecha"}
    },
    "facturación": {
        "strong": {"facturacion", "emision", "afip", "comprobante_fiscal", "factura_electronica", "cae", "tipo_comprobante"},
        "weak": {"neto", "iva", "total", "fecha", "monto"}
    },
    "fiscal/impositivo": {
        "strong": {"impuesto", "impuestos", "afip", "iva", "declaracion", "iva_compras", "iva_ventas", "declaracion_jurada", "retencion", "percepcion", "ingresos_brutos", "iibb", "ganancias"},
        "weak": {"total", "periodo", "mes", "monto"}
    },
    "laboral": {
        "strong": {"recibo_sueldo", "sueldos", "haberes", "empleado", "empleados", "nomina", "personal", "aportes", "cargas_sociales", "paritaria", "jornada"},
        "weak": {"total", "mes", "periodo", "monto"}
    },
    "producción": {
        "strong": {"produccion", "fabricacion", "formula", "receta", "materia_prima", "insumos_produccion", "merma", "desperdicio", "orden_trabajo", "lote_produccion"},
        "weak": {"cantidad", "total", "fecha"}
    }
}


class DocumentContextClassifier:
    @staticmethod
    def classify(payload: DocumentContextInput) -> DocumentContextClassification:
        reasons = []
        confidence: ClassificationConfidence = "low"
        document_context: DocumentContext = "desconocido"
        ingestion_route: IngestionRoute = "BEM_AI"
        required_followup = None
        
        # 1. Handle NARRATIVE route
        if payload.source_type == "narrative":
            reasons.append("Origen narrativo plano por entrada de chat.")
            return DocumentContextClassification(
                document_context="desconocido",
                ingestion_route="NARRATIVE",
                confidence="high",
                reasons=reasons,
                required_followup=None,
                evidence_candidate_type="narrative_claim_candidate",
                is_validated_evidence=False
            )
            
        # 2. Extract and check extension / mime-type
        file_name = payload.file_name or ""
        ext = payload.extension or (Path(file_name).suffix.lower() if file_name else "")
        if ext and not ext.startswith("."):
            ext = f".{ext}"
            
        mime = (payload.mime_type or "").lower()
        
        is_pdf_or_image = False
        if ext in {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}:
            is_pdf_or_image = True
            reasons.append(f"Archivo visual o PDF detectado por extensión: '{ext}'.")
        elif "pdf" in mime or "image" in mime:
            is_pdf_or_image = True
            reasons.append(f"Archivo visual o PDF detectado por tipo MIME: '{mime}'.")
            
        # 3. Text Tokenization and Scoring
        norm_file_name = _normalize_string(Path(file_name).stem if file_name else "")
        norm_sheets = [_normalize_string(s) for s in payload.sheet_names]
        
        # Tokenize headers deeply (as whole headers and single words)
        header_words = []
        for h in payload.column_headers:
            h_norm = _normalize_string(h)
            header_words.append(h_norm)
            header_words.extend(h_norm.replace("_", " ").replace("-", " ").split())
        header_words = list(set(header_words))
        
        preview_text = payload.extracted_text_preview or ""
        norm_preview = _normalize_string(preview_text[:1000])
        
        # Calculate scores
        scores = {ctx: 0.0 for ctx in CONTEXT_KEYWORDS.keys()}
        
        for ctx, kw_dict in CONTEXT_KEYWORDS.items():
            strong = kw_dict["strong"]
            weak = kw_dict["weak"]
            
            # Check sheet names
            for sheet in norm_sheets:
                if any(w in sheet for w in strong):
                    scores[ctx] += 5.0
                elif any(w in sheet for w in weak):
                    scores[ctx] += 1.0
                    
            # Check column headers
            for hw in header_words:
                if hw in strong:
                    scores[ctx] += 3.0
                elif hw in weak:
                    scores[ctx] += 1.0
                    
            # Check file name
            if any(w in norm_file_name for w in strong):
                scores[ctx] += 2.0
            elif any(w in norm_file_name for w in weak):
                scores[ctx] += 0.5
                
            # Check text preview
            if norm_preview:
                for w in strong:
                    if w in norm_preview:
                        scores[ctx] += 1.0
                        
        # Find best class
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_ctx, best_score = sorted_scores[0]
        second_ctx, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0.0)
        
        # Reasons logging
        if best_score > 0:
            document_context = best_ctx
            reasons.append(f"Clasificado en dominio '{best_ctx}' con puntaje de afinidad de {best_score}.")
            if second_score > 0 and (best_score - second_score) < 2.0:
                reasons.append(f"Conflicto de afinidad cercano con dominio '{second_ctx}' ({second_score}).")
        else:
            document_context = "desconocido"
            reasons.append("No se detectaron palabras clave de dominio contable conocidas.")
            
        # Determine confidence
        if document_context == "desconocido":
            confidence = "low"
        elif payload.entropy_level > 0.3:
            confidence = "low"
            reasons.append(f"Nivel de entropía elevado ({payload.entropy_level}) reduce la certidumbre.")
        elif second_score > 0 and (best_score - second_score) < 1.5:
            confidence = "low"
            reasons.append(f"Ambigüedad detectada por colisión de contextos: '{best_ctx}' vs '{second_ctx}'.")
        elif best_score >= 5.0:
            confidence = "high"
        elif best_score >= 3.0:
            confidence = "medium"
        else:
            confidence = "low"
            
        # Determine IngestionRoute
        if is_pdf_or_image:
            ingestion_route = "BEM_AI"
            reasons.append("Los archivos visuales o PDFs se derivan obligatoriamente a BEM_AI.")
        elif document_context in {"fiscal/impositivo", "laboral", "producción"}:
            ingestion_route = "BEM_AI"
            reasons.append(f"El dominio '{document_context}' es de índole administrativa no ejecutable síncronamente en local; desviado a BEM_AI.")
        elif document_context == "desconocido" or confidence == "low":
            ingestion_route = "BEM_AI"
            reasons.append("Clasificación de baja confianza o desconocida obliga a desviar por seguridad a BEM_AI.")
        else:
            if ext in {".xlsx", ".csv"} and payload.entropy_level <= 0.3:
                ingestion_route = "INTERNAL_FACT"
                reasons.append("Planilla limpia de baja entropía con contexto reconocido califica para INTERNAL_FACT.")
            else:
                ingestion_route = "BEM_AI"
                reasons.append("Extensión o estructura inadecuada para el procesamiento local directo.")
                
        # Handle required followup
        if confidence == "low" or document_context == "desconocido":
            if second_score > 0 and (best_score - second_score) < 1.5:
                required_followup = (
                    f"Recibí el archivo '{file_name}', pero detecto una mezcla de información entre {best_ctx} y {second_ctx}. "
                    "¿Podés confirmarme qué tema querés priorizar?"
                )
            else:
                required_followup = (
                    f"Recibí el archivo '{file_name}', pero no puedo determinar con seguridad si corresponde a ventas, stock, caja u otro contexto. "
                    "¿Podés confirmarme qué información contiene?"
                )
                
        evidence_candidate_type = f"{document_context}_evidence_candidate"
        
        return DocumentContextClassification(
            document_context=document_context,
            ingestion_route=ingestion_route,
            confidence=confidence,
            reasons=reasons,
            required_followup=required_followup,
            evidence_candidate_type=evidence_candidate_type,
            is_validated_evidence=False
        )

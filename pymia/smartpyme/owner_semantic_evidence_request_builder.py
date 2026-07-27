from __future__ import annotations

import hashlib
import json
from typing import Any

from pymia.contracts.owner_semantic_evidence_requests import OwnerSemanticEvidenceRequest


PRICE_VARIABILITY_TERMS = (
    "subio",
    "subió",
    "aumento",
    "aumentó",
    "cambio",
    "cambió",
    "cambiando",
    "tela",
    "insumo",
    "insumos",
    "precio",
    "precios",
)

STOCK_ESTIMATE_TERMS = (
    "ojo",
    "aproximado",
    "aprox",
    "estimado",
    "estimo",
    "memoria",
    "no prolijo",
    "sin sistema",
)

COLLECTION_DELAY_TERMS = (
    "pagan tarde",
    "atrasan",
    "se atrasan",
    "30",
    "45",
    "60",
    "pendiente",
    "cobro",
    "cobranza",
)


_REQUEST_TEMPLATES: dict[str, dict[str, Any]] = {
    "own_price": {
        "semantic_signal": "PRICE_VARIABILITY_DUE_TO_INPUT_COST",
        "interpreted_meaning": "El dueño aporta contexto de variación de precios, pero falta precio estructurado por producto.",
        "refined_request_text": (
            "Para calcular margen necesito precios de venta por producto/SKU de la última semana "
            "y, si cambiaron durante el período, desde qué fecha rigió cada precio."
        ),
        "required_fields": ["producto/SKU", "precio de venta", "fecha o semana de vigencia"],
        "accepted_formats": ["Excel", "lista de precios", "texto estructurado"],
        "confidence": 0.82,
    },
    "average_stock": {
        "semantic_signal": "STOCK_ESTIMATED_OR_INFORMAL",
        "interpreted_meaning": "El dueño indica que el stock puede estar disponible sólo como estimación o registro informal.",
        "refined_request_text": (
            "Para revisar stock necesito stock inicial y stock final por producto del período analizado. "
            "Si no lo tenés exacto, pasame una estimación y marcala como estimada."
        ),
        "required_fields": ["producto/SKU", "stock inicial", "stock final", "período", "si es estimado o exacto"],
        "accepted_formats": ["Excel", "foto de conteo", "texto estructurado"],
        "confidence": 0.76,
    },
    "dso": {
        "semantic_signal": "COLLECTION_DELAY_CONTEXT",
        "interpreted_meaning": "El dueño aporta contexto de cobranza irregular, pero faltan fechas o plazos de cobro.",
        "refined_request_text": (
            "Para revisar cobranzas necesito una lista con cliente, importe, fecha de factura o venta "
            "y fecha real de cobro. Si no tenés fecha exacta, indicá si cobró a 30, 45, 60 días o sigue pendiente."
        ),
        "required_fields": ["cliente", "importe", "fecha de factura o venta", "fecha real de cobro o plazo", "estado pendiente si aplica"],
        "accepted_formats": ["Excel", "exportación de ventas", "texto estructurado"],
        "confidence": 0.78,
    },
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _build_request_id(*, missing_key: str, owner_answer_text: str, source_ref: str) -> str:
    payload = {
        "missing_key": missing_key,
        "owner_answer_text": owner_answer_text,
        "source_ref": source_ref,
    }
    digest = hashlib.sha1(
        json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return f"owner_semantic_evidence_request_{digest[:12]}"


def build_owner_semantic_evidence_request(
    *,
    missing_key: str,
    owner_answer_text: str,
    source_ref: str,
    metadata: dict[str, Any] | None = None,
) -> OwnerSemanticEvidenceRequest:
    """Construye un pedido accionable desde narrativa del dueño y faltante estructural.

    No resuelve evidencia estructural ni produce findings.
    """

    missing_key_text = _normalize_text(missing_key)
    owner_answer_text_normalized = _normalize_text(owner_answer_text)
    source_ref_text = _normalize_text(source_ref)

    if missing_key_text not in _REQUEST_TEMPLATES:
        raise ValueError("unsupported missing_key for semantic evidence request")

    template = dict(_REQUEST_TEMPLATES[missing_key_text])

    if missing_key_text == "own_price" and not _contains_any(owner_answer_text_normalized, PRICE_VARIABILITY_TERMS):
        template["semantic_signal"] = "PRICE_REQUIRED_FOR_MARGIN"
        template["confidence"] = 0.64
    elif missing_key_text == "average_stock" and not _contains_any(owner_answer_text_normalized, STOCK_ESTIMATE_TERMS):
        template["semantic_signal"] = "STOCK_REQUIRED_FOR_ROTATION"
        template["confidence"] = 0.64
    elif missing_key_text == "dso" and not _contains_any(owner_answer_text_normalized, COLLECTION_DELAY_TERMS):
        template["semantic_signal"] = "COLLECTION_DATES_REQUIRED"
        template["confidence"] = 0.64

    return OwnerSemanticEvidenceRequest(
        request_id=_build_request_id(
            missing_key=missing_key_text,
            owner_answer_text=owner_answer_text_normalized,
            source_ref=source_ref_text,
        ),
        missing_key=missing_key_text,
        missing_input_type="STRUCTURAL_INPUT",
        owner_answer_text=owner_answer_text_normalized,
        semantic_signal=template["semantic_signal"],
        interpreted_meaning=template["interpreted_meaning"],
        refined_request_text=template["refined_request_text"],
        required_fields=template["required_fields"],
        accepted_formats=template["accepted_formats"],
        does_resolve_structural_input=False,
        confidence=template["confidence"],
        source_ref=source_ref_text,
        metadata=dict(metadata or {}),
    )

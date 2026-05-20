from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymia.audit_result.models import OperationalAuditResult, PathologyRoutingSummary


@dataclass
class RoutingDecision:
    pathology_code: str | None
    thread_id: str | None
    missing_evidence: list[str]
    next_question: str
    reply_text: str
    options: list[str]


_INTENT_KEYWORDS = {
    "liq": ("caja", "liquidez", "cobranza", "cobro", "cobranzas", "cuenta corriente"),
    "ren": ("margen", "ganancia", "rentabilidad", "precio", "precios"),
    "inv": ("stock", "inventario", "reposicion", "reposición", "sku"),
}


def _guard_no_raw_payload(audit: OperationalAuditResult) -> None:
    payload = audit.model_dump(mode="json", by_alias=True)
    forbidden = {"tables", "raw_tables", "normalized_tables", "kernel_output"}
    for key in forbidden:
        if key in payload:
            raise ValueError(f"Forbidden raw field in OperationalAuditResult payload: {key}")


def _family_match(message: str) -> str | None:
    normalized = message.lower()
    for family, keywords in _INTENT_KEYWORDS.items():
        if any(k in normalized for k in keywords):
            return family
    return None


def _choose(routes: list[PathologyRoutingSummary], family: str) -> list[PathologyRoutingSummary]:
    prefix = {"liq": "LIQ_", "ren": "REN_", "inv": "INV_"}[family]
    return [route for route in routes if route.pathology_code.startswith(prefix)]


def _status_rank(status: str) -> int:
    order = {"blocked": 0, "pending_data": 1, "candidate": 2, "calculable": 3, "not_applicable": 4}
    return order.get(status, 9)


def route_operational_audit_message(message_text: str, audit_result: OperationalAuditResult) -> RoutingDecision:
    _guard_no_raw_payload(audit_result)

    routes = sorted(
        audit_result.pathology_routing_summary,
        key=lambda item: (_status_rank(item.status), item.pathology_code),
    )
    if not routes:
        return RoutingDecision(
            pathology_code=None,
            thread_id=None,
            missing_evidence=[],
            next_question="No hay rutas auditables abiertas en este momento.",
            reply_text="No encuentro auditorías abiertas para profundizar ahora.",
            options=[],
        )

    # Explicit lookup by pathology code in message
    normalized_text = message_text.lower()
    for route in routes:
        if route.pathology_code.lower() in normalized_text:
            missing = route.missing_evidence
            reply = (
                f"Puedo abrir {route.pathology_code} ({route.status}). "
                f"Thread: {route.thread_id}."
            )
            if missing:
                reply += f" Me falta evidencia: {', '.join(missing)}."
            
            other_routes = [f"{r.pathology_code} ({r.status})" for r in routes if r.pathology_code != route.pathology_code]
            return RoutingDecision(
                pathology_code=route.pathology_code,
                thread_id=route.thread_id,
                missing_evidence=missing,
                next_question=route.next_question,
                reply_text=reply,
                options=other_routes[:3],
            )

    family = _family_match(message_text)
    if family is None:
        options = [f"{route.pathology_code} ({route.status})" for route in routes[:5]]
        return RoutingDecision(
            pathology_code=None,
            thread_id=None,
            missing_evidence=[],
            next_question="Elegí si querés profundizar liquidez, rentabilidad o inventario.",
            reply_text=(
                "Puedo auditar liquidez, rentabilidad o inventario. "
                "Decime cuál querés priorizar."
            ),
            options=options,
        )

    candidates = _choose(routes, family)
    if not candidates:
        options = [f"{route.pathology_code} ({route.status})" for route in routes[:5]]
        return RoutingDecision(
            pathology_code=None,
            thread_id=None,
            missing_evidence=[],
            next_question="No hay ruta de esa familia; elegí otra opción disponible.",
            reply_text="No tengo una ruta abierta para ese tema. Te muestro opciones disponibles.",
            options=options,
        )

    selected = sorted(candidates, key=lambda item: (_status_rank(item.status), item.pathology_code))[0]
    missing = selected.missing_evidence

    reply = (
        f"Puedo abrir {selected.pathology_code} ({selected.status}). "
        f"Thread: {selected.thread_id}."
    )
    if missing:
        reply += f" Me falta evidencia: {', '.join(missing)}."

    return RoutingDecision(
        pathology_code=selected.pathology_code,
        thread_id=selected.thread_id,
        missing_evidence=missing,
        next_question=selected.next_question,
        reply_text=reply,
        options=[f"{route.pathology_code} ({route.status})" for route in candidates[:3]],
    )

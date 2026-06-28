from __future__ import annotations

from typing import Final

from pymia.smartpyme.service_2_reconciliation_match_candidates_v1 import (
    build_reconciliation_match_candidates_v1,
)

AssistedReviewBlockV1 = dict[str, object]

BLOCK_REF: Final[str] = "S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1"
SERVICE_REF: Final[str] = "S2_ADMIN_OPERATIONS_V1"

STATUS_BY_SOURCE_STATUS: Final[dict[str, str]] = {
    "BLOCKED_BY_INVALID_INPUTS": "BLOCKED_BY_INVALID_INPUTS",
    "NEEDS_MORE_EVIDENCE": "NEEDS_MORE_EVIDENCE",
    "NO_CANDIDATES_FOUND": "NO_REVIEWABLE_CANDIDATES",
    "READY_FOR_HUMAN_REVIEW": "READY_FOR_ASSISTED_REVIEW",
    "PARTIAL_MATCHES_FOUND": "PARTIAL_REVIEW_READY",
}

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    "READY_FOR_ASSISTED_REVIEW",
    "NEEDS_MORE_EVIDENCE",
    "BLOCKED_BY_INVALID_INPUTS",
    "NO_REVIEWABLE_CANDIDATES",
    "PARTIAL_REVIEW_READY",
)

CAVEATS: Final[tuple[str, ...]] = (
    "No es conciliación definitiva.",
    "No certifica saldo bancario.",
    "No reemplaza revisión contable.",
    "No detecta fraude.",
    "No produce cierre contable ni fiscal.",
    "Requiere revisión humana.",
)

FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "banco conciliado",
    "conciliación cerrada",
    "saldo real confirmado",
    "auditoría",
    "certificación",
    "cierre contable",
    "cierre fiscal",
    "reemplazo del contador",
)


def build_reconciliation_assisted_review_block_v1(
    bank_movements: object,
    internal_movements: object,
    options: dict[str, object] | None = None,
) -> AssistedReviewBlockV1:
    source_result = build_reconciliation_match_candidates_v1(
        bank_movements,
        internal_movements,
        options=options,
    )
    source_status = str(source_result.get("status", "BLOCKED_BY_INVALID_INPUTS"))
    status = STATUS_BY_SOURCE_STATUS.get(source_status, "BLOCKED_BY_INVALID_INPUTS")
    review_summary = _build_review_summary(source_result)
    next_steps = _next_steps_for_status(status)
    exact_matches_summary = _section_summary(source_result, "matches_exactos")
    probable_matches_summary = _section_summary(source_result, "matches_probables")
    bank_pending_summary = _section_summary(source_result, "banco_sin_imputar")
    internal_pending_summary = _section_summary(source_result, "interno_sin_banco")
    amount_differences_summary = _section_summary(source_result, "diferencias_importe")
    date_differences_summary = _section_summary(source_result, "diferencias_fecha")
    missing_evidence_summary = _section_summary(source_result, "faltantes_evidencia")
    executive_summary = _build_executive_summary(status=status, review_summary=review_summary)

    return {
        "schema_version": "1.0",
        "service": SERVICE_REF,
        "block": BLOCK_REF,
        "status": status,
        "source_status": source_status,
        "requires_human_review": True,
        "audience": {
            "operator": True,
            "owner": True,
            "accountant": True,
        },
        "title": "Revisión asistida de conciliación",
        "executive_summary": executive_summary,
        "operator_brief": _operator_brief(status, review_summary),
        "owner_summary": _owner_summary(status, review_summary),
        "accountant_summary": _accountant_summary(status, review_summary),
        "review_summary": review_summary,
        "counts": dict(review_summary),
        "exact_matches_summary": exact_matches_summary,
        "probable_matches_summary": probable_matches_summary,
        "bank_pending_summary": bank_pending_summary,
        "internal_pending_summary": internal_pending_summary,
        "amount_differences_summary": amount_differences_summary,
        "date_differences_summary": date_differences_summary,
        "missing_evidence_summary": missing_evidence_summary,
        "sections": _build_sections(
            executive_summary=executive_summary,
            exact_matches_summary=exact_matches_summary,
            probable_matches_summary=probable_matches_summary,
            bank_pending_summary=bank_pending_summary,
            internal_pending_summary=internal_pending_summary,
            amount_differences_summary=amount_differences_summary,
            date_differences_summary=date_differences_summary,
            missing_evidence_summary=missing_evidence_summary,
            next_steps=next_steps,
            caveats=list(CAVEATS),
        ),
        "next_steps": next_steps,
        "caveats": list(CAVEATS),
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "markdown_ready": True,
        "io_performed": False,
        "files_created": [],
        "xlsx_created": False,
        "api_used": False,
        "llm_used": False,
        "source_result": source_result,
    }


def _build_review_summary(source_result: dict[str, object]) -> dict[str, int]:
    return {
        "matches_exactos": _count(source_result, "matches_exactos"),
        "matches_probables": _count(source_result, "matches_probables"),
        "banco_sin_imputar": _count(source_result, "banco_sin_imputar"),
        "interno_sin_banco": _count(source_result, "interno_sin_banco"),
        "diferencias_importe": _count(source_result, "diferencias_importe"),
        "diferencias_fecha": _count(source_result, "diferencias_fecha"),
        "faltantes_evidencia": _count(source_result, "faltantes_evidencia"),
    }


def _count(source_result: dict[str, object], key: str) -> int:
    value = source_result.get(key, [])
    if not isinstance(value, list):
        return 0
    return len(value)


def _section_summary(source_result: dict[str, object], key: str) -> dict[str, object]:
    value = source_result.get(key, [])
    items = value if isinstance(value, list) else []
    return {
        "count": len(items),
        "items": items,
    }


def _build_executive_summary(*, status: str, review_summary: dict[str, int]) -> str:
    return (
        "Revisión asistida preparada para revisión humana: "
        f"{review_summary['matches_exactos']} matches exactos, "
        f"{review_summary['matches_probables']} matches probables, "
        f"{review_summary['banco_sin_imputar']} movimientos bancarios sin imputar, "
        f"{review_summary['interno_sin_banco']} movimientos internos sin banco, "
        f"{review_summary['diferencias_importe']} diferencias de importe, "
        f"{review_summary['diferencias_fecha']} diferencias de fecha y "
        f"{review_summary['faltantes_evidencia']} faltantes de evidencia. "
        f"Estado de revisión: {status}. Requiere revisión humana."
    )


def _operator_brief(status: str, review_summary: dict[str, int]) -> str:
    return (
        f"Revisión asistida lista con estado {status}: "
        f"{review_summary['matches_exactos']} exactos, "
        f"{review_summary['matches_probables']} probables, "
        f"{review_summary['banco_sin_imputar']} bancarios pendientes, "
        f"{review_summary['interno_sin_banco']} internos pendientes."
    )


def _owner_summary(status: str, review_summary: dict[str, int]) -> str:
    return (
        "Se preparó una revisión asistida para mirar con responsable o contador: "
        f"{review_summary['matches_exactos']} coincidencias exactas, "
        f"{review_summary['matches_probables']} posibles coincidencias y "
        f"{review_summary['faltantes_evidencia']} faltantes de evidencia. "
        f"Estado: {status}."
    )


def _accountant_summary(status: str, review_summary: dict[str, int]) -> str:
    return (
        "Paquete preliminar para revisión contable asistida: "
        f"{review_summary['diferencias_importe']} diferencias de importe, "
        f"{review_summary['diferencias_fecha']} diferencias de fecha, "
        f"{review_summary['banco_sin_imputar']} movimientos bancarios sin imputar y "
        f"{review_summary['interno_sin_banco']} movimientos internos sin banco. "
        f"Estado: {status}."
    )


def _build_sections(
    *,
    executive_summary: str,
    exact_matches_summary: dict[str, object],
    probable_matches_summary: dict[str, object],
    bank_pending_summary: dict[str, object],
    internal_pending_summary: dict[str, object],
    amount_differences_summary: dict[str, object],
    date_differences_summary: dict[str, object],
    missing_evidence_summary: dict[str, object],
    next_steps: list[str],
    caveats: list[str],
) -> list[dict[str, object]]:
    return [
        _section("executive_summary", "Resumen ejecutivo", executive_summary),
        _section("exact_matches", "Matches exactos", exact_matches_summary),
        _section("probable_matches", "Matches probables", probable_matches_summary),
        _section("bank_pending", "Movimientos bancarios sin imputar", bank_pending_summary),
        _section("internal_pending", "Movimientos internos sin banco", internal_pending_summary),
        _section("amount_differences", "Diferencias de importe", amount_differences_summary),
        _section("date_differences", "Diferencias de fecha", date_differences_summary),
        _section("missing_evidence", "Faltantes de evidencia", missing_evidence_summary),
        _section("next_steps", "Próximos pasos", next_steps),
        _section("caveats", "Límites y caveats", caveats),
    ]


def _section(section_id: str, title: str, payload: object) -> dict[str, object]:
    return {
        "id": section_id,
        "title": title,
        "payload": payload,
        "markdown_ready": True,
    }


def _next_steps_for_status(status: str) -> list[str]:
    if status == "BLOCKED_BY_INVALID_INPUTS":
        return [
            "Corregir la estructura de datos de movimientos bancarios e internos.",
            "Validar que cada movimiento sea un registro con fecha e importe utilizables.",
            "Reintentar la revisión asistida sin declarar conciliación.",
        ]
    if status == "NEEDS_MORE_EVIDENCE":
        return [
            "Completar fecha, importe o referencia faltante en los movimientos observados.",
            "Pedir comprobantes o referencias al responsable administrativo.",
            "Revisar nuevamente cuando la evidencia mínima esté disponible.",
        ]
    if status == "NO_REVIEWABLE_CANDIDATES":
        return [
            "Revisar criterio de fechas e importes.",
            "Cargar más evidencia bancaria o interna si existe.",
            "Confirmar si los movimientos pertenecen al mismo período operativo.",
        ]
    if status == "PARTIAL_REVIEW_READY":
        return [
            "Revisar matches probables antes de marcar cualquier relación como aceptada.",
            "Analizar diferencias de importe y fecha con soporte documental.",
            "Separar pendientes bancarios e internos para seguimiento humano.",
        ]
    return [
        "Revisar matches exactos antes de marcar cualquier movimiento como conciliado.",
        "Confirmar evidencia con el responsable administrativo o contador.",
        "Mantener el resultado como revisión asistida, no como cierre definitivo.",
    ]

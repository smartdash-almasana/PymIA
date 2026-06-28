from __future__ import annotations

from typing import Final

DeliveryPacketV1 = dict[str, object]

SERVICE_REF: Final[str] = "S2_ADMIN_OPERATIONS_V1"
PACKET_REF: Final[str] = "S2_RECONCILIATION_ASSISTED_REVIEW_DELIVERY_PACKET_V1"
SOURCE_BLOCK_REF: Final[str] = "S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1"

ALLOWED_PACKET_STATUSES: Final[tuple[str, ...]] = (
    "READY_FOR_OPERATOR_REVIEW",
    "NEEDS_MORE_EVIDENCE",
    "BLOCKED_BY_INVALID_INPUTS",
    "NO_REVIEWABLE_CANDIDATES",
    "PARTIAL_PACKET_READY",
)

STATUS_BY_REVIEW_STATUS: Final[dict[str, str]] = {
    "READY_FOR_ASSISTED_REVIEW": "READY_FOR_OPERATOR_REVIEW",
    "PARTIAL_REVIEW_READY": "PARTIAL_PACKET_READY",
    "NEEDS_MORE_EVIDENCE": "NEEDS_MORE_EVIDENCE",
    "BLOCKED_BY_INVALID_INPUTS": "BLOCKED_BY_INVALID_INPUTS",
    "NO_REVIEWABLE_CANDIDATES": "NO_REVIEWABLE_CANDIDATES",
}

CAVEATS: Final[tuple[str, ...]] = (
    "Paquete lógico de revisión asistida; no escribe archivos.",
    "No es conciliación definitiva.",
    "No certifica saldo bancario.",
    "No reemplaza revisión contable.",
    "No produce cierre contable ni fiscal.",
    "Requiere revisión humana antes de cualquier decisión operativa.",
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


def build_reconciliation_assisted_review_delivery_packet_v1(
    assisted_review_result: object,
) -> DeliveryPacketV1:
    if not isinstance(assisted_review_result, dict):
        return _blocked_packet(
            reason="assisted_review_result_must_be_a_dict",
            assisted_review_result=assisted_review_result,
        )

    validation_errors = _validate_assisted_review_result(assisted_review_result)
    if validation_errors:
        return _blocked_packet(
            reason="invalid_assisted_review_result",
            assisted_review_result=assisted_review_result,
            validation_errors=validation_errors,
        )

    review_status = str(assisted_review_result["status"])
    packet_status = STATUS_BY_REVIEW_STATUS.get(review_status, "BLOCKED_BY_INVALID_INPUTS")
    review_summary = _safe_dict(assisted_review_result.get("review_summary"))

    return {
        "schema_version": "1.0",
        "service": SERVICE_REF,
        "packet": PACKET_REF,
        "source_block": SOURCE_BLOCK_REF,
        "status": packet_status,
        "source_status": review_status,
        "requires_human_review": True,
        "audience": {
            "operator": True,
            "owner": True,
            "accountant": True,
        },
        "title": "Paquete lógico de revisión asistida de conciliación",
        "operator_brief": _operator_brief(packet_status, review_summary),
        "owner_summary": _owner_summary(packet_status, review_summary),
        "accountant_summary": _accountant_summary(packet_status, review_summary),
        "sections": _build_sections(assisted_review_result),
        "counts": _counts_from_review_summary(review_summary),
        "next_steps": _safe_list(assisted_review_result.get("next_steps")),
        "caveats": _merge_unique(_safe_list(assisted_review_result.get("caveats")), list(CAVEATS)),
        "forbidden_claims": _merge_unique(
            _safe_list(assisted_review_result.get("forbidden_claims")),
            list(FORBIDDEN_CLAIMS),
        ),
        "markdown_ready": True,
        "io_performed": False,
        "files_created": [],
        "xlsx_created": False,
        "api_used": False,
        "llm_used": False,
        "source_result": assisted_review_result,
    }


def _blocked_packet(
    *,
    reason: str,
    assisted_review_result: object,
    validation_errors: list[dict[str, object]] | None = None,
) -> DeliveryPacketV1:
    return {
        "schema_version": "1.0",
        "service": SERVICE_REF,
        "packet": PACKET_REF,
        "source_block": SOURCE_BLOCK_REF,
        "status": "BLOCKED_BY_INVALID_INPUTS",
        "source_status": None,
        "requires_human_review": True,
        "audience": {
            "operator": True,
            "owner": True,
            "accountant": True,
        },
        "title": "Paquete lógico de revisión asistida de conciliación",
        "operator_brief": "No se puede preparar el paquete: el resultado de revisión asistida es inválido.",
        "owner_summary": "No se puede preparar una salida confiable con la evidencia recibida.",
        "accountant_summary": "No hay base suficiente para revisión contable asistida.",
        "sections": [],
        "counts": _empty_counts(),
        "next_steps": [
            "Corregir el resultado de revisión asistida recibido.",
            "Validar que la estructura tenga status, requires_human_review y review_summary.",
            "Reintentar sin declarar conciliación definitiva.",
        ],
        "caveats": list(CAVEATS),
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "markdown_ready": True,
        "io_performed": False,
        "files_created": [],
        "xlsx_created": False,
        "api_used": False,
        "llm_used": False,
        "block_reason": reason,
        "validation_errors": validation_errors or [],
        "source_result": assisted_review_result,
    }


def _validate_assisted_review_result(value: dict[str, object]) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    if value.get("service") != SERVICE_REF:
        errors.append({"field": "service", "reason": "must_be_S2_ADMIN_OPERATIONS_V1"})
    if value.get("block") != SOURCE_BLOCK_REF:
        errors.append({"field": "block", "reason": "must_be_assisted_review_block_v1"})
    if not isinstance(value.get("status"), str):
        errors.append({"field": "status", "reason": "must_be_string"})
    elif str(value["status"]) not in STATUS_BY_REVIEW_STATUS:
        errors.append({"field": "status", "reason": "unsupported_review_status"})
    if value.get("requires_human_review") is not True:
        errors.append({"field": "requires_human_review", "reason": "must_be_true"})
    if not isinstance(value.get("review_summary"), dict):
        errors.append({"field": "review_summary", "reason": "must_be_dict"})
    return errors


def _build_sections(assisted_review_result: dict[str, object]) -> list[dict[str, object]]:
    return [
        _section("executive_summary", "Resumen ejecutivo", assisted_review_result.get("executive_summary")),
        _section("exact_matches", "Matches exactos", assisted_review_result.get("exact_matches_summary")),
        _section("probable_matches", "Matches probables", assisted_review_result.get("probable_matches_summary")),
        _section("bank_pending", "Movimientos bancarios sin imputar", assisted_review_result.get("bank_pending_summary")),
        _section("internal_pending", "Movimientos internos sin banco", assisted_review_result.get("internal_pending_summary")),
        _section("amount_differences", "Diferencias de importe", assisted_review_result.get("amount_differences_summary")),
        _section("date_differences", "Diferencias de fecha", assisted_review_result.get("date_differences_summary")),
        _section("missing_evidence", "Faltantes de evidencia", assisted_review_result.get("missing_evidence_summary")),
        _section("next_steps", "Próximos pasos", assisted_review_result.get("next_steps")),
        _section("caveats", "Límites y caveats", assisted_review_result.get("caveats")),
    ]


def _section(section_id: str, title: str, payload: object) -> dict[str, object]:
    return {
        "id": section_id,
        "title": title,
        "payload": payload,
        "markdown_ready": True,
    }


def _counts_from_review_summary(review_summary: dict[str, object]) -> dict[str, int]:
    return {
        "matches_exactos": _int_count(review_summary.get("matches_exactos")),
        "matches_probables": _int_count(review_summary.get("matches_probables")),
        "banco_sin_imputar": _int_count(review_summary.get("banco_sin_imputar")),
        "interno_sin_banco": _int_count(review_summary.get("interno_sin_banco")),
        "diferencias_importe": _int_count(review_summary.get("diferencias_importe")),
        "diferencias_fecha": _int_count(review_summary.get("diferencias_fecha")),
        "faltantes_evidencia": _int_count(review_summary.get("faltantes_evidencia")),
    }


def _empty_counts() -> dict[str, int]:
    return {
        "matches_exactos": 0,
        "matches_probables": 0,
        "banco_sin_imputar": 0,
        "interno_sin_banco": 0,
        "diferencias_importe": 0,
        "diferencias_fecha": 0,
        "faltantes_evidencia": 0,
    }


def _operator_brief(status: str, review_summary: dict[str, object]) -> str:
    counts = _counts_from_review_summary(review_summary)
    return (
        f"Paquete lógico listo con estado {status}: "
        f"{counts['matches_exactos']} exactos, "
        f"{counts['matches_probables']} probables, "
        f"{counts['banco_sin_imputar']} bancarios pendientes, "
        f"{counts['interno_sin_banco']} internos pendientes."
    )


def _owner_summary(status: str, review_summary: dict[str, object]) -> str:
    counts = _counts_from_review_summary(review_summary)
    return (
        "Se preparó una revisión asistida para mirar con responsable o contador: "
        f"{counts['matches_exactos']} coincidencias exactas, "
        f"{counts['matches_probables']} posibles coincidencias y "
        f"{counts['faltantes_evidencia']} faltantes de evidencia. "
        f"Estado: {status}."
    )


def _accountant_summary(status: str, review_summary: dict[str, object]) -> str:
    counts = _counts_from_review_summary(review_summary)
    return (
        "Paquete preliminar para revisión contable asistida: "
        f"{counts['diferencias_importe']} diferencias de importe, "
        f"{counts['diferencias_fecha']} diferencias de fecha, "
        f"{counts['banco_sin_imputar']} movimientos bancarios sin imputar y "
        f"{counts['interno_sin_banco']} movimientos internos sin banco. "
        f"Estado: {status}."
    )


def _safe_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _safe_list(value: object) -> list[object]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return []


def _merge_unique(left: list[object], right: list[object]) -> list[object]:
    merged: list[object] = []
    for item in [*left, *right]:
        if item not in merged:
            merged.append(item)
    return merged


def _int_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    if value < 0:
        return 0
    return value

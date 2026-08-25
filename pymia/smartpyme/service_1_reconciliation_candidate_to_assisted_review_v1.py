"""Controlled adapter from a governed Servicio 1 reconciliation candidate.

The adapter accepts only a RECONCILIATION_CANDIDATE_READY packet produced by
``service_1_reconciliation_request_gate_v1``. It routes the candidate to the
existing deterministic bank or Mercado Pago reconciliation capability and
returns a uniform assisted-review envelope.

It does not read files, mutate source data, resolve ambiguity, accept matches,
create accounting entries, or promote the capability into the canonical
Servicio 1 product root.
"""
from __future__ import annotations

from typing import Any, Final, Mapping

from pymia.contracts.formula_contract import (
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
)
from pymia.services.formula_engine_service import FormulaEngineService

from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
    PACKET_TYPE as REQUEST_GATE_PACKET_TYPE,
    SCHEMA_VERSION as REQUEST_GATE_SCHEMA_VERSION,
    STATUS_READY as REQUEST_GATE_STATUS_READY,
)
from pymia.smartpyme.service_2_mercado_pago_bank_reconciliation_v1 import (
    build_mercado_pago_bank_reconciliation_v1,
)
from pymia.smartpyme.service_2_reconciliation_assisted_review_block_v1 import (
    BLOCK_REF as BANK_REVIEW_BLOCK_REF,
    build_reconciliation_assisted_review_block_v1,
)

SCHEMA_VERSION: Final[str] = (
    "SERVICE_1_RECONCILIATION_CANDIDATE_TO_ASSISTED_REVIEW_V1"
)
SERVICE_NAME: Final[str] = "SERVICE_1"
PACKET_TYPE: Final[str] = "RECONCILIATION_ASSISTED_REVIEW_ADAPTER"
EXPECTED_CANDIDATE_SCHEMA: Final[str] = "SERVICE_1_RECONCILIATION_CANDIDATE_V1"

STATUS_READY: Final[str] = "READY_FOR_ASSISTED_REVIEW"
STATUS_PARTIAL: Final[str] = "PARTIAL_REVIEW_READY"
STATUS_NEEDS_EVIDENCE: Final[str] = "NEEDS_MORE_EVIDENCE"
STATUS_NO_CANDIDATES: Final[str] = "NO_REVIEWABLE_CANDIDATES"
STATUS_BLOCKED: Final[str] = "BLOCKED_BY_INVALID_INPUTS"
ALLOWED_STATUSES: Final[frozenset[str]] = frozenset(
    {
        STATUS_READY,
        STATUS_PARTIAL,
        STATUS_NEEDS_EVIDENCE,
        STATUS_NO_CANDIDATES,
        STATUS_BLOCKED,
    }
)

BANK_RECONCILER_REF: Final[str] = BANK_REVIEW_BLOCK_REF
MERCADO_PAGO_RECONCILER_REF: Final[str] = (
    "S2_MERCADO_PAGO_BANK_RECONCILIATION_V1"
)

_SAFETY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)

_MP_STATUS_MAP: Final[dict[str, str]] = {
    "READY_FOR_HUMAN_REVIEW": STATUS_READY,
    "PARTIAL_MATCHES_FOUND": STATUS_PARTIAL,
    "NEEDS_MORE_EVIDENCE": STATUS_NEEDS_EVIDENCE,
    "NO_CANDIDATES_FOUND": STATUS_NO_CANDIDATES,
    "BLOCKED_BY_INVALID_INPUTS": STATUS_BLOCKED,
}


def build_service_1_reconciliation_assisted_review_v1(
    *,
    gate_packet: Mapping[str, Any],
    options: Mapping[str, Any] | None = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Route one governed candidate to deterministic assisted review."""
    if any(
        (
            runtime_authorized,
            tool_execution_authorized,
            product_ready,
            delivery_authorized,
            diagnosis_generated,
        )
    ):
        return _blocked(reason="REQUEST_SAFETY_FLAGS_FORBIDDEN")
    if not isinstance(gate_packet, Mapping) or not gate_packet:
        return _blocked(reason="GATE_PACKET_REQUIRED")
    if gate_packet.get("schema_version") != REQUEST_GATE_SCHEMA_VERSION:
        return _blocked(reason="GATE_SCHEMA_INVALID")
    if gate_packet.get("packet_type") != REQUEST_GATE_PACKET_TYPE:
        return _blocked(reason="GATE_PACKET_TYPE_INVALID")
    if gate_packet.get("status") != REQUEST_GATE_STATUS_READY:
        return _blocked(
            reason="GATE_NOT_READY",
            case_id=_text(gate_packet.get("case_id")),
            reconciliation_type=_text(gate_packet.get("reconciliation_type")),
        )
    if _has_forbidden_flag(gate_packet):
        return _blocked(
            reason="GATE_SAFETY_FLAGS_FORBIDDEN",
            case_id=_text(gate_packet.get("case_id")),
            reconciliation_type=_text(gate_packet.get("reconciliation_type")),
        )
    if options is not None and not isinstance(options, Mapping):
        return _blocked(
            reason="OPTIONS_MUST_BE_A_MAPPING",
            case_id=_text(gate_packet.get("case_id")),
            reconciliation_type=_text(gate_packet.get("reconciliation_type")),
        )

    candidate = gate_packet.get("reconciliation_candidate")
    if not isinstance(candidate, Mapping):
        return _blocked(
            reason="RECONCILIATION_CANDIDATE_REQUIRED",
            case_id=_text(gate_packet.get("case_id")),
            reconciliation_type=_text(gate_packet.get("reconciliation_type")),
        )
    if candidate.get("schema_version") != EXPECTED_CANDIDATE_SCHEMA:
        return _blocked(
            reason="CANDIDATE_SCHEMA_INVALID",
            case_id=_text(gate_packet.get("case_id")),
            reconciliation_type=_text(gate_packet.get("reconciliation_type")),
        )
    if _has_forbidden_flag(candidate):
        return _blocked(
            reason="CANDIDATE_SAFETY_FLAGS_FORBIDDEN",
            case_id=_text(gate_packet.get("case_id")),
            reconciliation_type=_text(gate_packet.get("reconciliation_type")),
        )

    case_id = _text(gate_packet.get("case_id"))
    reconciliation_type = _text(gate_packet.get("reconciliation_type"))
    if not case_id or not reconciliation_type:
        return _blocked(
            reason="CASE_AND_RECONCILIATION_TYPE_REQUIRED",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
        )
    if _text(candidate.get("case_id")) != case_id:
        return _blocked(
            reason="CANDIDATE_CASE_MISMATCH",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
        )
    if _text(candidate.get("reconciliation_type")) != reconciliation_type:
        return _blocked(
            reason="CANDIDATE_TYPE_MISMATCH",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
        )

    options_used = dict(options or {})
    if reconciliation_type == BANK_RECONCILIATION:
        return _run_bank_review(
            case_id=case_id,
            candidate=candidate,
            options=options_used,
        )
    if reconciliation_type == MERCADO_PAGO_BANK_RECONCILIATION:
        return _run_mercado_pago_review(
            case_id=case_id,
            candidate=candidate,
            options=options_used,
        )
    return _blocked(
        reason="UNSUPPORTED_RECONCILIATION_TYPE",
        case_id=case_id,
        reconciliation_type=reconciliation_type,
    )


def _run_bank_review(
    *,
    case_id: str,
    candidate: Mapping[str, Any],
    options: dict[str, Any],
) -> dict[str, Any]:
    bank_movements = candidate.get("bank_movements")
    internal_movements = candidate.get("internal_movements")
    if not isinstance(bank_movements, list) or not isinstance(internal_movements, list):
        return _blocked(
            reason="BANK_CANDIDATE_MOVEMENTS_REQUIRED",
            case_id=case_id,
            reconciliation_type=BANK_RECONCILIATION,
        )

    review_result = build_reconciliation_assisted_review_block_v1(
        bank_movements,
        internal_movements,
        options=options or None,
    )
    status = str(review_result.get("status") or STATUS_BLOCKED)
    if status not in ALLOWED_STATUSES:
        status = STATUS_BLOCKED
    source_status = str(review_result.get("source_status") or "")
    summary = _bank_summary(review_result)
    return _packet(
        case_id=case_id,
        reconciliation_type=BANK_RECONCILIATION,
        status=status,
        source_status=source_status,
        reconciler_ref=BANK_RECONCILER_REF,
        review_summary=summary,
        review_result=review_result,
        candidate=candidate,
    )


def _run_mercado_pago_review(
    *,
    case_id: str,
    candidate: Mapping[str, Any],
    options: dict[str, Any],
) -> dict[str, Any]:
    operations = candidate.get("mercado_pago_operations")
    bank_movements = candidate.get("bank_movements")
    if not isinstance(operations, list) or not isinstance(bank_movements, list):
        return _blocked(
            reason="MERCADO_PAGO_CANDIDATE_MOVEMENTS_REQUIRED",
            case_id=case_id,
            reconciliation_type=MERCADO_PAGO_BANK_RECONCILIATION,
        )

    review_result = build_mercado_pago_bank_reconciliation_v1(
        operations,
        bank_movements,
        options=options or None,
    )
    source_status = str(review_result.get("status") or "BLOCKED_BY_INVALID_INPUTS")
    status = _MP_STATUS_MAP.get(source_status, STATUS_BLOCKED)
    summary = _mercado_pago_summary(review_result)
    return _packet(
        case_id=case_id,
        reconciliation_type=MERCADO_PAGO_BANK_RECONCILIATION,
        status=status,
        source_status=source_status,
        reconciler_ref=MERCADO_PAGO_RECONCILER_REF,
        review_summary=summary,
        review_result=review_result,
        candidate=candidate,
    )


def _bank_summary(review_result: Mapping[str, Any]) -> dict[str, int]:
    source = review_result.get("review_summary")
    values = source if isinstance(source, Mapping) else {}
    return {
        "confirmed_candidates": _int(values.get("matches_exactos")),
        "probable_candidates": _int(values.get("matches_probables")),
        "ambiguous_groups": _int(values.get("matches_ambiguos")),
        "amount_differences": _int(values.get("diferencias_importe")),
        "date_differences": _int(values.get("diferencias_fecha")),
        "bank_pending": _int(values.get("banco_sin_imputar")),
        "internal_pending": _int(values.get("interno_sin_banco")),
        "missing_evidence": _int(values.get("faltantes_evidencia")),
        "calculation_inconsistencies": 0,
    }


def _mercado_pago_summary(review_result: Mapping[str, Any]) -> dict[str, int]:
    return {
        "confirmed_candidates": _count_list(review_result, "conciliaciones"),
        "probable_candidates": 0,
        "ambiguous_groups": _count_list(review_result, "ambiguos"),
        "amount_differences": _count_list(review_result, "diferencias_importe"),
        "date_differences": 0,
        "bank_pending": _count_list(
            review_result, "movimientos_banco_sin_operacion_mp"
        ),
        "internal_pending": _count_list(
            review_result, "operaciones_mp_sin_acreditacion"
        ),
        "missing_evidence": _count_list(review_result, "faltantes_evidencia"),
        "calculation_inconsistencies": _count_list(
            review_result, "inconsistencias_calculo"
        ),
    }


def _packet(
    *,
    case_id: str,
    reconciliation_type: str,
    status: str,
    source_status: str,
    reconciler_ref: str,
    review_summary: Mapping[str, int],
    review_result: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": status,
        "source_status": source_status,
        "reason": None,
        "case_id": case_id,
        "reconciliation_type": reconciliation_type,
        "reconciler_ref": reconciler_ref,
        "requires_human_review": True,
        "next_allowed_action": _next_action(status),
        "review_summary": dict(review_summary),
        "review_result": dict(review_result),
        "provenance": {
            "gate_schema": REQUEST_GATE_SCHEMA_VERSION,
            "candidate_schema": EXPECTED_CANDIDATE_SCHEMA,
            "candidate_source": dict(candidate.get("provenance") or {}),
            "reconciler_ref": reconciler_ref,
        },
        "io_performed": False,
        "files_created": [],
        "api_used": False,
        "llm_used": False,
        **_safety_flags(),
    }


def _blocked(
    *,
    reason: str,
    case_id: str | None = None,
    reconciliation_type: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_BLOCKED,
        "source_status": None,
        "reason": reason,
        "case_id": case_id or "",
        "reconciliation_type": reconciliation_type or "",
        "reconciler_ref": None,
        "requires_human_review": True,
        "next_allowed_action": "fix_reconciliation_candidate",
        "review_summary": {},
        "review_result": None,
        "provenance": {},
        "io_performed": False,
        "files_created": [],
        "api_used": False,
        "llm_used": False,
        **_safety_flags(),
    }


def _next_action(status: str) -> str:
    if status in {STATUS_READY, STATUS_PARTIAL}:
        return "human_reconciliation_review"
    if status == STATUS_NEEDS_EVIDENCE:
        return "request_reconciliation_evidence"
    if status == STATUS_NO_CANDIDATES:
        return "review_reconciliation_scope"
    return "fix_reconciliation_candidate"


def _has_forbidden_flag(value: Mapping[str, Any]) -> bool:
    return any(value.get(flag) is True for flag in _SAFETY_FLAGS)


def _safety_flags() -> dict[str, bool]:
    return {
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _text(value: object) -> str:
    return str(value or "").strip()


def _int(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        bounded = FormulaEngineService().calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.MAX,
                values=[value, 0],
                source_refs=["reconciliation:review_summary"],
            )
        )
        if bounded.status == FormulaStatus.OK and bounded.value is not None:
            return int(bounded.value)
    return 0


def _count_list(value: Mapping[str, Any], key: str) -> int:
    items = value.get(key)
    return len(items) if isinstance(items, list) else 0


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "EXPECTED_CANDIDATE_SCHEMA",
    "STATUS_READY",
    "STATUS_PARTIAL",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_NO_CANDIDATES",
    "STATUS_BLOCKED",
    "ALLOWED_STATUSES",
    "BANK_RECONCILER_REF",
    "MERCADO_PAGO_RECONCILER_REF",
    "build_service_1_reconciliation_assisted_review_v1",
]

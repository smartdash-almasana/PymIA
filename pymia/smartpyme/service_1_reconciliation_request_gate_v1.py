"""Governed Servicio 1 request gate for reconciliation preparation.

This module is a fail-closed boundary between Servicio 1 semantic governance
and the existing reconciliation capabilities. It validates an explicit owner
request, required sources, canonical field bindings, and upstream P5-P8
statuses. On success it prepares a reconciliation candidate packet only.

It never reads files, never calls a matcher, never resolves ambiguity, and
never authorizes runtime, product delivery, diagnosis, or accounting closure.
"""
from __future__ import annotations

from typing import Any, Final, Mapping, Sequence

SCHEMA_VERSION: Final[str] = "SERVICE_1_RECONCILIATION_REQUEST_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
PACKET_TYPE: Final[str] = "RECONCILIATION_REQUEST_GATE"

BANK_RECONCILIATION: Final[str] = "BANK_RECONCILIATION"
MERCADO_PAGO_BANK_RECONCILIATION: Final[str] = (
    "MERCADO_PAGO_BANK_RECONCILIATION"
)
ALLOWED_RECONCILIATION_TYPES: Final[frozenset[str]] = frozenset(
    {BANK_RECONCILIATION, MERCADO_PAGO_BANK_RECONCILIATION}
)

STATUS_READY: Final[str] = "RECONCILIATION_CANDIDATE_READY"
STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"
STATUS_MISSING_REQUIRED_SOURCE: Final[str] = "MISSING_REQUIRED_SOURCE"
STATUS_MISSING_REQUIRED_FIELD: Final[str] = "MISSING_REQUIRED_FIELD"
STATUS_BLOCKED: Final[str] = "BLOCKED"
ALLOWED_STATUSES: Final[frozenset[str]] = frozenset(
    {
        STATUS_READY,
        STATUS_NEEDS_OWNER_CONFIRMATION,
        STATUS_MISSING_REQUIRED_SOURCE,
        STATUS_MISSING_REQUIRED_FIELD,
        STATUS_BLOCKED,
    }
)

_REQUIRED_SOURCES: Final[dict[str, tuple[str, ...]]] = {
    BANK_RECONCILIATION: ("bank", "internal"),
    MERCADO_PAGO_BANK_RECONCILIATION: ("mercado_pago", "bank"),
}

_REQUIRED_FIELDS: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    BANK_RECONCILIATION: {
        "bank": ("id", "fecha", "importe", "referencia"),
        "internal": ("id", "fecha", "importe", "referencia"),
    },
    MERCADO_PAGO_BANK_RECONCILIATION: {
        "mercado_pago": (
            "operacion_mp_id",
            "fecha_operacion",
            "importe_bruto",
            "comision",
            "retencion",
            "importe_neto",
            "lote_id",
            "referencia",
        ),
        "bank": (
            "movimiento_banco_id",
            "fecha",
            "importe",
            "lote_id",
            "referencia",
        ),
    },
}

_OPTIONAL_FIELDS: Final[dict[str, tuple[str, ...]]] = {
    "bank": ("descripcion",),
    "internal": ("descripcion",),
    "mercado_pago": ("estado", "descripcion"),
}

_FORBIDDEN_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_reconciliation_request_gate_v1(
    *,
    case_id: str,
    owner_requested: bool,
    reconciliation_type: str,
    source_packets: Sequence[Mapping[str, Any]],
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Prepare a governed reconciliation candidate without executing it."""
    case = str(case_id or "").strip()
    requested_type = str(reconciliation_type or "").strip()

    if any(
        (
            runtime_authorized,
            tool_execution_authorized,
            product_ready,
            delivery_authorized,
            diagnosis_generated,
        )
    ):
        return _blocked(
            case_id=case or None,
            reconciliation_type=requested_type or None,
            reason="REQUEST_SAFETY_FLAGS_FORBIDDEN",
        )
    if not case:
        return _blocked(
            case_id=None,
            reconciliation_type=requested_type or None,
            reason="CASE_ID_REQUIRED",
        )
    if owner_requested is not True:
        return _blocked(
            case_id=case,
            reconciliation_type=requested_type or None,
            reason="EXPLICIT_OWNER_REQUEST_REQUIRED",
        )
    if requested_type not in ALLOWED_RECONCILIATION_TYPES:
        return _blocked(
            case_id=case,
            reconciliation_type=requested_type or None,
            reason="UNSUPPORTED_RECONCILIATION_TYPE",
        )
    if not isinstance(source_packets, Sequence) or isinstance(
        source_packets, (str, bytes)
    ):
        return _blocked(
            case_id=case,
            reconciliation_type=requested_type,
            reason="SOURCE_PACKETS_MUST_BE_A_SEQUENCE",
        )

    packet_index: dict[str, Mapping[str, Any]] = {}
    for packet in source_packets:
        if not isinstance(packet, Mapping):
            return _blocked(
                case_id=case,
                reconciliation_type=requested_type,
                reason="SOURCE_PACKET_MUST_BE_A_MAPPING",
            )
        source_kind = str(packet.get("source_kind") or "").strip()
        if not source_kind:
            return _blocked(
                case_id=case,
                reconciliation_type=requested_type,
                reason="SOURCE_KIND_REQUIRED",
            )
        if source_kind in packet_index:
            return _blocked(
                case_id=case,
                reconciliation_type=requested_type,
                reason=f"DUPLICATE_SOURCE_KIND:{source_kind}",
            )
        packet_index[source_kind] = packet

    required_sources = _REQUIRED_SOURCES[requested_type]
    missing_sources = [
        source_kind
        for source_kind in required_sources
        if source_kind not in packet_index
    ]
    if missing_sources:
        return _packet(
            case_id=case,
            reconciliation_type=requested_type,
            status=STATUS_MISSING_REQUIRED_SOURCE,
            reason="REQUIRED_RECONCILIATION_SOURCE_MISSING",
            missing_sources=missing_sources,
        )

    projected_sources: dict[str, list[dict[str, Any]]] = {}
    provenance_sources: list[dict[str, Any]] = []
    for source_kind in required_sources:
        source_packet = packet_index[source_kind]
        governance_result = _validate_governance(source_packet)
        if governance_result["status"] == STATUS_NEEDS_OWNER_CONFIRMATION:
            return _packet(
                case_id=case,
                reconciliation_type=requested_type,
                status=STATUS_NEEDS_OWNER_CONFIRMATION,
                reason=str(governance_result["reason"]),
                source_kind=source_kind,
            )
        if governance_result["status"] == STATUS_BLOCKED:
            return _blocked(
                case_id=case,
                reconciliation_type=requested_type,
                reason=f"{source_kind}:{governance_result['reason']}",
            )

        projection = _project_source_rows(
            reconciliation_type=requested_type,
            source_kind=source_kind,
            source_packet=source_packet,
            approved_columns=set(governance_result["approved_columns"]),
        )
        if projection["status"] == STATUS_MISSING_REQUIRED_FIELD:
            return _packet(
                case_id=case,
                reconciliation_type=requested_type,
                status=STATUS_MISSING_REQUIRED_FIELD,
                reason=str(projection["reason"]),
                source_kind=source_kind,
                missing_fields=list(projection["missing_fields"]),
            )
        if projection["status"] == STATUS_BLOCKED:
            return _blocked(
                case_id=case,
                reconciliation_type=requested_type,
                reason=f"{source_kind}:{projection['reason']}",
            )
        projected_sources[source_kind] = list(projection["rows"])
        provenance_sources.append(
            {
                "source_kind": source_kind,
                "source_ref": str(source_packet.get("source_ref") or "").strip()
                or source_kind,
                "row_count": len(projected_sources[source_kind]),
                "p5_status": governance_result["p5_status"],
                "p6_status": governance_result["p6_status"],
                "p7_status": governance_result["p7_status"],
                "p8_status": governance_result["p8_status"],
            }
        )

    candidate: dict[str, Any] = {
        "schema_version": "SERVICE_1_RECONCILIATION_CANDIDATE_V1",
        "case_id": case,
        "reconciliation_type": requested_type,
        "provenance": {
            "source": SCHEMA_VERSION,
            "sources": provenance_sources,
        },
        **_safety_flags(),
    }
    if requested_type == BANK_RECONCILIATION:
        candidate["bank_movements"] = projected_sources["bank"]
        candidate["internal_movements"] = projected_sources["internal"]
    else:
        candidate["mercado_pago_operations"] = projected_sources["mercado_pago"]
        candidate["bank_movements"] = projected_sources["bank"]

    return _packet(
        case_id=case,
        reconciliation_type=requested_type,
        status=STATUS_READY,
        reason=None,
        reconciliation_candidate=candidate,
    )


def _validate_governance(source_packet: Mapping[str, Any]) -> dict[str, Any]:
    governance = source_packet.get("governance")
    if not isinstance(governance, Mapping):
        return {"status": STATUS_BLOCKED, "reason": "GOVERNANCE_PACKET_REQUIRED"}
    if any(governance.get(flag) is True for flag in _FORBIDDEN_FLAGS):
        return {"status": STATUS_BLOCKED, "reason": "GOVERNANCE_FLAGS_FORBIDDEN"}

    p5_status = str(governance.get("p5_status") or "").strip()
    if p5_status in {"NEEDS_OWNER_CONFIRMATION", "AMBIGUOUS"}:
        return {
            "status": STATUS_NEEDS_OWNER_CONFIRMATION,
            "reason": f"P5_{p5_status}",
        }
    if p5_status != "CONFIRMED":
        return {"status": STATUS_BLOCKED, "reason": "P5_CONFIRMATION_REQUIRED"}

    decisions_raw = governance.get("p6_decisions")
    if not isinstance(decisions_raw, Sequence) or isinstance(
        decisions_raw, (str, bytes)
    ):
        return {"status": STATUS_BLOCKED, "reason": "P6_DECISIONS_REQUIRED"}
    decisions = list(decisions_raw)
    if not decisions or any(not isinstance(item, Mapping) for item in decisions):
        return {"status": STATUS_BLOCKED, "reason": "P6_DECISIONS_INVALID"}
    statuses = {str(item.get("status") or "").strip() for item in decisions}
    if statuses & {"NEEDS_OWNER_CONFIRMATION", "AMBIGUOUS"}:
        return {
            "status": STATUS_NEEDS_OWNER_CONFIRMATION,
            "reason": "P6_OWNER_CONFIRMATION_REQUIRED",
        }
    if statuses != {"APPROVED"}:
        return {"status": STATUS_BLOCKED, "reason": "P6_APPROVAL_REQUIRED"}
    approved_columns = {
        str(item.get("column_ref") or "").strip()
        for item in decisions
        if str(item.get("column_ref") or "").strip()
    }
    if not approved_columns:
        return {"status": STATUS_BLOCKED, "reason": "P6_APPROVED_COLUMNS_MISSING"}

    p7_status = str(governance.get("p7_status") or "").strip()
    if p7_status != "REQUIREMENT_MATCHED":
        return {"status": STATUS_BLOCKED, "reason": "P7_REQUIREMENT_MATCH_REQUIRED"}
    p8_status = str(governance.get("p8_status") or "").strip()
    if p8_status != "COMPUTABLE":
        return {"status": STATUS_BLOCKED, "reason": "P8_COMPUTABILITY_REQUIRED"}

    return {
        "status": STATUS_READY,
        "reason": None,
        "approved_columns": approved_columns,
        "p5_status": p5_status,
        "p6_status": "APPROVED",
        "p7_status": p7_status,
        "p8_status": p8_status,
    }


def _project_source_rows(
    *,
    reconciliation_type: str,
    source_kind: str,
    source_packet: Mapping[str, Any],
    approved_columns: set[str],
) -> dict[str, Any]:
    bindings = source_packet.get("field_bindings")
    if not isinstance(bindings, Mapping):
        return {
            "status": STATUS_MISSING_REQUIRED_FIELD,
            "reason": "FIELD_BINDINGS_REQUIRED",
            "missing_fields": list(_REQUIRED_FIELDS[reconciliation_type][source_kind]),
        }

    required_fields = _REQUIRED_FIELDS[reconciliation_type][source_kind]
    missing_bindings = [
        field
        for field in required_fields
        if not str(bindings.get(field) or "").strip()
    ]
    if missing_bindings:
        return {
            "status": STATUS_MISSING_REQUIRED_FIELD,
            "reason": "REQUIRED_FIELD_BINDING_MISSING",
            "missing_fields": missing_bindings,
        }

    bound_columns = {
        str(bindings[field]).strip()
        for field in required_fields
    }
    unapproved_columns = sorted(bound_columns - approved_columns)
    if unapproved_columns:
        return {
            "status": STATUS_BLOCKED,
            "reason": f"BOUND_COLUMNS_NOT_P6_APPROVED:{','.join(unapproved_columns)}",
        }

    rows_raw = source_packet.get("rows")
    if not isinstance(rows_raw, Sequence) or isinstance(rows_raw, (str, bytes)):
        return {"status": STATUS_BLOCKED, "reason": "SOURCE_ROWS_MUST_BE_A_SEQUENCE"}
    rows = list(rows_raw)
    if not rows:
        return {"status": STATUS_BLOCKED, "reason": "SOURCE_ROWS_EMPTY"}
    if any(not isinstance(row, Mapping) for row in rows):
        return {"status": STATUS_BLOCKED, "reason": "SOURCE_ROW_MUST_BE_A_MAPPING"}

    missing_columns: set[str] = set()
    for row in rows:
        for field in required_fields:
            source_column = str(bindings[field]).strip()
            if source_column not in row:
                missing_columns.add(source_column)
    if missing_columns:
        return {
            "status": STATUS_MISSING_REQUIRED_FIELD,
            "reason": "BOUND_SOURCE_COLUMN_MISSING",
            "missing_fields": sorted(missing_columns),
        }

    output_fields = list(required_fields)
    for optional_field in _OPTIONAL_FIELDS.get(source_kind, ()):
        if str(bindings.get(optional_field) or "").strip():
            output_fields.append(optional_field)

    projected: list[dict[str, Any]] = []
    for row in rows:
        projected.append(
            {
                field: row.get(str(bindings[field]).strip())
                for field in output_fields
            }
        )
    return {"status": STATUS_READY, "reason": None, "rows": projected}


def _packet(
    *,
    case_id: str,
    reconciliation_type: str,
    status: str,
    reason: str | None,
    reconciliation_candidate: Mapping[str, Any] | None = None,
    source_kind: str | None = None,
    missing_sources: Sequence[str] = (),
    missing_fields: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": status,
        "reason": reason,
        "case_id": case_id,
        "reconciliation_type": reconciliation_type,
        "source_kind": source_kind,
        "missing_sources": list(missing_sources),
        "missing_fields": list(missing_fields),
        "reconciliation_candidate": dict(reconciliation_candidate)
        if reconciliation_candidate is not None
        else None,
        **_safety_flags(),
    }


def _blocked(
    *,
    case_id: str | None,
    reconciliation_type: str | None,
    reason: str,
) -> dict[str, Any]:
    return _packet(
        case_id=case_id or "",
        reconciliation_type=reconciliation_type or "",
        status=STATUS_BLOCKED,
        reason=reason,
    )


def _safety_flags() -> dict[str, bool]:
    return {
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "BANK_RECONCILIATION",
    "MERCADO_PAGO_BANK_RECONCILIATION",
    "ALLOWED_RECONCILIATION_TYPES",
    "STATUS_READY",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_MISSING_REQUIRED_SOURCE",
    "STATUS_MISSING_REQUIRED_FIELD",
    "STATUS_BLOCKED",
    "ALLOWED_STATUSES",
    "build_service_1_reconciliation_request_gate_v1",
]

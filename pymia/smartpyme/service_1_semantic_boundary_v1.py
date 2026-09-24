"""Serialized consumer boundary for Service 1 canonical C2 semantics.

This module is intentionally a transport contract around the existing assisted
semantic wiring.  It owns no semantic interpretation, vocabulary, validation,
or owner decision logic; those remain in ``service_1_assisted_semantic_product_wiring_v1``.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping
from uuid import uuid4

from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_BLOCKED,
    run_service_1_assisted_semantic_initial_v1,
    run_service_1_assisted_semantic_reentry_v1,
)

INITIAL_REQUEST_SCHEMA = "SERVICE_1_C2_SEMANTIC_INITIAL_REQUEST_V1"
REENTRY_REQUEST_SCHEMA = "SERVICE_1_C2_SEMANTIC_REENTRY_REQUEST_V1"
RESPONSE_SCHEMA = "SERVICE_1_C2_SEMANTIC_RESPONSE_V1"
SOURCE = "SERVICE_1_C2_SEMANTIC_BOUNDARY_V1"

_INITIAL_FIELDS = frozenset({
    "schema_version", "ingestion_output", "requested_capability", "sheet_name",
    "compatible_tenant_memory_hints", "semantic_scope_capabilities", "atomic_confirmation",
    "table_scoped_semantics",
})
_REENTRY_FIELDS = frozenset({
    "schema_version", "semantic_state_ref", "owner_responses", "owner_actor_id",
    "owner_actor_role", "file_ref", "timestamp",
})


class Service1SemanticStateStoreV1:
    """Process-local opaque state store for the serialized reentry boundary."""

    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    def put(self, state: dict[str, Any]) -> str:
        ref = f"c2-semantic-state:{uuid4().hex}"
        self._states[ref] = state
        return ref

    def get(self, ref: str) -> dict[str, Any] | None:
        return self._states.get(str(ref or "").strip())

    def clear(self, ref: str) -> None:
        self._states.pop(str(ref or "").strip(), None)


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _blocked(reason: str, *, detail: Any = None) -> dict[str, Any]:
    return {
        "schema_version": RESPONSE_SCHEMA,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": _json_safe(detail),
        "case_id": None,
        "requested_capability": None,
        "semantic_state_ref": None,
        "workbook_profile": None,
        "proposed_semantics": [],
        "material_ambiguities": [],
        "owner_questions": [],
        "confirmed_bindings": None,
        "authority": {
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        },
        "source": SOURCE,
    }


def _project(packet: Mapping[str, Any], *, state_ref: str | None = None) -> dict[str, Any]:
    validated = packet.get("validated_packet")
    validated = validated if isinstance(validated, Mapping) else {}
    profile = packet.get("workbook_profile")
    profile = profile if isinstance(profile, Mapping) else None
    decisions = validated.get("decisions")
    if not isinstance(decisions, (list, tuple)):
        decisions = []
    ambiguities = validated.get("material_ambiguities")
    if not isinstance(ambiguities, (list, tuple)):
        ambiguities = []
    semantic_run = packet.get("semantic_run")
    return {
        "schema_version": RESPONSE_SCHEMA,
        "status": str(packet.get("status") or STATUS_BLOCKED),
        "blocked_reason": packet.get("blocked_reason"),
        "detail": _json_safe(packet.get("detail")),
        "case_id": packet.get("case_id"),
        "requested_capability": packet.get("requested_capability"),
        "semantic_state_ref": state_ref,
        "workbook_profile": _json_safe(profile),
        "proposed_semantics": _json_safe(decisions),
        "material_ambiguities": _json_safe(ambiguities),
        "owner_questions": _json_safe(packet.get("owner_questions") or []),
        "confirmed_bindings": _json_safe(semantic_run) if semantic_run is not None else None,
        "authority": {
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        },
        "source": SOURCE,
    }


def parse_initial_request_v1(payload: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(payload, Mapping):
        return None, _blocked("C2_SEMANTIC_REQUEST_MUST_BE_MAPPING")
    if set(payload) - _INITIAL_FIELDS:
        return None, _blocked("C2_SEMANTIC_REQUEST_UNKNOWN_FIELDS")
    if payload.get("schema_version") != INITIAL_REQUEST_SCHEMA:
        return None, _blocked("C2_SEMANTIC_REQUEST_VERSION_INVALID")
    if not isinstance(payload.get("ingestion_output"), Mapping):
        return None, _blocked("C2_SEMANTIC_INGESTION_REQUIRED")
    capability = payload.get("requested_capability")
    if capability is not None and not isinstance(capability, str):
        return None, _blocked("C2_SEMANTIC_CAPABILITY_INVALID")
    return dict(payload), None


def parse_reentry_request_v1(payload: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(payload, Mapping):
        return None, _blocked("C2_SEMANTIC_REENTRY_REQUEST_MUST_BE_MAPPING")
    if set(payload) - _REENTRY_FIELDS:
        return None, _blocked("C2_SEMANTIC_REENTRY_UNKNOWN_FIELDS")
    if payload.get("schema_version") != REENTRY_REQUEST_SCHEMA:
        return None, _blocked("C2_SEMANTIC_REENTRY_VERSION_INVALID")
    if not isinstance(payload.get("semantic_state_ref"), str) or not str(payload.get("semantic_state_ref")).strip():
        return None, _blocked("C2_SEMANTIC_STATE_REF_REQUIRED")
    if not isinstance(payload.get("owner_responses"), (list, tuple)):
        return None, _blocked("C2_SEMANTIC_OWNER_RESPONSES_REQUIRED")
    if not isinstance(payload.get("owner_actor_id"), str) or not str(payload.get("owner_actor_id")).strip():
        return None, _blocked("C2_SEMANTIC_OWNER_ID_REQUIRED")
    if not isinstance(payload.get("owner_actor_role"), str) or not str(payload.get("owner_actor_role")).strip():
        return None, _blocked("C2_SEMANTIC_OWNER_ROLE_REQUIRED")
    return dict(payload), None


def execute_service_1_semantic_initial_json_v1(
    payload: Any,
    *,
    provider: Any,
    state_store: Service1SemanticStateStoreV1,
) -> dict[str, Any]:
    request, blocked = parse_initial_request_v1(payload)
    if blocked is not None:
        return blocked
    assert request is not None
    packet = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=dict(request["ingestion_output"]),
        requested_capability=request.get("requested_capability"),
        provider=provider,
        sheet_name=str(request.get("sheet_name") or "sheet1"),
        compatible_tenant_memory_hints=tuple(request.get("compatible_tenant_memory_hints") or ()),
        semantic_scope_capabilities=tuple(request.get("semantic_scope_capabilities") or ()),
        atomic_confirmation=bool(request.get("atomic_confirmation", False)),
        table_scoped_semantics=request.get("table_scoped_semantics"),
    )
    ref = state_store.put(packet) if packet.get("status") != STATUS_BLOCKED else None
    return _project(packet, state_ref=ref)


def execute_service_1_semantic_reentry_json_v1(
    payload: Any,
    *,
    state_store: Service1SemanticStateStoreV1,
) -> dict[str, Any]:
    request, blocked = parse_reentry_request_v1(payload)
    if blocked is not None:
        return blocked
    assert request is not None
    ref = str(request["semantic_state_ref"]).strip()
    previous = state_store.get(ref)
    if previous is None:
        return _blocked("C2_SEMANTIC_STATE_NOT_FOUND")
    packet = run_service_1_assisted_semantic_reentry_v1(
        previous_state=previous,
        owner_responses=request["owner_responses"],
        owner_actor_id=str(request["owner_actor_id"]),
        owner_actor_role=str(request["owner_actor_role"]),
        file_ref=request.get("file_ref"),
        timestamp=request.get("timestamp"),
    )
    next_ref = ref if packet.get("status") != "CONFIRMED_BINDINGS" else None
    if next_ref is None:
        state_store.clear(ref)
    elif packet.get("status") != STATUS_BLOCKED:
        state_store._states[ref] = previous
    return _project(packet, state_ref=next_ref)


__all__ = [
    "INITIAL_REQUEST_SCHEMA", "REENTRY_REQUEST_SCHEMA", "RESPONSE_SCHEMA", "SOURCE",
    "Service1SemanticStateStoreV1", "parse_initial_request_v1", "parse_reentry_request_v1",
    "execute_service_1_semantic_initial_json_v1", "execute_service_1_semantic_reentry_json_v1",
]

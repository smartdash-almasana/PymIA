"""
SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_V1

Pure, read-only boundary that records whether the owner has confirmed the
required evidence and minimum semantic bindings for a pathology before any
semantic evidence binding may proceed.

This module is a governance recorder, not an execution bridge. It performs
no LLM decision, no chatbot interaction, no runtime, no mapper, no engine, no
CLI, no case traces, and never mutates JSON.

Mode: PURE BOUNDARY ONLY
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


OWNER_CONFIRMED = "OWNER_CONFIRMED"
OWNER_CONFIRMATION_REQUIRED = "OWNER_CONFIRMATION_REQUIRED"
OWNER_CONFIRMATION_PENDING = "OWNER_CONFIRMATION_PENDING"
OWNER_CONFIRMATION_CONFLICT = "OWNER_CONFIRMATION_CONFLICT"
OWNER_CONFIRMATION_INSUFFICIENT = "OWNER_CONFIRMATION_INSUFFICIENT"
OWNER_CONFIRMATION_BLOCKED_BY_POLICY = "OWNER_CONFIRMATION_BLOCKED_BY_POLICY"


@dataclass(frozen=True)
class Service1OwnerConfirmationResultV1:
    """Governed owner confirmation result."""

    schema_version: str = "SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_V1"
    service_name: str = "SERVICE_1"
    pathology_code: str = ""
    confirmation_status: str = OWNER_CONFIRMATION_PENDING
    confirmed_evidence: tuple[str, ...] = ()
    missing_confirmed_evidence: tuple[str, ...] = ()
    confirmed_semantic_bindings: tuple[str, ...] = ()
    missing_semantic_bindings: tuple[str, ...] = ()
    conflict_evidence: tuple[str, ...] = ()
    runtime_allowed: bool = False  # Always False per invariant I11
    phase_5_allowed: bool = False  # Always False per invariant I12
    metadata: dict[str, Any] = field(default_factory=dict)


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(str(v) for v in value)
    return (str(value),)


def build_owner_confirmation_result_v1(
    *,
    pathology_code: str,
    required_evidence: tuple[str, ...],
    minimum_semantic_bindings: tuple[str, ...],
    owner_confirmation_packet: dict | None,
) -> Service1OwnerConfirmationResultV1:
    """
    Pure boundary function recording owner confirmation status.

    Implements fail-closed governance:
      I11. runtime_allowed is always false.
      I12. phase_5_allowed is always false.

    Args:
        pathology_code: The pathology under confirmation.
        required_evidence: Required evidence codes from governed context.
        minimum_semantic_bindings: Required binding codes from governed context.
        owner_confirmation_packet: Owner-supplied confirmation dict, or None.

    Returns:
        Service1OwnerConfirmationResultV1 with mapped confirmation_status.
    """
    required_evidence = _as_tuple(required_evidence)
    minimum_semantic_bindings = _as_tuple(minimum_semantic_bindings)

    # No packet available -> pending
    if owner_confirmation_packet is None:
        return Service1OwnerConfirmationResultV1(
            pathology_code=pathology_code,
            confirmation_status=OWNER_CONFIRMATION_PENDING,
            metadata={"rule": "no_packet"},
        )

    packet = dict(owner_confirmation_packet)

    # Policy violation takes precedence
    if packet.get("policy_violation"):
        return Service1OwnerConfirmationResultV1(
            pathology_code=pathology_code,
            confirmation_status=OWNER_CONFIRMATION_BLOCKED_BY_POLICY,
            metadata={"rule": "policy_violation"},
        )

    confirmed_evidence = _as_tuple(packet.get("confirmed_evidence"))
    confirmed_bindings = _as_tuple(packet.get("confirmed_semantic_bindings"))

    # Conflict takes precedence over evidence/binding checks
    if packet.get("conflict"):
        return Service1OwnerConfirmationResultV1(
            pathology_code=pathology_code,
            confirmation_status=OWNER_CONFIRMATION_CONFLICT,
            confirmed_evidence=confirmed_evidence,
            confirmed_semantic_bindings=confirmed_bindings,
            conflict_evidence=required_evidence,
            metadata={"rule": "conflict"},
        )

    missing_evidence = tuple(
        e for e in required_evidence if e not in confirmed_evidence
    )
    missing_bindings = tuple(
        b for b in minimum_semantic_bindings if b not in confirmed_bindings
    )

    # All required evidence and bindings confirmed
    if not missing_evidence and not missing_bindings:
        return Service1OwnerConfirmationResultV1(
            pathology_code=pathology_code,
            confirmation_status=OWNER_CONFIRMED,
            confirmed_evidence=confirmed_evidence,
            confirmed_semantic_bindings=confirmed_bindings,
            metadata={"rule": "confirmed"},
        )

    # Required evidence completely missing -> insufficient
    if not confirmed_evidence:
        return Service1OwnerConfirmationResultV1(
            pathology_code=pathology_code,
            confirmation_status=OWNER_CONFIRMATION_INSUFFICIENT,
            confirmed_evidence=confirmed_evidence,
            missing_confirmed_evidence=missing_evidence,
            confirmed_semantic_bindings=confirmed_bindings,
            missing_semantic_bindings=missing_bindings,
            metadata={"rule": "insufficient"},
        )

    # Partial confirmation present -> required (owner must complete)
    return Service1OwnerConfirmationResultV1(
        pathology_code=pathology_code,
        confirmation_status=OWNER_CONFIRMATION_REQUIRED,
        confirmed_evidence=confirmed_evidence,
        missing_confirmed_evidence=missing_evidence,
        confirmed_semantic_bindings=confirmed_bindings,
        missing_semantic_bindings=missing_bindings,
        metadata={"rule": "required"},
    )

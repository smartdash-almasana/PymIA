"""
Service 1 Assisted Flow Orchestrator V1

Single caller that composes the 12 audited Servicio 1 assisted-flow links into
one end-to-end flow and (only when authorized) produces a delivery.

Flow composed (no LLM, no legacy CLI, no duplicated parser):

    boundary          -> owner question packet
    connector         -> canonical ingestion_output
    semantic bridge   -> semantic candidates (SEMANTIC_CANDIDATES_READY)
    gate              -> CONTROLLED_EXECUTION_CANDIDATE_READY / NEEDS_OWNER_CONFIRMATION
    confirmation loop -> OWNER_CONFIRMATION_RECHECK_READY
    reinjection       -> re-run gate -> READY
    plan packet       -> EXECUTION_PLAN_READY
    auth dialogue     -> OWNER_AUTHORIZATION_ACCEPTED
    dry-run candidate -> CONTROLLED_DRY_RUN_CANDIDATE_READY
    validation        -> OWNER_VALIDATION_ACCEPTED
    execution result  -> CONTROLLED_EXECUTION_RESULT_READY (in-memory)
    delivery          -> DELIVERY_PACKET_READY (only if delivery_authorized)

The orchestrator delegates ALL work to the existing link modules. It performs
no XLSX parsing itself (uses the boundary/canonical reader), runs no tools, and
never writes files except through the final delivery module (which requires
explicit delivery_authorized=True).

Any missing answer or rejected/required decision BLOCKS before delivery. The
output carries a ``trace`` mapping each link name to its produced status.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1 as build_boundary,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1 as build_connector,
)
from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_semantic_bridge,
)
from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1 as build_loop,
)
from pymia.smartpyme.service_1_owner_confirmation_reinjection_to_semantic_gate_v1 import (
    build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1 as build_reinject,
)
from pymia.smartpyme.service_1_controlled_execution_ready_to_plan_packet_v1 import (
    build_service_1_controlled_execution_plan_packet_v1 as build_plan,
)
from pymia.smartpyme.service_1_plan_packet_to_owner_authorization_dialogue_v1 import (
    build_service_1_owner_authorization_dialogue_from_plan_packet_v1 as build_auth_dialogue,
)
from pymia.smartpyme.service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 import (
    build_service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 as build_dry_run_candidate,
)
from pymia.smartpyme.service_1_dry_run_candidate_to_owner_validation_dialogue_v1 import (
    build_service_1_owner_validation_dialogue_from_dry_run_candidate_v1 as build_validation,
)
from pymia.smartpyme.service_1_owner_validated_dry_run_to_controlled_execution_result_v1 import (
    build_service_1_owner_validated_dry_run_to_controlled_execution_result_v1 as build_exec_result,
)
from pymia.smartpyme.service_1_controlled_execution_result_to_delivery_packet_v1 import (
    build_service_1_controlled_execution_result_to_delivery_packet_v1 as build_delivery,
)

SCHEMA_VERSION = "SERVICE_1_ASSISTED_FLOW_ORCHESTRATOR_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "ASSISTED_FLOW_ORCHESTRATOR"

STATUS_READY = "ASSISTED_FLOW_DELIVERY_READY"
STATUS_BLOCKED = "BLOCKED"

# Stable link names for the trace.
LINK_BOUNDARY = "boundary"
LINK_CONNECTOR = "owner_confirmation_to_ingestion"
LINK_SEMANTIC_BRIDGE = "semantic_bridge"
LINK_GATE = "controlled_execution_gate"
LINK_CONFIRMATION_LOOP = "owner_confirmation_loop"
LINK_REINJECTION = "owner_confirmation_reinjection"
LINK_GATE_RECHECK = "controlled_execution_gate_recheck"
LINK_PLAN = "controlled_execution_plan"
LINK_AUTH_DIALOGUE = "owner_authorization_dialogue"
LINK_DRY_RUN_CANDIDATE = "dry_run_candidate"
LINK_VALIDATION = "owner_validation_dialogue"
LINK_EXECUTION_RESULT = "controlled_execution_result"
LINK_DELIVERY = "delivery"

_LINK_ORDER = (
    LINK_BOUNDARY,
    LINK_CONNECTOR,
    LINK_SEMANTIC_BRIDGE,
    LINK_GATE,
    LINK_CONFIRMATION_LOOP,
    LINK_REINJECTION,
    LINK_GATE_RECHECK,
    LINK_PLAN,
    LINK_AUTH_DIALOGUE,
    LINK_DRY_RUN_CANDIDATE,
    LINK_VALIDATION,
    LINK_EXECUTION_RESULT,
    LINK_DELIVERY,
)


def build_service_1_assisted_flow_orchestrator_v1(
    *,
    local_xlsx_path: Any,
    owner_column_answers: Any,
    semantic_owner_answers: Any,
    owner_authorization: str = "accept",
    owner_validation: str = "accept",
    delivery_authorized: bool = False,
    output_dir: Any = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Run the full assisted flow and (if authorized) produce a delivery.

    Args:
        local_xlsx_path: Path to the source XLSX.
        owner_column_answers: Mapping column -> answer for the column-confirmation
            step (feeds the connector).
        semantic_owner_answers: Mapping column -> answer for the ambiguous-semantic
            confirmation loop (feeds the owner confirmation loop).
        owner_authorization: "accept"/"reject"/... for the plan authorization.
        owner_validation: "accept"/"reject"/"request_changes" for the dry-run
            validation.
        delivery_authorized: Must be True for the final delivery to be written.
        output_dir: Directory where the delivery (if authorized) is written.

    Returns:
        A packet dict with status ASSISTED_FLOW_DELIVERY_READY or BLOCKED, plus a
        ``trace`` of each link's produced status and the final ``delivery_packet``.
    """
    trace: dict[str, str] = {}

    def _fail(reason: str, *, at_link: str, packet: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        if packet is not None:
            trace[at_link] = packet.get("status", "UNKNOWN")
        return {
            "schema_version": SCHEMA_VERSION,
            "service_name": SERVICE_NAME,
            "packet_type": PACKET_TYPE,
            "status": STATUS_BLOCKED,
            "blocked_reason": reason,
            "blocked_at_link": at_link,
            "trace": trace,
            "delivery_packet": None,
            "delivery_created": False,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    # 1) Boundary: XLSX -> owner question packet.
    boundary = build_boundary(local_xlsx_path=local_xlsx_path)
    trace[LINK_BOUNDARY] = boundary.get("status")
    if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
        return _fail(boundary.get("blocked_reason", "BOUNDARY_FAILED"), at_link=LINK_BOUNDARY, packet=boundary)

    # 2) Connector: answers -> canonical ingestion_output.
    connector = build_connector(owner_question_packet=boundary, owner_answers=owner_column_answers)
    trace[LINK_CONNECTOR] = connector.get("status")
    if connector.get("status") != "INGESTION_OUTPUT_READY":
        return _fail(connector.get("blocked_reason", "CONNECTOR_FAILED"), at_link=LINK_CONNECTOR, packet=connector)

    # 3) Semantic bridge.
    bridge = build_semantic_bridge(ingestion_output=connector["ingestion_output"])
    trace[LINK_SEMANTIC_BRIDGE] = bridge.get("status")
    if bridge.get("status") != "SEMANTIC_CANDIDATES_READY":
        return _fail(bridge.get("blocked_reason", "SEMANTIC_BRIDGE_FAILED"), at_link=LINK_SEMANTIC_BRIDGE, packet=bridge)

    # 4) Gate (first pass).
    gate = build_gate(semantic_bridge_packet=bridge)
    trace[LINK_GATE] = gate.get("status")
    if gate.get("status") not in ("CONTROLLED_EXECUTION_CANDIDATE_READY", "NEEDS_OWNER_CONFIRMATION"):
        return _fail(gate.get("blocked_reason", "GATE_FAILED"), at_link=LINK_GATE, packet=gate)

    # 5/6) Confirmation is conditional. A high-confidence gate may already be
    # READY; in that case there is nothing to ask or reinject. Ambiguous cases
    # still require the complete owner-confirmation loop and fail closed.
    if gate.get("status") == "CONTROLLED_EXECUTION_CANDIDATE_READY":
        trace[LINK_CONFIRMATION_LOOP] = "SKIPPED_NOT_REQUIRED"
        trace[LINK_REINJECTION] = "SKIPPED_NOT_REQUIRED"
        gate_recheck = gate
    else:
        loop = build_loop(gate_packet=gate, owner_answers=semantic_owner_answers)
        trace[LINK_CONFIRMATION_LOOP] = loop.get("status")
        if loop.get("status") != "OWNER_CONFIRMATION_RECHECK_READY":
            return _fail(loop.get("blocked_reason", "CONFIRMATION_LOOP_FAILED"), at_link=LINK_CONFIRMATION_LOOP, packet=loop)

        reinject = build_reinject(
            semantic_bridge_packet=bridge,
            owner_confirmation_loop_packet=loop,
        )
        trace[LINK_REINJECTION] = reinject.get("status")
        if reinject.get("status") != "CONTROLLED_EXECUTION_CANDIDATE_READY":
            return _fail(reinject.get("blocked_reason", "REINJECTION_FAILED"), at_link=LINK_REINJECTION, packet=reinject)
        gate_recheck = reinject

    trace[LINK_GATE_RECHECK] = gate_recheck.get("status")

    # 7) Plan packet.
    plan = build_plan(gate_packet=gate_recheck)
    trace[LINK_PLAN] = plan.get("status")
    if plan.get("status") != "EXECUTION_PLAN_READY":
        return _fail(plan.get("blocked_reason", "PLAN_FAILED"), at_link=LINK_PLAN, packet=plan)

    # 8) Authorization dialogue.
    auth = build_auth_dialogue(plan_packet=plan, owner_authorization=owner_authorization)
    trace[LINK_AUTH_DIALOGUE] = auth.get("status")
    if auth.get("status") != "OWNER_AUTHORIZATION_ACCEPTED":
        return _fail(auth.get("blocked_reason", "AUTH_FAILED"), at_link=LINK_AUTH_DIALOGUE, packet=auth)

    # 9) Dry-run candidate.
    candidate = build_dry_run_candidate(owner_authorization_dialogue_packet=auth)
    trace[LINK_DRY_RUN_CANDIDATE] = candidate.get("status")
    if candidate.get("status") != "CONTROLLED_DRY_RUN_CANDIDATE_READY":
        return _fail(candidate.get("blocked_reason", "DRY_RUN_FAILED"), at_link=LINK_DRY_RUN_CANDIDATE, packet=candidate)

    # 10) Validation dialogue.
    validation = build_validation(dry_run_candidate_packet=candidate, owner_validation=owner_validation)
    trace[LINK_VALIDATION] = validation.get("status")
    if validation.get("status") != "OWNER_VALIDATION_ACCEPTED":
        return _fail(validation.get("blocked_reason", "VALIDATION_FAILED"), at_link=LINK_VALIDATION, packet=validation)

    # 11) Controlled execution result (in-memory).
    exec_result = build_exec_result(owner_validation_dialogue_packet=validation)
    trace[LINK_EXECUTION_RESULT] = exec_result.get("status")
    if exec_result.get("status") != "CONTROLLED_EXECUTION_RESULT_READY":
        return _fail(exec_result.get("blocked_reason", "EXECUTION_FAILED"), at_link=LINK_EXECUTION_RESULT, packet=exec_result)

    # 12) Delivery (only if authorized).
    delivery = build_delivery(
        controlled_execution_result_packet=exec_result,
        output_dir=output_dir,
        delivery_authorized=delivery_authorized,
    )
    trace[LINK_DELIVERY] = delivery.get("status")

    if delivery.get("status") != "DELIVERY_PACKET_READY":
        return {
            "schema_version": SCHEMA_VERSION,
            "service_name": SERVICE_NAME,
            "packet_type": PACKET_TYPE,
            "status": STATUS_BLOCKED,
            "blocked_reason": delivery.get("blocked_reason", "DELIVERY_FAILED"),
            "blocked_at_link": LINK_DELIVERY,
            "trace": trace,
            "delivery_packet": delivery,
            "delivery_created": False,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": bool(delivery_authorized),
            "diagnosis_generated": False,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "blocked_at_link": None,
        "trace": trace,
        "delivery_packet": delivery,
        "delivery_created": bool(delivery.get("delivery_created")),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": bool(delivery.get("product_ready")),
        "delivery_authorized": bool(delivery.get("delivery_authorized")),
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "LINK_BOUNDARY",
    "LINK_CONNECTOR",
    "LINK_SEMANTIC_BRIDGE",
    "LINK_GATE",
    "LINK_CONFIRMATION_LOOP",
    "LINK_REINJECTION",
    "LINK_GATE_RECHECK",
    "LINK_PLAN",
    "LINK_AUTH_DIALOGUE",
    "LINK_DRY_RUN_CANDIDATE",
    "LINK_VALIDATION",
    "LINK_EXECUTION_RESULT",
    "LINK_DELIVERY",
    "build_service_1_assisted_flow_orchestrator_v1",
]

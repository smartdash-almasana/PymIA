"""Single product application root for Servicio 1.

Connects the canonical deterministic semantic pipeline to the existing
physical First Aid pipeline. It does not parse files, infer tools, or duplicate
delivery logic.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    STATUS_OWNER_FOLLOWUP,
    STATUS_OWNER_QUESTIONS,
    STATUS_READY_FOR_COMPUTATION,
    build_computation_plan,
    run_initial_pass,
    run_owner_reentry,
)
from pymia.smartpyme.service_1_pipeline_v1 import (
    Service1PipelineToolRequestV1,
    run_service_1_pipeline_v1,
)

SCHEMA_VERSION = "SERVICE_1_PRODUCT_PIPELINE_V1"
STATUS_READY = "PRODUCT_PIPELINE_READY"
STATUS_COMPUTATION_PLAN_READY = "COMPUTATION_PLAN_READY"
STATUS_NEEDS_OWNER = "NEEDS_OWNER_CONFIRMATION"
STATUS_BLOCKED = "BLOCKED"


def run_service_1_product_pipeline_v1(
    *,
    ingestion_output: Any,
    tool_requests: Sequence[Service1PipelineToolRequestV1],
    output_dir: str | Path,
    sheet_name: str = "sheet1",
    owner_answers: Any = None,
    requested_capability: str | None = None,
) -> dict[str, Any]:
    """Run semantic confirmation before planning or explicit tool execution.

    When ``requested_capability`` is provided, the pipeline stops at the
    governed P7/P8 computation plan and executes no tool. Without it, the
    previously certified explicit-tool path remains unchanged.
    """
    semantic_run = run_initial_pass(
        ingestion_output=ingestion_output,
        sheet_name=sheet_name,
    )

    if semantic_run.get("status") == STATUS_OWNER_QUESTIONS:
        if not isinstance(owner_answers, dict) or not owner_answers:
            return _packet(
                status=STATUS_NEEDS_OWNER,
                semantic_run=semantic_run,
                owner_questions=list(semantic_run.get("owner_questions") or []),
            )
        semantic_run = run_owner_reentry(
            previous_run=semantic_run,
            owner_answers=owner_answers,
        )
        if semantic_run.get("status") == STATUS_OWNER_FOLLOWUP:
            return _packet(
                status=STATUS_NEEDS_OWNER,
                semantic_run=semantic_run,
                owner_questions=list(semantic_run.get("owner_questions") or []),
                owner_followup=list(semantic_run.get("owner_followup") or []),
            )

    if semantic_run.get("status") != STATUS_CONFIRMED_BINDINGS:
        return _packet(
            status=STATUS_BLOCKED,
            blocked_reason=semantic_run.get("blocked_reason")
            or "SEMANTIC_BINDINGS_NOT_CONFIRMED",
            semantic_run=semantic_run,
        )

    if requested_capability is not None:
        computation_plan = build_computation_plan(
            confirmed_bindings=semantic_run,
            requested_capability=requested_capability,
        )
        if computation_plan.get("status") != STATUS_READY_FOR_COMPUTATION:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason=computation_plan.get("blocked_reason")
                or computation_plan.get("status")
                or "COMPUTATION_PLAN_BLOCKED",
                semantic_run=semantic_run,
                computation_plan=computation_plan,
            )
        return _packet(
            status=STATUS_COMPUTATION_PLAN_READY,
            semantic_run=semantic_run,
            computation_plan=computation_plan,
        )

    physical_run = run_service_1_pipeline_v1(
        tool_requests=tool_requests,
        output_dir=output_dir,
    )
    return _packet(
        status=STATUS_READY,
        semantic_run=semantic_run,
        physical_run=physical_run,
    )


def _packet(
    *,
    status: str,
    blocked_reason: str | None = None,
    semantic_run: Any = None,
    physical_run: Any = None,
    computation_plan: Any = None,
    owner_questions: list[dict[str, Any]] | None = None,
    owner_followup: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "status": status,
        "blocked_reason": blocked_reason,
        "semantic_run": _public_semantic_run(semantic_run),
        "physical_run": physical_run,
        "computation_plan": computation_plan,
        "owner_questions": list(owner_questions or []),
        "owner_followup": [dict(item) for item in (owner_followup or [])],
        "semantic_bindings_confirmed": bool(
            isinstance(semantic_run, dict)
            and semantic_run.get("status") == STATUS_CONFIRMED_BINDINGS
        ),
        "tools_executed": bool(isinstance(physical_run, dict)),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _public_semantic_run(semantic_run: Any) -> dict[str, Any] | None:
    """Project the internal semantic trace onto the product-safe surface."""
    if not isinstance(semantic_run, dict):
        return None
    return {
        "schema_version": semantic_run.get("schema_version"),
        "service_name": semantic_run.get("service_name"),
        "status": semantic_run.get("status"),
        "blocked_reason": semantic_run.get("blocked_reason"),
        "owner_questions": list(semantic_run.get("owner_questions") or []),
        "owner_followup": [
            dict(item) for item in (semantic_run.get("owner_followup") or [])
        ],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_COMPUTATION_PLAN_READY",
    "STATUS_NEEDS_OWNER",
    "STATUS_BLOCKED",
    "run_service_1_product_pipeline_v1",
]

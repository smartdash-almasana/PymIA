"""Single product application root for Servicio 1."""
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
from pymia.smartpyme.service_1_liq_001_evaluator_v1 import (
    CAPABILITY_REF as LIQ_001_CAPABILITY_REF,
    STATUS_EVALUATED as LIQ_001_STATUS_EVALUATED,
    evaluate_liq_001_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_liq_001_outcome_v1 import (
    STATUS_READY as LIQ_001_OUTCOME_READY,
    build_liq_001_outcome_v1,
    deliver_liq_001_outcome_xlsx_v1,
)
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_EVALUATED as GENERIC_STATUS_EVALUATED,
    execute_generic_capability_v1,
)
from pymia.smartpyme.service_1_liq_002_evaluator_v1 import (
    CAPABILITY_REF as LIQ_002_CAPABILITY_REF,
)
from pymia.smartpyme.service_1_pipeline_v1 import (
    Service1PipelineToolRequestV1,
    run_service_1_pipeline_v1,
)
from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import (
    CAPABILITY_REF as PYME_011_CAPABILITY_REF,
)
from pymia.smartpyme.service_1_ren_001_evaluator_v1 import (
    CAPABILITY_REF as REN_001_CAPABILITY_REF,
    STATUS_EVALUATED as REN_001_STATUS_EVALUATED,
)
from pymia.smartpyme.service_1_ren_001_normalized_evidence_v1 import (
    evaluate_ren_001_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_ren_001_outcome_v1 import (
    STATUS_READY as REN_001_OUTCOME_READY,
    build_ren_001_outcome_v1,
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
    deliver_result: bool = False,
) -> dict[str, Any]:
    semantic_run = run_initial_pass(ingestion_output=ingestion_output, sheet_name=sheet_name)

    if semantic_run.get("status") == STATUS_OWNER_QUESTIONS:
        if not isinstance(owner_answers, dict) or not owner_answers:
            return _packet(
                status=STATUS_NEEDS_OWNER,
                semantic_run=semantic_run,
                owner_questions=list(semantic_run.get("owner_questions") or []),
            )
        semantic_run = run_owner_reentry(previous_run=semantic_run, owner_answers=owner_answers)
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
            blocked_reason=semantic_run.get("blocked_reason") or "SEMANTIC_BINDINGS_NOT_CONFIRMED",
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

        computation_result = None
        bounded_outcome = None
        delivery_result = None
        evidence = ingestion_output if isinstance(ingestion_output, dict) else {}
        normalized_tables = evidence.get("normalized_tables")
        column_refs = evidence.get("column_refs")
        has_complete_row_evidence = (
            isinstance(normalized_tables, list)
            and bool(normalized_tables)
            and isinstance(column_refs, list)
            and bool(column_refs)
        )

        if requested_capability == LIQ_001_CAPABILITY_REF and has_complete_row_evidence:
            computation_result = evaluate_liq_001_from_normalized_tables_v1(
                computation_plan=computation_plan,
                normalized_tables=normalized_tables,
                column_refs=column_refs,
            )
            if computation_result.get("status") != LIQ_001_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "LIQ_001_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                )
            bounded_outcome = build_liq_001_outcome_v1(computation_result=computation_result)
            if bounded_outcome.get("status") != LIQ_001_OUTCOME_READY:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "LIQ_001_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                delivery_result = deliver_liq_001_outcome_xlsx_v1(
                    outcome=bounded_outcome,
                    output_dir=output_dir,
                )
                if delivery_result.get("status") != "DELIVERED":
                    return _packet(
                        status=STATUS_BLOCKED,
                        blocked_reason=delivery_result.get("blocked_reason") or "LIQ_001_DELIVERY_BLOCKED",
                        semantic_run=semantic_run,
                        computation_plan=computation_plan,
                        computation_result=computation_result,
                        bounded_outcome=bounded_outcome,
                        delivery_result=delivery_result,
                    )

        elif requested_capability == REN_001_CAPABILITY_REF and has_complete_row_evidence:
            computation_result = evaluate_ren_001_from_normalized_tables_v1(
                computation_plan=computation_plan,
                normalized_tables=normalized_tables,
                column_refs=column_refs,
            )
            if computation_result.get("status") != REN_001_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "REN_001_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                )
            bounded_outcome = build_ren_001_outcome_v1(computation_result=computation_result)
            if bounded_outcome.get("status") != REN_001_OUTCOME_READY:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "REN_001_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason="REN_001_DELIVERY_NOT_AUTHORIZED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )

        elif requested_capability == LIQ_002_CAPABILITY_REF and has_complete_row_evidence:
            computation_result = execute_generic_capability_v1(
                capability_ref=requested_capability,
                computation_plan=computation_plan,
                normalized_tables=normalized_tables,
                column_refs=column_refs,
            )
            if computation_result.get("status") != GENERIC_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "LIQ_002_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                )
            bounded_outcome = computation_result["outcome"]
            if bounded_outcome.get("status") != "OUTCOME_READY":
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "LIQ_002_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason="LIQ_002_DELIVERY_NOT_AUTHORIZED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )

        elif requested_capability == PYME_011_CAPABILITY_REF and has_complete_row_evidence:
            computation_result = execute_generic_capability_v1(
                capability_ref=requested_capability,
                computation_plan=computation_plan,
                normalized_tables=normalized_tables,
                column_refs=column_refs,
            )
            if computation_result.get("status") != GENERIC_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "PYME_011_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                )
            bounded_outcome = computation_result["outcome"]
            if bounded_outcome.get("status") != "OUTCOME_READY":
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "PYME_011_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason="PYME_011_DELIVERY_NOT_AUTHORIZED",
                    semantic_run=semantic_run,
                    computation_plan=computation_plan,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )

        return _packet(
            status=STATUS_COMPUTATION_PLAN_READY,
            semantic_run=semantic_run,
            computation_plan=computation_plan,
            computation_result=computation_result,
            bounded_outcome=bounded_outcome,
            delivery_result=delivery_result,
        )

    if deliver_result:
        return _packet(
            status=STATUS_BLOCKED,
            blocked_reason="DELIVERY_REQUIRES_REQUESTED_CAPABILITY",
            semantic_run=semantic_run,
        )

    physical_run = run_service_1_pipeline_v1(tool_requests=tool_requests, output_dir=output_dir)
    return _packet(status=STATUS_READY, semantic_run=semantic_run, physical_run=physical_run)


def _packet(
    *,
    status: str,
    blocked_reason: str | None = None,
    semantic_run: Any = None,
    physical_run: Any = None,
    computation_plan: Any = None,
    computation_result: Any = None,
    bounded_outcome: Any = None,
    delivery_result: Any = None,
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
        "computation_result": computation_result,
        "bounded_outcome": bounded_outcome,
        "delivery_result": delivery_result,
        "owner_questions": list(owner_questions or []),
        "owner_followup": [dict(item) for item in (owner_followup or [])],
        "semantic_bindings_confirmed": bool(
            isinstance(semantic_run, dict) and semantic_run.get("status") == STATUS_CONFIRMED_BINDINGS
        ),
        "tools_executed": bool(isinstance(physical_run, dict)),
        "computation_executed": bool(
            isinstance(computation_result, dict)
            and computation_result.get("status")
            in {
                LIQ_001_STATUS_EVALUATED,
                REN_001_STATUS_EVALUATED,
                GENERIC_STATUS_EVALUATED,
            }
        ),
        "bounded_finding_generated": bool(
            isinstance(bounded_outcome, dict)
            and bounded_outcome.get("bounded_finding_generated") is True
        ),
        "delivery_generated": bool(
            isinstance(delivery_result, dict) and delivery_result.get("status") == "DELIVERED"
        ),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _public_semantic_run(semantic_run: Any) -> dict[str, Any] | None:
    if not isinstance(semantic_run, dict):
        return None
    return {
        "schema_version": semantic_run.get("schema_version"),
        "service_name": semantic_run.get("service_name"),
        "status": semantic_run.get("status"),
        "blocked_reason": semantic_run.get("blocked_reason"),
        "owner_questions": list(semantic_run.get("owner_questions") or []),
        "owner_followup": [dict(item) for item in (semantic_run.get("owner_followup") or [])],
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

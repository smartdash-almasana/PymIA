"""Focal tests for SERVICE_1_SEMANTIC_RUNTIME_PLAN_CANDIDATE_V1."""
from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_bounded_engine_to_allowed_computation_adapter_v1 import (
    ADAPTER_READY,
    Service1BoundedEngineToAllowedComputationAdapterResultV1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    STATUS_NEEDS_EVIDENCE,
    STATUS_READY_FOR_COMPUTATION_PLAN,
    Service1AllowedComputationCandidateV1,
)
from pymia.smartpyme.service_1_semantic_runtime_plan_candidate_v1 import (
    PLAN_BLOCKED_BY_ADAPTER,
    PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE,
    PLAN_BLOCKED_BY_GUARD,
    PLAN_BLOCKED_BY_POLICY,
    PLAN_READY_CANDIDATE,
    Service1SemanticRuntimePlanCandidateV1,
    build_service_1_semantic_runtime_plan_candidate_v1,
)

_MISSING = object()


def _candidate(
    *,
    ready: bool = True,
    computation_ref: str | None = "first_aid_precio_margen_basico_v1",
    guard_open: bool = False,
) -> Service1AllowedComputationCandidateV1:
    status = STATUS_READY_FOR_COMPUTATION_PLAN if ready else STATUS_NEEDS_EVIDENCE
    return Service1AllowedComputationCandidateV1(
        schema_version="SERVICE_1_PATHOLOGY_TO_ALLOWED_COMPUTATION_CANDIDATE_V1",
        service_name="SERVICE_1",
        pathology_code="REN_001",
        status=status,
        allowed_computation_ref=computation_ref,
        required_fields=("precio_venta", "costo_unitario", "volumen_vendido"),
        available_fields=("precio_venta", "costo_unitario", "volumen_vendido") if ready else ("precio_venta",),
        missing_fields=() if ready else ("costo_unitario", "volumen_vendido"),
        readiness_status=status,
        blocked_reason=None if ready else "missing_required_fields",
        runtime_authorized=guard_open,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )


def _adapter(
    *,
    ready: bool = True,
    prepared: bool | None = None,
    candidate: Service1AllowedComputationCandidateV1 | None | object = _MISSING,
    guard_open: bool = False,
    policy_violation: bool = False,
) -> Service1BoundedEngineToAllowedComputationAdapterResultV1:
    if prepared is None:
        prepared = ready
    resolved_candidate = _candidate() if candidate is _MISSING and ready else None if candidate is _MISSING else candidate
    return Service1BoundedEngineToAllowedComputationAdapterResultV1(
        pathology_code="REN_001",
        adapter_status=ADAPTER_READY if ready else "SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_BLOCKED_BY_ENGINE",
        engine_status="SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE" if ready else "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT",
        allowed_computation_candidate=resolved_candidate,
        adapter_prepared=prepared,
        runtime_authorized=guard_open,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        blocking_layer=None if ready else "bounded_engine",
        blocking_reasons=() if ready else ("bounded_engine_not_ready",),
        metadata={"policy_violation": True} if policy_violation else {},
    )


def _build(adapter=None):
    return build_service_1_semantic_runtime_plan_candidate_v1(adapter or _adapter())


def _assert_fail_closed(result: Service1SemanticRuntimePlanCandidateV1) -> None:
    assert result.computation_execution_allowed is False
    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False


def test_ready_adapter_prepares_plan_candidate_without_execution() -> None:
    result = _build()
    assert result.plan_status == PLAN_READY_CANDIDATE
    assert result.semantic_runtime_plan_prepared is True
    assert result.allowed_computation_ref == "first_aid_precio_margen_basico_v1"
    assert result.pathology_code == "REN_001"
    assert result.blocking_layer is None
    _assert_fail_closed(result)


def test_blocks_when_adapter_status_not_ready() -> None:
    result = _build(_adapter(ready=False, candidate=None))
    assert result.plan_status == PLAN_BLOCKED_BY_ADAPTER
    assert result.semantic_runtime_plan_prepared is False
    _assert_fail_closed(result)


def test_blocks_when_adapter_not_prepared() -> None:
    result = _build(_adapter(ready=True, prepared=False))
    assert result.plan_status == PLAN_BLOCKED_BY_ADAPTER
    assert result.blocking_reasons == ("adapter_not_prepared",)
    _assert_fail_closed(result)


def test_blocks_when_computation_candidate_missing() -> None:
    result = _build(_adapter(ready=True, candidate=None))
    assert result.plan_status == PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE
    assert result.semantic_runtime_plan_prepared is False
    _assert_fail_closed(result)


def test_blocks_when_computation_candidate_needs_evidence() -> None:
    result = _build(_adapter(candidate=_candidate(ready=False)))
    assert result.plan_status == PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE
    assert result.blocking_reasons == ("allowed_computation_candidate_not_ready",)
    _assert_fail_closed(result)


def test_blocks_when_allowed_computation_ref_missing() -> None:
    result = _build(_adapter(candidate=_candidate(computation_ref=None)))
    assert result.plan_status == PLAN_BLOCKED_BY_COMPUTATION_CANDIDATE
    assert result.blocking_reasons == ("allowed_computation_ref_missing",)
    _assert_fail_closed(result)


def test_blocks_policy_violation() -> None:
    result = _build(_adapter(policy_violation=True))
    assert result.plan_status == PLAN_BLOCKED_BY_POLICY
    assert result.blocking_layer == "policy"
    _assert_fail_closed(result)


def test_blocks_adapter_guard_open() -> None:
    result = _build(_adapter(guard_open=True))
    assert result.plan_status == PLAN_BLOCKED_BY_GUARD
    assert result.blocking_layer == "adapter_guard"
    _assert_fail_closed(result)


def test_blocks_allowed_computation_guard_open() -> None:
    result = _build(_adapter(candidate=_candidate(guard_open=True)))
    assert result.plan_status == PLAN_BLOCKED_BY_GUARD
    assert result.blocking_layer == "allowed_computation_guard"
    _assert_fail_closed(result)


def test_plan_prepared_true_only_for_ready_candidate() -> None:
    ready = _build()
    blocked = [
        _build(_adapter(ready=False, candidate=None)),
        _build(_adapter(ready=True, prepared=False)),
        _build(_adapter(candidate=None)),
        _build(_adapter(candidate=_candidate(ready=False))),
        _build(_adapter(candidate=_candidate(computation_ref=None))),
        _build(_adapter(policy_violation=True)),
        _build(_adapter(guard_open=True)),
        _build(_adapter(candidate=_candidate(guard_open=True))),
    ]
    assert ready.semantic_runtime_plan_prepared is True
    for result in blocked:
        assert result.semantic_runtime_plan_prepared is False
        assert result.plan_status != PLAN_READY_CANDIDATE
        _assert_fail_closed(result)


def test_product_module_has_no_forbidden_runtime_paths() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_semantic_runtime_plan_candidate_v1.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = [
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "pymia.cli",
        "CASE_001",
    ]
    for pattern in forbidden:
        assert pattern not in content

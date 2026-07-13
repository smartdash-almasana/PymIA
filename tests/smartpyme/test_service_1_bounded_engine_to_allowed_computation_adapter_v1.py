from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_bounded_engine_to_allowed_computation_adapter_v1 import (
    ADAPTER_BLOCKED_BY_ENGINE,
    ADAPTER_BLOCKED_BY_GUARD,
    ADAPTER_READY,
    build_service_1_bounded_engine_to_allowed_computation_adapter_v1,
)
from pymia.smartpyme.service_1_bounded_semantic_engine_implementation_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE,
    Service1BoundedSemanticEngineResultV1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_contract_v1 import (
    PATHOLOGY_REN_001,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    STATUS_NEEDS_EVIDENCE,
    STATUS_READY_FOR_COMPUTATION_PLAN,
)


def _engine(
    *,
    ready: bool = True,
    prepared: bool | None = None,
    execution_allowed: bool = False,
    execution_performed: bool = False,
    runtime_allowed: bool = False,
    phase_5_allowed: bool = False,
    product_ready: bool = False,
    delivery_allowed: bool = False,
) -> Service1BoundedSemanticEngineResultV1:
    if prepared is None:
        prepared = ready
    return Service1BoundedSemanticEngineResultV1(
        pathology_code=PATHOLOGY_REN_001,
        engine_status=(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE
            if ready
            else "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT"
        ),
        contract_status=(
            "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE"
            if ready
            else "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT"
        ),
        bounded_semantic_engine_candidate_prepared=prepared,
        bounded_semantic_engine_execution_allowed=execution_allowed,
        execution_performed=execution_performed,
        runtime_allowed=runtime_allowed,
        phase_5_allowed=phase_5_allowed,
        product_ready=product_ready,
        delivery_allowed=delivery_allowed,
    )


def _build(engine_result=None, **kwargs):
    return build_service_1_bounded_engine_to_allowed_computation_adapter_v1(
        engine_result=engine_result or _engine(),
        available_data_fields=kwargs.get("available_data_fields", ["precio", "costo", "cantidad"]),
        missing_evidence_items=kwargs.get("missing_evidence_items", []),
        business_period_reference=kwargs.get("business_period_reference", "2026-07"),
    )


def test_ready_engine_builds_existing_allowed_computation_candidate() -> None:
    result = _build()
    assert result.adapter_status == ADAPTER_READY
    assert result.adapter_prepared is True
    assert result.allowed_computation_candidate is not None
    assert result.allowed_computation_candidate.status == STATUS_READY_FOR_COMPUTATION_PLAN
    assert result.allowed_computation_candidate.allowed_computation_ref == "first_aid_precio_margen_basico_v1"


def test_missing_evidence_is_delegated_to_existing_candidate() -> None:
    result = _build(available_data_fields=["precio", "costo"])
    assert result.adapter_status == ADAPTER_READY
    assert result.allowed_computation_candidate is not None
    assert result.allowed_computation_candidate.status == STATUS_NEEDS_EVIDENCE
    assert "volumen_vendido" in result.allowed_computation_candidate.missing_fields


def test_blocks_when_engine_not_ready() -> None:
    result = _build(_engine(ready=False))
    assert result.adapter_status == ADAPTER_BLOCKED_BY_ENGINE
    assert result.adapter_prepared is False
    assert result.allowed_computation_candidate is None


def test_blocks_when_engine_candidate_not_prepared() -> None:
    result = _build(_engine(ready=True, prepared=False))
    assert result.adapter_status == ADAPTER_BLOCKED_BY_ENGINE
    assert result.blocking_reasons == ("bounded_engine_candidate_not_prepared",)


def test_blocks_any_open_upstream_guard() -> None:
    guarded = [
        _engine(execution_allowed=True),
        _engine(execution_performed=True),
        _engine(runtime_allowed=True),
        _engine(phase_5_allowed=True),
        _engine(product_ready=True),
        _engine(delivery_allowed=True),
    ]
    for engine_result in guarded:
        result = _build(engine_result)
        assert result.adapter_status == ADAPTER_BLOCKED_BY_GUARD
        assert result.adapter_prepared is False
        assert result.allowed_computation_candidate is None


def test_adapter_and_nested_candidate_never_authorize_execution_or_delivery() -> None:
    result = _build()
    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    candidate = result.allowed_computation_candidate
    assert candidate is not None
    assert candidate.runtime_authorized is False
    assert candidate.reexecution_authorized is False
    assert candidate.recalculation_authorized is False
    assert candidate.delivery_authorized is False


def test_product_module_has_no_runtime_cli_mapper_or_case_fixture_imports() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_bounded_engine_to_allowed_computation_adapter_v1.py"
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

"""Focal tests for SERVICE_1_SEMANTIC_PLAN_TO_XLSX_BRIDGE_COMPOSITION_V1."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pymia.smartpyme.service_1_owner_confirmation_boundary_v1 import (
    OWNER_CONFIRMED,
    OWNER_CONFIRMATION_REQUIRED,
    Service1OwnerConfirmationResultV1,
)
from pymia.smartpyme.service_1_semantic_plan_to_xlsx_bridge_composition_v1 import (
    STATUS_BLOCKED_BY_GUARD,
    STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
    STATUS_BLOCKED_BY_SEMANTIC_PLAN,
    STATUS_BLOCKED_BY_XLSX_BRIDGE,
    STATUS_COMPOSITION_CANDIDATE_READY,
    Service1SemanticPlanToXlsxBridgeCompositionV1,
    build_service_1_semantic_plan_to_xlsx_bridge_composition_v1,
)
from pymia.smartpyme.service_1_semantic_runtime_plan_candidate_v1 import (
    PLAN_BLOCKED_BY_ADAPTER,
    PLAN_READY_CANDIDATE,
    Service1SemanticRuntimePlanCandidateV1,
)
from pymia.smartpyme.service_1_xlsx_runtime_bridge_v1 import (
    STATUS_BRIDGE_BLOCKED,
    STATUS_BRIDGE_NEXT_OWNER_QUESTION,
    STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
    Service1XlsxRuntimeBridgeV1,
)


def _plan(*, ready: bool = True) -> Service1SemanticRuntimePlanCandidateV1:
    return Service1SemanticRuntimePlanCandidateV1(
        pathology_code="REN_001",
        plan_status=PLAN_READY_CANDIDATE if ready else PLAN_BLOCKED_BY_ADAPTER,
        adapter_status="SERVICE_1_BOUNDED_ENGINE_TO_ALLOWED_COMPUTATION_ADAPTER_READY",
        allowed_computation_ref="first_aid_precio_margen_basico_v1" if ready else None,
        required_fields=("precio_venta", "costo_unitario", "volumen_vendido"),
        available_fields=("precio_venta", "costo_unitario", "volumen_vendido") if ready else (),
        missing_fields=(),
        semantic_runtime_plan_prepared=ready,
        computation_execution_allowed=False,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        phase_5_allowed=False,
        product_ready=False,
        blocking_layer=None if ready else "adapter",
        blocking_reasons=() if ready else ("adapter_not_ready",),
        metadata={"rule": "ready" if ready else "adapter_not_ready"},
    )


def _bridge(
    *,
    status: str = STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
    owner_confirmation_required: bool = False,
    computation_ref: str | None = "first_aid_precio_margen_basico_v1",
) -> Service1XlsxRuntimeBridgeV1:
    return Service1XlsxRuntimeBridgeV1(
        schema_version="SERVICE_1_XLSX_RUNTIME_BRIDGE_V1",
        service_name="SERVICE_1",
        status=status,
        case_id="case_s1_001",
        tenant_id="tenant_demo",
        intake_id="intake_001",
        run_id="run_001",
        owner_ref="owner_demo",
        source_file_ref="ventas.xlsx",
        entrypoint_status="DELIVERY_PACKAGE_CANDIDATE_READY",
        pilot_pack_status="REAL_CLIENT_XLSX_FIRST_PILOT_PACK_READY",
        selected_primary_pathology="REN_001",
        allowed_computation_ref=computation_ref,
        next_owner_question="Confirmar columnas" if status == STATUS_BRIDGE_NEXT_OWNER_QUESTION else None,
        package_candidate_ref="pkg_001" if status == STATUS_BRIDGE_PACKAGE_CANDIDATE_READY else None,
        blocked_reason="blocked" if status == STATUS_BRIDGE_BLOCKED else None,
        owner_confirmation_required=owner_confirmation_required,
        entrypoint_result=None,
        pilot_pack_result=None,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={"parser_invoked": False},
    )


def _owner(*, confirmed: bool = True) -> Service1OwnerConfirmationResultV1:
    return Service1OwnerConfirmationResultV1(
        pathology_code="REN_001",
        confirmation_status=OWNER_CONFIRMED if confirmed else OWNER_CONFIRMATION_REQUIRED,
        confirmed_evidence=("precio_venta", "costo_unitario", "volumen_vendido") if confirmed else ("precio_venta",),
        missing_confirmed_evidence=() if confirmed else ("costo_unitario", "volumen_vendido"),
        confirmed_semantic_bindings=("precio_venta", "costo_unitario", "volumen_vendido") if confirmed else (),
        missing_semantic_bindings=() if confirmed else ("precio_venta", "costo_unitario"),
        runtime_allowed=False,
        phase_5_allowed=False,
        metadata={"rule": "confirmed" if confirmed else "required"},
    )


def _build(
    *,
    plan: Service1SemanticRuntimePlanCandidateV1 | None = None,
    bridge: Service1XlsxRuntimeBridgeV1 | None = None,
    owner: Service1OwnerConfirmationResultV1 | None = None,
) -> Service1SemanticPlanToXlsxBridgeCompositionV1:
    return build_service_1_semantic_plan_to_xlsx_bridge_composition_v1(
        semantic_plan=plan or _plan(),
        xlsx_bridge=bridge or _bridge(),
        owner_confirmation=owner or _owner(),
    )


def _assert_fail_closed(result: Service1SemanticPlanToXlsxBridgeCompositionV1) -> None:
    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.product_ready is False


def test_ready_semantic_plan_and_ready_xlsx_bridge_prepare_composition_candidate() -> None:
    result = _build()

    assert result.composition_status == STATUS_COMPOSITION_CANDIDATE_READY
    assert result.composition_candidate_prepared is True
    assert result.semantic_plan_ready is True
    assert result.xlsx_bridge_ready is True
    assert result.owner_confirmed is True
    assert result.owner_confirmation_required is False
    assert result.allowed_computation_ref == "first_aid_precio_margen_basico_v1"
    assert result.package_candidate_ref == "pkg_001"
    _assert_fail_closed(result)


def test_semantic_plan_blocked_blocks_composition() -> None:
    result = _build(plan=_plan(ready=False))

    assert result.composition_status == STATUS_BLOCKED_BY_SEMANTIC_PLAN
    assert result.composition_candidate_prepared is False
    assert result.blocking_layer == "semantic_plan"
    assert result.blocking_reasons == ("semantic_plan_not_ready",)
    _assert_fail_closed(result)


def test_xlsx_bridge_blocked_blocks_composition() -> None:
    result = _build(bridge=_bridge(status=STATUS_BRIDGE_BLOCKED))

    assert result.composition_status == STATUS_BLOCKED_BY_XLSX_BRIDGE
    assert result.composition_candidate_prepared is False
    assert result.blocking_layer == "xlsx_bridge"
    assert result.blocking_reasons == ("xlsx_bridge_not_ready",)
    _assert_fail_closed(result)


def test_xlsx_bridge_next_owner_question_blocks_as_owner_confirmation_required() -> None:
    result = _build(bridge=_bridge(status=STATUS_BRIDGE_NEXT_OWNER_QUESTION))

    assert result.composition_status == STATUS_BLOCKED_BY_OWNER_CONFIRMATION
    assert result.owner_confirmation_required is True
    assert result.next_owner_question == "Confirmar columnas"
    assert result.blocking_reasons == ("xlsx_bridge_requires_owner_confirmation",)
    _assert_fail_closed(result)


def test_owner_confirmation_required_blocks_composition() -> None:
    result = _build(owner=_owner(confirmed=False))

    assert result.composition_status == STATUS_BLOCKED_BY_OWNER_CONFIRMATION
    assert result.owner_confirmation_required is True
    assert result.blocking_layer == "owner_confirmation"
    assert result.blocking_reasons == ("owner_not_confirmed",)
    _assert_fail_closed(result)


def test_bridge_owner_confirmation_flag_blocks_even_with_confirmed_owner() -> None:
    result = _build(bridge=_bridge(owner_confirmation_required=True))

    assert result.composition_status == STATUS_BLOCKED_BY_OWNER_CONFIRMATION
    assert result.blocking_layer == "xlsx_bridge_owner_confirmation"
    assert result.blocking_reasons == ("xlsx_bridge_owner_confirmation_required",)
    _assert_fail_closed(result)


def test_guard_open_blocks_composition_before_ready_state() -> None:
    result = _build(plan=replace(_plan(), runtime_authorized=True))

    assert result.composition_status == STATUS_BLOCKED_BY_GUARD
    assert result.composition_candidate_prepared is False
    assert result.blocking_layer == "guard"
    assert result.blocking_reasons == ("semantic_plan_runtime_authorized",)
    _assert_fail_closed(result)


def test_allowed_computation_ref_mismatch_blocks_composition() -> None:
    result = _build(bridge=_bridge(computation_ref="another_computation"))

    assert result.composition_status == STATUS_BLOCKED_BY_XLSX_BRIDGE
    assert result.blocking_layer == "allowed_computation_ref"
    assert result.blocking_reasons == ("allowed_computation_ref_mismatch",)
    _assert_fail_closed(result)


def test_product_module_has_no_runtime_or_parser_imports() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_semantic_plan_to_xlsx_bridge_composition_v1.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = [
        "pymia.cli",
        "document_ingestion",
        "xlsx_to_normalized",
        "excel_lab_ingestion",
        "service_1_xlsx_runtime_bridge_contract_v1",
        "runtime_authorized=True",
        '"runtime_authorized": True',
        "delivery_authorized=True",
        "product_ready=True",
        "CASE_001",
    ]
    for pattern in forbidden:
        assert pattern not in content

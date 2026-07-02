from __future__ import annotations

from dataclasses import replace

from pymia.contracts.column_confirmation_v1 import CalculationRelevance, ColumnConfirmationEntry, ColumnConfirmationMatrix, ConfirmationStatus
from pymia.smartpyme.service_1_candidate_tools_to_controlled_execution_bridge_v1 import build_service_1_candidate_tools_to_controlled_execution_bridge_v1
from pymia.smartpyme.service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1 import (
    BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES,
    BLOCKED_UNSAFE_RUNTIME_FLAGS,
    NEEDS_EVIDENCE,
    NO_CANDIDATE_TOOLS,
    SUPERVISED_DRY_RUN_PLAN_READY,
    build_service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1,
)
from pymia.smartpyme.service_1_evidence_profile_to_candidate_tools_contract_v1 import build_service_1_evidence_profile_to_candidate_tools_v1
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import build_service_1_owner_rectified_evidence_profile_v1


def _entry(header: str, function: str) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=header,
        sheet_name="Ventas",
        suggested_semantic_role="unknown",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        owner_confirmed_role=function,
        owner_rectified_function=function,
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )


def _controlled(entries: list[ColumnConfirmationEntry]):
    profile = build_service_1_owner_rectified_evidence_profile_v1(
        matrix=ColumnConfirmationMatrix(file_name="pyme.xlsx", entries=entries),
        case_ref="CASE-DRY-RUN-001",
    )
    tools = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)
    return build_service_1_candidate_tools_to_controlled_execution_bridge_v1(
        candidate_tools_result=tools,
        operator_ref="OP-1",
        execution_window_ref="WIN-1",
    )


def _plan(controlled):
    return build_service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1(
        controlled_execution_candidates_result=controlled,
    )


def test_ready_controlled_candidate_builds_supervised_dry_run_plan_without_authorization() -> None:
    result = _plan(_controlled([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ]))

    assert result.status == SUPERVISED_DRY_RUN_PLAN_READY
    assert result.ready is True
    assert len(result.ordered_candidate_steps) == 1
    assert result.ordered_candidate_steps[0].tool_ref == "precio_margen_basico"
    assert "CONFIRM_NO_REAL_EXECUTION" in result.required_manual_confirmations
    assert result.dry_run_required is True
    assert result.execution_authorized is False
    assert result.execution_executed is False
    assert result.tool_execution_authorized is False
    assert result.pipeline_authorized is False
    assert result.delivery_authorized is False


def test_multiple_candidates_build_sorted_steps() -> None:
    result = _plan(_controlled([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
        _entry("Stock", "stock"),
        _entry("Fecha", "fecha"),
        _entry("Cobro", "cobro"),
    ]))

    assert [step.tool_ref for step in result.ordered_candidate_steps] == [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
    ]
    assert [step.step_order for step in result.ordered_candidate_steps] == [1, 2, 3]


def test_needs_evidence_is_propagated_without_steps() -> None:
    result = _plan(_controlled([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
    ]))

    assert result.status == NEEDS_EVIDENCE
    assert result.ready is False
    assert result.ordered_candidate_steps == ()
    assert "margen_basico:cost_function" in result.missing_requirements


def test_blocked_controlled_candidates_are_propagated() -> None:
    profile = build_service_1_owner_rectified_evidence_profile_v1(
        matrix=ColumnConfirmationMatrix(
            file_name="pyme.xlsx",
            entries=[ColumnConfirmationEntry(
                original_column_name="Precio",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            )],
        ),
        case_ref="CASE-BLOCKED",
    )
    tools = build_service_1_evidence_profile_to_candidate_tools_v1(evidence_profile=profile)
    controlled = build_service_1_candidate_tools_to_controlled_execution_bridge_v1(
        candidate_tools_result=tools,
        operator_ref="OP-1",
        execution_window_ref="WIN-1",
    )

    result = _plan(controlled)

    assert result.status == BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES
    assert "NO_OWNER_RECTIFIED_FUNCTIONS" in result.blocked_reasons
    assert result.ordered_candidate_steps == ()


def test_no_candidate_tools_is_propagated_without_steps() -> None:
    controlled = _controlled([_entry("Producto", "producto")])
    object.__setattr__(controlled, "status", "NO_CANDIDATE_TOOLS")
    object.__setattr__(controlled, "controlled_execution_candidates", ())
    object.__setattr__(controlled, "candidate_tool_refs", ())
    object.__setattr__(controlled, "missing_requirements", ())
    object.__setattr__(controlled, "blocked_reasons", ())

    result = _plan(controlled)

    assert result.status == NO_CANDIDATE_TOOLS
    assert result.ordered_candidate_steps == ()


def test_unsafe_flags_block_plan() -> None:
    controlled = _controlled([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])
    object.__setattr__(controlled, "execution_authorized", True)

    result = _plan(controlled)

    assert result.status == BLOCKED_UNSAFE_RUNTIME_FLAGS
    assert result.blocked_reasons == ("unsafe upstream flag is true: execution_authorized",)
    assert result.ordered_candidate_steps == ()


def test_unsafe_candidate_flag_blocks_plan() -> None:
    controlled = _controlled([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])
    unsafe_candidate = replace(controlled.controlled_execution_candidates[0], tool_execution_authorized=True)
    object.__setattr__(controlled, "controlled_execution_candidates", (unsafe_candidate,))

    result = _plan(controlled)

    assert result.status == BLOCKED_UNSAFE_RUNTIME_FLAGS
    assert result.blocked_reasons == (
        "unsafe candidate flag is true: precio_margen_basico.tool_execution_authorized",
    )


def test_output_is_deterministic() -> None:
    entries = [_entry("Costo", "costo_unitario"), _entry("Producto", "producto"), _entry("Precio", "precio_venta")]

    assert _plan(_controlled(entries)).to_dict() == _plan(_controlled(list(reversed(entries)))).to_dict()

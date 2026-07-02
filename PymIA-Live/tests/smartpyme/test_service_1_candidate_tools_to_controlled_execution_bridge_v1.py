from __future__ import annotations

from dataclasses import replace

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_candidate_tools_to_controlled_execution_bridge_v1 import (
    BLOCKED_INVALID_CANDIDATE_TOOLS,
    BLOCKED_MISSING_EXECUTION_WINDOW,
    BLOCKED_MISSING_OPERATOR,
    BLOCKED_UNSAFE_RUNTIME_FLAGS,
    CONTROLLED_EXECUTION_CANDIDATES_READY,
    NEEDS_EVIDENCE,
    NO_CANDIDATE_TOOLS,
    build_service_1_candidate_tools_to_controlled_execution_bridge_v1,
)
from pymia.smartpyme.service_1_evidence_profile_to_candidate_tools_contract_v1 import (
    build_service_1_evidence_profile_to_candidate_tools_v1,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import (
    build_service_1_owner_rectified_evidence_profile_v1,
)


def _entry(header: str, function: str, *, sheet: str = "Ventas") -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=header,
        sheet_name=sheet,
        suggested_semantic_role="unknown",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        owner_confirmed_role=function,
        owner_rectified_function=function,
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )


def _candidate_tools(entries: list[ColumnConfirmationEntry]):
    evidence_profile = build_service_1_owner_rectified_evidence_profile_v1(
        matrix=ColumnConfirmationMatrix(file_name="pyme.xlsx", entries=entries),
        case_ref="CASE-EXEC-001",
    )
    return build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=evidence_profile,
    )


def _bridge(candidate_tools_result, *, operator_ref: str | None = "OP-1", execution_window_ref: str | None = "WIN-1"):
    return build_service_1_candidate_tools_to_controlled_execution_bridge_v1(
        candidate_tools_result=candidate_tools_result,
        operator_ref=operator_ref,
        execution_window_ref=execution_window_ref,
    )


def test_ready_candidate_tools_prepare_controlled_execution_candidate_without_execution() -> None:
    candidate_tools = _candidate_tools([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])

    result = _bridge(candidate_tools)

    assert result.status == CONTROLLED_EXECUTION_CANDIDATES_READY
    assert result.ready is True
    assert result.candidate_tool_refs == ("precio_margen_basico",)
    assert len(result.controlled_execution_candidates) == 1

    candidate = result.controlled_execution_candidates[0]
    assert candidate.candidate_kind == "SERVICE_1_CONTROLLED_TOOL_EXECUTION_CANDIDATE"
    assert candidate.tool_ref == "precio_margen_basico"
    assert candidate.operator_ref == "OP-1"
    assert candidate.execution_window_ref == "WIN-1"
    assert candidate.dry_run_required is True
    assert candidate.execution_authorized is False
    assert candidate.execution_executed is False
    assert candidate.runtime_authorized is False
    assert candidate.tool_execution_authorized is False
    assert candidate.executable_tool_request_authorized is False
    assert result.execution_authorized is False
    assert result.tool_execution_authorized is False
    assert result.executable_tool_requests_authorized is False


def test_multiple_candidate_tools_prepare_sorted_controlled_candidates() -> None:
    candidate_tools = _candidate_tools([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
        _entry("Stock", "stock"),
        _entry("Fecha", "fecha"),
        _entry("Cobro", "cobro"),
    ])

    result = _bridge(candidate_tools)

    assert result.status == CONTROLLED_EXECUTION_CANDIDATES_READY
    assert result.candidate_tool_refs == (
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
    )
    assert [candidate.tool_ref for candidate in result.controlled_execution_candidates] == [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
    ]


def test_missing_operator_blocks_bridge() -> None:
    candidate_tools = _candidate_tools([
        _entry("SKU", "sku"),
        _entry("Stock", "stock"),
    ])

    result = _bridge(candidate_tools, operator_ref=" ")

    assert result.status == BLOCKED_MISSING_OPERATOR
    assert result.ready is False
    assert result.controlled_execution_candidates == ()
    assert result.blocked_reasons == ("operator_ref is required",)
    assert result.execution_authorized is False


def test_missing_execution_window_blocks_bridge() -> None:
    candidate_tools = _candidate_tools([
        _entry("SKU", "sku"),
        _entry("Stock", "stock"),
    ])

    result = _bridge(candidate_tools, execution_window_ref="")

    assert result.status == BLOCKED_MISSING_EXECUTION_WINDOW
    assert result.ready is False
    assert result.controlled_execution_candidates == ()
    assert result.blocked_reasons == ("execution_window_ref is required",)


def test_needs_evidence_is_propagated_without_candidates() -> None:
    candidate_tools = _candidate_tools([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
    ])

    result = _bridge(candidate_tools)

    assert result.status == NEEDS_EVIDENCE
    assert result.ready is False
    assert result.controlled_execution_candidates == ()
    assert "margen_basico:cost_function" in result.missing_requirements


def test_blocked_candidate_tools_are_propagated_without_execution_candidates() -> None:
    evidence_profile = build_service_1_owner_rectified_evidence_profile_v1(
        matrix=ColumnConfirmationMatrix(
            file_name="pyme.xlsx",
            entries=[
                ColumnConfirmationEntry(
                    original_column_name="Precio",
                    sheet_name="Ventas",
                    suggested_semantic_role="precio_venta",
                    calculation_relevance=CalculationRelevance.VENTAS,
                    confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                )
            ],
        ),
        case_ref="CASE-BLOCKED",
    )
    candidate_tools = build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=evidence_profile,
    )

    result = _bridge(candidate_tools)

    assert result.status == BLOCKED_INVALID_CANDIDATE_TOOLS
    assert result.ready is False
    assert result.controlled_execution_candidates == ()
    assert "NO_OWNER_RECTIFIED_FUNCTIONS" in result.blocked_reasons


def test_no_candidate_tools_status_is_propagated() -> None:
    candidate_tools = _candidate_tools([
        _entry("Producto", "producto"),
    ])
    object.__setattr__(candidate_tools, "status", "NO_CANDIDATE_TOOLS")
    object.__setattr__(candidate_tools, "candidate_tools", ())
    object.__setattr__(candidate_tools, "candidate_tool_refs", ())
    object.__setattr__(candidate_tools, "missing_requirements", ())
    object.__setattr__(candidate_tools, "blockers", ())

    result = _bridge(candidate_tools)

    assert result.status == NO_CANDIDATE_TOOLS
    assert result.ready is False
    assert result.controlled_execution_candidates == ()


def test_unsafe_upstream_flag_blocks_bridge() -> None:
    candidate_tools = _candidate_tools([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])
    object.__setattr__(candidate_tools, "runtime_authorized", True)

    result = _bridge(candidate_tools)

    assert result.status == BLOCKED_UNSAFE_RUNTIME_FLAGS
    assert result.ready is False
    assert result.controlled_execution_candidates == ()
    assert result.blocked_reasons == ("unsafe upstream flag is true: runtime_authorized",)


def test_unsafe_candidate_tool_flag_blocks_bridge() -> None:
    candidate_tools = _candidate_tools([
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
        _entry("Costo", "costo_unitario"),
    ])
    unsafe_candidate = replace(candidate_tools.candidate_tools[0], tool_execution_authorized=True)
    object.__setattr__(candidate_tools, "candidate_tools", (unsafe_candidate,))

    result = _bridge(candidate_tools)

    assert result.status == BLOCKED_UNSAFE_RUNTIME_FLAGS
    assert result.ready is False
    assert result.controlled_execution_candidates == ()
    assert result.blocked_reasons == (
        "unsafe candidate tool flag is true: precio_margen_basico.tool_execution_authorized",
    )


def test_dry_run_false_blocks_bridge() -> None:
    candidate_tools = _candidate_tools([
        _entry("SKU", "sku"),
        _entry("Stock", "stock"),
    ])

    result = build_service_1_candidate_tools_to_controlled_execution_bridge_v1(
        candidate_tools_result=candidate_tools,
        operator_ref="OP-1",
        execution_window_ref="WIN-1",
        dry_run_required=False,
    )

    assert result.status == BLOCKED_INVALID_CANDIDATE_TOOLS
    assert result.ready is False
    assert result.blocked_reasons == ("dry_run_required must be True",)


def test_bridge_output_is_deterministic() -> None:
    entries = [
        _entry("Costo", "costo_unitario"),
        _entry("Producto", "producto"),
        _entry("Precio", "precio_venta"),
    ]

    first = _bridge(_candidate_tools(entries)).to_dict()
    second = _bridge(_candidate_tools(list(reversed(entries)))).to_dict()

    assert first == second

from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_candidate_tools_to_controlled_execution_bridge_v1 import (
    CONTROLLED_EXECUTION_CANDIDATES_READY,
    build_service_1_candidate_tools_to_controlled_execution_bridge_v1,
)
from pymia.smartpyme.service_1_column_confirmation_applier_v1 import (
    apply_service_1_column_confirmation_v1,
)
from pymia.smartpyme.service_1_column_confirmation_classifier_v1 import (
    classify_owner_column_confirmation_answer,
)
from pymia.smartpyme.service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1 import (
    SUPERVISED_DRY_RUN_PLAN_READY,
    build_service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1,
)
from pymia.smartpyme.service_1_evidence_profile_to_candidate_tools_contract_v1 import (
    CANDIDATE_TOOLS_READY,
    build_service_1_evidence_profile_to_candidate_tools_v1,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import (
    MARGIN_SIGNAL,
    SALES_COLLECTION_SIGNAL,
    STOCK_SIGNAL,
    build_service_1_owner_rectified_evidence_profile_v1,
)

FILE_NAME = "synthetic_semantic_chain.xlsx"
SHEET = "Ventas"
CASE_REF = "CASE-SYNTHETIC-SEMANTIC-E2E-001"


def _target(column: str) -> str:
    return f"file:{FILE_NAME}:sheet:{SHEET}:column:{column}"


def _entry(column: str, suggested_role: str) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column,
        sheet_name=SHEET,
        suggested_semantic_role=suggested_role,
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    )


def _matrix() -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
        file_name=FILE_NAME,
        entries=[
            _entry("Producto", "producto"),
            _entry("Precio", "precio_venta"),
            _entry("Costo", "costo_unitario"),
            _entry("Stock", "stock"),
            _entry("Fecha", "fecha"),
            _entry("SaldoPendiente", "venta_total"),
        ],
    )


def _apply_owner_answer(
    *,
    matrix: ColumnConfirmationMatrix,
    column: str,
    proposed_role: str,
    answer: str,
) -> None:
    classification = classify_owner_column_confirmation_answer(
        raw_owner_answer=answer,
        question_target_ref=_target(column),
        proposed_role=proposed_role,
    )
    apply_service_1_column_confirmation_v1(
        classification=classification,
        matrix=matrix,
        case_id=CASE_REF,
        tenant_id="TENANT-SYNTHETIC",
        intake_id="INTAKE-SYNTHETIC-XLSX",
    )


def _semantic_chain_to_dry_run_plan(matrix: ColumnConfirmationMatrix):
    evidence_profile = build_service_1_owner_rectified_evidence_profile_v1(
        matrix=matrix,
        case_ref=CASE_REF,
    )
    candidate_tools = build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=evidence_profile,
    )
    controlled_candidates = build_service_1_candidate_tools_to_controlled_execution_bridge_v1(
        candidate_tools_result=candidate_tools,
        operator_ref="OP-SYNTHETIC",
        execution_window_ref="WINDOW-SYNTHETIC-DRY-RUN",
    )
    dry_run_plan = build_service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1(
        controlled_execution_candidates_result=controlled_candidates,
    )
    return evidence_profile, candidate_tools, controlled_candidates, dry_run_plan


def test_synthetic_semantic_chain_reaches_supervised_dry_run_plan_without_execution() -> None:
    matrix = _matrix()

    _apply_owner_answer(matrix=matrix, column="Producto", proposed_role="producto", answer="Sí, correcto.")
    _apply_owner_answer(matrix=matrix, column="Precio", proposed_role="precio_venta", answer="Sí, correcto.")
    _apply_owner_answer(matrix=matrix, column="Costo", proposed_role="costo_unitario", answer="Sí, correcto.")
    _apply_owner_answer(matrix=matrix, column="Stock", proposed_role="stock", answer="Sí, correcto.")
    _apply_owner_answer(matrix=matrix, column="Fecha", proposed_role="fecha", answer="Sí, correcto.")
    _apply_owner_answer(
        matrix=matrix,
        column="SaldoPendiente",
        proposed_role="venta_total",
        answer="Tu respuesta: esa columna es el saldo pendiente, no la venta total.",
    )

    assert matrix.status() == "all_confirmed"
    assert [entry.owner_rectified_function for entry in matrix.entries] == [
        "producto",
        "precio_venta",
        "costo_unitario",
        "stock",
        "fecha",
        "saldo",
    ]
    assert matrix.entries[-1].suggested_semantic_role == "venta_total"
    assert matrix.entries[-1].owner_rectified_function == "saldo"

    evidence_profile, candidate_tools, controlled_candidates, dry_run_plan = _semantic_chain_to_dry_run_plan(matrix)

    assert evidence_profile.evidence_ready is True
    assert {signal.signal_name for signal in evidence_profile.evidence_signals if signal.evidence_ready} == {
        MARGIN_SIGNAL,
        STOCK_SIGNAL,
        SALES_COLLECTION_SIGNAL,
    }
    assert evidence_profile.runtime_authorized is False
    assert evidence_profile.tool_execution_authorized is False

    assert candidate_tools.status == CANDIDATE_TOOLS_READY
    assert candidate_tools.candidate_tool_refs == (
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
    )
    assert candidate_tools.executable_tool_requests_authorized is False

    assert controlled_candidates.status == CONTROLLED_EXECUTION_CANDIDATES_READY
    assert controlled_candidates.execution_authorized is False
    assert controlled_candidates.tool_execution_authorized is False
    assert controlled_candidates.pipeline_authorized is False
    assert controlled_candidates.delivery_authorized is False

    assert dry_run_plan.status == SUPERVISED_DRY_RUN_PLAN_READY
    assert [step.tool_ref for step in dry_run_plan.ordered_candidate_steps] == [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
    ]
    assert "CONFIRM_NO_REAL_EXECUTION" in dry_run_plan.required_manual_confirmations
    assert dry_run_plan.execution_authorized is False
    assert dry_run_plan.execution_executed is False
    assert dry_run_plan.tool_execution_authorized is False
    assert dry_run_plan.pipeline_authorized is False
    assert dry_run_plan.delivery_authorized is False
    assert dry_run_plan.llm_authorized is False


def test_synthetic_semantic_chain_fails_closed_when_owner_rectification_is_missing() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name=FILE_NAME,
        entries=[
            _entry("Precio", "precio_venta"),
        ],
    )

    evidence_profile, candidate_tools, controlled_candidates, dry_run_plan = _semantic_chain_to_dry_run_plan(matrix)

    assert evidence_profile.evidence_ready is False
    assert "NO_OWNER_RECTIFIED_FUNCTIONS" in evidence_profile.blockers
    assert "UNRECTIFIED_SEMANTIC_FUNCTION:Ventas.Precio" in evidence_profile.blockers

    assert candidate_tools.status == "BLOCKED"
    assert controlled_candidates.ready is False
    assert controlled_candidates.controlled_execution_candidates == ()
    assert dry_run_plan.ready is False
    assert dry_run_plan.ordered_candidate_steps == ()
    assert dry_run_plan.execution_authorized is False
    assert dry_run_plan.tool_execution_authorized is False
